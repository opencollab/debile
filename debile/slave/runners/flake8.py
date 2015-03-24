from debile.slave.wrappers.flake8 import parse_flake8
from debile.slave.utils import cd
from debile.utils.commands import run_command


def flake8(dsc, analysis):
    run_command(["dpkg-source", "-x", dsc, "source-flake8"])
    with cd('source-flake8'):
        out, err, ret = run_command(['flake8', '.'])
        failed = ret != 0

        for issue in parse_flake8(out.splitlines()):
            analysis.results.append(issue)

        return (analysis, out, failed, None, None)


def version():
    out, err, ret = run_command([
        'flake8', '--version'
    ])
    if ret != 0:
        raise Exception("flake8 is not installed")
    return ('flake8', out.split(' ')[0])
