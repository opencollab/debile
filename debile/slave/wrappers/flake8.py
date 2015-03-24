from firehose.model import Issue, Message, File, Location, Point
import re


LINE_RE = re.compile(
    r"(?P<path>[^:]+):(?P<line>\d+):(?P<col>\d+): (?P<err>[^ ]+) (?P<msg>.*)"
)


def parse_flake8(lines):
    for line in lines:
        info = LINE_RE.match(line).groupdict()
        severity = "error" if info['err'].startswith("E") else "warning"
        if info['err'].startswith("E"):
            severity = "error"
        elif info['err'].startswith("W"):
            severity = "warning"
        elif info['err'].startswith("N8"):
            severity = "warning"
        elif info['err'].startswith("F"):
            severity = "error"
        else:
            severity = "Unknown flake8 plugin code"
        yield Issue(cwe=None,
                    testid=info['err'],
                    location=Location(file=File(info['path'], None),
                                      function=None,
                                      point=Point(*(int(x) for x in (
                                          info['line'], info['col'])))),
                    severity=severity,
                    message=Message(text=line),
                    notes=None,
                    trace=None)
