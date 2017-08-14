"""

    Microservices header template
    License: MIT
    Copyright (c) 2017 Crown Copyright (Office for National Statistics)

    This is used for development purposes / serves as an example or template

"""
from ons_ras_common import ons_env
from ons_ras_common.ons_decorators import before_request

if __name__ == '__main__':

    def callback(app):

        class RQ(object):

            def __init__(self, method, full_path):
                self.method = method
                self.full_path = full_path

        req = RQ('GET', 'MY_TEST_URL')

        @before_request(req)
        def testme():
            ons_env.logger.info({'event': 'This should contain bound data'})
            ons_env.logger.debug("Also bound")

        testme()
        ons_env.logger.debug("NOT bound")

    ons_env.activate(callback=callback)
