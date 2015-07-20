# Run with nosetests tests/test_jshint.py:test_jshint
from debile.slave.runners.jshint import jshint, version
from debile.slave.wrappers.jshint import parse_jshint
from firehose.model import (Analysis, Generator, Metadata)

import unittest
import mock


class JSHintTestCase(unittest.TestCase):
    filepath = "tests/resources/libjs-term.js_0.0.4-1.dsc"
    firehose_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='jshint'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )


    @mock.patch('debile.slave.runners.jshint.run_command',
            return_value=('output', 'jshint v2.8.0', 0))
    def test_jshint_version(self, mock):
        name, ver = version()

        self.assertEquals(name, 'jshint')
        self.assertEquals(ver, 'v2.8.0')


    @mock.patch('debile.slave.runners.jshint.run_command',
            return_value=('output', 'jshint v2.8.0', 1))
    def test_version_raise_exception(self, mock):
        self.assertRaises(Exception, version)


    def test_jshint(self):
        jshint_analysis = jshint(self.filepath, self.firehose_results)
        content = jshint_analysis[1]

        self.assertTrue("Bad line breaking" in content)

        # It think it is safe to say that the string is not 4 chars long
        self.assertTrue(len(content) > 4)


    @mock.patch('debile.slave.runners.jshint.run_command',
            return_value=(None, 'jshint v2.8.0', 1))
    def test_jshint_with_none_output(self, mock):
        jshint_analysis = jshint(self.filepath, self.firehose_results)

        self.assertEquals(jshint_analysis[0], self.firehose_results)
        self.assertIsNone(jshint_analysis[1])
        self.assertTrue(jshint_analysis[2])
        self.assertIsNone(jshint_analysis[3])
        self.assertIsNone(jshint_analysis[4])


    def test_jshint_wrappers(self):
        jshint_analysis = jshint(self.filepath, self.firehose_results)
        issues = parse_jshint(jshint_analysis[1].splitlines())
        i = 0
        found = None
        for issue in issues:
            if issue.location.file.givenpath == "test/index.js" and \
            issue.location.point.line==13 and issue.location.point.column==19:
                found = issue
            i += 1
        print found
        self.assertEquals(found.testid, "W014")
        self.assertEquals(found.location.file.givenpath, "test/index.js")
        self.assertEquals(found.location.point.line, 13)
        self.assertEquals(found.location.point.column, 19)
        self.assertEquals(found.severity, "warning")
        self.assertIsNone(found.notes)
        self.assertIsNone(found.customfields)
        self.assertTrue("Bad line breaking" in found.message.text)
        self.assertTrue(i > 75)
