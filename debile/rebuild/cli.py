# Copyright (c) 2013 Paul Tagliamonte <paultag@debian.org>
# Copyright (c) 2014 Clement Schreiner <clement@mux.me>
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


from debile.rebuild.utils import write_changes, fetch_and_upload
from clint import Args

args = Args()


def forge_changes():
    dist = None
    for flag in args.flags:
        if flag is None:
            break

        k, v = (x.strip() for x in flag.split("=", 1))
        if k == '--dist':
            dist = v

    if dist is None:
        raise Exception("No dist given with --dist=unstable")

    for what in args.files:
        write_changes(what, dist)


def upload_package():
    opts = {
        "dist": "unstable",
        "source": None,
        "version": None,
        "group": None
    }

    for flag in args.flags:
        if flag is None:
            break

        k, v = (x.strip() for x in flag.split("=", 1))
        if k.startswith('--'):
            k = k[2:]
        opts[k] = v

    for k, v in opts.items():
        if v is None:
            raise KeyError(
                "give me --dist=unstable --source=fluxbox --version=1.3.5-1 --group=test"
            )

    if opts['group']:
        opts['X-Debile-Group'] = opts.pop('group')
    else:
        opts.pop('group')

    fetch_and_upload(**opts)
