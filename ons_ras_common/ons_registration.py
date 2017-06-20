##############################################################################
#                                                                            #
#   Generic Configuration tool for Micro-Service environment discovery       #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSRegistration takes care of registering the Micro-service with the
#   RAS API gateway, and in future any other gateways involved in platform
#   provisioning.
#
##############################################################################
from json import dumps
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
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

    def log(self, text):
        self._env.logger.info('[reg] {}'.format(text))

    def info(self, text):
        self._env.logger.info('[reg] [info] {}'.format(text))

    def warn(self, text):
        self._env.logger.warn('[reg] [warning] {}'.format(text))

    def error(self, text):
        self._env.logger.warn('[reg] [error] {}'.format(text))

    def activate(self):
        """
        Load the routing table and kick off the recurring registration process
        """
        self.log('Activating service registration')
        legacy_key = '{}:{}'.format(self._env.flask_host, self._env.flask_port)
        self._key = self._env.get('my_ident', legacy_key, 'microservice')
        print("MY KEY = ", self._key)



        #try:
        #    for path in self._env.swagger.paths:
        #        uri = self._env.swagger.base + path.split('{')[0].rstrip('/')
        #        self._routes.append({'uri': uri})

         #   swagger_paths = ['ui/css', 'ui/lib', 'ui/images', 'swagger.json']
         #   swagger_paths.append(self._env.get('swagger_ui', 'ui')+'/')

#            for path in swagger_paths:
#                uri = self._env.swagger.base
#                if uri[-1] != '/':
#                    uri += '/'
#                uri += path
#                self._routes.append({'uri': uri})
#        except Exception as e:
#            print("ERROR: ", str(e))

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
                self.error('{} {}'.format(response.code, text))

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
                self._env.logger.info("====> {}".format(route))
                treq.post(api_register, data={'details': dumps(route)}).addCallback(registered)

            swagger_paths = ['/ui/css', '/ui/lib', '/ui/images', '/swagger.json']
            ui = '/' + self._env.get('swagger_ui', 'ui')+'/'
            swagger_paths.append(ui)

            for path in swagger_paths:
                uri = self._env.swagger.base
                if len(uri):
                    if uri[-1] != '/':
                        uri += '/'
                uri += path
                route = {
                    'protocol': self._env.flask_protocol,
                    'host': self._env.flask_host,
                    'port': self._env.flask_port,
                    'uri': uri,
                    'key': self._key,
                    'ui': path == ui
                }
                self._env.logger.info("====> {}".format(route))
                treq.post(api_register, data={'details': dumps(route)}).addCallback(registered)

            #for entry in self._routes:
            #    route = dict(entry, **dest)
            #    treq.post(api_register, data={'details': dumps(route)}).addCallback(registered)

            return True
        except Exception as e:
            self.warn("++++++ ERROR: {}".format(str(e)))

    def ping(self):
        """
        Start a timer which will bounce messages off the API gateway on a regular basis and (re)register
        endpoints if they're not already registered.
        """
        try:
            #api_ping = '{}://{}:{}/api/1.0.0/ping/{}/{}'.format(
            #    self._env.api_protocol,
            #    self._env.api_host,
            #    self._env.api_port,
            #    self._env.flask_host,
            #    self._env.flask_port
            #)
            api_ping = '{}://{}:{}/api/1.0.0/ping/{}/None'.format(
                self._env.api_protocol,
                self._env.api_host,
                self._env.api_port,
                self._key
            )

            def status_check(response):
                if response.code == 200:
                    self.error('200 - NO ACTION')
                elif response.code == 204:
                    self.error('200 - REGISTER')
                    self.register_routes()
                else:
                    self.error('{} - UNKNOWN ERROR'.format(response.code))
                return response

            treq.get(api_ping).addCallback(status_check)

        except requests.exceptions.ConnectionError as e:
            self.log('ping failed for "{}"'.format(api_ping))
            self.log('ping return = "{}"'.format(e.args[0].reason))
            self._state = False
