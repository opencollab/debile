Debile Rebuild
==============

Debile Rebuild is a tool for rebuilding packages using the Debile
infrastructure

Debile Rebuild is able to create a .dsc url to your friendly local mirror, and
fetch that exact version of the package. Debile Rebuild can then also use the
.dsc to forge a package_version_source.changes file, and sign it with an
autobuild key and upload it to the debile infrastructure.
