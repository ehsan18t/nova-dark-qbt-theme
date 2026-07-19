#!/usr/bin/env python3
"""Build the Nova Dark qBittorrent theme into dist/nova-dark.qbtheme.

This is the only build implementation, and it runs natively everywhere: Windows
(cmd, PowerShell, or double-clicking scripts\\build.bat), macOS, Linux, and the
container defined by the Dockerfile.

It is written in Python rather than shell because Python was never optional --
make-resource.py and generate-config.py *are* the build, and the toolchain image
is python:3.11-slim. A shell script made Windows depend on Git Bash for nothing,
and the alternative, a .bat that reimplemented the build, is precisely what let
the Windows path silently package a stale stylesheet for as long as it did.

build.sh and build.bat are both thin launchers for this file. Add logic here.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
THEME_ROOT = SRC_ROOT / "nova-dark"
SOURCE_DIR = THEME_ROOT / "source"
ICONS_DIR = THEME_ROOT / "icons" / "modern"
COMMON_DIR = SRC_ROOT / "common"
CONFIG_FILE = THEME_ROOT / "nova-dark-config.json"
STYLESHEET = THEME_ROOT / "NovaDark.qss"
OUTPUT = DIST_DIR / "nova-dark"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _supports_colour() -> bool:
    if not sys.stdout.isatty():
        return False
    if os.name != "nt":
        return True
    # Windows consoles need VT processing turned on explicitly; without this
    # the escape codes are printed literally, which is worse than no colour.
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        return bool(kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7))
    except Exception:
        return False


if _supports_colour():
    BLUE, YELLOW, RED, GREEN, NC = (
        "\033[0;34m", "\033[0;33m", "\033[0;31m", "\033[0;32m", "\033[0m",
    )
else:
    BLUE = YELLOW = RED = GREEN = NC = ""


# flush=True throughout: the helper scripts write straight to this process's
# stdout, so anything still sitting in Python's buffer would surface after their
# output and the log would read out of order.
def log_info(msg: str) -> None:
    print(f"{BLUE}[info]{NC} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{YELLOW}[warn]{NC} {msg}", file=sys.stderr, flush=True)


def log_error(msg: str) -> None:
    print(f"{RED}[error]{NC} {msg}", file=sys.stderr, flush=True)


def log_done(msg: str) -> None:
    print(f"{GREEN}[done]{NC} {msg}", flush=True)


def fail(*lines: str) -> None:
    for line in lines:
        log_error(line)
    sys.exit(1)


def rel(path: Path) -> str:
    """Path relative to the repo root, for messages."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def check_qtsass():
    """Import qtsass rather than shelling out to its CLI.

    The CLI lives in Python's Scripts/ directory, which is frequently not on
    PATH on Windows even when qtsass is correctly installed. Importing it needs
    only the interpreter running this script, so the common Windows failure
    disappears. qtsass's own CLI does exactly this for a file with an output
    path, so the compiled result is identical.
    """
    try:
        from qtsass import compile_filename
    except ImportError:
        fail(
            "qtsass not found.",
            f"Install it with: {Path(sys.executable).name} -m pip install qtsass",
            "Or build in Docker, which needs no local toolchain:",
            "    docker compose run --rm build",
        )
    return compile_filename


def check_icons() -> None:
    """Fatal, not a warning.

    make-resource.py globs this directory and silently packs zero icons if it is
    empty or misnamed: the build stays green, rcc succeeds, and the theme
    installs with every icon falling back to qBittorrent's stock set. That is
    the same silent-success failure as the stale-stylesheet bug, and it is why a
    "safe" rename of the icons directory is the most dangerous move in this repo.
    """
    if not any(ICONS_DIR.glob("*.svg")):
        fail(
            f"No SVG icons found in {rel(ICONS_DIR)}",
            "Fetch them with: python src/nova-dark/scripts/download_phosphor_icons.py",
        )


HEX = re.compile(r"#[0-9a-fA-F]{6}\b")


