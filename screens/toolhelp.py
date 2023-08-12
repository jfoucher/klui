from textual.app import ComposeResult
from textual.widgets import MarkdownViewer

from textual.containers import Vertical, VerticalScroll
from widgets.button import SmallButton
from textual.screen import ModalScreen
from rich.text import Text



HELP_TEXT = """\
# Toolhead Help

This screen presents a list of all axis present on the printer
Pressing the up and down arrow keys will select one of the axes.

- Press `F1` for this help
- Press `F2` to return to the main screen
- Press `F3` to home the selected axis
- Press `F4` to home all axes
- Press `F5` to set the position of the selected axis
- Press `F6` to move the selected axis in a positive direction
- Press `F7` to move the selected axis in a negative direction
- Press `F8` to trigger an emergenvy shutdown

"""


class ToolhelpScreen(ModalScreen):
    """Screen with a dialog to show help."""
    def compose(self) -> ComposeResult:
        cancel = Text()
        cancel.append("C", style="bold green on white")
        cancel.append("lose")
        with Vertical(id="help_dialog", classes="dialog"):
            with VerticalScroll():
                yield MarkdownViewer(HELP_TEXT, show_table_of_contents=False)

            yield SmallButton(cancel, id="cancel")


    def on_key(self, event):
        if event.key and (event.key == "C" or event.key == "c" or event.key == "escape"):
            self.app.pop_screen()

    def on_small_button_pressed(self, event: SmallButton.Pressed) -> None:
        if event.id == "cancel":
            self.app.pop_screen()
