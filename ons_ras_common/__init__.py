##############################################################################
#                                                                            #
#   Generic Configuration tool for Micro-Service environment discovery       #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
#
#   This is a common library package used to wrap standard ONS Micro-service
#   functionality. Specifically it covers the following aspects;
#
#   o Cloud Foundry startup
#   o Logging initialisation
#   o Database connections and automatic schema creation
#   o API Gateway registration
#
#   Utility routines provided include;
#
#   o JWT token encoding / decoding
#   o Generic cryptography (encryption / decryption)
#
##############################################################################
from .ons_environment import ONSEnvironment

__version__ = '0.1.53'


if 'ons_env' not in globals():
    ons_env = ONSEnvironment()
