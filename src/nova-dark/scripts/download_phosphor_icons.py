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

# Color palette for Nova Dark theme
COLORS = {
    "default": "#b0b0b0",      # Light gray - default icons
    # Blue - primary actions, links (matches progress bar)
    "accent": "#4a9eff",
    "success": "#4ade80",      # Green - downloads, completed, connected
    "warning": "#fbbf24",      # Amber - warnings, queued
    "error": "#f87171",        # Red - errors, disconnected, blocked
    "upload": "#c084fc",       # Purple - uploads
    "info": "#22d3ee",         # Cyan - info, help, statistics
    "muted": "#6b7280",        # Muted gray - disabled, stopped
    "orange": "#fb923c",       # Orange - force actions, trackers
    "stalled": "#8cb4b4",      # Teal gray - stalled transfers
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
    "speedometer": ("gauge", "accent"),

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

    # Downloads (green)
    "download": ("download", "success"),
    "downloading": ("arrow-circle-down", "success"),
    "stalledDL": ("arrow-down", "stalled"),

    # Uploads (purple)
    "upload": ("upload", "upload"),
    "stalledUP": ("arrow-up", "stalled"),

    # Edit actions
    "edit-clear": ("trash", "error"),
    "edit-copy": ("copy", "default"),
    "edit-find": ("magnifying-glass", "accent"),
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
    "network-connect": ("globe", "accent"),
    "network-server": ("hard-drives", "default"),

    # Peers
    "peers": ("users", "accent"),
    "peers-add": ("user-plus", "success"),
    "peers-remove": ("user-minus", "error"),

    # Settings and Preferences
    "configure": ("gear", "default"),
    "plugins": ("puzzle-piece", "upload"),
    "preferences-advanced": ("sliders", "default"),
    "preferences-bittorrent": ("share-network", "accent"),
    "preferences-desktop": ("monitor", "default"),
    "preferences-webui": ("browser", "accent"),

    # Security
    "object-locked": ("lock", "warning"),
    "security-high": ("shield-check", "success"),
    "security-low": ("shield", "warning"),

    # Torrent specific
    "torrent-creator": ("file-plus", "accent"),
    "torrent-magnet": ("magnet", "upload"),
    "torrent-start": ("play", "success"),
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

    # Tray icons
    "qbittorrent-tray": ("download", "accent"),
    "qbittorrent-tray-dark": ("download", "default"),
    "qbittorrent-tray-light": ("download", "accent"),
}


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


def main():
    parser = argparse.ArgumentParser(
        description="Download Phosphor icons for Nova Dark theme")
    parser.add_argument("--weight", choices=WEIGHTS, default="regular",
                        help="Icon weight (default: regular)")
    parser.add_argument("--output", default=None,
                        help="Output directory (default: ../icons/modern)")
    parser.add_argument("--mono", action="store_true",
                        help="Use monochrome icons (single color)")
    parser.add_argument("--color", default="#e0e0e0",
                        help="Monochrome color (only used with --mono)")
    args = parser.parse_args()

    # Determine output directory
    script_dir = Path(__file__).parent
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = script_dir.parent / "icons" / "modern"

    ensure_dir(output_dir)

    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║  Phosphor Icons Downloader for Nova Dark                     ║")
    print(f"╠══════════════════════════════════════════════════════════════╣")
    print(
        f"║  Weight: {args.weight:<10}  Colored: {'No' if args.mono else 'Yes':<10}            ║")
    print(f"║  Output: {str(output_dir):<50} ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print()

    if not args.mono:
        print("  Color Palette:")
        for name, color in COLORS.items():
            print(f"    {name:<10} {color}")
        print()

    success_count = 0
    fail_count = 0

    for qbt_name, (phosphor_name, color_key) in ICON_MAPPING.items():
        url = get_icon_url(phosphor_name, args.weight)

        # Determine color
        if args.mono:
            color = args.color
        else:
            color = COLORS.get(color_key, COLORS["default"])

        print(f"  {qbt_name} ← {phosphor_name} ({color})...", end=" ")

        svg_content = download_icon(url)

        if svg_content:
            # Recolor the icon
            svg_content = recolor_svg(svg_content, color)

            # Save the icon
            output_path = output_dir / f"{qbt_name}.svg"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            print("✓")
            success_count += 1
        else:
            fail_count += 1

    print()
    print(f"═══════════════════════════════════════════════════════════════")
    print(f"  Downloaded: {success_count} icons")
    if fail_count > 0:
        print(f"  Failed: {fail_count} icons")
    print(f"  Location: {output_dir}")
    print(f"═══════════════════════════════════════════════════════════════")

    # Generate a manifest file
    manifest = {
        "source": "Phosphor Icons",
        "version": "2.1.1",
        "weight": args.weight,
        "colored": not args.mono,
        "colors": COLORS if not args.mono else {"mono": args.color},
        "icons": {k: {"phosphor": v[0], "color": COLORS.get(v[1], COLORS["default"])}
                  for k, v in ICON_MAPPING.items()}
    }

    manifest_path = output_dir / "icon-manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"  Manifest: {manifest_path}")
    print()

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
