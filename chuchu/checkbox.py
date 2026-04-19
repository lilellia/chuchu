from collections.abc import Callable
import tkinter as tk
from typing import Any


from chuchu.ltypes import BoolVar
from chuchu.widget import DynamicWidget


class Checkbox(DynamicWidget[bool]):
    _TK_CLASS = tk.Checkbutton
    _TKVAR_CLASS = BoolVar

    def __init__(
        self,
        text: str = "",
        *,
        style: str = "window",
        checked: bool = False,
        onchange: Callable[[bool], Any] | None = None,
        **kwargs: Any,
    ) -> None:

        tk_kwargs = {
            "offvalue": 0,
            "onvalue": 1,
            "text": text,
        }

        super().__init__(tk_kwargs=tk_kwargs, style=style, checked=checked, onchange=onchange, **kwargs)

    @property
    def checked(self) -> bool:
        return self.value

    @checked.setter
    def checked(self, checked: bool, /) -> None:
        self.value = checked

    def set(self) -> None:
        """Set (turn on) the checkbox."""
        self.value = True

    def unset(self) -> None:
        """Unset (turn off) the checkbox."""
        self.value = False

    def toggle(self) -> None:
        """Reverse the setting of the checkbox: set if it unset, and vice versa."""
        self.value = not self.value
