##############################################################################
#                                                                            #
#   ONS Digital JWT token handling                                           #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ons_decorators is a generic decorator library hopefully containing all of
#   our custom decorators. i.e. any generic functionality you may wish to
#   import into your micro-service.
#
##############################################################################
from . import ons_env
from functools import wraps


def validate_jwt(scope, request):
    """
    Validate the incoming JWT token, don't allow access to the endpoint unless we pass this test

    :param scope: A list of scope identifiers used to protect the endpoint
    :param request: The incoming request object
    :return: Exit variables from the protected function
    """
    def authorization_required_decorator(original_function):
        @wraps(original_function)
        def authorization_required_wrapper(*args, **kwargs):
            if not ons_env.is_secure:
                return original_function(*args, **kwargs)
            if ons_env.jwt.validate(scope, request.headers.get('authorization', ''), request):
                return original_function(*args, **kwargs)
            return "Access forbidden", 403
        return authorization_required_wrapper
    return authorization_required_decorator
