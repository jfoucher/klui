from textual.app import App, ComposeResult

from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Horizontal
from widgets.button import SmallButton
from rich.text import Text
from typing import ClassVar
import rich.repr
from widgets.button import SmallButtonNoFocus

@rich.repr.auto
class KluiFooter(Widget, can_focus=True):
    DEFAULT_CSS = """
    KluiFooter {
        background: $accent;
        color: $text-muted;
        dock: bottom;
        height: 1;
    }

    
    """

    buttons = reactive([
        'Help',
        'Quit',
        'Toolhead',
        'Print',
        'Extruder',
        'Misc',
        'Console',
        '',
        '',
        'STOP',
    ])

    def __init__(self, *children: Widget, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False, buttons: list|None = None) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        if buttons:
            self.buttons = buttons

    def compose(self) -> ComposeResult:
        with Horizontal():
            for i, button in enumerate(self.buttons):
                if button:
                    yield self.generate_button_markup(button, i)

    async def on_small_button_pressed(self, event: SmallButton.Pressed):
        try:
            action = "request_quit" if event.id == "quit" else event.id
            if self.app.get_screen('toolhead').is_current and action == 'help':
                self.app.push_screen("toolhelp")
            else:
                func = getattr(self.app, f"action_{action.replace(' ', '_')}")

                await func()
        except AttributeError:
            print(f"action_{action} not found")

    async def on_key(self, event):
        if not event.key or 'f' not in event.key:
            return
        num = int(event.key.replace('f', '')) - 1
        action = self.buttons[num].lower()

        try:
            action = "request_quit" if action == "quit" else action
            func = getattr(self.app, f"action_{action.replace(' ', '_')}")

            await func()
        except AttributeError:
            print(f"action_{action.replace(' ', '_')} not found")


    def generate_button_markup(self, label, i):
        return SmallButtonNoFocus("", shortcut=str(i+1), text = label, id=label.lower())
        return f"{i+1}{label}"
        text = Text()

        key_text = Text.assemble(
                (f" {i+1}", key_style),
                (
                    f"{label}  ",
                    base_style + description_style,
                ),
                meta={
                    "key": label[0].lower(),
                },
            )

        text.append_text(key_text)
        return text