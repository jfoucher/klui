from textual.app import ComposeResult
from textual.widgets import Label, Input, Button, RichLog
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Vertical

from textual.validation import Number
from textual.message import Message
from textual.geometry import Size
from textual.strip import Strip
from textual.scroll_view import ScrollView

from rich.segment import Segment

class ConsoleLog(RichLog):
    def add_line(self, line):
        self.write(f"{line}")

    
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
                yield ConsoleLog(id="console_log")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        print(event.value)
        self.post_message(Console.SendGcode(gcode=event.value, id=self.id))
        self.add_line(event.value)

        event.input.value = ""

    def add_line(self, line):
        self.query_one(ConsoleLog).add_line(line)
        # self.query_one(ConsoleLog).text = f"{line}\n" + self.query_one(Log).text
