import debile.utils.config as config_utils

import os
import shutil
import yaml
import unittest


class ConfigTestCase(unittest.TestCase):
    config = os.path.expanduser('~/.config/debile/config.yaml')
    config_dir = os.path.expanduser('~/.config/debile')


    @classmethod
    def setUp(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        with open(self.config, 'w') as f:
            f.write(yaml.dump(dict(A = 'a')))

    
    @classmethod
    def tearDown(self):
        if os.path.isfile(self.config):
            shutil.rmtree(self.config_dir, ignore_errors=True)


    def test_find_config_file_that_exists(self):
        found_file = config_utils._find_config_file('config.yaml')

        self.assertEqual(found_file, self.config)


    def test_find_config_file_that_not_exists(self):
        self.assertRaises(Exception, config_utils._find_config_file,'fake.yaml')


    def test_get_config(self):
        file_content = config_utils.get_config('config.yaml')

        self.assertEqual(file_content['A'], 'a')


    def test_get_config_passing_path(self):
        file_content = config_utils.get_config('config.yaml', self.config)

        self.assertEqual(file_content['A'], 'a')
