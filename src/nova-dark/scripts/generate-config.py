#!/usr/bin/env python3
"""Generate one config/<palette>.json per palette, from the SCSS palettes.

qBittorrent paints two different ways. The stylesheet covers widgets it has a
rule for; everything else falls back to the QPalette and the semantic colour
IDs it reads from a theme's config.json. There is no way for QSS to reference a
config.json colour -- different consumers, different parse paths -- so the two
sets of colours have no choice but to be duplicated.

This script is what stops that duplication from drifting. The palette fragments
stay the single source of truth, and each config.json becomes a derived
artifact: the MAPPING below says which primitive each qBittorrent colour ID
takes.

That divergence was not hypothetical. Before this existed, config.json and the
stylesheet shared 3 colours out of 33 -- a cool blue-grey system and Catppuccin
Mocha painting the same window. It showed wherever the stylesheet did not
reach, most visibly when the window lost focus and Qt fell back to the
QPalette-derived Inactive group.

THE MAPPING IS PALETTE-INDEPENDENT, and that is the whole reason the variant
matrix was cheap to add: it names variables, never hexes, so all three palettes
run through it unchanged. Adding a fourth palette does not touch this file.

The generated files are checked in on purpose, even though the build rewrites
them every time. They are the only place a palette change becomes visible in
`git diff` as colours rather than as SCSS, which is how a bad value gets caught
before it is packed.

Usage:
    generate-config.py                rewrite every palette's config
    generate-config.py --palette X    rewrite just that one
    generate-config.py --check        exit 1 if any file is stale (for CI)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
THEME_ROOT = SCRIPT_DIR.parent
PALETTE_DIR = THEME_ROOT / "source" / "palettes"
CONFIG_DIR = THEME_ROOT / "config"
VARIANTS = THEME_ROOT / "variants.json"

# qBittorrent colour ID -> palette primitive.
#
# Every ID qBittorrent 5.2.3 recognises appears here; the build fails if the
# two lists ever diverge, which is how a qBittorrent upgrade that adds a colour
# gets noticed instead of silently falling back to a stock value.
MAPPING = {
    # --- QPalette: the fallback layer, painting whatever QSS does not ------
    # Aligned to the chrome the stylesheet paints, so the two agree wherever
    # both are visible.
    "Palette.Window": "crust-1",              # matches QMainWindow/QToolBar
    "Palette.WindowText": "text-2",
    # $rail, not $panel. TransferListFiltersWidget is a custom QWidget with no
    # paintEvent (transferlistfilterswidget.cpp:52-56), so the sidebar container
    # and the gaps between its sections cannot be painted from the stylesheet at
    # all -- they follow this. The five filter widgets are set to the same
    # primitive in _widgets.scss; the two are one decision in two files, and
    # leaving them apart stripes the pane. Everything that must stay $panel
    # (the transfer list, inputs, menus) sets its background explicitly.
    "Palette.Base": "rail",
    "Palette.AlternateBase": "crust-2",
    "Palette.Text": "text-2",
    "Palette.ToolTipBase": "panel",           # matches QToolTip
    "Palette.ToolTipText": "text-2",
    "Palette.BrightText": "white",
    "Palette.Highlight": "accent",            # matches focus rings
    "Palette.HighlightedText": "white",
    "Palette.Button": "nova-button",          # matches QPushButton
    "Palette.ButtonText": "text-2",
    "Palette.Link": "accent-info",            # matches the `a` rule
    "Palette.LinkVisited": "accent-info",
    # Qt's 3D bevel ramp, brightest to darkest: Light > Midlight > Mid > Dark.
    "Palette.Light": "surface-0",
    "Palette.Midlight": "nova-elevated",
    "Palette.Mid": "crust-2",
    "Palette.Dark": "crust-0",
    "Palette.Shadow": "shadow",
    # One disabled colour across the roles that sit on a dark background.
    "Palette.WindowTextDisabled": "surface-3",
    "Palette.TextDisabled": "surface-3",
    "Palette.ToolTipTextDisabled": "surface-3",
    "Palette.BrightTextDisabled": "surface-3",
    "Palette.ButtonTextDisabled": "surface-3",
    # NOT dimmed. This one draws on top of Palette.Highlight, and Highlight is
    # two very different things: the dark selection background, and the light
    # progress-bar fill (progressbarpainter.cpp:77 assigns ProgressBar to
    # QPalette::Highlight, then :73 switches to the Disabled group for a stopped
    # torrent). A mid-grey satisfies neither -- surface-3 measured 1.89:1 on
    # BOTH, which is why the percentage on a paused torrent was unreadable.
    # White is the best available compromise: 9.2:1 on the selection, and it
    # matches the enabled state over the fill instead of being worse than it.
    "Palette.HighlightedTextDisabled": "white",

    # --- Execution log: severity, so the accent ramp is the right source ---
    "Log.TimeStamp": "text-0",
    "Log.Normal": "text-1",
    "Log.Info": "accent-info",
    "Log.Warning": "accent-warning",
    "Log.Critical": "accent-error",
    "Log.BannedPeer": "accent-error",

    # --- RSS -------------------------------------------------------------
    "RSS.ReadArticle": "text-1",
    # $text-bright, NOT $accent. This is the only place the chrome accent was
    # ever drawn as TEXT, and it has to stay readable on $panel in every
    # palette. Graphite's accent is a neutral in the same band as $surface-3,
    # which measures 3.56:1 there -- dimmer than the READ articles beside it,
    # which inverts the one distinction the pair exists to make. Brightest text
    # against $text-1 is the conventional unread treatment and holds in all
    # three palettes without the mapping having to know which one it is.
    "RSS.UnreadArticle": "text-bright",

    # --- Transfer list -----------------------------------------------------
    # Straight onto the shared state family in palettes/_states.scss, so a state
    # reads the same colour in every variant. Only the two deliberately quiet
    # states have their own primitives.
    "TransferList.Downloading": "accent-blue",
    "TransferList.DownloadingMetadata": "accent-info",
    "TransferList.ForcedDownloading": "accent-peach",
    "TransferList.ForcedDownloadingMetadata": "accent-peach",
    "TransferList.ForcedUploading": "accent-peach",
    "TransferList.Uploading": "accent-success",
    # $accent-queued, NOT $accent. The chrome accent is violet in Nebula but
    # blue in Graphite and teal in Slate, either of which would be
    # indistinguishable from Downloading or Checking in this one column. The
    # split is what lets a palette pick any accent it likes.
    "TransferList.QueuedDownloading": "accent-queued",
    "TransferList.QueuedUploading": "accent-queued",
    # All three checking states share one colour. They used to be split, but the
    # two values were dE 10 apart -- indistinguishable in a column, and the
    # distinction is cosmetic.
    "TransferList.CheckingDownloading": "accent-teal",
    "TransferList.CheckingUploading": "accent-teal",
    "TransferList.CheckingResumeData": "accent-teal",
    "TransferList.Moving": "accent-warning",
    # missing is dull, error is bright. Separating them by lightness as well as
    # hue reads faster when scanning than hue alone.
    "TransferList.MissingFiles": "accent-maroon",
    "TransferList.Error": "accent-error",
    "TransferList.StalledDownloading": "status-stalled",
    "TransferList.StalledUploading": "status-stalled",
    "TransferList.StoppedDownloading": "status-stopped",
    "TransferList.StoppedUploading": "status-stopped",

    # --- Pieces bar and progress -----------------------------------------
    # $panel, deliberately NOT a frame colour.
    #
    # piecesbar.cpp:181 draws the bar's content into QRect(1, 1, w-2, h-2), then
    # :205-207 strokes a border along addRect(0, 0, w, h). The left and top edges
    # of that rect land on real pixels; the right and bottom fall at x = w and
    # y = h, one pixel outside the widget, and are clipped away. The outermost
    # column and row are then covered by neither the content nor the border, so
    # they show the pane behind the bar.
    #
    # The result is a border on two sides and bare background on the other two,
    # which is unmissable once the bar is filled. The geometry is C++ and a theme
    # supplies borderColor() and nothing else, so the only fix is to stop the two
    # drawn edges standing out: matching them to the pane makes all four agree.
    "PiecesBar.Border": "panel",
    # $progress-fill: the palette's accent, darkened. The bar has to satisfy two
    # things at once. It must match the variant, which a fixed blue did not --
    # that was the first report. And white has to be readable on it, because
    # progressbarpainter.cpp draws the percentage in Palette.HighlightedText
    # straight over the fill -- using the accent raw measured 1.79:1 on slate,
    # which was the second report. A darkened accent is the only value that does
    # both. The pieces bar follows it because they measure the same thing.
    "PiecesBar.Piece": "progress-fill",
    # Follows the palette: a lighter shade of the fill where the palette has an
    # accent, a dimmer neutral in Graphite where it does not.
    "PiecesBar.PartialPiece": "progress-partial",
    # The trough, not $panel. With the border above no longer visible, a bar
    # filled with the pane's own colour would vanish entirely when empty, and the
    # properties pane opens empty on every launch. On the trough it stays legible
    # as a recessed slot.
    "PiecesBar.MissingPiece": "nova-progress-trough",
    "ProgressBar": "progress-fill",
}

DECL = re.compile(r"\s*\$([\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;")


def palette_names() -> list[str]:
    return json.loads(VARIANTS.read_text(encoding="utf-8"))["axes"]["palette"]["values"]


def read_scss_colors(path: Path) -> dict[str, str]:
    """Parse `$name: #hex;` declarations, ignoring commented-out lines."""
    colors = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = DECL.match(line.split("//")[0])
        if match:
            colors[match.group(1)] = match.group(2).lower()
    return colors


def palette_colors(name: str) -> dict[str, str]:
    """The shared state colours, then the palette's own, which may override."""
    colors = read_scss_colors(PALETTE_DIR / "_states.scss")
    fragment = PALETTE_DIR / f"_{name}.scss"
    if not fragment.exists():
        sys.stderr.write(
            f"[error] no palette fragment at {fragment}\n"
            f"        variants.json lists '{name}' on the palette axis.\n")
        sys.exit(1)
    colors.update(read_scss_colors(fragment))
    return colors


