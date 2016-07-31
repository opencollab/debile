# Create a Debile slave.
#
# VERSION   0.1
FROM        debian:sid
MAINTAINER  Clément Schreiner <clement@mux.me>
# OK. Enough about that. Let's take our pristine Debian image and
# add our key.

RUN mkdir -p /srv/debile/
RUN groupadd -r debile && useradd -r -g debile -d /srv/debile debile
RUN chown -R debile:debile /srv/debile

COPY sources.list /etc/apt/
COPY *.deb /tmp/

WORKDIR /tmp

RUN apt-get update && apt-get install -y python python-dput dput-ng python-firehose adduser python-debian python-requests python-yaml python-schroot

# Use a custom version of sbuild written by Léo Cavaillé that adds an
# option --use-schroot-session, which enables starting sbuild with an
# existing schroot session.
RUN apt-get build-dep --assume-yes sbuild
RUN apt-get source sbuild
COPY support-for-schroot-sessions.patch /tmp/
RUN cd sbuild-* && cp ../support-for-schroot-sessions.patch . && \
    patch -p1 < ../support-for-schroot-sessions.patch && \
    dpkg-buildpackage -us -uc -nc
RUN (dpkg --install *sbuild*.deb || true)
RUN apt-get --assume-yes --fix-broken install

RUN dpkg -i python-debile*.deb debile-slave*.deb

RUN sbuild-adduser debile

RUN chown -R debile:debile /etc/debile/*

COPY slave.yaml /etc/debile/

USER debile

COPY slave-keys.tar.gz /tmp/

RUN sh -c "tar xvf slave-keys.tar.gz -O | gpg --import --status-fd 1"

CMD debile-slave --debug --auth simple
