from debile.master.keyrings import import_pgp, import_ssl

import os
import mock
import unittest


class KeyringsTestCase(unittest.TestCase):
    @mock.patch('debile.master.keyrings.run_command', return_value=('', 0, 0))
    def test_import_pgp_raise_value_error(self, mock):
        self.assertRaises(ValueError, import_pgp, 'keyring', 'data')


    @mock.patch('debile.master.keyrings.run_command',
            return_value=('[GNUPG:] IMPORT_OK KEY 000XXX000', 0, 0))
    def test_import_pgp_successful(self, mock):
        fingerprint = import_pgp('keyring', 'data')

        self.assertEquals(fingerprint, '000XXX000')


    @mock.patch('debile.master.keyrings.run_command', return_value=('', 0, 0))
    def test_import_ssl_fingerprint_or_subject_is_none(self, mock):
        self.assertRaises(ValueError, import_ssl, 'keyring', 'certdata')


    @mock.patch('debile.master.keyrings.run_command',
            return_value=('subject=CN=cn2', 0, 0))
    def test_import_ssl_cn_not_in_subject(self, mock):
        self.assertRaises(ValueError, import_ssl, 'keyring', 'certdata', 'cn')


    @mock.patch('debile.master.keyrings.run_command',
            return_value=('subject=emailAddress=email2', 0, 0))
    def test_import_ssl_cn_not_in_subject(self, mock):
        self.assertRaises(ValueError, import_ssl, 'keyring', 'certdata', None,
                'email')


    @mock.patch('debile.master.keyrings.run_command',
            return_value=('subject=emailAddress=email2\nSHA1 Fingerprint=00XX00',
                0, 0))
    def test_import_ssl_successful(self, mock):
        fingerprint = import_ssl('tests/resources/keyring', 'certdata')
        os.remove('tests/resources/keyring')

        self.assertEquals(fingerprint, '00XX00')
