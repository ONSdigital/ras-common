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

