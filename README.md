# ras-common
[![Build Status](https://travis-ci.org/ONSdigital/ras-common.svg?branch=twine)](https://travis-ci.org/ONSdigital/ras-common)
[![codecov](https://codecov.io/gh/ONSdigital/ras-common/branch/twine/graph/badge.svg)](https://codecov.io/gh/ONSdigital/ras-common)

This code is derived from work done as a part of Swagger-Codegen and the API Gateway. It's aim is to
standardise boilerplate code used by RAS Micro-Services and extricate as much infrastructure as possible
from the Micro-Service code bases. It should be possible (as demonstrated below) to implement a Micro-Service
in two lines of code (with a few text based configuration files) that is immediately deployable on Cloud Foundry.

This code WAS published on the Python Package Index here;
[https://pypi.python.org/pypi/ons-ras-common](https://pypi.python.org/pypi/ons-ras-common) but this is being obsoleted
in favour of using the GitHub "requirements" feature. i.e. the package is pulled in directly from GitHub rather than
via Pypi.

### The Modules

These modules are subject to continual change, but every effort will be made to maintain backwards compatibility
so no future additions should break Micro-Services already using the library. In the event something major *does*
change that breaks this model, it should be well documented on RAS_Developers. With a view to *not* being 
immediately subject to any breakage, the recommendation is that *pip freeze* is used to tag Micro-Service
implementations to specific versions of this library.

* ons_cloudfoundry

  This code is used to automatically detect the presence of Cloud Foundry and amend available environmnt
  variables accordingly. Useful properties include;
  
  * detected - True if we're running on Cloud Foundry
  
  This module will also update environment variables *db_name* and *db_connection* if there are any
  database service credentials available in VCAP_SERVICES.

* ons_cryptograpgher

  This provides *encrypt* and *decrypt* as standard functions, which are intended to be impelented by the
  platform recommended encryption routines. If you call these functions in preference to implementing your
  own encryption routine, should the platform recommendation change in the future, using the most recent
  version of this library should be the only change needed.

* ons_database

  Currently database access if provided via SQLAlchemy over a generic database driver, so within the bounds
  of current testing the driver in use is database agnostic. This code will interact with the local configuration
  file and the Cloud Foundry detection module and attempt to automatically connect up your database. There are
  some additional configuration options that allow you to automatically drop all tables on startup (useful for
  unit testing), and any missing tables are created from your in-code models. Current support includes both 
  Postgres and SQLite drivers.

* ons_decorators
    
  We are building a library of useful decorators, currently the focus of this module is *validate_jwt*. This
  can be added to a micro-service endpoint to ensure the endpoint is protected using the currently implemented
  JWT token authorization. There is a flag in the configuration file that can be used to turn this option off
  dynamically for testing purposes, and the same flag when applied to the API gateway will cause JWT tokens
  to be injected into headers as they pass through the gateway, also good for testing. (so there's no real
  excuse for 'not' protecting every endpoint as it's implemented)

* ons_environment

  The environment model wraps all the others together and provides access to them via a single global variable.
  To use the package, follow the following pattern;
  
  ```python
  from ons_ras_common import ons_env
  if __name__ == '__main__':
      ons_env.activate()
  ```
  There are many properties exposed by **ons_env** that provide access to the other underlying modules.
        
* ons_jwt

  Wraps the current implementation of our token authorization. The main function *validate* is called by the
  *validate_jwt* wrapper, but the other functions may be useful. This is likely to be extended in the near
  future with more functionality.

* ons_logger

  This is a functioning logging system, but currently a placeholder for the 'next generation' logger which will
  log in JSON format for the centralised Splunk logging infrastructure.

* ons_registration

  In order to become visible to the API gateway for the purposes of endpoint routing, Micro-Services need to
  register their endpoints (one way or another) with the gateway. This routine provides a connection, registration
  and keep-alive service for just that. The routines are generic and easy to replicate in other languages should
  the need arise.

* ons_swagger

  This is a very basic library for managing the local 'swagger' (or API specification) file. It's useful for
  extracting information (such as a list of endpoints) and re-writing parts of the file, for example to re-point
  the 'host' component.

* ons_rabbit

  This is a wrapper for RabbitMQ connections and works with the Cloud Foundry module to detect whether there is a
  Rabbit Queue available, and if there is, makes the credentials available as properties. i.e. if you have a queue
  installed you should have **onv_env.rabbit.**{*host,port,name,username,password*}. Alternatively you can put
  local defaults in your config.ini using **rabbit_**{*host,port,name,username,password*}. See the **development**
  section in this repo's config.ini for an example.

#### How to use this code

To set up a new Micro-Service you need the following lines of code;

  ```python
  from ons_ras_common import ons_env
  if __name__ == '__main__':
      ons_env.activate()
  ```

You will also need the **config.ini** as provided in this repository, and to be useful you also need a swagger.yaml
file. The location of this file can be set in your config.ini with **swagger =** .. the location of your file. 
Logging provided should point you in the right direction if this doesn't work.

### Using this code with Unit tests

This needs a little improvement, but currently you will (typically) need to call;
```python
ons_env.setup_ini()
ons_env.db.activate()
```
Rather than *activate*.

## Providing an installable package

When you have a change you wish to publish, follow these steps;

1. Update the version listed in setup.py
2. Update the version listed in ons_ras_common/__init__.py
3. Type "make"
4. git commit -a -m "(version number)" && git push

Don't forget to put a comment in *CHANGELOG.md* detailing the change.


## Example

Copy main.py from the repo and create a requirements.txt with the following line;
```bash
git+https://github.com/ONSdigital/ras-common.git@shim#ons_ras_common==0.1.82
```

Then;
```bash
$ .. (create config.ini and local.ini, sourced from the repo source)
$ virtualenv .build -p python3

Running virtualenv with interpreter .build/bin/python3
Using real prefix '/usr'
Installing setuptools, pkg_resources, pip, wheel...done.
(.build) $ source .build/bin/activate
(.build) $ pip install -r requirements.txt
(.. lots of depency stuff ..)

$ python3
Python 3.5.3 (default, Jan 19 2017, 14:11:04)
[GCC 6.3.0 20170118] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from ons_ras_common import ons_env
>>> ons_env.activate()
2017-06-21 08:43:29+0100 [-] Log opened.
2017-06-21 08:43:29+0100 [-] [log] Logger activated [environment=development]
2017-06-21 08:43:29+0100 [-] [cf] Platform: LOCAL (no CF detected)
2017-06-21 08:43:29+0100 [-] [db] [warning] [swagger_server/models/_models.py] file is missing
2017-06-21 08:43:29+0100 [-] [swagger] Swagger API NOT detected
2017-06-21 08:43:29+0100 [-] [crypto] Setting crypto key to "ONS_DUMMY_KEY"
2017-06-21 08:43:29+0100 [-] [reg] Activating service registration
2017-06-21 08:43:29+0100 [-] Site starting on 33751
2017-06-21 08:43:29+0100 [-] Starting factory <twisted.web.server.Site object at 0x7ff6ab840d30>
```

## v0.2+

Packages ras_config, ras_database, ras_error, ras_logger and util packages are introduced as of v0.2. The intent
of these changes are:
 
- Supply an immutable config object which can easily be used with Flask, and enables separation of environment
specifics from service code (i.e. 12-factor compliant). This relies on a yaml-format config file, a minimal example
of which is below.

- Provide a familiar means of interfacing with common concepts, including Flask config & logging.

As an example of using the new configuration approach and logger:

`Main Python module...`
```Python
import os
import structlog
from ons_ras_common.ras_logger.ras_logger import configure_logger
from ons_ras_common.ras_config.flask_extended import Flask

logger = structlog.get_logger()

if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_yaml(os.path.join(app.root_path, 'config/config.yaml'))
    
    configure_logger(app.config)

    from my_ras_service.views import my_view
    app.register_blueprint(my_view, url_prefix='/my_ras_service/v1')

    scheme, host, port = app.config['scheme'], app.config['host'], app.config['port']
    app.run(debug=app.config.get('debug'), port=port)

```

`And in some_other_module.py...`

```Python
from structlog import get_logger

logger = get_logger()

def some_function():
    logger.info('Doing some logging')
```

`config/config.yaml`
```Yaml
service:
    name: my-ras-service
    version: 1.0.0
    scheme: http
    host: 0.0.0.0
    port: 8080
```
