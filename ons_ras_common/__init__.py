"""

   Generic Configuration tool for Micro-Service environment discovery
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)

"""
for item in list(globals()):
    print(item)
if 'ons_env' not in globals():
    from .ons_version import __version__
    from .ons_environment import ONSEnvironment
    ons_env = ONSEnvironment()
