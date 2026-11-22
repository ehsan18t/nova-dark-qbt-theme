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
INDICATOR = re.compile(r"^(QCheckBox|QRadioButton)::indicator(.*)$")
PSEUDO = re.compile(r"(?<!:):(?!:)(!?)([a-z-]+)")

PROP_PATTERNS = {
    "border": r"^border(-left)?\s*:",
    "background": r"^background(-color)?\s*:",
    "image": r"^image\s*:",
}

INDICATORS = ("QCheckBox", "QRadioButton")
CHECKED_COMPOUND_STATES = [
    ("checked hover", {"checked", "hover"}),
    ("checked focus", {"checked", "focus"}),
    ("checked focus hover", {"checked", "focus", "hover"}),
]


def _subcontrol_rules(stylesheet: str, selector_re: re.Pattern[str], prop: str):
    """(type, positive pseudo-states, negated states, value, depth, order, selector)."""
    pattern = PROP_PATTERNS[prop]
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
            parsed = selector_re.match(selector)
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


def item_rules(stylesheet: str, prop: str):
    """(type, positive pseudo-states, negated states, value, depth, order, selector)."""
    return _subcontrol_rules(stylesheet, ITEM, prop)


def indicator_rules(stylesheet: str, prop: str):
    """(type, positive pseudo-states, negated states, value, depth, order, selector)."""
    return _subcontrol_rules(stylesheet, INDICATOR, prop)


def _winner(rules, widget, base, state):
    matching = [
        r for r in rules
        if r[0] in (widget, base) and r[1] <= state and not (r[2] & state)
    ]
    if not matching:
        return None
    # CSS2.1: specificity first, then source order.
    return max(matching, key=lambda r: (r[4], r[5]))


def _check_indicator_prop(rules, widget, label, state, expected_win, prop_name):
    win = _winner(rules, widget, widget, state)
    expected_val = expected_win[3] if expected_win else None
    actual_val = win[3] if win else None
    if expected_val is None or actual_val != expected_val:
        actual_desc = f"`{win[6]}` (`{actual_val}`)" if win else "none"
        return (
            f"{widget}::indicator [{label}]: {prop_name} -- "
            f"{actual_desc} does not match expected `{expected_val}`"
        )
    return None


def check_indicators(text: str) -> list[str]:
    """Verify QCheckBox/QRadioButton ::indicator checked/hover/disabled cascades."""
    backgrounds = indicator_rules(text, "background")
    images = indicator_rules(text, "image")
    failures = []

    for widget in INDICATORS:
        checked_bg = _winner(backgrounds, widget, widget, {"checked"})
        checked_img = _winner(images, widget, widget, {"checked"})
        for label, state in CHECKED_COMPOUND_STATES:
            for rules, expected, prop_name in (
                (backgrounds, checked_bg, "background"),
                (images, checked_img, "image"),
            ):
                err = _check_indicator_prop(
                    rules, widget, label, state, expected, prop_name
                )
                if err:
                    failures.append(err)

        hover_bg = _winner(backgrounds, widget, widget, {"hover"})
        err = _check_indicator_prop(
            backgrounds, widget, "focus hover", {"focus", "hover"},
            hover_bg, "background"
        )
        if err:
            failures.append(err)

        disabled_bg = _winner(backgrounds, widget, widget, {"disabled"})
        err = _check_indicator_prop(
            backgrounds, widget, "checked disabled", {"checked", "disabled"},
            disabled_bg, "background"
        )
        if err:
            failures.append(err)

    return failures


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

    failures.extend(check_indicators(text))
    return failures


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: check_cascade.py <compiled.qss> [...]")

    problems = []
    for arg in sys.argv[1:]:
        for failure in check(Path(arg)):
            problems.append(f"{Path(arg).name}: {failure}")

    if problems:
        sys.stderr.write("[error] a stylesheet rule loses the cascade:\n")
        for line in problems:
            sys.stderr.write(f"          {line}\n")
        sys.stderr.write(
            "        Fix the winning specificity/order in _widgets.scss.\n")
        sys.exit(1)

    checked = len(sys.argv) - 1
    print(f"sidebar rail/fill ({len(STATES)} states x {len(SIDEBAR)} widgets) "
          f"and indicator cascades ({len(INDICATORS)} widgets) resolve "
          f"correctly across {checked} stylesheet(s)")


if __name__ == "__main__":
    main()
