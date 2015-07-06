from debile.master.filerepo import FileRepo, FilesAlreadyRegistered
from debile.master.dud import Dud

import unittest
import mock


class FileRepoTestCase(unittest.TestCase):
    @mock.patch('debile.utils.deb822.Changes', return_value='Update package')
    def setUp(self, mock):
        self.filerepo = FileRepo()
        self.dud = Dud(string='Update package')


    @mock.patch('os.path.isdir', return_value=True)
    def test_add_dud_but_files_already_exist(self, mock):
        self.assertRaises(FilesAlreadyRegistered, self.filerepo.add_dud,
                '/tmp/', self.dud, 666)


    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('os.makedirs')
    @mock.patch('debile.master.dud.Dud.get_dud_file',
            return_value=['debile.dud'])
    @mock.patch('debile.master.dud.Dud.get_files', return_value=['debile'])
    @mock.patch('shutil.copy2')
    @mock.patch('os.chmod')
    @mock.patch('os.path.basename', return_value='debile')
    def test_add_dud(self, mock_basename, mock_chmod, mock_copy, mock_get_files,
            mock_dud, mock_makedirs, mock_path):
        self.filerepo.add_dud('/tmp', self.dud, 666)

        self.assertTrue(mock_makedirs.called)
        self.assertTrue(mock_copy.called)

        args,_ = mock_copy.call_args

        self.assertEquals(args, ('debile', '/tmp'))
        self.assertTrue(mock_chmod.called)

        args,kwargs = mock_chmod.call_args

        self.assertEquals(args, ('/tmp/debile', 666))

