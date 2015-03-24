Debile
======

Debile is a Debian build system. It's reduced, minimal and
purely implemented in modern Python. This allows folks to use debile
as a platform to aid with building debs, or running custom tooling
against debs or debian source packages.

Debile isn't useful for many "normal" situations, other tools, such as
sbuild, or pbuilder will do much better when used directly by simple shell
scripts. It's also not great as a buildd, check out wanna-build if you're
interested in a big professional setup.

Quick setup for development, using Docker
=========================================

Debile is currently quite difficult to install. If you want to set it
up quickly and start hacking immediately, you can use
[docker](https://docs.docker.com/articles/basics/).

Some *Dockerfile*s for *debile-master*, *debile-slave* and the required
services are provided in contrib/clemux/docker. Both the *Dockerfile*s
and documentation need more work, so don't hesitate to ask for help on
[#debile](irc://irc.debian.org/debile) (irc.debian.org), or send an email to clement@mux.me and
sylvestre@debian.org.


Postgresql install
==================

$ sudo -u postgres createuser debile

$ sudo -u postgres psql -c "ALTER USER debile WITH PASSWORD 'foobar';"

$ sudo -u postgres createdb -E UTF-8 -O debile debile

For the tests:

$ sudo -u postgres createdb -E UTF-8 -O debile debile_tests

Run tests
=========

$ apt-get install python-nose

$ nosetests

Run flake8
==========

(see .travis.yaml)

 $ flake8 debile/ --ignore E711,E241 --max-line-length=200

Fedmsg Topics
=============

All topics are under:

    org.anized.{dev,sage,prod}.debile
    `-- source
    |   |-- accept
    |   |-- reject
    |
    `-- binary
    |   |-- accept
    |   |-- reject
    |
    `-- job
    |   |-- start
    |   |-- complete
    |   |-- abort
    |
    `-- result
        |-- receive
