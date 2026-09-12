#!/usr/bin/env python3
"""Verify the sidebar selection rail actually wins the cascade, in every state.

WHY THIS EXISTS

The rail vanished while the sidebar had focus and reappeared once focus moved
away. Nothing was wrong with the rail rule; it was out-specified. A selector
like `TagFilterWidget::item:selected` carries one pseudo-class, while the
generic reset rules in _widgets.scss reach three of them:

    QTreeView::item:selected:active:only-one { border-left: 0; }

So the instant a row was genuinely selected, with its widget active, the generic
rule won and zeroed the border. Drop focus, `:active` stops matching, the rail
comes back. It looked intermittent; it was deterministic.

That class of bug is invisible in the source and invisible in the compiled
stylesheet. It only shows up if you resolve the cascade the way Qt does, which
is what this script does: for every state a sidebar item can occupy, it finds
the rule that actually wins on border-left and checks it is the sidebar's.

Run by scripts/build.py on every build. If you add a reset in a new item state,
this fails and names the state rather than letting the rail silently disappear
there.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# The five filter widgets, and the generic class each also matches as.
SIDEBAR = {
    "StatusFilterWidget": "QListView",
    "TrackersFilterWidget": "QListView",
    "TrackerStatusFilterWidget": "QListView",
    "CategoryFilterWidget": "QTreeView",
    "TagFilterWidget": "QTreeView",
}

# Every state an item can actually occupy. `active` means the view has focus --
# the one that broke.
STATES = [
    ("rest", set()),
    ("rest first", {"first"}),
    ("rest last", {"last"}),
    ("rest only-one", {"only-one"}),
    ("rest focus", {"focus"}),
    ("rest hover", {"hover"}),
    ("rest hover first", {"hover", "first"}),
    ("rest hover only-one", {"hover", "only-one"}),
    ("selected", {"selected"}),
    ("selected active", {"selected", "active"}),
    ("selected active first", {"selected", "active", "first"}),
    ("selected active last", {"selected", "active", "last"}),
    ("selected active only-one", {"selected", "active", "only-one"}),
    ("selected active hover", {"selected", "active", "hover"}),
    ("selected hover", {"selected", "hover"}),
    ("selected only-one", {"selected", "only-one"}),
]

RULE = re.compile(r"([^{}]+)\{([^}]*)\}")
ITEM = re.compile(r"^(\w+)::item(.*)$")
PSEUDO = re.compile(r"(?<!:):(?!:)(!?)([a-z-]+)")


def item_rules(stylesheet: str, prop: str):
    """(type, positive pseudo-states, negated states, value, depth, order).

    prop is "border" (matching border / border-left) or "background".
    """
    pattern = (r"^border(-left)?\s*:" if prop == "border"
               else r"^background(-color)?\s*:")
    out, order = [], 0
    for match in RULE.finditer(stylesheet):
        value = None
        for decl in match.group(2).split(";"):
            decl = decl.strip()
            if re.match(pattern, decl):
                value = decl.split(":", 1)[1].strip()
        if value is None:
            continue
        for selector in match.group(1).split(","):
            selector = " ".join(selector.split())
            order += 1
            parsed = ITEM.match(selector)
            if not parsed:
                continue
            raw = PSEUDO.findall(parsed.group(2))
            out.append((
                parsed.group(1),
                {name for bang, name in raw if not bang},
                {name for bang, name in raw if bang},
                value, len(raw), order, selector,
            ))
    return out


def _winner(rules, widget, base, state):
    matching = [
        r for r in rules
        if r[0] in (widget, base) and r[1] <= state and not (r[2] & state)
    ]
    if not matching:
        return None
    # CSS2.1: specificity first, then source order.
    return max(matching, key=lambda r: (r[4], r[5]))


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    borders = item_rules(text, "border")
    backgrounds = item_rules(text, "background")
    failures = []

    for widget, base in SIDEBAR.items():
        for label, state in STATES:
            # --- the selection rail -------------------------------------
            win = _winner(borders, widget, base, state)
            if win:
                owner, value, selector = win[0], win[3], win[6]
                wants_rail = "selected" in state
                if owner != widget or ("#" in value) != wants_rail:
                    failures.append(
                        f"{widget} [{label}]: rail -- `{selector}` wins with "
                        f"`{value}`, so it is "
                        f"{'missing' if wants_rail else 'drawn when it should not be'}")

            # --- the fill, but only where the sidebar owns one ----------
            # A resting row has no fill of its own; it shows the pane through.
            if not ({"hover", "selected"} & state):
                continue
            win = _winner(backgrounds, widget, base, state)
            if win and win[0] != widget:
                failures.append(
                    f"{widget} [{label}]: fill -- generic `{win[6]}` wins with "
                    f"`{win[3]}`, so the sidebar's own hover/selection colour "
                    f"is overridden")
    return failures


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: check_cascade.py <compiled.qss> [...]")

    problems = []
    for arg in sys.argv[1:]:
        for failure in check(Path(arg)):
            problems.append(f"{Path(arg).name}: {failure}")

    if problems:
        sys.stderr.write("[error] a sidebar rule loses the cascade:\n")
        for line in problems:
            sys.stderr.write(f"          {line}\n")
        sys.stderr.write(
            "        Add that state to one of the $sidebar-*-states lists in\n"
            "        _widgets.scss, in the group whose fill it should take.\n")
        sys.exit(1)

    checked = len(sys.argv) - 1
    print(f"sidebar rail and fill resolve correctly in {len(STATES)} states "
          f"x {len(SIDEBAR)} widgets, across {checked} stylesheet(s)")


if __name__ == "__main__":
    main()
