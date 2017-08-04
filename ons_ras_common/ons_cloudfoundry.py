import re
import cfenv

RegexType = type(re.compile(''))


class ONSCloudFoundry(object):

    def __init__(self, env):

        #
        #   Monkey patch cfenv so it can handle a list match
        #
        cfenv.match = my_match

        self._env = env
        self._cf_env = cfenv.AppEnv()
        self._database = self._cf_env.get_service(tags='database') if self.detected else None
        self._host = self._cf_env.uris[0].split(':') if self.detected else 'localhost'
        self._port = 443 if self.detected else 8080
        self._protocol = 'https' if self.detected else 'http'

    def activate(self):
        pass

    @property
    def url(self):
        return self._database.credentials['uri']

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

def my_match(target, pattern):
    """
    This is a customised version of "match" that also handles matching based
    on 'target' possibly being a list.
    """

    if target is None:
        return False
    if isinstance(pattern, RegexType):
        return pattern.search(target)
    if isinstance(target, list):
        return pattern in target
    return pattern == target
