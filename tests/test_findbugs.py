from debile.slave.runners.findbugs import findbugs, version
from debile.slave.wrappers.findbugs import parse_findbugs
from firehose.model import (Analysis, Generator, Metadata)

import unittest
import mock


class FindbugsTestCase(unittest.TestCase):
    filepath = 'tests/resources/libjdom1-java_1.1.3-1_all.deb'
    firehose_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='findbugs'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )


    @mock.patch('debile.slave.runners.findbugs.run_command',
            return_value=('2.0.3', '', 0))
    def test_version(self, mock):
        name, ver = version()

        self.assertEquals(name, 'findbugs')
        self.assertEquals(ver, '2.0.3')


    @mock.patch('debile.slave.runners.findbugs.run_command',
            return_value=('2.0.3', '', 1))
    def test_version_without_findbugs(self, mock):
        self.assertRaises(Exception, version)


    def test_findbugs(self):
        findbugs_analysis = findbugs(self.filepath, self.firehose_results)
        content = findbugs_analysis[1]
        self.assertTrue("The following classes needed for analysis" in content)

        # It think it is safe to say that the string is not 4 chars long
        self.assertTrue(len(content) > 4)


    @mock.patch('debile.slave.runners.findbugs.run_command',
            return_value=(0, 'error', -1))
    def test_findbugs_with_exception(self, mock):
        self.assertRaises(Exception, findbugs, self.filepath,
            self.firehose_results)
