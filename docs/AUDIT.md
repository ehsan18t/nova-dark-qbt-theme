# Nova Dark Theme — Full Source Audit

**Date:** 2026-11-23  
**Scope:** SCSS sources (`src/nova-dark/source/`), all 4 compiled stylesheets (`build/qss/*.qss`), build & helper scripts (`scripts/build.py`, `src/nova-dark/scripts/`), control SVGs (`src/common/controls/`), icon manifest & docs (`src/nova-dark/icons/modern/`, `README.md`), and upstream `qbittorrent/qBittorrent` (`master`) parity.

## Executive Summary

- **Upstream qBittorrent parity is complete:** All **56/56** colour IDs in upstream `src/gui/uithemecommon.h` are mapped in [`src/nova-dark/scripts/generate-config.py`](../src/nova-dark/scripts/generate-config.py) and generated across all 4 palettes, and **91/94** icons in upstream `src/icons/` are covered (omitting only `mascot`, `qbittorrent_mac`, and `splash`).
- **6 real QSS cascade & styling bugs** remain in [`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss), mostly caused by higher-specificity legacy rules in the BaseTheme half (L1–L974) beating lower-specificity rules in the Nova Overrides half (L975–L2182).
- **81 exact selectors are duplicated** in the compiled QSS, alongside **4 dead/invalid QSS rules**, **16 unused SCSS variables**, **4 no-op self-assignments**, and **7 script/documentation drift items**.

| Category | Validated Items | Primary Location(s) |
| :--- | :---: | :--- |
| High-priority visual & QSS cascade bugs | 6 | `src/nova-dark/source/_widgets.scss` |
| Duplicated selectors & dead/invalid QSS | 5 | `src/nova-dark/source/_widgets.scss` |
| Unused SCSS variables & no-ops | 20 | `_tokens.scss`, `_states.scss`, palettes, `_comfortable.scss` |
| Script & documentation drift | 7 | `generate-config.py`, `recolour_icons.py`, `download_phosphor_icons.py`, `ICON-LIST.md`, `README.md`, `_widgets.scss` |
| Optional enhancements | 2 | `check_cascade.py`, Qt 6.5+ `placeholder-text-color` |

---

## 1. High-Priority Visual & QSS Cascade Bugs

> **Qt QSS specificity refresher** (`qtbase` `qcssparser.cpp`, `Selector::specificity()`):
> - `+0x01` per type selector (`QPushButton` and `StatusFilterWidget` carry equal weight `0x01`).
> - `+0x10` per subcontrol (`::indicator`, `::item`), pseudo-state (`:hover`, `:focus`, `:horizontal`), or attribute selector (`[popupMode="1"]`).
> - `+0x100` per ID selector (`#lineEditSearchPattern`).
> - On equal specificity, the rule appearing **later** in source order wins.

### 1.1 `QComboBox` focus/hover and editable state overrides

- **Files:** [`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss) (L612, L869–L927 vs. L1570–L1591)
- **Bug:**
  1. Legacy `QComboBox:focus:hover` (`0x21`, L879–L882) sets `background-color: $button-focus-hover-bg;` (`$surface-1`) and `border-color: $button-focus-hover-border;` (`$accent`), out-specifying Nova's `QComboBox:hover`, `QComboBox:focus`, and `QComboBox:on` (`0x11` each, L1579–L1591). Once a combo box receives focus (e.g., on click), hovering it falls back to the legacy `$surface-1` fill and `$accent` border instead of Nova's `$nova-elevated` / `$surface-2`.
  2. Legacy `QComboBox:focus` (L873–L875) sets `background-color: $button-focus;` (`$surface-0`), which Nova's `QComboBox:focus` (L1584–L1586, `border-color` only) never resets.
  3. Editable combo boxes are additionally overridden by legacy `QComboBox:editable` (L612, `0x11`), `QComboBox:editable:focus` (L896/L925, `0x21`), `QComboBox:editable:hover` (L910, `0x21`), and `QComboBox:editable:focus:hover` (L903, `0x31`).
- **Fix:** Remove `QComboBox` from the legacy `:focus` / `:focus:hover` / `:hover` blocks (or explicitly declare the intended `:focus`, `:hover`, `:focus:hover`, `:on`, and `:editable*` states in the Nova `COMBO BOX` section).

### 1.2 `QPushButton` `:pressed:focus` and `:hover:focus` overrides

- **Files:** [`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss) (L264–L278, L1046–L1052, L1649–L1686)
- **Bug:**
  1. On platforms using `Qt::StrongFocus` (Windows/Linux), clicking a button gives it `:focus`, so legacy `QPushButton:pressed:focus` (`0x21`, L274–L278: `background-color: $highlight-bg`, `border-color: $highlight-bg`, `color: $highlight-text`) **always** beats Nova's `QPushButton:pressed` (`0x11`, L1664–L1666: `background-color: $surface-1`). Even on non-focusing clicks, legacy `QPushButton:pressed` (L273) leaks `border-color: $surface-2` and `color: #ffffff` because L1664 only sets `background-color`.
  2. Legacy `QPushButton:hover:focus` (`0x21`, L268–L271: `background-color: $surface-1`, `border-color: $accent`) overrides Nova's `QPushButton:hover` (`0x11`, L1659–L1662: `$surface-0` / `$surface-2`) once a button has focus.
  3. Both legacy `0x21` rules also out-specify `QStatusBar QPushButton:hover` and `QStatusBar QPushButton:pressed` (`0x12`: 2 types + 1 pseudo, L1046–L1052) whenever a status bar button has focus.
  4. When pressing a hovered, focused `:default` button, Nova's `QPushButton:default:hover` (`0x21`, L1684–L1686) ties legacy `QPushButton:pressed:focus` (`0x21`, L274) and wins by source order on `background-color`, preventing pressed feedback.
- **Fix:** Remove the legacy `QPushButton:focus` / `:hover:focus` / `:pressed` / `:pressed:focus` block at L264–L278 and declare any desired `:hover:focus`, `:pressed:focus`, and `:default:pressed` rules directly in the Nova `PUSH BUTTON IMPROVEMENTS` section.

### 1.3 `QSlider` cross-palette violet leak & broken `:disabled` / `:focus` / `:pressed` states

- **Files:** [`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss) (L826–L867 vs. L1833–L1855) and [`src/nova-dark/source/palettes/_states.scss`](../src/nova-dark/source/palettes/_states.scss) (L59)
- **Bug:**
  1. **Cross-palette colour leak:** `QSlider::handle:horizontal:hover` (L1848–L1850) sets `background-color: $accent-lavender;` (`#bfb6f6` from `_states.scss`). Because `$accent-lavender` is a fixed shared colour, hovering a horizontal slider handle turns it **violet** in Graphite (monochrome), Nova (blue), and Slate (teal).
  2. **Broken `:disabled` / `:focus` / `:pressed` states:** `QSlider::groove:horizontal` (L1833), `QSlider::handle:horizontal` (L1839), and `QSlider::sub-page:horizontal` (L1852) each carry specificity `0x21` (1 type + 1 subcontrol + 1 pseudo) and appear *after* the earlier `0x21` rules for `:disabled` (L826, L864), `::handle:focus` (L850), `::handle:hover` (L855), and `::handle:pressed` (L859). As a result, disabled horizontal sliders ignore `:disabled` and remain brightly painted in `$accent`.
- **Fix:** Replace `$accent-lavender` on `QSlider::handle:horizontal:hover` with a palette-derived colour (e.g. `$accent` / `$text-bright` or a hover token per palette), and move/qualify `:disabled`, `:focus`, and `:pressed` rules after `:horizontal` (or include `:horizontal:disabled`, etc.).

### 1.4 `QListView::item:hover` 1px border leak

- **Files:** [`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss) (L303–L306 vs. L1322–L1333, L2067–L2073)
- **Bug:** Legacy `QListView::item:hover` (`0x21`, L303–L306) sets `border: 1px solid $sub-hover;` (`$nova-elevated`). Nova's `QListView::item` resets `border: none;` (`0x11`, L1325), and Nova's `QListView::item:hover` (L1331–L1333) only sets `background-color` without resetting `border`. Hovering any `QListView` item — including sidebar `StatusFilterWidget`, `TrackersFilterWidget`, `TrackerStatusFilterWidget` (whose generated rules only override `border-left`), and `LogListView` — draws a 1px `$nova-elevated` border that mismatches the sidebar's `$sidebar-pane-hover-bg`.
- **Fix:** Remove `border: 1px solid $sub-hover;` from legacy `QListView::item:hover` (L305) or explicitly set `border: none;` on `QListView::item:hover` (L1331) and ensure sidebar list-widget hover states clear top/right/bottom borders.

### 1.5 `QTabBar::tab:top:selected` vertical padding asymmetry & `QTabBar::tab:top` margin leak

- **Files:** [`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss) (L481–L504 vs. L1698–L1716)
- **Bug:** Legacy `QTabBar::tab:top:selected` (`0x31`, L501–L504) sets `padding-bottom: $base-padding * 1.5 + 1;` (`7px` in `comfortable`), out-specifying Nova's `QTabBar::tab` (`0x11`, L1703: `padding: 4px 10px;`). Selected top tabs therefore render with asymmetric vertical padding (`4px` top vs. `7px` bottom). Meanwhile, legacy `QTabBar::tab:top` (`0x21`, L481–L484) leaks `margin-bottom: 1px;` onto unselected top tabs.
- **Fix:** Remove the conflicting legacy `QTabBar::tab:top*` padding/margin rules (or reset them explicitly in Nova's `TAB WIDGET IMPROVEMENTS` block).

### 1.6 `QProgressBar` hardcoded font & dead legacy rule

- **Files:** [`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss) (L802–L804 vs. L990–L1004)
- **Bug:** Legacy `QProgressBar` (L802–L804) sets `font: bold italic large "Times New Roman";` only for Nova (L996) to hardcode `font-family: "Segoe UI", sans-serif;` instead of `$font-family` (`_tokens.scss:L151–L152`), dropping Linux/macOS font fallbacks.
- **Fix:** Remove L802–L804 and use `$font-family` (or inherit from `QObject`) in L990–L1004.

---

## 2. Structural Duplication & Dead / Invalid QSS

### 2.1 BaseTheme + Nova Overrides duplication (81 duplicate exact selectors)

- **Files:** [`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss), `build/qss/*.qss`
- **Finding:** Because `_widgets.scss` still concatenates the legacy BaseTheme rules (L1–L974) with Nova Overrides (L975–L2182), the compiled QSS contains **81** duplicated exact selectors (**100** extra occurrences):
  - **67** selectors appear in both BaseTheme and Nova Overrides.
  - **14** selectors are duplicated within BaseTheme itself (e.g., `QAbstractSpinBox` 4 times, `QTreeView::indicator` 4 times, `QHeaderView::down-arrow` / `::up-arrow`, `QTabBar::tab:top:only-one` / `:bottom:only-one`, `QCheckBox::indicator:focus`).
- **Cascade impact (`QTreeView::item` & sidebar):**
  - In `QTreeView::item` (L1367–L1501), the **12 positional rules** (`:first`, `:last`, `:only-one` combinations) and per-side border/radius resets exist solely to counteract legacy L326–L374, while the **8 non-positional states** (`""`, `:hover`, `:focus`, `:selected`, `:selected:!active`, `:selected:active`, `:selected:hover`, `:selected:active:hover`) actively style `TransferListWidget` and the Content file tree.
  - Removing legacy L326–L374 and Nova's 12 positional resets would eliminate **60 of the 100 generated sidebar selectors** at L2050–L2093 (the 12 positional states × 5 widgets). The remaining **40 selectors** (8 non-positional states × 5 widgets) are still needed because sidebar class selectors tie `QTreeView`/`QListView` on specificity (`0x01`).

### 2.2 Dead & invalid QSS selectors / declarations

| Item | Location | Issue |
| :--- | :--- | :--- |
| `DockTitleBar {}` | `_widgets.scss:L83–L84` | Empty rule block (stripped by `qtsass`). |
| `QAbstractCheckBox` | `_widgets.scss:L743` | Non-existent Qt widget class (Qt uses `QAbstractButton`); emitted verbatim into compiled QSS. |
| `QPushButton[popupMode="1"]`, `QPushButton[popupMode="2"]` | `_widgets.scss:L659–L662` | Invalid selector: `popupMode` is a `QToolButton` property, not `QPushButton`; never matches. |
| `QAbstractScrollArea::corner` | `_widgets.scss:L580–L589` | Declares `border-left` and `border-top` twice inside the same block (L581–L582 and L586–L587); emitted verbatim into compiled QSS. |

---

## 3. Unused SCSS Variables & No-Op Declarations

A full cross-reference across SCSS, Python scripts, and JSON configs shows **0 consumers** for the following declarations:

- **All 4 palette fragments** (`_graphite.scss`, `_nebula.scss`, `_nova.scss`, `_slate.scss`):
  - `$piece-border` (unused since `PiecesBar.Border` switched to `$panel`)
  - `$palette-name` (metadata-only, never read)
  - *Constraint:* `scripts/build.py:check_fragment_parity()` requires all palette fragments to declare identical variable names, so any removal must happen across all 4 palette files together.
- **Density fragment** ([`_comfortable.scss`](../src/nova-dark/source/densities/_comfortable.scss)):
  - `$density-name` (L17; metadata-only, never read)
- **Token layer** ([`_tokens.scss`](../src/nova-dark/source/_tokens.scss)):
  - 13 unused variables: `$base-pressed` (L10), `$control-icon-disabled` (L94), `$tab-selected` (L107), `$tab-hover` (L110), `$radio` (L118), `$accent-primary` (L145), `$font-size-bigger` (L153), `$font-size-big` (L154), `$font-size-normal` (L155), `$font-size-medium` (L156), `$font-size-extra-small` (L158), `$font-size-qslider-groove` (L159), `$font-size-qslider-handle` (L160).
  - 4 no-op self-assignments at L146–L149: `$accent-success: $accent-success;`, `$accent-warning: $accent-warning;`, `$accent-error: $accent-error;`, `$accent-info: $accent-info;`.
- **Shared state colours** ([`_states.scss`](../src/nova-dark/source/palettes/_states.scss)):
  - `$accent-lavender` (L59) is currently referenced **only** by the buggy `QSlider::handle:horizontal:hover` rule (`_widgets.scss:L1849`) and becomes completely unused once Section 1.3 is fixed.

*(Note: `src/common/controls/radio_check_dark.svg` is unreferenced in the 4 current compiled stylesheets because every current palette's `$check-fill` has YIQ > 128 and selects `on_light`, **but it is intentional by design** per [`_tokens.scss`](../src/nova-dark/source/_tokens.scss) L123–L141 as the `"dark"` branch for future dark `$check-fill` palettes. Keep it.)*

---

## 4. Build Scripts & Documentation Drift

1. **[`src/nova-dark/scripts/generate-config.py`](../src/nova-dark/scripts/generate-config.py) (L249):** `count = rendered.count(": ")` prints `57 colours each` instead of `56` because it also counts the top-level `"colors": {` line. Replace with `len(MAPPING)`.
2. **[`src/nova-dark/scripts/generate-config.py`](../src/nova-dark/scripts/generate-config.py) (L132):** Stale comment says Graphite's accent is blue; Graphite now uses neutral `#6e727c` (`_graphite.scss:L55`).
3. **[`src/nova-dark/scripts/recolour_icons.py`](../src/nova-dark/scripts/recolour_icons.py) (L24, L56, L108):**
   - L24 docstring example says `("edit-find" -> "accent")`, whereas `edit-find` uses `"default"`.
   - L56 `DEFAULT_ROLE = "default"` is unused (and L53–L55 comment describes unused treatment roles, not `DEFAULT_ROLE`).
   - L108 `recolour(...) -> int` has an incorrect return annotation; it returns `tuple[int, int]` (`return len(svgs), verbatim` at L168).
4. **[`src/nova-dark/scripts/download_phosphor_icons.py`](../src/nova-dark/scripts/download_phosphor_icons.py) (L93–L98):** `INNER_CHECK_ICONS` only generates `checkbox_check_dark` and `radio_check_dark`, omitting `checkbox_check_on_light` and `radio_check_on_light` (`fill="#101114"` in `src/common/controls/`).
5. **[`src/nova-dark/icons/modern/ICON-LIST.md`](../src/nova-dark/icons/modern/ICON-LIST.md) (L67):** `edit-find` lists role `` `upload` ``, while `icon-manifest.json` (L69) and `download_phosphor_icons.py` (L156) assign `default`. (Confirmed as the only discrepancy across all 88 entries.)
6. **[`README.md`](../README.md) (L116, L163):**
   - L116 says `build.bat` drops outputs in `dist\` instead of `build\dist\` (`scripts/build.py:L61`).
   - L163 repeats the stale claim that Graphite's accent is blue.
7. **[`src/nova-dark/source/_widgets.scss`](../src/nova-dark/source/_widgets.scss) (L6):** Comment says `"82 selectors were styled in BOTH files"`, whereas 67 selectors appear in both halves (81 duplicated total).

---

## 5. Optional Stability & Theme Enhancements

- **Expand [`src/nova-dark/scripts/check_cascade.py`](../src/nova-dark/scripts/check_cascade.py):** Currently verifies sidebar rows (`16` states × `5` widgets) and `QCheckBox`/`QRadioButton` indicators. Extending it to assert winning rules for `QComboBox`, `QPushButton`, `QSlider`, `QListView::item`, and `QTabBar::tab` will prevent future cascade regressions at build time.
- **`placeholder-text-color` in QSS (Qt 6.5+ only):** qBittorrent's `config.json` does not expose `Palette.PlaceholderText` (`uithemecommon.h` lists 56 keys, without `PlaceholderText`). Verified in `qt/qtbase` `qcssparser.cpp` that QSS `placeholder-text-color` was introduced in **Qt 6.5** (not present in Qt 5.15, 6.2, or 6.4). For qBittorrent 5.x (Qt 6.5+), setting `placeholder-text-color: $text-0;` on `QLineEdit`, `QTextEdit`, and `QComboBox` ensures consistent placeholder contrast, though older Qt 5.15 / 6.0–6.4 builds will log `Unknown property placeholder-text-color` and ignore it.

---

## 6. Recommended Implementation Phases

1. **Phase 1 — Targeted Fixes & Cleanup (Low Risk):**
   - Fix all 6 cascade/styling bugs in Section 1 (`QComboBox`, `QPushButton`, `QSlider`, `QListView::item:hover`, `QTabBar::tab:top*`, `QProgressBar` font).
   - Extend `check_cascade.py` to cover those controls.
   - Remove the 4 dead/invalid QSS rules (Section 2.2) and unused SCSS variables/no-ops (Section 3), keeping `radio_check_dark.svg`.
   - Fix the 7 script & documentation drift items (Section 4).
2. **Phase 2 — Stylesheet Consolidation (Structural Refactor):**
   - Merge the BaseTheme (L1–L974) and Nova Overrides (L975–L2182) halves of `_widgets.scss` into one canonical rule block per widget so the 81 duplicate selectors and the 60 positional `QTreeView::item` / sidebar reset selectors are eliminated permanently.
