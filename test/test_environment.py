import unittest
from unittest.mock import patch

from ons_ras_common import ons_env
from os import environ

ons_env.setup()


class TestEnvironment(unittest.TestCase):

    def test_default_settings_exist(self):
        enable_database = ons_env.get('enable_database', boolean=True)
        print(">>>", enable_database)
        self.assertFalse(enable_database)

        drop_database = ons_env.get('drop_database', boolean=True)
        self.assertTrue(drop_database)

        self.assertTrue(ons_env.drop_database)

    def test_set_a_random_variable(self):
        ons_env.set('this_is_new', 'HELLO')
        hello = ons_env.get('this_is_new')
        self.assertEqual(hello, 'HELLO')

    def test_get_on_non_section(self):
        test = ons_env.get('this_is_new', 'HELLO', 'NO SECTION')
        self.assertEqual(test, 'HELLO')

    def test_using_env_to_override_config_options(self):
        environ['MY_ENV_KEY'] = 'HELLO'
        test = ons_env.get('MY_ENV_KEY')
        self.assertEqual(test, 'HELLO')

    def test_environment_override_always_active(self):
        environ['API_PORT'] = '5555'
        a1 = ons_env.get('api_port')
        a2 = ons_env.get('api_port', section='nonexistent')
        self.assertEqual(a1, a2)

    def test_host_attribute(self):
        self.assertEqual(ons_env.host, 'localhost')

    def test_get_database(self):
        self.assertTrue(ons_env.db)

    def test_get_logger(self):
        self.assertTrue(ons_env.logger)

    def test_get_cf(self):
        self.assertTrue(ons_env.cf)

    def test_get_crypt(self):
        self.assertTrue(ons_env.crypt)

    def test_get_cipher(self):
        self.assertTrue(ons_env.cipher)

    def test_get_swagger(self):
        self.assertTrue(ons_env.swagger)

    def test_get_algo(self):
        self.assertTrue(ons_env.jwt_algorithm)

    def test_get_environment(self):
        self.assertTrue(ons_env.environment)

    def test_jwt_secret(self):
        self.assertEqual(ons_env.jwt_secret, "vrwgLNWEffe45thh545yuby")

    def test_jwt(self):
        self.assertTrue(ons_env.jwt)

    def test_get_ms_name(self):
        self.assertEqual(ons_env.ms_name, "ONS Micro-Service")

    def test_get_is_secure(self):
        self.assertEqual(ons_env.is_secure, True)

    def test_get_flask_protocol(self):
        self.assertEqual(ons_env.get('flask_protocol'), 'http')

    def test_get_flask_host(self):
        self.assertEqual(ons_env.get('flask_host', 'localhost'), 'localhost')

    def test_get_flask_port(self):
        self.assertEqual(ons_env.get('flask_port', 123), 123)

    def test_get_free_port(self):
        self.assertTrue(ons_env.get_free_port())