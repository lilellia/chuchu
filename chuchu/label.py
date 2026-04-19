from collections.abc import Callable
import sys
import tkinter as tk
import tkinter.font
from tkinter import ttk
from typing import Any, cast, TYPE_CHECKING

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from chuchu.theming import active_theme

if TYPE_CHECKING:
    # This needs to be in TYPE_CHECKING because we use it here as just a type hint in Label.bind,
    # but Container.form needs Label at runtime
    from chuchu.widget import Container

from chuchu.text_widget import TextWidget


class Label(TextWidget):
    _TK_CLASS = tk.Label

    def __init__(
        self,
        text: str = "",
        *,
        style: str = "window",
        onchange: Callable[[str], Any] | None = None,
        **kwargs: Any
    ) -> None:
        super().__init__(text=text, value=text, style=style, onchange=onchange, **kwargs)

    @property
    def text(self) -> str:
        return cast(str, self.tkget("text"))

    @text.setter
    def text(self, text: str, /) -> None:
        self._value = text
        self.tkset(text=text)


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
        if master is None:
            raise TypeError("StatusBar master cannot be None")

        if master._tkobj is None:
            raise ValueError(f"StatusBar cannot be bound to master {master!r} which is not yet bound.")

        if not isinstance(master._tkobj, tk.Tk):
            raise ValueError("StatusBar master must be root window")

        super().bind(master, **kwargs)

        # immediately draw onto the parent
        assert isinstance(self._tkobj, (tk.Widget | ttk.Widget))
        self._tkobj.pack(side="bottom", fill="x", anchor="e", ipady=2)
