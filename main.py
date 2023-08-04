from textual.app import App, ComposeResult
from textual import log
from textual.binding import Binding
from textual.widgets import Label, Input, Header, Footer, Button, Static, Placeholder
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical
import argparse
import asyncio
import json
import random
import websockets
from widgets.temp import Connected, Heater, CurrentTemp, SetTemp


class Printer():
    objects = {}
    sensors = {}
    heaters = {}
    connected = False

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
        yield Container(
            Horizontal(
                Connected(id="klippy_status", classes="header"),
                Button.error("Emergency stop", classes="header", id="emergency_stop")
            ),
            id="header",
        )
        with Container(id="container"):
            with Horizontal():
                yield Vertical (
                    id="temps"
                )
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


            


    async def handle_message(self, message):
        method = None
        if "id" in message:
            # this is a reply to one of our messages
            m = next(iter([x for x in self.messages if "id" in message and x["id"] == message["id"]]), None)
            
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

        elif method == "notify_status_update":
            data = message['params'][0]

            for heater_widget in self.query_one("#temps").query(Heater):
                if heater_widget.id in data:
                    if 'temperature' in data[heater_widget.id]:
                        heater_widget.set_current_temp(data[heater_widget.id]["temperature"])
                    if 'target' in data[heater_widget.id]:
                        heater_widget.set_set_temp(data[heater_widget.id]["target"])
                    if 'power' in data[heater_widget.id]:
                        heater_widget.set_power(data[heater_widget.id]['power'])
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
    

    

