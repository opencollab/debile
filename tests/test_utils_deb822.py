from debile.utils.deb822 import Changes

import unittest


class Deb822TestCase(unittest.TestCase):
    def test_deb822(self):
        files = Changes(
                open("tests/samples/morse-simulator_1.2.1-2_amd64.changes", 
                    "r")).get("Files", [])
        self.assertIsNotNone(files)
