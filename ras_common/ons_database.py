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


class ONSDatabase(object):
    """
    Wrap the database functionality including database and schema creation if necessary
    """
    def __init__(self, env):
        self._env = env
        self._engine = None
        self._base = declarative_base()
        self._session = scoped_session(sessionmaker())

    def activate(self):
        if self._env.get('database_enabled', 'false').lower() not in ['true', 'yes']:
            return self._env.logger.info('Database is NOT enabled [missing "database_enabled = true"]')

        db_connection = self._env.get('db_connection')
        self._env.logger.info('Database connection is "{}"'.format(db_connection))
        self._engine = create_engine(db_connection, convert_unicode=True)
        self._session.remove()
        if self._env.drop_database:
            self.drop()
        self.create()

    def drop(self):
        self._env.logger.info('Dropping database tables')
        from swagger_server.models_local import _models
        connection = self._env.get('db_connection')
        schema = self._env.get('db_schema')
        if connection.startswith('postgres'):
            self._env.logger.info('Dropping schema "{}"'.format(schema))
            self._base.metadata.schema = schema
            self._engine.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(schema))
        else:
            self._base.metadata.drop_all(self._engine)

    def create(self):
        self._env.logger.info('Creating database tables')
        from swagger_server.models_local import _models
        connection = self._env.get('db_connection')
        schema = self._env.get('db_schema')
        if connection.startswith('postgres'):
            self._env.logger.info('Creating schema "{}"'.format(schema))
            self._base.metadata.schema = schema

        self._env.logger.info('Creating database with uri "{}"'.format(connection))
        if connection.startswith('postgres'):
            self._env.logger.info("Creating schema {}.".format(schema))
            engine.execute("CREATE SCHEMA IF NOT EXISTS {}".format(schema))
        self._env.logger.info("Creating database tables.")
        self._base.metadata.create_all(self._engine)
