from textual.app import ComposeResult
from textual.widgets import Label, Input, ProgressBar
from textual.widget import Widget
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.validation import Function, Number, ValidationResult, Validator
from textual.message import Message


class CurrentTemp(Label):
    """Show current temperature"""

    current = reactive("0")

    def render(self) -> str:
        return f"Current {self.current}"

    async def on_mount(self):
        self.styles.width = 40

class SetTemp(Label):
    """Show set temperature"""

    temp = reactive("0")

    def render(self) -> str:
        return f"Set to {self.temp}"

    async def on_mount(self):
        self.styles.width = 40

class Powerbar(Label):
    """Show set temperature"""
    
    def render(self) -> str:
        return "━"*300

class TempName(Label):
    """Show current temperature name"""

    name = reactive("Temp")

    def render(self) -> str:
        return f"{self.name}"

    async def on_mount(self):
        self.styles.width = 40

class Connected(Label):
    """Show connection status"""

    connected = reactive("✕")
    

    # def compose(self) -> ComposeResult:
    #     yield(Label(self.connected))

    def render(self) -> str:
        return f"{self.connected}"

    async def on_mount(self) -> None:
        self.styles.background = "red"




class Heater(Widget):
    """Show a temperature sensor"""
    set_point = reactive(0)
    max = reactive(100)

    class ChangeSetTemp(Message):
        """Sent when the set temperature changes."""

        def __init__(self, temp: int, id: str) -> None:
            super().__init__()
            self.temp = temp
            self.id = id

    def compose(self) -> ComposeResult:
        yield Vertical(
            Horizontal(
                Vertical(
                    TempName(),
                    SetTemp(),
                    CurrentTemp(),
                    
                    classes="temp_label",
                ),
                Input(
                    placeholder=str(self.set_point),
                    validators=[
                        Number(minimum=0, maximum=self.max),
                    ],
                    classes="temp_input",
                )
            ),
            Powerbar()
        )

    def set_name(self, name):
        self.query_one(TempName).name = name

    def set_current_temp(self, current):
        self.query_one(CurrentTemp).current = current

    def set_set_temp(self, temp):
        self.query_one(SetTemp).temp = temp

    def set_power(self, power):
        print('')
        self.query_one(Powerbar).styles.width = str((power*100))+ '%'

    async def on_mount(self) -> None:
        self.styles.background = "blue"


    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self.set_set_temp(event.value)
        self.post_message(Heater.ChangeSetTemp(temp=event.value, id=self.id))
        # await app.message_queue.put({
        #     "method":"printer.gcode.script",
        #     "params":{
        #         "script": f"SET_HEATER_TEMPERATURE HEATER={self.id} TARGET={event.value}"
        #     },
        # })

