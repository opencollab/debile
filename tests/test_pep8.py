# Run with nosetests tests/test_pep8.py:test_pep8
from debile.slave.runners.pep8 import pep8, version
from debile.slave.wrappers.pep8 import parse_pep8
from firehose.model import (Analysis, Generator, Metadata)


filepath = "tests/resources/python-firehose_0.3-1.dsc"


def test_pep8_version():
    version()


def test_pep8_common():
    firehorse_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='pep8'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )

    return pep8(filepath, firehorse_results)


def test_pep8():
    pep8_analysis = test_pep8_common()
    content = pep8_analysis[1]
    assert "missing whitespace around operator" in content

    # It think it is safe to say that the string is not 4 chars long
    assert len(content) > 4


def test_pep8_wrappers():
    pep8_analysis = test_pep8_common()
    issues = parse_pep8(pep8_analysis[1].splitlines())
    i = 0
    for issue in issues:
        if issue.location.file.givenpath == "./firehose/model.py" and \
           issue.location.point.line==96 and issue.location.point.column==1:
            found = issue
        i += 1
    print found
    assert found.testid == "E302"
    assert found.location.file.givenpath == "./firehose/model.py"
    assert found.location.point.line == 96
    assert found.location.point.column == 1
    assert found.severity == "error"
    assert found.notes is None
    assert found.customfields is None
    assert "E302 expected 2 blank lines, found 1" in found.message.text
    assert i > 100
