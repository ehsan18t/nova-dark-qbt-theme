#!/usr/bin/env python3
"""
Download and configure Phosphor icons for Nova Dark qBittorrent theme.

This script downloads Phosphor icons from the official repository and maps them
to qBittorrent's expected icon names. Icons are recolored to match the Nova Dark theme.

Usage:
    python download_phosphor_icons.py [--weight WEIGHT] [--color COLOR]

Options:
    --weight    Icon weight: thin, light, regular, bold, fill, duotone (default: regular)
    --color     Icon color in hex format (default: #e0e0e0 for light gray)
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

# Mapping from qBittorrent icon names to Phosphor icon names
# Format: "qbittorrent-name": "phosphor-name"
ICON_MAPPING = {
    # Application and System
    "application-exit": "sign-out",
    "application-rss": "rss",
    "application-url": "link",
    "browser-cookies": "cookie",
    "system-log-out": "sign-out",

    # Chart and Statistics
    "chart-line": "chart-line",
    "view-statistics": "chart-bar",
    "speedometer": "gauge",

    # Status and State
    "checked-completed": "check-circle",
    "connected": "wifi-high",
    "disconnected": "wifi-slash",
    "error": "warning-circle",
    "dialog-warning": "warning",
    "firewalled": "shield-warning",
    "loading": "spinner",
    "paused": "pause-circle",
    "queued": "clock",
    "stopped": "stop-circle",

    # Files and Folders
    "directory": "folder",
    "fileicon": "file",
    "folder-documents": "folder-open",
    "folder-new": "folder-plus",
    "folder-remote": "cloud",

    # Downloads and Uploads
    "download": "download",
    "downloading": "arrow-circle-down",
    "upload": "upload",
    "stalledDL": "arrow-down",
    "stalledUP": "arrow-up",

    # Edit actions
    "edit-clear": "trash",
    "edit-copy": "copy",
    "edit-find": "magnifying-glass",
    "edit-rename": "pencil-simple",

    # Filters
    "filter-active": "funnel",
    "filter-all": "list",
    "filter-inactive": "funnel-simple",
    "filter-stalled": "hourglass",

    # Navigation and Queue
    "go-bottom": "arrow-line-down",
    "go-down": "arrow-down",
    "go-top": "arrow-line-up",
    "go-up": "arrow-up",

    # Actions
    "force-recheck": "arrows-clockwise",
    "reannounce": "megaphone",
    "view-refresh": "arrow-clockwise",
    "view-preview": "eye",

    # List operations
    "list-add": "plus-circle",
    "list-remove": "minus-circle",
    "insert-link": "link",

    # Help and Info
    "help-about": "info",
    "help-contents": "question",
    "hash": "hash",
    "name": "tag",

    # Network
    "network-connect": "globe",
    "network-server": "hard-drives",
    "ip-blocked": "prohibit",

    # Peers
    "peers": "users",
    "peers-add": "user-plus",
    "peers-remove": "user-minus",

    # Settings and Preferences
    "configure": "gear",
    "plugins": "puzzle-piece",
    "preferences-advanced": "sliders",
    "preferences-bittorrent": "share-network",
    "preferences-desktop": "monitor",
    "preferences-webui": "browser",

    # Security
    "object-locked": "lock",
    "security-high": "shield-check",
    "security-low": "shield",

    # Torrent specific
    "torrent-creator": "file-plus",
    "torrent-magnet": "magnet",
    "torrent-start": "play",
    "torrent-start-forced": "fast-forward",
    "torrent-stop": "stop",
    "pause-session": "pause",
    "set-location": "map-pin",

    # Trackers
    "tracker-error": "warning-octagon",
    "tracker-warning": "warning",
    "trackerless": "globe-simple",
    "trackers": "list-bullets",

    # RSS
    "rss_read_article": "article",
    "rss_unread_article": "article-medium",
    "mail-inbox": "envelope",

    # Categories and Tags
    "view-categories": "folders",
    "tags": "tag",

    # Misc
    "ratio": "scales",
    "slow": "traffic-cone",
    "slow_off": "rabbit",
    "task-complete": "check",
    "task-reject": "x",
    "wallet-open": "heart",

    # Tray icons (these need special handling - using app icon)
    "qbittorrent-tray": "download",
    "qbittorrent-tray-dark": "download",
    "qbittorrent-tray-light": "download",
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
    # Remove any existing fill or stroke colors and replace with our color
    # Phosphor icons typically use currentColor, so we need to set it

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
    parser.add_argument("--color", default="#e0e0e0",
                        help="Icon color in hex (default: #e0e0e0)")
    parser.add_argument("--output", default=None,
                        help="Output directory (default: ../icons)")
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
        f"║  Weight: {args.weight:<10}  Color: {args.color:<10}              ║")
    print(f"║  Output: {str(output_dir):<50} ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print()

    success_count = 0
    fail_count = 0

    for qbt_name, phosphor_name in ICON_MAPPING.items():
        url = get_icon_url(phosphor_name, args.weight)
        print(f"  {qbt_name} ← {phosphor_name}...", end=" ")

        svg_content = download_icon(url)

        if svg_content:
            # Recolor the icon
            svg_content = recolor_svg(svg_content, args.color)

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
        "color": args.color,
        "icons": list(ICON_MAPPING.keys()),
        "mapping": ICON_MAPPING
    }

    manifest_path = output_dir / "icon-manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"  Manifest: {manifest_path}")
    print()

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
