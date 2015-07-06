from debile.master.dud import Dud, DudFileException

import unittest
import mock


class DudTestCase(unittest.TestCase):
    @mock.patch('debile.utils.deb822.Changes', return_value='Update package')
    def setUp(self, mock):
        self.dud = Dud(string='Update package')


    def test_dud_constructor_type_error_exception(self):
        self.assertRaises(TypeError, Dud, filename='/tmp/tmp.dud', 
                string='Update package')
        
        self.assertRaises(TypeError, Dud)


    @mock.patch('debile.utils.deb822.Changes', return_value='')
    def test_dud_constructor_dud_file_exception(self, mock):
        self.assertRaises(DudFileException, Dud, string='Update package')


    def test_dud_constructor_with_string(self):
        self.assertIsNone(self.dud._absfile)
        self.assertIsNone(self.dud._basename)
        self.assertEquals(self.dud._directory, '')


    @mock.patch('debile.master.dud.Dud.get_files', 
            return_value=['debile.firehose.xml'])
    def test_get_firehose_file(self, mock_get_files):
        self.assertEquals(self.dud.get_firehose_file(), 'debile.firehose.xml')


    @mock.patch('debile.master.dud.Dud.get_files', 
            return_value=['debile.log'])
    def test_get_log_file(self, mock_get_files):
        self.assertEquals(self.dud.get_log_file(), 'debile.log')


    @mock.patch('debile.master.dud.run_command', return_value=(0,0,-1))
    @mock.patch('debile.master.dud.Dud.get_dud_file', return_value='debile.dud')
    def test_validate_signature_with_run_command_error(self, mock_dud, mock):
        self.assertRaises(DudFileException, self.dud.validate_signature,
                'tests/resources/keyring')


    @mock.patch('debile.master.dud.run_command',
            return_value=('[GNUPG:] BADSIG', 0, 0))
    @mock.patch('debile.master.dud.Dud.get_dud_file', return_value='debile.dud')
    def test_validate_signature_with_badsign(self, mock_dud, mock):
        self.assertRaises(DudFileException, self.dud.validate_signature,
                'tests/resources/keyring')


    @mock.patch('debile.master.dud.run_command',
            return_value=('[GNUPG:] ERRSIG', 0, 0))
    @mock.patch('debile.master.dud.Dud.get_dud_file', return_value='debile.dud')
    def test_validate_signature_with_errorsign(self, mock_dud, mock):
        self.assertRaises(DudFileException, self.dud.validate_signature,
                'tests/resources/keyring')


    @mock.patch('debile.master.dud.run_command',
            return_value=('[GNUPG:] NODATA', 0, 0))
    @mock.patch('debile.master.dud.Dud.get_dud_file', return_value='debile.dud')
    def test_validate_signature_with_no_data(self, mock_dud, mock):
        self.assertRaises(DudFileException, self.dud.validate_signature,
                'tests/resources/keyring')


    @mock.patch('debile.master.dud.run_command',
            return_value=('[GNUPG:] ERROR', 0, 0))
    @mock.patch('debile.master.dud.Dud.get_dud_file', return_value='debile.dud')
    def test_validate_signature_with_unknown_problem(self, mock_dud, mock):
        self.assertRaises(DudFileException, self.dud.validate_signature,
                'tests/resources/keyring')


    @mock.patch('debile.master.dud.run_command',
            return_value=('[GNUPG:] GOODSIG\n[GNUPG:] VALIDSIG 000ABC345', 0, 0))
    @mock.patch('debile.master.dud.Dud.get_dud_file', return_value='debile.dud')
    def test_validate_signature_with_valid_sign(self, mock_dud, mock):
        key = self.dud.validate_signature('tests/resources/keyring')

        self.assertTrue(mock.is_called)
        self.assertEquals(key, '000ABC345')
