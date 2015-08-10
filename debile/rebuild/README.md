Debile Rebuild
==============

Debile Rebuild is a tool for rebuilding packages using the Debile
infrastructure.

Debile Rebuild is able to create a .dsc url to your friendly local mirror, and
fetch that exact version of the package. Debile Rebuild can then also use the
.dsc to forge a package_version_source.changes file, and sign it with an
autobuild key and upload it to the debile infrastructure.

This library is important to simplify the package upload into debile
infrastructure, and it is used to upload a set of packages and verify new
packages from incoming queue.

To upload package you must have a config file (/etc/debile-rebuild.ini) as you
can see below:

###############################################################
[config]
# Preferably a GPG auto key of yours to avoid repeatedly typing your passphrase
signing-key=B11A9FEC01B2B1F6C1C31DD4896AE222CC16515C
# Should be setup in your dput configuration
dput-target=debile
###############################################################

The dput target must be configured in ~/.dput.cf.

To use it you can call debile-upload like this:

$ debile-upload --dist=unstable --source=awesome --version=3.4.15-1 --group=test-packages
