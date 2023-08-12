from textual.app import ComposeResult
from textual.widgets import Label, Static
from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Horizontal
from rich.console import RenderableType

class Connected(Label):
    """Show connection status"""

    connected = reactive("✕")
    

    # def compose(self) -> ComposeResult:
    #     yield(Label(self.connected))

    def render(self) -> str:
        return f"{self.connected}"

    async def on_mount(self) -> None:
        self.styles.background = "grey"

class ReactiveLabel(Label):
    label = reactive("")
    def __init__(self, renderable: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled)
        self.label = renderable

    def render(self) -> str:
        return f"{self.label}"
class KluiHeader(Widget):
    def compose(self) -> ComposeResult:
        with Container():
            with Horizontal():
                yield Connected(id="klippy_status", classes="header")
                yield ReactiveLabel("Unkown", id="status")
                yield ReactiveLabel("", id="file")
                yield ReactiveLabel("0%", id="completion")
                yield ReactiveLabel("Home", id="homed")
                yield ReactiveLabel("Step", id="motors")

                yield ReactiveLabel("Fil", id="filament")
                yield ReactiveLabel("Fan", id="fan")
                yield Static()
                yield ReactiveLabel("Load", id="sysload")
    
    async def update(self, data):
        if 'quad_gantry_level' in data:
            try :
                qgl_btn = self.query_one('#qgl_button')
            except Exception:
                variant = "warning"
                if data['quad_gantry_level']['applied']:
                    variant = "success"
                # qgl_btn = Button("QGL", classes="home_button", id="qgl_button", variant=variant, disabled=True)
                # await self.query_one('#home_buttons').mount(qgl_btn)

        if 'fan' in data and 'speed' in data['fan']:
            if data['fan']['speed'] < 0.3:
                self.query_one('#fan').styles.background = "green"
            elif data['fan']['speed'] < 0.6:
                self.query_one('#fan').styles.background = "orange"
            else:
                self.query_one('#fan').styles.background = "red"

            self.query_one('#fan').label = "Fan "+str(round(data['fan']['speed'] * 100))

        if 'idle_timeout' in data and 'state' in data['idle_timeout']:
            state = data['idle_timeout']['state']
            if state == 'Printing':
                self.query_one('#file').styles.display = "block"
                self.query_one('#completion').styles.display = "block"
                self.query_one('#status').styles.background = 'green'
            else:
                self.query_one('#file').styles.display = "none"
                self.query_one('#completion').styles.display = "none"
                if state == 'Idle':
                    self.query_one('#status').styles.background = 'darkgray'
                else:
                    # Ready state
                    self.query_one('#status').styles.background = 'darkcyan'
            self.query_one('#status').label = state
        if 'toolhead' in data:
            if 'homed_axes' in data['toolhead']:
                homed = data['toolhead']['homed_axes']
                home = self.query_one('#homed')

                if len(homed) < 1:
                    home.styles.background = "red"
                    home.styles.color = "white"
                elif len(homed) < 2:
                    home.styles.background = "orange"
                    home.styles.color = "black"
                elif len(homed) < 3:
                    home.styles.background = "yellow"
                    home.styles.color = "black"
                else:
                    home.styles.background = "green"
                    home.styles.color = "black"
        if 'stepper_enable' in data:
            def steppers_enabled(ls):
                for s in ls:
                    if s:
                        return True
                return False

            s = list(data['stepper_enable']['steppers'].values())
            motors = self.query_one('#motors')
            if steppers_enabled(s):
                motors.styles.background = 'darkgreen'
            else:
                motors.styles.background = 'darkred'

        for k in data.keys():
            if 'filament_switch_sensor' in k and 'filament_detected' in data[k]:
                if data[k]['filament_detected']:
                    self.query_one('#filament').styles.background = 'green'
                else: 
                    self.query_one('#filament').styles.background = 'red'


                break
        if 'system_stats' in data and 'sysload' in data['system_stats']:
            l = data['system_stats']['sysload']
            self.query_one('#sysload').label = l
            if l < 1.0:
                self.query_one('#sysload').styles.background = "green"
            elif l < 2.0:
                self.query_one('#sysload').styles.background = "orange"
            else:
                self.query_one('#sysload').styles.background = "red"