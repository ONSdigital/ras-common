"""

   Generic Configuration tool for Micro-Service environment discovery
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)


   ONSRegistration takes care of registering the Micro-service with the
   RAS API gateway, and in future any other gateways involved in platform
   provisioning.

"""
from json import dumps
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import urllib3
import requests
import treq
import twisted.internet._sslverify as v
v.platformTrust = lambda: None

urllib3.disable_warnings()


class ONSRegistration(object):

    def __init__(self, env):
        """
        Set up configuration and local variables
        :param env: The global configuration context
        """
        self._env = env
        self._routes = []
        self._proto = None
        self._port = None
        self._state = False
        self._key = None

    def activate(self):
        """
        Load the routing table and kick off the recurring registration process
        """
        if not self._env.enable_registration:
            return
        self._env.logger.info('Activating service registration')
        legacy_key = '{}:{}'.format(self._env.flask_host, self._env.flask_port)
        self._key = self._env.get('my_ident', legacy_key, 'microservice')
        LoopingCall(self.ping).start(5, now=False)

    def register_routes(self):
        """
        Actually apply the routing table to the gateway. This will happen on startup, or any time
        the gateway itself does a reload or restart.
        """
        @inlineCallbacks
        def registered(response):
            if response.code != 200:
                text = yield response.text()
                self._env.logger.error('{} {}'.format(response.code, text))

        try:
            api_register = '{}://{}:{}/api/1.0.0/register'.format(
                self._env.api_protocol,
                self._env.api_host,
                self._env.api_port
            )
            remote_ms = self._env.get('remote_ms', None)

            for path in self._env.swagger.paths:
                uri = self._env.swagger.base + path.split('{')[0].rstrip('/')
                if remote_ms:
                    route = {
                        'protocol': 'https',
                        'host': remote_ms,
                        'port': 443,
                    }
                else:
                    route = {
                        'protocol': self._env.flask_protocol,
                        'host': self._env.flask_host,
                        'port': self._env.flask_port,
                    }
                route = dict(route, **{'uri': uri, 'key': self._key})
                #self._env.logger.info('Route> {}'.format(str(route)))
                treq.post(api_register, data={'details': dumps(route)}).addCallback(registered)

            swagger_paths = ['/ui/css', '/ui/lib', '/ui/images', '/swagger.json']
            ui = '/' + self._env.get('swagger_ui', 'ui')+'/'
            swagger_paths.append(ui)

            for path in swagger_paths:
                uri = self._env.swagger.base
                if len(uri):
                    if uri[-1] == '/':
                        uri = uri[:-1]
                uri += path
                route = {
                    'protocol': self._env.flask_protocol,
                    'host': self._env.flask_host,
                    'port': self._env.flask_port,
                    'uri': uri,
                    'key': self._key,
                    'ui': path == ui,
                    'name': self._env.get('my_name', 'no local name', 'microservice')
                }
                treq.post(api_register, data={'details': dumps(route)}).addCallback(registered)

            return True
        except Exception as e:
            self._env.logger.error('error registering routes "{}"'.format(str(e)))

    def ping(self):
        """
        Start a timer which will bounce messages off the API gateway on a regular basis and (re)register
        endpoints if they're not already registered.
        """
        try:
            api_ping = '{}://{}:{}/api/1.0.0/ping/{}/None'.format(
                self._env.api_protocol,
                self._env.api_host,
                self._env.api_port,
                self._key
            )

            def check(response):
                if response.code == 204:
                    self._env.logger.info('204 - Registering new routes')
                    self.register_routes()
                elif response.code != 200:
                    self._env.logger.error('{} - UNKNOWN ERROR'.format(response.code))
                return response

            def log(failure):
                """
                Just log the error, a return code of 'False' will be returned elsewhere
                :param failure: A treq failure object
                """
                return self._env.logger.warning('[ping] {}'.format(failure.getErrorMessage()))

            treq.get(api_ping).addCallback(check).addErrback(log)

        except requests.exceptions.ConnectionError as e:
            self._env.logger.warning('ping failed for "{}"'.format(api_ping))
            self._env.logger.warning('ping return = "{}"'.format(e.args[0].reason))
            self._state = False
