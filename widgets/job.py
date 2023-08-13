from textual.app import ComposeResult
from textual.widgets import Label
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Vertical, Horizontal
from widgets.header import ReactiveLabel
import datetime
from widgets.temp import Heater, TemperatureFan

class Job(Label):
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical():
                yield ReactiveLabel(self.renderable, id='name')
                yield ReactiveLabel("Print time: 00:00:00 Fil length: 1000mm, 100g", id="time")
            yield ReactiveLabel("✕", id='status')

    def set_filename(self, name):
        self.query_one('#name').label = '[b]' + name + '[/]'

    def set_meta(self, time, fil_length, fil_weight):
        t = str(datetime.timedelta(seconds=round(time)))
        self.query_one('#time').label = f"[dark_turquoise]Print time:[/] {t} [dark_orange3]Fil length:[/] {round(fil_length)}mm, {round(fil_weight)}g"
            