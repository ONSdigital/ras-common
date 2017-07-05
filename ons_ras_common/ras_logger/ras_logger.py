import datetime
import logging
import sys

import structlog

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


class RasJsonLogger:
    def __init__(self, config):
        self.logger = structlog.get_logger(__name__)

        service_name = config.info['name']

        def add_service_name(logger, method_name, event_dict):  # pylint: disable=unused-argument
            """
            Add the service name to the event dict.
            """
            event_dict['service'] = service_name
            return event_dict

        processors = [
                structlog.processors.TimeStamper(fmt='iso'),
                structlog.stdlib.filter_by_level,
                add_service_name,
                structlog.stdlib.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(sort_keys=True)
        ]
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=LEVELS.get(config.get('log_level', 'INFO').lower(), logging.INFO)
        )

        structlog.configure(
            processors=processors,
            context_class=structlog.threadlocal.wrap_dict(dict),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True
        )

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def warn(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.logger.critical(*args, **kwargs)


class RasTextLogger:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)

        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=LEVELS.get(config.get('log_level', 'INFO').lower(), logging.INFO)
        )

    def info(self, *args, **kwargs):
        text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
        self.logger.info('{} {}'.format(datetime.datetime.now().isoformat(), text))

    def debug(self, *args, **kwargs):
        text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
        self.logger.debug('{} {}'.format(datetime.datetime.now().isoformat(), text))

    def warn(self, *args, **kwargs):
        text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
        self.logger.warning('{} {}'.format(datetime.datetime.now().isoformat(), text))

    def error(self, *args, **kwargs):
        text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
        self.logger.error('{} {}'.format(datetime.datetime.now().isoformat(), text))

    def critical(self, *args, **kwargs):
        text = '{} {}'.format(str(args).strip('()').strip(',').strip("'"), str(kwargs))
        self.logger.critical('{} {}'.format(datetime.datetime.now().isoformat(), text))


def make(config):
    log_format = config.get('LOG_FORMAT')
    if log_format and log_format.lower() == 'json':
        return RasJsonLogger(config)
    else:
        return RasTextLogger(config)


def get_logger():
    # TODO: unclear how this relates to structlog
    return logging.getLogger()
