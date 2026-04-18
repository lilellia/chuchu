from collections.abc import Callable
import tkinter as tk
from typing import Any, override


from chuchu.widget import TkConstructorInfo, Widget


class Checkbox(Widget):
    _TK_CLASS = tk.Checkbutton

    def __init__(
        self,
        text: str = "",
        *,
        style: str = "window",
        checked: bool = False,
        onchange: Callable[[bool], Any] | None = None,
        **kwargs: Any
    ) -> None:

        tk_kwargs = {
            "offvalue": 0,
            "onvalue": 1,
            "text": text,
        }

        info = TkConstructorInfo(cls=self._TK_CLASS, kwargs=tk_kwargs)

        super().__init__(constructor_info=info, style=style, checked=checked, onchange=onchange, **kwargs)

    @override
    def bind(self, master: Container | None, **kwargs: Any) -> None:
        if master is None:
            raise ValueError("Checkbox master cannot be None")

        self._var = tk.IntVar(master._tkobj)
        super().bind(master, variable=self._var)
        if self.onchange:
            self.bind_onchange(self.onchange)

    @property
    def value(self) -> bool:
        if self.is_bound:
            return bool(self._var.get())

        return self._checked

    @value.setter
    def value(self, value: bool, /) -> None:
        if self.is_bound:
            self._var.set(int(bool(value)))

        self._checked = bool(value)

    @property
    def checked(self) -> bool:
        return self.value

    @checked.setter
    def checked(self, checked: bool, /) -> None:
        self.value = checked

    @property
    def onchange(self) -> Callable[[float], Any] | None:
        return self._onchange

    @onchange.setter
    def onchange(self, onchange: Callable[[float], Any] | None, /) -> None:
        self._onchange = onchange
        if onchange:
            self.bind_onchange(onchange)

    def set(self) -> None:
        """Set (turn on) the checkbox."""
        self.value = True

    def unset(self) -> None:
        """Unset (turn off) the checkbox."""
        self.value = False

    def toggle(self) -> None:
        """Reverse the setting of the checkbox: set if it unset, and vice versa."""
        self.value = not self.value
