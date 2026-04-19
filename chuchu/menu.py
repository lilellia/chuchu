from __future__ import annotations
from collections.abc import Callable
import sys
import tkinter as tk
from typing import Any, Protocol, cast

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


from chuchu.theming import active_theme
from chuchu.widget import Widget, Container


class TkMenu(Protocol):
    def add_cascade(self, label: str, menu: TkMenu) -> None: ...
    def add_command(self, label: str, command: Callable[[], Any] | None) -> None: ...
    def add_separator(self) -> None: ...


class MenuBar(Widget):
    _TK_CLASS = tk.Menu

    def __init__(
        self, layout: dict[str, dict[str, Callable[[], Any] | None]], style: str = "window", **kwargs: Any
    ) -> None:
        self.layout = layout

        super().__init__(tk_kwargs={}, style=style, **kwargs)

    @override
    def bind(self, master: Container | None, **kwargs: Any) -> Any:
        if master is None:
            raise TypeError("MenuBar master cannot be None")

        if master._tkobj is None:
            raise ValueError(f"MenuBar cannot be bound to master {master!r} which is not yet bound.")

        self._tkobj = cast(TkMenu, self._TK_CLASS(master._tkobj))  # type: ignore[assignment]

        for key, sublayout in self.layout.items():
            # create a new submenu bound to this menubar
            submenu = cast(TkMenu, self._TK_CLASS(self._tkobj, tearoff=0))
            cast(TkMenu, self._tkobj).add_cascade(label=key, menu=submenu)

            # bind the individual options to this new submenu
            for subkey, command in sublayout.items():
                if command is None:
                    submenu.add_separator()
                else:
                    submenu.add_command(label=subkey, command=command)

        # attach this menubar as the menu for the parent
        master.tkset(menu=self._tkobj)

        self.apply_style()

    @override
    def apply_style(self) -> None:
        if not self.is_bound or self.style is None:
            return

        style = active_theme.get_style(self.style)

        assert self._tkobj is not None
        for tkobj in (self._tkobj, *self._tkobj.winfo_children()):
            tkobj.configure(**style.tkdict())
