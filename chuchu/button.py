from collections.abc import Callable, MutableMapping
from functools import wraps
import tkinter as tk
from typing import Any, TypeVar, cast

from chuchu.widget import TextWidget


T = TypeVar("T")


class Button(TextWidget):
    _TK_CLASS = tk.Button

    _onclick: Callable[[], Any] | None
    _onclick_return_value: Any = None

    def __init__(
        self,
        text: str = "",
        *,
        style: str | None = None,
        tk_kwargs: MutableMapping[str, Any] | None = None,
        onclick: Callable[[], T] | None = None,
        **kwargs: Any
    ) -> None:
        if tk_kwargs is None:
            tk_kwargs = {}

        self._onclick_return_value = None

        if onclick:

            @wraps(onclick)
            def wrapper() -> T:
                res = self._onclick_return_value = onclick()
                return res

            tk_kwargs["command"] = wrapper

        super().__init__(text=text, style=style, onclick=onclick, tk_kwargs=tk_kwargs, **kwargs)

    @property
    def onclick(self) -> Callable[[], Any] | None:
        return self._onclick

    @onclick.setter
    def onclick(self, func: Callable[[], Any] | None, /) -> None:
        if not func:
            self._onclick = None
            return

        @wraps(func)
        def wrapper(*_: str) -> Any:
            res = self._onchange_return_value = func()
            return res

        self.tkset(command=wrapper)
        self._onclick = func

    def click(self) -> Any:
        if self.onclick and self.is_bound:
            cast(tk.Button, self._tkobj).invoke()
            return self._onclick_return_value
