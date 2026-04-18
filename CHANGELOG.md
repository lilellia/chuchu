# CHANGELOG

## v0.1.1

- Added widgets:
  - `Checkbox`
  - `MenuBar`, accessible via `Application().set_menubar`.
  - `StatusBar`, accessible via `Application().status = ...`.
- Add `Container.form`, allowing easy construction of a Nx2 grid of Label+Widget.
- Add `Container.__getitem__`, allowing access to elements posted by `Container.form`.
- `Container.grid` and `Container.add_row` now return the widget array passed into them.
- `TextWidget` now implements `.value` as an alias for `.text` to better align with other widgets.
- `theming.Style` now takes `active_background` and `active_foreground` fields (instead of just `active` in place of `active_background`).
- `theming.Style` now also provides `.tkdict() -> dict[str, str]` to allow for `widget.tkset(**style.tkdict())`.

## v0.1.0

- Initial release.
