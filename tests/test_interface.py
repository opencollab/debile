from debile.master.dimport import dimport
from debile.master.interface import DebileMasterInterface, NAMESPACE
from debile.master.orm import Base, Builder, Person


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import unittest


class DebileInterfaceTestCase(unittest.TestCase):
    def setUp(self):
        # setup the database
        engine = create_engine(os.environ['DATABASE_URI'],
                               implicit_returning=False)

        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()
        Base.metadata.drop_all(self.session.bind)

        # feed database
        class Args:
            pass
        args = Args()
        args.file = 'tests/resources/debile.yaml'
        args.force = False
        dimport(args, self.session)

        # some more setting up
        u = self.session.query(Person).filter_by(
            email='clement@mux.me'
        ).first()
        NAMESPACE.user = u

        self.blade01_key = None
        with open('tests/resources/blade01.pgp') as f:
            self.blade01_key = f.read()

    def test_create_builder(self):
        interface = DebileMasterInterface(pgp_keyring=u'tests/resources/keyring')
        NAMESPACE.session = self.session
        interface.create_builder('blade01', self.blade01_key, ip='10.0.0.1')

        b = self.session.query(Builder).filter_by(name='blade01').one()

        assert b.ssl is None
        assert b.ip == '10.0.0.1'
        assert b.pgp == '7C367D02AF6D20DCF2BFB686E8D62122F818733D'
