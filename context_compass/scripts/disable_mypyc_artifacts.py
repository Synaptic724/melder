"""
Disable local mypyc extension artifacts under ``src/melder``.

Behavior:
- deletes stale ``*.pyd.disabled`` files that would block renaming
- renames live ``*.pyd`` files to ``*.pyd.disabled``

Examples:
    python codex/context_compass/scripts/disable_mypyc_artifacts.py
    python codex/context_compass/scripts/disable_mypyc_artifacts.py src/melder
"""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Disable local mypyc .pyd artifacts by renaming them to .pyd.disabled."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default="src/melder",
        help="Root directory to scan. Defaults to src/melder.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Root path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Root path is not a directory: {root}")

    stale_disabled = sorted(root.rglob("*.pyd.disabled"))
    for path in stale_disabled:
        path.unlink()
        print(f"REMOVED\t{path}")

    renamed = 0
    for path in sorted(root.rglob("*.pyd")):
        target = path.with_name(path.name + ".disabled")
        path.rename(target)
        renamed += 1
        print(f"DISABLED\t{path}\t->\t{target}")

    print(
        f"Summary: removed {len(stale_disabled)} stale disabled file(s), "
        f"disabled {renamed} active .pyd artifact(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
