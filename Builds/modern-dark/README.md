# Nova Dark Theme

Nova Dark ships a refreshed color story on top of the battle-tested Mumble dark stylesheet. By importing `mumble-theme`'s base rules we inherit the exact same spacing, padding, focus rings, and widget geometry while swapping in a new palette and transfer-state colors.

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
    ModernDark.scss         # imports Nova Definitions + Mumble Base Theme
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

If you want the Nova theme to look identical to Mumble Dark, copy the SVG set from `Builds/mumble-theme` (or rerun the original recolor pipeline) into `icons/modern` before building. The optional `scripts/generate_icon_manifest.py` can still produce a checklist from qBittorrent's `iconconfig.json` if you plan to curate a brand-new icon pack.

> Tip: Because Nova reuses the base stylesheet, keeping the icon filenames identical to Mumble's guarantees all lookups resolve without further tweaks.
