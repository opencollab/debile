from debile.utils.xmlrpc import get_proxy

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
