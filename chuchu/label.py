import tkinter as tk
import tkinter.font
from typing import override

from chuchu.theming import active_theme
from chuchu.widget import TextWidget


class Label(TextWidget):
    _TK_CLASS = tk.Label

    def __init__(self, text: str = "", *, style: str = "window", **kwargs: Any) -> None:
        super().__init__(text=text, style=style, **kwargs)


class StatusBar(Label):
    def __init__(self, text: str = "", *, style: str = "window", **kwargs: Any) -> None:
        super().__init__(text=text, style=style, tk_kwargs=dict(anchor="e"), **kwargs)

    @override
    def apply_style(self) -> None:
        if not self.is_bound or self.style is None:
            return

        style = active_theme.get_style(self.style)

        f = tkinter.font.nametofont("TkDefaultFont").copy()
        f.config(size=8)

        cfg = {
            **style.tkdict(),
            "relief": "sunken",
            "bd": 1,
            "font": f,
        }

        self.tkset(**cfg)

    @override
    def bind(self, master: Container | None, **kwargs: Any) -> None:
        if not isinstance(master._tkobj, tk.Tk):
            raise ValueError("StatusBar master must be root window")

        super().bind(master, **kwargs)

        # immediately draw onto the parent
        self._tkobj.pack(side="bottom", fill="x", anchor="e", ipady=2)
