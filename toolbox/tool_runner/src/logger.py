"""
Logs messsages to a file and redirects stdout and stderror to the logger.
"""

import sys

from datetime import datetime


class Logger:

    _TIME_STAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self, filename):
        self._filename = filename
        with open(self._filename, "w", encoding="utf-8") as fp:
            fp.close()
        self._org_stdout = sys.stdout
        sys.stdout = self
        sys.stderr = self

    def write(self, message):
        message = message.rstrip()
        if message != "":
            timestamp = datetime.now().strftime(self._TIME_STAMP_FORMAT)[:-3]
            output = f"{timestamp} - {message}\n"
            with open(self._filename, "a", encoding="utf-8") as fp:
                fp.write(output)
            if self._org_stdout is not None and callable(self._org_stdout.write):
                self._org_stdout.write(output)

    def flush(self):
        pass
