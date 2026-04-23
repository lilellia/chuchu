# CHANGELOG

## 0.3.2

- Fixes `Slider.onchange`.

## 0.3.0

- Adds `ImageWidget`.

## v0.2.\*

- Allow `DynamicWidget[T]` to skip binding the underlying `tk.Variable` (v0.2.9).
- Corrects update logic for `Dropdown` (v0.2.13).
- Corrects access of `Dropdown._onchange` (v0.2.10), `Dropdown._varmap` (v0.2.8), `Dropdown.multiselect` (v0.2.6)
- `Dropdown.__init__` now takes `selected: Iterable[str] | None = None` instead of `value: str = ""` (v0.2.7).
- Re-adds `onchange` support on `Button` (v0.2.4).
- Fixes import cycling between `Container` and `Label` (v0.2.5).
- Fixes `* > TextWidget > DynamicWidget` inheritance (v0.2.1).
- Correctly exports `Dropdown` and `Frame` (v0.2.2).
- Corrects default themes for `Dropdown` and `Slider` (v0.2.11).

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
