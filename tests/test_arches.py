from debile.master.arches import get_preferred_affinity, get_source_arches


class FnordArch(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Fnord: %s>" % (self.name)


valid_arches = [
    FnordArch("amd64"),
    FnordArch("sparc"),
    FnordArch("ppc64"),
    FnordArch("kfreebsd-amd64"),
    FnordArch("kfreebsd-i386"),
    FnordArch("hurd-amd64"),
    FnordArch("hurd-i386"),
    FnordArch("armhf"),
    FnordArch("armel"),
    FnordArch("mips"),
]


def test_affinity_basic():
    arch = get_preferred_affinity(
        ['amd64', 'sparc', 'armhf'],
        ["amd64", "sparc", "ppc64"],
        valid_arches
    )
    assert arch.name == 'amd64'


def test_affinity_out_of_order():
    arch = get_preferred_affinity(
        ['amd64', 'sparc', 'armhf'],
        ["ppc64", "sparc", "amd64"],
        valid_arches
    )
    assert arch.name == 'amd64'


def test_affinity_secondary():
    arch = get_preferred_affinity(
        ['amd64', 'sparc', 'armhf'],
        ["ppc64", "sparc"],
        valid_arches
    )
    assert arch.name == 'sparc'


def test_affinity_any():
    arch = get_preferred_affinity(
        ['amd64', 'sparc', 'armhf'],
        ["any"],
        valid_arches
    )
    assert arch.name == 'amd64'


def test_affinity_linux_any():
    arch = get_preferred_affinity(
        ['amd64', 'sparc', 'armhf'],
        ["linux-any"],
        valid_arches
    )
    assert arch.name == 'amd64'


def test_affinity_any_arm():
    arch = get_preferred_affinity(
        ['amd64', 'sparc', 'armhf'],
        ["any-arm"],
        valid_arches
    )
    assert arch.name == 'armhf'


def test_affinity_fail():
    try:
        arch = get_preferred_affinity(
            ['amd64', 'sparc', 'armhf'],
            ["ppc64", "armel"],
            valid_arches
        )
        assert False == True, "Didn't bomb out as expected."
    except ValueError:
        pass


def test_any_arches():
    assert valid_arches == get_source_arches(['any'], valid_arches)


def test_simple_arches():
    assert set(['amd64', 'armhf']) == set([
        x.name for x in get_source_arches(['amd64', 'armhf'], valid_arches)
    ])


def test_kfreebsd_arches():
    assert set([
        'kfreebsd-i386', 'kfreebsd-amd64', 'armhf'
    ]) == set([
        x.name for x in get_source_arches([
            'kfreebsd-i386', 'kfreebsd-amd64', 'armhf'
        ], valid_arches)
    ])


def test_hurd_arches():
    assert set([
        'hurd-i386', 'hurd-amd64', 'armel'
    ]) == set([
        x.name for x in get_source_arches([
            'hurd-i386', 'hurd-amd64', 'armel'
        ], valid_arches)
    ])


from debile.master.arches import arch_matches
from debile.master.orm import Arch

import unittest
import mock


class ArchesTestCase(unittest.TestCase):
    arches = [
        Arch(name="amd64"),
        Arch(name="sparc"),
        Arch(name="ppc64"),
        Arch(name="kfreebsd-amd64"),
        Arch(name="kfreebsd-i386"),
        Arch(name="hurd-amd64"),
        Arch(name="hurd-i386"),
        Arch(name="armhf"),
        Arch(name="armel"),
        Arch(name="mips"),
    ]


    def test_arch_matches_arch_equal_alias(self):
        self.assertTrue(arch_matches('amd64','amd64'))


    def test_arch_matches_pseudo_arches(self):
        self.assertFalse(arch_matches('all', 'amd64'))
        self.assertFalse(arch_matches('source', 'amd64'))


    def test_arch_matches_any_arch(self):
        self.assertTrue(arch_matches('amd64', 'any'))


    def test_arch_matches_linux_any_alias(self):
        self.assertTrue(arch_matches('amd64', 'linux-any'))
        self.assertTrue(arch_matches('linux-amd64', 'linux-any'))
        self.assertFalse(arch_matches('hurd-i386', 'linux-any'))


    def test_arch_matches_ends_with_any(self):
        self.assertTrue(arch_matches('bsd-amd64', 'bsd-any'))
        self.assertFalse(arch_matches('linux-amd64', 'kfreebsd-any'))


    def test_arch_matches_without_dash(self):
        self.assertFalse(arch_matches('any', 'amd64'))


    @mock.patch('debile.master.arches.run_command', return_value=(0,0,0))
    def test_arch_matches_with_successful_run_command(self, mock):
        self.assertTrue(arch_matches('linux-amd64', 'amd64'))


    @mock.patch('debile.master.arches.run_command', return_value=(2,2,2))
    def test_arch_matches_with_unsuccessful_run_command(self, mock):
        self.assertFalse(arch_matches('linux-amd64', 'i386'))


    def test_get_preferred_affinity_value_error(self):
        affinity = ['linux-amd64']
        valid = ['linux-i386']

        self.assertRaises(ValueError, get_preferred_affinity, affinity, valid,
                self.arches)


    @mock.patch('debile.master.arches.arch_matches', return_value=True)
    def test_get_preferred_affinity(self, mock):
        affinity = ['amd64']
        valid = ['i386']

        arch = get_preferred_affinity(affinity, valid, self.arches)

        self.assertEquals(arch.name, 'amd64')


    @mock.patch('debile.master.arches.arch_matches', return_value=False)
    def test_get_source_arches_without_matches(self, mock):
        dsc_arch = ['linux-i386']

        ret = get_source_arches(dsc_arch, self.arches)

        self.assertEquals(ret, [])


    @mock.patch('debile.master.arches.arch_matches', return_value=True)
    def test_get_source_arches_without_matches(self, mock):
        dsc_arch = ['amd64', 'sparc']

        ret = get_source_arches(dsc_arch, self.arches)

        self.assertEquals(ret[0].name, 'amd64')
        self.assertEquals(ret[1].name, 'sparc')
