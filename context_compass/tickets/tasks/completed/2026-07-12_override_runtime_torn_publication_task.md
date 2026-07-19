- Completed: 2026-07-12T21:00:00Z
- Summary: Every multi-field last-entry cache in the phase-11 override
  runtime (7 cells across 5 files - the 2 reported targeting caches plus
  the last_state executor cell and both finalize-step dict cells) now
  publishes ONE immutable tuple per cache with snapshot reads - no torn
  observations, no locks on the hot path. Closed on owner directive;
  pytest Not run by agent - reopen on red.

# Task: phase-11 override runtime torn-publication fix

## Metadata
- Task ID: TASK-2026-07-12-override-runtime-torn-publication
- Parent: none (owner-reported defect, 2026-07-12)
- Status: in_progress
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-12T19:45:00Z
- Updated: 2026-07-12T19:45:00Z

## Problem / Opportunity
Owner finding: the phase-11 override runtime (shared by every thread
melding one compiled root) published its two last-entry caches as
SEPARATE fields/slots/keys. Each individual write is structurally safe,
but interleaved writers can assemble a logical cache entry that never
existed in any real meld: (a) the override-target cache can pair
key_B/value_B with map_A/shape_A, corrupting prepared routing or (in
the overlapping-override lane) feeding another meld's socket map
directly; (b) the last-shape cache can pair shape_B/arity_1 with
executor_A - executors are shape-specialized, so the wrong one can
KeyError, override the wrong constructor parameter, or build the root
with the wrong dependency. Owner-chosen repair: publish each cache
entry as ONE immutable tuple snapshot (single reference store = atomic
on 3.14t); no locks.

## Ticket Contract
- ENTRY_GATE: owner directive with the full interleaving analysis and
  the chosen repair shape; routed on attention_board.md.
- EXECUTION_BOUNDARY: the last-entry caches only - snapshot cells, no
  semantic change to resolution, specialization, or the dict-backed
  bound-executor caches.
- EXIT_GATE: all torn-publication sites converted; owner-run green.
- FAILURE_ESCALATION: BLOCKER if any consumer depends on per-field
  publication (none found).

## Notes
- DATETIME: 2026-07-12T19:50:00Z
  TYPE: FACT
  CLAIM: FIX LANDED AT ALL SITES - the sweep found MORE than the two
    reported: (1+2) SpellOverrideTargetingCodegenCreation in BOTH
    strategy families (generalized + many_only artifacts) - the
    4-field single cache and 3-field multi cache each collapsed to one
    Optional[tuple] slot (_last_single_cache/_last_multi_cache);
    readers load once + unpack; writers publish one tuple; __slots__/
    __init__/cleanup synced. (3) generalized_manifest_overrides_runtime
    last_state 3-slot list -> one-slot last_state_cell[0] tuple.
    (4+5) BOTH finalize-creation-context steps (generalized +
    many_only) carried the SAME bug in dict flavor
    (override_last_state 3-key dict) -> override_last_state_cell[0]
    tuple. Grep-clean: zero per-field cache tokens remain in src; 7
    snapshot cells across 5 files. Semantics preserved exactly (key
    equality + value identity for single; signature equality for
    multi; shape identity + arity equality for last-state). AST: Not
    run (standing replica rot; every edited region read back via
    file-tool during editing + grep sentinels verified). pytest: Not
    run (owner-run 3.14t; the compiler/creation-context suites +
    override integration trees are the run set).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/artifacts/spell_override_targeting_codegen_creation.py
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/artifacts/spell_override_targeting_codegen_creation.py
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py
  IMPACT: no thread can ever consume a cache entry assembled from two
    different melds; constructor routing/arguments can no longer cross
    calls.
  NEXT: owner-run; then closure walk.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Owner-reported torn publication in the shared phase-11 override
runtime's last-entry caches. Repair = one immutable tuple snapshot per
cache (atomic reference swap, no locks), landed at 7 cells across 5
files including three sites beyond the report (many_only mirror +
both finalize steps). Awaiting owner run.
