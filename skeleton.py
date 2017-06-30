##############################################################################
#                                                                            #
#   Micros-ervices header template                                           #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from ons_ras_common import ons_env




class skeleton(object):

    def hello_world():
        ons_env._case.post(category = 'COLLECTION_INSTRUMENT_DOWNLOADED', created_by = 'ME', party_id = 'MY_PARTY_ID', description = "MY DESC")
        return "Hello World!"
