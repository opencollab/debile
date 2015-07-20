# Run with nosetests tests/test_lintian.py:test_lintian
from debile.slave.runners.lintian import lintian, version
from debile.slave.wrappers.lintian import parse_lintian
from firehose.model import (Analysis, Generator, Metadata)

import unittest
import mock


class LintianTestCase(unittest.TestCase):
    filepath = "tests/resources/libjsoncpp0_0.6.0~rc2-3.1_amd64.deb"
    firehose_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='lintian'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )


    @mock.patch('debile.slave.runners.lintian.run_command',
            return_value=('Lintian v2.5.31', '', 0))
    def test_version(self, mock):
        name, ver = version()

        self.assertEquals(name, 'Lintian')
        self.assertEquals(ver, 'v2.5.31')


    @mock.patch('debile.slave.runners.lintian.run_command',
            return_value=('Lintian v2.5.31', '', 1))
    def test_version_without_lintian(self, mock):
        self.assertRaises(Exception, version)


    def test_lintian(self):
        lintian_analysis = lintian(self.filepath, self.firehose_results)
        content = lintian_analysis[1]
        self.assertTrue("no-symbols-control-file" in content)

        # It think it is safe to say that the string is not 4 chars long
        self.assertTrue(len(content) > 4)


    def test_lintian_wrappers(self):
        lintian_analysis = lintian(self.filepath, self.firehose_results)
        issues = parse_lintian(lintian_analysis[1].splitlines(), self.filepath)
        i = 0
        for issue in issues:
            if issue.testid == "no-symbols-control-file":
                found = issue
            i += 1
        self.assertEquals(found.testid, "no-symbols-control-file")
        self.assertEquals(found.location.file.givenpath,
                "tests/resources/libjsoncpp0_0.6.0~rc2-3.1_amd64.deb")
        self.assertIsNone(found.location.point)
        self.assertEquals(found.severity, "info")
        self.assertIsNone(found.notes)
        self.assertIsNone(found.customfields)
        self.assertTrue("libjsoncpp0: no-symbols-control-file usr/lib/libjsoncpp.so.0.6.0"
                in found.message.text)
        self.assertTrue(i > 1)
