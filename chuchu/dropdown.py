from collections.abc import Callable, Iterable, MutableMapping
import sys
import tkinter as tk
from typing import Any
import warnings

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


from chuchu.ltypes import TkVar
from chuchu.widget import Container, DynamicWidget


class Dropdown(DynamicWidget[str]):
    _TK_CLASS = tk.Menubutton
    _TKVAR_CLASS = tk.StringVar

    # We set _TKVAR_NAME to the empty string to bypass DynamicWidget's automatic binding of the variable
    # to the underlying tkobj. This is because tk.Menubutton doesn't support a bound variable.
    # We'll handle the variable ourselves.
    _TKVAR_NAME = ""

    _master: Container | None = None
    _options: tuple[str, ...]
    _multiselect: bool
    _blank_text: str

    # self._tkobj will be the tk.Menubutton object
    # self._tkmenu will be the child tk.Menu object that stores the options
    _tkmenu: tk.Menu | None = None

    # {option: var}
    # When multiselect=True, each key will point to a unique StringVar;
    # When multiselect=False, every will point to the same StringVar
    _varmap: dict[str, TkVar[str]]

    def __init__(
        self,
        options: Iterable[str],
        *,
        blank_text: str = "Select ▾",
        selected: Iterable[str] | None = None,
        style: str | None = None,
        multiselect: bool = False,
        tk_kwargs: MutableMapping[str, Any] | None = None,
        onchange: Callable[[str], Any] | None = None,
        **kwargs: Any,
    ) -> None:
        # initial assignments to ensure attributes are always set
        self._multiselect = False
        self._varmap = {}

        self._value = ""

        super().__init__(
            tk_kwargs=tk_kwargs,
            style=style,
            multiselect=multiselect,
            options=options,
            selected=selected or [],
            blank_text=blank_text,
            onchange=onchange,
            **kwargs,
        )

    @override
    def bind(self, master: Container | None, **kwargs: Any) -> None:
        if master is None:
            raise TypeError(f"{type(self).__name__} master cannot be None")

        if not master._tkobj:
            raise ValueError(f"Cannot bind {type(self).__name__} to a widget that has not been bound")

        # Dropdown.bind is a bit unique in that it's not expected to only be called once:
        # we'll call it again when we change between single-select and multi-select mode
        # since that requires rebuilding the child menu elements, which we have to do
        # in this method anyway.
        #
        # This is also why we store a reference to the master object, unlike the other widgets:
        # we need to be able to pass it in Dropdown.multiselect.setter and Dropdown.options.setter

        self._master = master
        self._tk_kwargs.update(kwargs)
        if not self._tkobj:
            # This is the first time we're being bound, so we can go ahead and create the tkobj
            super().bind(master, text=self.blank_text)
            assert self._tkobj is not None
            self._tkmenu = self._tkobj["menu"] = tk.Menu(self._tkobj, tearoff=0)
            self._protected_onchange_cb = {}
        else:
            # We already have the elements instantiated, so we just need to reconfigure them
            # In this case, we'll remove all of the elements from the menu since we're about to rebuild them
            assert self._tkmenu is not None
            self._tkmenu.delete(0, tk.END)
            self._varmap.clear()

            # We also need to unbind the update-button-text trace
            assert self._protected_onchange_cb is not None
            for cb_name, var in self._protected_onchange_cb.items():
                var.trace_remove("write", cb_name)

            self._protected_onchange_cb.clear()

        # We'll need a function to automatically bind the selected options as the button text.
        def _update(*_: str) -> None:
            # Force-update self._var/self._value and trigger the onchange.
            if self._var:
                self._var.set(self.value)

            self._value = self.value
            self.tkset(text=self.value)

        # Add all of the options to the menu
        if self.multiselect:
            for opt in self.options:
                # We'll use StringVar with "0" or "1" just because it means we don't need to use IntVar in this case
                var = self._varmap[opt] = tk.StringVar(self._tkmenu, "0")
                self._tkmenu.add_checkbutton(label=opt, variable=var, offvalue="0", onvalue="1")

                cbname = var.trace_add("write", _update)
                self._protected_onchange_cb[cbname] = var
        else:
            var = tk.StringVar(self._tkmenu, "")
            cbname = var.trace_add("write", _update)
            for opt in self.options:
                self._varmap[opt] = var
                self._tkmenu.add_radiobutton(label=opt, variable=var, value=opt)

        self.tkset(**self._tk_kwargs)

    @property
    def multiselect(self) -> bool:
        return self._multiselect

    @multiselect.setter
    def multiselect(self, flag: bool, /) -> None:
        if not isinstance(flag, bool):
            raise TypeError(f"{type(self).__name__}.multiselect must be a boolean, not {flag!r}")

        if flag == self._multiselect:
            # we don't need to do anything since the state is already correct
            return

        self._multiselect = flag

        if self._tkobj:
            # We're already bound, so we can just rebind and that'll correct all of the options.
            self.bind(self._master)
        else:
            # We don't actually have any of the tkinter stuff set up yet,
            # so it doesn't really matter that we're changing the selection mode.
            # All we need to do is change the _multiselect flag, which we've already done.
            pass

    @property
    def _first_tk_var(self) -> TkVar[str] | None:
        vars = iter(self._varmap.values())
        return next(vars, None)

    @property
    def blank_text(self) -> str:
        return self._blank_text

    @blank_text.setter
    def blank_text(self, value: str) -> None:
        self._blank_text = value

        if not self.selected:
            self.tkset(text=value)

    @property
    def selected(self) -> tuple[str, ...]:
        if self.multiselect:
            # We'll return any option whose variable is set (== "1")
            return tuple(opt for opt, var in self._varmap.items() if var.get() == "1")

        if (var := self._first_tk_var) is not None:
            # This weird next(iter(...), None) is just a safety in case there aren't any options.
            # If any options exist, there's only one var object since this is the select-one situation,
            # so we'll just return whatever option it's pointing to.

            if s := var.get():
                # One option is selected
                return (s,)
            else:
                # No option is selected
                return ()

        # select-one but no options exist
        return ()

    @selected.setter
    def selected(self, selected: Iterable[str], /) -> None:
        selected = set(selected)
        options = set(self.options)

        if invalid := set.difference(selected, options):
            raise ValueError(f"Cannot select {', '.join(invalid)!r} as these are not valid options.")

        if self.multiselect:
            for opt, var in self._varmap.items():
                var.set("1" if opt in selected else "0")
        else:
            if len(selected) > 1:
                raise ValueError("Cannot select multiple options for a select-one dropdown.")

            if (var := self._first_tk_var) is not None:
                # We know that `selected` only has at most one element, so we can safely .pop() to get it uniquely.
                var.set(selected.pop() if selected else "")

    @property
    @override
    def value(self) -> str:
        return self._parse_value()

    def _parse_value(self) -> str:
        if self.multiselect:
            return ", ".join(self.selected) or ""
        else:
            return self.selected[0] if self.selected else ""

    def _set_value(self, value: str, /, warn: bool = False, set_selected: bool = False) -> None:
        if warn and (have_commas := [opt for opt in self.options if "," in opt]):
            msg = (
                f"Options {have_commas} have commas, so setting Dropdown.value may not work as expected. "
                "Use Dropdown.selected = ... instead."
            )
            warnings.warn(msg, RuntimeWarning)

        # Update the selection as well as we can.
        if set_selected:
            self.selected = value.split(", ")

        # And update the internal variable to point to the correct string
        self._value = self._parse_value()

        if self._var:
            self._var.set(self._value)

    @value.setter
    @override
    def value(self, value: str, /) -> None:
        # This gets a bit hard since what you *really* want to be setting is Dropdown.selected.
        # dropdown.value should be a string, but we need to parse it out to be a list of options.
        # If any of the individual options contain commas, then this isn't reliable.
        # Just... feel free to *read* Dropdown.value, but *set* Dropdown.selected.
        # Dropdown.value.setter is provided purely for compliance with the DynamicWidget interface.
        self._set_value(value, warn=True, set_selected=True)

    @property
    def options(self) -> tuple[str, ...]:
        return self._options

    @options.setter
    def options(self, options: Iterable[str], /) -> None:
        self._options = tuple(str(opt) for opt in options)

        if self._tkobj:
            # We're already bound, so we can just rebind and that'll correct all of the options.
            self.bind(self._master)
        else:
            # We don't actually have any of the tkinter stuff set up yet,
            # so it doesn't really matter that we're changing the internal list of options,
            # which we've already done.
            pass
