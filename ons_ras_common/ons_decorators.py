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
            return original_function(session)
        return extract_session_wrapper
    return extract_session


@contextmanager
def _bind_logger(request):
    """
    For local use only, referenced by 'before_request', essentially this information
    is included in each logger event within the request context so you can match up log
    events that relate to any given endpoint request. This is useful in an environment where
    you're logging against multiple concurrent requests which may produce interleaved entries
    in the log output.

    :param request: A standard request object
    """
    #try:
    ons_env.logger.bind({
        'tx_id': str(uuid4()),
        'method': request.method,
        'path': request.full_path
    })
    yield
    #finally:
    ons_env.logger.unbind()


def before_request(request):
    """
    Binds additional logging information to the logger within the context of this
    request. Data is stored on a thread-local basis to play nice with WSGI.

    :param request: The request object passed in
    :return: the result of the passed function
    """
    def before_request_decorator(original_function):
        @wraps(original_function)
        def before_request_wrapper(*args, **kwargs):
            with _bind_logger(request) as binder:
                result = original_function(*args, **kwargs)
            return result
        return before_request_wrapper
    return before_request_decorator
