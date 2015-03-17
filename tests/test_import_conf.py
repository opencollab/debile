import tools.debile_slave_import_conf as import_conf

import os
import pwd
import tarfile


def test_editconf():
    assert True


def test_cg():
    with tarfile.open('tests/resources/blade01.tar.gz', 'r:gz') as tf:
        get = import_conf.cg(tf)
        assert get('fingerprint') == 'D6B08791B954F001A7641F8E5564626D79CAB8E8'


def test_import_pgp():
    current_user = pwd.getpwuid(os.getuid()).pw_name
    key = None
    with tarfile.open('tests/resources/blade01.tar.gz', 'r:gz') as tf:
        get = import_conf.cg(tf)
        key = get('key.pub')
    import_conf.import_pgp(current_user, key, 'tests/resources/keyring')
