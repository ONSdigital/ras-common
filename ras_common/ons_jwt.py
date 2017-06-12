##############################################################################
#                                                                            #
#   ONS Digital JWT token handling                                           #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from jose import jwt, JWTError
from datetime import datetime
from sys import _getframe
from logging import WARN, INFO, ERROR


class ONSJwt(object):

    def __init__(self, env):
        self._env = env
        self._algorithm = None
        self._secret = None

    def activate(self):
        """
        Read in defaults from the config.ini
        """
        self._algorithm = self._env.jwt_algorithm
        self._secret = self._env.jwt_secret

    def report(self, lvl, msg):
        """
        Report an issue to the external logging infrastructure
        :param lvl: The log level we're outputting to
        :param msg: The message we want to log
        :return:
        """
        line = _getframe(1).f_lineno
        name = _getframe(1).f_code.co_name
        ons_env.logger.log(lvl, "{}: #{} - {}".format(name, line, msg))
        return False

    def encode(self, data):
        """
        Function to encode python dict data
        :param: The data to convert into a token
        :return: A JWT token
        """
        return jwt.encode(data, self._secret, algorithm=self._algorithm)

    def decode(self, token):
        """
        Function to decode python dict data
        :param: token - the token to decode
        :return: the decrypted token in dict format
        """
        return jwt.decode(token, self._secret, algorithms=[self._algorithm])

    def validate(self, scope, jwt_token, request):
        """
        This function checks a jwt token for a required scope type.
        :param scope: The scopes to test against
        :param jwt_token: The incoming request object
        :param request: The incoming request
        :return: Token is value, True or False
        """
        for entry in request.headers:
            self.report(INFO, "=>{}".format(entry))

        self.report(INFO, 'validating token "{}" for scope "{}"'.format(jwt_token, scope))
        try:
            token = self.decode(jwt_token)
        except JWTError:
            return self.report(ERROR, 'unable to decode token "{}"'.format(jwt_token))
        #
        #   Make sure the token hasn't expired on us ...
        #
        now = datetime.now().timestamp()
        if now >= token.get('expires_at', now):
            return self.report(WARN, 'token has expired "{}"'.format(token))
        #
        #   See if there is an intersection between the scopes required for this endpoint
        #   end and the scopes available in the token.
        #
        if not set(scope).intersection(token.get('scope', [])):
            return self.report(WARN, 'unable to validate scope for "{}"'.format(token))
        self.report(INFO, 'validated scope for "{}"'.format(token))
        return True
