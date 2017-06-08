##############################################################################
#                                                                            #
#   Generic Configuration tool for Micro-Service environment discovery       #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSEnvironment wraps the application environment in terms of configuration
#   files, environment variables and anything else that pops up.
#
##############################################################################
from configparser import ConfigParser, ExtendedInterpolation
from os import getenv
from .ons_database import ONSDatabase
from .ons_cloudfoundry import ONSCloudFoundry
from .ons_logger import ONSLogger
from .ons_jwt import ONSJwt
from .ons_swagger import ONSSwagger


class ONSEnvironment(object):
    """

    """
    def __init__(self):
        """
        Setup access to ini files and the environment based on the environment
        variable ONS_ENV ...
        """
        self._jwt_algorithm = None
        self._jwt_secret = None
        self._config = ConfigParser()
        self._config._interpolation = ExtendedInterpolation()
        self._env = getenv('ONS_ENV', 'dev')
        self._lg = ONSLogger(self)
        self._cf = ONSCloudFoundry(self)
        self._db = ONSDatabase()
        self._jw = ONSJwt(self)
        self._sw = ONSSwagger(self)

    def activate(self):
        """
        Start the ball rolling ...
        """
        self.setup_ini()
        self._cf.activate()
        self._db.activate()
        self._lg.activate()

    def setup_ini(self):
        self._config.read(['local.ini', 'config.ini', '../config.ini'])
        self._jwt_algorithm = self.get('jwt_algorithm')
        self._jwt_secret = self.get('jwt_secret')

    def get(self, attribute, default=None, section=None):
        """
        Recover an attribute from a section in a .INI file

        :param attribute: The attribute to recover
        :param default: The section to recover it from
        :param section: An optional section name, otherwise we use the environment
        :return: The value of the attribute or 'default' if not found
        """
        if not section:
            section = self._env
        if section in self._config:
            return self._config[section].get(attribute, default)
        return default

    @property
    def jwt_algorithm(self):
        return self._jwt_algorithm

    @property
    def jwt_secret(self):
        return self._jwt_secret

    @property
    def jwt(self):
        return self._jw

    @property
    def environment(self):
        return self._env