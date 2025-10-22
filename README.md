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
Nova now layers a new palette on top of the Mumble base stylesheet. Geometry, spacing, and focus behavior are identical to Mumble Dark, while colors and transfer-state accents are refreshed. Assets live under `Builds/modern-dark`.

This repo contains different stylesheed edited to run with qbittorrent's style system  
DarkStyleSheet theme is based on https://github.com/ColinDuquesnoy/QDarkStyleSheet  
Mumble themes are based on https://github.com/mumble-voip/mumble-theme  
Breeze themes are based on https://github.com/Alexhuszagh/BreezeStyleSheets  
Icons used in dark themes are from nowshed-imran. They are meant to be icons for next qbittorrent major release (https://github.com/qbittorrent/qBittorrent/pull/12965). Do give your opinions on the thread :)


## How to create your own theme file?
This repo also contains different tool to create your own qbittorrent theme files.
You can check the source of above style in `Builds` folder

## Build With Docker

If you have Docker installed you can compile the Mumble Dark theme without setting up the native toolchain:

- `docker build -t qbt-theme-builder .`
- `docker run --rm -v ${PWD}/Builds/dist:/workspace/Builds/dist qbt-theme-builder`

The generated `.qbtheme` files will appear in `Builds/dist`.

## Build the Nova Dark theme locally

To build Nova, copy the Mumble dark SVG icon set (or your replacement artwork) into `Builds/modern-dark/icons/modern`, then run one of:

- `Builds\build-modern-dark.bat`
- `./Builds/build-modern-dark.sh`

The build will emit two archives in `Builds/dist`:

- `nova-dark-modern.qbtheme` – includes the icons sitting in `icons/modern`
- `nova-dark-no-icons.qbtheme` – ships only the stylesheet and configuration, allowing qBittorrent's stock icons to remain in place

> Tip: A dedicated Dockerfile lives at `Builds/modern-dark/Dockerfile`. Build it with `docker build -t nova-dark-builder -f Builds/modern-dark/Dockerfile .`, then run `docker run --rm -v ${PWD}/Builds/dist:/workspace/Builds/dist nova-dark-builder` to generate the theme archives. Mount `Builds/modern-dark/icons/modern` so your copied Mumble icons (or custom set) are packaged.
