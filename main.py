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
from widgets.temperature import KluiTemperature
from textual.screen import ModalScreen, Screen
from rich.segment import Segment
from textual.strip import Strip
from rich.style import Style
from rich.text import Text

class Printer():
    objects = {}
    sensors = {}
    heaters = {}
    connected = False
    homed_axes = ""


class KluiScreen(Screen):
    status = {}
    messages = []
    url = ""
    connected = reactive(False)
    printer = Printer()
    message_queue = asyncio.Queue()


    def compose(self) -> ComposeResult:
        with Vertical():
            yield KluiHeader(id="header")
            yield KluiTemperature(id='temperature')
            yield KluiFooter(id='footer')


    async def on_heater_change_set_temp(self, event: Heater.ChangeSetTemp):
        script = f"SET_HEATER_TEMPERATURE HEATER={event.id} TARGET={event.temp}"
        await self.message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": script
            },
        })
        #self.query_one(Console).add_line(script)

    async def on_axis_change_position(self, event: Axis.ChangePosition):
        axis = event.id.replace('axis_', '')
        print(axis)
        speed = "6000"
        if axis == "z":
            speed = "1000"
        script = f"G1 {axis.capitalize()}{event.pos} F{speed}"
        await self.message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": script
            },
        })
        #self.query_one(Console).add_line(script)

    async def on_console_send_gcode(self, event: Console.SendGcode):
        await self.message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": f"{event.gcode}"
            },
        })

    async def on_temperature_fan_change_set_temp(self, event: TemperatureFan.ChangeSetTemp):
        print(f"SET_TEMPERATURE_FAN_TARGET TEMPERATURE_FAN={event.id} TARGET={event.temp}")
        # SET_TEMPERATURE_FAN_TARGET TEMPERATURE_FAN=pi_temp TARGET=50
        script = f"SET_TEMPERATURE_FAN_TARGET TEMPERATURE_FAN={event.id} TARGET={event.temp}"
        #self.query_one(Console).add_line(script)
        await self.message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": script
            },
        })

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        # motors off : M84
        button_id = event.button.id
        if button_id == 'home_all_button':
            print('home All')
            script = f"G28"
        elif button_id == 'home_x_button':
            print('home X')
            script = f"G28 X"
        elif button_id == 'home_y_button':
            print('home Y')
            script = f"G28 Y"
        elif button_id == 'home_z_button':
            print('home Z')
            script = f"G28 Z"
        elif button_id == 'qgl_button':
            print('QGL')
            script = f"QUAD_GANTRY_LEVEL"
            # QUAD_GANTRY_LEVEL

        await self.message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": script
            },
        })

        #self.query_one(Console).add_line(script)


    async def ws_message_handler(self):
        # your infinite loop here, for example:
        async for websocket in websockets.connect("ws://"+self.url+'/websocket'):
            try:
                print("connection OK")
                while True:
                    try:
                        res = await asyncio.wait_for(websocket.recv(), timeout=5)
                    except asyncio.exceptions.TimeoutError:
                        print("receive timeout")
                        if self.message_queue.empty():
                            await self.identify()
                            await self.update_status()
                            await self.get_printer_objects()

                    message = json.loads(res)

                    await self.handle_message(message)

                    if not self.message_queue.empty():
                        msg = await self.message_queue.get()
                        id = random.randbytes(32).hex()
                        msg["id"] = id

                        event = {
                            "jsonrpc":"2.0",
                            "method": msg['method'],
                            "params": msg['params'],
                            "id": msg["id"],
                        }
                        self.messages.append(msg)
                        await websocket.send(json.dumps(event))
                    await asyncio.sleep(0)
            except websockets.ConnectionClosed:
                print("Connection closed")
                # prepare messages to send for when we come back online
                await self.identify()
                await self.update_status()
                await self.get_printer_objects()
                continue


            
    def update_home_buttons(self, data):
        if 'quad_gantry_level' in data:
            if data['quad_gantry_level']['applied']:
                self.query_one('#qgl_button').variant = "success"
            else:
                self.query_one('#qgl_button').variant = "warning"
        if 'toolhead' in data:
            if 'position' in data['toolhead']:
                for i, axis in enumerate(["x", "y", "z"]):
                    self.query_one(f"#axis_{axis}").query_one(CurrentPos).pos = str(round(data['toolhead']['position'][i], 2))

            if 'homed_axes' in data['toolhead']:
                hm = data['toolhead']['homed_axes']
                self.printer.homed_axes = hm
                # Change button colors depending on homed axes
                qgl_btn = None
                try: 
                    qgl_btn = self.query_one('#qgl_button')
                    qgl_btn.disabled = True
                except:
                    print('no QGL button')
                if "x" in hm and "y" in hm:
                    self.query_one(f"#home_z_button").disabled = False
                else:
                    # cannot home Z if X and Y are not homed first
                    self.query_one(f"#home_z_button").disabled = True
                if "x" in hm and "y" in hm and "z" in hm:
                    self.query_one('#home_all_button').variant = "success"
                    if qgl_btn:
                        qgl_btn.disabled = False
                else: 
                    self.query_one('#home_all_button').variant = "warning"
                for axis in ["x", "y", "z"]:
                    if axis in hm:
                        self.query_one(f"#home_{axis}_button").variant = "success"
                    else: 
                        self.query_one(f"#home_{axis}_button").variant = "warning"


    async def handle_message(self, message):
        method = None
        if "id" in message:
            # this is a reply to one of our messages
            m = next(iter([x for x in self.messages if "id" in message and x["id"] == message["id"]]), None)
            
            if m != None:
                self.messages = list(filter(lambda m: "id" in message and m["id"] != message["id"], self.messages))
                if "method" in m:
                    method = m["method"]

        if "method" in message:
            # This is a notificaiton from the printer
            method = message["method"]

        if method == "server.info":
            self.status = message['result']
            if self.status and self.status['klippy_connected'] == True  and self.status['klippy_state'] == "ready":
                print("connected")
                self.query_one(Connected).connected = "✔"
                self.query_one(Connected).styles.background = "green"
                self.printer.connected = True
        elif method == "printer.emergency_stop" or method == "notify_klippy_shutdown":
            self.query_one(Connected).connected = "✕"
            self.query_one(Connected).styles.background = "red"
            self.printer.connected = False
        elif method == "notify_klippy_ready":
            self.query_one(Connected).connected = "✔"
            self.query_one(Connected).styles.background = "green"
            self.printer.connected = True
        elif method == "printer.objects.list":
            self.printer.objects = dict.fromkeys(message['result']['objects'], None)
            await self.get_printer_objects_details()
        elif method == "notify_gcode_response":
            print('Got gcode response')
            # for line in message['params']:
            #     self.query_one('#right').add_line(line)
            print(message['params'])
        elif method == "printer.objects.query":
            await self.printer_subscribe()

            data = message['result']['status']
            await self.query_one('#header').update(data)
            await self.query_one('#temperature').update(data)

            # self.update_home_buttons(data)
            
        elif method == "notify_status_update":
            data = message['params'][0]
            await self.query_one('#header').update(data)
            await self.query_one('#temperature').update(data)
            # temps = self.query_one("#temps")
            # self.update_home_buttons(data)
            # for heater_widget in temps.query(Heater):
            #     heater_widget.update(data)
            # for temp_fan in temps.query(TemperatureFan):
            #     temp_fan.update(data)

        elif method == "server.sensors.list":
            print(message)
        elif method == "server.temperature_store":
            print("")
        # else:
        #     print("unhandled")



    async def on_mount(self) -> None:
        self.url = args.url

        asyncio.Task(self.ws_message_handler())

        await self.identify()
        await self.update_status()
        await self.get_printer_objects()
        # await self.sensors_list()
        # await self.temp_store()
        
        
    async def identify(self):
        await self.message_queue.put({
            "method": "server.connection.identify",
            "params":{
                "client_name": "klui",
                "version":	"0.0.1",
                "type":	"web",
                "url":	"https://github.com/jfoucher"
            },
        })


    async def update_status(self):
        await self.message_queue.put({
            "method":"server.info",
            "params":{},
        })

    async def temp_store(self):
        await self.message_queue.put({
            "method":"server.temperature_store",
            "params":{},
        })
            
    async def sensors_list(self):
        await self.message_queue.put({
            "method":"server.sensors.list",
            "params":{},
        })
            
    async def em_stop(self):
        await self.message_queue.put({
            "method":"printer.emergency_stop",
            "params":{},
        })
    
            
    async def get_printer_objects(self):
        await self.message_queue.put({
            "method":"printer.objects.list",
            "params":{},
        })
    async def get_printer_objects_details(self):
        await self.message_queue.put({
            "method":"printer.objects.query",
            "params":{
                "objects": self.printer.objects
            },
        })
    async def printer_subscribe(self):
        await self.message_queue.put({
            "method":"printer.objects.subscribe",
            "params":{
                "objects": self.printer.objects
            },
        })

