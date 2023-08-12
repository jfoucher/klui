from textual.app import ComposeResult
from textual.widgets import Input, RichLog
from textual.widget import Widget

from textual.containers import Container, Vertical


from textual.message import Message
import re
from functools import lru_cache
from typing import Callable, List

LINE_AND_ENDING_PATTERN = re.compile(r"(.*?)(\r\n|\r|\n|$)", re.S)


@lru_cache(maxsize=4096)
def get_character_cell_size(character: str) -> int:
    """Get the cell size of a character.

    Args:
        character (str): A single character.

    Returns:
        int: Number of cells (0, 1 or 2) occupied by that character.
    """
    return _get_codepoint_cell_size(ord(character))


@lru_cache(maxsize=4096)
def _get_codepoint_cell_size(codepoint: int) -> int:
    """Get the cell size of a character.

    Args:
        character (str): A single character.

    Returns:
        int: Number of cells (0, 1 or 2) occupied by that character.
    """

    _table = CELL_WIDTHS
    lower_bound = 0
    upper_bound = len(_table) - 1
    index = (lower_bound + upper_bound) // 2
    while True:
        start, end, width = _table[index]
        if codepoint < start:
            upper_bound = index - 1
        elif codepoint > end:
            lower_bound = index + 1
        else:
            return 0 if width == -1 else width
        if upper_bound < lower_bound:
            break
        index = (lower_bound + upper_bound) // 2
    return 1

@lru_cache(4096)
def cached_cell_len(text: str) -> int:
    """Get the number of cells required to display text.

    This method always caches, which may use up a lot of memory. It is recommended to use
    `cell_len` over this method.

    Args:
        text (str): Text to display.

    Returns:
        int: Get the number of cells required to display text.
    """
    _get_size = get_character_cell_size
    total_size = sum(_get_size(character) for character in text)
    return total_size

def cell_len(text: str, _cell_len: Callable[[str], int] = cached_cell_len) -> int:
    """Get the number of cells required to display text.

    Args:
        text (str): Text to display.

    Returns:
        int: Get the number of cells required to display text.
    """
    if len(text) < 512:
        return _cell_len(text)
    _get_size = get_character_cell_size
    total_size = sum(_get_size(character) for character in text)
    return total_size

def line_split(input_string: str) -> list[tuple[str, str]]:
    r"""
    Splits an arbitrary string into a list of tuples, where each tuple contains a line of text and its line ending.

    Args:
        input_string (str): The string to split.

    Returns:
        list[tuple[str, str]]: A list of tuples, where each tuple contains a line of text and its line ending.

    Example:
        split_string_to_lines_and_endings("Hello\r\nWorld\nThis is a test\rLast line")
        >>> [('Hello', '\r\n'), ('World', '\n'), ('This is a test', '\r'), ('Last line', '')]
    """
    return LINE_AND_ENDING_PATTERN.findall(input_string)[:-1] if input_string else []

    
class Console(Widget):

    class SendGcode(Message):
        """Sent when the set position changes."""

        def __init__(self, gcode: str, id: str) -> None:
            super().__init__()
            self.gcode = gcode
            self.id = id

    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Input(
                    placeholder="Send code...",
                    classes="console_input",
                )
                yield RichLog(id="console_log")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        print(event.value)
        self.post_message(Console.SendGcode(gcode=event.value, id=self.id))
        self.add_line(event.value)

        event.input.value = ""

    def add_line(self, line):
        self.query_one(RichLog).write(line)
        # self.query_one(ConsoleLog).text = f"{line}\n" + self.query_one(Log).text
