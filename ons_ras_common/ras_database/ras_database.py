import importlib

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import _app_ctx_stack

from ons_ras_common.ras_database.manage import Manage
from ons_ras_common.ras_logger import ras_logger

logger = ras_logger.get_logger()


# TODO: factor this out to the appropriate place
def current_request():
    return _app_ctx_stack.__ident_func__()


class RasDatabase:
    name = 'ras_database'
    model_paths = ['swagger_server.models._models']

    @classmethod
    def make(cls, model_paths):
        cls.model_paths = model_paths
        for path in model_paths:
            importlib.import_module(path)
        return cls

    def __init__(self, name, config):
        assert(self.model_paths, "RasDatabase model_paths must be specified.")
        self._name = name
        self._config = config
        db_connection = self._config.dependency(name)['uri']
        self._engine = create_engine(db_connection, convert_unicode=True)
        self._session = scoped_session(sessionmaker(), scopefunc=current_request)
        # TODO: review this session configuration
        self._session.configure(bind=self._engine, autoflush=False, autocommit=False, expire_on_commit=False)
        self._activate()

    @property
    def session(self):
        return self._session

    def _activate(self):
        db_config = self._config.dependency(self._name)
        manager = Manage(db_config, self._engine)
        if self._config.drop_database:
            manager.drop()
        manager.create()
        return self
