#!/usr/bin/env python3
"""Generate one recoloured icon set per (palette x icon treatment).

WHY THIS EXISTS

The checked-in SVGs under icons/modern/ are GEOMETRY. Their colour is whatever
they were last downloaded with and is not meaningful; this script overwrites it
on the way into a build. That is the trick that makes the variant matrix cheap:
six icon sets are produced from one set of 91 files, so git holds 91 SVGs no
matter how many palettes and treatments exist, and adding a treatment never
touches the network.

The alternative -- committing a directory per combination -- was rejected. Six
sets is 546 files that all have to be regenerated together or they drift, and
the drift is invisible because nobody reads an SVG diff.

Every icon is a single <path> under one fill="#rrggbb" on the root <svg>, so
recolouring is a one-attribute rewrite. That is checked, not assumed: an icon
whose root carries no fill is a hard error rather than a silently grey icon in
the packed theme.

HOW A COLOUR IS CHOSEN

    icon-manifest.json   name -> role        ("edit-find" -> "accent")
    source/icons/<t>.json  role -> variable  ("accent" -> "icon-accent")
    source/palettes/*      variable -> hex   ("icon-accent" -> "#a78bfa")

Three indirections, one per axis of the thing that varies. The mono treatment is
just a file that maps every role onto the same variable.

Usage (normally called by scripts/build.py, not by hand):
    recolour_icons.py --palette nebula --treatment mono --out build/icons/x
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
THEME_ROOT = SCRIPT_DIR.parent
GEOMETRY_DIR = THEME_ROOT / "icons" / "modern"
MANIFEST = GEOMETRY_DIR / "icon-manifest.json"
TREATMENT_DIR = THEME_ROOT / "source" / "icons"
PALETTE_DIR = THEME_ROOT / "source" / "palettes"

DECL = re.compile(r"\s*\$([\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;")
FILL = re.compile(r'\bfill="(#[0-9a-fA-F]{3,8})"')

# Roles an icon may carry but that the manifest does not currently use. They
# stay declared in every treatment so a future icon drawn on an inverted fill
# has somewhere to point.
DEFAULT_ROLE = "default"


def fail(*lines: str) -> None:
    for line in lines:
        sys.stderr.write(f"[error] {line}\n")
    sys.exit(1)


def read_scss_colors(path: Path) -> dict[str, str]:
    colors = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = DECL.match(line.split("//")[0])
        if match:
            colors[match.group(1)] = match.group(2).lower()
    return colors


def palette_colors(palette: str) -> dict[str, str]:
    fragment = PALETTE_DIR / f"_{palette}.scss"
    if not fragment.exists():
        fail(f"no palette fragment at {fragment}")
    colors = read_scss_colors(PALETTE_DIR / "_states.scss")
    colors.update(read_scss_colors(fragment))
    return colors


def resolve(palette: str, treatment: str) -> dict[str, str]:
    """role -> hex, for this palette and this treatment."""
    spec_path = TREATMENT_DIR / f"{treatment}.json"
    if not spec_path.exists():
        fail(f"no icon treatment at {spec_path}")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    colors = palette_colors(palette)

    resolved, missing = {}, []
    for role, variable in spec["roles"].items():
        if variable not in colors:
            missing.append(f"{role} -> ${variable}")
        else:
            resolved[role] = colors[variable]

    if missing:
        fail(
            f"treatment '{treatment}' points at variables palette '{palette}' "
            f"does not define:",
            *(f"  {entry}" for entry in missing),
            "Every palette fragment must define the same names; see "
            "source/palettes/_nebula.scss.")
    return resolved


def recolour(palette: str, treatment: str, out_dir: Path) -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["icons"]
    role_hex = resolve(palette, treatment)

    svgs = sorted(GEOMETRY_DIR.glob("*.svg"))
    if not svgs:
        fail(
            f"no SVGs in {GEOMETRY_DIR}",
            "Fetch them with: python src/nova-dark/scripts/download_phosphor_icons.py")

    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("*.svg"):
        stale.unlink()

    unknown_role, unthemeable, verbatim = [], [], 0
    for svg in svgs:
        text = svg.read_text(encoding="utf-8")

        # Absent from the manifest means "not a themed glyph". The three
        # qbittorrent-tray*.svg files are the app's own brand mark, and
        # repainting those in the icon ramp would destroy the light/dark pair
        # they exist to provide. Copy them through untouched.
        if svg.stem not in manifest:
            (out_dir / svg.name).write_text(text, encoding="utf-8")
            verbatim += 1
            continue

        role = manifest[svg.stem]["role"]
        if role not in role_hex:
            unknown_role.append(f"{svg.name}: role '{role}'")
            continue

        # Replace by VALUE, not by position: Phosphor puts the fill on the root
        # <svg>, but a hand-made icon may put it on the path instead. Requiring
        # exactly one distinct fill is what makes replacing all of them safe --
        # a two-tone icon would lose its second colour, so it is refused rather
        # than quietly flattened.
        fills = set(FILL.findall(text))
        if len(fills) != 1:
            unthemeable.append(
                f"{svg.name}: {len(fills)} distinct fills "
                f"({', '.join(sorted(fills)) or 'none'})")
            continue

        (out_dir / svg.name).write_text(
            text.replace(fills.pop(), role_hex[role]), encoding="utf-8")

    if unknown_role:
        fail(
            f"treatment '{treatment}' declares no colour for these roles:",
            *(f"  {entry}" for entry in unknown_role),
            f"Add them to {TREATMENT_DIR / (treatment + '.json')}.")
    if unthemeable:
        fail(
            "these icons are in the manifest but cannot be recoloured, so they "
            "would ship in whatever colour they were last downloaded with:",
            *(f"  {entry}" for entry in unthemeable),
            "Give each one a single fill, or drop it from icon-manifest.json to "
            "have it packed verbatim.")

    return len(svgs), verbatim


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palette", required=True)
    parser.add_argument("--treatment", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    written, verbatim = recolour(args.palette, args.treatment, args.out)
    if not args.quiet:
        note = f" ({verbatim} copied verbatim)" if verbatim else ""
        print(f"recoloured {written} icons for {args.palette}/{args.treatment}{note}")


if __name__ == "__main__":
    main()
