Authentication between master and slaves
========================================

Secure authentication (TLS)
---------------------------

This is the default authentication backend, which is used when no
``--auth`` argument is passed to ``debile-master`` and
``debile-slave``.


Simple authentication (IP address)
----------------------------------

To use the simple authentication backend, run debile-master with

 $ debile-master --auth simple

and debile-slave with

 $ debile-slave --auth simple

To use debile-remote, you'll run into
https://github.com/opencollab/debile/issues/13. Patch welcome.

To add allow a slave connecting to debile-master.

 $ debile-remote create-slave-ip <name> <pgp-key> <ip address>
