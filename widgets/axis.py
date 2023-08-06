from textual.app import ComposeResult
from textual.widgets import Label, Input, Button
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Horizontal
from textual.validation import Number
from textual.message import Message

class CurrentPos(Label):
    """Show current position"""

    pos = reactive("0")

    def render(self) -> str:
        return f"{self.pos}"

    async def on_mount(self):
        self.styles.width = 6
        self.styles.margin = 1

class Axis(Widget):
    """Show axis home button and position"""

    class ChangePosition(Message):
        """Sent when the set position changes."""

        def __init__(self, pos: float, id: str) -> None:
            super().__init__()
            self.pos = pos
            self.id = id

    # pass axis name in d
    def compose(self) -> ComposeResult:
        id = self.id.replace("axis_", "")
        with Container():
            with Horizontal():
                yield Button(id.capitalize(), classes="home_button", id=f"home_{id}_button", variant="warning")
                yield CurrentPos()
                yield Input(
                    placeholder="0.0",
                    validators=[
                        Number(minimum=0, maximum=350),
                    ],
                    classes="pos_input",
                )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Validate input temperature
        if len(event.validation_result.failures) == 0:
            self.query_one(CurrentPos).pos = event.value
            self.post_message(Axis.ChangePosition(pos=event.value, id=self.id))
        else:
            print(event.validation_result.failures[0].description)
