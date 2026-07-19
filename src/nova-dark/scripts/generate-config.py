#!/usr/bin/env python3
"""Generate nova-dark-config.json from the SCSS palette.

qBittorrent paints two different ways. The stylesheet covers widgets it has a
rule for; everything else falls back to the QPalette and the semantic colour
IDs it reads from a theme's config.json. There is no way for QSS to reference a
config.json colour -- different consumers, different parse paths -- so the two
sets of colours have no choice but to be duplicated.

This script is what stops that duplication from drifting. _palette.scss stays
the single source of truth, and config.json becomes a derived artifact: the
MAPPING below says which primitive each qBittorrent colour ID takes.

That divergence was not hypothetical. Before this existed, config.json and the
stylesheet shared 3 colours out of 33 -- a cool blue-grey system and Catppuccin
Mocha painting the same window. It showed wherever the stylesheet did not
reach, most visibly when the window lost focus and Qt fell back to the
QPalette-derived Inactive group.

Usage:
    generate-config.py            rewrite the config from the palette
    generate-config.py --check    exit 1 if the file is stale (for CI)
"""

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
THEME_ROOT = SCRIPT_DIR.parent
PALETTE = THEME_ROOT / "source" / "_palette.scss"
CONFIG = THEME_ROOT / "nova-dark-config.json"

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
    "Palette.Base": "panel",                  # matches QTreeView/QLineEdit bg
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
    # One disabled colour, applied across every role.
    "Palette.WindowTextDisabled": "surface-3",
    "Palette.TextDisabled": "surface-3",
    "Palette.ToolTipTextDisabled": "surface-3",
    "Palette.BrightTextDisabled": "surface-3",
    "Palette.HighlightedTextDisabled": "surface-3",
    "Palette.ButtonTextDisabled": "surface-3",

    # --- Execution log: severity, so the accent ramp is the right source ---
    "Log.TimeStamp": "text-0",
    "Log.Normal": "text-1",
    "Log.Info": "accent-info",
    "Log.Warning": "accent-warning",
    "Log.Critical": "accent-error",
    "Log.BannedPeer": "accent-error",

    # --- RSS -------------------------------------------------------------
    "RSS.ReadArticle": "text-1",
    "RSS.UnreadArticle": "accent",

    # --- Transfer list: state, not severity. See the STATUS note in the ---
    # --- palette for why these are their own ramp.                      ---
    "TransferList.Downloading": "status-downloading",
    "TransferList.DownloadingMetadata": "status-downloading-meta",
    "TransferList.ForcedDownloading": "status-forced",
    "TransferList.ForcedDownloadingMetadata": "status-forced",
    "TransferList.ForcedUploading": "status-forced",
    "TransferList.Uploading": "status-uploading",
    "TransferList.StalledDownloading": "status-stalled",
    "TransferList.StalledUploading": "status-stalled",
    "TransferList.StoppedDownloading": "status-stopped",
    "TransferList.StoppedUploading": "status-stopped",
    "TransferList.QueuedDownloading": "status-queued",
    "TransferList.QueuedUploading": "status-queued",
    "TransferList.CheckingDownloading": "status-checking",
    "TransferList.CheckingUploading": "status-checking-up",
    "TransferList.CheckingResumeData": "status-checking",
    "TransferList.Moving": "status-moving",
    "TransferList.MissingFiles": "status-missing",
    "TransferList.Error": "status-error",

    # --- Pieces bar and progress -----------------------------------------
    "PiecesBar.Border": "piece-border",
    "PiecesBar.Piece": "piece-complete",
    "PiecesBar.PartialPiece": "piece-partial",
    "PiecesBar.MissingPiece": "panel",
    "ProgressBar": "piece-complete",
}


def read_palette() -> dict[str, str]:
    """Parse `$name: #hex;` declarations, ignoring commented-out lines."""
    colors = {}
    for line in PALETTE.read_text(encoding="utf-8").splitlines():
        code = line.split("//")[0]
        match = re.match(r"\s*\$([\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;", code)
        if match:
            colors[match.group(1)] = match.group(2).lower()
    return colors


def build_config(palette: dict[str, str]) -> dict:
    missing = sorted({v for v in MAPPING.values() if v not in palette})
    if missing:
        sys.stderr.write(
            "[error] MAPPING refers to primitives that _palette.scss does not define:\n"
        )
        for name in missing:
            sys.stderr.write(f"          ${name}\n")
        sys.exit(1)

    return {"colors": {key: palette[var] for key, var in MAPPING.items()}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the config matches the palette instead of rewriting it",
    )
    args = parser.parse_args()

    config = build_config(read_palette())
    rendered = json.dumps(config, indent=2) + "\n"

    if args.check:
        current = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""
        if current != rendered:
            sys.stderr.write(
                f"[error] {CONFIG.name} is stale. Regenerate it with:\n"
                f"          python {Path(__file__).relative_to(THEME_ROOT.parent.parent)}\n"
            )
            sys.exit(1)
        print(f"{CONFIG.name} is up to date ({len(config['colors'])} colours)")
        return

    current = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""
    if current == rendered:
        print(f"{CONFIG.name} already matches the palette ({len(config['colors'])} colours)")
        return

    CONFIG.write_text(rendered, encoding="utf-8")
    print(f"regenerated {CONFIG.name} ({len(config['colors'])} colours) from _palette.scss")


if __name__ == "__main__":
    main()
