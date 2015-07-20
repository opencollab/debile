# Run with nosetests tests/test_roodi.py:test_roodi
from debile.slave.runners.roodi import roodi, version
from debile.slave.wrappers.roodi import parse_roodi
from firehose.model import (Analysis, Generator, Metadata)

import unittest
import mock


class RoodiTestCase(unittest.TestCase):
    file_path="tests/resources/bundler_1.7.4-1.dsc"
    firehose_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='roodi'
            ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
    )


    @mock.patch('debile.slave.runners.roodi.run_command',
            return_value=('5.0.0', '', 0))
    def test_roodi_version(self, mock):
        name, ver = version()

        self.assertEquals(name, 'roodi')
        self.assertEquals(ver, '5.0.0')


    @mock.patch('debile.slave.runners.roodi.run_command',
            return_value=('', '', 1))
    def test_roodi_version_with_error(self, mock):
        self.assertRaises(Exception, version)


    def test_roodi(self):
        ruby_analysis = roodi(self.file_path, self.firehose_results)
        content = ruby_analysis[1]

        # this should be the most common error
        self.assertTrue("Found = in conditional.  It should probably be an =="
                in content)

        # just a check to see if there actually are some errors
        self.assertTrue(len(content) > 4)


    def test_roodi_wrappers(self):
        ruby_analysis = roodi(self.file_path, self.firehose_results)
        issues = parse_roodi(ruby_analysis[1].splitlines())
        i = 0
        for issue in issues:
            if issue.location.file.givenpath == "./spec/support/builders.rb":
                found = issue
            i += 1
        self.assertEquals(found.location.file.givenpath,
                "./spec/support/builders.rb")
        self.assertEquals(found.location.point.line, 4)
        self.assertEquals(found.location.point.column, 1)
        self.assertEquals(found.severity, "warning")
        self.assertTrue("Module \"Builders\" has 648 lines.  It should have 300 or less"
                in found.message.text)
        self.assertIsNone(found.notes)
        self.assertIsNone(found.trace)
        self.assertIsNone(found.customfields)
        self.assertTrue(i > 100)
