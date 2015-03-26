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

from firehose.model import Issue, File, Message, Location, Point
import re


LINE_RE = re.compile(r"\[(?P<err>E|F|W|C|R)\](?P<path>[^:]+):(?P<line>\d+),(?P<col>\d+):\((?P<id>\w+)\)(?P<msg>.*)")


def parse_pylint(lines):
    severity_opts = {'E': 'error',
                     'F': 'fatal',
                     'W': 'warning',
                     'C': 'convention',
                     'R': 'refactor'}

    for line in lines:
        if LINE_RE.match(line):
            info = LINE_RE.match(line).groupdict()
        else:
            continue

        severity = severity_opts[info['err']]

        yield Issue(cwe=None, testid=info['id'],
                    location=Location(file=File(info['path'], None),
                    function=None,
                    point=Point(int(info['line']), int(info['col']))),
                    severity=severity,
                    message=Message(text=info['msg']), notes=None, trace=None)
