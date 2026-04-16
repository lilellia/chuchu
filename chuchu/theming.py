import colorsys
from dataclasses import dataclass
from typing import TypedDict, Self


def hsl(hue: float, saturation: float, lightness: float) -> str:
    """Convert the given HSL color to hex. 0 <= hue < 360 and 0 <= saturation, lightness < 1."""
    r, g, b = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
    return f"#{round(255*r):02X}{round(255*g):02X}{round(255*b):02X}"


@dataclass
class Style:
    background: str
    active: str
    foreground: str
    relief: Literal["flat", "raised"]


@dataclass
class Theme:
    name: str
    window: Style
    primary: Style
    secondary: Style

    def get_style(self, key: str) -> Style:
        return getattr(self, key)


THEMES = {
    "default": Theme(
        name="default",
        window=Style(
            foreground="#a0a0a0",
            active="#000000",
            background="#101010",
            relief="flat"
        ),
        primary=Style(
            foreground="#000000",
            background=hsl(200, 1.0, 0.5),
            active=hsl(200, 1.0, 0.3),
            relief="flat",
        ),
        secondary=Style(
            foreground="#000000",
            background=hsl(60, 1.0, 0.5),
            active=hsl(60, 1.0, 0.3),
            relief="flat",
        )
    )
}


def get_theme(name: str) -> Theme:
    if (t := THEMES.get(name, None)):
        return t

    raise ValueError(f"Unknown theme name {name!r}")


active_theme: Theme = get_theme("default")
