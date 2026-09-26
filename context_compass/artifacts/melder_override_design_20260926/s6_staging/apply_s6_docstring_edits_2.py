"""S6 docstring corrections, second pass (no behavior change): the two family hydrators.

Same mechanics as apply_s6_docstring_edits.py: anchored whole-block replacements with asserted
counts, line endings kept per file, `--check` writes nothing.
"""
import argparse
import pathlib
import sys
from typing import Dict, List, Tuple

GH = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py"
MH = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py"

EDITS: Dict[str, List[Tuple[str, str, int]]] = {
    GH: [
        (
            "    1. Resolve live identity (spells, path registry) through the resolver.\n",
            "    1. Resolve the live spells through the resolver.\n",
            1,
        ),
        (
            "       specializer; its body comes from the family's old step emitter and it\n"
            "       deopts to the normal plan.\n",
            "       specializer; its body comes from the specializer emitter in\n"
            "       `generalized_manifest_no_overrides_compiler` and it deopts to the\n"
            "       normal plan.\n",
            1,
        ),
    ],
    MH: [
        (
            "        - Requires phases 1-7 live (phase-5 path registry) and ownership\n"
            "          wiring (`spell._owner_creations`), which first-meld gates guarantee.\n"
            "        - The no-overrides door mirrors the legacy many_only finalize step:\n"
            "          the door-level fast-transient flag stays False because transient\n"
            "          unrolling is the inner executor's concern in this family.\n",
            "        - Requires phases 1-7 live (the site graph reads the live Phase-3\n"
            "          topologies) and ownership wiring (`spell._owner_creations`), which\n"
            "          first-meld gates guarantee.\n"
            "        - The door-level fast-transient flag stays False: the inner executor\n"
            "          is the site-plan runtime's normal plan.\n",
            1,
        ),
    ],
}


def _apply(root: pathlib.Path, check: bool) -> int:
    """Verify every anchor, then (unless `check`) write all files; returns a process exit code."""
    staged: Dict[pathlib.Path, bytes] = {}
    for rel, edits in EDITS.items():
        path = root / rel
        raw = path.read_bytes()
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8")
        for old, new, count in edits:
            if crlf:
                old = old.replace("\n", "\r\n")
                new = new.replace("\n", "\r\n")
            found = text.count(old)
            if found != count:
                print(f"ANCHOR MISMATCH {rel}: expected {count}, found {found}: {old[:70]!r}")
                return 1
            text = text.replace(old, new)
        staged[path] = text.encode("utf-8")
        print(f"ok {rel} ({'CRLF' if crlf else 'LF'}, {len(edits)} edits)")
    if check:
        return 0
    for path, data in staged.items():
        path.write_bytes(data)
    return 0


def main() -> int:
    """Parse arguments and run the edits."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return _apply(pathlib.Path(args.root), args.check)


if __name__ == "__main__":
    sys.exit(main())
