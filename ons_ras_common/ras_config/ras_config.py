import json
from _socket import AF_INET, SOCK_STREAM
from configparser import ConfigParser, ExtendedInterpolation
from os import getenv
from socket import socket

import yaml

from ons_ras_common.util.dict_util import PropDict


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


class RasConfig:
    def __init__(self, section, config_data):
        # TODO: section reserved in case lookup into different config sections needed
        # (e.g. dev/test/prod... which are NOT environments!)
        self.service = PropDict(lower_keys(config_data['service']))
        self._dependencies = lower_keys(config_data.get('dependencies', {}))

    def dependency(self, name):
        try:
            return lower_keys(self._dependencies[name])
        except KeyError as e:
            raise RasDependencyError(e)

    def get(self, k, default=None):
        return getenv(k, default)

    def __getattr__(self, k):
        return self.get(k)


class CloudFoundryServices:
    def __init__(self, section, service_data):
        self._lookup = {v['name']: v['credentials']
                        for service_config in service_data.values()
                        for v in service_config}

    def get(self, svc_name):
        result = self._lookup[svc_name]
        return result


class RasCloudFoundryConfig(RasConfig):

    def __init__(self, section, config_data):
        super().__init__(section, config_data)

        vcap_services = json.loads(getenv('VCAP_SERVICES'))
        self._services = CloudFoundryServices(section, vcap_services)

    def dependency(self, name):
        try:
            return self._services.get(name)
        except KeyError:
            return super().dependency(name)


def make(env_name, config_data):
    # TODO: allow a means of overrides aside from VCAP_SERVICES
    vcap_application = getenv('VCAP_APPLICATION')
    if vcap_application:
        return RasCloudFoundryConfig(env_name, config_data)
    else:
        return RasConfig(env_name, config_data)


def from_yaml_file(env_name, path):
    with open(path) as f:
        data = yaml.load(f.read())

    return make(env_name, data)
