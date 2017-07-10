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
import crochet
from twisted.internet import defer


class ONSCollectionInstrument(object):
    """
    This class is designed to take all the work out of accessing the case service. Initially it
    should be able to validate and log events against the case service and also query the event
    service for specific combinations of events. (for example to determine case status)
    """
    def __init__(self, env):
        self._env = env
        self._get = '/collection-instrument-api/1.0.2/collectioninstrument/id/{}'
        self._upload = '/collection-instrument-api/1.0.2/survey_responses/{}'

    def activate(self):
        """"""
        pass

    def get_by_id(self, instrument_id):
        """
        Recover an exercise by instrument_id

        :param instrument_id: The id of the exercise in question
        :return: An instrument record
        """
        instrument = self._env.asyncio.access_endpoint(self._get.format(instrument_id))
        if not instrument:
            return 404, {'code': 404, 'text': 'unable to find instrument for this instrument_id'}

        return 200, {'code': 200, 'instrument': instrument}

    def upload(self, case_id, file_obj):

        upload = self._env.asyncio.post_upload(self._upload, case_id, file_obj)
        if not upload:
            return 404, {'code': 404, 'text': 'unable to upload instrument'}

        return 200, {'code': 200, 'text': 'instrument posted'}
