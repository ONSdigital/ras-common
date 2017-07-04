##############################################################################
#                                                                            #
#   Micros-ervices header template                                           #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from ons_ras_common import ons_env
from flask import request, jsonify, make_response


class Skeleton(object):

    @staticmethod
    def hello_world():
        case_id = 'ab548d78-c2f1-400f-9899-79d944b87300'
        exercise_id = ''
        #code, msg = ons_env.case_service.post_event(case_id,
        #    category='COLLECTION_INSTRUMENT_DOWNLOADED',
        #    created_by='ME',
        #    party_id='db036fd7-ce17-40c2-a8fc-932e7c228397',
        #    description="MY DESC")

        #code, msg = ons_env.case_service.case_status(case_id)

        #code, msg = ons_env.case_service.get_by_id(case_id)
        code, msg = ons_env.exercise_service.get_by_id(exercise_id)

        return make_response(jsonify(msg), code)

