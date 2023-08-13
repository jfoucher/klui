from textual.app import ComposeResult
from textual.widgets import MarkdownViewer, Label, Input, Static
from textual.widget import Widget
from textual.containers import Vertical, VerticalScroll, Container, Horizontal
from widgets.button import SmallButton
from widgets.axis import Axis
from widgets.footer import KluiFooter
from widgets.header import KluiHeader
from textual.screen import Screen
from screens.toolhelp import ToolhelpScreen
from widgets.header import ReactiveLabel
from textual.validation import Number
from textual.reactive import reactive
from screens.error import ErrorScreen

class ToolheadScreen(Screen):
    selected_axis = reactive(0)
    footer_buttons = [
        'Help',
        'Home',
        'Close',
        'All',
        'Set',
        'Move',
        'QGL',
        '',
        '',
        'STOP',
    ]
    """Screen with a dialog to show toolhead info, such as position, home buttons, etc."""
    def compose(self) -> ComposeResult:
        # TODO, control part fan with M106 S0 to M106 S255
        with Vertical(id="toolhead_screen"):
            yield KluiHeader(id="header")
            with Vertical(id='container'):
                yield Label("Toolhead", classes='title')
                for n in ["x", "y", "z"]:
                    yield Axis(id=f"axis_{n}", classes="axis")
                with Horizontal(classes='offset'):
                    yield ReactiveLabel("Z offset: 0.000", id='zoffset')
                    yield Input(
                        placeholder="0.00",
                        validators=[
                            Number(minimum=0, maximum=60),
                        ],
                        classes='axis_input',
                    )
                    yield ReactiveLabel("Fan:   0%", id='part_fan')
                    yield Input(
                        placeholder="0",
                        validators=[
                            Number(minimum=0, maximum=60),
                        ],
                        classes='axis_input',
                        id='part_fan_input'
                    )
                    yield Static("%")
            yield KluiFooter(id='footer', buttons=self.footer_buttons)

    def on_mount(self):
        self.query_one("#axis_x").classes = 'axis selected'

    def on_input_changed(self, event: Input.Changed):
        print(event)

    async def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == 'part_fan_input':
            await self.app.get_screen('main').message_queue.put({
                "method":"printer.gcode.script",
                "params":{
                    "script": f"M106 S{round(float(event.value) * 255 / 100)}"
                },
            })
        

    def on_key(self, event):
        if event.key and event.key == "up":
            self.selected_axis = (self.selected_axis - 1) % 3
            for i, ax in enumerate(self.query(Axis)):
                if self.selected_axis == i:
                    ax.classes = 'axis selected'
                else:
                    ax.classes = 'axis unselected'
                ax.refresh()
        elif event.key and event.key == "down":
            self.selected_axis = (self.selected_axis + 1) % 3
            for i, ax in enumerate(self.query(Axis)):
                if self.selected_axis == i:
                    ax.classes = 'axis selected'
                else:
                    ax.classes = 'axis unselected'
                ax.refresh()
        elif event.key and event.key == "f1":
            self.app.push_screen(ToolhelpScreen())
        else:
            self.app.post_message(event)


    async def home_all(self):
        await self.app.get_screen('main').message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": "G28"
            },
        })

    async def home(self):
        ax = self.query_one('.axis.selected').id.replace('axis_', '')

        print(f"homing {ax.upper()} axis")
        # print('QGL')
        # script = f"QUAD_GANTRY_LEVEL"
        # QUAD_GANTRY_LEVEL

        await self.app.get_screen('main').message_queue.put({
            "method":"printer.gcode.script",
            "params":{
                "script": f"G28 {ax.upper()}"
            },
        })
    async def qgl(self):
        data = self.app.get_screen('main').printer.data
        if 'toolhead' not in data or 'homed_axes' not in data['toolhead'] or data['toolhead']['homed_axes'] != 'xyz':
            self.app.push_screen(ErrorScreen(text="You must home all axes before doing a quad gantry leveling"))
        else:
            await self.app.get_screen('main').message_queue.put({
                "method":"printer.gcode.script",
                "params":{
                    "script": "QUAD_GANTRY_LEVEL"
                },
            })

    async def update(self, data):
        if 'quad_gantry_level' not in data and 'QGL' in self.footer_buttons:
            # remove QGL button from footer
            try:
                self.query_one(KluiFooter).remove()
            except:
                pass

            self.footer_buttons =['' if x == 'QGL' else x for x in self.footer_buttons]

            try:
                self.query_one('#toolhead_screen').mount(KluiFooter(id='footer', buttons=btns))
            except:
                pass

        try:
            await self.query_one(KluiHeader).update(data)
            # import json
            # with open('data.json', 'w', encoding='utf-8') as f:
            #     json.dump(data, f, ensure_ascii=False, indent=4)
        except:
            pass
        if 'gcode_move' in data and 'position' in data['gcode_move'] and 'gcode_position' in data['gcode_move']:
            zoffset = data['gcode_move']['position'][2] - data['gcode_move']['gcode_position'][2]

            try:
                # use goce_move -> homing_origin instead ?
                self.query_one('#zoffset').label = "Z offset: {:3.3f}".format(zoffset)
            except:
                pass

        if 'motion_report' in data:
            if 'live_position' in data['motion_report']:
                for i, axis in enumerate(["x", "y", "z"]):
                    try:
                        a = self.query_one(f"#axis_{axis}").query_one('.axis_pos')
                        a.pos = data['motion_report']['live_position'][i]
                    except:
                        pass
        elif 'toolhead' in data:
            if 'position' in data['toolhead']:
                for i, axis in enumerate(["x", "y", "z"]):
                    try:
                        a = self.query_one(f"#axis_{axis}").query_one('.axis_pos')
                        a.pos = data['toolhead']['position'][i]
                    except:
                        pass
        if 'toolhead' in data and 'homed_axes' in data['toolhead']:
            hm = data['toolhead']['homed_axes']
            for axis in ["x", "y", "z"]:
                try:
                    a = self.query_one(f"#axis_{axis}").query_one('.axis_homed')
                except:
                    continue
                if axis in hm:
                    a.label = "Homed"
                    a.styles.background = 'green'
                else: 
                    a.label = "Unhomed"
                    a.styles.background = 'orange'


