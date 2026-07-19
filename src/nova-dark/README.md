# Nova Dark Theme

A modern, carefully crafted dark theme for qBittorrent featuring a refined color palette, semantic status colors, and a custom icon set built with Phosphor Icons.

## Features

- **Modern Dark Palette** – Deep, easy-on-the-eyes background with excellent contrast
- **Semantic Status Colors** – Distinct, meaningful colors for each torrent state:
  - Blue for downloading
  - Green for uploading/seeding
  - Orange for forced transfers
  - Gray for stopped/stalled
  - Red for errors
- **Custom Icon Set** – 90+ carefully colored Phosphor icons
- **Consistent UI** – Polished look across all widgets, dialogs, and panels

## Project Structure

```
nova-dark/
├── nova-dark-config.json      # GENERATED from _palette.scss - do not hand-edit
├── NovaDark.qss               # Compiled stylesheet (generated)
├── icons/
│   └── modern/                # Custom Phosphor icon set
│       └── icon-manifest.json # Icon color definitions
├── scripts/
│   ├── download_phosphor_icons.py  # Icon generator
│   └── generate-config.py          # Builds nova-dark-config.json
└── source/
    ├── NovaDark.scss          # Entry point; imports the three layers below
    ├── _palette.scss          # Primitive colours - the ONLY hex literals
    ├── _tokens.scss           # Semantic roles mapped onto primitives
    └── _widgets.scss          # Widget rules, referring to names
```

## Colour

Every colour originates in `source/_palette.scss`. The build fails if a hex
literal appears anywhere else.

qBittorrent paints two different ways, and a theme has to satisfy both:

| Consumer | Source | Covers |
| -------- | ------ | ------ |
| Stylesheet (QSS) | `_palette.scss` → `_tokens.scss` → `_widgets.scss` | widgets with an explicit rule |
| qBittorrent itself | `nova-dark-config.json` | QPalette fallback, transfer-list states, log levels, pieces bar |

QSS cannot reference a `config.json` colour — different consumers, different
parse paths — so those values must be duplicated. `scripts/generate-config.py`
is what keeps the duplicate honest: it derives all 56 config keys from the
palette using a mapping, and the build regenerates it every time. Edit the
palette, not the JSON.

```bash
python scripts/generate-config.py           # regenerate
python scripts/generate-config.py --check   # exit 1 if stale (CI)
```

## Build

### Using Docker (Recommended)

```bash
docker build -t qbt-theme-builder .
docker run --rm -v "${PWD}:/workspace" qbt-theme-builder
```

### Manual Build

Run from the repository root:
- **Windows:** `scripts\build-nova-dark.bat`
- **Linux/macOS:** `./scripts/build-nova-dark.sh`

### Output

Two theme variants are generated in `dist/`:
- `nova-dark-modern.qbtheme` – Full theme with custom icons
- `nova-dark-no-icons.qbtheme` – Stylesheet only (uses qBittorrent's default icons)

## Regenerating Icons

To regenerate the icon set with custom colors:

```bash
cd src/nova-dark/scripts
python download_phosphor_icons.py
```

The script downloads Phosphor icons and applies the color palette defined in the script. Edit `COLORS` and `ICON_MAPPING` to customize.

## Status Text Colors

| Status        | Color     | Hex       |
| ------------- | --------- | --------- |
| Downloading   | Blue      | `#5cb8ff` |
| Uploading     | Green     | `#50e0a0` |
| Forced        | Orange    | `#ffb86c` |
| Stalled       | Gray      | `#8899aa` |
| Stopped       | Dark Gray | `#707888` |
| Queued        | Lavender  | `#b8a0d8` |
| Moving        | Gold      | `#e0c060` |
| Error         | Red       | `#ff5555` |
| Missing Files | Red       | `#f87171` |

## License

MIT License
