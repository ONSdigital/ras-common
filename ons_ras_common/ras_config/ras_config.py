from _socket import AF_INET, SOCK_STREAM

import json
import yaml
from os import getenv
from socket import socket


def get_free_port():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('localhost', 0))
    _, port = sock.getsockname()
    sock.close()
    return port


def map_dict(d, key_mapper=None, value_mapper=None):
    def ident(x):
        return x
    key_mapper = key_mapper or ident
    value_mapper = value_mapper or ident
    return {key_mapper(k): value_mapper(v) for k, v in d.items()}


def lower_keys(d):
    return map_dict(d, key_mapper=str.lower)


class RasDependencyError(Exception):
    pass


class DependencyProxy:

    def __init__(self, dependency, name):
        self._dependency = lower_keys(dependency)
        self._name = name

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, item):
        k = "{}.{}".format(self._name, item)
        return getenv(k, self._dependency[item])


class RasConfig:
    def __init__(self, config_data):
        # TODO: enable env var override
        self.service = config_data['service']
        self._dependencies = lower_keys(config_data.get('dependencies', {}))
        self._features = lower_keys(config_data.get('features', {}))

    # TODO env var override
    def dependency(self, name):
        try:
            return DependencyProxy(self._dependencies[name], name)
        except KeyError as e:
            raise RasDependencyError(e)

    def feature(self, name, default=None):
        return self._features.get(name, default)

    def get(self, k, default=None):
        return getenv(k, default)

    def __getattr__(self, k):
        return self.get(k)

    def items(self):
        return self.service.items()

    def dependencies(self):
        return {k: DependencyProxy(self._dependencies[k], k) for k in self._dependencies.keys()}.items()

    def features(self):
        return self._dependencies.items()


class CloudFoundryServices:
    def __init__(self, service_data):
        self._lookup = {v['name']: v['credentials']
                        for service_config in service_data.values()
                        for v in service_config}

    def get(self, svc_name):
        result = self._lookup[svc_name]
        return result


class RasCloudFoundryConfig(RasConfig):

    def __init__(self, config_data):
        super().__init__(config_data)

        vcap_services = json.loads(getenv('VCAP_SERVICES'))
        self._services = CloudFoundryServices(vcap_services)

    def dependency(self, name):
        try:
            return self._services.get(name)
        except KeyError:
            return super().dependency(name)


def make(config_data):
    # TODO: allow a means of overrides aside from VCAP_SERVICES
    vcap_application = getenv('VCAP_APPLICATION')
    if vcap_application:
        return RasCloudFoundryConfig(config_data)
    else:
        return RasConfig(config_data)


def from_yaml_file(path):
    with open(path) as f:
        data = yaml.load(f.read())

    return make(data)