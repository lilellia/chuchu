from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping, MutableMapping
from functools import wraps
import itertools
import sys
import tkinter as tk
from tkinter import ttk
from typing import Any, ClassVar, Generic, NamedTuple, TypeVar, cast


if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


from chuchu.ltypes import Tk, TkVar, TypeTkWidget
from chuchu.theming import active_theme


T = TypeVar("T", str, float, int, bool)


class Widget:
    _TK_CLASS: ClassVar[TypeTkWidget]

    def __init__(
        self, *, style: str | None = None, tk_kwargs: MutableMapping[str, Any] | None = None, **kwargs: Any
    ) -> None:
        self._tkobj: tk.Tk | tk.Widget | ttk.Widget | None = None
        self._tk_kwargs = tk_kwargs or {}
        self.style = style

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def is_bound(self) -> bool:
        return self._tkobj is not None

    def bind(self, master: Container | None, **kwargs: Any) -> None:
        self._tk_kwargs.update(kwargs)
        clsname = self._TK_CLASS.__name__

        if master is None:
            if self._TK_CLASS != Tk:
                raise TypeError(f"Instance of {clsname} must have a master object, not None.")

            self._tkobj = self._TK_CLASS(**self._tk_kwargs)

        else:
            if self._TK_CLASS == Tk:
                raise TypeError(f"Instance of {clsname} cannot have a master object.")

            if master._tkobj is None:
                raise ValueError(f"Instance of {clsname} cannot be bound to master {master!r} which is not yet bound.")

            self._tkobj = self._TK_CLASS(master._tkobj, **self._tk_kwargs)

    def apply_style(self) -> None:
        if not self.is_bound or self.style is None:
            return

        style = active_theme.get_style(self.style)

        self.tkset(**style.tkdict())

    def tkget(self, field: str, default: Any = None) -> Any:
        """Query the underlying tkinter object for the given field. If the field is unknown, raise KeyError."""
        if self._tkobj:
            try:
                return self._tkobj.cget(field)
            except tk.TclError:
                return default

        return self._tk_kwargs.get(field, default)

    def tkset(self, **kwargs: Any) -> None:
        if self._tkobj:
            self._tkobj.configure(**kwargs)

        self._tk_kwargs.update(**kwargs)

    def defer_set(self, **kwargs: Any) -> Callable[[], None]:
        def _set() -> None:
            self.tkset(**kwargs)

        return _set


class DynamicWidget(Widget, Generic[T]):
    _TKVAR_CLASS: ClassVar[type[TkVar[Any]]]
    _TKVAR_NAME: ClassVar[str] = "variable"

    _var: TkVar[T] | None = None
    _value: T

    _onchange: Callable[[T], Any] | None
    _onchange_return_value: Any = None

    # {cb_name: var}
    # This is a dict mapping callback names to the variable that is tracing them.
    # As these are internal/protected callbacks, the usual onchange property won't touch them.
    _protected_onchange_cb: dict[str, tk.Variable] | None = None

    @property
    def value(self) -> T:
        if self._var:
            return self._var.get()

        return self._value

    @value.setter
    def value(self, value: T, /) -> None:
        if self._var:
            self._var.set(value)

        self._value = value

    @property
    def onchange(self) -> Callable[[T], Any] | None:
        return self._onchange

    @onchange.setter
    def onchange(self, func: Callable[[T], Any] | None, /) -> None:
        if self._var:
            # remove any existing trace on the variable
            # as long as it's not protected
            for mode, cb_name in self._var.trace_info():
                if self._protected_onchange_cb and cb_name in self._protected_onchange_cb:
                    continue

                if "write" in mode:
                    self._var.trace_remove("write", cb_name)

        if not func:
            self._onchange = None
            return

        @wraps(func)
        def wrapper(*_: str) -> Any:
            res = self._onchange_return_value = func(self.value)
            return res

        if self._var:
            self._var.trace_add("write", wrapper)

        self._onchange = func

    @override
    def bind(self, master: Container | None, **kwargs: Any) -> None:
        if master is None:
            raise TypeError(f"None is not a valid bind target for {type(self).__name__} variable")

        if master._tkobj is None:
            raise ValueError(f"Cannot bind variable of {type(self).__name__} to unbound parent {master!r}")

        self._var = self._TKVAR_CLASS(master._tkobj, self.value)

        if self._TKVAR_NAME:
            kwargs[self._TKVAR_NAME] = self._var

        super().bind(master, **kwargs)

        # This looks silly, but if an onchange was registered, it won't be hooked into the trace yet,
        # so we do this to force that hook to be made.
        if self._onchange:
            self.onchange = self._onchange


