from collections.abc import Iterable
import itertools
import tkinter as tk
from typing import Any, NamedTuple

from chuchu.theming import Style, active_theme


def clone_tk_widget(tkobj, master=None):
    """
    Create a cloned version of a given tk widget.
    Optionally, set a new master.

    ALai on Stack Overflow:
    https://stackoverflow.com/a/69538200
    """
    parent = master or tkobj.master
    cls = tkobj.__class__

    cfg = {k: tkobj.cget(k) for k in tkobj.configure()}
    cloned = cls(parent, **cfg)

    # clone the children
    for child in tkobj.winfo_children():
        child_cloned = clone_tk_widget(child, master=cloned)

        if info := child.grid_info():
            grid_info = {k: v for k, v in info.items() if k not in ("in",)}
            child_cloned.grid(**grid_info)

        elif info := child.place_info():
            place_info = {k: v for k, v in info.items() if k not in ("in",)}
            child_cloned.place(**place_info)

        elif info := child.pack_info():
            pack_info = {k: v for k, v in info.items() if k not in ("in",)}

    return cloned


class Widget:
    def __init__(self, *, tkobj, style: str | None = None, **kwargs) -> None:
        self._tkobj = tkobj
        self.style = style
        for k, v in kwargs.items():
            setattr(self, k, v)

    def apply_style(self) -> None:
        if self.style is None:
            return

        style = active_theme.get_style(self.style)

        self.proxy("configure")(
            bg=style.background,
            fg=style.foreground,
            activebackground=style.active,
            border=0,
            relief=style.relief,
        )

    def proxy(self, attr: str) -> Any:
        """Proxy the lookup of the given attribute onto the underlying tkinter object."""
        return getattr(self._tkobj, attr)

    def tkget(self, field: str) -> str:
        """Query the underlying tkinter object for the given field. If the field is unknown, raise KeyError."""
        try:
            return self.proxy("cget")(field)
        except tk.TclError:
            raise KeyError(field)


class GridNode(NamedTuple):
    widget: Widget
    weight: int


class Container(Widget):
    def __init__(self, *, tkobj, **kwargs) -> None:
        super().__init__(tkobj=tkobj, **kwargs)
        self._grid = []

    def grid(self, widgets: Iterable[Iterable[Widget]], *, columns: int | None = None, weights: Iterable[Iterable[int]] | None = None, **kwargs) -> None:
        if weights is None:
            weights = itertools.repeat(itertools.repeat(1))

        for widget_row, weight_row in zip(widgets, weights):
            allocated = 0
            row = []
            for widget, weight in zip(widget_row, weight_row):
                if columns is None or allocated + weight <= columns:
                    # this widget will fit on the current row, so put it there
                    row.append(GridNode(widget, weight))
                    allocated += weight
                else:
                    # it doesn't fit, so push the row and start a new one
                    self._grid.append(row)
                    row = [GridNode(widget, weight)]
                    allocated = weight

            if row:
                self._grid.append(row)

        kwargs = {"padx": 5, "pady": 5, "sticky": "nsew", **kwargs}
        self._update_grid(**kwargs)

    def add_row(self, widgets: Iterable[Widget], *, columns: int | None = None, weights: Iterable[int] | None = None, **kwargs) -> None:
        self.grid([widgets], columns=columns, weights=[weights] if weights else None, **kwargs)

    def _update_grid(self, **kwargs) -> None:
        for y, row in enumerate(self._grid):
            x = 0
            for node in row:
                if node.widget is not None:
                    w = node.widget._tkobj = clone_tk_widget(node.widget._tkobj, master=self._tkobj)
                    node.widget.apply_style()
                    w.grid(row=y, column=x, columnspan=node.weight, **kwargs)


                x += node.weight


class TextWidget(Widget):
    _TK_CLASS: type[tk.Widget]

    def __init__(self, text: str = "", *, tk_kwargs: dict[str, Any] | None = None, **kwargs) -> None:
        self._var = tk.StringVar(None, text)

        super().__init__(
            tkobj=self._TK_CLASS(None, textvariable=self._var, **(tk_kwargs or {})),
            **kwargs
        )

    @property
    def text(self) -> str:
        return self._var.get()

    @text.setter
    def text(self, text: str, /) -> None:
        if not isinstance(text, str):
            raise TypeError(f"{type(self).__name__}.text should be a string, not {text!r}")

        if (validator := getattr(self, "validator", None)) and not validator(text):
            raise ValueError(f"{text=} is not a valid value for this textbox: {validator.__name__}")

        self._var.set(text)

    def __str__(self) -> str:
        return self.text
