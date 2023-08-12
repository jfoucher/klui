from textual.app import ComposeResult
from textual.widgets import MarkdownViewer, Label
from textual.widget import Widget
from textual.containers import Vertical, VerticalScroll, Container
from widgets.button import SmallButton
from widgets.axis import Axis
from widgets.footer import KluiFooter
from widgets.header import KluiHeader
from textual.screen import Screen
from screens.toolhelp import ToolhelpScreen

class ToolheadScreen(Screen):
    footer_buttons = [
        'Help',
        'Close',
        'Home',
        'Home all',
        'Set',
        'Pos',
        'Neg',
        'QGL',
        '',
        'STOP',
    ]
    """Screen with a dialog to show toolhead info, such as position, home buttons, etc."""
    def compose(self) -> ComposeResult:
        with Vertical(id="toolhead_screen"):
            yield KluiHeader(id="header")
            with Container(id='container'):
                yield Label("Toolhead", classes='title')
                for n in ["x", "y", "z"]:
                    yield Axis(id=f"axis_{n}", classes="axis")
            yield KluiFooter(id='footer', buttons=self.footer_buttons)

    def on_key(self, event):

        if event.key and event.key == "up":
            self.focus_previous()
        elif event.key and event.key == "down":
            self.focus_next()
        elif event.key and event.key == "f1":
            self.app.push_screen(ToolhelpScreen())
        else:
            self.query_one(KluiFooter).post_message(event)

    async def home_all(self):
        await self.app.get_screen('main').message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": "G28"
            },
        })

    async def home(self):
        ax = self.query_one('.axis:focus').id.replace('axis_', '')

        print(f"homing {ax.upper()} axis")
        script = f"G28 {ax.upper()}"
        # print('QGL')
        # script = f"QUAD_GANTRY_LEVEL"
        # QUAD_GANTRY_LEVEL

        await self.app.get_screen('main').message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": script
            },
        })

    async def update(self, data):
        try:
            await self.query_one(KluiHeader).update(data)
        except:
            pass
        if 'toolhead' in data:
            if 'position' in data['toolhead']:
                for i, axis in enumerate(["x", "y", "z"]):
                    try:
                        a = self.query_one(f"#axis_{axis}").query_one('.axis_pos')
                        a.pos = data['toolhead']['position'][i]
                    except:
                        pass
            # if 'homed_axes' in data['toolhead']:
            #     hm = data['toolhead']['homed_axes']
            #     self.printer.homed_axes = hm
            #     # Change button colors depending on homed axes
            #     qgl_btn = None
            #     try: 
            #         qgl_btn = self.query_one('#qgl_button')
            #         qgl_btn.disabled = True
            #     except:
            #         print('no QGL button')
            #     if "x" in hm and "y" in hm:
            #         self.query_one(f"#home_z_button").disabled = False
            #     else:
            #         # cannot home Z if X and Y are not homed first
            #         self.query_one(f"#home_z_button").disabled = True
            #     if "x" in hm and "y" in hm and "z" in hm:
            #         self.query_one('#home_all_button').variant = "success"
            #         if qgl_btn:
            #             qgl_btn.disabled = False
            #     else: 
            #         self.query_one('#home_all_button').variant = "warning"
            #     for axis in ["x", "y", "z"]:
            #         if axis in hm:
            #             self.query_one(f"#home_{axis}_button").variant = "success"
            #         else: 
            #             self.query_one(f"#home_{axis}_button").variant = "warning"


