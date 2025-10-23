# Nova Dark Theme for qBittorrent

Nova Dark refreshes qBittorrent’s interface with a Catppuccin-inspired palette while keeping widget geometry and behavior consistent with the original Mumble-derived base theme. All source files for Nova live under `src/nova-dark`, and the shared scaffolding resides in `src/common`.

![Nova Dark screenshot](screenshots/nova-dark.png)

## Install

1. Download the Nova `.qbtheme` archive you prefer from `dist/` (either the version with icons or without).
2. In **qBittorrent**, open *Tools → Options → Behavior* and enable **Use custom UI Theme**.
3. Browse to the downloaded `.qbtheme` file, click **Apply**, then **OK**.
4. Restart qBittorrent to load the new styling.

## Build Nova

You can rebuild the theme locally while iterating on colors or icons:

- Copy the desired SVG icons into `src/nova-dark/icons/modern/` (optional if you prefer stock icons).
- Run `scripts\build-nova-dark.bat` on Windows or `./scripts/build-nova-dark.sh` on macOS/Linux.

The scripts emit two artifacts in `dist/`:

- `nova-dark-modern.qbtheme` – includes the custom icon set.
- `nova-dark-no-icons.qbtheme` – ships only the stylesheet and palette configuration.

### Using Docker (optional)

If Docker is available, you can build without installing the native toolchain:

- `docker build -t qbt-theme-builder .`
- `docker run --rm -e THEME_BUILD_SCRIPT=build-nova-dark.sh -v ${PWD}:/workspace qbt-theme-builder`

The container mounts the repository, runs the Nova build script, and drops the resulting `.qbtheme` archives into `dist/` on the host.
