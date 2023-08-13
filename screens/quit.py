from textual.app import ComposeResult
from textual.widgets import Label
from textual.containers import Grid
from widgets.button import SmallButton
from textual.screen import ModalScreen
from rich.text import Text


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            SmallButton('Quit', id="quit", classes='action'),
            SmallButton('Cancel', id="close", classes='cancel'),
            id="quit_dialog",
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
