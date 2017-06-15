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
from twisted.internet.task import LoopingCall
import urllib3
import requests

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
        self._gateway = None
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
        self._gateway = self._env.get('api_gateway')
        self.log("Gateway={}".format(self._gateway))
        if self._proto not in self._ports:
            self._proto = 'http'
            self.log('Protocol defaulting to "http" [protocol=http|https is missing]')

        if self._proto == 'https':
            self._port = self._ports[self._proto]
        else:
            self._port = self._env.port

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
        api_register = '{}://{}:{}/api/1.0.0/register'.format(
            self._proto,
            self._gateway,
            443 if self._proto == 'https' else 8080
        )
        for entry in self._routes:
            route = dict(entry, **{'protocol': self._proto, 'host': self._env.host, 'port': self._port})
            resp = requests.post(api_register, verify=False, data={'details': dumps(route)})
            if resp.status_code != 200:
                return self.warn("[{}] {} - {} - {}".format(resp.status_code, api_register, resp.reason, resp.text))
            self.log('Register endpoint "{}" => "{}"'.format(route, resp.status_code))
        return True

    def ping(self):
        """
        Start a timer which will bounce messages off the API gateway on a regular basis and (re)register
        endpoints if they're not already registered.
        """
        try:
            api_ping = '{}://{}:{}/api/1.0.0/ping/{}/{}'.format(
                self._proto,
                self._gateway,
                443 if self._proto == 'https' else 8080,
                self._env.host,
                self._port
            )
            resp = requests.get(api_ping, verify=False)
            if not self._state:
                self.log('Ping "{}" => "{}"'.format(api_ping, resp.status_code))
            if resp.status_code not in [200, 204]:
                self._state = False
                return self.error('"{}" connecting to gateway for "{}"'.format(resp.status_code, api_ping))
            if resp.status_code == 200:
                self._state = True
                return
            self.register_routes()
        except requests.exceptions.ConnectionError as e:
            self.log('ping failed for "{}"'.format(api_ping))
            self.log('ping return = "{}"'.format(e.args[0].reason))
            self._state = False
