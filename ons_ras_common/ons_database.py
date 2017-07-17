"""

   Generic Configuration tool for Micro-Service environment discovery
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)

   ONSDatabase wraps all database functionality including ORM handling
   and generic schema creation.

"""
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path
from contextlib import contextmanager


class ONSDatabase(object):
    """
    Wrap the database functionality including database and schema creation if necessary
    """
    def __init__(self, env):
        self._env = env
        self._engine = None
        self._base = declarative_base()
        self._session = scoped_session(sessionmaker())
        self._connection = None

    def activate(self):
        if self._env.get('enable_database', 'false').lower() not in ['true', 'yes']:
            return self._env.logger.info('Database is NOT enabled [missing "enabled_database = true"]')

        if not self.check_paths():
            return self._env.logger.info('[swagger_server/models/_models.py] file is missing')

        if not len(self._env.cf.databases):
            if not self._env.get('db_connection'):
                return self._env.logger.info('no databases available')
            else:
                self._connection = self._env.get('db_connection')
        else:
            self._connection = self._env.cf.databases[0].uri

        self._env.logger.info('Database connection is "{}"'.format(self._connection))
        self._engine = create_engine(self._connection, convert_unicode=True)
        self._session.remove()
        self._session.configure(bind=self._engine, autoflush=True, autocommit=False, expire_on_commit=True)
        if self._env.drop_database:
            self.drop()
        self.create()

    def check_paths(self):
        """
        Check our filesystem for required database files ...
        :return: True if database environment is available
        """
        return Path('swagger_server/models/_models.py').is_file()

    def drop(self):
        self._env.logger.info('Dropping any existing Database Tables')
        from swagger_server.models import _models
        schema = self._env.get('db_schema')
        if self._connection.startswith('postgres'):
            self._env.logger.info('Dropping pre-existing schema "{}" if it exists'.format(schema))
            self._base.metadata.schema = schema
            self._engine.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(schema))
        else:
            self._base.metadata.drop_all(self._engine)

    def create(self):
        self._env.logger.info('Creating any missing Database tables')
        schema = self._env.get('db_schema')
        if self._connection.startswith('postgres'):
            self._env.logger.info('Creating Database schema "{}"'.format(schema))
            self._base.metadata.schema = schema
        from swagger_server.models import _models

        if self._connection.startswith('postgres'):
            self._env.logger.info("Creating schema {} if it does't exist".format(schema))
            self._engine.execute("CREATE SCHEMA IF NOT EXISTS {}".format(schema))
        self._env.logger.info("Running Create-All")
        self._base.metadata.create_all(self._engine)

    @property
    def base(self):
        return self._base

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session

    @contextmanager
    def transaction(self):
        """Provide a transactional scope around a series of operations."""
        session = self._session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
