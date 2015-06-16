from debile.utils.commands import run_command
from debile.utils.commands import safe_run
from debile.utils.deb822 import Changes
from debile.utils.xmlrpc import get_auth_method
from debile.slave.cli import parse_args

def test_run_command():
    run_command("ls")
    run_command("cat","foo")
    (output, output_stderr, exit_status) = run_command("ls2")
    assert exit_status != 0



def test_safe_run():
    safe_run("ls",expected=0)
    safe_run("ls",expected=0)
    safe_run("cat","foo")
    (output, output_stderr, exit_status) = safe_run("ls2",expected=-1)
    assert exit_status != 0


def test_deb822():
    files = Changes(open("tests/samples/morse-simulator_1.2.1-2_amd64.changes", "r")).get("Files", [])
    assert files is not None
#    assert "morse-simulator_1.2.1-2.dsc" in files


def test_get_auth_method_without_cli_option_and_without_yaml_config():
    # Default value in args is 'ssl'
    args = parse_args(['--auth', 'ssl'])
    config = {}

    auth_method = get_auth_method(args, config)

    assert auth_method == 'ssl'

def test_get_auth_method_without_cli_option_but_with_yaml_config():
    # Default value in args is 'ssl'
    args = parse_args(['--auth', 'ssl'])
    config = {'xmlrpc': {'auth_method': 'simple'}}

    auth_method = get_auth_method(args, config)

    assert auth_method == 'simple'

def test_get_auth_method_with_cli_option_and_without_yaml_config():
    args = parse_args(['--auth', 'simple'])
    config = {}

    auth_method = get_auth_method(args, config)

    assert auth_method == 'simple'
