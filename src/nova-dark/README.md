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
├── nova-dark-config.json      # Color palette configuration
├── NovaDark.qss               # Compiled stylesheet
├── icons/
│   └── modern/                # Custom Phosphor icon set
│       └── icon-manifest.json # Icon color definitions
├── scripts/
│   └── download_phosphor_icons.py  # Icon generator script
└── source/
    ├── NovaDark.scss          # Main stylesheet source
    └── Imports/
        ├── Nova Definitions.scss   # Color variables
        └── Nova Overrides.scss     # Custom overrides
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
