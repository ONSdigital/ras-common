import os
from pathlib import Path

from connexion import App
from flask_cors import CORS

from ons_ras_common.ras_error.ras_error import RasError
from ons_ras_common.ras_logger import ras_logger

logger = ras_logger.get_logger()


class ConnexionFactory:

    def __init__(self, config, swagger_service):
        self._config = config
        self._swagger_service = swagger_service

    def make(self):
        # swagger_file = '{}/{}'.format(self._swagger_service.path, self._swagger_service.file)
        swagger_path = self._swagger_service.path
        # if not Path(swagger_file).is_file():
        #     logger.error('Unable to access swagger file "{}"'.format(swagger_file))
        #     raise RasError("Unable to access swagger file at location '{}'".format(swagger_file))

        specification_dir = swagger_path.parent
        specification_file = swagger_path.name
        swagger_ui = self._config.get('swagger_ui', 'ui')
        app = App(__name__, specification_dir=specification_dir)
        app.add_api(specification_file, arguments={'title': self._config.service.name}, swagger_url=swagger_ui)
        CORS(app.app)
        return app
