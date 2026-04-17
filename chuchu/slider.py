from functools import wraps
import tkinter as tk
from tkinter import ttk
from typing import override

from chuchu.widget import TkConstructorInfo, TWidget, Widget


class Slider[T](Widget, TWidget):
    _TK_CLASS = ttk.Scale

    def __init__(
        self,
        *,
        minimum: float = 0.0,
        value: float = 0.0,
        maximum: float = 100.0,
        resolution: float = 1.0,
        horizontal: bool = True,
        length: int = 100,
        onchange: Callable[[float], T] | None = None
    ) -> None:
        tk_kwargs = {
            "from_": minimum,
            "to": maximum,
            "orient": "horizontal" if horizontal else "vertical",
            "length": length,
        }

        kwargs = {
            "minimum": minimum,
            "maximum": maximum,
            "resolution": resolution,
            "horizontal": horizontal,
            "length": length,
        }

        if onchange:
            @wraps(onchange)
            def wrapper(_: float) -> T:
                value = self._lock_to_resolution()
                res = self._onchange_return_value = onchange(value)
                return res

            tk_kwargs["command"] = kwargs["onchange"] = wrapper

        info = TkConstructorInfo(cls=self._TK_CLASS, kwargs=tk_kwargs)
        super().__init__(constructor_info=info, **kwargs)
        self._value = value

    @override
    def bind(self, master: Container) -> None:
        self._var = tk.DoubleVar(master._tkobj, self._value)
        super().bind(master, variable=self._var)

    @override
    def apply_style(self) -> None:
        pass

    @property
    def value(self) -> float:
        if self.is_bound:
            return self._var.get()

        return self._value

    @value.setter
    def value(self, value: float) -> None:
        value = max(self.minimum, min(value, self.maximum))

        if self.is_bound:
            self._var.set(value)
        else:
            self._value = value

        self._lock_to_resolution()

    def _lock_to_resolution(self, *_) -> float:
        steps = round((self.value - self.minimum) / self.resolution)
        value = self.minimum + steps * self.resolution

        if self.is_bound:
            self._var.set(value)
        else:
            self._value = value

        return value
