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

from firehose.model import Issue, Message, File, Location, Point
import re


LINE_RE = re.compile(
    r"(?P<path>.*):(?P<line>\d+) - (?P<msg>.*)"
)


def parse_roodi(lines):
    dic = {'should': 'warning', 'missing': 'error', "Don't": 'critical'}

    for line in lines:
        info = LINE_RE.match(line)
        if info is not None:
            info.groupdict()
            testid = str(id(line))
            # TODO find a pretty way to remove color escape codes
            path = info.group('path')[5:]
            message = info.group('msg')[:-5]
            for key in dic:
                if key in info.group('msg'):
                    severity = dic[key]
            yield Issue(cwe=None,
                        testid=testid,
                        location=Location(
                            file=File(path, None),
                            function=None,
                            point=Point(int(info.group('line')), 1)
                        ),
                        severity=severity,
                        message=Message(message),
                        notes=None,
                        trace=None)
