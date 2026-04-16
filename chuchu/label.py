import tkinter as tk

from chuchu.widget import TextWidget


class Label(TextWidget):
    _TK_CLASS = tk.Label

    def __init__(self, text: str = "", *, style: str = "window",  **kwargs) -> None:
        super().__init__(text=text, style=style, **kwargs)
