from textual.app import ComposeResult
from textual.widgets import MarkdownViewer, Button

from textual.containers import Vertical, VerticalScroll, Container
from widgets.button import SmallButton
from textual.screen import ModalScreen
from rich.text import Text



HELP_TEXT = """\
# Toolhead Help

This screen presents a list of all axis present on the printer.

Pressing the up and down arrow keys will select one of the axes.

- Press `F1` for this help
- Press `F2` to home the selected axis
- Press `F3` to return to the main screen
- Press `F4` to home all axes
- Press `F5` to set the position of the selected axis
- Press `F6` to move the selected axis
- Press `F7` to start the quad gantry leveling (if supported by your printer)
- Press `F8` to trigger an emergency shutdown

"""


class ToolhelpScreen(ModalScreen):
    """Screen with a dialog to show help."""
    def compose(self) -> ComposeResult:
        with Container(id="help_dialog", classes="dialog"):
            with VerticalScroll():
                yield MarkdownViewer(HELP_TEXT, show_table_of_contents=False)
            yield SmallButton('Close', id="cancel", classes='cancel')


    def on_key(self, event):
        if event.key and (event.key == "C" or event.key == "c" or event.key == "escape"):
            self.app.pop_screen()

    def on_small_button_pressed(self, event: SmallButton.Pressed) -> None:
        if event.id == "cancel":
            self.app.pop_screen()