def build_config(name: str, colors: dict[str, str]) -> dict:
    missing = sorted({v for v in MAPPING.values() if v not in colors})
    if missing:
        sys.stderr.write(
            f"[error] palette '{name}' does not define primitives the MAPPING needs:\n")
        for var in missing:
            sys.stderr.write(f"          ${var}\n")
        sys.exit(1)

    return {"colors": {key: colors[var] for key, var in MAPPING.items()}}


def render(name: str) -> str:
    return json.dumps(build_config(name, palette_colors(name)), indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palette", help="only this palette (default: all of them)")
    parser.add_argument(
        "--check", action="store_true",
        help="verify the configs match the palettes instead of rewriting them")
    args = parser.parse_args()

    names = [args.palette] if args.palette else palette_names()
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    stale, written, count = [], 0, 0
    for name in names:
        rendered = render(name)
        target = CONFIG_DIR / f"{name}.json"
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        count = rendered.count(": ")

        if args.check:
            if current != rendered:
                stale.append(target)
            continue

        if current != rendered:
            target.write_text(rendered, encoding="utf-8")
            written += 1

    if args.check:
        if stale:
            sys.stderr.write("[error] stale config(s). Regenerate with:\n")
            sys.stderr.write("          python src/nova-dark/scripts/generate-config.py\n")
            for path in stale:
                sys.stderr.write(f"          {path.name}\n")
            sys.exit(1)
        print(f"{len(names)} config(s) up to date ({count} colours each)")
        return

    if written:
        print(f"regenerated {written} of {len(names)} config(s) ({count} colours each)")
    else:
        print(f"{len(names)} config(s) already match the palettes ({count} colours each)")


if __name__ == "__main__":
    main()
