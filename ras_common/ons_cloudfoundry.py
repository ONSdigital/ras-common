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
        self._port = 0
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
        self._host = url.split(':')[0]
        self._port = int(url.split(':')) if ':' in url else 0
        #
        #   Now get our database connection (if there is one)
        #
        vcap_services = getenv('VCAP_SERVICES')
        if not vcap_services:
            return self.log('Services: No services detected')
        for service in loads(vcap_services).values():
            credentials = service['credentials']
            self._env.set('db_connection', credentials['uri'])
            self._env.set('db_connection_name', service['name'])
            self.info('DB Connection String: {}'.format(credentials['uri']))
            self.info('DB Connection Name..: {}'.format(service['name']))

    @property
    def detected(self):
        return self._cf_detected



"""
    "VCAP_SERVICES": {
        "rds": [
            {
                "credentials": {
                    "db_name": "db9nh2xczpqu91sh1",
                    "host": "mvp-applicationdb.cef6vnd8djsq.eu-central-1.rds.amazonaws.com",
                    "password": "u23hxhq228uv4xn5lro6og5fk",
                    "uri": "postgres://ugysr9v3llul8e8i:u23hxhq228uv4xn5lro6og5fk@mvp-applicationdb.cef6vnd8djsq.eu-central-1.rds.amazonaws.com:5432/db9nh2xczpqu91sh1",
                    "username": "ugysr9v3llul8e8i"
                },
                "label": "rds",
                "name": "ras-postgres",
                "plan": "shared-psql",
                "provider": null,
                "syslog_drain_url": null,
                "tags": [
                    "database",
                    "RDS",
                    "postgresql"
                ],
                "volume_mounts": []
            }
        ]
    }
    }
"""

