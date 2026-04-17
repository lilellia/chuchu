import tkinter as tk
from typing import Any

from chuchu.widget import TextWidget


class Label(TextWidget):
    _TK_CLASS = tk.Label

    def __init__(self, text: str = "", *, style: str = "window", **kwargs: Any) -> None:
        super().__init__(text=text, style=style, **kwargs)
