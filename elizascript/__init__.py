import io
from typing import Any, Tuple

from elizascript.script import Script

class StringIOWithPeek(io.StringIO):
    def peek(self, size=1):
        current_position = self.tell()
        data = self.read(size)
        self.seek(current_position)
        return data


