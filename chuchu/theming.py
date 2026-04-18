import colorsys
from dataclasses import dataclass
from typing import Any, Literal, cast


def hsl(hue: float, saturation: float, lightness: float) -> str:
    """Convert the given HSL color to hex. 0 <= hue < 360 and 0 <= saturation, lightness < 1."""
    r, g, b = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
    return f"#{round(255 * r):02X}{round(255 * g):02X}{round(255 * b):02X}"


@dataclass
class Style:
    background: str
    foreground: str
    active_background: str
    active_foreground: str
    relief: Literal["flat", "raised"]

    def tkdict(self) -> dict[str, Any]:
        return dict(
            bg=self.background,
            fg=self.foreground,
            activebackground=self.active_background,
            activeforeground=self.active_foreground,
            border=0,
            relief=self.relief,
        )


@dataclass
class Theme:
    name: str
    window: Style
    primary: Style
    secondary: Style

    def get_style(self, key: str) -> Style:
        return cast(Style, getattr(self, key))


THEMES = {
    "default": Theme(
        name="default",
        window=Style(
            foreground="#a0a0a0",
            background="#101010",
            active_background="#080808",
            active_foreground="#a0a0a0",
            relief="flat"
        ),
        primary=Style(
            foreground="#000000",
            background=hsl(200, 1.0, 0.5),
            active_background=hsl(200, 1.0, 0.3),
            active_foreground="#000000",
            relief="flat",
        ),
        secondary=Style(
            foreground="#000000",
            background=hsl(60, 1.0, 0.5),
            active_background=hsl(60, 1.0, 0.3),
            active_foreground="#000000",
            relief="flat",
        ),
    )
}


def get_theme(name: str) -> Theme:
    if t := THEMES.get(name, None):
        return t

    raise ValueError(f"Unknown theme name {name!r}")


active_theme: Theme = get_theme("default")
