# Nova Dark Theme

Nova Dark ships a refreshed color story on top of a shared base stylesheet (`Builds/common/styles/BaseTheme.scss`) that was extracted from the original Mumble dark theme. The common layer preserves widget geometry, spacing, focus rings, and behaviour while Nova swaps in a new palette and transfer-state colors.

## Layout

```
modern-dark/
  README.md
  modern-dark-config.json   # qB palette used by the application chrome
  icons/
    modern/                 # drop SVG icons here (defaults to Mumble's set)
  scripts/
    generate_icon_manifest.py
  source/
  ModernDark.scss         # imports Nova Definitions + shared BaseTheme
    Imports/
      Nova Definitions.scss # palette values consumed by the base stylesheet
      Nova Overrides.scss   # qproperty/QPalette tweaks layered on top
```

## Build Steps

Run the helper scripts from `Builds/`:

- `../build-modern-dark.bat`
- `../build-modern-dark.sh`

Each script compiles `ModernDark.scss`, then packages two variants into `Builds/dist`:

- `nova-dark-modern.qbtheme` – includes whatever icons live in `icons/modern`
- `nova-dark-no-icons.qbtheme` – relies on qBittorrent's stock icons

## Icons

If you want the Nova theme to look identical to Mumble Dark, copy the SVG set from `Builds/mumble-theme` (or rerun the original recolor pipeline) into `icons/modern` before building. The shared controls (checkboxes, radios, tree toggles, etc.) live in `Builds/common/controls` and already use Nova's accent hue.

> Tip: Because Nova reuses the base stylesheet, keeping the icon filenames identical to Mumble's guarantees all lookups resolve without further tweaks.
