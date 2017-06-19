### Version 0.1.26

[Testing ...]
* Adding SHIM capabilities, i.e. 'remote_ms' environment variable
* This version also has fully ASYNC registration

### Version 0.1.21

* Insert an operating system test for the importing of EPOLL
  (Mac doesn't have this)

### Version 0.1.20

* Repointed models_local to models

### Version 0.1.19

* Introducing callback function for activate

### Version 0.1.18

* Fixing Environment detection
* First fully working version for collection-instruments

### Version 0.1.9

* Debugging / fixing CF service array handler

### Version 0.1.8

* Rationalise logging in JWT
* Add cipher as an alias for crypt

### Version 0.1.7

* Adding missing database binding

### Version 0.1.6

* Adding missing reference to ons_env

### Version 0.1.5

* Re-adding missing "is_secure" property

### Version 0.1.4

* Separated 'setup' from 'activate' so unit tests can initialise the module without
  having toi run up a network listener.

