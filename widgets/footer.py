from textual.app import App, ComposeResult

from textual.widget import Widget

from textual.containers import Horizontal
from widgets.button import SmallButton
from rich.text import Text
from typing import ClassVar
import rich.repr
from widgets.button import SmallButton

@rich.repr.auto
class KluiFooter(Widget, can_focus=True):
    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "footer--description",
        "footer--key",
    }
    DEFAULT_CSS = """
    KluiFooter {
        background: $accent;
        color: $text-muted;
        dock: bottom;
        height: 1;
    }

    KluiFooter > .footer--key {
        text-style: bold;
        background: $accent-darken-3;
        color: $text;
    }
    """

    buttons = [
        'Quit',
        'Help',
        'Toolhead',
        'Print',
        'Extruder',
        'Misc',
        'Console',
        'STOP',
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            for button in self.buttons:
                yield SmallButton(self.generate_button_markup(button), id=button.lower())

    async def on_small_button_pressed(self, event: SmallButton.Pressed):
        try:
            action = "request_quit" if event.id == "quit" else event.id
            func = getattr(self.app, f"action_{action}")

            await func()
        except AttributeError:
            print(f"action_{action} not found")

    def generate_button_markup(self, label):
        text = Text()
        key_style = self.get_component_rich_style("footer--key")
        description_style = self.get_component_rich_style("footer--description")

        base_style = self.rich_style

        key_text = Text.assemble(
                (f" {label[0]}", key_style),
                (
                    f"{label[1:]}  ",
                    base_style + description_style,
                ),
                meta={
                    "key": label[0].lower(),
                },
            )

        text.append_text(key_text)
        return text