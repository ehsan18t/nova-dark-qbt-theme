# Shared Assets

This folder collects resources that are shared across theme variants:

- `styles/BaseTheme.scss` – the common geometry/spacing rules for qBittorrent widgets.
- `controls/` – accent-tinted UI glyphs (checkboxes, radios, tree toggles, toolbar overflow, splitter handles, etc.) that the base stylesheet references.

Keep palette tokens and theme-specific overrides in the individual theme folders. Update this location when you need to tweak behaviour that should stay consistent across themes.
