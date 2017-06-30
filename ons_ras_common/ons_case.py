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
from crochet import wait_for, no_setup
from json import loads
from uuid import UUID
import treq
from twisted.internet import reactor
from twisted.internet.error import UserError
no_setup()

class ONSCase(object):

    def __init__(self, env):
        self._env = env

    def activate(self):
        pass

    def error(self, text):
        self._env.logger.error('[case] {}'.format(text))

    def info(self, text):
        self._env.logger.info('[case] {}'.format(text))

    @wait_for(timeout=5)
    def _lookup_categories(self):

        def hit_route(params):

            self.info('Params={}'.format(params))

            def status_check(response):
                if response.code != 200:
                    self.error('Response code = {}'.format(response.code))
                    raise UserError(url)
                return response

            def json(response):
                categories = loads(response.decode())
                return categories

            url = '{protocol}://{host}:{port}{endpoint}'.format(**params)
            #url='http://ras-api-gateway-int.apps.mvp.onsclofo.uk:80/categories'
            self.info("URL={}".format(url))
            deferred = treq.request(method="GET", url=url)
            return deferred
#            return deferred.addCallback(status_check).addCallback(treq.content).addCallback(json)

        params = {
            'endpoint': '/categories',
            'protocol': self._env.api_protocol,
            'host': self._env.api_host,
            'port': self._env.api_port
        }
        return hit_route(params)


    def post(self, *args, description=None, category=None, party_id=None, created_by=None, payload=None):

        try:
            print(self._lookup_categories())
        except Exception as e:
            print(str(e))
            return False
        if not (description and category and party_id and created_by):
            self.error('insufficient arguments: description={} category={} party_id={} created_by={}'.format(
                description, category, party_id, created_by
            ))
            return False

        message = {
            'description': description,
            'category': category,
            'partyId': party_id,
            'createdBy': created_by
        }
        if payload:
            message = dict(message, **payload)

        print(message)
        return True
    #
    #   POST /cases/<caseid>/events
    #
    #{
    #    "description": "Initial creation of case",
    #    "category": "CASE_CREATED",
    #    "subCategory": null,
    #    "partyId": "3b136c4b-7a14-4904-9e01-13364dd7b972",
    #    "createdBy": "Fred Bloggs"
    #}

#    @wait_for(timeout=5)
#    def _lookup_exercise(self, exercise_id):

#        if exercise_id in self._exercise_cache:
#            return self._exercise_cache[exercise_id]

#        def hit_route(params):
#            def status_check(response):
#                if response.code != 200:
#                    raise UserError(url)
#                return response

#            def json(response):
#                exercise = loads(response.decode())
#                self._exercise_cache[exercise_id] = exercise
#                return exercise

#            url = '{protocol}://{host}:{port}{endpoint}'.format(**params)
#            deferred = treq.get(url)
#            return deferred.addCallback(status_check).addCallback(treq.content).addCallback(json)

#        params = {
#            'endpoint': '/collectionexercises/{}'.format(exercise_id),
#            'protocol': ons_env.api_protocol,
#            'host': ons_env.api_host,
#            'port': ons_env.api_port
#        }
#        return hit_route(params)
#        survey = self._get_survey(survey_id)
#        if not survey:
#            if reactor.running:
#                try:
#                    exercise = self._lookup_exercise(exercise_id)
#                    survey_id = exercise.get('surveyId', None)
#                except UserError as e:
#                    ons_env.logger.info('Error in survey lookup - {}'.format(str(e)))
#                    return 405, 'error looking up survey id'
#                except Exception as e:
#                    ons_env.logger.info('General exception: {}'.format(str(e)))
#                    return 500, 'error looking up survey id'
#            else:
#                try:
#                    survey_id = UUID(survey_id)
#                except Exception as e:
#                    ons_env.logger.error(e)
#                    return 500, 'invalid survey ID'
#            if not survey_id:
#                return 404, "unable to lookup exercise ID"#

#            survey = SurveyModel(survey_id=survey_id)
#            ons_env.db.session.add(survey)