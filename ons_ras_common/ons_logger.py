##############################################################################
#                                                                            #
#   Generic Configuration tool for Micro-Service environment discovery       #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSLogger is a generic logging module, ultimately this will be converted
#   to output JSON format, but for now it's a simple syslog style output.
#
##############################################################################
from twisted.python import log
from sys import stdout
import logging


class ONSLogger(object):
    """
    Generic logging module mock in advance of the real module ...
    """
    def __init__(self, env):
        self._env = env

    def activate(self):
        logging.getLogger('twisted').setLevel(logging.ERROR)
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        log.startLogging(stdout)
        self.info('[log] Logger activated [environment={}]'.format(self._env.environment))

    @staticmethod
    def info(text):
        log.msg(text, logLevel=logging.INFO)

    @staticmethod
    def debug(text):
        log.msg(text, logLevel=logging.DEBUG)

    @staticmethod
    def warn(text):
        log.msg(text, logLevel=logging.WARN)

    @staticmethod
    def error(text):
        log.msg(text, logLevel=logging.ERROR)

    @staticmethod
    def critical(text):
        log.msg(text, logLevel=logging.CRITICAL)

#    from sys import _getframe
#    from logging import WARN, INFO, ERROR

#    def report(self, lvl, msg):
#        """
#        Report an issue to the external logging infrastructure
#        :param lvl: The log level we're outputting to
#        :param msg: The message we want to log
#        :return:
#        """
#        line = _getframe(1).f_lineno
#        name = _getframe(1).f_code.co_name
#        self._env.logger.info("{}:{}: #{} - {}".format(lvl, name, line, msg))
#        return False

