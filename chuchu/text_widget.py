from collections.abc import MutableMapping
import tkinter as tk
from typing import Any

from chuchu.widget import DynamicWidget

class TextWidget(DynamicWidget[str]):
    _TKVAR_CLASS = tk.StringVar
    _TKVAR_NAME = "textvariable"

    def __init__(
        self,
        text: str = "",
        *,
        style: str | None = None,
        tk_kwargs: MutableMapping[str, Any] | None = None,
        **kwargs: Any
    ) -> None:
        if tk_kwargs is None:
            tk_kwargs = {}

        tk_kwargs.setdefault("text", text)

        super().__init__(style=style, tk_kwargs=tk_kwargs, **kwargs)
        self._text = text

    @property
    def text(self) -> str:
        return self.value

    @text.setter
    def text(self, text: str, /) -> None:
        self.value = text

    def __str__(self) -> str:
        return self.text
