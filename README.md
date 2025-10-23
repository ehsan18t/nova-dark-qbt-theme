# How to use

1. Download the `.qbtheme` file of your taste. We recommend you download it in a **qBittorrent Themes** folder, but it is not mandatory.
2. Open **qBittorrent**, then go to *Tools -> Options* and click on the box next to *Use custom UI Theme*.
3. Right below that, browse to the path where you previously downloaded the `.qbtheme` file. Click **Apply** and then **OK**.
4. Restart **qBittorrent**. (Close it and then open it again).

# Screenshots
## Darkstylesheet.qbtheme
![darkstylesheet.qbtheme](screenshots/darkstylesheet.JPG)
## Mumble-Dark.qbtheme
![mumble-dark.qbtheme](screenshots/mumble-dark.JPG)
## Mumble-Lite.qbtheme
![mumble-lite.qbtheme](screenshots/mumble-lite.JPG)
## Breeze-Dark.qbtheme
![mumble-lite.qbtheme](screenshots/breeze-dark.JPG)
## Nova-Dark.qbtheme *(coming soon)*
Nova now layers a new palette on top of a shared base stylesheet (`Builds/common/styles/BaseTheme.scss`) extracted from the Mumble theme. Geometry, spacing, and focus behavior stay identical to Mumble Dark while colors and transfer-state accents are refreshed. Assets live under `Builds/modern-dark`, with shared controls/icons in `Builds/common`.

This repo contains different stylesheed edited to run with qbittorrent's style system  
DarkStyleSheet theme is based on https://github.com/ColinDuquesnoy/QDarkStyleSheet  
Mumble themes are based on https://github.com/mumble-voip/mumble-theme  
Breeze themes are based on https://github.com/Alexhuszagh/BreezeStyleSheets  
Icons used in dark themes are from nowshed-imran. They are meant to be icons for next qbittorrent major release (https://github.com/qbittorrent/qBittorrent/pull/12965). Do give your opinions on the thread :)


## How to create your own theme file?
This repo also contains different tool to create your own qbittorrent theme files.
You can check the source of above style in `Builds` folder

## Build With Docker

If you have Docker installed you can compile every theme without setting up the native toolchain:

- `docker build -t qbt-theme-builder .`
- `docker run --rm -v ${PWD}:/workspace qbt-theme-builder`

The container binds the whole repository, so changes to the source are picked up immediately. Every build script listed below runs in order, and the generated `.qbtheme` files land in `Builds/dist` on your host.

Need just one theme? Override the entrypoint target, for example:

- `docker run --rm -e THEME_BUILD_SCRIPT=build-modern-dark.sh -v ${PWD}:/workspace qbt-theme-builder`

## Build the Nova Dark theme locally

To build Nova, copy the Mumble dark SVG icon set (or your replacement artwork) into `Builds/modern-dark/icons/modern`, then run one of:

- `Builds\build-modern-dark.bat`
- `./Builds/build-modern-dark.sh`

The build will emit two archives in `Builds/dist`:

- `nova-dark-modern.qbtheme` – includes the icons sitting in `icons/modern`
- `nova-dark-no-icons.qbtheme` – ships only the stylesheet and configuration, allowing qBittorrent's stock icons to remain in place

> Tip: Use `THEME_BUILD_SCRIPT=build-modern-dark.sh` with the command above to rebuild Nova repeatedly while iterating on icons or palette tweaks; the same container can run any of the other build scripts (see `Builds/build-all.sh`).
