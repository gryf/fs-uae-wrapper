"""
Display message as simple text on console
"""
import sys


class Message:
    """Just a fake message window for systems without TK"""

    def __init__(self, msg):
        self.msg = msg
        self._process = None

    def show(self):
        sys.stdout.write(self.msg + "\n")

    def close(self):
        return None
