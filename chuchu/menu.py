from collections.abc import Callable
import tkinter as tk
from typing import Any, override

from chuchu.theming import active_theme
from chuchu.widget import Widget, Container, TkConstructorInfo

class MenuBar(Widget):
    _TK_CLASS = tk.Menu

    def __init__(
        self,
        layout: dict[str, dict[str, Callable[[], Any]] | None],
        style: str = "window",
        **kwargs: Any
    ) -> None:
        self.layout = layout

        # this largely gets ignored since MenuBar.bind's override
        # handles the construction on its own rather than deferring
        info = TkConstructorInfo(cls=self._TK_CLASS, kwargs={})

        super().__init__(constructor_info=info, style=style, **kwargs)

    @override
    def bind(self, master: Container | None, **kwargs: Any) -> Any:
        if master is None:
            raise ValueError("MenuBar master cannot be None")

        self._tkobj = self._TK_CLASS(master._tkobj)

        for key, sublayout in self.layout.items():
            # create a new submenu bound to this menubar
            submenu = self._TK_CLASS(self._tkobj, tearoff=0)
            self._tkobj.add_cascade(label=key, menu=submenu)

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

        for tkobj in (self._tkobj, *self._tkobj.winfo_children()):
            tkobj.configure(**style.tkdict())
