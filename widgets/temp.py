from textual.app import ComposeResult
from textual.widgets import Label, Input
from textual.widget import Widget
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.validation import Number
from textual.message import Message


class CurrentTemp(Label):
    """Show current temperature"""

    current = reactive(100.00)

    def render(self) -> str:
        form = "{:10.2f}".format(self.current)
        return f"{form}°C "

class SetTemp(Label):
    """Show set temperature"""

    temp = reactive(1000.0)

    def render(self) -> str:
        form = "{:3.0f}°C".format(self.temp)
        return f"Target: {form}"

class Powerbar(Label):
    """Show set temperature"""
    power = reactive(0.0)
    def render(self) -> str:

        p = self.power*45/100
        a = "" # power_item*int(self.power*45/100)
        fill = ""
        for _ in range(45-int(p)):
            fill = fill + " "
        for i in range(int(p)):
            color = 'red1'
            if i < 45/3:
                color = 'green1'
            elif i < 2*45/3:
                color = 'orange1'
            a = a + f"[bold {color}]|[/]"

        pow = a + fill
        return "[bold aquamarine3][[/]" + pow + "[bold aquamarine3]][/]"

    def on_mount(self):
        self.styles.width = 47

class TempName(Label):
    """Show current temperature name"""

    name = reactive("Temperature probe")

    def render(self) -> str:
        return f"{self.name}"

    def on_mount(self):
        self.styles.width = 10






class Heater(Widget):
    """Show a temperature sensor"""
    set_point = reactive(0)
    class ChangeSetTemp(Message):
        """Sent when the set temperature changes."""

        def __init__(self, temp: int, id: str) -> None:
            super().__init__()
            self.temp = temp
            self.id = id

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Horizontal(
                TempName(),
                CurrentTemp(),
                SetTemp(),
                Input(
                    placeholder=str(self.set_point),
                    validators=[
                        Number(minimum=0, maximum=60),
                    ],
                    classes="temp_input",
                ),
                
                
            )
            yield Horizontal(Powerbar())

    def set_name(self, name):
        self.query_one(TempName).name = name

    def set_current_temp(self, current):
        self.query_one(CurrentTemp).current = current

    def set_set_temp(self, temp):
        self.query_one(Input).placeholder = str(temp)
        self.query_one(SetTemp).temp = temp
        self.query_one(SetTemp).refresh(layout=True)

    def set_power(self, power):
        self.query_one(Powerbar).power = round(power*100)

    def set_max_temp(self, max):
        self.query_one(Input).validators = [Number(minimum=0, maximum=max)]


    def update(self, data):
        heater = self.id
        if heater not in data:
            return
        if 'temperature' in data[heater]:
            self.set_current_temp(data[heater]["temperature"])
        if 'target' in data[heater]:
            self.set_set_temp(data[heater]["target"])
        if 'power' in data[heater]:
            self.set_power(data[heater]['power'])
        if 'configfile' in data and 'settings' in data['configfile'] and heater in data['configfile']['settings'] and 'max_temp' in data['configfile']['settings'][heater]:
            self.set_max_temp(data['configfile']['settings'][heater]['max_temp'])
        
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Validate input temperature
        self.app.query_one('#footer').focus()
        if len(event.validation_result.failures) == 0:
            self.set_set_temp(float(event.value))
            self.post_message(Heater.ChangeSetTemp(temp=float(event.value), id=self.id))
        else:
            print(event.validation_result.failures[0].description)

class TemperatureFan(Widget):
    """Show a temperature sensor"""
    set_point = reactive(0)
    class ChangeSetTemp(Message):
        """Sent when the set temperature changes."""

        def __init__(self, temp: int, id: str) -> None:
            super().__init__()
            self.temp = temp
            self.id = id

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Horizontal(
                TempName(),
                CurrentTemp(),
                SetTemp(),
                Input(
                    placeholder=str(self.set_point),
                    validators=[
                        Number(minimum=0, maximum=60),
                    ],
                    classes="temp_input",
                ),
            )
            yield Horizontal(Powerbar())

    def set_name(self, name):
        self.query_one(TempName).name = name

    def set_current_temp(self, current):
        self.query_one(CurrentTemp).current = current

    def set_set_temp(self, temp):
        self.query_one(Input).placeholder = str(temp)
        self.query_one(SetTemp).temp = temp
        self.query_one(SetTemp).refresh(layout=True)

    def set_power(self, power):
        self.query_one(Powerbar).power = round(power*100)

    def set_max_temp(self, max):
        self.query_one(Input).validators = [Number(minimum=0, maximum=max)]

    def update(self, data):
        heater = self.id.replace("temperature_fan", "temperature_fan ")
        if heater not in data:
            return
        if 'temperature' in data[heater]:
            self.set_current_temp(data[heater]["temperature"])
        if 'target' in data[heater]:
            self.set_set_temp(data[heater]["target"])
        if 'speed' in data[heater]:
            self.set_power(data[heater]['speed'])
        if 'configfile' in data and 'settings' in data['configfile'] and heater in data['configfile']['settings'] and 'max_temp' in data['configfile']['settings'][heater]:
            self.set_max_temp(data['configfile']['settings'][heater]['max_temp'])
        

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Validate input temperature
        self.app.query_one('#footer').focus()
        if len(event.validation_result.failures) == 0:
            self.set_set_temp(float(event.value))
            self.post_message(TemperatureFan.ChangeSetTemp(temp=float(event.value), id=self.id.replace("temperature_fan", "")))
        else:
            print(event.validation_result.failures[0].description)

