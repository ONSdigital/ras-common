from json import dumps

import requests
import treq
import twisted.internet._sslverify as v
import urllib3
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from ons_ras_common.ras_logger import ras_logger

logger = ras_logger.get_logger()


v.platformTrust = lambda: None

urllib3.disable_warnings()


class RasRegistration:

    name = 'ras_registration'

    def __init__(self, config, swagger):
        """
        Set up configuration and local variables
        :param env: The global configuration context
        """
        self._config = config
        self._swagger = swagger
        self._state = False

    def activate(self):
        """
        Load the routing table and kick off the recurring registration process
        """
        logger.info('Activating service registration')
        # TODO: if we must ping the GW, then prefer to use asyncio
        LoopingCall(self.ping).start(5, now=False)

    def register_routes(self):
        """
        Actually apply the routing table to the gateway. This will happen on startup, or any time
        the gateway itself does a reload or restart.
        """
        api_gw_config = self._config.dependency('api-gateway')
        api_protocol = api_gw_config['scheme']
        api_host = api_gw_config['host']
        api_port = api_gw_config['port']

        @inlineCallbacks
        def registered(response):
            if response.code != 200:
                text = yield response.text()
                logger.error('{} {}'.format(response.code, text))

        try:
            api_register = '{}://{}:{}/api/1.0.0/register'.format(
                api_protocol,
                api_host,
                api_port
            )
            for path in self._swagger.paths:
                uri = self._swagger.base + path.split('{')[0].rstrip('/')
                route = {
                    'protocol': self._config.service.scheme,
                    'host': self._config.service.host,
                    'port': self._config.service_port,
                    'uri': uri,
                    'key': self._config.service.name
                }
                route = dict(route, **{'uri': uri, 'key': self._config.service.name})
                treq.post(api_register, data={'details': dumps(route)}).addCallback(registered)

            swagger_paths = ['/ui/css', '/ui/lib', '/ui/images', '/swagger.json']
            ui = '/' + self._config.get('swagger_ui', 'ui')+'/'
            swagger_paths.append(ui)

            for path in swagger_paths:
                uri = self._swagger.base
                if len(uri):
                    if uri[-1] == '/':
                        uri = uri[:-1]
                uri += path
                route = {
                    'protocol': self._config.service.scheme,
                    'host': self._config.service.host,
                    'port': self._config.service.port,
                    'uri': uri,
                    'key': self._config.service.name,
                    'ui': path == ui
                }
                self.info("DEBUG :: {}".format(str(route)))
                treq.post(api_register, data={'details': dumps(route)}).addCallback(registered)

            return True
        except Exception as e:
            self.warn("++++++ ERROR: {}".format(str(e)))

    def ping(self):
        """
        Ping the API GW to let it know we're still alive
        """
        api_gw = self._config.dependency('api-gateway')
        try:
            api_ping = '{}://{}:{}/api/1.0.0/ping/{}/None'.format(
                api_gw['scheme'],
                api_gw['host'],
                api_gw['port'],
                self._config.service.name
            )

            def status_check(response):
                if response.code == 204:
                    logger.info('Ok from API gateway, registering routes.')
                    self.register_routes()
                elif response.code != 200:
                    logger.error('Error contacting API gateway, status code = {}'.format(response.code))
                return response

            treq.get(api_ping).addCallback(status_check)

        except requests.exceptions.ConnectionError as e:
            logger.warning('ping failed for "{}"'.format(api_ping))
            logger.info('ping return = "{}"'.format(e.args[0].reason))
            self._state = False
        except Exception as e:
            logger.error("Unhandled error while attempting to ping API gateway")
            logger.error("ERROR: {}".format(e))
            raise
