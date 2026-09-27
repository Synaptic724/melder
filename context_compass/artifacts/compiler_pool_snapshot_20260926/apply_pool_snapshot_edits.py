"""
Compiler passes on the meld-time path iterate a copy of the spell pool (patch compiler_pool_snapshot_2026_09_26).

Line-based anchored edits: each OLD block must match consecutive lines (compared without their line ending)
exactly COUNT times; the replacement lines take the line ending of the first matched line, so files with mixed
endings keep each region's own style. `--check` verifies every anchor and writes nothing.
"""
import argparse
import pathlib
import sys
from typing import Dict, List, Tuple

P = "src/melder/aether/spellbook/spell_compiler/"
EDITS: Dict[str, List[Tuple[List[str], List[str], int]]] = {
    P + "phases/compiler_phase_3.py": [
        (["            Iterate all visible spells via the Spellbook's live spell_id_pool."],
         ["            Iterate all visible spells via a copy of the Spellbook's spell_id_pool."], 1),
        (["                - Uses the Spellbook's live \"_spell_id_pool\" directly; no copies",
          "                  or snapshots are created."],
         ["                - Iterates a copy of \"_spell_id_pool\" taken in one call when the",
          "                  iteration starts. A concurrent bind, notch, contract grant or",
          "                  transfer changes the live dict under the Spellbook lock, which",
          "                  this pass does not hold (meld-time reruns run outside any",
          "                  transaction); iterating it live raised \"dictionary changed size",
          "                  during iteration\"."], 1),
        (["                Iterator[Tuple[SpellIndex, Spell]]: Live iteration stream."],
         ["                Iterator[Tuple[SpellIndex, Spell]]: Stream over the copy."], 1),
        (["        for spell_instance in spellbook._spell_id_pool.values():"],
         ["        for spell_instance in spellbook._spell_id_pool.copy().values():"], 1),
    ],
    P + "validation/strategies/binding_resolution_cycle_strategy.py": [
        (["            - Pure read over `spellbook._spell_id_pool` and each spell's"],
         ["            - Pure read over a copy of `spellbook._spell_id_pool` (concurrent binds",
          "              change the live dict under the Spellbook lock) and each spell's"], 1),
        (["        for spell_id, spell_instance in spellbook._spell_id_pool.items():"],
         ["        # A copy: concurrent binds change the live pool under the Spellbook lock, not held here.",
          "        for spell_id, spell_instance in spellbook._spell_id_pool.copy().items():"], 2),
    ],
    P + "validation/strategies/circular_dependency_strategy.py": [
        (["            for spell_id, spell in spellbook._spell_id_pool.items():"],
         ["            # A copy: concurrent binds change the live pool under the Spellbook lock, not held here.",
          "            for spell_id, spell in spellbook._spell_id_pool.copy().items():"], 1),
    ],
    P + "validation/strategies/duplicate_spell_name_strategy.py": [
        (["            for spell_id, other_spell in spellbook._spell_id_pool.items():"],
         ["            # A copy: concurrent binds change the live pool under the Spellbook lock, not held here.",
          "            for spell_id, other_spell in spellbook._spell_id_pool.copy().items():"], 1),
    ],
    P + "phases/compiler_phase_5.py": [
        (["          and local topology remain available through their original owners."],
         ["          and local topology remain available through their original owners.",
          "        - Each pass reads one copy of the Spellbook's spell pool and admits only",
          "          ids with a registered SpellSystemState; it never takes the Spellbook",
          "          lock, and a concurrent bind cannot change the pool under it."], 1),
        (["        visible_spell_ids = {",
          "            spell_id for spell_id, candidate in spellbook._spell_id_pool.items() if candidate.resolvable",
          "        }"],
         ["        # One copy of the pool serves the whole pass: binds, notches, contract grants and",
          "        # transfers change the live dict under the Spellbook lock, which this pass does not",
          "        # hold. Only ids in the adjacency snapshot (registered SpellSystemState) are visible:",
          "        # bind publishes its pool entry before registering the state, and such a spell is",
          "        # left to the revalidation its bind schedules.",
          "        spell_lookup = spellbook._spell_id_pool.copy()",
          "        visible_spell_ids = {",
          "            spell_id",
          "            for spell_id, candidate in spell_lookup.items()",
          "            if candidate.resolvable and spell_id in snapshot.all_spell_ids",
          "        }"], 1),
        (["            spell_lookup=spellbook._spell_id_pool,"],
         ["            spell_lookup=spell_lookup,"], 2),
        (["        spell_lookup = spellbook._spell_id_pool",
          "        visible_spell_ids = {spell_id for spell_id, candidate in spell_lookup.items() if candidate.resolvable}"],
         ["        # One copy of the pool serves the whole pass; see run_frame_wide.",
          "        spell_lookup = spellbook._spell_id_pool.copy()",
          "        visible_spell_ids = {",
          "            spell_id",
          "            for spell_id, candidate in spell_lookup.items()",
          "            if candidate.resolvable and spell_id in snapshot.all_spell_ids",
          "        }"], 1),
    ],
    P + "phases/compiler_phase_6.py": [
        (["        spell_lookup: Dict[str, Spell] = spellbook._spell_id_pool"],
         ["        # One copy of the pool serves every stage and strategy of this pass: concurrent binds",
          "        # change the live dict under the Spellbook lock, which this pass does not hold.",
          "        spell_lookup: Dict[str, Spell] = spellbook._spell_id_pool.copy()"], 1),
    ],
    P + "spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py": [
        (["            - Returns `None` on any walk failure."],
         ["            - Returns `None` on any walk failure.",
          "            - Iterates a copy of `spell_lookup` (the live pool at every call site)",
          "              taken in one call; a concurrent bind used to fail the walk here and",
          "              drop the existence-occurrence analysis for the pass."], 1),
        (["            for spell_id, candidate_spell in sorted(spell_lookup.items()):"],
         ["            for spell_id, candidate_spell in sorted(spell_lookup.copy().items()):"], 1),
    ],
}


def _find(lines: List[bytes], old: List[bytes]) -> List[int]:
    """Return every start index where `old` matches consecutive lines (ending-insensitive)."""
    bare = [ln.rstrip(b"\r") for ln in lines]
    hits = []
    for i in range(len(bare) - len(old) + 1):
        if bare[i:i + len(old)] == old:
            hits.append(i)
    return hits


def _apply(root: pathlib.Path, check: bool) -> int:
    """Verify every anchor, then (unless `check`) write every file; returns a process exit code."""
    staged: Dict[pathlib.Path, bytes] = {}
    for rel, edits in EDITS.items():
        path = root / rel
        lines = path.read_bytes().split(b"\n")
        for old_s, new_s, count in edits:
            old = [s.encode("utf-8") for s in old_s]
            hits = _find(lines, old)
            if len(hits) != count:
                print(f"ANCHOR MISMATCH {rel}: expected {count}, found {len(hits)}: {old_s[0][:70]!r}")
                return 1
            for start in reversed(hits):
                eol = b"\r" if lines[start].endswith(b"\r") else b""
                new = [s.encode("utf-8") + eol for s in new_s]
                lines[start:start + len(old)] = new
        staged[path] = b"\n".join(lines)
        print(f"ok {rel} ({len(edits)} edits)")
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
