##############################################################################
#                                                                            #
#   Generic ASYNC IO Routines for accessing remote REST endpoints            #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSAsyncIO wraps generic endpoint access routines
#
##############################################################################
import crochet
import treq
from json import loads, dumps
from twisted.internet import defer
#
#   How long (by default) do we wait for an endpoint call before we timeout?
#
DEFAULT_TIMEOUT = 3


class ONSAsyncIO(object):
    """
    This class is designed to take all the work out of accessing the case service. Initially it
    should be able to validate and log events against the case service and also query the event
    service for specific combinations of events. (for example to determine case status)
    """
    def __init__(self, env):
        self._env = env
        self._bases = None

    def activate(self):
        """
        Set up a base URL for future access to the case service (currently via the gateway)
        """
        self._bases = {}

    def get_base(self, endpoint):
        """
        Get a base reference for a given endpoint. Initially we're pointing at the gateway but allow
        provision for holding direct routes to multiple micro-service, either by static routing or by
        route discovery from the Gateway.

        :param endpoint: endpoint we're about to call
        :return: the base reference for the endpoint
        """
        if endpoint not in self._bases:
            self._bases[endpoint] = '{}://{}:{}'.format(self._env.api_protocol, self._env.api_host, self._env.api_port)
            self._env.logger.info('[++] Setting base for "{}" to "{}"'.format(endpoint, self._bases[endpoint]))

        return self._bases[endpoint]

    @crochet.run_in_reactor
    def get_route(self, endpoint):
        """
        Generic routine to hit a remote endpoint. This is set to run in the twisted reactor and will
        be called with a 'crochet' wait. So it will either return the results of the call as a Python
        structure after decoding with JSON, or it will raise an error (or timeout error).

        :param endpoint: The URL we want to hit
        :return: The decoded results of the hit
        """
        def check(response):
            """
            Make sure the call succeeded, otherwise raise an error which will abort the pipeline

            :param response: A deferred response object
            :return: A deferred response object
            """
            if response.code != 200:
                raise Exception('Call to "{}" yielded error code "{}"'.format(url, response.code))
            return response

        def json(response):
            """
            Decode the response (from bytes to string) then convert to a Python dict

            :param response: Response object
            :return: results as a dict
            """
            return loads(response.decode())

        def log(failure):
            """
            Just log the error, a return code of 'False' will be returned elsewhere
            :param failure: A treq failure object
            """
            return self._env.logger.error('[asyncio-error] {}'.format(failure.getErrorMessage()))

        # Invoke a Twisted pipeline to hit the endpoint and process the results
        url = '{}{}'.format(self.get_base(endpoint), endpoint)
        return treq.get(url).addCallback(check).addCallback(treq.content).addCallback(json).addErrback(log)

    @crochet.run_in_reactor
    def post_route(self, endpoint, payload):
        """
        Generic posting routine to send data to a remote endpoint.

        :param endpoint: endpoint to hit
        :param payload: data to send
        :return: response object
        """
        @defer.inlineCallbacks
        def check(response):
            """
            Make sure the call succeeded, otherwise raise an error which will abort the pipeline

            :param response: A deferred response object
            :return: A deferred response object
            """
            msg = yield response.text()
            msg = loads(msg)
            if response.code > 299:
                self._env.logger.error('[case] Failed to post event', code=response.code, reason=str(msg))
            return response.code, msg

        url = '{}{}'.format(self.get_base(endpoint), endpoint)
        return treq.post(
            url,
            dumps(payload).encode('ascii'),
            headers={b'Content-Type': [b'application/json']}
        ).addCallback(check)

    def access_endpoint(self, endpoint):
        """
        Wrapper for hit_endpoint with generic error checking and reporting.

        :param endpoint: The endpoint we're going to hit relative to the API base (/)
        :return: A valid result as a python dict, or False in the case of an error
        """
        self._env.logger.info('[endpoint] {}'.format(endpoint))
        try:
            result = self.get_route(endpoint).wait(DEFAULT_TIMEOUT)
        except crochet.TimeoutError:
            """The call timed out, endpoint was probably unavailable!"""
            return self._env.logger.error('Endpoint call timed out', endpoint=endpoint)
        except Exception as e:
            """Unexpected error!"""
            return self._env.logger.error('Endpoint call failed', endpoint=endpoint, error=str(e))
        return result


    @crochet.run_in_reactor
    def post_upload(self, endpoint, case_id, upload_file):
        """
        """
        @defer.inlineCallbacks
        def check(response):
            """
            Make sure the call succeeded, otherwise raise an error which will abort the pipeline

            :param response: A deferred response object
            :return: A deferred response object
            """
            msg = yield response.text()
            msg = loads(msg)
            if response.code > 299:
                self._env.logger.error('[case] Failed to post event', code=response.code, reason=str(msg))
            return response.code, msg

        #upload_filename = upload_file.filename
        #upload_file = {'file': (upload_filename, upload_file.stream, upload_file.mimetype, {'Expires': 0})}
        #url = Config.API_GATEWAY_COLLECTION_INSTRUMENT_URL + 'survey_responses/{}'.format(case_id)

        #result = requests.post(url, headers, files=upload_file, verify=False)

        #    if result.status_code == 200:
        #        logger.debug('Upload successful')
        #        return render_template('surveys-upload-success.html', _theme='default', upload_filename=upload_filename)
        #    else:
        #        logger.debug('Upload failed')
        #        error_info = json.loads(result.text)
        #        return render_template('surveys-upload-failure.html',  _theme='default', error_info=error_info,
        #                               case_id=case_id)



        url = '{}{}/{}'.format(self.get_base(endpoint), endpoint, case_id)
        self._env.logger.info('[##] call "{}"'.format(url))
        files = {upload_file.filename: upload_file}
        headers = {b'Content-Type': [b'application/json']}
        data = {'name': upload_file.filename, 'filename': upload_file.filename}
        return treq.post(url, data=data, files = files, headers=headers).addCallback(check)
