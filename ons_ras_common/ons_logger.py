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
        self._ident = self._env.get('my_ident', __name__, 'microservice')
        self._log_format = self._env.get('log_format', 'json')
        self._log_level = getattr(logging, self._env.get('log_level', 'INFO').upper(), 0)

        @provider(ILogObserver)
        def ons_logger(event):
            #try:
            #    stamp = arrow.get(event.get('time', 0)).format(fmt='YYYY-MM-DDTHH:mm:ssZZ')
            #except Exception as e:
            #    print(e)
            #    exit()

            log_time = event.get('log_time')
            log_level = event.get('log_level', '')
            log_format = event.get('log_format', '')

            #if self._log_format == 'text':
                #    _getframe(7).f_globals['__name__'],
                #    _getframe(7).f_lineno
            name="xx"
            line=0

            try:
                print('{} {}: [{}] {} @{}#{}'.format(
                    arrow.get(log_time).format(fmt='YYYY-MM-DDTHH:mm:ssZZ'),
                    self._ident,
                    log_level.name,
                    log_format,
                    name,
                    line
                ))
            except Exception as e:
                print(e)
            return




            print(event)
            print(type(event['log_format']))
            #message = event['message']
            #if len(message):
            #    message = message[0]

            #print(stamp,message)
            #print(formatEvent(event))

        global log
        log = Logger(observer=ons_logger)

        log.info({'event': 'Hello world', 'extra': 'More data'})


        def ons_logger(event):
            """
            Custom logger function fed from the Twisted Python Observer

            :param event: A Twisted event dictionary
            """
            print(event)
            return True

            print(dir(event))
            return

            try:
                stamp = arrow.get(event.get('time', 0)).format(fmt='YYYY-MM-DDTHH:mm:ssZZ')
            except Exception as e:
                print(e)
                exit()
            message = event['message']
            if len(message):
                message = message[0]
            #
            #   This is the text logger (debugging only)
            #
            if self._log_format == 'text':
                if type(message) is not dict:
                    message = event['log_format'].format(**event)

                #    _getframe(7).f_globals['__name__'],
                #    _getframe(7).f_lineno
                name="xx"
                line=0

                try:
                    print('{} {}: [{}] {} @{}#{}'.format(
                        stamp,
                        self._ident,
                        event['log_level'].name,
                        message, name, line
                    ))
                except Exception as e:
                    print(e)
                return
            #
            #   This is the JSON logger (production)
            #
            entry = [
                ('created', stamp),
                ('service', self._ident),
                ('level', event['log_level'].name),
            ]
            if type(message) is dict:
                for k,v in message.items():
                    entry.append((k, v))
            else:
                entry.append(('event', event['log_format'].format(**event)))
            #
            #   Access to the stack frame is expensive, we only want to do this for debug messages
            #   or in instances where we've hit an error.
            #
            if event['log_level'].name in ['debug', 'error']:
                entry.append(('@', '{}#{}'.format(_getframe(7).f_globals['__name__'], _getframe(7).f_lineno)))
            #
            #   Render the error in order so it's usable / readable in the output window
            #
            print("{", end="")
            [print('"{0}": "{1}", '.format(v[0], v[1].replace('"', "'").replace('\n', '')), end="") for v in entry]
            print("}")

        #twisted.python.log.addObserver(ons_logger)

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
