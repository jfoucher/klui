from textual.app import ComposeResult
from textual.widgets import Label, LoadingIndicator
from textual.containers import Vertical, Horizontal, Grid, Container
from widgets.button import SmallButton
from textual.screen import ModalScreen
from rich.text import Text


class ConnectScreen(ModalScreen):
    """Screen with a dialog to quit."""
    def compose(self) -> ComposeResult:
        cancel = Text()
        cancel.append("C", style="bold green on white")
        cancel.append("ancel")
        restart = Text()
        restart.append("R", style="bold red on white")
        restart.append("estart")
        yield Grid(
            Label("Klippy reports shutdown\n\nShutdown due to webhooks request\n\nOnce the underlying issue is corrected, click [b]R[/]estart or press [b]R[/] to reset the firmware, reload the config, and restart the host software.\n\nPrinter is shutdown", id="question"),
            SmallButton(restart, id="restart"),
            SmallButton(cancel, id="close"),
            
            classes="dialog"
        )
    
    async def restart(self):
        await self.app.get_screen('main').message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": f"FIRMWARE_RESTART"
            },
        })
        self.query_one('#restart').remove()
        self.mount(LoadingIndicator(), after=self.query_one(Label))

    async def on_key(self, event):
        if event.key and(event.key == "C" or event.key == "c" or event.key == "escape"):
            self.app.pop_screen()
        elif event.key and(event.key == "R" or event.key == "r"):
            await self.restart()

    def remove_screen(self):
        try:
            self.query_one(LoadingIndicator).remove()
        except:
            pass
        try:
            self.query_one('#restart')
        except:
            self.mount(SmallButton("[bold red on white]R[/]estart", id="restart"), after=self.query_one(Label))
        self.app.pop_screen()
    
    async def on_small_button_pressed(self, event: SmallButton.Pressed) -> None:
        if event.id == "restart":
            await self.restart()
        else:
            self.app.pop_screen()
