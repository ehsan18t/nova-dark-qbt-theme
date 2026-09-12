#!/usr/bin/env python3
"""Build every Nova Dark variant into dist/.

This is the only build implementation, and it runs natively everywhere: Windows
(cmd, PowerShell, or double-clicking scripts\\build.bat), macOS, Linux, and the
container defined by the Dockerfile.

It is written in Python rather than shell because Python was never optional --
make-resource.py, generate-config.py and recolour_icons.py *are* the build, and
the toolchain image is python:3.11-slim. A shell script made Windows depend on
Git Bash for nothing, and the alternative, a .bat that reimplemented the build,
is precisely what let the Windows path silently package a stale stylesheet for
as long as it did.

build.sh and build.bat are both thin launchers for this file. Add logic here.


THE MATRIX

src/nova-dark/variants.json declares the axes; this file takes their cartesian
product. Today that is 4 palettes x 1 density x 2 icon treatments = 8 themes,
but nothing here knows those numbers. Adding a value is one fragment file plus
one line in that manifest, and adding a whole axis needs no change here at all.

The work is NOT 8x anything, because the axes have different blast radius:

    config.json     depends on palette only              -> 4 generated
    stylesheet      depends on palette x density         -> 4 compiled
    icon set        depends on palette x treatment       -> 8 recoloured
    .qbtheme        depends on all three                 -> 8 packed

So each intermediate is produced once and reused across the variants that share
it. Skipping that would triple the slowest steps for no benefit.

SEQUENTIAL ON PURPOSE. make-resource.py writes resources.qrc into the working
directory and deletes it afterwards, so two packs running at once would race on
that one path. The same applies to the generated SCSS entry point. If this ever
needs to be parallelised, give both a per-variant name first.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
THEME_ROOT = SRC_ROOT / "nova-dark"
SOURCE_DIR = THEME_ROOT / "source"
PALETTE_DIR = SOURCE_DIR / "palettes"
DENSITY_DIR = SOURCE_DIR / "densities"
ICONS_DIR = THEME_ROOT / "icons" / "modern"
COMMON_DIR = SRC_ROOT / "common"
CONFIG_DIR = THEME_ROOT / "config"
VARIANTS_FILE = THEME_ROOT / "variants.json"

# Written into SOURCE_DIR so that the relative @imports inside it resolve
# exactly as a hand-written entry point's would, then removed. Gitignored.
ENTRY_NAME = "build-entry.scss"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _supports_colour() -> bool:
    if not sys.stdout.isatty():
        return False
    if os.name != "nt":
        return True
    # Windows consoles need VT processing turned on explicitly; without this
    # the escape codes are printed literally, which is worse than no colour.
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        return bool(kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7))
    except Exception:
        return False


if _supports_colour():
    BLUE, YELLOW, RED, GREEN, DIM, NC = (
        "\033[0;34m", "\033[0;33m", "\033[0;31m", "\033[0;32m", "\033[2m", "\033[0m",
    )
else:
    BLUE = YELLOW = RED = GREEN = DIM = NC = ""


# flush=True throughout: the helper scripts write straight to this process's
# stdout, so anything still sitting in Python's buffer would surface after their
# output and the log would read out of order.
def log_info(msg: str) -> None:
    print(f"{BLUE}[info]{NC} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{YELLOW}[warn]{NC} {msg}", file=sys.stderr, flush=True)


def log_error(msg: str) -> None:
    print(f"{RED}[error]{NC} {msg}", file=sys.stderr, flush=True)


def log_done(msg: str) -> None:
    print(f"{GREEN}[done]{NC} {msg}", flush=True)


def log_step(msg: str) -> None:
    print(f"{DIM}       {msg}{NC}", flush=True)


def fail(*lines: str) -> None:
    for line in lines:
        log_error(line)
    sys.exit(1)


def rel(path: Path) -> str:
    """Path relative to the repo root, for messages."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# The manifest
# ---------------------------------------------------------------------------

