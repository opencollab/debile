import debile.master.changes as changes

import unittest
import mock


class ChangesTestCase(unittest.TestCase):
    @mock.patch('debile.utils.deb822.Changes', return_value='Update package')
    def setUp(self, mock):
        self.change = changes.Changes(string='Update package')


    def test_changes_constructor_type_error_exception(self):
        self.assertRaises(TypeError, changes.Changes,
                filename='/tmp/tmp.changes', string='Update package')
        
        self.assertRaises(TypeError, changes.Changes)


    @mock.patch('debile.utils.deb822.Changes', return_value='')
    def test_chages_constructor_changes_file_exception(self, mock):
        self.assertRaises(changes.ChangesFileException, changes.Changes,
                string='Update package')


    def test_changes_constructor(self):
        self.assertIsNone(self.change._absfile)
        self.assertIsNone(self.change._basename)
        self.assertEquals(self.change._directory, '')


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.udeb'])
    def test_is_source_only_upload_with_udeb_file(self, mock_get_files):
        self.assertFalse(self.change.is_source_only_upload())


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.deb'])
    def test_is_source_only_upload_with_deb_file(self, mock_get_files):
        self.assertFalse(self.change.is_source_only_upload())


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.changes'])
    def test_is_source_only_upload_with_changes_file(self, mock_get_files):
        self.assertTrue(self.change.is_source_only_upload())


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.udeb'])
    def test_is_binary_only_upload_with_udeb_file(self, mock_get_files):
        self.assertTrue(self.change.is_binary_only_upload())


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.deb'])
    def test_is_binary_only_upload_with_deb_file(self, mock_get_files):
        self.assertTrue(self.change.is_binary_only_upload())


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.changes'])
    def test_is_binary_only_upload_with_changes_file(self, mock_get_files):
        self.assertFalse(self.change.is_binary_only_upload())


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.changes'])
    def test_get_dsc_without_dsc_file(self, mock_get_files):
        self.assertIsNone(self.change.get_dsc())


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.dsc'])
    def test_get_dsc_with_dsc_file(self, mock_get_files):
        self.assertEquals(self.change.get_dsc(), 'debile.dsc')


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.changes'])
    def test_get_diff_without_diff_file(self, mock_get_files):
        self.assertIsNone(self.change.get_diff())


    @mock.patch('debile.master.changes.Changes.get_files', 
            return_value=['debile.debian.tar.gz'])
    def test_get_dsc_with_diff_file(self, mock_get_files):
        self.assertEquals(self.change.get_diff(), 'debile.debian.tar.gz')


    def test_parse_section_with_non_main_section(self):
        component, section = self.change._parse_section('non-free/python')

        self.assertEquals(component, 'non-free')
        self.assertEquals(section, 'python')


    def test_parse_section_with_main_section(self):
        component, section = self.change._parse_section('python')

        self.assertEquals(component, 'main')
        self.assertEquals(section, 'python')


    @mock.patch('debile.master.changes.run_command', return_value=(0,0,-1))
    @mock.patch('debile.master.changes.Changes.get_changes_file',
            return_value='debile.dsc')
    def test_validate_signature_with_run_command_error(self, mock, mock_changes):
        self.assertRaises(changes.ChangesFileException,
                self.change.validate_signature, 'tests/resources/keyring')


    @mock.patch('debile.master.changes.run_command',
            return_value=('[GNUPG:] BADSIG', 0, 0))
    @mock.patch('debile.master.changes.Changes.get_changes_file',
            return_value='debile.dsc')
    def test_validate_signature_with_badsign(self, mock, mock_changes):
        self.assertRaises(changes.ChangesFileException,
                self.change.validate_signature, 'tests/resources/keyring')


    @mock.patch('debile.master.changes.run_command',
            return_value=('[GNUPG:] ERRSIG', 0, 0))
    @mock.patch('debile.master.changes.Changes.get_changes_file',
            return_value='debile.dsc')
    def test_validate_signature_with_errorsign(self, mock, mock_changes):
        self.assertRaises(changes.ChangesFileException,
                self.change.validate_signature, 'tests/resources/keyring')


    @mock.patch('debile.master.changes.run_command',
            return_value=('[GNUPG:] NODATA', 0, 0))
    @mock.patch('debile.master.changes.Changes.get_changes_file',
            return_value='debile.dsc')
    def test_validate_signature_with_no_data(self, mock, mock_changes):
        self.assertRaises(changes.ChangesFileException,
                self.change.validate_signature, 'tests/resources/keyring')


    @mock.patch('debile.master.changes.run_command',
            return_value=('[GNUPG:] ERROR', 0, 0))
    @mock.patch('debile.master.changes.Changes.get_changes_file',
            return_value='debile.dsc')
    def test_validate_signature_with_unknown_problem(self, mock, mock_changes):
        self.assertRaises(changes.ChangesFileException,
                self.change.validate_signature, 'tests/resources/keyring')


    @mock.patch('debile.master.changes.run_command',
            return_value=('[GNUPG:] GOODSIG\n[GNUPG:] VALIDSIG 000ABC345', 0, 0))
    @mock.patch('debile.master.changes.Changes.get_changes_file',
            return_value='debile.dsc')
    def test_validate_signature_with_valid_sign(self, mock, mock_changes):
        key = self.change.validate_signature('tests/resources/keyring')

        self.assertTrue(mock.is_called)
        self.assertEquals(key, '000ABC345')


    @mock.patch('debile.utils.deb822.Changes',
            return_value={'distribution':'unstable'})
    def test_get_item(self, mock):
        new_change = changes.Changes(string='Update package')

        self.assertEquals(new_change.__getitem__('distribution'), 'unstable')


    @mock.patch('debile.utils.deb822.Changes', return_value={'key':'value'})
    def test_contains(self, mock):
        new_change = changes.Changes(string='Update package')

        self.assertTrue(new_change.__contains__('key'))


    @mock.patch('debile.utils.deb822.Changes', return_value={'key':'value'})
    def test_get_with_defined_key(self, mock):
        new_change = changes.Changes(string='Update package')

        self.assertEquals(new_change.get('key'), 'value')


    @mock.patch('debile.utils.deb822.Changes', return_value={'key':'value'})
    def test_get_without_defined_key(self, mock):
        new_change = changes.Changes(string='Update package')

        self.assertEquals(new_change.get('key2', default='value2'), 'value2')
