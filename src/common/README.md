# Shared Assets

This folder collects resources that are reused by multiple themes:

- `styles/BaseTheme.scss` – the common geometry/spacing rules originally shipped with the Mumble theme.
- `controls/` – accent-tinted UI glyphs (checkboxes, radios, tree toggles, toolbar overflow, splitter handles, etc.) that the base stylesheet references.

Keep palette tokens and theme-specific overrides in the individual theme folders. Update this location when you need to tweak behaviour that should stay consistent across themes.
