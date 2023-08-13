
from textual.widgets import Static, Label
from textual.message import Message
from textual.binding import Binding
from textual.containers import Horizontal, Container
from textual.app import ComposeResult
from rich.console import RenderableType

class SmallButton(Static, can_focus=True):

    class Pressed(Message):
        def __init__(self, id: str | None) -> None:
            self.id = id
            super().__init__()

    
    def compose(self) -> ComposeResult:
        with Container():
            with Horizontal():
                yield Label(self.renderable[0:1], classes='shortcut')
                yield Label(self.renderable[1:], classes='text')

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