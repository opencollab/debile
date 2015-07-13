from debile.master.reprepro import Repo, RepoException, RepoPackageNotFound
from debile.master.changes import Changes
from debile.master.orm import Source, Suite, Component

import unittest
import mock


class ReprepoTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Repo('/root')


    def test_repo_constructor(self):
        self.assertEquals(self.repo.root, '/root')


    @mock.patch('debile.utils.deb822.Changes',
            return_value={'distribution':'unstable'})
    @mock.patch('debile.master.reprepro.Repo.include')
    @mock.patch('debile.master.changes.Changes.get_changes_file',
            return_value='mock.dsc')
    def test_add_changes(self, mock_changes, mock_reprepro, mock):
        changes = Changes(string='Some change')
        self.repo.add_changes(changes)

        args,_ = mock_reprepro.call_args
        
        self.assertEquals(args, ('unstable', 'mock.dsc'))


    @mock.patch('debile.master.reprepro.run_command', return_value=(0,0,0))
    def test_exec_with_successful_command(self, mock):
        self.repo._exec('include', 'unstable', 'test.changes')
        self.assertTrue(mock.called)

        args,_ = mock.call_args

        self.assertEquals(args, (['reprepro', '-Vb', '/root', 'include',
            'unstable', 'test.changes'],))


    @mock.patch('debile.master.reprepro.run_command', return_value=(0,0,-1))
    def test_exec_with_failure_command(self, mock):
        self.assertRaises(RepoException, self.repo._exec)


    @mock.patch('debile.master.reprepro.run_command', return_value=(0,0,0))
    def test_include(self, mock):
        (out, stderr, ret) = self.repo.include('unstable', 'test.changes')

        self.assertTrue(mock.called)
        self.assertEquals((out, stderr, ret), (0,0,0))


    @mock.patch('debile.master.reprepro.RepoException.message', return_value=1)
    @mock.patch('debile.master.reprepro.run_command', return_value=(0,0,-1))
    def test_include_raise_repoexception(self, mock, mock_exception):
        self.assertRaises(RepoException, self.repo.include, 'unstable',
                'test.changes')


    @mock.patch('debile.master.reprepro.RepoException.message', return_value=254)
    @mock.patch('debile.master.reprepro.run_command', return_value=(0,0,-1))
    def test_include_raise_repo_source_already_registered(self, mock,
            mock_exception):
        self.assertRaises(RepoException, self.repo.include, 'unstable',
                'test.changes')


    def test_includedeb_not_implemented(self):
        self.assertRaises(NotImplementedError, self.repo.includedeb, 'unstable',
                'test.deb')


    def test_includeudeb_not_implemented(self):
        self.assertRaises(NotImplementedError, self.repo.includeudeb, 'unstable',
                'test.udeb')


    def test_includedsc_not_implemented(self):
        self.assertRaises(NotImplementedError, self.repo.includedsc, 'unstable',
                'test.dsc')


    def test_list_not_implemented(self):
        self.assertRaises(NotImplementedError, self.repo.list, 'unstable', 
                'test')


    def test_clearvanished_not_implemented(self):
        self.assertRaises(NotImplementedError, self.repo.clearvanished)
