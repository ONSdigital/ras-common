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
import twisted
import arrow
#from twisted.python import log
from sys import _getframe
from zope.interface import provider
from twisted.logger import Logger, ILogObserver, formatEvent
log = None



#'format': '%(log_legacy)s'' \
#''log_logger': <Logger 'twisted.python.log'>
#'log_format': '{log_io}'' \
#''system': '-'' \
#''log_io': '"127.0.0.1" - - [13/Jul/2017:20:16:31 +0000] "GET /static/img/favicon.ico HTTP/1.1" 404 233 "http://localhost:5001/sign-in" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36"',
#'isError': 0,
#'log_source': None,
#'log_namespace': 'twisted.python.log',
#'log_level': <LogLevel=info>,
#'log_time': 1499976991.7132602,
#'time': 1499976991.7132602,
# 'message': (),
#'log_legacy': <twisted.logger._stdlib.StringifiableFromEvent object at 0x7fc8aa64c8d0>}

LEVELS = {
    10: 'ingo'
}


class ONSLogger(object):
    """
    Generic logging module mock in advance of the real module ...
    """
    def __init__(self, env):
        self._env = env
        self._log_format = 'text'
        self._log_level = 0
        self._ident = '~~ none ~~'

    def activate(self):
        """
        Activate the logging systems ...
        """
        global log

        self._ident = self._env.get('my_ident', __name__, 'microservice')
        self._log_format = self._env.get('log_format', 'json')
        self._log_level = getattr(logging, self._env.get('log_level', 'INFO').upper(), 0)

        @provider(ILogObserver)
        def ons_logger_text(event):
            try:
                log_time = event.get('log_time')
                log_level = event.get('log_level', '')
                log_format = event.get('log_format', '')
                name = _getframe(4).f_globals['__name__']
                line = _getframe(4).f_lineno
                print('{} {}: [{}] {} @{}#{}'.format(
                    arrow.get(log_time).format(fmt='YYYY-MM-DDTHH:mm:ssZZ'),
                    self._ident,
                    log_level.name,
                    log_format.format(**event),
                    name,
                    line
                ))
            except Exception as e:
                print(e)

        @provider(ILogObserver)
        def ons_logger_json(event):
            """
            Observation logger (JSON format)

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
                ('service', self._ident),
                ('level', log_level.name)
            ]
            if type(message) is dict:
                for k,v in message.items():
                    entry.append((k, v))
            else:
                try:
                    entry.append(('event', event['log_format'].format(**event)))
                except Exception:
                    entry.append(('event', event['log_format']))

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

        if self._log_format == 'text':
            log = Logger(observer=ons_logger_text)
            twisted.python.log.addObserver(ons_logger_text)
        else:
            log = Logger(observer=ons_logger_json)
            twisted.python.log.addObserver(ons_logger_json)

        log.debug({'event': 'Hello world', 'extra': 'More data'})

    def debug(self, *args, **kwargs):
        if self._log_level <= logging.DEBUG:
            log.debug(*args, **kwargs)
        return False

    def info(self, *args, **kwargs):
        if self._log_level <= logging.INFO:
            log.info(*args, **kwargs)
        return False

    def warning(self, *args, **kwargs):
        if self._log_level <= logging.WARNING:
            log.warn(*args, **kwargs)
        return False

    def error(self, e):
        log.error(e)
        return False
