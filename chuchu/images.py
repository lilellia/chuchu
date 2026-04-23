from collections.abc import MutableMapping
from os import PathLike
from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk
from typing import Any

from chuchu.ltypes import Size
from chuchu.widget import Widget


class ImageWidget(Widget):
    _TK_CLASS = tk.Label

    _image_path: Path
    _image: Image.Image
    _image_tk: ImageTk.PhotoImage
    _size: Size

    def __init__(
        self,
        image_path: PathLike[str],
        *,
        size: tuple[int, int] | None = None,
        style: str | None = None,
        tk_kwargs: MutableMapping[str, Any] | None = None,
        **kwargs: Any
    ) -> None:


        super().__init__(style=style, tk_kwargs=tk_kwargs, image_path=image_path, **kwargs)

    @property
    def image_path(self) -> Path:
        return self._image_path

    @image_path.setter
    def image_path(self, value: PathLike[str]) -> None:
        self._set_image(value, size=None)

    def _set_image(self, image_path: PathLike[str], size: tuple[int, int] | None = None) -> None:
        self._image_path = Path(image_path)

        # open the image
        self._image = Image.open(self._image_path)

        if size:
            self._image = self._image.resize(size)

        self._image_tk = ImageTk.PhotoImage(self._image)
        self.tkset(image=self._image_tk)

    @property
    def size(self) -> Size:
        return Size(*self._image.size)

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        self._set_image(self._image_path, size=value)
