#!/usr/bin/env python3
"""
Dependency health check — compares pinned versions in pyproject.toml
against the latest releases on PyPI and reports what's out of date.

Operator semantics:
  ==  exact pin   → "behind" if PyPI latest > pinned version
  ~=  compat pin  → "behind" if PyPI latest's major.minor > pin's major.minor
  >=  lower bound → reported for information only (not flagged as behind)
  >   lower bound → reported for information only
  <=, <, !=       → reported for information only

Usage:
    python scripts/check_deps.py
    python scripts/check_deps.py --json   # machine-readable output
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"

DEP_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_.\-]+)"
    r"\s*(?P<op>==|~=|>=|<=|!=|>|<)?"
    r"\s*(?P<ver>[0-9][^\s,;]*)?",
)


def parse_deps(path: Path) -> list[dict]:
    """Return list of {name, raw, op, pinned_ver} dicts from pyproject.toml."""
    text = path.read_text()
    m = re.search(r'dependencies\s*=\s*\[(.*?)\]', text, re.DOTALL)
    if not m:
        sys.exit("Could not locate 'dependencies' list in pyproject.toml")
    block = m.group(1)
    deps = []
    for line in block.splitlines():
        line = line.strip().strip('",').strip()
        if not line or line.startswith("#"):
            continue
        m2 = DEP_RE.match(line)
        if not m2:
            continue
        deps.append({
            "name": m2.group("name"),
            "raw": line,
            "op": m2.group("op") or "",
            "pinned_ver": m2.group("ver") or "",
        })
    return deps


def pypi_latest(package: str) -> str | None:
    """Return the latest stable version string from PyPI, or None on error."""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        return data["info"]["version"]
    except Exception:
        return None


def version_tuple(ver: str) -> tuple[int, ...]:
    """Convert '1.2.3' → (1, 2, 3) for numeric comparison (digits only)."""
    try:
        return tuple(int(x) for x in re.split(r"[.\-]", ver) if x.isdigit())
    except Exception:
        return (0,)


def classify(op: str, pinned_ver: str, latest: str) -> str:
    """
    Return one of: 'exact_behind', 'compat_behind', 'ok', 'ranged', 'unknown'.

    - exact_behind : op == '==' and a newer version exists on PyPI
    - compat_behind: op == '~=' and PyPI has a newer compatible release
    - ok            : pin is current
    - ranged        : op is >=/>/<=/< (lower-bound or upper-bound; informational)
    - unknown       : version info missing or could not be fetched
    """
    if not pinned_ver or not latest:
        return "unknown"

    pv = version_tuple(pinned_ver)
    lv = version_tuple(latest)

    if op == "==":
        return "exact_behind" if lv > pv else "ok"

    if op == "~=":
        # Compatible release: newer if PyPI latest has a higher major or minor
        # segment (using the first two components to stay in the compat window).
        pv2 = pv[:2] if len(pv) >= 2 else pv
        lv2 = lv[:2] if len(lv) >= 2 else lv
        return "compat_behind" if lv2 > pv2 else "ok"

    # >=, >, <=, <, != — these are lower/upper bounds, not exact pins.
    # Report them for information but do not flag as "behind".
    return "ranged"


def main():
    parser = argparse.ArgumentParser(description="Check deps for newer PyPI releases")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    deps = parse_deps(PYPROJECT)
    results = []

    for dep in deps:
        latest = pypi_latest(dep["name"])
        status = classify(dep["op"], dep["pinned_ver"], latest)
        results.append({**dep, "latest": latest or "?", "status": status})

    if args.json:
        print(json.dumps(results, indent=2))
        return

    exact_behind  = [r for r in results if r["status"] == "exact_behind"]
    compat_behind = [r for r in results if r["status"] == "compat_behind"]
    ok            = [r for r in results if r["status"] == "ok"]
    ranged        = [r for r in results if r["status"] == "ranged"]
    unknown       = [r for r in results if r["status"] == "unknown"]

    col_w = max(len(r["name"]) for r in results) + 2

    def row(r):
        name    = r["name"].ljust(col_w)
        pin_str = (r["op"] + r["pinned_ver"]) if r["pinned_ver"] else r["raw"]
        pin_str = pin_str.ljust(18)
        return f"  {name}  pinned {pin_str}  latest {r['latest']}"

    print("=" * 72)
    print("  DEPENDENCY HEALTH CHECK")
    print(f"  Source: {PYPROJECT}")
    print("=" * 72)

    if exact_behind:
        print(f"\n🔴  EXACT PINS BEHIND ({len(exact_behind)})  — upgrade needed:")
        for r in exact_behind:
            print(row(r))

    if compat_behind:
        print(f"\n🟡  COMPATIBLE-RANGE PINS BEHIND ({len(compat_behind)})  (~=):")
        for r in compat_behind:
            print(row(r))

    if ok:
        print(f"\n✅  PINNED AND UP TO DATE ({len(ok)}):")
        for r in ok:
            print(row(r))

    if ranged:
        print(f"\nℹ️   LOWER/UPPER BOUNDS — not flagged as pins ({len(ranged)}):")
        for r in ranged:
            print(row(r))

    if unknown:
        print(f"\n❓  UNKNOWN / COULD NOT FETCH ({len(unknown)}):")
        for r in unknown:
            print(row(r))

    print()
    n_behind = len(exact_behind) + len(compat_behind)
    if n_behind:
        print(
            f"Summary: {len(exact_behind)} exact pin(s) and "
            f"{len(compat_behind)} compat pin(s) have newer releases available."
        )
        sys.exit(1)
    else:
        print("Summary: All pinned packages are at the latest available release.")


if __name__ == "__main__":
    main()
