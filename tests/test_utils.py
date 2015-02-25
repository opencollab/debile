from debile.utils.commands import run_command
from debile.utils.commands import safe_run
from debile.utils.deb822 import Changes

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
