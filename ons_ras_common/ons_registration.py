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
import urllib3
import requests
import treq
import twisted.internet._sslverify as v
v.platformTrust = lambda: None

urllib3.disable_warnings()


class ONSRegistration(object):

    _ports = {
        'https': 443,
        'http': 8080
    }

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

    def log(self, text):
        self._env.logger.info('[reg] {}'.format(text))

    def warn(self, text):
        self._env.logger.warn('[reg] [warning] {}'.format(text))

    def error(self, text):
        self._env.logger.warn('[reg] [error] {}'.format(text))

    def activate(self):
        """
        Load the routing table and kick off the recurring registration process
        """
        self.log('Activating service registration')
        self._proto = self._env.get('protocol')
        if self._proto not in self._ports:
            self._proto = 'http'
            self.log('Protocol defaulting to "http" [protocol=http|https is missing]')

        if self._proto == 'https':
            self._port = self._ports[self._proto]
        else:
            self._port = self._env.port

        #self.log("Gateway={}".format(self._env.gateway))
        #self.log("Port={}".format(self._port))

        for path in self._env.swagger.paths:
            uri = self._env.swagger.base + path.split('{')[0].rstrip('/')
            self._routes.append({'uri': uri})
        for path in ['ui/', 'ui/css', 'ui/lib', 'ui/images', 'swagger.json']:
            uri = self._env.swagger.base + '/' + path
            self._routes.append({'uri': uri})
        LoopingCall(self.ping).start(5)

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

        api_register = '{}://{}:{}/api/1.0.0/register'.format(
            self._proto,
            self._env.gateway,
            443 if self._proto == 'https' else 8080
        )
        for entry in self._routes:
            route = dict(entry, **{'protocol': self._proto, 'host': self._env.host, 'port': self._port})
            treq.post(api_register, data={'details': dumps(route)}).addCallback(registered)

        return True

    def ping(self):
        """
        Start a timer which will bounce messages off the API gateway on a regular basis and (re)register
        endpoints if they're not already registered.
        """
        try:
            api_ping = '{}://{}:{}/api/1.0.0/ping/{}/{}'.format(
                self._proto,
                self._env.gateway,
                443 if self._proto == 'https' else 8080,
                self._env.host,
                self._port
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
