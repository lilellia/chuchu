from collections.abc import Callable, Mapping
import sys
import tkinter as tk
from typing import ParamSpec, TypeVar, cast

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from chuchu.frame import Frame
from chuchu.label import StatusBar
from chuchu.ltypes import Position, Size
from chuchu.menu import MenuBar
from chuchu.theming import active_theme
from chuchu.widget import Container, TkConstructorInfo


P = ParamSpec("P")
R = TypeVar("R")


class Application(Container):
    def __init__(
        self,
        *,
        title: str = "chuchu application",
        size: tuple[int, int] | None = None,
        status: str | None = None,
    ) -> None:
        super().__init__(constructor_info=TkConstructorInfo(cls=tk.Tk, kwargs={}))
        self.bind(None)

        self.title = title

        if size:
            self.size = size

        # create the status bar
        self._status_bar: StatusBar | None = None
        self.status = status

        # create the general background frame
        self._frame = Frame()
        self._frame.bind(self)
        self._frame._tkobj.pack(side="top", fill="both", expand=True)

        self.apply_style()

    def dispatch(self, func: Callable[P, R], after: float = 0.0, *args: P.args, **kwargs: P.kwargs) -> None:
        """Schedule a thread-safe call of the function to run on the main thread after `after` seconds."""
        cast(tk.Tk, self._tkobj).after(round(1000 * after), lambda: func(*args, **kwargs))

    def set_menubar(self, layout: dict[str, dict[str, Callable[[], Any]] | None]) -> MenuBar:
        menubar = MenuBar(layout)
        menubar.bind(self)
        return menubar

    @override
    def grid(
        self,
        widgets: Iterable[Iterable[Widget]],
        *,
        columns: int | None = None,
        weights: Iterable[Iterable[int]] | None = None,
        **kwargs: Any
    ) -> Iterable[Iterable[Widget]]:
        return self._frame.grid(widgets, columns=columns, weights=weights, **kwargs)

    @override
    def add_row(
        self,
        widgets: Iterable[Widget],
        *,
        columns: int | None = None,
        weights: Iterable[int] | None = None,
        **kwargs: Any,
    ) -> Iterable[Widget]:
        return self._frame.add_row(widgets, columns=columns, weights=weights, **kwargs)

    @override
    def form(self, widget_map: Mapping[str, Widget], *, weights: tuple[int, int] | None = None) -> None:
        return self._frame.form(widget_map, weights=weights)

    @override
    def apply_style(self) -> None:
        self.tkset(background=active_theme.window.background)
        self._frame.apply_style()

    @property
    def title(self) -> str:
        """Get the window title."""
        return cast(tk.Tk, self._tkobj).title()

    @title.setter
    def title(self, title: str) -> None:
        """Return the current window title. Raises a TypeError if the new title is not a string."""
        if not isinstance(title, str):
            raise TypeError(f"window title should be a string, not {title!r}")

        cast(tk.Tk, self._tkobj).title(title)

    @property
    def size(self) -> Size:
        """Get the current window size, in the form Size(width=500, height=750)."""
        g = cast(tk.Tk, self._tkobj).geometry()

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

        cast(tk.Tk, self._tkobj).geometry(f"{width}x{height}")

    @property
    def position(self) -> Position:
        """Return the current window position, in the form Position(x=100, y=300)."""
        g = cast(tk.Tk, self._tkobj).geometry()

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
        cast(tk.Tk, self._tkobj).geometry(f"{size.width}x{size.height}+{x}+{y}")

    @property
    def status(self) -> str | None:
        return self._status

    @status.setter
    def status(self, value: str | None, /) -> None:
        match (value, self._status_bar):
            case [None, None]:
                # there wasn't a status bar and we still don't want one
                pass

            case [None, sb]:
                # there was a status bar, but we don't want one now
                sb.forget()

            case [status, None]:
                # there wasn't a status bar, but now we want one
                self._status_bar = StatusBar(f"{status}  ")

                self._status_bar.bind(self)
                self._status_bar.apply_style()

            case [status, sb]:
                # just update the status
                sb.text = f"{status}  "

    def run(self) -> None:
        """Run the application. This is a blocking call."""
        cast(tk.Tk, self._tkobj).mainloop()

    def quit(self) -> None:
        self._tkobj.destroy()
