##############################################################################
#                                                                            #
#   ONS Digital Rabbit queue handling                                        #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################


class RabbitQueue(object):

    def __init__(self, queue):
        self.name = queue['name']
        self.host = queue['host']
        self.port = queue['port']
        self.username = queue['username']
        self.password = queue['password']
        self.vhost = queue['vhost']

class ONSRabbit(object):

    def __init__(self, env):
        self._env = env
        self._queues = {}

    def info(self, text):
        self._env.logger.info('[rabbit] {}'.format(text))

    def activate(self):
        """
        Queue activation goes here if required
        """
        if self._env.get('rabbit_username', None):
            self.add_service({
                'name': self._env.get('rabbit_name', None),
                'host': self._env.get('rabbit_host', None),
                'port': self._env.get('rabbit_port', None),
                'username': self._env.get('rabbit_username', None),
                'password': self._env.get('rabbit_password', None),
                'vhost': self._env.get('rabbit_vhost', None)
            })
        if not len(self._queues):
            self.info('No Rabbit queues detected')
            self.add_service({
                'name': 'none',
                'host': 'none',
                'port': 'none',
                'username': 'none',
                'password': 'none',
                'vhost': 'none'
            })
        if self._env.debug:
            for queue in self._queues.values():
                self.info('Queue "{name}" user="{username}" pass="{password}" host="{host}" port="{port}" vhost="{vhost}"'.format(**vars(queue)))

    def add_service(self, que):
        self._queues[que['name']] = RabbitQueue(que)

    def get(self, name):
        return self._queues.get(name, None)

    @property
    def host(self):
        key = list(self._queues.keys())[0]
        return self._queues[key].host

    @property
    def port(self):
        key = list(self._queues.keys())[0]
        return self._queues[key].port

    @property
    def name(self):
        key = list(self._queues.keys())[0]
        return self._queues[key].name

    @property
    def username(self):
        key = list(self._queues.keys())[0]
        return self._queues[key].username

    @property
    def password(self):
        key = list(self._queues.keys())[0]
        return self._queues[key].password

    @property
    def vhost(self):
        key = list(self._queues.keys())[0]
        return self._queues[key].vhost