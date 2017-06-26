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
from uuid import uuid4


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


def _bind_request_detail_to_log(request):
    """
    Set up logging details for a request logger

    :param request: The request object to get our data from
    :return: None
    """
    ons_env.logger.logger.bind(
        tx_id=str(uuid4()),
        method=request.method,
        path=request.full_path
    )


def before_request(request):
    """
    Sets up request data before a transaction.

    :param request: The request object passed in
    :return: the original_function call
    """
    def before_request_decorator(original_function):
        @wraps(original_function)
        def before_request_wrapper(*args, **kwargs):
            if ons_env.logger.is_json:
                _bind_request_detail_to_log(request)
            return original_function(*args, **kwargs)
        return before_request_wrapper
    return before_request_decorator
