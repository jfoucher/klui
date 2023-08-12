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
from widgets.header import KluiHeader
from widgets.footer import KluiFooter
from textual.screen import ModalScreen, Screen
from rich.segment import Segment
from textual.strip import Strip
from rich.style import Style
from rich.text import Text

class KluiTemperature(Widget):
    heaters = reactive(['extruder'])

    def compose(self) -> ComposeResult:
        yield Label("Temperatures", classes="title")

    async def update(self, data):
        for heater in self.query(Heater):
            heater.update(data)
        
        for fan in self.query(TemperatureFan):
            fan.update(data)
        if 'heaters' in data and 'available_heaters' in data['heaters']:
            for heater in data['heaters']['available_heaters']:
                try :
                    tmp = self.query_one('#'+heater)
                except Exception:
                    tmp = Heater(
                        id=heater,
                        classes="temperature",
                    )
                    
                    await self.mount(tmp)

                tmp.set_name(heater.replace('_', ' ').title())
                if 'target' in data[heater]:
                    tmp.set_set_temp(data[heater]['target'])
                if 'temperature' in data[heater]:
                    tmp.set_current_temp(data[heater]['temperature'])
                if 'power' in data[heater]:
                    tmp.set_power(data[heater]['power'])

                # set maximum temp for this heater
                if 'configfile' in data and 'settings' in data['configfile'] and heater in data['configfile']['settings'] and 'max_temp' in data['configfile']['settings'][heater]:
                    tmp.set_max_temp(data['configfile']['settings'][heater]['max_temp'])

        if 'heaters' in data and 'available_sensors' in data['heaters']:
            for sensor in data['heaters']['available_sensors']:
                if "temperature_fan" not in sensor:
                    continue
                sensor_id = sensor.replace("temperature_fan ", "temperature_fan")
                sensor_name = sensor.replace("temperature_fan ", "")
                try :
                    tmp = self.query_one('#'+sensor_id)
                except Exception:
                    tmp = TemperatureFan(
                        id=sensor_id,
                        classes="temperature",
                    )
                    
                    await self.mount(tmp)
                tmp.set_name(sensor_name.replace('_', ' ').title())
                if 'target' in data[sensor]:
                    tmp.set_set_temp(data[sensor]['target'])
                if 'temperature' in data[sensor]:
                    tmp.set_current_temp(data[sensor]['temperature'])
                if 'speed' in data[sensor]:
                    tmp.set_power(data[sensor]['speed'])
                if 'configfile' in data and 'settings' in data['configfile'] and sensor in data['configfile']['settings'] and 'max_temp' in data['configfile']['settings'][sensor]:
                    tmp.set_max_temp(data['configfile']['settings'][sensor]['max_temp'])
