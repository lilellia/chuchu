from collections.abc import Callable
import sys
import tkinter as tk
from tkinter import ttk
from typing import Any, Literal, NamedTuple, Protocol, TypeAlias, TypeVar

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


T = TypeVar("T", str, float, int, bool)


class Size(NamedTuple):
    width: int
    height: int


class Position(NamedTuple):
    x: int
    y: int


TkWidget: TypeAlias = tk.Tk | tk.Widget | ttk.Widget

TkTraceMode: TypeAlias = Literal["array", "read", "write", "unset"]
TkTraceFunc: TypeAlias = Callable[[str, str, str], None]
TkTraceInfo: TypeAlias = tuple[tuple[TkTraceMode, ...], str]


class TypeTkWidget(Protocol):
    __name__: str

    def __call__(self, master: TkWidget | None = None, *args: Any, **kwargs: Any) -> TkWidget: ...


class Tk(tk.Tk):
    def __init__(self, master: TkWidget | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class TkVar(Protocol[T]):
    def __init__(self, master: TkWidget, value: T) -> None: ...

    def get(self) -> T: ...
    def set(self, value: T) -> None: ...

    def trace_add(self, mode: TkTraceMode, callback: TkTraceFunc) -> str: ...
    def trace_remove(self, mode: TkTraceMode, cbname: str) -> None: ...
    def trace_info(self) -> list[TkTraceInfo]: ...


class BoolVar(tk.Variable):
    @override
    def get(self) -> bool:
        v = super().get()  # type: ignore[no-untyped-call]
        return bool(v)

    @override
    def set(self, value: bool) -> None:
        super().set(value)
