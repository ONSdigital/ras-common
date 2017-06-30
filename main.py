##############################################################################
#                                                                            #
#   Microservices header template                                            #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from ons_ras_common import ons_env

if __name__ == '__main__':

    def callback(app):
        ons_env._case.post(category='CATEGORY')
        ons_env._case.post(category='CATEGORY', created_by='ME', party_id='MY_PARTY_ID', description="MY DESC")

    ons_env.activate(callback)
