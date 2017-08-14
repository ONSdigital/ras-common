"""

   Generic Configuration tool for Micro-Service environment discovery
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)

   ONSCase wraps routines used to access the case service

"""


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

    def my_surveys(self, party_id, filter):
        """
        Interrogate the surveys todo (aggregated endpoint) and get the data needed to build
        the my-surveys screen.

        :param party_id: The concerned party
        :param filter: An array of statuses that we're interested in
        :return: A dictionary containing all the stuff we need for my-surveys
        """
        return  self._env.asyncio.access_endpoint('/api/1.0.0/surveys/todo/{}'.format(party_id), params=filter)
