#!/usr/bin/env python3
"""Generate the list of SVG icons required by the Nova Dark theme.

Usage:
    python generate_icon_manifest.py --icon-config /path/to/qBittorrent/src/icons/iconconfig.json \
                                     --icons-root /path/to/qBittorrent/src/icons \
                                     --output ../icons/modern/ICON-LIST.md

The script reads qBittorrent's canonical icon configuration file and emits a
Markdown checklist that mirrors the expected folder layout and filenames.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from textwrap import dedent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a Markdown list of the qBittorrent icons Nova Dark expects.")
    parser.add_argument("--icon-config", required=True, type=Path,
                        help="Path to qBittorrent's iconconfig.json file.")
    parser.add_argument("--icons-root", required=True, type=Path,
                        help="Root directory that contains the source SVG/PNG icons referenced by iconconfig.json.")
    parser.add_argument("--output", default=Path("../icons/modern/ICON-LIST.md"),
                        type=Path, help="Destination Markdown file for the manifest.")
    return parser.parse_args()


def resolve_icon_path(icon_id: str, root: Path) -> Path | None:
    candidate = root / icon_id
    if candidate.exists():
        return candidate
    for extension in (".svg", ".png", ".bmp", ".ico"):
        candidate_with_ext = candidate.with_suffix(extension)
        if candidate_with_ext.exists():
            return candidate_with_ext
    return None


def main() -> None:
    args = parse_args()

    if not args.icon_config.exists():
        raise FileNotFoundError(
            f"iconconfig.json not found at {args.icon_config}")

    with args.icon_config.open("r", encoding="utf-8") as fh:
        icon_map = json.load(fh)

    lines: list[str] = []
    lines.append("# Nova Dark Icon Manifest")
    lines.append("")
    lines.append(
        "This list is generated from qBittorrent's iconconfig.json. Place the final SVG artwork")
    lines.append(
        "inside `src/nova-dark/icons/modern` using the filenames below (preserving subdirectories).")
    lines.append("")

    missing: list[str] = []

    for icon_key, relative_path in sorted(icon_map.items()):
        resolved = resolve_icon_path(relative_path, args.icons_root)
        rel_display = relative_path
        if resolved is None:
            missing.append(relative_path)
        else:
            rel_display = str(resolved.relative_to(args.icons_root))
        lines.append(f"- [ ] `{rel_display}`  <!-- {icon_key} -->")

    if missing:
        lines.append("")
        lines.append("## Missing Files")
        lines.append("")
        lines.append(
            "The entries below were not found relative to the provided icons root. Ensure the paths exist:")
        lines.append("")
        for path in missing:
            lines.append(f"- `{path}`")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(dedent(
        f"""
        Icon manifest written to {args.output}.
        Checked {len(icon_map)} icon bindings; {len(missing)} missing.
        """
    ).strip())


if __name__ == "__main__":
    main()
