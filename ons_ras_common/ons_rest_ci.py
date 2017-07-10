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

        payload = {'file': (file_obj.filename, file_obj.stream, file_obj.mimetype, {'Expires': 0})}
        upload = self._env.asyncio.post_route(self._upload.format(case_id), payload)
        if not upload:
            return 404, {'code': 404, 'text': 'unable to upload instrument'}

        return 200, {'code': 200, 'text': 'instrument posted'}


#    headers = {}
#    # Get the uploaded file
#    upload_file = request.files['file']
#    upload_filename = upload_file.filename
#    upload_file = {'file': (upload_filename, upload_file.stream, upload_file.mimetype, {'Expires': 0})}
    # Build the URL
#    url = Config.API_GATEWAY_COLLECTION_INSTRUMENT_URL + 'survey_responses/{}'.format(case_id)
#    logger.debug('upload_survey URL is: {}'.format(url))
    # Call the API Gateway Service to upload the selected file
#    result = requests.post(url, headers, files=upload_file, verify=False)

#    if result.status_code == 200:
#        logger.debug('Upload successful')
#        return render_template('surveys-upload-success.html', _theme='default', upload_filename=upload_filename)
#    else:
#        logger.debug('Upload failed')
#        error_info = json.loads(result.text)
#        return render_template('surveys-upload-failure.html',  _theme='default', error_info=error_info,
#                               case_id=case_id)
