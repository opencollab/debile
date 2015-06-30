#!/usr/bin/env python
#
# Copyright (c) Paul R. Tagliamonte <paultag@debian.org>, 2014
# Copyright (c) Clement Schreiner   <clement@mux.me>, 2015
# Copyright (c) Lucas Kanashiro   <kanashiro.duarte@gmail.com>, 2015
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
from debile.utils.exceptions import WrongUserException, GpgImportException


@contextmanager
def editconf(conf_dir):
    where = conf_dir + "slave.yaml"
    with open(where, 'r') as fd:
        info = yaml.load(fd)
        yield info
    # We've got control again. Let's save this.
    with open(where, 'w') as fd:
        yaml.dump(info, fd)


def get_attribute_from_tarfile(attribute, tarfile):
    return tarfile.extractfile(attribute).read().strip()


def ensure_uid(user):
    current_uid = os.geteuid()
    uid = getpwnam(user).pw_uid
    if current_uid != uid:
        if os.geteuid() != 0:
            print("Error: I'm neither {0} nor root.".format(user))
            print("Please re-run either as root or {0}".format(user))
            raise WrongUserException

        os.setuid(uid)


def import_pgp(user, pgp_key, key_type, keyring, gpg_home_dir):
    ensure_uid(user)

    if key_type == 'public':
        keyring_type = '--keyring'
    elif key_type == 'secret':
        keyring_type = '--secret-keyring'
    else:
        print("You must specify the type of imported key.")
        raise GpgImportException

    out, err, code = run_command(['gpg', '--batch', '--import', '--status-fd',
                                  '1', '--no-default-keyring', '--homedir',
                                  gpg_home_dir, keyring_type, keyring],
                                  input=pgp_key)

    if code != 0:
        print("STDERR: {0}".format(err))
        print("GPG import failed: {0}".format(code))
        raise GpgImportException


def write_conf(conf_dir, name, key, auth_method):
    with editconf(conf_dir) as config:
        config['gpg'] = key

        if 'xmlrpc' in config:
            xmlrpc = config['xmlrpc']
            if auth_method == 'ssl':
                xmlrpc['keyfile'] = conf_dir + name + '.key'
                xmlrpc['certfile'] = conf_dir + name + '.crt'
                xmlrpc['auth_method'] = 'ssl'
                print("WARNING: I haven't copied the x.509 key and certificate"
                      "to {0} and {1}".format(xmlrpc['keyfile'],
                                              xmlrpc['certfile']))
                print("Please copy those files manually, "
                      "run `debile-slave-import-cred`, "
                      "or patch this script to handle those two files")
                print("That last solution is best. See "
                      "https://github.com/opencollab/debile/issues/4")
            elif auth_method == 'simple':
                xmlrpc['auth_method'] = 'simple'


def import_conf(user, conf_dir, tarball, keyring, secret_keyring, auth_method,
        gpg_home_dir):
    """
    Import the slave configuration from the tarball.
    :param str auth: authentication method (ssl or simple)
    :param str conf_dir: path to the debile configuration
    :param str auth_method: authentication backend (ssl or simple)

    """
    with tarfile.open(tarball, "r:gz") as tf:
        name = get_attribute_from_tarfile("name", tf)
        key = get_attribute_from_tarfile("fingerprint", tf)

        write_conf(conf_dir, name, key, auth_method)

        import_pgp(user, get_attribute_from_tarfile('key.pub', tf),
                   'public', keyring, gpg_home_dir)
        import_pgp(user, get_attribute_from_tarfile('key.priv', tf),
                   'secret', secret_keyring, gpg_home_dir)


def parse_args(args):
    parser = ArgumentParser(description="Debile slave configuration importer")
    parser.add_argument("--user", action="store", dest="debile_user",
                        help="User to run gpg --import as")
    parser.add_argument("--conf-dir", action="store", dest="conf_dir",
                        default="/etc/debile/",
                        help="Debile configuration directory (default: /etc/debile/)")

    parser.add_argument("--keyring", action="store", dest="keyring",
                        default="~/.gnupg/pubring.gpg",
                        help="GPG public keyring (default: ~/.gnupg/pubring.gpg)")
    parser.add_argument("--secret-keyring", action="store",
                        dest="secret_keyring",
                        default="~/.gnupg/secring.gpg",
                        help="GPG secret keyring (default: ~/.gnupg/secring.gpg)")
    parser.add_argument("--gpg-home", action="store", dest="gpg_home_dir",
                        default="~/.gnupg/",
                        help="GPG public keyring (default: ~/.gnupg/pubring.gpg)")

    parser.add_argument("--auth", action="store", dest="auth_method",
                        default='ssl',
                        help="Auth method: 'ssl' or 'simple' (ip-based)")

    parser.add_argument("tarball",
                        help="path to the tarball containing the PGP keys")

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    try:
        import_conf(args.debile_user, args.conf_dir, args.tarball,
                    args.keyring, args.secret_keyring, args.auth_method,
                    args.gpg_home_dir)
    except WrongUserException:
        print("Cannot set correct uid in the system.")
    except GpgImportException:
        print("Cannot import GPG key. Verify if exists GPG binary "
              "in your system or any trouble with your key")