class Axis:
    def __init__(self, name: str, spec: dict):
        self.name = name
        self.dir = THEME_ROOT / spec["dir"]
        self.prefix = spec.get("prefix", "")
        self.suffix = spec["suffix"]
        self.shared = set(spec.get("shared", []))
        self.values = list(spec["values"])

    def path(self, value: str) -> Path:
        return self.dir / f"{self.prefix}{value}{self.suffix}"

    def on_disk(self) -> list[str]:
        found = []
        for entry in sorted(self.dir.glob(f"*{self.suffix}")):
            if entry.name in self.shared:
                continue
            if self.prefix and not entry.name.startswith(self.prefix):
                continue
            found.append(entry.name[len(self.prefix):-len(self.suffix)])
        return found


def load_axes() -> tuple[dict[str, Axis], dict[str, str]]:
    if not VARIANTS_FILE.exists():
        fail(f"{rel(VARIANTS_FILE)} not found; it declares the variant matrix.")
    manifest = json.loads(VARIANTS_FILE.read_text(encoding="utf-8"))
    axes = {name: Axis(name, spec) for name, spec in manifest["axes"].items()}
    return axes, manifest["default"]


def variant_name(combo: dict[str, str], axes: dict[str, Axis]) -> str:
    """Name a variant by the axes that actually vary.

    An axis carrying a single value distinguishes nothing, so it is left out:
    with one density there is no "comfortable" to tell apart from anything, and
    carrying it in every filename is noise. Add a second density and it returns
    to the names automatically, for every variant at once.
    """
    parts = [combo[name] for name, axis in axes.items() if len(axis.values) > 1]
    if not parts:  # every axis pinned; fall back to the full combination
        parts = [combo[name] for name in axes]
    return "nova-dark-" + "-".join(parts)


# ---------------------------------------------------------------------------
# Gates. Every one of these exists because the failure it catches is SILENT:
# the build stays green and the wrong thing ships.
# ---------------------------------------------------------------------------

HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
LENGTH = re.compile(r"\b\d+(?:\.\d+)?(px|pt|em|ex|%)\b")
COLOURISH = re.compile(r"\b(rgba?|hsla?)\s*\(")


def _code_lines(path: Path):
    """Yield (line number, code) with `//` comments stripped."""
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        code = line.split("//")[0]
        if code.strip():
            yield number, code


def check_qtsass():
    """Import qtsass rather than shelling out to its CLI.

    The CLI lives in Python's Scripts/ directory, which is frequently not on
    PATH on Windows even when qtsass is correctly installed. Importing it needs
    only the interpreter running this script, so the common Windows failure
    disappears. qtsass's own CLI does exactly this for a file with an output
    path, so the compiled result is identical.
    """
    try:
        from qtsass import compile_filename
    except ImportError:
        fail(
            "qtsass not found.",
            f"Install it with: {Path(sys.executable).name} -m pip install qtsass",
            "Or build in Docker, which needs no local toolchain:",
            "    docker compose run --rm build",
        )
    return compile_filename


def check_icons() -> None:
    """Fatal, not a warning.

    recolour_icons.py globs this directory and make-resource.py packs whatever
    comes out, so an empty or misnamed directory means the build stays green,
    rcc succeeds, and every theme installs with all icons falling back to
    qBittorrent's stock set. That is the same silent-success failure as the
    stale-stylesheet bug, and it is why a "safe" rename of the icons directory
    is the most dangerous move in this repo.
    """
    if not any(ICONS_DIR.glob("*.svg")):
        fail(
            f"No SVG icons found in {rel(ICONS_DIR)}",
            "Fetch them with: python src/nova-dark/scripts/download_phosphor_icons.py",
        )


def check_axis_files(axes: dict[str, Axis]) -> None:
    """variants.json and the files on disk must agree, in both directions.

    Declared-but-missing would fail later with a confusing SCSS error. Present-
    but-undeclared is the subtler one: a half-finished palette sitting in the
    directory would either become a shipped theme by accident or, worse, look
    like it was being built when it was not.
    """
    problems = []
    for axis in axes.values():
        declared, found = set(axis.values), set(axis.on_disk())
        for value in sorted(declared - found):
            problems.append(
                f"{axis.name}: '{value}' is in variants.json but "
                f"{rel(axis.path(value))} does not exist")
        for value in sorted(found - declared):
            problems.append(
                f"{axis.name}: {rel(axis.path(value))} exists but '{value}' is "
                f"not listed in variants.json")
    if problems:
        log_error("variants.json disagrees with the files on disk:")
        for entry in problems:
            print(f"          {entry}", file=sys.stderr, flush=True)
        fail("Add the missing file, or add the missing line to variants.json.")


