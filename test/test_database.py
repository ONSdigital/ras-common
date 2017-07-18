import unittest
from datetime import datetime, timedelta
from ons_ras_common import ons_env
from os import environ, getcwd

ons_env.setup()


class TestDatabase(unittest.TestCase):

    def setUp(self):
        pass

    def test_check_activate(self):
        environ['ENABLE_DATABASE'] = "false"
        self.assertFalse(ons_env.db.activate())
        environ['ENABLE_DATABASE'] = "true"
        self.assertTrue(ons_env.db.activate())
        environ['ENABLE_DATABASE'] = "false"
        self.assertTrue(hasattr(ons_env.db._models, 'GUID'))
