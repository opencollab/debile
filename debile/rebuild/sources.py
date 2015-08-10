# Copyright (c) 2012-2014 Paul Tagliamonte <paultag@debian.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the Software),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


from debile.rebuild.utils import tmpfile
from debile.rebuild.core import get_sources_uri, db, _get_context
from contextlib import contextmanager
import urllib2
import gzip


@contextmanager
def download_sources():
    with tmpfile() as fd:
        f = urllib2.urlopen(get_sources_uri())
        open(fd, 'w').write(f.read())
        yield (fd, _get_context())


@contextmanager
def process_sources():
    with download_sources() as info:
        fd, suite = info
        with tmpfile():
            f = gzip.open(fd, 'r')
            try:
                yield (f, suite)
            finally:
                pass
            f.close()


def digest_sources():
    sent = None
    with process_sources() as info:
        fd, suite = info
        sent = Sources(suite)
        ret = {}
        key = None
        for line in fd.readlines():
            if line.strip() == "":
                package = PackageEntry(ret)
                sent.add_entry(package)
                ret = {}
                continue

            if line[0] == " ":
                if ret[key] != "":
                    ret[key] += "\n"
                ret[key] += line.strip()
            else:
                line = line.strip()
                key, val = line.split(":", 1)
                key = key.strip()
                ret[key] = val.strip()
    return sent


class PackageEntry(dict):
    def __init__(self, entry, mangle=True):
        if mangle:
            entry = self._mangle(entry)

        for key in entry:
            self[key] = entry[key]

    def _mangle(self, entry):
        for key in ['Build-Depends', 'Build-Depends-Indep']:
            if key in entry:
                entry[key] = [
                    x.split()[0].strip() for x in entry[key].split(",")
                ]

        if 'Uploaders' in entry:
            entry['Uploaders'] = [
                x.strip() for x in entry['Uploaders'].split(",")
            ]

        if 'Package-List' in entry:
            entry['Package-List'] = [
                {
                    "name": y[0],
                    "type": y[1],
                    "section": y[2],
                    "priority": y[3]
                } for y in [
                    x.split() for x in entry['Package-List'].split("\n")
                ]
            ]
        for key in ["Files", "Checksums-Sha256", "Checksums-Sha1"]:
            entry[key] = [
                {
                    "hash": y[0],
                    "size": y[1],
                    "file": y[2]
                } for y in [x.split() for x in entry[key].split("\n")]
            ]

        return entry


class Sources(dict):
    def __init__(self, info):
        self.info = info
        self.base = "{protocol}{base}".format(**info)
        self.suite = info['suite']
        self.dist = info['distro']
        self.version = info['version']

    def add_entry(self, package):
        key = package['Package']
        self[key] = package
        # print "I: New package: %s" % (key)

    def get_table(self):
        suite, dist, version = (
            self.suite, self.dist, self.version
        )
        table = getattr(getattr(getattr(db, dist), version), suite)
        return table

    def load(self):
        table = self.get_table()
        for package in table.find():
            self.add_entry(PackageEntry(package))

    def save(self):
        suite, dist, version = (
            self.suite, self.dist, self.version
        )
        foo = "{dist}/{ver}/{sui}".format(
            dist=dist,
            ver=version,
            sui=suite
        )

        table = self.get_table()
        obj = self.info
        obj['_id'] = foo
        db.meta.update({"_id": foo}, obj, True, safe=True)

        print("Dropping old data")
        table.drop()
        print("Table dropped, reloading")

        for package in self:
            obj = self[package]
            obj['_id'] = obj['Package']
            table.update({"_id": obj['_id']}, obj, True, safe=True)

        print("Updated.")

    def query(self, query):
        table = self.get_table()
        for package in table.find(query, timeout=False):
            yield package
