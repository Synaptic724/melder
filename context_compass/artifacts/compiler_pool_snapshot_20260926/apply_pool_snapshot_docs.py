"""Promote patch compiler_pool_snapshot_2026_09_26 into src_components and src_architecture (LF files)."""
import argparse
import pathlib
import sys
from typing import Dict, List, Tuple

COMPONENTS_BLOCK = """
Compiler pool reads (2026-09-26):
- Compiler passes that run outside a transaction (meld-time structural reruns, conduit-local resolution,
  deferred 8-11) iterate a copy of `Spellbook._spell_id_pool` taken in one call, never the live dict. Binds,
  notches, contract grants and transfers change the pool under the Spellbook lock, which no pass takes;
  iterating it live raised "dictionary changed size during iteration" on free-threaded builds. The copy is
  atomic there (the dict's own lock) and under the GIL.
- Sites: Phase 3 `_iter_all_spells` (every candidate scan), the binding-resolution-cycle, circular-dependency
  and duplicate-name Phase-4 strategies, Phase 5 frame-wide and local, Phase 6 frame-wide (one copy for all its
  stages and the two Phase-6 system strategies it passes the pool to) and the Phase-8 pool walk, which used to
  swallow the error and return None, dropping the existence-occurrence analysis family discovery reads.
- Phase 5 uses its copy for the visible set and every lookup in the pass, and admits only ids present in its
  adjacency snapshot (a registered SpellSystemState). Bind publishes the pool entry before registering the
  state; a pass in that gap used to raise "requires a live SpellSystemState" and now leaves the spell to the
  revalidation its bind schedules. With no write during a pass the visible set is unchanged.
- Not changed: lookups (`get`, `[]`, `in`) on the live pool; the conjure-time sweeps in the creation system and
  structural snapshot (inside the CONJURE transaction); the Nexus relationship publisher.
- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:CompilerPhase5.run_local`,
  `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:CompilerPhase3._iter_all_spells` and
  `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py`.
"""

ARCH_BULLET = """- Compiler pool reads (2026-09-26): a compiler pass never iterates the live `Spellbook._spell_id_pool`; it
  iterates a copy taken in one call (Phases 3, 4, 5, 6 frame-wide and the Phase-8 walk). Pool writers hold the
  Spellbook lock and passes run without it at meld time, so a concurrent bind used to abort revalidation. Phase 5
  sees only ids with a registered SpellSystemState, which leaves a half-registered bind to its own
  revalidation. No lock was added.
  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:CompilerPhase5`.
"""

HANDOFF_COMPONENTS = """2026-09-26 compiler pool reads (0.2.72): the open item recorded by the override site-plan lane below is
closed. Compiler passes on the meld-time path iterate a copy of the spell pool, Phase 5 admits only ids with a
registered state, and the Phase-8 walk no longer drops its analysis under a concurrent bind. Promoted into the
SpellCompiler entry ("Compiler pool reads").

"""

HANDOFF_ARCH = """2026-09-26 compiler pool reads (0.2.72): compiler passes iterate a copy of the spell pool instead of the live
dict, so a concurrent bind no longer aborts meld-time revalidation; the operational invariants carry the rule.

"""

EDITS: Dict[str, List[Tuple[str, str, int]]] = {
    "src_components.md": [
        ("- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:CompilerPhase5`.\n\n"
         "Constructor default precedence (2026-09-13):\n",
         "- EVIDENCE: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:CompilerPhase5`.\n"
         + COMPONENTS_BLOCK + "\nConstructor default precedence (2026-09-13):\n", 1),
        ("## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + HANDOFF_COMPONENTS, 1),
    ],
    "src_architecture.md": [
        ("## Operational Invariants\n", "## Operational Invariants\n" + ARCH_BULLET, 1),
        ("## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + HANDOFF_ARCH, 1),
    ],
}


def main() -> int:
    """Verify anchors, then write unless --check."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    staged = {}
    for rel, edits in EDITS.items():
        p = pathlib.Path(a.root) / rel
        t = p.read_text(encoding="utf-8")
        for old, new, count in edits:
            if t.count(old) != count:
                print(f"ANCHOR MISMATCH {rel}: {t.count(old)} != {count}: {old[:60]!r}")
                return 1
            t = t.replace(old, new)
        for line in t.split("\n"):
            if len(line) > 120 and ("pool" in line and "Compiler" in line):
                print("LONG", line[:80])
                return 1
        staged[p] = t
        print("ok", rel)
    if not a.check:
        for p, t in staged.items():
            p.write_text(t, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
