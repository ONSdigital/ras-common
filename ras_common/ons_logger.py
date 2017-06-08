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
        log.startLogging(stdout)

    def activate(self):
        self.info('Logger activated [environment={}'.format(self._env.environment))

    def info(self, text):
        log.msg(text, logLevel=logging.INFO)

    def debug(self, text):
        log.msg(text, logLevel=logging.DEBUG)

    def warn(self, text):
        log.msg(text, logLevel=logging.WARN)

    def error(self, text):
        log.msg(text, logLevel=logging.ERROR)

    def critical(self, text):
        log.msg(text, logLevel=logging.CRITICAL)

