# Run with nosetests tests/test_roodi.py:test_roodi
from debile.slave.runners.roodi import roodi, version
from debile.slave.wrappers.roodi import parse_roodi
from firehose.model import (Analysis, Generator, Metadata)


def test_roodi_version():
    version()


def test_roodi_common():
    firehorse_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='roodi'
            ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
    )

    return roodi("tests/resources/bundler_1.7.4-1.dsc", firehorse_results)


def test_roodi():
    ruby_analysis = test_roodi_common()
    content = ruby_analysis[1]

    # this should be the most common error
    assert "Found = in conditional.  It should probably be an ==" in content

    # just a check to see if there actually are some errors
    assert len(content) > 4


def test_roodi_wrappers():
    ruby_analysis = test_roodi_common()
    issues = parse_roodi(ruby_analysis[1].splitlines())
    i = 0
    for issue in issues:
        if issue.location.file.givenpath == "./spec/support/builders.rb":
            found = issue
        i += 1
    assert found.location.file.givenpath == "./spec/support/builders.rb"
    assert found.location.point.line == 4
    assert found.location.point.column == 1
    assert found.severity == "warning"
    assert "Module \"Builders\" has 648 lines.  It should have 300 or less" in found.message.text
    assert found.notes is None
    assert found.trace is None
    assert found.customfields is None
    assert i > 100
