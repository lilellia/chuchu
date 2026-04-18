import tkinter as tk
from typing import Any, override

from chuchu.theming import active_theme
from chuchu.widget import TkConstructorInfo, Container


class Frame(Container):
    _TK_CLASS = tk.Frame

    def __init__(self, *, style: str | None = "window", **kwargs: Any) -> None:
        info = TkConstructorInfo(cls=self._TK_CLASS, kwargs=kwargs)
        super().__init__(constructor_info=info, style=style, **kwargs)

    @override
    def apply_style(self) -> None:
        if not self.is_bound or self.style is None:
            return

        style = active_theme.get_style(self.style)

        self.tkset(
            bg=style.background,
            relief=style.relief,
            border=0,
        )
