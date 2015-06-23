from debile.utils.xmlrpc import get_auth_method
from debile.slave.cli import parse_args

import unittest


class CliTestCase(unittest.TestCase):
    def test_get_auth_method_without_cli_option_and_without_yaml_config(self):
        # Default value in args is 'ssl'
        args = parse_args(['--auth', 'ssl'])
        config = {}

        auth_method = get_auth_method(args, config)

        assert auth_method == 'ssl'


    def test_get_auth_method_without_cli_option_but_with_yaml_config(self):
        # Default value in args is 'ssl'
        args = parse_args(['--auth', 'ssl'])
        config = {'xmlrpc': {'auth_method': 'simple'}}

        auth_method = get_auth_method(args, config)

        assert auth_method == 'simple'


    def test_get_auth_method_with_cli_option_and_without_yaml_config(self):
        args = parse_args(['--auth', 'simple'])
        config = {}

        auth_method = get_auth_method(args, config)

        assert auth_method == 'simple'
