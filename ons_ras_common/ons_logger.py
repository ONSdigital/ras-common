"""

    Generic Configuration tool for Micro-Service environment discovery
    License: MIT
    Copyright (c) 2017 Crown Copyright (Office for National Statistics)

    This is a generic logging module that pulls together the functionality of the
    Python Logger, structlog and the Twisted logger. The previous attempt at logging
    wasn't working properly and was obstructing logging and fault-finding.

    This is just one non-black-box solution which provides clear logging.

"""
import logging
import twisted
import threading
import arrow
from sys import _getframe
from zope.interface import provider
from twisted.logger import Logger, ILogObserver
log = None


class ONSLogger(object):
    """
    """
    def __init__(self, env):
        self._env = env
        self._log_format = 'text'
        self._log_level = 0
        self._log_ident = '~~ none ~~'
        self._local = threading.local()
        self._local.extra = None

    def activate(self):
        """
        Read in configuration variables and kick off the event log observers
        """
        global log

        self._log_format = self._env.get('log_format', 'json')
        self._log_ident = self._env.get('my_ident', __name__, 'microservice')
        self._log_level = getattr(logging, self._env.get('log_level', 'INFO').upper(), 0)

        @provider(ILogObserver)
        def ons_logger_text(event):
            """
            Observer (TEXT format)
            This should only be used for development

            :param event: An event dict from the event service
            """
            try:
                log_time = event.get('log_time')
                log_level = event.get('log_level', '')
                log_format = event.get('log_format', '')
                log_msg = str(log_format) if type(log_format) is dict else log_format.format(**event)
                log_name = _getframe(4).f_globals['__name__']
                log_line = _getframe(4).f_lineno
                print('{} {}: [{}] {} @{}#{}'.format(
                    arrow.get(log_time).format(fmt='YYYY-MM-DDTHH:mm:ssZZ'),
                    self._log_ident,
                    log_level.name,
                    log_msg,
                    log_name,
                    log_line
                ))
            except Exception as e:
                print(e)

        @provider(ILogObserver)
        def ons_logger_json(event):
            """
            Observer (JSON format)
            If we don't care about ordering on output, this can be greatly simplified, but from a
            development point of view, having JSON fields printed in a consistent order makes the output
            readable. Hopefully logging will be set to 'warning' or above in a production environment
            so the 'cost' of logging should be relatively inconsequential.

            :param event: An event dict from the event service
            """
            message = event.get('message', ())
            if len(message):
                message = message[0]
            else:
                message = event['log_format']

            log_time = event.get('log_time')
            log_level = event.get('log_level', '')
            log_fmt = event.get('log_format', '')

            entry = [
                ('created', arrow.get(log_time).format(fmt='YYYY-MM-DDTHH:mm:ssZZ')),
                ('service', self._log_ident),
                ('level', log_level.name)
            ]
            if type(message) is dict:
                for k,v in message.items():
                    entry.append((k, v))
            else:
                try:
                    entry.append(('event', log_fmt.format(**event)))
                except Exception:
                    entry.append(('event', log_fmt))
            #
            #   Include any "bound" data from thread-local storage
            #
            if self._local.extra:
                for k,v in self._local.extra.items():
                    entry.append((k, v))
            #
            #   Access to the stack frame is expensive, we only want to do this for debug messages
            #   or in instances where we've hit an error.
            #
            if log_level in ['debug', 'error']:
                name = _getframe(4).f_globals['__name__']
                line = _getframe(4).f_lineno
                entry.append(('@', '{}#{}'.format(name, line)))
            #
            #   Render the error in order so it's usable / readable in the output window
            #
            def fmt(val):
                if type(val) == int:
                    return str(val)
                return str(val).replace('"', "'").replace('\n', ' ')

            print("{", end="")
            [print('"{0}": "{1}", '.format(v[0], fmt(v[1])), end="") for v in entry]
            print("}")

        #
        #   Choose an observer based on our choice of logging format
        #
        if self._log_format == 'text':
            log = Logger(observer=ons_logger_text)
            twisted.python.log.addObserver(ons_logger_text)
        else:
            log = Logger(observer=ons_logger_json)
            twisted.python.log.addObserver(ons_logger_json)

    def debug(self, *args, **kwargs):
        """
        This is just a wrapper function to set the log level and filter output
        """
        if self._log_level <= logging.DEBUG:
            log.debug(*args, **kwargs)
        return False

    def info(self, *args, **kwargs):
        """
        This is just a wrapper function to set the log level and filter output
        """
        if self._log_level <= logging.INFO:
            log.info(*args, **kwargs)
        return False

    def warning(self, *args, **kwargs):
        """
        This is just a wrapper function to set the log level and filter output
        """
        if self._log_level <= logging.WARNING:
            log.warn(*args, **kwargs)
        return False

    def error(self, e):
        """
        This is just a wrapper function to set the log level - we always log errors
        """
        log.error(e)
        return False

    def bind(self, extra):
        """
        Bind some additional logging information to the current request context

        :param key: A unique key to bind
        :param extra: The data to bind
        """
        self._local.extra = extra

    def unbind(self):
        """
        Unbind the additional information for the specified key

        :param key: A unique key to unbind
        """
        self._local.extra = None
