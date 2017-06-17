##############################################################################
#                                                                            #
#   ONS Digital JWT token handling                                           #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from jose import JWTError
from jose.jwt import encode, decode
from datetime import datetime


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

    def debug(self, text):
        self._env.logger.debug('[jwt] {}'.format(text))

    def warn(self, text):
        self._env.logger.warn('[jwt] {}'.format(text))

    def encode(self, data):
        """
        Function to encode python dict data
        :param: The data to convert into a token
        :return: A JWT token
        """
        return encode(data, self._secret, algorithm=self._algorithm)

    def decode(self, token):
        """
        Function to decode python dict data
        :param: token - the token to decode
        :return: the decrypted token in dict format
        """
        return decode(token, self._secret, algorithms=[self._algorithm])

    def validate(self, scope, jwt_token):
        """
        This function checks a jwt token for a required scope type.
        :param scope: The scopes to test against
        :param jwt_token: The incoming request object
        :return: Token is value, True or False
        """
        self.debug('validating token "{}" for scope "{}"'.format(jwt_token, scope))
        try:
            token = self.decode(jwt_token)
        except JWTError:
            return self.warn('unable to decode token "{}"'.format(jwt_token))
        #
        #   Make sure the token hasn't expired on us ...
        #
        now = datetime.now().timestamp()
        if now >= token.get('expires_at', now):
            return self.warn('token has expired "{}"'.format(token))
        #
        #   See if there is an intersection between the scopes required for this endpoint
        #   end and the scopes available in the token.
        #
        if not set(scope).intersection(token.get('scope', [])):
            return self.warn('unable to validate scope for "{}"'.format(token))
        self.debug('validated scope for "{}"'.format(token))
        return True
