from cfenv import AppEnv

class ONSCloudFoundry(object):

    def __init__(self, env):

        self._env = env
        self._cf_env = AppEnv()
        self._database = self._cf_env.get_service(tags='database') if self.detected else None

    def activate(self):
        pass

    @property
    def url(self):
        return self._database.get_url()

    @property
    def detected(self):
        return self._cf_env.app
