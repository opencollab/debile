from debile.utils.commands import run_command
from debile.utils.commands import safe_run
from debile.utils.commands import SubprocessError

import unittest


class CommandsTestCase(unittest.TestCase):
    def test_run_command_wrong_one(self):
        (output, output_stderr, exit_status) = run_command("ls2")
        self.assertNotEqual(exit_status, 0)


    def test_run_command_simple_one(self):
        (output, output_stderr, exit_status) = run_command(["echo", "hello"])
        self.assertEqual(exit_status, 0)


    def test_run_command_without_list(self):
        (output,output_stderr,exit_status) = run_command("echo -e hello\nworld")
        self.assertEqual(exit_status, 0)


    def test_run_command_with_input(self):
        command_input = "test run command"
        (output, output_stderr, exit_status) = run_command("cat", command_input)
        self.assertEqual(output, "test run command")
        self.assertEqual(exit_status, 0)


    def test_run_command_handle_exception(self):
        (output, output_stderr, exit_status) = run_command("xls")
        self.assertIsNone(output)
        self.assertIsNone(output_stderr)
        self.assertEqual(exit_status, -1)


    def test_safe_run_simple(self):
        (output, output_stderr, exit_status) = safe_run("ls",expected=0)
        self.assertEqual(exit_status, 0)


    def test_safe_run_with_expected_wrong_exit_code(self):
        (output, output_stderr, exit_status) = safe_run("ls2",expected=-1)
        self.assertEqual(exit_status, -1)


    def test_safe_run_without_tuple(self):
        (output, output_stderr, exit_status) = safe_run("ls")
        self.assertEqual(exit_status, 0)


    def test_safe_run_raise_exception(self):
        self.assertRaises(SubprocessError, safe_run, "ls", expected=-1)
