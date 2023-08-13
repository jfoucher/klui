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
- Home X, Y and Z axes (I do not have another type of printer to test)
- View the position of X Y and Z axes
- Do a quad gantry leveling procedure if your printer supports it
- Show the status of the printer (printing or not, homed, QGL, filament sensors, steppers active, system load)
- View this help text

## Shortcuts
Some shortcuts have the first letter highlighted, representing the key to be pressed to trigger the action.

Most shortcuts are displayed in the app footer, the number represents the function key to press to launch the action.
For example, press the `F2` key to exit the app. The will popup a confirmation dialog. press `q` to quit, or `c` to cancel.
If you have a mouse, you can also click on the shortcuts as if they were buttons to trigger the action.

You can also press `escape` to exit any modal window that may be open to return to the main screen.

When you are in another screen, regular shortcuts are disabled. The only one that will always function is the `F8` key that will trigger an emergency stop. 
"""


class HelpScreen(ModalScreen):
    """Screen with a dialog to show help."""
    def compose(self) -> ComposeResult:
        with Vertical(id="help_dialog", classes="dialog"):
            with VerticalScroll():
                yield MarkdownViewer(HELP_TEXT, show_table_of_contents=False)

            yield SmallButton('Close', id="cancel", classes='cancel')


    def on_key(self, event):
        if event.key and (event.key == "C" or event.key == "c" or event.key == "escape"):
            self.app.pop_screen()

    def on_small_button_pressed(self, event: SmallButton.Pressed) -> None:
        if event.id == "cancel":
            self.app.pop_screen()
