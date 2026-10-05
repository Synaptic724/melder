"""Append the investigation FACT and the design DECISION to the lane task."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md")
TS = now_utc()

NOTES = f"""- DATETIME: {TS}
  TYPE: FACT
  CLAIM: Both tiers and the staging path re-read whole. Conjure order: `_prepare_spellbook_for_conjure`
    (freeze/bind the configuration, `StructuralSnapshot.classify` -> replay phases 3-4 on a full structural
    hit, else phases 1-4 live) -> `_build_conjure_cache_state` -> phases 5-11 with `force_skip_plan_phases`
    on an executor full hit -> `_activate_conjured_conduit` (full hit: lazy-load every live payload; mixed or
    full miss: `_stage_spell_payloads_at_conjure_end` removes every payload and re-stages every live spell;
    every path: `capture_at_conjure_end`; then one emit when flagged). The existing-conduit route
    (`Spellbook._conjure_existing_conduit`) calls the same two helpers. The executor rule is payload ids
    only: `live = {{resolvable and not existing-creation}}`, `full_hit = live and not (live - cached)`; an
    existing creation or a non-resolvable definition is in `_spell_id_pool` but never in `live`, so adding,
    removing or re-keying one leaves the classification a full hit while the structural tier - whose
    `classify` compares each row's `world_stamp` (sha256 over the sorted pool ids, the posture name and the
    sorted borrowed ids) with the live one - already misses and reruns phases 1-4. The loaded payload is a
    lazy manifest package (no hydration at conjure), so the stale executor surfaces at the first meld. The
    envelope (`_build_empty_cache_data` / `_normalize_loaded_cache_data` / `_write_current_cache_to_disk_
    locked`) carries version, melder_version, python, frame_name, conduit_name, spell_payloads and the
    optional structural_payloads; `set`-style writes take the instance RLock; `CURRENT_VERSION` is 18 and
    the history is pinned by the integration test. Every Spellbook has `_aetheric_frame_configuration`
    (None before init) and `_contracted_spells` from `__init__`, so `world_stamp` is computable where the
    executor tier classifies. Tests that stub the Book (`_make_spellbook_stub`, the fastpath file's
    SimpleNamespaces) carry neither attribute, and both `_StubCachingSystem`s have no stamp surface.
    `test_cache_integration_stale_surplus_cache_still_full_hits` conjures world {{Service, Logger}} then
    {{Service}} and expects the executor full hit; the emit-shape unit test pins the exact envelope key set.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:210-300
  - src/melder/aether/spellbook/spellbook_creation_system.py:303-400
  - src/melder/aether/spellbook/spellbook_creation_system.py:616-721
  - src/melder/aether/spellbook/spellbook_creation_system.py:724-780
  - src/melder/aether/spellbook/spellbook_creation_system.py:985-1252
  - src/melder/aether/spellbook/spellbook.py:6880-7004
  - src/melder/aether/spellbook/spellbook.py:896-1066
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:285-320
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:562-619
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:700-767
  - src/melder/utilities/caching_system/caching_system.py:175-200
  - src/melder/utilities/caching_system/caching_system.py:656-818
  - tests/unit/melder/spellbook/test_cache_runtime_verification.py:15-96
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:198-240
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1563-1700
  - tests/unit/melder/utilities/test_caching_system.py:645-662
  - tests/integration/melder/spellbook/test_cache_runtime_integration.py:301-333
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:12-87
  IMPACT: The defect is the executor tier's admission rule, not a payload or a tier mismatch; the fix is one
    more condition on the full hit plus the stamp's write at staging and its carriage in the envelope.
  NEXT: DECISION note on the stamp granularity, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {TS}
  TYPE: DECISION
  CLAIM: The executor tier keys its full hit on the SAME world stamp the structural tier already uses, stored
    once per bundle (`world_stamp` in the envelope, written at staging), rather than on a per-spell
    resolution fingerprint. Rationale: (1) the stamp is the invariant the phase 3-11 artifacts are a function
    of (pool ids, posture, borrowed ids; the release and the interpreter are already in the envelope), and
    the structural tier is keyed on it by design (2026-09-26), so the two tiers become coherent - a world
    the structural tier reruns is a world the executor tier recompiles; (2) a missing live spell already
    recompiles the WHOLE eligible set (the mixed path re-stages everything), so a coarse key costs nothing
    new on that path, and the one case it newly recompiles - an existing creation or a non-resolvable
    definition added, removed or re-keyed - is exactly the defect; (3) a per-spell fingerprint would be a
    second keying scheme beside the structural rows and a redesign of both tiers, not a fix. Consequence:
    a world that only REMOVED a spell is a changed world and recompiles once (mixed), then full-hits; the
    integration contract "stale surplus cache still full hits" is retired and re-pinned as "a removed spell
    is a changed world: rerun, then full hit". Generation 19 (`executor_world_stamp`) retires bundles
    without the field; a loaded bundle without it (hand-made) carries "" and never full-hits (fail-closed).
    The owner is told of the retired contract at the report; rollback is the one condition.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:34-135
  - src/melder/aether/spellbook/spellbook_creation_system.py:1095-1162
  - tests/integration/melder/spellbook/test_cache_runtime_integration.py:301-333
  IMPACT: One envelope field, one classification condition, one staging write, one generation entry; the
    rest is tests and docs.
  NEXT: patch docs (architecture, component Spellbook Core / caching, code description) and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(NOTES)
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTES + "## Context / Handoff Summary\n", "handoff")
write_text(TASK, text, nl)
print("noted", TS)
