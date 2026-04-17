from abc import ABC, abstractproperty, abstractmethod
from collections.abc import Iterable
from collections import ChainMap
import itertools
import tkinter as tk
from typing import Any, NamedTuple

from chuchu.theming import Style, active_theme


class TkConstructorInfo(NamedTuple):
    cls: type[tk.Widget] | type[ttk.Widget]
    kwargs: dict[str, Any]


class Widget:
    def __init__(self, *, constructor_info: TkConstructorInfo, style: str | None = None, **kwargs) -> None:
        self._tkobj: tk.Widget | ttk.Widget | None = None
        self._constructor_info = constructor_info
        self._config_buffer: dict[str, Any] = {}
        self._lookup = ChainMap(constructor_info.kwargs, self._config_buffer)
        self.style = style

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def is_bound(self) -> bool:
        return self._tkobj is not None

    def bind(self, master: Container | None, **kwargs) -> None:
        self._tkobj = self._constructor_info.cls(master._tkobj if master else None, **{**self._lookup, **kwargs})
        self._config_buffer.clear()

    def apply_style(self) -> None:
        if not self.is_bound or self.style is None:
            return

        style = active_theme.get_style(self.style)

        self.tkset(
            bg=style.background,
            fg=style.foreground,
            activebackground=style.active,
            border=0,
            relief=style.relief,
        )

    def tkget(self, field: str) -> Any:
        """Query the underlying tkinter object for the given field. If the field is unknown, raise KeyError."""
        if not self.is_bound:
            return self._lookup[field]

        try:
            return self._tkobj.cget(field)
        except tk.TclError:
            raise KeyError(field)

    def tkget_or(self, field: str, default: Any = None) -> Any:
        try:
            return self.tkget(field)
        except Exception:
            return default

    def tkset(self, **kwargs: Any) -> None:
        if not self.is_bound:
            self._config_buffer.update(**kwargs)
            return

        self._tkobj.configure(**kwargs)


class GridNode(NamedTuple):
    widget: Widget
    weight: int


class Container(Widget):
    def __init__(self, *, constructor_info: TkConstructorInfo, **kwargs) -> None:
        super().__init__(constructor_info=constructor_info, **kwargs)
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
        max_columns = 0
        for y, row in enumerate(self._grid):
            self._tkobj.rowconfigure(y, weight=1)
            x = 0
            for node in row:
                if node.widget is not None:
                    if not node.widget.is_bound:
                        node.widget.bind(self)

                    node.widget.apply_style()
                    node.widget._tkobj.grid(row=y, column=x, columnspan=node.weight, **kwargs)


                x += node.weight
                max_columns = max(max_columns, x)

        for i in range(max_columns):
            self._tkobj.columnconfigure(i, weight=1)


class TWidget(ABC):
    @property
    def style_key_template(self) -> str:
        return f"{{id}}.T{self._TK_CLASS.__name__}"

    def apply_ttk_style(self, **kwargs) -> None:
        key = self.style_key_template.format(id=id(self))

        ttk.Style().configure(key, **kwargs)
        self.tkset(style=key)

    @abstractmethod
    def apply_style(self) -> None:
        pass


class TextWidget(Widget):
    _TK_CLASS: type[tk.Widget]

    def __init__(self, text: str = "", *, tk_kwargs: dict[str, Any] | None = None, **kwargs) -> None:
        info = TkConstructorInfo(cls=self._TK_CLASS, kwargs={"text": text, **(tk_kwargs or {})})
        super().__init__(constructor_info=info, **kwargs)
        self._text = text

    def bind(self, master: Container) -> None:
        self._var = tk.StringVar(master._tkobj, self._text)
        super().bind(master, textvariable=self._var)

    @property
    def text(self) -> str:
        if self.is_bound:
            return self._var.get()

        return self._text

    @text.setter
    def text(self, text: str, /) -> None:
        if not isinstance(text, str):
            raise TypeError(f"{type(self).__name__}.text should be a string, not {text!r}")

        if (validator := getattr(self, "validator", None)) and not validator(text):
            raise ValueError(f"{text=} is not a valid value for this textbox: {validator.__name__}")

        if self.is_bound:
            self._var.set(text)

        self._text = text

    def __str__(self) -> str:
        return self.text
