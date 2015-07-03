from debile.utils.xmlrpc import get_proxy
from debile.utils.xmlrpc import DebileSafeTransport

import xmlrpclib
import unittest


class UtilsXMLRPCTestCase(unittest.TestCase):
    def test_get_proxy_without_xml(self):
        self.assertRaises(Exception, get_proxy, dict(), 'simple')


    def test_get_proxy_simple_auth(self):
        data = dict(xmlrpc = dict(host='localhost', port='22017'))

        proxy = get_proxy(data, 'simple')

        self.assertEquals(proxy.__dict__['_ServerProxy__host'],
                'localhost:22017')
        self.assertTrue(proxy.__dict__['_ServerProxy__allow_none'])


    def test_get_proxy_ssl_auth(self):
        data = dict(xmlrpc = dict(host='localhost', port='22017',
            keyfile='~/keyfile.key', certfile='~/certfile.crt'))

        proxy = get_proxy(data, 'ssl')

        self.assertEquals(proxy.__dict__['_ServerProxy__host'],
                'localhost:22017')
        self.assertTrue(proxy.__dict__['_ServerProxy__allow_none'])
        self.assertIsInstance(proxy.__dict__['_ServerProxy__transport'],
                DebileSafeTransport)
