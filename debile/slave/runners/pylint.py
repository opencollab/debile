# Copyright (c) 2015 Lucas Kanashiro <kanashiro.duarte@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from debile.slave.wrappers.pylint import parse_pylint
from debile.slave.utils import cd
from debile.utils.commands import run_command
import os
import fnmatch


def find_python_files(directory):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, '*.py'):
                filename = os.path.join(root, basename)
                yield filename


def pylint(dsc, analysis):
    run_command(["dpkg-source", "-x", dsc, "source-pylint"])
    with cd('source-pylint'):
        sources = find_python_files('.')
        failed = False
        output = ""

        for source in sources:
            out, _, ret = run_command([
                'pylint', '-rn',
                '--msg-template="[{C}]{path}:{line},{column}:({msg_id})[{symbol}]{msg}"',
                source
            ])
            failed = ret != 0

            if out is not None:
                output += out

                for issue in parse_pylint(out.splitlines()):
                    analysis.results.append(issue)

        return (analysis, output, failed, None, None)


def version():
    out, _, ret = run_command(['pylint', '--version'])
    if ret != 0:
        raise Exception("pylint is not installed")
    name, version = out.splitlines()[0].strip(" ").split(" ")
    return (name, version.strip(','))
