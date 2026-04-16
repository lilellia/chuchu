import sys
from threading import Thread
import tkinter as tk
from typing import override

from chuchu.widget import Container
from chuchu.ltypes import Position, Size
from chuchu.theming import active_theme


class Application(Container):
    def __init__(self, *, title: str = "chuchu application", size: tuple[int, int] | None = None) -> None:
        super().__init__(tkobj=tk.Tk())

        self.title = title

        if size:
            self.size = size

        self.apply_style()

    @override
    def apply_style(self) -> None:
        self.proxy("configure")(background=active_theme.window.background)

    @property
    def title(self) -> str:
        """Get the window title."""
        return self.proxy("title")()

    @title.setter
    def title(self, title: str) -> None:
        """Return the current window title. Raises a TypeError if the new title is not a string."""
        if not isinstance(title, str):
            raise TypeError(f"window title should be a string, not {title!r}")

        self.proxy("title")(title)

    @property
    def size(self) -> Size:
        """Get the current window size, in the form Size(width=500, height=750)."""
        g = self.proxy("geometry")()

        # g = "200x200+860+430" (WxH+X+Y)
        width, height = g.split("+")[0].split("x")
        return Size(width=int(width), height=int(height))

    @size.setter
    def size(self, size: tuple[int, int]) -> None:
        """Set the window size. Raises ValueError if the value cannot be interpreted as (int, int)."""
        try:
            width, height = map(int, size)
        except ValueError:
            raise ValueError(f"Window size must be interpretable as (int, int), not {size!r}")

        self.proxy("geometry")(f"{width}x{height}")

    @property
    def position(self) -> Position:
        """Return the current window position, in the form Position(x=100, y=300)."""
        g = self.proxy("geometry")()

        # g = "200x200+860+430" (WxH+X+Y)
        x, y = g.split("+", maxsplit=1)[1].split("+")
        return Position(x=int(x), y=int(y))

    @position.setter
    def position(self, pos: tuple[int, int]) -> None:
        """Set the window position. Raises ValueError if the value cannot be interpreted as (int, int)."""
        try:
            x, y = map(int, pos)
        except ValueError:
            raise ValueError(f"Window position must be interpretable as (int, int), not {pos!r}")

        size = self.size
        self.proxy("geometry")(f"{size.width}x{size.height}+{x}+{y}")

    @property
    def theme(self) -> str:
        return self.proxy("tk").call("ttk::style", "theme", "use")

    @theme.setter
    def theme(self, theme: str) -> None:
        ttk.Style(self._tkobj).theme_use(theme)

    def run(self) -> None:
        """Run the application. This is a blocking call."""
        self.proxy("mainloop")()
