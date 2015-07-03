import debile.master.utils as utils

import unittest
import mock


class MasterUtilsTestCase(unittest.TestCase):
    def test_init_config(self):
        config = utils._init_config('tests/resources/master.yaml')

        self.assertEquals(config['database'], 'sqlite:////srv/debile/debile.db')
        self.assertIsNotNone(config['fedmsg'])
        self.assertIsNotNone(config['xmlrpc'])
        self.assertIsNotNone(config['repo'])
        self.assertIsNotNone(config['keyrings'])


    @mock.patch('debile.master.utils.create_engine')
    @mock.patch('debile.master.utils.Session.configure')
    def test_init_sqlalchemy(self, mock_configure, mock_engine):
        config = {'database':'sqlite:////srv/debile/debile.db'}

        utils._init_sqlalchemy(config)

        self.assertTrue(mock_engine.called)
        self.assertTrue(mock_configure.called)

        args, kwargs = mock_engine.call_args

        self.assertEquals(args, ('sqlite:////srv/debile/debile.db',))
        self.assertFalse(kwargs['implicit_returning']) 