def check_no_stray_hex() -> None:
    """source/palettes/ is the single source of truth for colour.

    A hex literal anywhere else silently reintroduces the duplication the
    layering exists to prevent, so fail rather than let it drift back. Comments
    are exempt: they do not compile, and commented-out rules are useful history.
    """
    stray = []
    for scss in sorted(SOURCE_DIR.rglob("*.scss")):
        if scss.parent == PALETTE_DIR:
            continue
        for number, code in _code_lines(scss):
            if HEX.search(code):
                stray.append(f"{rel(scss)}:{number}:{code.strip()}")

    if stray:
        log_error("Hex literal outside source/palettes/:")
        for entry in stray:
            print(f"          {entry}", file=sys.stderr, flush=True)
        fail("Add the colour to a palette fragment and reference it by name.")


def check_axis_purity() -> None:
    """A palette owns colour; a density owns geometry. Neither owns the other.

    This is what makes the axes orthogonal, and orthogonality is what makes
    three spot-checked variants enough evidence for twelve: if a palette cannot
    move a row and a density cannot shift a hue, then the combinations cannot
    surprise you. Without the gate the separation is a convention, and
    conventions in a generated matrix last about one busy afternoon.
    """
    problems = []

    for scss in sorted(PALETTE_DIR.glob("*.scss")):
        for number, code in _code_lines(scss):
            match = LENGTH.search(code)
            if match:
                problems.append(
                    f"{rel(scss)}:{number}: geometry ('{match.group(0)}') in a "
                    f"palette fragment; it belongs in source/densities/")

    for scss in sorted(DENSITY_DIR.glob("*.scss")):
        for number, code in _code_lines(scss):
            if HEX.search(code) or COLOURISH.search(code):
                problems.append(
                    f"{rel(scss)}:{number}: colour in a density fragment; it "
                    f"belongs in source/palettes/")

    if problems:
        log_error("An axis fragment reaches outside its own axis:")
        for entry in problems:
            print(f"          {entry}", file=sys.stderr, flush=True)
        fail("Move the declaration to the axis that owns it.")


DECL = re.compile(r"^\s*\$([\w-]+)\s*:")


def _declared(path: Path) -> set[str]:
    return {m.group(1) for _, code in _code_lines(path)
            for m in [DECL.match(code)] if m}


