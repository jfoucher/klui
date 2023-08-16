
from textual.widgets import Static, Label
from textual.message import Message
from textual.binding import Binding
from textual.containers import Horizontal, Container
from textual.app import ComposeResult
from rich.console import RenderableType

class SmallButton(Static, can_focus=True):
    shortcut = ""
    text = ""

    def __init__(self, renderable: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False, shortcut: str | None = None, text: str | None = None) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled)
        self.shortcut = self.renderable[0:1]
        self.text = self.renderable[1:]
        if shortcut:
            self.shortcut = shortcut
        if text:
            self.text = text
    class Pressed(Message):
        def __init__(self, id: str | None) -> None:
            self.id = id
            super().__init__()

    
    def compose(self) -> ComposeResult:
        with Container():
            with Horizontal():
                yield Label(self.shortcut, classes='shortcut')
                yield Label(self.text, classes='text')

    def on_click(self) -> None:
        # The post_message method sends an event to be handled in the DOM
        self.post_message(self.Pressed(self.id))

    def on_key(self, event):
        if event.key == 'enter':
            self.on_click()


class SmallCancelButton(SmallButton):
    def render(self) -> str:
        return self.renderable
class SmallButtonNoFocus(SmallButton, can_focus=False):
    pass