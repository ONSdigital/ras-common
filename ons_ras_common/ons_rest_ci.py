##############################################################################
#                                                                            #
#   Generic Routines for access to the collection instruments service        #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   ONSCollectionInstrument wraps access to the CI service
#
##############################################################################
from os import getenv

class ONSCollectionInstrument(object):
    """
    This class is designed to take all the work out of accessing the case service. Initially it
    should be able to validate and log events against the case service and also query the event
    service for specific combinations of events. (for example to determine case status)
    """
    def __init__(self, env):
        self._env = env
        self._get = '/collection-instrument-api/1.0.2/collectioninstrument/id'
        self._upload = '/collection-instrument-api/1.0.2/survey_responses'

    def activate(self):
        """"""
        api = getenv('ONS_API_CI', default=None)
        if api:
            self._env.asyncio.endpoint_init(api, self._get)
            self._env.asyncio.endpoint_init(api, self._upload)

    def get_by_id(self, instrument_id):
        """
        Recover an exercise by instrument_id

        :param instrument_id: The id of the exercise in question
        :return: An instrument record
        """
        instrument = self._env.asyncio.access_endpoint('{}/{}'.format(self._get, instrument_id))
        if not instrument:
            return 404, {'code': 404, 'text': 'unable to find instrument for this instrument_id'}

        return 200, {'code': 200, 'instrument': instrument}

    def upload(self, case_id, party_id, file_obj):

        try:
            upload = self._env.asyncio.post_upload(self._upload, case_id, file_obj)
            if  upload:
                # Post an authentication case event to the case service
                code, msg = self._env.case_service.post_event(case_id,
                                                category='SUCCESSFUL_RESPONSE_UPLOAD',
                                                created_by='TODO',
                                                party_id=party_id,
                                                description='Instrument response uploaded "{}"'.format(case_id))

                return code, {'code': code, 'text': msg}

            return 404, {'code': 404, 'text': 'unable to upload instrument'}
        except Exception as e:
            return 500, str(e)
