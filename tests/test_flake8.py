# Run with nosetests tests/test_flake8.py:test_flake8
from debile.slave.runners.flake8 import flake8, version
from debile.slave.wrappers.flake8 import parse_flake8
from firehose.model import (Analysis, Generator, Metadata)

import unittest
import mock


class Flake8TestCase(unittest.TestCase):
    filepath = "tests/resources/python-firehose_0.3-1.dsc"
    firehose_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='flake8'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )


    @mock.patch('debile.slave.runners.flake8.run_command',
            return_value=('2.2.2 (pep8: 1.5.7, mccabe: 0.2.1, pyflakes: 0.8.1) CPython 2.7.10 on Linux',
                '', 0))
    def test_flake8_version(self, mock):
        name, ver = version()

        self.assertEquals(name, 'flake8')
        self.assertEquals(ver, '2.2.2')


    @mock.patch('debile.slave.runners.flake8.run_command',
            return_value=('', '', 1))
    def test_flake8_version_with_error(self, mock):
        self.assertRaises(Exception, version)


    def test_flake8(self):
        flake8_analysis = flake8(self.filepath, self.firehose_results)
        content = flake8_analysis[1]
        self.assertTrue("missing whitespace around operator" in content)

        # It think it is safe to say that the string is not 4 chars long
        self.assertTrue(len(content) > 4)


    def test_flake8_wrappers(self):
        flake8_analysis = flake8(self.filepath, self.firehose_results)
        issues = parse_flake8(flake8_analysis[1].splitlines())
        i = 0
        for issue in issues:
            if issue.location.file.givenpath == "./firehose/parsers/cppcheck.py" and \
            issue.location.point.line==37 and issue.location.point.column==5:
                found = issue
            i += 1
        print found
        self.assertEquals(found.testid, "F841")
        self.assertEquals(found.location.file.givenpath,
                "./firehose/parsers/cppcheck.py")
        self.assertEquals(found.location.point.line, 37)
        self.assertEquals(found.location.point.column, 5)
        self.assertEquals(found.severity, "error")
        self.assertIsNone(found.notes)
        self.assertIsNone(found.customfields)
        self.assertTrue("F841 local variable 'version' is assigned to but never used"
                in found.message.text)
        self.assertTrue(i > 100)