def check_no_stray_hex() -> None:
    """_palette.scss is the single source of truth for colour.

    A hex literal anywhere else silently reintroduces the duplication the
    layering exists to prevent, so fail rather than let it drift back. Comments
    are exempt: they do not compile, and commented-out rules are useful history.
    """
    stray = []
    for scss in sorted(SOURCE_DIR.rglob("*.scss")):
        if scss.name == "_palette.scss":
            continue
        for number, line in enumerate(scss.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("//")[0]
            if HEX.search(code):
                stray.append(f"{rel(scss)}:{number}:{code.strip()}")

    if stray:
        log_error("Hex literal outside _palette.scss:")
        for entry in stray:
            print(f"          {entry}", file=sys.stderr, flush=True)
        fail("Add the colour to _palette.scss and reference it by name.")


def run_script(script: Path, *args: str) -> None:
    """Run a helper script with the interpreter running this build.

    sys.executable, never a bare "python": on Windows that name is often absent
    or a Store alias stub, and inside the container it would be an unnecessary
    PATH lookup.
    """
    result = subprocess.run([sys.executable, str(script), *args], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        fail(f"{rel(script)} failed with exit code {result.returncode}")


def compile_stylesheet(compile_filename) -> None:
    """Compile the SCSS, then normalise line endings.

    qtsass writes through Python's text mode, so on Windows every newline lands
    as CRLF and the stylesheet comes out ~1.4 KB larger than the identical build
    on Linux. Qt parses either, so this is not about correctness -- it is so the
    compiled stylesheet can be diffed across build hosts. Comparing NovaDark.qss
    between two builds is how a "no visual change" claim gets verified here, and
    that check is worthless if the Windows output differs from the Linux one on
    every single line.

    This does NOT make dist/nova-dark.qbtheme reproducible: Qt's rcc embeds
    timestamps, so even two consecutive identical builds produce different
    bytes. Compare the .qss, never the .qbtheme.
    """
    previous = Path.cwd()
    try:
        os.chdir(SOURCE_DIR)
        compile_filename("NovaDark.scss", str(Path("..") / "NovaDark.qss"))
    finally:
        os.chdir(previous)

    STYLESHEET.write_bytes(STYLESHEET.read_bytes().replace(b"\r\n", b"\n"))


def fix_ownership() -> None:
    """In Docker the build runs as root, so artifacts written into the
    bind-mounted tree land root-owned and the host user cannot overwrite them on
    the next build. No-op for an ordinary non-root host build, and on Windows,
    which has no geteuid.
    """
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        return
    stat = PROJECT_ROOT.stat()
    for path in [DIST_DIR, *DIST_DIR.rglob("*")]:
        try:
            os.chown(path, stat.st_uid, stat.st_gid)
        except OSError:
            pass


def main() -> None:
    compile_filename = check_qtsass()

    # rcc is deliberately not checked here: make-resource.py resolves it from
    # QBT_THEME_RCC, then PATH, then the bundled src/tools/rcc.exe, and reports
    # its own failure with more context than a guess made up front would.
    check_icons()
    check_no_stray_hex()
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # nova-dark-config.json carries the colours qBittorrent paints itself
    # (QPalette, transfer-list states, log levels). QSS cannot reference them, so
    # they have to be duplicated -- this regenerates them from _palette.scss so
    # the duplicate cannot drift. It is checked in, so any change shows up in
    # `git status`.
    log_info("Generating nova-dark-config.json from the palette")
    run_script(THEME_ROOT / "scripts" / "generate-config.py")

    log_info("Compiling NovaDark.scss")
    compile_stylesheet(compile_filename)

    log_info("Packing nova-dark.qbtheme")
    run_script(
        SRC_ROOT / "make-resource.py",
        "-base-dir", str(THEME_ROOT),
        "-find-files",
        "-config", str(CONFIG_FILE),
        "-icons-dir", str(ICONS_DIR),
        "-include-dir", str(COMMON_DIR),
        "-output", str(OUTPUT),
        "-style", "NovaDark.qss",
    )

    fix_ownership()
    log_done(f"{OUTPUT}.qbtheme")


if __name__ == "__main__":
    main()
