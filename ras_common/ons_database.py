##############################################################################
#                                                                            #
#   Generic Configuration tool for Micro-Service environment discovery       #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSDatabase wraps all database functionality including ORM handling
#   and generic schema creation.
#
##############################################################################
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path


class ONSDatabase(object):
    """
    Wrap the database functionality including database and schema creation if necessary
    """
    def __init__(self, env):
        self._env = env
        self._engine = None
        self._base = declarative_base()
        self._session = scoped_session(sessionmaker())

    def info(self, text):
        self._env.logger.info('[db] {}'.format(text))

    def warn(self, text):
        self._env.logger.warn('[db] [warning] {}'.format(text))

    def activate(self):
        if self._env.get('enable_database', 'false').lower() not in ['true', 'yes']:
            return self.info('Database is NOT enabled [missing "enabled_database = true"]')

        if not self.check_paths():
            return self.warn('[swagger_server/models_local/_models.py] file is missing')

        db_connection = self._env.get('db_connection')
        if not db_connection:
            return self.warn('Database connection not available [{}]'.format(db_connection))

        self.info('Database connection is "{}"'.format(db_connection))
        self._engine = create_engine(db_connection, convert_unicode=True)
        self._session.remove()
        if self._env.drop_database:
            self.drop()
        self.create()

    def check_paths(self):
        """
        Check our filesystem for required database files ...
        :return: True if database environment is available
        """
        return Path('swagger_server/models_local/_models.py').is_file()

    def drop(self):
        self.info('Dropping any existing Database Tables')
        from swagger_server.models_local import _models
        connection = self._env.get('db_connection')
        schema = self._env.get('db_schema')
        if connection.startswith('postgres'):
            self.info('Dropping pre-existing schema "{}" if it exists'.format(schema))
            self._base.metadata.schema = schema
            self._engine.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(schema))
        else:
            self._base.metadata.drop_all(self._engine)

    def create(self):
        self.info('Creating any missing Database tables')
        from swagger_server.models_local import _models
        connection = self._env.get('db_connection')
        schema = self._env.get('db_schema')
        if connection.startswith('postgres'):
            self.info('Creating Database schema "{}"'.format(schema))
            self._base.metadata.schema = schema

        if connection.startswith('postgres'):
            self.info("Creating schema {} if it does't exist".format(schema))
            self._engine.execute("CREATE SCHEMA IF NOT EXISTS {}".format(schema))
        self.info("Running Create-All")
        self._base.metadata.create_all(self._engine)
