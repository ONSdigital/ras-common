"""
   ONS Digital Rabbit queue handling
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)
    RabbitMQ helper function, this can probably be refactored out, but for now
    it maintains a handy compatibility layer for other modules.
"""


class ONSRabbit(object):

    def __init__(self, env):
        self._env = env
        self._queues = {}

    def activate(self):
        pass

    @property
    def host(self):
        rabbit = self._env.cf.rabbits[0] if len(self._env.cf.rabbits) else None
        return rabbit.host if rabbit else None

    @property
    def port(self):
        rabbit = self._env.cf.rabbits[0] if len(self._env.cf.rabbits) else None
        return rabbit.port if rabbit else None

    @property
    def name(self):
        rabbit = self._env.cf.rabbits[0] if len(self._env.cf.rabbits) else None
        return rabbit.name if rabbit else None

    @property
    def username(self):
        rabbit = self._env.cf.rabbits[0] if len(self._env.cf.rabbits) else None
        return rabbit.username if rabbit else None

    @property
    def password(self):
        rabbit = self._env.cf.rabbits[0] if len(self._env.cf.rabbits) else None
        return rabbit.password if rabbit else None

    @property
    def vhost(self):
        rabbit = self._env.cf.rabbits[0] if len(self._env.cf.rabbits) else None
        return rabbit.vhost if rabbit else None