def check_fragment_parity(axes: dict[str, Axis]) -> None:
    """Every fragment on an axis must declare the same variable names.

    A missing name would usually surface as an SCSS "undefined variable" error,
    which is survivable. The one that is not survivable is a name that exists in
    two fragments and is MISSPELLED in a third: the third silently inherits
    whatever the shared layer last set, and only that one variant is wrong. This
    compares the set and names the difference.
    """
    for axis in axes.values():
        if axis.suffix != ".scss" or len(axis.values) < 2:
            continue
        reference = axis.values[0]
        expected = _declared(axis.path(reference))
        for value in axis.values[1:]:
            actual = _declared(axis.path(value))
            missing, extra = expected - actual, actual - expected
            if missing or extra:
                log_error(
                    f"{axis.name} fragments disagree: "
                    f"'{value}' vs '{reference}'")
                for name in sorted(missing):
                    print(f"          missing: ${name}", file=sys.stderr, flush=True)
                for name in sorted(extra):
                    print(f"          extra:   ${name}", file=sys.stderr, flush=True)
                fail("Every fragment on an axis must define the same names.")


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def run_script(script: Path, *args: str) -> None:
    """Run a helper script with the interpreter running this build.

    sys.executable, never a bare "python": on Windows that name is often absent
    or a Store alias stub, and inside the container it would be an unnecessary
    PATH lookup.
    """
    result = subprocess.run([sys.executable, str(script), *args], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        fail(f"{rel(script)} failed with exit code {result.returncode}")


def compile_stylesheet(compile_filename, palette: str, density: str) -> Path:
    """Compile one palette x density stylesheet, then normalise line endings.

    The entry point is generated rather than checked in, because it is the one
    file that names a specific palette and density -- and there are six of those
    pairs. It is written into source/ so its relative @imports resolve the same
    way a hand-written entry's would, and removed afterwards.

    qtsass writes through Python's text mode, so on Windows every newline lands
    as CRLF and the stylesheet comes out ~1.4 KB larger than the identical build
    on Linux. Qt parses either, so this is not about correctness -- it is so the
    compiled stylesheets can be diffed across build hosts. Comparing them is how
    a "no visual change" claim gets verified here, and that check is worthless
    if the Windows output differs from the Linux one on every single line.

    This does NOT make the .qbtheme files reproducible: Qt's rcc embeds
    timestamps, so even two consecutive identical builds produce different
    bytes. Compare the .qss, never the .qbtheme.
    """
    out = BUILD_DIR / "qss" / f"{palette}-{density}.qss"
    out.parent.mkdir(parents=True, exist_ok=True)

    entry = SOURCE_DIR / ENTRY_NAME
    entry.write_text(
        "// GENERATED by scripts/build.py. Do not edit; it is rewritten and\n"
        "// deleted on every build. The layering it encodes is the point:\n"
        "//   palettes/_states  shared state colours, identical in every variant\n"
        "//   palettes/_<name>  this variant's neutrals, chrome accent, icon ramp\n"
        "//   densities/_<name> this variant's geometry, no colour\n"
        "//   _tokens           primitives mapped onto roles\n"
        "//   _widgets          the rules, written against roles only\n"
        f'@import "palettes/states";\n'
        f'@import "palettes/{palette}";\n'
        f'@import "densities/{density}";\n'
        f'@import "tokens";\n'
        f'@import "widgets";\n',
        encoding="utf-8")

    previous = Path.cwd()
    try:
        os.chdir(SOURCE_DIR)
        compile_filename(ENTRY_NAME, str(out))
    finally:
        os.chdir(previous)
        entry.unlink(missing_ok=True)

    out.write_bytes(out.read_bytes().replace(b"\r\n", b"\n"))
    return out


def build_icon_set(palette: str, treatment: str) -> Path:
    out = BUILD_DIR / "icons" / f"{palette}-{treatment}"
    run_script(
        THEME_ROOT / "scripts" / "recolour_icons.py",
        "--palette", palette, "--treatment", treatment, "--out", str(out), "--quiet")
    return out


def pack(name: str, stylesheet: Path, config: Path, icons: Path) -> Path:
    """Pack one variant.

    base-dir is the directory holding this variant's stylesheet and nothing
    else, so make-resource.py's directory walk stays trivial; the control SVGs
    arrive through -include-dir with their `common/` prefix, which is the form
    the stylesheet's :/uitheme/common/... references expect.
    """
    staging = BUILD_DIR / "pack" / name
    staging.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(stylesheet, staging / "NovaDark.qss")

    run_script(
        SRC_ROOT / "make-resource.py",
        "-base-dir", str(staging),
        "-find-files",
        "-config", str(config),
        "-icons-dir", str(icons),
        "-include-dir", str(COMMON_DIR),
        "-output", str(DIST_DIR / name),
        "-style", "NovaDark.qss",
    )
    return DIST_DIR / f"{name}.qbtheme"


def fix_ownership() -> None:
    """In Docker the build runs as root, so artifacts written into the
    bind-mounted tree land root-owned and the host user cannot overwrite them on
    the next build. No-op for an ordinary non-root host build, and on Windows,
    which has no geteuid.
    """
    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        return
    stat = PROJECT_ROOT.stat()
    for directory in (DIST_DIR, BUILD_DIR):
        for path in [directory, *directory.rglob("*")]:
            try:
                os.chown(path, stat.st_uid, stat.st_gid)
            except OSError:
                pass


# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only", action="append", default=[], metavar="AXIS=VALUE",
        help="restrict an axis, e.g. --only palette=nebula. Repeatable.")
    parser.add_argument(
        "--list", action="store_true",
        help="print the variants that would be built, then exit")
    args = parser.parse_args()

    axes, default = load_axes()

    # Gates first: all of them, before any work, so a bad fragment is reported
    # once rather than twelve times.
    check_icons()
    check_axis_files(axes)
    check_no_stray_hex()
    check_axis_purity()
    check_fragment_parity(axes)

    selected = {name: list(axis.values) for name, axis in axes.items()}
    for restriction in args.only:
        if "=" not in restriction:
            fail(f"--only wants AXIS=VALUE, got '{restriction}'")
        axis_name, value = restriction.split("=", 1)
        if axis_name not in axes:
            fail(f"no axis '{axis_name}'. Axes: {', '.join(axes)}")
        if value not in axes[axis_name].values:
            fail(f"'{value}' is not a value of {axis_name}. "
                 f"Values: {', '.join(axes[axis_name].values)}")
        selected[axis_name] = [value]

    order = list(axes)
    combos = [dict(zip(order, values))
              for values in itertools.product(*(selected[name] for name in order))]

    if args.list:
        for combo in combos:
            print(variant_name(combo, axes))
        return

    compile_filename = check_qtsass()
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # The configs carry the colours qBittorrent paints itself (QPalette,
    # transfer-list states, log levels). QSS cannot reference them, so they have
    # to be duplicated -- this regenerates them from the palettes so the
    # duplicate cannot drift. They are checked in, so any change shows up in
    # `git status`.
    log_info("Generating one config per palette")
    run_script(THEME_ROOT / "scripts" / "generate-config.py")

    palettes = sorted({c["palette"] for c in combos})
    densities = sorted({c["density"] for c in combos})
    treatments = sorted({c["icons"] for c in combos})

    log_info(f"Compiling {len(palettes) * len(densities)} stylesheet(s)")
    sheets = {}
    for palette in palettes:
        for density in densities:
            sheets[(palette, density)] = compile_stylesheet(
                compile_filename, palette, density)
            log_step(f"{palette} / {density}")

    # A compiled stylesheet can be perfectly valid and still paint the wrong
    # thing, because a rule the sidebar relies on can be out-specified by a
    # generic reset. That is invisible in the source and invisible in the
    # output; it only shows when the cascade is resolved the way Qt resolves it.
    # This already caught the selection rail disappearing whenever the sidebar
    # had focus.
    log_info("Checking the sidebar rail wins the cascade")
    run_script(THEME_ROOT / "scripts" / "check_cascade.py",
               *[str(p) for p in sheets.values()])

    log_info(f"Recolouring {len(palettes) * len(treatments)} icon set(s)")
    icon_sets = {}
    for palette in palettes:
        for treatment in treatments:
            icon_sets[(palette, treatment)] = build_icon_set(palette, treatment)
            log_step(f"{palette} / {treatment}")

    log_info(f"Packing {len(combos)} theme(s)")
    built = {}
    for combo in combos:
        name = variant_name(combo, axes)
        built[tuple(combo[a] for a in order)] = pack(
            name,
            sheets[(combo["palette"], combo["density"])],
            CONFIG_DIR / f"{combo['palette']}.json",
            icon_sets[(combo["palette"], combo["icons"])],
        )

    # The default alias. The README's install instructions point at this name,
    # and so does anyone who has been using the theme since before it had
    # variants, so it keeps working and simply means "the recommended one".
    alias_key = tuple(default[a] for a in order)
    if alias_key in built:
        alias = DIST_DIR / "nova-dark.qbtheme"
        shutil.copyfile(built[alias_key], alias)
        log_step(f"alias {alias.name} -> {variant_name(default, axes)}")
    elif not args.only:
        log_warn(f"default combination {default} was not built; no alias written")

    fix_ownership()
    log_done(f"{len(built)} theme(s) in {rel(DIST_DIR)}")


if __name__ == "__main__":
    main()
