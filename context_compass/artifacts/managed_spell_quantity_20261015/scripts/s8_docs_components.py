"""S8: promote parked_versions_wired_at_conjure_2026_10_16 into src_components (exact replacements, LF).

Also re-points the numeric citations into spellbook.py, spellbook_creation_system.py and transfer_of_ownership.py
that 0.2.8248 moved or that the 0.2.8247 handoff listed as stale. Run from the repository root:
    python s8_docs_components.py <NOW>
Every old text must occur exactly once; nothing is written unless all of them do.
"""
import pathlib
import sys

NOW = sys.argv[1]
DOC = pathlib.Path("context_compass/system_docs/src_components.md")
DCIS = "`src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem.define_conduit_into_spells`"

EDITS = [
    # Spellbook Core: a dated entry.
    ("### Component: Spellbook Core (Binding and Conjure)\nManaged bind options (2026-10-15, 0.2.8242-0.2.8243):",
     "### Component: Spellbook Core (Binding and Conjure)\n"
     "Parked versions wired at conjure (2026-10-16, 0.2.8248): `SpellbookCreationSystem.define_conduit_into_spells`, the\n"
     "conjure tail's owner wiring, stamps every version in `_inactive_spells` after the active versions, under the same\n"
     "Book lock and with the same `Spell._add_owned_conduit` arguments (the root's id, name and store, its dynamic flag and\n"
     "gate controller, the Book's caching posture), and does nothing else for a parked version: no existing-object\n"
     "registration and no `resolution_required` write - what a post-conjure `bind_inactive` gives a version it parks, as\n"
     "its comment says. A version staged before conjure therefore has its CreationContextFactory (and, managed, its pool\n"
     "and registry entry) from conjure on and melds after a notch; until 0.2.8248 its first meld after a notch raised\n"
     "\"Spell has no configured CreationContextFactory.\". A stamp that raises is logged per version (\"Failed to define\n"
     "conduit into parked spell_id=<id>: <error>\") and the loop goes on.\n"
     "EVIDENCE: " + DCIS + "\n"
     "and `src/melder/aether/spellbook/spellbook.py:Spellbook.bind_inactive`.\n\n"
     "Managed bind options (2026-10-15, 0.2.8242-0.2.8243):"),
    # Release-bound creation cache: generation 21.
    ("  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.set_world_stamp` and\n"
     "  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`.\n"
     "EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem`,\n",
     "  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.set_world_stamp` and\n"
     "  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem._build_conjure_cache_state`.\n"
     "- Generation 21 (2026-10-16, `managed_spell_lease_codegen`, 0.2.8248): the envelope is unchanged; the bump retires\n"
     "  bundles written before the managed lease codegen of 0.2.8245 (plans gained the leasing and fresh managed sites,\n"
     "  the doors the \"managed\" route rows, the generalized manifest its route key). Rows of other spells did not change\n"
     "  and a release change already cold-starts every bundle (generation 9), so the bump is the explicit retirement the\n"
     "  owner asked for whenever codegen changes: each older bundle is cold once and rewritten at 21 by the next conjure.\n"
     "  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.\n"
     "EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem`,\n"),
    # Spellbook Core lock evidence (drifted since 0.2.8215; 0.2.8248 moved them again).
    ("  - src/melder/aether/spellbook/spellbook.py:7233-7244 (`_run_structural_phases`\n"
     "    at :7135; the caller-held-lock precondition is stated at :7146; remeasured 2026-09-30 at 0.2.8215)\n"
     "  - src/melder/aether/spellbook/spellbook_creation_system.py:2083 (the only\n",
     "  - src/melder/aether/spellbook/spellbook.py:7412-7433 (`_run_structural_phases`; the caller-held-lock\n"
     "    precondition is stated at :7423; remeasured 2026-10-16 at 0.2.8248)\n"
     "  - src/melder/aether/spellbook/spellbook_creation_system.py:2151 (the only\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:286 (`_phase_run_lock` created)\n"
     "  - src/melder/aether/spellbook/spellbook_creation_system.py:2055-2083\n",
     "  - src/melder/aether/spellbook/spellbook.py:288 (`_phase_run_lock` created)\n"
     "  - src/melder/aether/spellbook/spellbook_creation_system.py:2123-2151\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:5713-5719\n\nExtension Points:",
     "  - src/melder/aether/spellbook/spellbook.py:5893-5898 (`Spellbook._initialize_configuration`, the\n"
     "    configuration-mismatch branch; remeasured 2026-10-16 at 0.2.8248)\n\nExtension Points:"),
    ("  - src/melder/aether/spellbook/spellbook.py:5273-5285 (`Spellbook.bind\n    -> str`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:5422-5438 (`Spellbook.bind\n    -> str`)\n"),
    ("  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:953` passes"
     " `SafeGuard(tgt_book._lock, src_book._lock)`\n  and `:1444` passes",
     "  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:960` passes"
     " `SafeGuard(tgt_book._lock, src_book._lock)`\n  and `:1451` passes"),
    ("  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:953, 1444\n",
     "  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:960, 1451\n"),
    ("  `src/melder/aether/spellbook/spellbook.py:6546`; the patch-lane copy cited\n",
     "  `src/melder/aether/spellbook/spellbook.py:6725`; the patch-lane copy cited\n"),
    # SpellCompiler managed sites: generation 21 and the message.
    ("managed step are byte-identical, and no cache generation moves.\n"
     "EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:"
     "SitePlanEmission._emit_leased_region`,\n",
     "managed step are byte-identical. Plans are emitted at hydration, so no cache generation had to move; generation 21\n"
     "(0.2.8248) retires older bundles anyway, on the owner's ruling that a codegen change bumps the cache. A failed\n"
     "per-creation pool read calls `_raise_missing_managed_pool`: MeldExecutionError \"Managed spell '<name>' has no pool\n"
     "to lease from: its owner root was torn down, or its owner store holds no pool for this version. Meld it through a\n"
     "live root that owns it.\" (0.2.8248 dropped the pre-conjure staging cause, which conjure's parked stamp removed).\n"
     "EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:"
     "SitePlanEmission._emit_leased_region`,\n"),
    # Managed Spell Pools lifecycle.
    ("- A pool is composed at owner stamping (conjure, a post-conjure bind or bind_inactive, an ownership transfer's\n"
     "  stamps) and lives",
     "- A pool is composed at owner stamping (conjure - the active versions and, since 0.2.8248, the versions parked with\n"
     "  `bind_inactive` before it - a post-conjure bind or bind_inactive, an ownership transfer's stamps) and lives"),
    # Spellbook Conjure Pipeline subcomponent.
    ("  foundational success), then build a Conduit and wire ownership into spells.\n",
     "  foundational success), then build a Conduit and wire ownership into spells: every active\n"
     "  version, then every version parked before conjure, which gets the owner stamp alone (0.2.8248).\n"),
    ("- Spellbook lock + PhaseScheduler workers.\nKey Files (C1):\n- `src/melder/aether/spellbook/spellbook.py`\n",
     "- Spellbook lock + PhaseScheduler workers.\nKey Files (C1):\n- `src/melder/aether/spellbook/spellbook.py`\n"
     "- `src/melder/aether/spellbook/spellbook_creation_system.py`\n"),
    # Ownership Transfer subcomponent.
    ("  leases from the fresh pool its stamp composed. A failed transfer stamps every member back and discards the\n"
     "  composed pools after the rows went back.\n",
     "  leases from the fresh pool its stamp composed. A failed transfer stamps every member back and discards the\n"
     "  composed pools after the rows went back. Since 0.2.8248 conjure stamps the versions staged before it, so every\n"
     "  parked member carries a stamp; only one whose stamp raised at conjure (logged) moves unstamped, as before.\n"),
    # Flow: Conjure -> Phases -> Conduit.
    ("   - Fires pre/activated/post hooks and wires Conduit into spells.\n",
     "   - Fires pre/activated/post hooks and wires Conduit into spells (`define_conduit_into_spells`): each active\n"
     "     version gets the owner stamp, its resolution flag cleared and an existing object registered; then each\n"
     "     version parked before conjure gets the owner stamp alone (0.2.8248).\n"),
    # Code map.
    ("  end_line: 892\n  loc: 892\n  verified_at: 2026-10-15T21:40:35Z\n"
     "  note: release-bound creation-cache admission and atomic envelope persistence.\n",
     "  end_line: 900\n  loc: 900\n  verified_at: " + NOW + "\n"
     "  note: release-bound creation-cache admission and atomic envelope persistence; generation 21 (0.2.8248).\n"),
    ("  end_line: 7615\n  loc: 7615\n  verified_at: 2026-10-16T01:15:52Z\n",
     "  end_line: 7618\n  loc: 7618\n  verified_at: " + NOW + "\n"),
    ("  end_line: 2155\n  loc: 2155\n  verified_at: 2026-10-16T01:15:52Z\n",
     "  end_line: 2158\n  loc: 2158\n  verified_at: " + NOW + "\n"),
    ("  end_line: 2119\n  loc: 2119\n  verified_at: 2026-10-15T21:40:35Z\n",
     "  end_line: 2121\n  loc: 2121\n  verified_at: " + NOW + "\n"),
    # Handoff, newest first.
    ("## Context / Handoff Summary\n\n2026-10-16 non-resolvable definitions leave the Book flag (0.2.8247):",
     "## Context / Handoff Summary\n\n"
     "2026-10-16 parked versions wired at conjure (0.2.8248): Spellbook Core carries conjure's stamp of the versions\n"
     "parked before it (the owner stamp alone, as a post-conjure `bind_inactive` gives) and the creation cache's\n"
     "generation 21; the Spellbook Conjure Pipeline, the conjure flow, Managed Spell Pools (pools composed at conjure for\n"
     "parked versions too), Ownership Transfer (every parked member stamped) and the SpellCompiler's managed sites (the\n"
     "new missing-pool text, generation 21) follow. The code map remeasures four extents. Re-pointed at their code: the\n"
     "citations the 0.2.8247 entry below listed as stale - spellbook.py `_run_structural_phases` (7412-7433, :7423), :288,\n"
     "the configuration-mismatch branch (5893-5898), `Spellbook.bind` (5422-5438), `Spellbook.conduit` (6725),\n"
     "transfer_of_ownership.py's SafeGuard pair (:960, :1451) - and spellbook_creation_system.py's `_phase_run_lock`\n"
     "acquisition (2123-2151), which 0.2.8248 moved. The 2026-10-15 entry's open item, stamping versions staged before\n"
     "conjure, is closed.\n\n"
     "2026-10-16 non-resolvable definitions leave the Book flag (0.2.8247):"),
]


def main() -> None:
    """Apply every edit or none."""
    text = DOC.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    for old, new in EDITS:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"expected one occurrence, found {count}: {old[:90]!r}")
        text = text.replace(old, new)
    DOC.write_bytes(text.encode("utf-8"))
    long_lines = [n for n, line in enumerate(text.split("\n"), 1) if len(line) > 120 and "`" not in line]
    print("edits", len(EDITS), "lines", len(text.split("\n")) - 1, "long non-code lines", long_lines[:20])


if __name__ == "__main__":
    main()
