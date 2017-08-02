from crochet import no_setup
no_setup()
from twisted.internet import reactor
from twisted.web import client
from configparser import ConfigParser, ExtendedInterpolation
from os import getenv
from connexion import App
from flask import Flask
from flask_cors import CORS
from flask_twisted import Twisted
from .ons_database import ONSDatabase
from .ons_cloudfoundry import ONSCloudFoundry
from .ons_logger import ONSLogger
from .ons_jwt import ONSJwt
from .ons_swagger import ONSSwagger
from .ons_cryptographer import ONSCryptographer
from .ons_rabbit import ONSRabbit
from .ons_info import ONSInfo
from socket import socket, AF_INET, SOCK_STREAM
from pathlib import Path
from os import getcwd
from . import __version__


class ONSEnvironment(object):

    def __init__(self):
        """
        Setup access to ini files and the environment based on the environment
        variable ONS_ENV ...
        """
        self._jwt_algorithm = None
        self._jwt_secret = None
        self._port = None
        self._host = None
        self._gateway = None
        self._debug = None
        self._api_protocol = None
        self._api_host = None
        self._api_port = None
        self._dynamic_port = self.get_free_port()

        self._config = ConfigParser()
        self._config._interpolation = ExtendedInterpolation()

        self._env = getenv('ONS_ENV', 'development')
        self._logger = ONSLogger(self)
        self._database = ONSDatabase(self)
        self._rabbit = ONSRabbit(self)
        self._cloudfoundry = ONSCloudFoundry(self)
        self._swagger = ONSSwagger(self)
        self._jwt = ONSJwt(self)
        self._cryptography = ONSCryptographer(self)
        self.setup_ini()
        self._info = ONSInfo(self)
        self._logger.activate()

    def setup(self):
        """
        Setup the various modules, we want to call this specifically from the test routines
        as they won't want a running reactor for testing purposes ...
        """
        self.logger.info('<< RAS_COMMON version {}>>'.format(__version__))
        self._cloudfoundry.activate()
        self._database.activate()
        self._swagger.activate()
        self._jwt.activate()
        self._cryptography.activate()
        self._rabbit.activate()

    def activate(self, callback=None, app=None, twisted=False):
        """
        Start the ball rolling ...
        """
        self.setup()
        if self.swagger.has_api:
            swagger_file = '{}/{}'.format(self.swagger.path, self.swagger.file)
            if not Path(swagger_file).is_file():
                self.logger.info('Unable to access swagger file "{}"'.format(swagger_file))
                return

            swagger_ui = self.get('swagger_ui', 'ui')
            app = App(__name__, specification_dir='{}/{}'.format(getcwd(), self.swagger.path))
            app.add_api(self.swagger.file, arguments={'title': self.ms_name}, swagger_url=swagger_ui)

            healthcheck_file = '{}/{}'.format(self.swagger.path, 'health_check.yaml')
            if Path(healthcheck_file).is_file():
                app.add_api(healthcheck_file)

            CORS(app.app)

            @app.app.teardown_appcontext
            def flush_session_manager(exception):
                self.db.session.remove()

        else:
            if not app:
                app = Flask(__name__)
                CORS(app)

            @app.teardown_appcontext
            def flush_session_manager(exception):
                self.db.session.remove()

        reactor.suggestThreadPoolSize(200)
        client._HTTP11ClientFactory.noisy = False
        if callback:
            callback(app)

        #   Sorry, flask_private is the only remotely sane way I can think of doing
        #   this at the moment. It's a special case for endpoints in the API gateway.
        if self.get('flask_private', False, boolean=True):
            port = self.get('flask_port')
        else:
            port = 8080 if self.flask_port == 443 else self.flask_port

        self.logger.info('starting listening port "{}"'.format(port))
        if twisted:
            Twisted(app).run(host='0.0.0.0', port=port, debug=False)
        else:
            app.run(host='0.0.0.0', port=port, debug=False)

    def setup_ini(self):
        self._config.read(['local.ini', '../local.ini', 'config.ini', '../config.ini'])
        self._jwt_algorithm = self.get('jwt_algorithm')
        self._jwt_secret = self.get('jwt_secret')
        self._api_host = self.get('api_host')
        self._api_port = self.get('api_port')
        self._api_protocol = self.get('api_protocol')
        self._debug = self.get('debug', 'False', boolean=True)

    def get(self, attribute, default=None, section=None, boolean=False):
        """
        Recover an attribute from a section in a .INI file

        :param attribute: The attribute to recover
        :param default: The section to recover it from
        :param section: An optional section name, otherwise we use the environment
        :return: The value of the attribute or 'default' if not found
        """
        section = section or self._env
        if section not in self._config:
            return default

        value = getenv(attribute.upper(), default=None)
        if value:
            if not boolean:
                return value
            return value.lower() in ['yes', 'true']

        base = self._config[section]
        return base.getboolean(attribute, default) if boolean else base.get(attribute, default)

    def set(self, attribute, value):
        """
        Store a variable back into the memory copy of our .INI file

        :param attribute: The key to write to
        :param value: The value to write
        """
        self._config[self._env][attribute] = value

    def get_free_port(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(('localhost', 0))
        _, port = sock.getsockname()
        sock.close()
        return port

    @property
    def drop_database(self):
        return self.get('drop_database', 'false').lower() in ['yes', 'true']

    @property
    def host(self):
        return self._host if self._host else 'localhost'

    @property
    def db(self):
        return self._database

    @property
    def logger(self):
        return self._logger

    @property
    def cf(self):
        return self._cloudfoundry

    @property
    def crypt(self):
        return self._cryptography

    @property
    def cipher(self):
        return self._cryptography

    @property
    def swagger(self):
        return self._swagger

    @property
    def jwt_algorithm(self):
        return self._jwt_algorithm

    @property
    def jwt_secret(self):
        return self._jwt_secret

    @property
    def jwt(self):
        return self._jwt

    @property
    def environment(self):
        return self._env

    @property
    def ms_name(self):
        return "ONS Micro-Service"

    @property
    def is_secure(self):
        return self.get('authentication', True, boolean=True)

    @property
    def protocol(self):
        return self.api_protocol

    @property
    def api_protocol(self):
        return self._api_protocol

    @property
    def api_host(self):
        return self._api_host

    @property
    def gateway(self):
        return self.api_host

    @property
    def api_port(self):
        return self._api_port

    @property
    def rabbit(self):
        return self._rabbit

    @property
    def debug(self):
        return self._debug

    #@property
    #def asyncio(self):
    #    return self._asyncio

    #@property
    #def case_service(self):
    #    return self._case

    #@property
    #def exercise_service(self):
    #    return self._exercise

    #@property
    #def collection_instrument(self):
    #    return self._ci

    #@property
    #def enable_registration(self):
    #    return self.get('enable_registration', True, boolean=True)

    @property
    def flask_protocol(self):
        protocol = getenv('FLASK_PROTOCOL')
        if not protocol and self.cf.detected:
            protocol = self.cf.protocol
        else:
            protocol = self.get('flask_protocol', 'http')
        return protocol

    @property
    def flask_host(self):
        host = getenv('FLASK_HOST')
        if not host and self.cf.detected:
            return self.cf.host
        else:
            host = self.get('flask_host', 'localhost')
        return host

    @property
    def flask_port(self):
        port = getenv('FLASK_PORT')
        if not port and self.cf.detected:
            port = self.cf.port
        else:
            port = self.get('flask_port', self._dynamic_port)
        return int(port)

    @property
    def info(self):
        return self._info.health_check