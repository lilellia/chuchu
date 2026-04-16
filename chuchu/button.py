from functools import wraps
import tkinter as tk

from chuchu.widget import TextWidget


class Button[T](TextWidget):
    _TK_CLASS = tk.Button

    def __init__(self, text: str = "", *, onclick: Callable[[], T] | None = None, **kwargs) -> None:
        self._onclick_return_value = None

        if onclick:
            @wraps(onclick)
            def wrapper() -> T:
                res = self._onclick_return_value = onclick()
                return res

            tk_kwargs = dict(command=wrapper)
        else:
            tk_kwargs = None

        super().__init__(text=text, onclick=onclick, tk_kwargs=tk_kwargs, **kwargs)

    def click(self) -> T:
        if self.onclick:
            self._tkobj.invoke()
            return self._onclick_return_value

        # in the case where self.onclick is None, T should be None
        return None
