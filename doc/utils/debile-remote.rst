debile-remote usage
===================

This CLI tool is used to manage all the slaves from master.

create-user, update-user-keys
-----------------------------

The PGP key must be ASCII. Use gpg --export --armor.

How to activate new plugins
---------------------------

To activate a new plugin in slave(s) you need to set the new plugin in database
passing where it must work on (source, binary or build) as argument:

 $ debile-remote set-check <check-name> [source] [binary] [build]

Note that you can set your plugin to work on in only one or more of them.

After, we need to enable plugin for a given group and suite:

 $ debile-remote enable-check <check-name> <group> <suite>

Done. Now your plugin works in slave(s) :-)

How to create user with simple authentication
---------------------------------

Just execute the command below:

 $ debile-remote create-user-ip <name> <email> <pgp_file> <ip_address>

where <pgp_file> should be a file that contains your exported pgp public key.
