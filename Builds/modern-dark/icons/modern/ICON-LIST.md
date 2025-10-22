# Nova Dark Icon Checklist

Run `../scripts/generate_icon_manifest.py` against a local qBittorrent source tree if you plan to craft a bespoke icon set. For a drop-in experience that mirrors Mumble Dark, simply copy the SVGs from `Builds/mumble-theme` (or the recolored `mumble-icons` output) into this folder before running the build script.

Key controls referenced by `Nova Overrides.scss` include:

- `chevron_down.svg`
- `arrow_down.svg`
- `arrow_up.svg`

Those filenames already exist in the Mumble bundle, so copying its icons ensures everything resolves out of the box.

Example:

```powershell
python ..\scripts\generate_icon_manifest.py \
  --icon-config C:\path\to\qBittorrent\src\icons\iconconfig.json \
  --icons-root C:\path\to\qBittorrent\src\icons \
  --output ICON-LIST.md
```

After generating the list, mark completed icons by editing the Markdown checkboxes. Place the SVG files alongside this manifest before running the build scripts.
