##############################################################################
#                                                                            #
#   Generic Configuration tool for Micro-Service environment discovery       #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSCase wraps routines used to access the case service
#
##############################################################################


class ONSCase(object):
    """
    This class is designed to take all the work out of accessing the case service. Initially it
    should be able to validate and log events against the case service and also query the event
    service for specific combinations of events. (for example to determine case status)
    """
    def __init__(self, env):
        self._env = env
        self._categories = None

    def activate(self):
        """"""
        pass

    def post_event(self, case_id, description=None, category=None, party_id=None, created_by=None, payload=None):
        """
        Post an event to the case service ...

        :param case_id: The Id if the case to post against
        :param description: Event description
        :param category: Event category (must be a valid category)
        :param party_id: Party Id
        :param created_by: Who created the event
        :param payload: An optional event payload
        :return: status, message
        """
        #
        #   Start by making sure we were given a working data set
        #
        if not (description and category and party_id and created_by):
            msg = 'description={} category={} party_id={} created_by={}'.format(
                description, category, party_id, created_by
            )
            self._env.logger.error('Insufficient arguments', arguments=msg)
            return 500, {'code': 500, 'text': 'insufficient arguments'}

        #
        #   If this is our first time, we need to acquire the current set of valid categories
        #   form the case service in order to validate the type of the message we're going to post
        #
        if not self._categories:
            self._env.logger.info('first pass :: caching event category list')
            categories = self._env.asyncio.access_endpoint('/categories')
            if not categories:
                return 404, {'code': 404, 'text': 'error loading categories'}
            self._categories = {}
            for cat in categories:
                action = cat.get('name')
                if action:
                    self._categories[action] = cat
                else:
                    self._env.logger.warn('received unknown category "{}"'.format(str(cat)))
            self._env.logger.info('first pass :: cached ({}) categories'.format(len(categories)))

        #
        #   Make sure the category we have is valid
        #
        if category not in self._categories:
            self._env.logger.error(error='invalid category code', category=category)
            return 404, {'code': 404, 'text': 'invalid category code - {}'.format(category)}

        #
        #   Build a message to post
        #
        message = {
            'description': description,
            'category': category,
            'partyId': party_id,
            'createdBy': created_by
        }
        #
        #   If we have anything in the optional payload, add it to the message
        #
        if payload:
            message = dict(message, **payload)

        #
        #   Call the poster, returning the actual status and text to the caller
        #
        code, msg = self._env.asyncio.post_route('/cases/{}/events'.format(case_id), message).wait(2)
        return code, msg

    def case_status(self, case_id):
        """
        Calculate the 'status' for a given case (for surveys/todo)

        :param case_id: the id of the case in question
        :return: the current status
        """
        case_events = self._env.asyncio.access_endpoint('/cases/{}/events'.format(case_id))

        if not case_events:
            return 404, {'code': 404, 'text': 'unable to find cases for this case_id'}

        def calculate_status():
            for event in case_events:
                self._env.logger.debug('A-Event category: {}'.format(event['category']))
                if event['category'] == 'SUCCESSFUL_RESPONSE_UPLOAD':
                    return 'Complete'
            for event in case_events:
                self._env.logger.debug('B-Event category: {}'.format(event['category']))
                if event['category'] == 'COLLECTION_INSTRUMENT_DOWNLOADED':
                    return 'In progress'
            return 'Not Started'

        return 200, {'code': 200, 'text': calculate_status()}

    def get_by_id(self, case_id):
        """
        Recover a case by case_id

        :param case_id: The case in question
        :return: A case record
        """
        case = self._env.asyncio.access_endpoint('/cases/{}'.format(case_id))
        if not case:
            return 404, {'code': 404, 'text': 'unable to find case for this case_id'}

        return 200, {'code': 200, 'case': case}






#    import crochet
#    import treq
#    from json import loads, dumps
#    from twisted.internet import defer

    #        """
#        Set up a base URL for future access to the case service (currently via the gateway)
#        """
#        self._base = '{}://{}:{}'.format(self._env.api_protocol, self._env.api_host, self._env.api_port)

#    def error(self, text):
#        return self._env.logger.error('[case] {}'.format(text))

#    def warn(self, text):
#        return self._env.logger.warn('[case] {}'.format(text))

#    def info(self, text):
#        return self._env.logger.info('[case] {}'.format(text))

#    @crochet.run_in_reactor
#    def get_route(self, endpoint):
#        """
#        Generic routine to hit a remote endpoint. This is set to run in the twisted reactor and will
#        be called with a 'crochet' wait. So it will either return the results of the call as a Python
#        structure after decoding with JSON, or it will raise an error (or timeout error).

#        :param endpoint: The URL we want to hit
#        :return: The decoded results of the hit
#        """
#        def check(response):
#            """
#            Make sure the call succeeded, otherwise raise an error which will abort the pipeline

#            :param response: A deferred response object
#            :return: A deferred response object
#            """
#            if response.code != 200:
#                raise Exception('Call to "{}" yielded error code "{}"'.format(url, response.code))
#            return response

#        def json(response):
#            """
#            Decode the response (from bytes to string) then convert to a Python dict

#            :param response: Response object
#            :return: results as a dict
#            """
#            return loads(response.decode())

#        def log(failure):
#            """
#            Just log the error, a return code of 'False' will be returned elsewhere
#            :param failure: A treq failure object
#            """
#            return self.error(failure.getErrorMessage())

 #       # Invoke a Twisted pipeline to hit the endpoint and process the results
 #       url = '{}{}'.format(self._base, endpoint)
 #       return treq.get(url).addCallback(check).addCallback(treq.content).addCallback(json).addErrback(log)

#    @crochet.run_in_reactor
#    def post_route(self, endpoint, payload):
#        """
#        Generic posting routine to send data to a remote endpoint.

#        :param endpoint: endpoint to hit
#        :param payload: data to send
#        :return: response object
#        """
#        @defer.inlineCallbacks
#        def check(response):
#            """
#            Make sure the call succeeded, otherwise raise an error which will abort the pipeline

#            :param response: A deferred response object
#            :return: A deferred response object
#            """
#            msg = yield response.text()
#            msg = loads(msg)
#            if response.code != 200:
#                self._env.logger.error('[case] Failed to post event', code=response.code, reason=str(msg))
#            return response.code, msg

#        url = '{}{}'.format(self._base, endpoint)
#        return treq.post(
#            url,
#            dumps(payload).encode('ascii'),
#            headers={b'Content-Type': [b'application/json']}
#        ).addCallback(check)

#    def access_endpoint(self, endpoint):
#        """
#        Wrapper for hit_endpoint with generic error checking and reporting.

#        :param endpoint: The endpoint we're going to hit relative to the API base (/)
#        :return: A valid result as a python dict, or False in the case of an error
#        """
#        try:
#            result = self.get_route(endpoint).wait(DEFAULT_TIMEOUT)
#        except crochet.TimeoutError:
#            """The call timed out, endpoint was probably unavailable!"""
#            return self._env.logger.error('Endpoint call timed out', endpoint=endpoint)
#        except Exception as e:
#            """Unexpected error!"""
#            return self._env.logger.error('Endpoint call failed', endpoint=endpoint, error=str(e))
#        return result
