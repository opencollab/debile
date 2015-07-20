# Run with nosetests tests/test_pylint.py:test_pylint
from debile.slave.runners.pylint import pylint, version
from debile.slave.wrappers.pylint import parse_pylint
from firehose.model import (Analysis, Generator, Metadata)

import unittest
import mock


class PylintTestCase(unittest.TestCase):
    filepath = "tests/resources/python-firehose_0.3-1.dsc"
    firehose_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='pylint'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )


    @mock.patch('debile.slave.runners.pylint.run_command',
            return_value=(
                'pylint 1.4.3,\nastroid 1.3.6, common 0.62.0\nPython 2.7.10',
                '', 0))
    def test_pylint_version(self, mock):
        name, ver = version()

        self.assertEquals(name, 'pylint')
        self.assertEquals(ver, '1.4.3')


    @mock.patch('debile.slave.runners.pylint.run_command',
            return_value=('', '', 1))
    def test_pylint_version_with_error(self, mock):
        self.assertRaises(Exception, version)


    def test_pylint(self):
        pylint_analysis = pylint(self.filepath, self.firehose_results)
        content = pylint_analysis[1]
        self.assertTrue("Missing method docstring" in content)

        # It think it is safe to say that the string is not 4 chars long
        self.assertTrue(len(content) > 4)


    def test_pylint_wrappers(self):
        pylint_analysis = pylint(self.filepath, self.firehose_results)
        issues = parse_pylint(pylint_analysis[1].splitlines())
        i = 0
        for issue in issues:
            if issue.location.file.givenpath == \
                    "tests/parsers/test_clanganalyzer_parser.py" and \
            issue.location.point.line==22 and issue.location.point.column==0:
                found = issue
            i += 1
        print found
        self.assertEquals(found.testid, "W0611")
        self.assertEquals(found.location.file.givenpath,
                "tests/parsers/test_clanganalyzer_parser.py")
        self.assertEquals(found.location.point.line, 22)
        self.assertEquals(found.location.point.column, 0)
        self.assertEquals(found.severity, "warning")
        self.assertIsNone(found.notes)
        self.assertIsNone(found.customfields)
        self.assertTrue(
                "[unused-import]Unused Analysis imported from firehose.model"
                in found.message.text)
        self.assertTrue(i > 500)
