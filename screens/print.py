from textual.app import ComposeResult
from textual.widgets import Label, LoadingIndicator
from textual.containers import Vertical, Horizontal, Grid, Container
from widgets.button import SmallButton
from textual.screen import ModalScreen
from rich.text import Text
import datetime


class PrintScreen(ModalScreen):
    """Screen with a dialog to print."""
    job = ""
    def __init__(self, job: dict, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.job = job
        print(job)

    def compose(self) -> ComposeResult:
        t = self.job['metadata']['estimated_time']
        hours, remainder = divmod(t, 60*60)
        minutes, seconds = divmod(remainder, 60)
        time = f"{round(minutes)}m{round(seconds)}s"
        if hours > 0:
            time = f"{round(hours)}h" + time

        yield Grid(
            Label(f"Please confirm to start a print of [bold dark_orange3]{self.job['filename']}[/]\nEstimated print time is {time} with a filament use of {self.job['metadata']['filament_weight_total']}g", id="question"),
            SmallButton('[bold red on white]P[/]rint', id="print"),
            SmallButton('[bold green on white]C[/]ancel', id="close"),
            id="print_dialog",
            classes="dialog"
        )
    
    async def print(self):
        self.query_one('#print').remove()
        await self.mount(LoadingIndicator(), after=self.query_one(Label))
        await self.app.get_screen('main').message_queue.put({
            "method":"printer.print.start",
            "params":{
                "filename": self.job['filename']
            },
        })
        self.app.pop_screen()
        

    async def on_key(self, event):
        if event.key and(event.key == "C" or event.key == "c" or event.key == "escape"):
            self.app.pop_screen()
        elif event.key and(event.key == "P" or event.key == "p"):
            await self.print()

    async def on_small_button_pressed(self, event: SmallButton.Pressed) -> None:
        if event.id == "print":
            await self.print()
        else:
            self.app.pop_screen()