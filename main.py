from textual.app import App, ComposeResult
from textual import log
from textual.binding import Binding
from textual.widgets import Label, Input, Header, Footer, Button, Static, Placeholder
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
import argparse
import asyncio
import json
import random
import websockets
from widgets.temp import Connected, Heater, CurrentTemp, SetTemp, TemperatureFan


class Printer():
    objects = {}
    sensors = {}
    heaters = {}
    connected = False
    homed_axes = ""

class HelloWorld(App):
    status = {}
    messages = []
    url = ""
    printer = Printer()
    message_queue = asyncio.Queue()
    CSS_PATH = "klui.css"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        )
    ]

    def compose(self) -> ComposeResult:
        with Container(id="header"):
            with Horizontal():
                yield Connected(id="klippy_status", classes="header")
                yield Button.error("Emergency stop", classes="header", id="emergency_stop")
                

        with Container(id="container"):
            with Horizontal():
                with VerticalScroll(id="temps"):
                    with Horizontal(id="home_buttons"):
                        yield Button("Home All", classes="home_button unhomed", id="home_button", variant="warning")
                        yield Button("X", classes="home_button unhomed", id="home_x_button", variant="warning")
                        yield Button("Y", classes="home_button unhomed", id="home_y_button", variant="warning")
                        yield Button("Z", classes="home_button unhomed", id="home_Z_button", variant="warning")
                yield Placeholder(
                    id="right"
                )
        
        yield Footer()

    async def on_heater_change_set_temp(self, event: Heater.ChangeSetTemp):
        await app.message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": f"SET_HEATER_TEMPERATURE HEATER={event.id} TARGET={event.temp}"
            },
        })

    async def on_temperature_fan_change_set_temp(self, event: TemperatureFan.ChangeSetTemp):
        print(f"SET_TEMPERATURE_FAN_TARGET TEMPERATURE_FAN={event.id} TARGET={event.temp}")
        # SET_TEMPERATURE_FAN_TARGET TEMPERATURE_FAN=pi_temp TARGET=50
        await app.message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": f"SET_TEMPERATURE_FAN_TARGET TEMPERATURE_FAN={event.id} TARGET={event.temp}"
            },
        })


    async def ws_message_handler(self):
        # your infinite loop here, for example:
        async for websocket in websockets.connect("ws://"+self.url+'/websocket'):
            try:
                print("connection OK")
                while True:
                    try:
                        res = await asyncio.wait_for(websocket.recv(), timeout=2)
                    except asyncio.exceptions.TimeoutError:
                        print("receive timeout")
                        self.query_one(Connected).connected = "✔"
                        self.query_one(Connected).styles.background = "grey"
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
        if 'toolhead' in data and 'homed_axes' in data['toolhead']:
            self.printer.homed_axes = data['toolhead']['homed_axes']
            # TODO changed button colors depending on homed axes
            
            if "x" in data['toolhead']['homed_axes']:
                self.query_one('#home_x_button').variant = "success"
            if "y" in data['toolhead']['homed_axes']:
                self.query_one('#home_y_button').variant = "success"
            if "z" in data['toolhead']['homed_axes']:
                self.query_one('#home_z_button').variant = "success"

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
        elif method == "printer.emergency_stop":
            # remove emergency stop button and show firmware restart
            self.query_one(Button).remove()
        elif method == "notify_klippy_shutdown":
            self.query_one(Connected).connected = "✕"
            self.query_one(Connected).styles.background = "red"
            self.printer.connected = False
            self.query_one(Button).remove()
        elif method == "notify_klippy_ready":
            self.query_one(Connected).connected = "✔"
            self.query_one(Connected).styles.background = "green"
            self.printer.connected = True
        elif method == "printer.objects.list":
            self.printer.objects = dict.fromkeys(message['result']['objects'], None)
            await self.get_printer_objects_details()
            
        elif method == "printer.objects.query":
            await self.printer_subscribe()
            with open('data.json', 'w') as f:
                json.dump(message['result']['status'], f)
            data = message['result']['status']

            if 'quad_gantry_level' in data:
                qgl_btn = Button("QGL", classes="home_button unhomed", id="qgl_button", variant="warning")
                await self.query_one('#home_buttons').mount(qgl_btn)
            
            temps = self.query_one('#temps')
            for heater in data['heaters']['available_heaters']:
                try :
                    tmp = temps.query_one('#'+heater)
                except Exception:
                    tmp = Heater(
                        id=heater,
                        classes="temperature",
                    )
                    
                    await temps.mount(tmp)

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


            for sensor in data['heaters']['available_sensors']:
                if "temperature_fan" not in sensor:
                    continue
                sensor_id = sensor.replace("temperature_fan ", "temperature_fan")
                sensor_name = sensor.replace("temperature_fan ", "")
                try :
                    tmp = temps.query_one('#'+sensor_id)
                except Exception:
                    tmp = TemperatureFan(
                        id=sensor_id,
                        classes="temperature",
                    )
                    
                    await temps.mount(tmp)
                tmp.set_name(sensor_name.replace('_', ' ').title())
                if 'target' in data[sensor]:
                    tmp.set_set_temp(data[sensor]['target'])
                if 'temperature' in data[sensor]:
                    tmp.set_current_temp(data[sensor]['temperature'])
                if 'speed' in data[sensor]:
                    tmp.set_power(data[sensor]['speed'])
                if 'configfile' in data and 'settings' in data['configfile'] and sensor in data['configfile']['settings'] and 'max_temp' in data['configfile']['settings'][sensor]:
                    tmp.set_max_temp(data['configfile']['settings'][sensor]['max_temp'])

        elif method == "notify_status_update":
            data = message['params'][0]
            temps = self.query_one("#temps")
            self.update_home_buttons(data)
            for heater_widget in temps.query(Heater):
                heater_widget.update(data)
            for temp_fan in temps.query(TemperatureFan):
                temp_fan.update(data)

        elif method == "server.sensors.list":
            print(message)
        elif method == "server.temperature_store":
            print("")
        # else:
        #     print("unhandled")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        if button_id == "emergency_stop":
            await self.em_stop()
            await self.update_status()

    async def on_mount(self) -> None:
        self.url = args.url
        self.screen.styles.background = "darkblue"
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser("klui")
    parser.add_argument("url", help="url of the moonraker server")
    args = parser.parse_args()
    
    app = HelloWorld()
    app.run()
    

    

