# Nova Dark Theme for qBittorrent

A modern, carefully crafted dark theme for qBittorrent featuring a refined color palette, semantic status colors, and a custom icon set.

![Nova Dark screenshot](screenshots/nova-dark.png)

## Features

- 🎨 **Modern Dark Palette** – Deep, easy-on-the-eyes background with excellent contrast
- 🚦 **Semantic Status Colors** – Distinct colors for each torrent state (downloading, seeding, stalled, error, etc.)
- 🎯 **90+ Custom Icons** – Phosphor icon set with meaningful color coding
- ✨ **Polished UI** – Consistent styling across all widgets, dialogs, and panels

## Install

1. Download `nova-dark.qbtheme` from the [Releases](https://github.com/ehsan18t/qbt-theme/releases) page
2. In qBittorrent, go to **Tools → Options → Behavior**
3. Enable **Use custom UI Theme**
4. Browse to the downloaded `.qbtheme` file
5. Click **Apply**, then **OK**
6. Restart qBittorrent

## Build from Source

```bash
docker compose run --rm build
```

That's it. No local toolchain required, and it works the same on Windows, macOS and Linux. The image is built automatically on first run.

The result is `dist/nova-dark.qbtheme`.

## Local Build (without Docker)

The container is only a toolchain wrapper. `scripts/build.py` is the actual build, and every path runs that same file. To run it directly you need:

| Tool | What it does | Provided by |
| ---- | ------------ | ----------- |
| Python 3.8+ | Runs the build itself | [python.org](https://www.python.org/downloads/) |
| `qtsass` | Compiles the SCSS sources to Qt-flavoured QSS | `pip install qtsass` |
| `rcc` | Packs the stylesheet, icons and config into a `.qbtheme` | Qt 5 base tools |

`qtsass` is imported, not called as a command, so it does not need to be on `PATH`. Installing it for the Python you build with is enough.

### Setup

**Linux (Debian/Ubuntu)**

```bash
sudo apt install python3 python3-pip qtbase5-dev-tools
pip install qtsass
```

**macOS**

```bash
brew install qt@5
pip3 install qtsass
export PATH="$(brew --prefix qt@5)/bin:$PATH"   # puts rcc on PATH
```

**Windows**

Install [Python](https://www.python.org/downloads/), then:

```bat
py -m pip install qtsass
```

`rcc` is not on PATH by default. This repo ships `src/tools/rcc.exe`, which `make-resource.py` falls back to automatically, so nothing further is needed. To use your own Qt build instead, point `QBT_THEME_RCC` at it:

```bat
set QBT_THEME_RCC=C:\Qt\5.15.2\msvc2019_64\bin\rcc.exe
```

Then **double-click `scripts\build.bat`**. Python is the only thing it needs: no Docker, no Git Bash, no WSL. It keeps the window open so you can read any errors, and drops the result in `dist\`.

`build.bat` and `build.sh` are both thin launchers that locate a Python and hand over to `build.py`, which is the single build implementation on every platform. Neither launcher contains build logic, so there is nothing to drift: keeping a second copy in sync is what previously let the Windows path silently package a stale stylesheet.

### Build

```bat
scripts\build.bat           :: Windows, or just double-click it
```

```bash
./scripts/build.sh          # macOS, Linux
python scripts/build.py     # anywhere, if you prefer
```

The script checks its own prerequisites and tells you what is missing rather than failing halfway through. Pass `-v` to `make-resource.py` if you want the full list of embedded resources instead of a summary.

<details>
<summary>Regenerating icons</summary>

Icons come from [Phosphor](https://phosphoricons.com/) and are checked in, so a normal build never touches the network. To refetch or recolor them (needs Python 3.10+ and an internet connection):

```bash
python src/nova-dark/scripts/download_phosphor_icons.py
```

Useful flags: `--weight <thin|light|regular|bold|fill|duotone>`, `--mono` with `--color <hex>` for a single-color set.

</details>

## Status Colors

| Status            | Color      |
| ----------------- | ---------- |
| Downloading       | 🔵 Blue     |
| Uploading/Seeding | 🟢 Green    |
| Forced            | 🟠 Orange   |
| Stalled           | ⚪ Gray     |
| Queued            | 🟣 Lavender |
| Error/Missing     | 🔴 Red      |

## License

MIT License
