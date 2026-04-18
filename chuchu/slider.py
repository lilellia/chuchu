from collections.abc import Callable
from functools import wraps
import sys
from tkinter import ttk
from typing import Any, TypeVar

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from chuchu.widget import TWidget, DynamicWidget


T = TypeVar("T")


class Slider(DynamicWidget[float], TWidget):
    _TK_CLASS = ttk.Scale

    minimum: float
    maximum: float
    resolution: float
    horizontal: bool
    length: int

    def __init__(
        self,
        *,
        minimum: float = 0.0,
        value: float = 0.0,
        maximum: float = 100.0,
        resolution: float = 1.0,
        horizontal: bool = True,
        length: int = 100,
        onchange: Callable[[float], T] | None = None,
        style: str | None = "default",
    ) -> None:
        tk_kwargs: dict[str, Any] = {
            "from_": minimum,
            "to": maximum,
            "orient": "horizontal" if horizontal else "vertical",
            "length": length,
        }

        kwargs: dict[str, Any] = {
            "minimum": minimum,
            "maximum": maximum,
            "resolution": resolution,
            "horizontal": horizontal,
            "length": length,
        }

        if onchange:

            @wraps(onchange)
            def wrapper(_: float) -> Any:
                value = self._lock_to_resolution()
                res = self._onchange_return_value = onchange(value)
                return res

            tk_kwargs["command"] = kwargs["onchange"] = wrapper

        super().__init__(tk_kwargs=tk_kwargs, style=style, **kwargs)
        self._value = value

    @override
    def apply_style(self) -> None:
        pass

    @property
    def value(self) -> float:
        return super().value

    @value.setter
    def value(self, value: float) -> None:
        value = max(self.minimum, min(value, self.maximum))

        if self._var:
            self._var.set(value)

        self._value = value

        self._lock_to_resolution()

    def _lock_to_resolution(self, *_: Any) -> float:
        steps = round((self.value - self.minimum) / self.resolution)
        value = self.minimum + steps * self.resolution

        if self._var:
            self._var.set(value)

        self._value = value
        return value
