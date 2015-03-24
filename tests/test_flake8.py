# Run with nosetests tests/test_flake8.py:test_flake8
from debile.slave.runners.flake8 import flake8, version
from debile.slave.wrappers.flake8 import parse_flake8
from firehose.model import (Analysis, Generator, Metadata)


filepath = "tests/resources/python-firehose_0.3-1.dsc"


def test_flake8_version():
    version()


def test_flake8_common():
    firehorse_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='flake8'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )

    return flake8(filepath, firehorse_results)


def test_flake8():
    flake8_analysis = test_flake8_common()
    content = flake8_analysis[1]
    assert "missing whitespace around operator" in content

    # It think it is safe to say that the string is not 4 chars long
    assert len(content) > 4


def test_flake8_wrappers():
    flake8_analysis = test_flake8_common()
    issues = parse_flake8(flake8_analysis[1].splitlines())
    i = 0
    for issue in issues:
        if issue.location.file.givenpath == "./firehose/parsers/cppcheck.py" and \
           issue.location.point.line==37 and issue.location.point.column==5:
            found = issue
        i += 1
    print found
    assert found.testid == "F841"
    assert found.location.file.givenpath == "./firehose/parsers/cppcheck.py"
    assert found.location.point.line == 37
    assert found.location.point.column == 5
    assert found.severity == "error"
    assert found.notes is None
    assert found.customfields is None
    assert "F841 local variable 'version' is assigned to but never used" in found.message.text
    assert i > 100
