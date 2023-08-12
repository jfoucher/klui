from textual.app import ComposeResult
from textual.widgets import MarkdownViewer

from textual.containers import Vertical, VerticalScroll
from widgets.button import SmallButton
from textual.screen import ModalScreen
from rich.text import Text



HELP_TEXT = """\
# KLUI Help

KLUI is a simple controller for a klipper-enabled 3D printer. It requires the Moonraker server as well.

## Features

- View all the reported temperatures and change their targets, for both heaters and temperature fans.
- View this help text

## Shortcuts
All shortcuts have the first letter highlighted, representing the key to be pressed to trigger the action.

Most shortcuts are displayed in the app footer.
For example, press the `F2` key to exit the app. The will popup a confirmation dialog. press `q` to quit, or `c` to cancel.
If you have a mouse, you can also click on the shortcuts as if they were buttons to trigger the action.

You can also press `escape` to exit any modal window that may be open to return to the main screen.

When you are in another screen, regular shortcuts are disabled. The only one that will always function is the `F8` key that will trigger an emergency stop. 
"""


class HelpScreen(ModalScreen):
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
