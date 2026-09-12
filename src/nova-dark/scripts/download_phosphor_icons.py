#!/usr/bin/env python3
"""
Download and configure Phosphor icons for Nova Dark qBittorrent theme.
Icons are colored based on their semantic meaning for a cohesive look.
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error
import argparse
from pathlib import Path

# Phosphor icon weight variants
WEIGHTS = ["thin", "light", "regular", "bold", "fill", "duotone"]

# Base URL for Phosphor icons (using jsDelivr CDN)
PHOSPHOR_CDN_BASE = "https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2.1.1"

# THIS SCRIPT NO LONGER DECIDES WHAT COLOUR A THEMED ICON IS.
#
# It downloads GEOMETRY. Every icon under icons/modern/ is written with the
# placeholder fill below and recoloured on the way into each build by
# scripts/recolour_icons.py, which resolves the icon's role through
# source/icons/<treatment>.json onto a palette variable. That is what lets 91
# checked-in files serve every palette and every icon treatment, and it is why
# adding a treatment never touches the network.
#
# So the value here is deliberately meaningless. It exists only so each SVG has
# exactly one fill for recolour_icons.py to find; shipping a set with this
# colour still visible would mean the recolour step was skipped.
GEOMETRY_FILL = "#808080"

# The control icons are the exception, and the reason this still reads a
# palette at all. They live in src/common/controls/ and are referenced straight
# from the stylesheet as :/uitheme/common/controls/*.svg, shared verbatim by
# every variant, so nothing recolours them at build time and their colour has
# to be baked in here.
#
# They resolve against the DEFAULT palette. That is a real limitation rather
# than an oversight: check marks and arrows drawn in one neutral read correctly
# on all three grounds because all three are dark, and giving them a per-variant
# copy would mean a fourth axis for a handful of 13px glyphs.
DEFAULT_PALETTE = "nebula"
PALETTE_DIR = Path(__file__).resolve().parent.parent / "source" / "palettes"
TREATMENT_DIR = Path(__file__).resolve().parent.parent / "source" / "icons"


def load_colors() -> dict[str, str]:
    """Read $icon-<name> declarations out of the shared and default palettes."""
    sources = [PALETTE_DIR / "_states.scss", PALETTE_DIR / f"_{DEFAULT_PALETTE}.scss"]
    missing = [p for p in sources if not p.exists()]
    if missing:
        for path in missing:
            sys.stderr.write(f"[error] palette not found: {path}\n")
        sys.exit(1)

    colors = {}
    for path in sources:
        for line in path.read_text(encoding="utf-8").splitlines():
            code = line.split("//")[0]
            match = re.match(r"\s*\$icon-([\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;", code)
            if match:
                colors[match.group(1)] = match.group(2).lower()

    if not colors:
        sys.stderr.write(
            "[error] no $icon-* colours found in source/palettes/.\n"
            "        Icon colours are defined there under the $icon- prefix.\n"
        )
        sys.exit(1)

    return colors


COLORS = load_colors()

# Control icons (checkboxes, radios, dock titlebar) - saved to src/common/controls/
CONTROL_ICONS = {
    "checkbox-unchecked": ("square", "default"),
    "checkbox-checked": ("check-square", "success"),
    "radio-unchecked": ("circle", "default"),
    "radio-checked": ("radio-button", "success"),
    # QDockWidget titlebar buttons (see Nova Overrides.scss)
    "close": ("x", "default"),
    "undock": ("arrow-square-out", "default"),
}

# Inner check/radio marks - these use bold weight for visibility
# Saved to src/common/controls/ alongside CONTROL_ICONS
INNER_CHECK_ICONS = {
    # White check for dark backgrounds
    "checkbox_check_dark": ("check", "white"),
    # White dot for dark backgrounds
    "radio_check_dark": ("circle", "white"),
}

# Mapping from qBittorrent icon names to (Phosphor icon name, color key)
ICON_MAPPING = {
    # Application and System
    "application-exit": ("sign-out", "error"),
    "application-rss": ("rss", "orange"),
    "application-url": ("link", "accent"),
    "browser-cookies": ("cookie", "warning"),
    "system-log-out": ("sign-out", "error"),

    # Chart and Statistics
    "chart-line": ("chart-line", "info"),
    "view-statistics": ("chart-bar", "info"),
    "speedometer": ("gauge", "warning"),

    # Status and State - Success (green)
    "checked-completed": ("check-circle", "success"),
    "connected": ("wifi-high", "success"),
    "task-complete": ("check", "success"),

    # Status and State - Error (red)
    "disconnected": ("wifi-slash", "error"),
    "error": ("warning-circle", "error"),
    "firewalled": ("shield-warning", "error"),
    "task-reject": ("x", "error"),
    "ip-blocked": ("prohibit", "error"),
    "tracker-error": ("warning-octagon", "error"),

    # Status and State - Warning (amber)
    "dialog-warning": ("warning", "warning"),
    "tracker-warning": ("warning", "warning"),
    "queued": ("clock", "warning"),

    # Status and State - Muted
    "loading": ("spinner", "muted"),
    "paused": ("pause-circle", "muted"),
    "stopped": ("stop-circle", "error"),

    # Files and Folders
    "directory": ("folder", "warning"),
    "fileicon": ("file", "default"),
    "folder-documents": ("folder-open", "warning"),
    "folder-new": ("folder-plus", "warning"),
    "folder-remote": ("cloud", "accent"),

    # Downloads (cyan for active, green for completed)
    "download": ("download", "success"),
    "downloading": ("arrow-circle-down", "info"),
    "stalledDL": ("arrow-down", "stalled"),

    # Uploads (purple)
    "upload": ("upload", "upload"),
    "stalledUP": ("arrow-up", "stalled"),

    # Edit actions
    "edit-clear": ("trash", "error"),
    "edit-copy": ("copy", "default"),
    "edit-find": ("magnifying-glass", "default"),
    "edit-rename": ("pencil-simple", "default"),

    # Filters
    "filter-active": ("funnel", "success"),
    "filter-all": ("list", "default"),
    "filter-inactive": ("funnel-simple", "muted"),
    "filter-stalled": ("hourglass", "warning"),

    # Navigation and Queue
    "go-bottom": ("arrow-line-down", "accent"),
    "go-down": ("arrow-down", "accent"),
    "go-top": ("arrow-line-up", "accent"),
    "go-up": ("arrow-up", "accent"),

    # Actions
    "force-recheck": ("arrows-clockwise", "orange"),
    "reannounce": ("megaphone", "orange"),
    "view-refresh": ("arrow-clockwise", "accent"),
    "view-preview": ("eye", "info"),

    # List operations
    "list-add": ("plus-circle", "success"),
    "list-remove": ("minus-circle", "error"),
    "insert-link": ("link", "accent"),

    # Help and Info
    "help-about": ("info", "info"),
    "help-contents": ("question", "info"),
    "hash": ("hash", "default"),
    "name": ("tag", "default"),

    # Network
    "network-connect": ("globe", "info"),
    "network-server": ("hard-drives", "default"),

    # Peers
    "peers": ("users", "accent"),
    "peers-add": ("user-plus", "success"),
    "peers-remove": ("user-minus", "error"),

    # Settings and Preferences
    "configure": ("gear", "default"),
    "plugins": ("puzzle-piece", "upload"),
    "preferences-advanced": ("sliders", "upload"),
    "preferences-bittorrent": ("share-network", "success"),
    "preferences-desktop": ("monitor", "accent"),
    "preferences-webui": ("browser", "info"),

    # Security
    "object-locked": ("lock", "warning"),
    "security-high": ("shield-check", "success"),
    "security-low": ("shield", "warning"),

    # Torrent specific
    "torrent-creator": ("file-plus", "accent"),
    "torrent-magnet": ("magnet", "upload"),
    "torrent-start": ("play", "accent"),
    "torrent-start-forced": ("fast-forward", "orange"),
    "torrent-stop": ("stop", "error"),
    "pause-session": ("pause", "warning"),
    "set-location": ("map-pin", "accent"),

    # Trackers
    "trackerless": ("globe-simple", "muted"),
    "trackers": ("list-bullets", "default"),

    # RSS
    "rss_read_article": ("article", "muted"),
    "rss_unread_article": ("article-medium", "orange"),
    "mail-inbox": ("envelope", "accent"),

    # Categories and Tags
    "view-categories": ("folders", "warning"),
    "tags": ("tag", "accent"),

    # Misc
    "ratio": ("scales", "info"),
    "slow": ("traffic-cone", "warning"),
    "slow_off": ("rabbit", "success"),
    "wallet-open": ("heart", "error"),

    # Tray icons - manually customized with qBittorrent logo, not auto-generated
    # "qbittorrent-tray": custom
    # "qbittorrent-tray-dark": custom
    # "qbittorrent-tray-light": custom
}


def check_roles() -> None:
    """Fail if a mapping asks for a role no icon treatment can colour.

    Every lookup is a .get() with a fallback, so a role that nothing defines
    does not raise -- the icons that referenced it are silently regenerated in
    default grey and the build stays green. Renaming a role repaints five icons
    and reports nothing. That is the same silent-success failure as an empty
    icons directory, which build.py treats as fatal for exactly this reason.

    Two different checks, because the two icon families are coloured at
    different times: themed icons need their role to exist in every treatment
    file, and control icons need their key to exist in the default palette.
    """
    themed = {role for _, role in ICON_MAPPING.values()} | {"default"}
    control = {key for mapping in (CONTROL_ICONS, INNER_CHECK_ICONS)
               for _, key in mapping.values()} | {"default"}

    problems = []

    treatments = sorted(TREATMENT_DIR.glob("*.json"))
    if not treatments:
        problems.append(f"no icon treatments found in {TREATMENT_DIR}")
    for path in treatments:
        declared = set(json.loads(path.read_text(encoding="utf-8"))["roles"])
        for role in sorted(themed - declared):
            problems.append(f"{path.name} declares no colour for role '{role}'")

    for key in sorted(control - set(COLORS)):
        problems.append(
            f"control icons use $icon-{key}, which "
            f"source/palettes/_{DEFAULT_PALETTE}.scss does not define")

    if problems:
        for entry in problems:
            sys.stderr.write(f"[error] {entry}\n")
        sys.stderr.write(
            "        Add the missing entry, or update the mapping in this file.\n")
        sys.exit(1)


check_roles()


def get_icon_url(icon_name: str, weight: str = "regular") -> str:
    """Get the CDN URL for a Phosphor icon."""
    if weight == "regular":
        return f"{PHOSPHOR_CDN_BASE}/assets/regular/{icon_name}.svg"
    elif weight == "fill":
        return f"{PHOSPHOR_CDN_BASE}/assets/fill/{icon_name}-fill.svg"
    elif weight == "duotone":
        return f"{PHOSPHOR_CDN_BASE}/assets/duotone/{icon_name}-duotone.svg"
    else:
        return f"{PHOSPHOR_CDN_BASE}/assets/{weight}/{icon_name}-{weight}.svg"


def download_icon(url: str) -> str | None:
    """Download an icon from URL and return its content."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP Error {e.code}: {url}")
        return None
    except urllib.error.URLError as e:
        print(f"  ✗ URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def recolor_svg(svg_content: str, color: str) -> str:
    """Recolor an SVG to use the specified color."""
    # Add fill color to the SVG root element
    if 'fill="' not in svg_content:
        svg_content = svg_content.replace("<svg ", f'<svg fill="{color}" ')
    else:
        svg_content = re.sub(r'fill="[^"]*"', f'fill="{color}"', svg_content)

    # Replace currentColor with our color
    svg_content = svg_content.replace("currentColor", color)

    return svg_content


def ensure_dir(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def generate_icon_list_md(output_dir: Path, weight: str, mono: bool, mono_color: str) -> None:
    """Generate the ICON-LIST.md documentation file."""
    lines = [
        "# Nova Dark Icons",
        "",
        "This folder contains the custom Phosphor icon set for the Nova Dark theme.",
        "",
        f"**Generated:** {len(ICON_MAPPING)} icons using Phosphor Icons (weight: {weight})",
        "",
        "## Regenerating Icons",
        "",
        "To regenerate all icons with the defined color palette:",
        "",
        "```bash",
        "cd src/nova-dark/scripts",
        "python download_phosphor_icons.py",
        "```",
        "",
        "### Options",
        "",
        "| Option | Description |",
        "|--------|-------------|",
        "| `--weight <w>` | Icon weight: thin, light, regular, bold, fill, duotone |",
        "| `--output <dir>` | Custom output directory |",
        "",
        "## Colour",
        "",
        "These files are GEOMETRY. Every themed icon below is written with the",
        f"placeholder fill `{mono_color}` and recoloured on the way into each build",
        "by `scripts/recolour_icons.py`, which resolves the icon's role through",
        "`source/icons/<treatment>.json` onto a palette variable.",
        "",
        "That is why one set of files serves every palette and every icon",
        "treatment, and why adding a treatment never touches the network. If you",
        "see the placeholder colour in a packed theme, the recolour step was",
        "skipped.",
        "",
        "| Role | Meaning |",
        "|------|---------|",
    ]

    color_usage = {
        "default": "Default icons",
        "accent": "Primary actions, links",
        "success": "Downloads complete, connected",
        "warning": "Warnings, queued items",
        "error": "Errors, disconnected",
        "upload": "Uploads, seeding",
        "info": "Info, help, statistics",
        "muted": "Disabled, stopped",
        "orange": "Force actions",
        "stalled": "Stalled transfers",
    }

    for name in sorted({role for _, role in ICON_MAPPING.values()}):
        lines.append(f"| `{name}` | {color_usage.get(name, '')} |")

    lines.extend([
        "",
        "## Icon List",
        "",
        "| qBittorrent Icon | Phosphor Icon | Color |",
        "|------------------|---------------|-------|",
    ])

    for qbt_name, (phosphor_name, role) in sorted(ICON_MAPPING.items()):
        lines.append(f"| `{qbt_name}` | {phosphor_name} | `{role}` |")

    lines.extend([
        "",
        "## Files",
        "",
        "- `icon-manifest.json` - Machine-readable icon configuration",
        "- `*.svg` - Individual icon files",
        "",
        "---",
        "*This file is auto-generated by `download_phosphor_icons.py`*",
    ])

    icon_list_path = output_dir / "ICON-LIST.md"
    with open(icon_list_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Download Phosphor icons for Nova Dark theme")
    parser.add_argument("--weight", choices=WEIGHTS, default="regular",
                        help="Icon weight (default: regular)")
    parser.add_argument("--output", default=None,
                        help="Output directory (default: ../icons/modern)")
    # --mono is deliberately gone. Monochrome is now an ICON TREATMENT chosen
    # per build (source/icons/mono.json), not a property of the downloaded
    # files, so every variant can offer both without downloading twice.
    parser.add_argument("--mono", action="store_true",
                        help=argparse.SUPPRESS)
    args = parser.parse_args()

    # Determine output directory
    script_dir = Path(__file__).parent
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = script_dir.parent / "icons" / "modern"

    ensure_dir(output_dir)

    print("=" * 64)
    print("  Phosphor Icons Downloader for Nova Dark")
    print("=" * 64)
    print(
        f"  Weight: {args.weight:<10}  Colored: {'No' if args.mono else 'Yes'}")
    print(f"  Output: {output_dir}")
    print("=" * 64)
    print()

    if args.mono:
        print("  --mono no longer applies here. Monochrome is a build-time icon")
        print("  treatment: build the *-mono variants instead, or edit")
        print("  src/nova-dark/source/icons/mono.json.")
        print()

    print(f"  Themed icons download with the placeholder fill {GEOMETRY_FILL};")
    print("  scripts/recolour_icons.py colours them per variant at build time.")
    print()
    print(f"  Control icons bake in colours from the {DEFAULT_PALETTE} palette:")
    for name, color in sorted(COLORS.items()):
        print(f"    {name:<10} {color}")
    print()

    success_count = 0
    fail_count = 0

    for qbt_name, (phosphor_name, color_key) in ICON_MAPPING.items():
        url = get_icon_url(phosphor_name, args.weight)

        # The placeholder, never a real colour: recolour_icons.py decides what
        # this icon looks like, once per palette and treatment, at build time.
        color = GEOMETRY_FILL

        print(f"  {qbt_name} ← {phosphor_name} ({color})...", end=" ")

        svg_content = download_icon(url)

        if svg_content:
            # Recolor the icon
            svg_content = recolor_svg(svg_content, color)

            # Save the icon
            output_path = output_dir / f"{qbt_name}.svg"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            print("OK")
            success_count += 1
        else:
            fail_count += 1

    print()
    print("=" * 64)
    print(f"  Downloaded: {success_count} icons")
    if fail_count > 0:
        print(f"  Failed: {fail_count} icons")
    print(f"  Location: {output_dir}")
    print("=" * 64)

    # Download control icons (checkboxes, radio buttons) to src/common/controls/
    controls_dir = script_dir.parent.parent.parent / "src" / "common" / "controls"
    ensure_dir(controls_dir)

    print()
    print(f"  Downloading control icons to {controls_dir}...")

    for ctrl_name, (phosphor_name, color_key) in CONTROL_ICONS.items():
        url = get_icon_url(phosphor_name, args.weight)
        color = COLORS.get(color_key, COLORS["default"])

        print(f"    {ctrl_name} ← {phosphor_name} ({color})...", end=" ")

        svg_content = download_icon(url)
        if svg_content:
            svg_content = recolor_svg(svg_content, color)
            output_path = controls_dir / f"{ctrl_name}.svg"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print("OK")
        else:
            print("FAILED")

    # Download inner check icons (bold weight for visibility) to src/common/controls/
    src_controls_dir = script_dir.parent.parent.parent / "src" / "common" / "controls"
    ensure_dir(src_controls_dir)

    print()
    print(f"  Downloading inner check icons (bold) to {src_controls_dir}...")

    for icon_name, (phosphor_name, color_key) in INNER_CHECK_ICONS.items():
        # Always use bold for visibility
        url = get_icon_url(phosphor_name, "bold")
        color = COLORS.get(color_key, COLORS["default"])

        print(f"    {icon_name} ← {phosphor_name}-bold ({color})...", end=" ")

        svg_content = download_icon(url)
        if svg_content:
            svg_content = recolor_svg(svg_content, color)
            output_path = src_controls_dir / f"{icon_name}.svg"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print("OK")
        else:
            print("FAILED")

    # Generate a manifest file
    manifest = {
        "source": "Phosphor Icons",
        "version": "2.1.1",
        "weight": args.weight,
        "_note": (
            "Icon colour is a ROLE, not a hex. scripts/recolour_icons.py "
            "resolves each role through source/icons/<treatment>.json onto a "
            "palette variable, so the same icons serve every palette and every "
            "icon treatment. Adding a treatment means adding one JSON file, "
            "never re-downloading anything."
        ),
        "icons": {k: {"phosphor": v[0], "role": v[1]}
                  for k, v in sorted(ICON_MAPPING.items())}
    }

    manifest_path = output_dir / "icon-manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"  Manifest: {manifest_path}")

    # Generate ICON-LIST.md documentation
    generate_icon_list_md(output_dir, args.weight, args.mono, GEOMETRY_FILL)
    print(f"  Icon List: {output_dir / 'ICON-LIST.md'}")
    print()

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
