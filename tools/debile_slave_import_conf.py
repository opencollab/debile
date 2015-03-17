#!/usr/bin/env python
#
# Copyright (c) Paul R. Tagliamonte <paultag@debian.org>, 2014
# Copyright (c) Clement Schreiner   <clement@mux.me>, 2015
# under the terms and conditions of the Debile project, MIT/Expat. You
# should have recieved a copy of the license with this script.
#
# Ohkay, a few jobs. We need to digest the .tar.gz and write the values
# we care about to /etc/debile/slave.yaml
#
# After that's all sorted, we'll su over to Debian-debile-unpriv and import
# our OpenPGP keys

import os
import sys
import yaml
import tarfile
from contextlib import contextmanager
from argparse import ArgumentParser
from pwd import getpwnam

from debile.utils.commands import run_command


@contextmanager
def editconf(conf_dir):
    where = conf_dir + "slave.yaml"
    with open(where, 'r') as fd:
        info = yaml.load(fd)
        yield info
    # We've got control again. Let's save this.
    with open(where, 'w') as fd:
        yaml.dump(info, fd)


def cg(tf):
    def get(what):
        return tf.extractfile(what).read().strip()
    return get


def import_pgp(user, pgp_key, keyring):
    current_uid = os.geteuid()
    uid = getpwnam(user).pw_uid
    if current_uid != uid:
        if os.geteuid() != 0:
            print("Error: I'm neither {0} nor root.".format(user))
            print("Please re-run either as root or {0}".format(user))
            sys.exit(1)

        os.setuid(uid)

    out, err, code = run_command(['gpg', '--batch', '--import', '--status-fd', '1',
                                  '--no-default-keyring', '--keyring',
                                  keyring], input=pgp_key)
    if code != 0:
        print("Gpg import failed: {0}".format(code))
        sys.exit(1)


def import_conf(user, conf_dir, tarball, keyring, secret_keyring, auth_method):
    """
    Import the slave configuration from the tarball.
    :param str auth: authentication method (ssl or simple)
    :param str conf_dir: path to the debile configuration
    :param str auth_method: authentication backend (ssl or simple)

    """
    with tarfile.open(tarball, "r:gz") as tf:
        get = cg(tf)
        name = get("name")
        key = get("fingerprint")
        kname = "%" + (name)

        with editconf(conf_dir) as config:
            config['gpg'] = key
            r = config['xmlrpc']
            if auth == 'ssl':
                r['keyfile'] = conf_dir + name + ".key"
                r['certfile'] = conf_dir + name + ".crt"
                print("WARNING: I haven't copied the x.509 key and certificate"
                      "to {0} and {1}".format(r['keyfile'], r['certfile']))
                print("Please copy those files manually, "
                      "run `debile-slave-import-cred`, "
                      "or patch this script to handle those two files")
                print("That last solution is best. See "
                      "https://github.com/opencollab/debile/issues/4")

        import_pgp(user, get('key.pub'), keyring)
        import_pgp(user, get('key.priv'), secret_keyring)


if __name__ == "__main__":
    parser = ArgumentParser(description="Debile slave configuration importer")
    parser.add_argument("--user", action="store", dest="debile_user",
                        help="User to run gpg --import as")
    parser.add_argument("--conf-dir", action="store", dest="conf_dir", default="/etc/debile",
                        help="Debile configuration directory (default: /etc/debile)")

    parser.add_argument("--keyring", action="store", dest="keyring",
                        default="~/.gnupg/pubring.gpg",
                        help="GPG public keyring (default: ~/.gnupg/pubring.gpg)")
    parser.add_argument("--secret-keyring", action="store", dest="secret_keyring",
                        default="~/.gnupg/secring.gpg",
                        help="GPG secret keyring (default: ~/.gnupg/secring.gpg)")

    parser.add_argument("--auth", action="store", dest="auth_method", default='ssl',
                        help="Auth method: 'ssl' or 'simple' (ip-based)")

    parser.add_argument("tarball",
                        help="path to the tarball containing the PGP keys")

    args = parser.parse_args()

    import_conf(args.user, args.conf_dir, args.tarball, args.keyring,
                args.secret_keyring, args.auth_method)
