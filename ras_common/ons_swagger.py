##############################################################################
#                                                                            #
#   Generic Configuration tool for Micro-Service environment discovery       #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSSwagger is a wrapper for the OpenAPI spec (if there is one) for the
#   given micro-service.
#
##############################################################################
from pathlib import Path
from yaml import load, dump


class ONSSwagger(object):
    """
    Management wrapper for Swagger OpenAPI spec (YAML) files
    """
    def __init__(self, env):
        self._env = env
        self._changed = False
        self._spec = {}
        self._swagger = {}
        self._has_api = False

    def info(self, text):
        self._env.logger.info('[swagger] {}'.format(text))

    def activate(self):
        """
        Obligatory changes to the swagger specification based on the deployment environment
        """
        self._swagger = self._env.get('swagger', 'swagger_server/swagger/swagger.yaml')
        self._has_api = Path(self._swagger).is_file()
        self.info('Swagger API {} detected'.format('has been' if self._has_api else 'NOT'))
        if not self._has_api:
            return

        with open(self._swagger) as io:
            self._spec = load(io.read())

        self.rewrite_host(self._env.get('api_gateway', 'localhost'))

    def rewrite_host(self, host):
        """
        Update the host component in the Swagger specification
        :param host: New host name
        """
        if self._has_api:
            self._spec['host'] = host
            self._changed = True

    def flush(self):
        """
        Write any changes back to the swagger file
        """
        if self._has_api and self._changed:
            with open(self._swagger, 'w') as io:
                io.write(dump(self._spec))
                self.info('Swagger API updated')

    @property
    def has_api(self):
        return self._has_api

    @property
    def path(self):
        swagger = self._env.get('swagger', self._swagger)
        if '/' not in swagger:
            return './'
        parts = swagger.split('/')
        return '/'.join(parts[:-1])

    @property
    def file(self):
        parts = self._env.get('swagger', self._swagger).split('/')
        return parts[-1]

    @property
    def host(self):
        if not self._has_api:
            return ''
        return self._spec.get('host', None)

    @property
    def base(self):
        if not self._has_api:
            return ''
        return self._spec.get('basePath', None)

    @property
    def paths(self):
        return self._spec.get('paths', [])