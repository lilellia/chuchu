from collections.abc import Callable, Iterable
from contextlib import suppress
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import tkinter as tk
from threading import Thread
from tkinter import ttk
from typing import Any, Literal, TypeVar, cast

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


from chuchu.widget import TkConstructorInfo, TWidget, Widget, Container
from chuchu.theming import active_theme
from chuchu.window import Application


T = TypeVar("T")


class ProgressBar(Widget, TWidget):
    _TK_CLASS = ttk.Progressbar

    def __init__(
        self,
        *,
        horizontal: bool = True,
        length: float = 100.0,
        determinate: bool = True,
        maximum: float = 100.0,
        value: float = 0.0,
        style: str = "primary",
        onchange: Callable[[float], Any] | None = None,
        **kwargs: Any,
    ) -> None:
        tk_kwargs = {
            "orient": "horizontal" if horizontal else "vertical",
            "length": length,
            "mode": "determinate" if determinate else "indeterminate",
            "maximum": maximum,
            "value": value,
        }

        kwargs = {
            "horizontal": horizontal,
            "length": length,
            "determinate": determinate,
            "maximum": maximum,
            "value": value,
            "style": style,
            "onchange": onchange,
        }

        info = TkConstructorInfo(cls=self._TK_CLASS, kwargs=tk_kwargs)
        super().__init__(constructor_info=info, **kwargs)
        self._value = value

    @property
    @override
    def style_key_template(self) -> str:
        return f"{{id}}.{self.orientation.capitalize()}.TProgressbar"

    @override
    def apply_style(self) -> None:
        if not self.is_bound or self.style is None:
            return

        style = active_theme.get_style(self.style)

        self.apply_ttk_style(
            background=style.background,
            troughcolor=active_theme.window.background,
            bordercolor=active_theme.window.background,
            darkcolor=style.background,
            lightcolor=style.background,
        )

    @override
    def bind(self, master: Container | None, **kwargs: Any) -> None:
        if master is None:
            raise ValueError("ProgressBar master cannot be None")
        self._var = tk.DoubleVar(master._tkobj)
        super().bind(master, variable=self._var)
        if self.onchange:
            self.bind_onchange(self.onchange)

    @property
    def value(self) -> float:
        if self.is_bound:
            return self._var.get()

        return self._value

    @value.setter
    def value(self, value: float) -> None:
        if self.is_bound:
            self._var.set(value)

        self._value = value

    @property
    def orientation(self) -> Literal["horizontal", "vertical"]:
        try:
            return cast(Literal["horizontal", "vertical"], str(self.tkget("orient")))
        except KeyError:
            return "horizontal" if self.horizontal else "vertical"  # type: ignore[attr-defined]

    @property
    def onchange(self) -> Callable[[float], Any] | None:
        return self._onchange

    @onchange.setter
    def onchange(self, onchange: Callable[[float], Any] | None, /) -> None:
        self._onchange = onchange
        if onchange:
            self.bind_onchange(onchange)

    def start(self, tick_ms: int = 50) -> None:
        if not self.is_bound:
            raise RuntimeError("Cannot start progress bar until it's been rendered")

        cast(ttk.Progressbar, self._tkobj).start(tick_ms)

    def stop(self) -> None:
        if not self.is_bound:
            raise RuntimeError("Cannot stop progress bar until it's been rendered")

        cast(ttk.Progressbar, self._tkobj).stop()

    def step(self, amount: float = 1.0) -> None:
        if self.value + amount >= (max := self.tkget("maximum")):
            self.value = max
        else:
            self.value += amount

    def monitor_progress(
        self, ctx: Application, items: Iterable[T], func: Callable[[T], Any], *, total: int | None = None
    ) -> None:
        n: int | None = None
        with suppress(TypeError):
            n = len(items)  # type: ignore[arg-type]

        if total is not None:
            n = total

        if n is None:
            self.tkset(mode="indeterminate")
            self.determinate = False
        else:
            self.tkset(mode="determinate", maximum=n)
            self.determinate = True

        def worker(item: T) -> None:
            func(item)
            ctx.dispatch(self.step, 1)

        def consumer(items: Iterable[T]) -> None:
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(worker, item) for item in items]

                for future in as_completed(futures):
                    pass

        t = Thread(target=consumer, args=(items,), daemon=True)
        t.start()
