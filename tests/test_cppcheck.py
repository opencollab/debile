# Run with nosetests tests/test_cppcheck.py:test_cppcheck
from debile.slave.runners.cppcheck import cppcheck, version
from debile.slave.wrappers.cppcheck import parse_cppcheck
from firehose.model import (Analysis, Generator, Metadata)
import lxml.etree


def test_cppcheck_version():
    version()

def test_cppcheck_common():
    firehorse_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='cppcheck'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )

    return cppcheck("tests/resources/libjsoncpp_0.6.0~rc2-3.1.dsc", firehorse_results)


def test_cppcheck():
    cpp_analysis = test_cppcheck_common()
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
    assert i > 4
    # Check that some values exist (the order might change)
    assert "src/lib_json/json_value.cpp" in paths
    assert "style" in severity
    assert "704" in lines
    assert "toomanyconfigs" in testid

def test_cppcheck_wrappers():
    cpp_analysis = test_cppcheck_common()
    issues = parse_cppcheck(cpp_analysis[1])
    i = 0
    for issue in issues:
        if issue.testid == "toomanyconfigs":
            found = issue
        i += 1
    assert found.testid == "toomanyconfigs"
    assert found.location.file.givenpath == "src/lib_json/json_value.cpp"
    assert found.location.point.line == 0
    assert found.location.point.column == 0
    assert found.severity == "style"
    assert found.notes is None
    assert found.customfields is None
    assert i > 4