class Klui(App):
    SCREENS = {"main": KluiScreen()}

    CSS_PATH = "klui.css"

    BINDINGS = [
        Binding(key="q", action="request_quit", description="Quit"),
        Binding(
            key="h",
            action="help",
            description="Help",
            key_display="H",
        ),
        Binding(
            key="t",
            action="toolhead",
            description="Toolhead",
            key_display="T",
        ),
        Binding(
            key="p",
            action="print",
            description="Print",
            key_display="P",
        ),
        Binding(
            key="E",
            action="extruder",
            description="Extruder",
            key_display="E",
        ),
        Binding(
            key="M",
            action="misc",
            description="Misc",
            key_display="M",
        ),

        Binding(
            key="c",
            action="console",
            description="Console",
            key_display="C",
        ),


        Binding(
            key="s",
            action="stop",
            description="STOP",
            key_display="S",
        )
    ]

    def on_mount(self):
        self.push_screen("main")

    async def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.push_screen(QuitScreen())

    async def action_help(self):
        self.push_screen(HelpScreen())

    async def action_toolhead(self):
        print('toolhead')

    async def action_misc(self):
        print('misc')

    async def action_print(self):
        print('print')
    
    async def action_stop(self):
        s = self.get_screen('main')
        await s.em_stop()
        await s.update_status()

if __name__ == "__main__":
    parser = argparse.ArgumentParser("klui")
    parser.add_argument("url", help="url of the moonraker server")

    args = parser.parse_args()
    
    app = Klui()
    app.run()
    

    

