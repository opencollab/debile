# Run with nosetests tests/test_slave_cli.py
import debile.slave.cli as slave


def test_parse_args():
    args = slave.parse_args(['--auth', 'simple', '--config', \
            '/etc/debile/slave.yaml', '-s', '-d'])

    assert args.auth_method == 'simple'
    assert args.config == '/etc/debile/slave.yaml'
    assert args.syslog == True
    assert args.debug == True
