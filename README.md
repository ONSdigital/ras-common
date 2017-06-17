# ras-common
[![Build Status](https://travis-ci.org/ONSdigital/ras-collection-instrument-demo.svg?branch=master)](https://travis-ci.org/ONSdigital/ras-common?branch=twine)

This code is derived from work done as a part of Swagger-Codegen and the API Gateway. It's aim is t
standardise boilerplate code used by RAS Micro-Services and extricate as much infrastructure as possible
from the Micro-Service code bases. It should be possible (as demonstrated below) to implement a Micro-Service
in two lines of code (with a few text based configuration files) that is immediately deployable on Cloud Foundry.

This code is published on the Python Package Index here;
[https://pypi.python.org/pypi/ons-ras-common](https://pypi.python.org/pypi/ons-ras-common)

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

## Pushing to PyPi

You will need some credentials that are authorized on the account, these need to go into a files
in your home folder called **.pypirc**;

```ini
[distutils]
index-servers = 
  pypitest
  pypi

[pypitest]
repository = https://testpypi.python.org/pypi
username = (username)
password = (password)

[pypi]
repository = https://pypi.python.org/pypi
username = (username)
password = (password)
```

You can only ever push one version ONCE, to do this you need to change the __version__ header in
setup.py, then the matching __version__ in ons_ras_common/__init__.py, then you need to add an entry
to *CHANGELOG.md* detailing the change. To actually make the push;
```bash
make test && make install
```

Expect it to take between 20 seconds and 5 mins for the new version to be visible via **pip**.


## Example

```bash
$ .. (create config.ini and local.ini, sourced from the repo source)
$ virtualenv .build -p python3

Running virtualenv with interpreter .build/bin/python3
Using real prefix '/usr'
Installing setuptools, pkg_resources, pip, wheel...done.
(.build) $ source .build/bin/activate
(.build) $ pip install ons_ras_common
Collecting ons_ras_common
  Downloading ons_ras_common-0.1.1.tar.gz

(.. lots of depency stuff ..)
Successfully built ons-ras-common
Installing collected packages: attrs, six, Automat, certifi, chardet, click, PyYAML, clickclick, jsonschema, inflection, itsdangerous, MarkupSafe, Jinja2, Werkzeug, Flask, typing, swagger-spec-validator, idna, urllib3, requests, connexion, constantly, ecdsa, Flask-Cors, incremental, zope.interface, hyperlink, Twisted, observable, Flask-Twisted, future, psycopg2, pycrypto, python-jose, SQLAlchemy, ons-ras-common
Successfully installed Automat-0.6.0 Flask-0.12.2 Flask-Cors-3.0.2 Flask-Twisted-0.1.2 Jinja2-2.9.6 MarkupSafe-1.0 PyYAML-3.12 SQLAlchemy-1.1.10 Twisted-17.5.0 Werkzeug-0.12.2 attrs-17.2.0 certifi-2017.4.17 chardet-3.0.4 click-6.7 clickclick-1.2.1 connexion-1.1.10 constantly-15.1.0 ecdsa-0.13 future-0.16.0 hyperlink-17.1.1 idna-2.5 incremental-17.5.0 inflection-0.3.1 itsdangerous-0.24 jsonschema-2.6.0 observable-0.3.2 ons-ras-common-0.1.1 psycopg2-2.7.1 pycrypto-2.6.1 python-jose-1.3.2 requests-2.17.3 six-1.10.0 swagger-spec-validator-2.1.0 typing-3.6.1 urllib3-1.21.1 zope.interface-4.4.1

(.build) $ python3
Python 3.5.3 (default, Jan 19 2017, 14:11:04)
[GCC 6.3.0 20170118] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from ons_ras_common import ons_env
>>> ons_env.activate()
2017-06-14 09:14:08+0100 [-] Log opened.
2017-06-14 09:14:08+0100 [-] [log] Logger activated [environment=development]
2017-06-14 09:14:08+0100 [-] [cf] Platform: LOCAL (no CF detected)
2017-06-14 09:14:08+0100 [-] [db] [warning] [swagger_server/models_local/_models.py] file is missing
2017-06-14 09:14:08+0100 [-] [swagger] Swagger API NOT detected
2017-06-14 09:14:08+0100 [-] [crypto] Setting crypto key to "ONS_DUMMY_KEY"
2017-06-14 09:14:08+0100 [-] [reg] Activating service registration
2017-06-14 09:14:08+0100 [-] [reg] ping failed for "http://localhost:8080/api/1.0.0/ping/localhost/59733"
2017-06-14 09:14:08+0100 [-] [reg] ping return = "<urllib3.connection.HTTPConnection object at 0x7fd08c387278>: Failed to establish a new connection: [Errno 111] Connection refused"
2017-06-14 09:14:08+0100 [-] Site starting on 59733
2017-06-14 09:14:08+0100 [-] Starting factory <twisted.web.server.Site object at 0x7fd08c387e80>
2017-06-14 09:14:13+0100 [-] [reg] ping failed for "http://localhost:8080/api/1.0.0/ping/localhost/59733"
2017-06-14 09:14:13+0100 [-] [reg] ping return = "<urllib3.connection.HTTPConnection object at 0x7fd08c11fb70>: Failed to establish a new connection: [Errno 111] Connection refused"
```

