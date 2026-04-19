from collections.abc import Iterable, MutableMapping
import itertools
import sys
import tkinter as tk
from tkinter import ttk
from typing import Any

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


from chuchu.widget import DynamicWidget, TtkWidget


class Dropdown(TtkWidget, DynamicWidget[str]):
    _TK_CLASS = ttk.Combobox
    _TKVAR_CLASS = tk.StringVar
    _TKVAR_NAME = "textvariable"

    _options: tuple[str, ...]

    def __init__(
        self,
        options: Iterable[str],
        *,
        value: str = "",
        style: str | None = "default",
        tk_kwargs: MutableMapping[str, Any] | None = None,
        **kwargs: Any
    ) -> None:
        if tk_kwargs is None:
            tk_kwargs = {}

        self.options = options
        tk_kwargs["values"] = self.options
        tk_kwargs.setdefault("state", "readonly")

        super().__init__(tk_kwargs=tk_kwargs, style=style, value=value, **kwargs)

    @override
    @property
    def value(self) -> str:
        return super().value

    @override
    @value.setter
    def value(self, value: str, /) -> None:
        if value not in self.options:
            opts = ", ".join(self.options)
            raise ValueError(f"{value} is not a valid option: must be one of {{{opts}}}")

        super().value = value

    @property
    def options(self) -> tuple[str, ...]:
        return self.tkget("values", self._options)

    @options.setter
    def options(self, options: Iterable[str], /) -> None:
        # always prepend "" (empty string) to the options list
        self._options = tuple(str(opt) for opt in itertools.chain(("",), options))
        self.tkset(values=self._options)

        # if the current value is no longer valid, reset it
        if self.value not in self._options:
            self.value = ""
