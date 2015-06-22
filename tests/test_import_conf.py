import tools.debile_slave_import_conf as import_conf
from debile.utils.commands import run_command
from debile.utils.exceptions import GpgImportException

import unittest
import os
import pwd
import tarfile
import yaml


class SlaveImportConfTest(unittest.TestCase):
    key = 'D6B08791B954F001A7641F8E5564626D79CAB8E8'
    name = 'blade01'
    user = pwd.getpwuid(os.geteuid()).pw_name
    keyring = '/home/{0}/.gnupg/debile.gpg'.format(user)
    secret_keyring = '/home/{0}/.gnupg/debile_secret.gpg'.format(user)
    slave_config = '/tmp/slave.yaml'


    @classmethod
    def tearDown(self):
        if os.path.isfile(self.keyring):
            os.remove(self.keyring)

        if os.path.isfile(self.keyring + '~'):
            os.remove(self.keyring + '~')

        if os.path.isfile(self.secret_keyring):
            os.remove(self.secret_keyring)

        if os.path.isfile(self.secret_keyring + '~'):
            os.remove(self.secret_keyring + '~')

        if os.path.isfile(self.slave_config):
            os.remove(self.slave_config)


    def load_yaml(self):
        with open(self.slave_config, 'r') as f:
            out = yaml.load(f)
            return out


    def write_yaml(self, data):
        with open(self.slave_config, 'w') as f:
            f.write(yaml.dump(data))


    def test_parse_args_with_only_tarball(self):
        args = import_conf.parse_args(['tarball.tar.gz'])

        assert args.debile_user == None
        assert args.conf_dir == '/etc/debile'
        assert args.keyring == '~/.gnupg/pubring.gpg'
        assert args.secret_keyring == '~/.gnupg/secring.gpg'
        assert args.auth_method == 'ssl'
        assert args.tarball == 'tarball.tar.gz'


    def test_parse_args_with_all_args(self):
        args = import_conf.parse_args(['tarball.tar.gz', '--conf-dir',
            '~/debile', '--keyring', '~/keyring.gpg', '--secret-keyring',
            '~/secret.gpg', '--auth', 'simple', '--user', 'john'])

        assert args.debile_user == 'john'
        assert args.conf_dir == '~/debile'
        assert args.keyring == '~/keyring.gpg'
        assert args.secret_keyring == '~/secret.gpg'
        assert args.auth_method == 'simple'
        assert args.tarball == 'tarball.tar.gz'


    def test_get_attribute_from_tarfile(self):
        with tarfile.open('tests/resources/blade01.tar.gz', 'r:gz') as tf:
            fingerprint=import_conf.get_attribute_from_tarfile('fingerprint',tf)
            name_tar = import_conf.get_attribute_from_tarfile('name', tf)

        assert fingerprint == self.key
        assert name_tar == self.name


    def test_editconf(self):
        data = dict(A = 'a', B = 'b')
        self.write_yaml(data)

        with import_conf.editconf('/tmp/') as config:
            config['A'] = 'b'
            config['B'] = 'a'
            config['C'] = 'c'

        out = self.load_yaml()

        assert out['A'] == 'b'
        assert out['B'] == 'a'
        assert out['C'] == 'c'


    def test_write_conf_simple_auth(self):
        data = dict(xmlrpc = dict(host='localhost', port='22017'), gpg='00000')
        self.write_yaml(data)

        import_conf.write_conf('/tmp/', self.name, self.key, 'simple')

        out = self.load_yaml()

        assert out['gpg'] == self.key


    def test_write_conf_ssl_auth(self):
        data = dict(xmlrpc = dict(host='localhost', port='22017'), gpg='00000')
        self.write_yaml(data)

        import_conf.write_conf('/tmp/', self.name, self.key, 'ssl')

        out = self.load_yaml()

        assert out['gpg'] == self.key
        assert out['xmlrpc']['keyfile'] == '/tmp/blade01.key'
        assert out['xmlrpc']['certfile'] == '/tmp/blade01.crt'


    def test_import_pgp_public_key(self):
        with tarfile.open('tests/resources/blade01.tar.gz', 'r:gz') as tf:
            pub_key = import_conf.get_attribute_from_tarfile('key.pub', tf)

        import_conf.import_pgp(self.user, pub_key, 'public', self.keyring)

        out,_,_ = run_command(['gpg', '--list-keys', '--keyring', self.keyring])

        assert 'Debile Autobuilder (Debile Slave Key (blade01))' in out


    def test_import_pgp_secret_key(self):
        with tarfile.open('tests/resources/blade01.tar.gz', 'r:gz') as tf:
            priv_key = import_conf.get_attribute_from_tarfile('key.priv', tf)

        import_conf.import_pgp(self.user, priv_key, 'secret',
                self.secret_keyring)

        out,_,_ = run_command(['gpg', '--list-keys', '--keyring',
            self.secret_keyring])

        assert 'Debile Autobuilder (Debile Slave Key (blade01))' in out


    def test_import_pgp_with_wrong_key_file_format(self):
        keyring = 'debile.gpg'

        with tarfile.open('tests/resources/blade01.tar.gz', 'r:gz') as tf:
            # Take name instead of the public key
            pub_key = import_conf.get_attribute_from_tarfile('name', tf)

        self.assertRaises(GpgImportException, import_conf.import_pgp, self.user,
            pub_key, 'public', keyring)


    def test_import_conf_simple_auth(self):
        conf_dir = '/tmp/'
        tarball = 'tests/resources/blade01.tar.gz'
        auth_method = 'simple'

        data = dict(xmlrpc = dict(host='localhost', port='22017'), gpg='00000')
        self.write_yaml(data)

        import_conf.import_conf(self.user, conf_dir, tarball, self.keyring,
                self.secret_keyring, auth_method)

        out = self.load_yaml()

        assert out['gpg'] == self.key

        public_out,_,_ = run_command(['gpg', '--list-keys', '--keyring',
            self.keyring])
        secret_out,_,_ = run_command(['gpg', '--list-keys', '--keyring',
            self.secret_keyring])

        assert 'Debile Autobuilder (Debile Slave Key (blade01))' in public_out
        assert 'Debile Autobuilder (Debile Slave Key (blade01))' in secret_out


    def test_import_conf_ssl_auth(self):
        conf_dir = '/tmp/'
        tarball = 'tests/resources/blade01.tar.gz'
        auth_method = 'ssl'

        data = dict(xmlrpc = dict(host='localhost', port='22017'), gpg='00000')
        self.write_yaml(data)

        import_conf.import_conf(self.user, conf_dir, tarball, self.keyring,
                self.secret_keyring, auth_method)

        out = self.load_yaml()

        assert out['gpg'] == self.key
        assert out['xmlrpc']['keyfile'] == '/tmp/blade01.key'
        assert out['xmlrpc']['certfile'] == '/tmp/blade01.crt'

        public_out,_,_ = run_command(['gpg', '--list-keys', '--keyring',
            self.keyring])
        secret_out,_,_ = run_command(['gpg', '--list-keys', '--keyring',
            self.secret_keyring])

        assert 'Debile Autobuilder (Debile Slave Key (blade01))' in public_out
        assert 'Debile Autobuilder (Debile Slave Key (blade01))' in secret_out
