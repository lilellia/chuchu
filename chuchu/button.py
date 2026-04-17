from collections.abc import Callable
from functools import wraps
import tkinter as tk
from typing import Any, TypeVar, cast

from chuchu.widget import TextWidget


T = TypeVar("T")


class Button(TextWidget):
    _TK_CLASS = tk.Button

    def __init__(self, text: str = "", *, onclick: Callable[[], T] | None = None, **kwargs: Any) -> None:
        self._onclick_return_value = None

        if onclick:

            @wraps(onclick)
            def wrapper() -> T:
                res = self._onclick_return_value = onclick()
                return res

            tk_kwargs = dict(command=wrapper)
        else:
            tk_kwargs = None

        super().__init__(text=text, onclick=onclick, tk_kwargs=tk_kwargs, **kwargs)

    def click(self) -> Any:
        if self.onclick and self.is_bound:  # type: ignore[attr-defined]
            cast(tk.Button, self._tkobj).invoke()
            return self._onclick_return_value

        # in the case where self.onclick is None, T should be None
        return None
