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

    def __init__(self, config, app_factory=None):
        self._config = config
        self._factory = app_factory

        # self._subsystem_instances = [s(config) for s in subsystems]
        # self._registry = self._ServiceRegistry(self._subsystem_instances)

    def configure(self):
        # for subsystem in self._subsystem_instances:
        #     subsystem.activate()
        return self

    def run(self):
        # TODO: parameterise the wsgi container
        reactor.suggestThreadPoolSize(200)
        client._HTTP11ClientFactory.noisy = False

        logger.info('Running on port "{}"'.format(self._config.service.port))
        app = self._factory.make()
        # app.run(host=self._config.service.host, port=self._config.service.port)
        Twisted(app).run(host=self._config.service.host, port=self._config.service.port)
    #
    # def __getattr__(self, k):
    #     return self._registry.get(k)
