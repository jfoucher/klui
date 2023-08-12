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
from widgets.quit import QuitScreen
from widgets.help import HelpScreen
from textual.screen import ModalScreen, Screen
from rich.segment import Segment
from textual.strip import Strip
from rich.style import Style
from rich.text import Text
from rich.console import RenderableType

class ReactiveLabel(Label):
    label = reactive("")
    def __init__(self, renderable: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled)
        self.label = renderable

    def render(self) -> str:
        return f"{self.label}"
class KluiHeader(Widget):
    def compose(self) -> ComposeResult:
        with Container():
            with Horizontal():
                yield Connected(id="klippy_status", classes="header")
                yield ReactiveLabel("Unkown", id="status")
                yield ReactiveLabel("", id="file")
                yield ReactiveLabel("0%", id="completion")
                yield ReactiveLabel("\uf015", id="homed")
                yield ReactiveLabel("\udb80\uddfa".encode('utf-16','surrogatepass').decode('utf-16'), id="motors")
                #\udb82\ude46
                yield ReactiveLabel("\udb85\udedf".encode('utf-16','surrogatepass').decode('utf-16'), id="filament")
                yield Static()
                yield ReactiveLabel("Load", id="sysload")
    
    async def update(self, data):
        if 'quad_gantry_level' in data:
            try :
                qgl_btn = self.query_one('#qgl_button')
            except Exception:
                variant = "warning"
                if data['quad_gantry_level']['applied']:
                    variant = "success"
                # qgl_btn = Button("QGL", classes="home_button", id="qgl_button", variant=variant, disabled=True)
                # await self.query_one('#home_buttons').mount(qgl_btn)

        if 'idle_timeout' in data and 'state' in data['idle_timeout']:
            state = data['idle_timeout']['state']
            if state == 'Printing':
                self.query_one('#file').styles.display = "block"
                self.query_one('#completion').styles.display = "block"
                self.query_one('#status').styles.background = 'green'
            else:
                self.query_one('#file').styles.display = "none"
                self.query_one('#completion').styles.display = "none"
                if state == 'Idle':
                    self.query_one('#status').styles.background = 'darkgray'
                else:
                    # Ready state
                    self.query_one('#status').styles.background = 'darkcyan'
            self.query_one('#status').label = state
        if 'toolhead' in data:
            if 'homed_axes' in data['toolhead']:
                homed = data['toolhead']['homed_axes']
                home = self.query_one('#homed')

                if len(homed) < 1:
                    home.styles.background = "red"
                    home.styles.color = "white"
                elif len(homed) < 2:
                    home.styles.background = "orange"
                    home.styles.color = "black"
                elif len(homed) < 3:
                    home.styles.background = "yellow"
                    home.styles.color = "black"
                else:
                    home.styles.background = "green"
                    home.styles.color = "black"
        if 'stepper_enable' in data:
            def steppers_enabled(ls):
                for s in ls:
                    if s:
                        return True
                return False
            print(data['stepper_enable'])
            s = list(data['stepper_enable']['steppers'].values())
            motors = self.query_one('#motors')
            if steppers_enabled(s):
                motors.styles.background = 'darkgreen'
            else:
                motors.styles.background = 'darkred'

        if 'system_stats' in data and 'sysload' in data['system_stats']:
            l = data['system_stats']['sysload']
            self.query_one('#sysload').label = l
            if l < 1.0:
                self.query_one('#sysload').styles.background = "green"
            elif l < 2.0:
                self.query_one('#sysload').styles.background = "orange"
            else:
                self.query_one('#sysload').styles.background = "red"