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
import logging
import datetime
import sys
import structlog
import time

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


class ONSLogger(object):
    """
    Generic logging module mock in advance of the real module ...
    """
    def __init__(self, env):
        self._env = env

    def activate(self):
        """
        Activate the logging systems ...
        """
        log_level = self._env.get('log_level', 'INFO')
        self._ident = self._env.get('my_ident', __name__, 'microservice')
        self._log_format = self._env.get('log_format')
        if self._log_format == 'text':
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = structlog.get_logger(__name__)

        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=LEVELS.get(log_level.lower(), logging.INFO)
        )

        def add_service_name(logger, method_name, event_dict):  # pylint: disable=unused-argument
            """
            Add the service name to the event dict.
            """
            event_dict['service'] = self._ident
            return event_dict

        processors = [
                structlog.processors.TimeStamper(fmt='iso'),
                structlog.stdlib.filter_by_level,
                add_service_name,
                structlog.stdlib.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(sort_keys=True)
        ]
        structlog.configure(
            processors=processors,
            context_class=structlog.threadlocal.wrap_dict(dict),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True
        )
        self.info('Logger activated', environment=self._env.environment)

    def info(self, *args, **kwargs):
        if self._log_format == 'text':
            text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
            self.logger.info('{} {}'.format(datetime.datetime.now().isoformat(), text))
        else:
            self.logger.info(*args, **kwargs)

    def debug(self, *args, **kwargs):
        if self._log_format == 'text':
            text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
            self.logger.debug('{} {}'.format(datetime.datetime.now().isoformat(), text))
        else:
            self.logger.debug(*args, **kwargs)

    def warn(self, *args, **kwargs):
        if self._log_format == 'text':
            text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
            self.logger.warning('{} {}'.format(datetime.datetime.now().isoformat(), text))
        else:
            self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        if self._log_format == 'text':
            text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
            self.logger.error('{} {}'.format(datetime.datetime.now().isoformat(), text))
        else:
            self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        if self._log_format == 'text':
            text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
            self.logger.critical('{} {}'.format(datetime.datetime.now().isoformat(), text))
        else:
            self.logger.critical(*args, **kwargs)

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

