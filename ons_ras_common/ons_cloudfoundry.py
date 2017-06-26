##############################################################################
#                                                                            #
#   Generic Configuration tool for Micro-Service environment discovery       #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSCloudFoundry wraps all platform functionality including environment
#   detection and parsing using environment variables and manifests.
#
##############################################################################
from os import getenv
from json import loads


class ONSCloudFoundry(object):
    """

    """
    def __init__(self, env):
        self._env = env
        self._host = None
        self._cf_detected = False

    def info(self, text):
        self._env.logger.info('[cf] {}'.format(text))

    def activate(self):
        """
        See if we're running on Cloud Foundry and if we are, run the detection and
        startup sequence.
        """
        vcap_application = getenv('VCAP_APPLICATION')
        if not vcap_application:
            return self.info('Platform: LOCAL (no CF detected)')
        self.info('Platform: CLOUD FOUNDRY')
        self._cf_detected = True
        #
        #   Get our host and port
        #
        vcap_application = loads(vcap_application)
        url = vcap_application.get('application_uris', [''])[0]

        if self._env.get('flask_private', 'false').lower() not in ['yes', 'true']:
            self._env.flask_host = url.split(':')[0]
            self._env.flask_port = 443
            self._env.flask_protocol = 'https'
            self.info('Setting host to "{}" and port to "{}"'.format(self._env.api_host, self._env.api_port))
        #
        #   Now get our database connection (if there is one)
        #
        vcap_services = getenv('VCAP_SERVICES')
        vcap_services = loads(vcap_services)
        if not vcap_services:
            return self.info('Services: No services detected')
        for key, services in vcap_services.items():
            if key == 'rds':
                for service in services:
                    credentials = service.get('credentials', {})
                    self._env.set('db_connection', credentials.get('uri',''))
                    self._env.set('db_connection_name', service.get('name', ''))
                    self.info('Detected service "{}"'.format(service.get('name', '')))

            if key == 'rabbitmq':
                for service in services:
                    amqp = service.get('credentials', {}).get('protocols', {}).get('amqp', None)
                    if amqp:
                        self._env.rabbit.add_service({
                            'host': amqp.get('host', 'no host'),
                            'port': amqp.get('port', 'no port'),
                            'username': amqp.get('username', 'no username'),
                            'password': amqp.get('password', 'no password'),
                            'vhost': amqp.get('vhost', 'no vhost'),
                            'name': service.get('name', 'no name')
                        })
                    self.info('Detected service "{}"'.format(service.get('name', '')))

    @property
    def detected(self):
        return self._cf_detected
