from debile.slave.runners.flake8 import flake8, version


def run(dsc, package, job, firehose):
    return flake8(dsc, firehose)


def get_version():
    return version()
