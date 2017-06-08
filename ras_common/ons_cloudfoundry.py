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
        self.info('Logger activated [environment={}'.format(self._env.environment))

    def activate(self):
        """
        See if we're running on Cloud Foundry and if we are, run the detection and
        startup sequence.
        """
        vcap_application = getenv('VCAP_APPLICATION')
        if not vcap_application:
            self.info('Platform: LOCAL (no CF detected')
            return
        self.info('Platform: CLOUD FOUNDRY')
        vcap_application = loads(vcap_application)
