Warning: this should not be used for production deployments.

Second warning: the Dockerfiles need improvement.

Third warning: this documentation is not complete.

/srv/debile is stored in a `data-only container`_: debile-data

 .. _data-only container: https://docs.docker.com/userguide/dockervolumes/#creating-and-mounting-a-data-volume-container

initial setup
-------------

Since you will build several images that will download the same packages, you can save time by using apt-cacher-ng.

 $ sudo apt-get install apt-cacher-ng

The sources.list in debile-master's and debile-slave's Dockerfile is
already setup to use apt-cacher.

Otherwise, you'll need to edit the ``sources.list`` files to use the
mirror of your choosing.

Docker runs as root, and the ``docker`` CLI program will need access
to docker's unix socket. If you don't want to run ``docker`` as root,
you can add your user to the group ``docker``:

 $ sudo adduser <your user> docker

For more information, `Giving non-root access`_ in docker's official
documentation for Debian users.

 .. _Giving non-root access:
    https://docs.docker.com/installation/debian/#giving-non-root-access

Building images
---------------

debile-data
~~~~~~~~~~~

This needs a tarball ``master-keys.tar.gz`` containing the PGP keys
for the master.  You can use this script:

 contrib/clemux/docker/debile-data $ ./debile-generate-master-pgp-keys

(Note: on a VM or headless server, this might take a while because of
a lack of entropy on the system. You might want to generate the keys
on a desktop machine, or use `haveged`_

.. _haveged: http://www.issihosts.com/haveged/

Then you can build the image:

 contrib/clemux/docker/debile-data $ docker build -t clemux/debile-data .


debile-master
~~~~~~~~~~~~~

This needs ``debile-master_1.3.2_all.deb``,
``python-debile_1.3.2_all.deb`` and
``python-firewoes_0.2+mux_all.deb`` in the same directory as
Dockerfile. You can build them from the debile git repository, with
`dpkg-buildpackage`.

You can find ``python-firewoes_0.2+mux_all.deb`` here:
http://www.mux.me/debile/python-firewoes_0.2+mux_all.deb

Or build it from https://github.com/clemux/firewoes, branch
``iterative_uniquify``.

Edit ``debile.yaml``.

Then you can build the image:

 contrib/clemux/docker/debile-master $ docker build -t clemux/debile-master .

debile-http
~~~~~~~~~~~

This should be straightforward. Systemd unit file also provided.

 $ docker build -t clemux/debile-http .

debile-pg
~~~~~~~~~

Same here:

 $ docker build -t clemux/debile-pg .

debile-slave
~~~~~~~~~~~~

This requires ``debile-slave_1.3.2_all.deb`` and ``python-debile_1.3.2_all.deb``.

Create slave-keys.tar.gz:

 $ ./debile-generate-slave-keys

Then edit ``slave.yaml``, and put the right fingerprint into the
``gpg`` section.

 $ docker build -t clemux/debile-slave .

A systemd unit file is provided: ``debile-slave.service``.

Running debile-master
---------------------

Creating the data volume container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This container will store /srv/debile. You only need to create it, and not run it:

 $ docker create --name debile-data -v /srv/debile clemux/debile-data


Running postgresql-server (debile-pg)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First you will need to run postgresql. If you're using systemd:

 $ sudo cp debile-postgresql.service /etc/systemd/system/
 
 $ sudo systemctl start debile-postgresql.service

Otherwise:

 $ docker run -d --name debile-pg -p 5432:5432 clemux/debile-pg

Initializing debile-master
~~~~~~~~~~~~~~~~~~~~~~~~~~

Run a temporary container:

 $ docker run -ti --rm --volumes-from debile-data --link debile-pg:debile-pg clemux/debile-master bash

Inside the container's shell:

 $ debile-master-init --config /etc/debile/master.yaml /etc/debile/debile.yaml


Running nginx (debile-http)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

With systemd:

 $ sudo cp nginx-debile.service /etc/systemd/system/

 $ sudo systemctl start nginx-debile.service

Otherwise:

 $ docker run -d --name debile-http --volumes-from debile-data -v /var/log/nginx -p 80:80 clemux/debile-http