class GridNode(NamedTuple):
    widget: Widget
    weight: int


class Container(Widget):
    def __init__(self, *, style: str | None = None, tk_kwargs: MutableMapping[str, Any] | None, **kwargs: Any) -> None:
        super().__init__(style=style, tk_kwargs=tk_kwargs, **kwargs)
        self._grid: list[list[GridNode]] = []
        self._form: dict[str, Widget] = {}

    def __getitem__(self, key: str) -> Widget:
        """Return a reference to the widget that was added as a form element with the given key."""
        return self._form[key]

    def grid(
        self,
        widgets: Iterable[Iterable[Widget]],
        *,
        columns: int | None = None,
        weights: Iterable[Iterable[int]] | None = None,
        **kwargs: Any,
    ) -> Iterable[Iterable[Widget]]:
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
        return widgets

    def add_row(
        self,
        widgets: Iterable[Widget],
        *,
        columns: int | None = None,
        weights: Iterable[int] | None = None,
        **kwargs: Any,
    ) -> Iterable[Widget]:
        self.grid([widgets], columns=columns, weights=[weights] if weights else None, **kwargs)
        return widgets

    def form(self, widget_map: Mapping[str, Widget], *, weights: tuple[int, int] | None = None) -> None:
        if weights is None:
            weights = (1, 1)

        for key, widget in widget_map.items():
            label = self._form[f"{key}-label"] = Label(key)
            self._form[key] = widget
            self.add_row((label, widget), columns=2, weights=weights)

    def _update_grid(self, **kwargs: Any) -> None:
        max_columns = 0
        for y, row in enumerate(self._grid):
            assert self._tkobj is not None
            self._tkobj.rowconfigure(y, weight=1)
            x = 0
            for node in row:
                if node.widget is not None:
                    if not node.widget.is_bound:
                        node.widget.bind(self)

                    assert node.widget._tkobj is not None
                    node.widget.apply_style()
                    w = cast(tk.Widget | ttk.Widget, node.widget._tkobj)
                    w.grid(row=y, column=x, columnspan=node.weight, **kwargs)

                x += node.weight
                max_columns = max(max_columns, x)

        for i in range(max_columns):
            assert self._tkobj is not None
            self._tkobj.columnconfigure(i, weight=1)


class TWidget(Widget, ABC):
    @property
    def style_key_template(self) -> str:
        return f"{{id}}.T{self._TK_CLASS.__name__}"

    def apply_ttk_style(self, **kwargs: Any) -> None:
        key = self.style_key_template.format(id=id(self))

        ttk.Style().configure(key, **kwargs)
        self.tkset(style=key)

    @abstractmethod
    def apply_style(self) -> None:
        pass


class TextWidget(DynamicWidget[str]):
    _TKVAR_CLASS = tk.StringVar
    _TKVAR_NAME = "textvariable"

    def __init__(
        self,
        text: str = "",
        *,
        style: str | None = None,
        tk_kwargs: MutableMapping[str, Any] | None = None,
        **kwargs: Any,
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


class Label(TextWidget):
    _TK_CLASS = tk.Label

    def __init__(
        self, text: str = "", *, style: str = "window", onchange: Callable[[str], Any] | None = None, **kwargs: Any
    ) -> None:
        super().__init__(text=text, value=text, style=style, onchange=onchange, **kwargs)

    @property
    def text(self) -> str:
        return cast(str, self.tkget("text"))

    @text.setter
    def text(self, text: str, /) -> None:
        self._value = text
        self.tkset(text=text)
