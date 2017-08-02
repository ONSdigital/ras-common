from pathlib import Path
from json import loads

class ONSInfo(object):

    def __init__(self, env):
        """
        Initialise the object with the parent environment

        :param env:
        """
        if Path('git_info').exists():
            with open('git_info') as io:
                self._info = loads(io.read())
        else:
            self._info = {}

        self._info = dict(self._info, **{'version': env.get('version', 'no version')})

    @property
    def health_check(self):
        return self._info

