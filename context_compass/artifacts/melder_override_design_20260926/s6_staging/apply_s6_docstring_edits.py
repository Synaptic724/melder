"""S6 docstring corrections for the site-plan lane (no behavior change).

Anchored, whole-block replacements; each anchor must match its asserted count. Line endings are kept
per file (two of the four files are CRLF). `--check` verifies every anchor and writes nothing.
"""
import argparse
import pathlib
import sys
from typing import Dict, List, Tuple

SA = "src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_site_graph_analysis.py"
SP = "src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_site_graph_processor_strategy.py"
LOW = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"
RT = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py"

EDITS: Dict[str, List[Tuple[str, str, int]]] = {
    SA: [
        (
            "        Built at the first override meld of a root by `SitePlanOverrideRuntime`\n"
            "        (design v2 S3), which resolves override keys against it; conjure does\n"
            "        not build it (2026-09-26).\n",
            "        Built by `SitePlanOverrideRuntime` (through\n"
            "        `SitePlanLowering.build_site_graph`) when a root of the many_only or\n"
            "        generalized family is hydrated at its first meld, normal or override\n"
            "        (since S2b-2); plans are placed and override keys resolved against it.\n"
            "        Conjure does not build it (2026-09-26).\n",
            1,
        ),
        (
            "        rows, name index and logical path counts. Input to override key resolution.\n",
            "        rows, name index and logical path counts. Input to override key resolution\n"
            "        and site-plan placement.\n",
            1,
        ),
    ],
    SP: [
        (
            "        processor chain since 2026-09-26: `SitePlanOverrideRuntime` calls\n"
            "        `build_site_graph` at the first override meld; `process` remains for\n"
            "        callers that fit the section on a model.\n",
            "        processor chain since 2026-09-26: `SitePlanLowering.build_site_graph`\n"
            "        calls `build_site_graph` when a `SitePlanOverrideRuntime` is built at\n"
            "        hydration; `process` remains for callers that fit the section on a model.\n",
            1,
        ),
    ],
    LOW: [
        (
            "        Phase-11 override lane (design v2 step S3).\n",
            "        Phase-11 normal and override lanes of the many_only and generalized\n"
            "        families (design v2 S2/S3).\n",
            4,
        ),
        (
            "        The shared lowering of design v2 for the override lane: given the\n"
            "        lane's no-overrides steps and one resolved key set, emit Python that\n",
            "        The shared lowering of design v2 for normal and override melds: given\n"
            "        the lane's no-overrides steps and one resolved key set (empty for the\n"
            "        normal plan), emit Python that\n",
            1,
        ),
        (
            "        access: internal. Site graph from steps, demand walk and key-set plan source emission\n"
            "        for override melds.\n",
            "        access: internal. Site graph from steps, demand walk and key-set plan source emission\n"
            "        for normal and override melds.\n",
            1,
        ),
    ],
    RT: [
        (
            "        Phase-11 override lane (design v2 step S3); CreationContext override\n"
            "        slots and doors are unchanged.\n",
            "        Phase-11 normal and override lanes (design v2 S2/S3); CreationContext\n"
            "        slots and doors are unchanged.\n",
            1,
        ),
        (
            "        access: internal. Key-set dispatcher for override melds: lazily compiled\n"
            "        per-key-set plans over the lane's no-overrides steps.\n",
            "        access: internal. Owns a root's normal plan (the family's inner executor)\n"
            "        and its lazily compiled per-key-set override plans over the lane's steps.\n",
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
