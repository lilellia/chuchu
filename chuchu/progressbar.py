import tkinter as tk
from tkinter import ttk
from typing import override

from chuchu.widget import Widget, clone_tk_widget
from chuchu.theming import active_theme


class ProgressBar(Widget):
    _TK_CLASS = ttk.Progressbar

    def __init__(self, *, horizontal: bool = True, length: float = 100.0, determinate: bool = True, maximum: float = 100.0, value: float = 0.0, style: str = "primary", **kwargs) -> None:
        tk_kwargs = {
            "orient": "horizontal" if horizontal else "vertical",
            "length": length,
            "mode": "determinate" if determinate else "indeterminate",
            "maximum": maximum,
            "value": value
        }
        super().__init__(tkobj=self._TK_CLASS(None, **tk_kwargs), horizontal=horizontal, length=length, determinate=determinate, maximum=maximum, value=value, style=style)

    @override
    def apply_style(self) -> None:
        if self.style is None:
            return

        style = active_theme.get_style(self.style)

        s = ttk.Style()

        key = f"{id(self)}.{self.orientation.capitalize()}.T{self._TK_CLASS.__name__}"
        s.configure(
            key,
            background=style.background,
            troughcolor=active_theme.window.background,
            bordercolor=active_theme.window.background,
            darkcolor=style.background,
            lightcolor=style.background
        )


        self.proxy("configure")(style=key)

    @property
    def value(self) -> float:
        return self.tkget("value")

    @value.setter
    def value(self, value: float) -> None:
        self.proxy("configure")(value=value)

    @property
    def orientation(self) -> Literal["horizontal", "vertical"]:
        return str(self.tkget("orient"))

    def start(self, tick_ms: int = 50) -> None:
        self.proxy("start")(tick_ms)

    def stop(self) -> None:
        self.proxy("stop")()

    def step(self, amount: float = 1.0) -> None:
        self.proxy("step")(amount)
