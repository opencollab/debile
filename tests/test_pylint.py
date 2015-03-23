# Run with nosetests tests/test_pylint.py:test_pylint
from debile.slave.runners.pylint import pylint, version
from debile.slave.wrappers.pylint import parse_pylint
from firehose.model import (Analysis, Generator, Metadata)


filepath = "tests/resources/python-firehose_0.3-1.dsc"


def test_pylint_version():
    version()


def test_pylint_common():
    firehorse_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='pylint'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )

    return pylint(filepath, firehorse_results)


def test_pylint():
    pylint_analysis = test_pylint_common()
    content = pylint_analysis[1]
    assert "Missing method docstring" in content

    # It think it is safe to say that the string is not 4 chars long
    assert len(content) > 4


def test_pylint_wrappers():
    pylint_analysis = test_pylint_common()
    issues = parse_pylint(pylint_analysis[1].splitlines())
    i = 0
    for issue in issues:
        if issue.location.file.givenpath == \
                "tests/parsers/test_clanganalyzer_parser.py" and \
           issue.location.point.line==22 and issue.location.point.column==0:
            found = issue
        i += 1
    print found
    assert found.testid == "W0611"
    assert found.location.file.givenpath == \
            "tests/parsers/test_clanganalyzer_parser.py"
    assert found.location.point.line == 22
    assert found.location.point.column == 0
    assert found.severity == "warning"
    assert found.notes is None
    assert found.customfields is None
    assert "[unused-import]Unused Analysis imported from firehose.model" \
            in found.message.text
    assert i > 500
