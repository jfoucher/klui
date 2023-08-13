from textual.app import ComposeResult
from textual.widgets import Label
from textual.containers import Vertical
from widgets.button import SmallButton
from textual.screen import ModalScreen
from rich.text import Text


class ErrorScreen(ModalScreen):
    text = ""
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None, text: str|None = None) -> None:
        super().__init__(name, id, classes)
        self.text = text

    """Screen with a dialog to quit."""
    def compose(self) -> ComposeResult:


        yield Vertical(
            Label(self.text, id="question"),
            SmallButton('Close', id="close", classes='cancel'),
            id="error_dialog",
            classes="dialog"
        )

    def on_key(self, event):
        if event.key and event.key == "q":
            self.app.exit()
        elif event.key and(event.key == "C" or event.key == "c" or event.key == "escape"):
            self.app.pop_screen()

    def on_small_button_pressed(self, event: SmallButton.Pressed) -> None:
        if event.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()
