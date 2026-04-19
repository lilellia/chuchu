from collections.abc import MutableMapping
import sys
import tkinter as tk
from typing import Any

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from chuchu.theming import active_theme
from chuchu.widget import Container


class Frame(Container):
    _TK_CLASS = tk.Frame

    def __init__(
        self, *, style: str | None = "window", tk_kwargs: MutableMapping[str, Any] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(tk_kwargs=tk_kwargs, style=style, **kwargs)

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
