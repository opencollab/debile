# Run with nosetests tests/test_jshint.py:test_jshint
from debile.slave.runners.jshint import jshint, version
from debile.slave.wrappers.jshint import parse_jshint
from firehose.model import (Analysis, Generator, Metadata)


filepath = "tests/resources/libjs-term.js_0.0.4-1.dsc"


def test_jshint_version():
    version()


def test_jshint_common():
    firehorse_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='jshint'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )

    return jshint(filepath, firehorse_results)


def test_jshint():
    jshint_analysis = test_jshint_common()
    content = jshint_analysis[1]
    print content
    assert "Bad line breaking" in content

    # It think it is safe to say that the string is not 4 chars long
    assert len(content) > 4


def test_jshint_wrappers():
    jshint_analysis = test_jshint_common()
    issues = parse_jshint(jshint_analysis[1].splitlines())
    i = 0
    found = None
    for issue in issues:
        if issue.location.file.givenpath == "test/index.js" and \
           issue.location.point.line==13 and issue.location.point.column==19:
            found = issue
        i += 1
    print found
    assert found.testid == "W014"
    assert found.location.file.givenpath == "test/index.js"
    assert found.location.point.line == 13
    assert found.location.point.column == 19
    assert found.severity == "warning"
    assert found.notes is None
    assert found.customfields is None
    assert "Bad line breaking" in found.message.text
    assert i > 75
