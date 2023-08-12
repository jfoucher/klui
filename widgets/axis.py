from textual.app import ComposeResult
from textual.widgets import Label, Input, Button
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Horizontal
from textual.validation import Number
from textual.message import Message
from widgets.button import SmallButton
from widgets.header import ReactiveLabel


class CurrentPos(Label):
    """Show current position"""
    pos = reactive(0.0)

    def render(self) -> str:
        return " {:3.2f}".format(self.pos)
class Axis(Widget):
    """Show axis home button and position"""

    homed = reactive(False)
    position = reactive(0.0)
    selected = reactive(False)

    def __init__(self, *children: Widget, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False, selected: bool = False) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        self.selected = selected

    class ChangePosition(Message):
        """Sent when the set position changes."""

        def __init__(self, pos: float, id: str) -> None:
            super().__init__()
            self.pos = pos
            self.id = id

    # pass axis name in d
    def compose(self) -> ComposeResult:
        id = self.id.replace("axis_", "")

        with Horizontal():
            yield Label(f"{id.upper()}", classes="axis_name")
            yield ReactiveLabel(f"Unhomed", classes="axis_homed")
            yield CurrentPos(classes='axis_pos')

    def on_key(self, event):
        print(self.id, event.key)
        if event.key and (event.key == 'h' or event.key == 'H'):
            ax = self.id.replace("axis_", "")
            print(f"home {ax} axis")
        else:
            self.app.get_screen('toolhead').post_message(event)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Validate input temperature
        if len(event.validation_result.failures) == 0:
            self.query_one(CurrentPos).pos = event.value
            self.post_message(Axis.ChangePosition(pos=event.value, id=self.id))
        else:
            print(event.validation_result.failures[0].description)
