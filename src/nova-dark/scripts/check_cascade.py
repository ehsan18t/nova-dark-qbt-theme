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
COMBOBOX = re.compile(r"^(QComboBox)((?::!?[a-z-]+)*)$")
PUSHBUTTON = re.compile(r"^(QPushButton)((?::!?[a-z-]+)*)$")
SLIDER = re.compile(r"^QSlider::(groove|handle|sub-page)(.*)$")
TAB = re.compile(r"^(QTabBar)::tab(.*)$")
PSEUDO = re.compile(r"(?<!:):(?!:)(!?)([a-z-]+)")

PROP_PATTERNS = {
    "border": r"^border(-left)?\s*:",
    "border_shorthand": r"^border\s*:",
    "border_color": r"^border-color\s*:",
    "background": r"^background(-color)?\s*:",
    "color": r"^color\s*:",
    "image": r"^image\s*:",
    "padding_bottom": r"^padding-bottom\s*:",
    "margin_bottom": r"^margin-bottom\s*:",
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


def widget_rules(stylesheet: str, widget_re: re.Pattern[str], prop: str):
    """(type, positive pseudo-states, negated states, value, depth, order, selector)."""
    return _subcontrol_rules(stylesheet, widget_re, prop)


def _winner(rules, widget, base, state):
    matching = [
        r for r in rules
        if r[0] in (widget, base) and r[1] <= state and not (r[2] & state)
    ]
    if not matching:
        return None
    # CSS2.1: specificity first, then source order.
    return max(matching, key=lambda r: (r[4], r[5]))


def _check_match(rules, widget, prefix, label, state, expected_win, prop_name):
    win = _winner(rules, widget, widget, state)
    expected_val = expected_win[3] if expected_win else None
    actual_val = win[3] if win else None
    if expected_val is None or actual_val != expected_val:
        actual_desc = f"`{win[6]}` (`{actual_val}`)" if win else "none"
        return (
            f"{prefix} [{label}]: {prop_name} -- "
            f"{actual_desc} does not match expected `{expected_val}`"
        )
    return None


def check_indicators(text: str) -> list[str]:
    """Verify QCheckBox/QRadioButton ::indicator checked/hover/disabled cascades."""
    backgrounds = indicator_rules(text, "background")
    images = indicator_rules(text, "image")
    failures = []

    for widget in INDICATORS:
        prefix = f"{widget}::indicator"
        checked_bg = _winner(backgrounds, widget, widget, {"checked"})
        checked_img = _winner(images, widget, widget, {"checked"})
        for label, state in CHECKED_COMPOUND_STATES:
            for rules, expected, prop_name in (
                (backgrounds, checked_bg, "background"),
                (images, checked_img, "image"),
            ):
                err = _check_match(
                    rules, widget, prefix, label, state, expected, prop_name
                )
                if err:
                    failures.append(err)

        hover_bg = _winner(backgrounds, widget, widget, {"hover"})
        err = _check_match(
            backgrounds, widget, prefix, "focus hover", {"focus", "hover"},
            hover_bg, "background"
        )
        if err:
            failures.append(err)

        disabled_bg = _winner(backgrounds, widget, widget, {"disabled"})
        err = _check_match(
            backgrounds, widget, prefix, "checked disabled", {"checked", "disabled"},
            disabled_bg, "background"
        )
        if err:
            failures.append(err)

    return failures


def check_combobox(text: str) -> list[str]:
    """Verify QComboBox focus/hover/on/editable cascades."""
    backgrounds = widget_rules(text, COMBOBOX, "background")
    border_colors = widget_rules(text, COMBOBOX, "border_color")
    failures = []

    rest_bg = _winner(backgrounds, "QComboBox", "QComboBox", set())
    hover_bg = _winner(backgrounds, "QComboBox", "QComboBox", {"hover"})
    hover_bc = _winner(border_colors, "QComboBox", "QComboBox", {"hover"})
    on_bg = _winner(backgrounds, "QComboBox", "QComboBox", {"on"})
    on_bc = _winner(border_colors, "QComboBox", "QComboBox", {"on"})
    disabled_bg = _winner(backgrounds, "QComboBox", "QComboBox", {"disabled"})

    checks = [
        (backgrounds, "focus hover", {"focus", "hover"}, hover_bg, "background"),
        (border_colors, "focus hover", {"focus", "hover"}, hover_bc, "border-color"),
        (backgrounds, "focus", {"focus"}, rest_bg, "background"),
        (backgrounds, "on focus hover", {"on", "focus", "hover"}, on_bg, "background"),
        (border_colors, "on focus hover", {"on", "focus", "hover"}, on_bc, "border-color"),
        (backgrounds, "editable disabled", {"editable", "disabled"}, disabled_bg, "background"),
    ]
    for rules, label, state, expected, prop_name in checks:
        err = _check_match(rules, "QComboBox", "QComboBox", label, state, expected, prop_name)
        if err:
            failures.append(err)
    return failures


def check_pushbutton(text: str) -> list[str]:
    """Verify QPushButton focus/pressed/default/disabled and status-bar priority."""
    backgrounds = widget_rules(text, PUSHBUTTON, "background")
    border_colors = widget_rules(text, PUSHBUTTON, "border_color")
    colors = widget_rules(text, PUSHBUTTON, "color")
    failures = []

    hover_bg = _winner(backgrounds, "QPushButton", "QPushButton", {"hover"})
    pressed_bg = _winner(backgrounds, "QPushButton", "QPushButton", {"pressed"})
    pressed_bc = _winner(border_colors, "QPushButton", "QPushButton", {"pressed"})
    pressed_fg = _winner(colors, "QPushButton", "QPushButton", {"pressed"})
    rest_fg = _winner(colors, "QPushButton", "QPushButton", set())
    disabled_bg = _winner(backgrounds, "QPushButton", "QPushButton", {"disabled"})

    if not pressed_bc:
        failures.append("QPushButton [pressed]: missing explicit `border-color`")
    if not pressed_fg or (rest_fg and pressed_fg[3] == rest_fg[3]):
        failures.append("QPushButton [pressed]: missing highlight `color`")

    checks = [
        ("pressed focus", {"pressed", "focus"}, pressed_bg),
        ("hover focus", {"hover", "focus"}, hover_bg),
        ("default pressed", {"default", "pressed"}, pressed_bg),
        ("default disabled", {"default", "disabled"}, disabled_bg),
    ]
    for label, state, expected in checks:
        err = _check_match(
            backgrounds, "QPushButton", "QPushButton", label, state, expected, "background"
        )
        if err:
            failures.append(err)

    for prop in ("background", "border_color"):
        for r in widget_rules(text, PUSHBUTTON, prop):
            if r[4] >= 2 and ({"hover", "focus"} <= r[1] or {"pressed", "focus"} <= r[1]):
                failures.append(
                    f"QPushButton: `{r[6]}` has specificity {r[4]} pseudos and "
                    f"would override `QStatusBar QPushButton` (specificity 0x12)"
                )
    return failures


def check_slider(text: str) -> list[str]:
    """Verify QSlider disabled/hover/pressed cascades and palette purity."""
    backgrounds = widget_rules(text, SLIDER, "background")
    failures = []

    for part in ("groove", "handle", "sub-page"):
        prefix = f"QSlider::{part}"
        horiz_bg = _winner(backgrounds, part, part, {"horizontal"})
        disabled_bg = _winner(backgrounds, part, part, {"disabled"})
        err = _check_match(
            backgrounds, part, prefix, "horizontal disabled",
            {"horizontal", "disabled"}, disabled_bg, "background"
        )
        if err:
            failures.append(err)
        elif horiz_bg and disabled_bg and horiz_bg[3] == disabled_bg[3]:
            failures.append(
                f"{prefix} [horizontal disabled]: background `{disabled_bg[3]}` "
                f"is identical to enabled `horizontal`"
            )

    handle_horiz = _winner(backgrounds, "handle", "handle", {"horizontal"})
    for label, state in (("horizontal hover", {"horizontal", "hover"}),
                         ("horizontal pressed", {"horizontal", "pressed"})):
        win = _winner(backgrounds, "handle", "handle", state)
        if not win or not handle_horiz or win[3] == handle_horiz[3]:
            failures.append(
                f"QSlider::handle [{label}]: background `{win[3] if win else None}` "
                f"does not differ from resting `horizontal` (`{handle_horiz[3] if handle_horiz else None}`)"
            )
        if win and win[3].lower() == "#bfb6f6":
            failures.append(
                f"QSlider::handle [{label}]: hardcoded `#bfb6f6` lavender leak"
            )

    return failures


def check_listview_and_tabbar(text: str) -> list[str]:
    """Verify QListView::item:hover border reset and QTabBar::tab top symmetry."""
    failures = []

    lv_borders = item_rules(text, "border_shorthand")
    lv_hover = _winner(lv_borders, "QListView", "QListView", {"hover"})
    if not lv_hover or lv_hover[3] != "none":
        val = f"`{lv_hover[6]}` (`{lv_hover[3]}`)" if lv_hover else "none"
        failures.append(
            f"QListView::item [hover]: border -- {val} must resolve to `none`"
        )

    item_colors = item_rules(text, "color")
    for view in ("QListView", "QTreeView"):
        for label, state in (("rest", set()), ("hover", {"hover"})):
            win_color = _winner(item_colors, view, view, state)
            if win_color:
                failures.append(
                    f"{view}::item [{label}]: `{win_color[6]}` sets `color: "
                    f"{win_color[3]}`, overriding Qt::ForegroundRole colours from config.json"
                )

    tab_pb = widget_rules(text, TAB, "padding_bottom")
    win_pb = _winner(tab_pb, "QTabBar", "QTabBar", {"top", "selected"})
    if win_pb:
        failures.append(
            f"QTabBar::tab [top selected]: `{win_pb[6]}` sets `padding-bottom: "
            f"{win_pb[3]}`, breaking vertical padding symmetry"
        )

    tab_mb = widget_rules(text, TAB, "margin_bottom")
    win_mb = _winner(tab_mb, "QTabBar", "QTabBar", {"top"})
    if win_mb and win_mb[3] not in ("0", "0px"):
        failures.append(
            f"QTabBar::tab [top]: `{win_mb[6]}` leaks `margin-bottom: {win_mb[3]}`"
        )

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
    failures.extend(check_combobox(text))
    failures.extend(check_pushbutton(text))
    failures.extend(check_slider(text))
    failures.extend(check_listview_and_tabbar(text))
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
          f"and widget cascades (indicators, combo, button, slider, list, tab) "
          f"resolve correctly across {checked} stylesheet(s)")


if __name__ == "__main__":
    main()
