
from textual.widgets import Static
from textual.reactive import reactive
from rich.console import RenderableType
from textual.color import Color
from textual.message import Message
from textual.binding import Binding

class SmallButton(Static):
    BINDINGS = [Binding("enter", "press", "Press Button", show=False)]

    class Pressed(Message):
        def __init__(self, id: str | None) -> None:
            self.id = id
            super().__init__()


    def on_click(self) -> None:
        # The post_message method sends an event to be handled in the DOM
        self.post_message(self.Pressed(self.id))


    def render(self) -> str:
        return self.renderable
        
    def action_press(self):
        self.post_message(self.Pressed(self.id))