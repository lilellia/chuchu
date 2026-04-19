from collections.abc import Callable
import tkinter as tk
from typing import Any

from chuchu.widget import TextWidget


class Textbox(TextWidget):
    _TK_CLASS = tk.Entry

    def __init__(
        self,
        text: str = "",
        *,
        validator: Callable[[str], bool] | None = None,
        onchange: Callable[[str], Any] | None = None,
        **kwargs: Any
    ) -> None:
        super().__init__(text=text, validator=validator, value=text, onchange=onchange, **kwargs)

    def write(self, text: str) -> int:
        """Write the given text to the end of the textbox, returning the number of characters written."""
        if not isinstance(text, str):
            raise TypeError(f"Textbox.write argument should be a string, not {text!r}")

        self.text += text
        return len(text)

    def clear(self) -> None:
        """Clear the contents of the textbox. Equivalent to `textbox.text = ""`"""
        self.text = ""

    def backspace(self) -> str:
        """
        Remove the final character of the textbox, returning it.
        If the textbox is already empty, return the empty string.
        """
        if not self.text:
            return ""

        self.text, final = self.text[:-1], self.text[-1]
        return final
