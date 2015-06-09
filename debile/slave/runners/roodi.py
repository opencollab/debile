# Copyright (c) 2015 Julien Gamba <jgamba@aius.u-strasbg.fr>
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

from debile.slave.wrappers.roodi import parse_roodi
from debile.slave.utils import cd
from debile.utils.commands import run_command


def roodi(dsc, analysis):
    run_command(["dpkg-source", "-x", dsc, "source-roodi"])
    with cd('source-roodi'):
        out, _, ret = run_command(['roodi', '.'])
        failed = ret != 0

        for issue in parse_roodi(out.splitlines()):
            analysis.results.append(issue)

        return (analysis, out, failed, None, None)


def version():
    out, _, ret = run_command(['roodi', '-v'])
    if ret != 0:
        raise Exception("roodi is not installed")
    version = out
    return ('roodi', version)
