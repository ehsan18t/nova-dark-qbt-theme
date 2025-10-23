#!/usr/bin/env python3
"""
Recolor SVG icons based on theme accent color.
Copies icons from source to temp directory and applies color replacements.
"""
import sys
import os
import shutil
import re
from pathlib import Path


def extract_accent_color(scss_file):
    """Extract $icon-fill color from SCSS definitions file."""
    try:
        with open(scss_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for $icon-fill: #color;
        match = re.search(r'\$icon-fill:\s*#([0-9a-fA-F]{6})', content)
        if match:
            return f"#{match.group(1).lower()}"

        print(
            f"[warn] Could not find $icon-fill in {scss_file}, using default #5fb8ad", file=sys.stderr)
        return "#5fb8ad"
    except Exception as e:
        print(f"[error] Failed to read SCSS file: {e}", file=sys.stderr)
        return "#5fb8ad"


def recolor_svg_icons(source_dir, dest_dir, new_color):
    """Copy SVG files from source to dest and replace old colors with new_color."""
    if not os.path.exists(source_dir):
        print(
            f"[error] Source directory not found: {source_dir}", file=sys.stderr)
        return False

    # Create destination directory
    os.makedirs(dest_dir, exist_ok=True)

    # Old colors to replace (common icon colors)
    old_colors = ['#5C8DFF', '#5c8dff', '#1E90FF', '#1e90ff', '#4a8fff']

    svg_count = 0
    for filename in os.listdir(source_dir):
        if not filename.lower().endswith('.svg'):
            continue

        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(dest_dir, filename)

        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace all old colors with new color
            for old_color in old_colors:
                content = content.replace(old_color, new_color)

            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)

            svg_count += 1
        except Exception as e:
            print(f"[warn] Failed to recolor {filename}: {e}", file=sys.stderr)

    if svg_count > 0:
        print(f"[info] Recolored {svg_count} SVG icons to {new_color}")

    return svg_count > 0


def main():
    if len(sys.argv) < 4:
        print("Usage: recolor-icons.py <scss_definitions_file> <source_icons_dir> <dest_icons_dir>", file=sys.stderr)
        sys.exit(1)

    scss_file = sys.argv[1]
    source_dir = sys.argv[2]
    dest_dir = sys.argv[3]

    # Extract accent color from theme
    accent_color = extract_accent_color(scss_file)
    print(f"[info] Using accent color: {accent_color}")

    # Recolor icons
    if not recolor_svg_icons(source_dir, dest_dir, accent_color):
        print("[warn] No icons were recolored", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
