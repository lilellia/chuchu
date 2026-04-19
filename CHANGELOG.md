# CHANGELOG

## v0.2.5

- Reverts `TextWidget` move and instead moves `Label` into `widget.py`.

## v0.2.4

- Re-adds `onchange` support to `Button`.
- Fixes import cycling by moving `TextWidget` to its own file.

## v0.2.3

- Attempts to fix import cycling.

## v0.2.2

- Correctly exports Dropdown and Frame.

## v0.2.1

- Fixes `* > TextWidget > DynamicWidget` inheritance.

## v0.2.0

- Adds widgets:
    - `Checkbox`
    - `Dropdown`, capable of single-select or multi-select
    - `Frame`
    - `MenuBar`, accessible via `Application().set_menubar`.
    - `StatusBar`, accessible via `Application().status = ...`.
- Adds `Widget.defer_set` as an alias of `lambda: w.tkset(**kwargs)`.
- Adds `Container.form`, allowing easy construction of a Nx2 grid of Label+Widget.
- Adds `Container.__getitem__`, allowing access to elements posted by `Container.form`.
- `Container.grid` and `Container.add_row` now return the widget array passed into them.
- Adds `DynamicWidget` middlelayer to implement uniform interface for any widget that contains a tk variable.
- `theming.Style` now takes `active_background` and `active_foreground` fields (instead of just `active` in place of `active_background`).
- `theming.Style` now also provides `.tkdict() -> dict[str, str]` to allow for `widget.tkset(**style.tkdict())`.
- `Widget.tkset` now continues to update `self._tk_kwargs` to allow objects (`Dropdown`) to be bound multiple times while continuing to inherit the correct settings.

## v0.1.0

- Initial release.
