import tkinter as tk
from tkinter import ttk
from typing import override

from chuchu.widget import TkConstructorInfo, TWidget, Widget
from chuchu.theming import active_theme


class ProgressBar(Widget, TWidget):
    _TK_CLASS = ttk.Progressbar

    def __init__(self, *, horizontal: bool = True, length: float = 100.0, determinate: bool = True, maximum: float = 100.0, value: float = 0.0, style: str = "primary", **kwargs) -> None:
        tk_kwargs = {
            "orient": "horizontal" if horizontal else "vertical",
            "length": length,
            "mode": "determinate" if determinate else "indeterminate",
            "maximum": maximum,
            "value": value
        }

        info = TkConstructorInfo(cls=self._TK_CLASS, kwargs=tk_kwargs)
        super().__init__(constructor_info=info, horizontal=horizontal, length=length, determinate=determinate, maximum=maximum, value=value, style=style)
        self._value = value

    @override
    def style_key_template(self) -> str:
        return f"{{id}}.{self.orientation.capitalize()}.TProgressbar"

    @override
    def apply_style(self) -> None:
        if not self.is_bound or self.style is None:
            return

        style = active_theme.get_style(self.style)

        self.apply_ttk_style(
            background=style.background,
            troughcolor=active_theme.window.background,
            bordercolor=active_theme.window.background,
            darkcolor=style.background,
            lightcolor=style.background
        )

    @property
    def value(self) -> float:
        return self.tkget_or("value", default=self._value)

    @value.setter
    def value(self, value: float) -> None:
        if self.is_bound:
            self.tkset(value=value)

        self._value = value

    @property
    def orientation(self) -> Literal["horizontal", "vertical"]:
        try:
            return str(self.tkget("orient"))
        except KeyError:
            return "horizontal" if self.horizontal else "vertical"

    def start(self, tick_ms: int = 50) -> None:
        self._tkobj.start(tick_ms)

    def stop(self) -> None:
        self._tkobj.stop()

    def step(self, amount: float = 1.0) -> None:
        self._tkobj.step(amount)
