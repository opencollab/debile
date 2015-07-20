# Run with nosetests tests/test_pep8.py:test_pep8
from debile.slave.runners.pep8 import pep8, version
from debile.slave.wrappers.pep8 import parse_pep8
from firehose.model import (Analysis, Generator, Metadata)

import unittest
import mock


class Pep8TestCase(unittest.TestCase):
    filepath = "tests/resources/python-firehose_0.3-1.dsc"
    firehose_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='pep8'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )


    @mock.patch('debile.slave.runners.pep8.run_command',
            return_value=('1.5.7', '', 0))
    def test_pep8_version(self, mock):
        name, ver = version()

        self.assertEquals(name, 'pep8')
        self.assertEquals(ver, '1.5.7')


    @mock.patch('debile.slave.runners.pep8.run_command',
            return_value=('1.5.7', '', 1))
    def test_pep8_version(self, mock):
        self.assertRaises(Exception, version)


    def test_pep8(self):
        pep8_analysis = pep8(self.filepath, self.firehose_results)
        content = pep8_analysis[1]
        self.assertTrue("missing whitespace around operator" in content)

        # It think it is safe to say that the string is not 4 chars long
        self.assertTrue(len(content) > 4)


    def test_pep8_wrappers(self):
        pep8_analysis = pep8(self.filepath, self.firehose_results)
        issues = parse_pep8(pep8_analysis[1].splitlines())
        i = 0
        for issue in issues:
            if issue.location.file.givenpath == "./firehose/model.py" and \
            issue.location.point.line==96 and issue.location.point.column==1:
                found = issue
            i += 1
        print found
        self.assertEquals(found.testid, "E302")
        self.assertEquals(found.location.file.givenpath, "./firehose/model.py")
        self.assertEquals(found.location.point.line, 96)
        self.assertEquals(found.location.point.column, 1)
        self.assertEquals(found.severity, "error")
        self.assertIsNone(found.notes)
        self.assertIsNone(found.customfields)
        self.assertTrue("E302 expected 2 blank lines, found 1" in found.message.text)
        self.assertTrue(i > 100)
