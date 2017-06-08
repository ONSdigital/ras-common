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
        self._swagger = self._env.get('swagger', '../swagger_server/swagger/swagger.yaml')
        self._has_api = Path(self._swagger).is_file()
        self.info('Swagger API {} detected'.format('has been' if self._has_api else 'NOT'))
        if not self._has_api:
            return

        with open(self._swagger) as io:
            self._spec = load(io.read())

    def rewrite_host(self, host):
        """
        Update the host component in the Swagger specification
        :param host: New host name
        """
        if self._has_api:
            self._spec['host'] = host

    def flush(self):
        """
        Write any changes back to the swagger file
        """
        if self._has_api:
            with open(self._swagger, 'w') as io:
                io.write(dump(self._spec))
