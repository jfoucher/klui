from textual.app import App, ComposeResult
from textual import log
from textual.binding import Binding
from textual.widgets import LoadingIndicator, Label, Input, Header, Footer, Button, Static, Placeholder
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
from widgets.help import HelpScreen
from textual.screen import ModalScreen, Screen
from rich.segment import Segment
from textual.strip import Strip
from rich.style import Style
from rich.text import Text


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""
    def compose(self) -> ComposeResult:
        cancel = Text()
        cancel.append("C", style="bold green on white")
        cancel.append("ancel")
        quit = Text()
        quit.append("Q", style="bold red on white")
        quit.append("uit")
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            SmallButton(quit, id="quit"),
            SmallButton(cancel, id="cancel"),
            id="quit_dialog",
            classes="dialog"
        )

    def on_key(self, event):
        if event.key and event.key == "q":
            self.app.exit()
        elif event.key and (event.key == "c" or event.key == "escape"):
            self.app.pop_screen()

    def on_small_button_pressed(self, event: SmallButton.Pressed) -> None:
        if event.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()
