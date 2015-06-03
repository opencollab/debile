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


FILE_RE = re.compile(r'\t*<file name="(?P<file>[^"]+)"')
LINE_RE = re.compile(r'\t*<error line="(?P<line>\d+)" column="(?P<col>\d+)" severity="(?P<severity>[^"]+)" message="(?P<msg>[^"]+)" source="jshint.(?P<testid>[\w\d]+)"')


def parse_jshint(lines):
    for line in lines:
        if FILE_RE.match(line):
            path = FILE_RE.match(line).groupdict()
        if LINE_RE.match(line):
            info = LINE_RE.match(line).groupdict()
        else:
            continue

        yield Issue(cwe=None, testid=info['testid'],
                    location=Location(
                        file=File(path['file'], None),
                        function=None,
                        point=Point(int(info['line']), int(info['col']))),
                    severity=info['severity'],
                    message=Message(text=info['msg']), notes=None, trace=None)
