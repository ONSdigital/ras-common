"""
   Generic Configuration tool for Micro-Service environment discovery
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)
   ONSCloudFoundry wraps Cloud Foundry detection and setup routines.
"""
from os import getenv
from json import loads

SERVICE_RABBITMQ = 'rabbitmq'
SERVICE_DATABASE = 'rds'
SUPPORTED_SERVICES = [SERVICE_DATABASE, SERVICE_RABBITMQ]


class ONSCloudFoundry(object):

    def __init__(self, env):
        self._env = env
        self._host = None
        self._port = None
        self._protocol = None
        self._rabbits = []
        self._databases = []
        self._detected = False

    def activate(self):
        """
        Read in the VCAP_APPLICATION and VCAP_SERVICES environment variables, then parse
        and extract the information we're interested in.
        """
        vcap_application = getenv('VCAP_APPLICATION')
        if not vcap_application:
            return self._env.logger.info('Platform: LOCAL (no CF detected)')
        self._env.logger.info('Platform: CLOUD FOUNDRY')
        self._detected = True
        #
        #   Extract the name of the host we think we are. We need to be a little bit careful here
        #   as CF is more than happy to assign more than one URI to any given host, and it's not
        #   great at correcting this event should an additional route be assigned in error. i.e.
        #   it's easy to pick up an unwanted uri in this array (!)
        #
        vcap_application = loads(vcap_application)
        url = vcap_application.get('application_uris', [''])[0]
        #
        #   These should be used to override any pre-existing environment variables
        #
        self._host = url.split(':')[0]
        self._port = 443
        self._protocol = 'https'
        #
        #   Do we have any services enabled for this host
        #
        vcap_services = getenv('VCAP_SERVICES')
        if not vcap_services:
            return self._env.logger.info('no Cloud Foundry services detected')
        #
        #   Cycle through any available services and extract the ones we're interested in
        #
        vcap_services = loads(vcap_services)
        for key, services in vcap_services.items():
            if key not in SUPPORTED_SERVICES:
                self._env.logger.info('Ignoring service "{}"'.format(key))
                continue
            #
            #   Handle database service entries
            #
            if key == SERVICE_DATABASE:
                for service in services:
                    creds = service.get('credentials')
                    if not creds:
                        continue
                    db = Database(
                        creds.get('uri'),
                        creds.get('db_name')
                    )
                    self._env.logger.info('added CF service :: {}'.format(db))
                    self._databases.append(db)
            #
            #   Handle RabbitMQ service entries
            #
            elif key == SERVICE_RABBITMQ:
                for service in services:
                    amqp = service.get('credentials', {}).get('protocols', {}).get('amqp')
                    if not amqp:
                        continue
                    rabbit = Rabbit(
                        amqp.get('host'),
                        amqp.get('port'),
                        amqp.get('username'),
                        amqp.get('password'),
                        amqp.get('vhost'),
                        service.get('name')
                    )
                    self._env.logger.info('added CF service :: {}'.format(rabbit))
                    self._rabbits.append(rabbit)

    @property
    def detected(self):
        return self._detected

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def protocol(self):
        return self._protocol

    @property
    def rabbits(self):
        return self._rabbits

    @property
    def databases(self):
        return self._databases


class Database(object):

    def __init__(self, uri, name):
        self._uri = uri
        self._name = name

    def __repr__(self):
        return 'database "{}" with URI "{}"'.format(self._name, self._uri)

    @property
    def uri(self):
        return self._uri

    @property
    def name(self):
        return self._name

class Rabbit(object):

    def __init__(self, host, port, user, password, vhost, name):
        self._host = host
        self._port = port
        self._user = user
        self._pass = password
        self._vhost = vhost
        self._name = name

    def __repr__(self):
        return 'rabbit queue "{}" on host "{}":"{}" with vhost "{}"'.format(
            self._name, self._host, self._port, self._vhost
        )

    @property
    def name(self):
        return self._name

    @property
    def host(self):
        return self._vhost

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._user

    @property
    def password(self):
        return self._pass

    @property
    def vhost(self):
        return self._vhost