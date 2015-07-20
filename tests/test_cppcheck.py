# Run with nosetests tests/test_cppcheck.py:test_cppcheck
from debile.slave.runners.cppcheck import cppcheck, version
from debile.slave.wrappers.cppcheck import parse_cppcheck
from firehose.model import (Analysis, Generator, Metadata)
import lxml.etree

import unittest
import mock


class CppcheckTestCase(unittest.TestCase):
    file_path="tests/resources/libjsoncpp_0.6.0~rc2-3.1.dsc"
    firehose_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='cppcheck'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )


    @mock.patch('debile.slave.runners.cppcheck.run_command',
            return_value=('Cppcheck 1.69', '', 0))
    def test_cppcheck_version(self, mock):
        name, ver = version()

        self.assertEquals(name, 'Cppcheck')
        self.assertEquals(ver, '1.69')


    @mock.patch('debile.slave.runners.cppcheck.run_command',
            return_value=('Cppcheck 1.69', '', 1))
    def test_cppcheck_version_with_error(self, mock):
        self.assertRaises(Exception, version)


    def test_cppcheck(self):
        cpp_analysis = cppcheck(self.file_path, self.firehose_results)
        xml_content = cpp_analysis[1]
        tree = lxml.etree.fromstring(xml_content.encode('utf-16'))
        i = 0
        paths = []
        lines = []
        severity = []
        messages = []
        testid = []
        for result in tree.xpath("//results/error"):
            paths.append(result.attrib['file'])
            lines.append(result.attrib['line'])
            severity.append(result.attrib['severity'])
            messages.append(result.attrib['msg'])
            testid.append(result.attrib['id'])
            i += 1
        # It think it is safe to say that this number won't be less than 4
        self.assertTrue(i > 4)
        # Check that some values exist (the order might change)
        self.assertTrue("src/lib_json/json_value.cpp" in paths)
        self.assertTrue("style" in severity)
        self.assertTrue("704" in lines)
        self.assertTrue("toomanyconfigs" in testid)


    @mock.patch('debile.slave.runners.cppcheck.run_command',
            return_value=('', '    ', 0))
    def test_cppcheck_with_withespace_in_stderr(self, mock):
        cpp_analysis = cppcheck(self.file_path, self.firehose_results)

        self.assertEquals(cpp_analysis[0], self.firehose_results)
        self.assertEquals(cpp_analysis[1], '    ')
        self.assertFalse(cpp_analysis[2])
        self.assertIsNone(cpp_analysis[3])
        self.assertIsNone(cpp_analysis[4])


    def test_cppcheck_wrappers(self):
        cpp_analysis = cppcheck(self.file_path, self.firehose_results)
        issues = parse_cppcheck(cpp_analysis[1])
        i = 0
        for issue in issues:
            if issue.testid == "toomanyconfigs":
                found = issue
            i += 1
        self.assertEquals(found.testid, "toomanyconfigs")
        self.assertEquals(found.location.file.givenpath,
                "src/lib_json/json_value.cpp")
        self.assertEquals(found.location.point.line, 0)
        self.assertEquals(found.location.point.column, 0)
        self.assertEquals(found.severity, "style")
        self.assertIsNone(found.notes)
        self.assertIsNone(found.customfields)
        self.assertTrue(i > 4)
