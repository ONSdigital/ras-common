##############################################################################
#                                                                            #
#   Microservices header template                                            #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from ons_ras_common import ons_env
from ons_ras_common.ons_decorators import jwt_session

if __name__ == '__main__':
    ons_env.activate()
