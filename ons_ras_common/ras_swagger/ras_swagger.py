from pathlib import Path

import yaml

from ons_ras_common.ras_error.ras_error import RasError
from ons_ras_common.ras_logger import ras_logger

logger = ras_logger.get_logger()


class RasSwagger:
    """
    Management wrapper for Swagger OpenAPI spec (YAML) files
    """

    name = 'ras_swagger'

    def __init__(self, config, swagger_path):
        self._config = config
        self._swagger_path = Path(swagger_path)
        if not self._swagger_path.is_file():
            raise RasError("Could not access swagger file at '{}'".format(swagger_path))
        # self._has_api = Path(swagger_path).is_file()
        # self._spec = {}
        # self._swagger = {}
        # self._has_api = False

        with open(self._swagger_path) as io:
            self._spec = yaml.load(io.read())

    def activate(self):
        logger.info('Swagger API {} detected'.format('has been' if self._has_api else 'NOT'))
    #
    # @property
    # def has_api(self):
    #     return self._has_api

    @property
    def path(self):
        return self._swagger_path.resolve()

    # @property
    # def path(self):
    #     if '/' not in self._swagger_path:
    #         return './'
    #     parts = self._swagger_path.split('/')
    #     return '/'.join(parts[:-1])
    #
    # @property
    # def file(self):
    #     # parts = self._config.get('swagger', self._swagger).split('/')
    #     parts = self._swagger_path.split('/')
    #     return parts[-1]

    @property
    def host(self):
        return self._spec.get('host', None)

    @property
    def port(self):
        # TODO: why do we need this logic? shouldn't the config specify scheme AND port?
        return 443 if self._config.service.protocol == 'https' else self._config.service.port

    @property
    def base(self):
        return self._spec.get('basePath', '')

    @property
    def paths(self):
        return self._spec.get('paths', [])
