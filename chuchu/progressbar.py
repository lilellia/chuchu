from contextlib import suppress
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from collections.abc import Iterable, Iterator
import tkinter as tk
from threading import Thread
from tkinter import ttk
from typing import override

from chuchu.widget import TkConstructorInfo, TWidget, Widget
from chuchu.theming import active_theme
from chuchu.window import Application


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
        **kwargs
    ) -> None:
        tk_kwargs = {
            "orient": "horizontal" if horizontal else "vertical",
            "length": length,
            "mode": "determinate" if determinate else "indeterminate",
            "maximum": maximum,
            "value": value
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

    @override
    @property
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
            lightcolor=style.background
        )

    @override
    def bind(self, master: Container) -> None:
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
            return str(self.tkget("orient"))
        except KeyError:
            return "horizontal" if self.horizontal else "vertical"

    @property
    def onchange(self) -> Callable[[float], Any] | None:
        return self._onchange

    @onchange.setter
    def onchange(self, onchange: Callable[[float], Any] | None, /) -> None:
        self._onchange = onchange
        self.bind_onchange(onchange)

    def start(self, tick_ms: int = 50) -> None:
        self._tkobj.start(tick_ms)

    def stop(self) -> None:
        self._tkobj.stop()

    def step(self, amount: float = 1.0) -> None:
        if (val := self.value + amount) >= (max := self.tkget("maximum")):
            self.value = max
        else:
            self._tkobj.step(amount)

    def monitor_progress[T](self, ctx: Application, items: Iterable[T], func: Callable[[T], Any], *, total: int | None = None) -> None:
        n: int | None = None
        with suppress(TypeError):
            n = len(items)

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
