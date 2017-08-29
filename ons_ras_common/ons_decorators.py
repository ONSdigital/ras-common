"""

   ONS Digital JWT token handling
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)


   ons_decorators is a generic decorator library hopefully containing all of
   our custom decorators. i.e. any generic functionality you may wish to
   import into your micro-service.

"""
from . import ons_env
from functools import wraps
from flask import render_template
from contextlib import contextmanager
from uuid import uuid4


def validate_jwt(scope, request, on_error=None):
    """
    Validate the incoming JWT token, don't allow access to the endpoint unless we pass this test

    :param scope: A list of scope identifiers used to protect the endpoint
    :param request: The incoming request object
    :param on_error: The error structure
    :return: Exit variables from the protected function
    """
    def authorization_required_decorator(original_function):
        @wraps(original_function)
        def authorization_required_wrapper(*args, **kwargs):
            if not ons_env.is_secure:
                return original_function(*args, **kwargs)

            if ons_env.jwt.validate(scope, request.headers.get('authorization', '')):
                return original_function(*args, **kwargs)

            if not on_error:
                return "Access forbidden", 403

            return render_template(on_error.get('file'), _theme='default', data=on_error.get('error'))

        return authorization_required_wrapper
    return authorization_required_decorator


def jwt_session(request):
    """
    Validate an incoming session and only proceed with a decoded session if the session is valid,
    otherwise render the not-logged-in page.

    :param request: The current request object
    """
    def extract_session(original_function):
        @wraps(original_function)
        def extract_session_wrapper(*args, **kwargs):
            if 'authorization' in request.cookies:
                session = ons_env.jwt.decode(request.cookies['authorization'])
            else:
                session = None
            if not session:
                return render_template('not-signed-in.html', _theme='default', data={"error": {"type": "failed"}})
            return original_function(session, **kwargs)
        return extract_session_wrapper
    return extract_session


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

    # TODO: what's the point of this decorator? With the commented-out code, it doesn't do anything!
    def before_request_decorator(original_function):
        @wraps(original_function)
        def before_request_wrapper(*args, **kwargs):
            #if ons_env.logger.is_json:
            #    _bind_request_detail_to_log(request)
            return original_function(*args, **kwargs)

        return before_request_wrapper

    return before_request_decorator
