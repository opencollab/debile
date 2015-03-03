# Run with nosetests tests/test_lintian.py:test_lintian
from debile.slave.runners.lintian import lintian, version
from debile.slave.wrappers.lintian import parse_lintian
from firehose.model import (Analysis, Generator, Metadata)


filepath = "tests/resources/libjsoncpp0_0.6.0~rc2-3.1_amd64.deb"


def test_lintian_version():
    version()


def test_lintian_common():
    firehorse_results = Analysis(
        metadata=Metadata(
            generator=Generator(
                name='lintian'
                ),
            sut=None,
            file_=None,
            stats=None),
        results=[]
        )

    return lintian(filepath, firehorse_results)


def test_lintian():
    lintian_analysis = test_lintian_common()
    content = lintian_analysis[1]
    assert "no-symbols-control-file" in content

    # It think it is safe to say that the string is not 4 chars long
    assert len(content) > 4


def test_lintian_wrappers():
    lintian_analysis = test_lintian_common()
    issues = parse_lintian(lintian_analysis[1].splitlines(), filepath)
    i = 0
    for issue in issues:
        if issue.testid == "no-symbols-control-file":
            found = issue
        i += 1
    assert found.testid == "no-symbols-control-file"
    assert found.location.file.givenpath == "tests/resources/libjsoncpp0_0.6.0~rc2-3.1_amd64.deb"
    assert found.location.point is None
    assert found.severity == "info"
    assert found.notes is None
    assert found.customfields is None
    assert "libjsoncpp0: no-symbols-control-file usr/lib/libjsoncpp.so.0.6.0" in found.message.text
    assert i > 1
