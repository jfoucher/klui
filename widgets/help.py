from textual.app import App, ComposeResult
from textual import log
from textual.binding import Binding
from textual.widgets import MarkdownViewer, LoadingIndicator, Label, Input, Header, Footer, Button, Static, Placeholder
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Grid, Container, Horizontal, Vertical, VerticalScroll
import argparse

import asyncio
import json
import random
import websockets
from widgets.temp import Connected, Heater, CurrentTemp, SetTemp, TemperatureFan
from widgets.axis import Axis, CurrentPos
from widgets.console import Console
from widgets.button import SmallButton
from textual.screen import ModalScreen, Screen
from rich.segment import Segment
from textual.strip import Strip
from rich.style import Style
from rich.text import Text



HELP_TEXT = """\
# Markdown Viewer

This is an example of Textual's `MarkdownViewer` widget.


## Features

Markdown syntax and extensions are supported.

- Typography *emphasis*, **strong**, `inline code` etc.
- Headers
- Lists (bullet and ordered)
- Syntax highlighted code blocks
- Tables!

## Tables

Tables are displayed in a DataTable widget.

| Name            | Type   | Default | Description                        |
| --------------- | ------ | ------- | ---------------------------------- |
| `show_header`   | `bool` | `True`  | Show the table header              |
| `fixed_rows`    | `int`  | `0`     | Number of fixed rows               |
| `fixed_columns` | `int`  | `0`     | Number of fixed columns            |
| `zebra_stripes` | `bool` | `False` | Display alternating colors on rows |
| `header_height` | `int`  | `1`     | Height of header row               |
| `show_cursor`   | `bool` | `True`  | Show a cell cursor                 |


## Code Blocks

Code blocks are syntax highlighted, with guidelines.

```python
class ListViewExample(App):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )
        yield Footer()
```
"""


class HelpScreen(ModalScreen):
    """Screen with a dialog to show help."""
    def compose(self) -> ComposeResult:
        cancel = Text()
        cancel.append("C", style="bold magenta")
        cancel.append("lose")
        with Vertical(id="help_dialog", classes="dialog"):
            with VerticalScroll():
                yield MarkdownViewer(HELP_TEXT, show_table_of_contents=False)

            yield SmallButton(cancel, id="cancel")


    def on_key(self, event):
        if event.key and (event.key == "c" or event.key == "escape"):
            self.app.pop_screen()

    def on_small_button_pressed(self, event: SmallButton.Pressed) -> None:
        if event.id == "cancel":
            self.app.pop_screen()
