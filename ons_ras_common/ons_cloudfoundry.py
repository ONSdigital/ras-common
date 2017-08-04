from cfenv import AppEnv

class ONSCloudFoundry(object):

    def __init__(self, env):

        self._env = env
        self._cf_env = AppEnv()
        self._database = self._cf_env.get_service(tags='database') if self.detected else None

        self._host = self._cf_env.uris.split(':')[0] if self.detected else 'localhost'
        self._port = 443 if self.detected else 8080
        self._protocol = 'https' if self.detected else 'http'

    def activate(self):
        pass

    @property
    def url(self):
        return self._database.get_url()

    @property
    def detected(self):
        return self._cf_env.app

    @property
    def port(self):
        return self._port

    @property
    def host(self):
        return self._host

    @property
    def protocol(self):
        return self._protocol
