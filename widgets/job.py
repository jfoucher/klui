from textual.app import ComposeResult
from textual.widgets import Label
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Vertical, Horizontal
from widgets.header import ReactiveLabel
import time
from widgets.temp import Heater, TemperatureFan

class Job(Label):
    last_click_time = time.time()
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical():
                yield ReactiveLabel(self.renderable, id='name')
                yield ReactiveLabel("Print time: 00:00:00 Fil length: 1000mm, 100g", id="time")
            yield ReactiveLabel("✕", id='status')

    def set_filename(self, name):
        self.query_one('#name').label = name

    def set_meta(self, t, fil_length, fil_weight):
        hours, remainder = divmod(t, 60*60)
        minutes, seconds = divmod(remainder, 60)
        time = f"{round(minutes)}m{round(seconds)}s"
        if hours > 0:
            time = f"{round(hours)}h" + time
        self.query_one('#time').label = f"[dark_turquoise]Print time:[/] {time} [dark_orange3]Fil length:[/] {round(fil_length)}mm, {round(fil_weight)}g"
            
    def on_click(self, event):
        now = time.time()
        if now - self.last_click_time < 0.5:
            # double click
            self.parent.parent.print()
        else:
            self.parent.parent.select_job(self.id)
        self.last_click_time = time.time()