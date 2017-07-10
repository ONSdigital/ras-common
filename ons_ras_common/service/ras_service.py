from platform import system
if system() == "Linux":
    from twisted.internet import epollreactor
    epollreactor.install()
from twisted.internet import reactor
from twisted.web import client
from flask_twisted import Twisted

from ons_ras_common.ras_logger import ras_logger

logger = ras_logger.get_logger()


class RasMicroService(object):
    # class _ServiceRegistry:
    #     def __init__(self, services):
    #         self._lookup = {service.name: service for service in services}
    #
    #     def get(self, service_name):
    #         return self._lookup.get(service_name)

    def __init__(self, config, app_factory=None, **services):
        self.config = config
        self._factory = app_factory
        self.__dict__.update(services)

        # self._subsystem_instances = [s(config) for s in subsystems]
        # self._registry = self._ServiceRegistry(self._subsystem_instances)
        self._app = self._factory.make()

    @property
    def app(self):
        return self._app.app

    def run(self):
        # TODO: parameterise the wsgi container
        reactor.suggestThreadPoolSize(200)
        client._HTTP11ClientFactory.noisy = False

        logger.info('Running on port "{}"'.format(self.config.service.port))
        # app.run(host=self._config.service.host, port=self._config.service.port)
        Twisted(self._app).run(host=self.config.service.host, port=self.config.service.port)
        #
        # def __getattr__(self, k):
        #     return self._registry.get(k)
