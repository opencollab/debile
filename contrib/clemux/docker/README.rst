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

This container will store debile-master's data: settings, upload queue, result
of build/QA checks jobs.

This needs a tarball ``master-keys.tar.gz`` containing the PGP keys
for the master.  You can use this script:

 contrib/clemux/docker/debile-data $ ./debile-generate-master-pgp-keys

(Note: on a VM or headless server, this might take a while because of
a lack of entropy on the system. You might want to generate the keys
on a desktop machine, or use `haveged`_

.. _haveged: http://www.issihosts.com/haveged/

You will need to edit reprepo-conf/distributions: change 'SignWith' to
the id of the pgp key you generated.

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

This container provides a nginx server for:

- accessing the repository of packages built by debile
  
- providing a WebDAV access to the UploadQueue, for use with dput and its http
  upload method.

This should be straightforward. Systemd unit file also provided.

 $ docker build -t clemux/debile-http .

debile-pg
~~~~~~~~~

This container provides a postgresql server for use by debile-master.

Same here:

 $ docker build -t clemux/debile-pg .

debile-slave
~~~~~~~~~~~~

This container provides an instance of debile-slave, which will connect to
debile-master and receive jobs (build or QA checks).

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

This container will store /srv/debile. It will exit immediately, but the data will live as long as you don't delete the container (docker rm debile-data).

 $ docker run --name debile-data -v /srv/debile clemux/debile-data


Running postgresql-server (debile-pg)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First you will need to run postgresql. If you're using systemd:

 $ sudo cp postgresql-debile.service /etc/systemd/system/
 
 $ sudo systemctl start postgresql-debile.service

Otherwise:

  $ docker run -d --name debile-pg -p 5432:5432 clemux/debile-pg

Note: this will expose the container's port 5432 to the host. If you want to
expose that port on some other port of the host, the syntax is:

  -p HOSTPORT:CONTAINERPORT

Initializing debile-master
~~~~~~~~~~~~~~~~~~~~~~~~~~

Run a temporary container:

 $ docker run -ti --rm --volumes-from debile-data --link debile-pg:debile-pg clemux/debile-master bash

Inside the container's shell:

 $ debile-master-init --config /etc/debile/master.yaml /etc/debile/debile.yaml

You can test whether it worked, or make manual modifications to the
database:

On the host (password 'debile'):

 $ psql -h localhost -U debile -d debile -W

 debile=#

Running debile-master
~~~~~~~~~~~~~~~~~~~~~

With systemd:

 $ sudo cp debile-master.service /etc/systemd/system/

 $ systemctl start debile-master.service

Otherwise:

 $ docker run --name debile-master --volumes-from debile-data --link debile-pg:debile-pg clemux/debile-master


Running nginx (debile-http)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

With systemd:

 $ sudo cp nginx-debile.service /etc/systemd/system/

 $ sudo systemctl start nginx-debile.service

Otherwise:

  $ docker run -d --name debile-http --volumes-from debile-data -v /var/log/nginx -p 80:80 clemux/debile-http

  As for the postgres container, you can change the host port which will point to the container's nginx server, for example:

  -p 8080:80

will expose the ngix port on the host as 8080. 

Running debile-slave
--------------------

 $ docker run --name debile-slave --link debile-master:debile-master --link debile-http:debile-http clemux/debile-slave

 Tip: If you get authentication failure similar to this: 
      <Slave ip address> - - [11/Aug/2015 05:46:28] code 401, message Authentication failed
      update ip address of debile-slave in builders table of database.
