"""melder_2 P4 notch: __version__ 0.2.67 -> 0.2.68, release-note header and LLM-bundle line follow, plus one
"Faster warm melds" bullet for SpellSpace id melds. Anchored, count-checked, line-wise; endings preserved.

usage: python notch_p4.py --root <repo root> [--check]
"""
import argparse, pathlib, sys

VERSION_OLD = '__version__ = "0.2.67"\n'
VERSION_NEW = '__version__ = "0.2.68"\n'
HEADER_OLD = "# Melder 0.2.67\n"
HEADER_NEW = "# Melder 0.2.68\n"
BUNDLE_OLD = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.67.\n"
BUNDLE_NEW = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.68.\n"
BULLET_OLD = """- **Id melds on an automatic conduit** - `conduit.meld(spell_id=...)` - are served from the warm fast
  lane directly, about 100 ns less per call (free-threaded 3.14, main thread).
"""
BULLET_NEW = """- **Id melds on an automatic conduit** - `conduit.meld(spell_id=...)` - are served from the warm fast
  lane directly, about 100 ns less per call (free-threaded 3.14, main thread).
- **Id melds on a SpellSpace** - `space.meld(spell_id=...)` - are served from the same warm fast lane
  without entering the spellspace's meld door, about 40 ns less per call (free-threaded 3.14, worker
  thread). Results, errors and hooks are unchanged.
"""
EDITS = {
    "src/melder/__version__.py": [(VERSION_OLD, VERSION_NEW, 1)],
    "release_docs/next_version_release.md": [
        (HEADER_OLD, HEADER_NEW, 1),
        (BUNDLE_OLD, BUNDLE_NEW, 1),
        (BULLET_OLD, BULLET_NEW, 1),
    ],
}


def _apply_edits(raw: bytes, edits, rel: str) -> bytes:
    """Apply anchored edits line-wise, keeping every untouched line's own ending."""
    lines = raw.decode("utf-8").splitlines(keepends=True)
    for old, new, count in edits:
        norm = [line.rstrip("\r\n") for line in lines]
        old_lines = old.split("\n")[:-1]
        new_lines = new.split("\n")[:-1]
        hits = [i for i in range(len(norm) - len(old_lines) + 1) if norm[i:i + len(old_lines)] == old_lines]
        if len(hits) != count:
            raise SystemExit(f"ANCHOR MISMATCH {rel}: expected {count}, found {len(hits)}: {old[:70]!r}")
        for i in reversed(hits):
            ending = "\r\n" if lines[i].endswith("\r\n") else "\n"
            lines[i:i + len(old_lines)] = [line + ending for line in new_lines]
    return "".join(lines).encode("utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = pathlib.Path(a.root)
    plans = [(root / rel, _apply_edits((root / rel).read_bytes(), edits, rel)) for rel, edits in EDITS.items()]
    print(f"OK: {len(plans)} files" + (" (check only)" if a.check else ""))
    if not a.check:
        for path, data in plans:
            path.write_bytes(data)
        print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
