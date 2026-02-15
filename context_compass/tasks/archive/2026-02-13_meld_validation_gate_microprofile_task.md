Completed: 2026-02-14
Summary: Cached per-frame change-control manager lookup in Meld validation gating while preserving per-call dirty-root checks and gate semantics.

# Task: Microprofile Meld Validation Gates

## Metadata
- Task ID: TASK-2026-02-13-meld-validation-gate-microprofile
- Story: STORY-2026-02-13-optimize-meld-paths
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-13
- Updated: 2026-02-14

## Objective
Quantify and reduce repeated validation-gate overhead in meld execution without
weakening structural/resolution/change-control safety guarantees.

## Scope Boundaries
- In scope:
- `_ensure_lineage_resolvable`, `_gated_validation_required`, and
  `_ensure_resolution_resolvable` hot-path checks.
- Targeted micro-optimizations that preserve gate semantics.
- Focused validation for gated/dirty/valid states.
- Out of scope:
- Removing or bypassing required validation gates.
- Mutation-runtime policy changes.

## Steps / Checklist
- [x] Capture baseline call-flow costs for gated vs warm-valid states.
- [x] Identify repeated checks that can be collapsed or cached safely.
- [x] Implement micro-optimizations preserving gate correctness.
- [x] Add tests for validity state transitions and dirty-root error behavior.

## Deliverables
- Evidence-backed validation-gate cost profile and optimization delta.
- Updated tests for unchanged gate semantics.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`
- `tests/unit/melder/aether/conduit/meld/test_meld.py`
- `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract*.py`

## Validation
- `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py` -> `55 passed`
- `python -m pytest -q tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract.py tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_more.py` -> `63 passed`

## Risks / Rollback Notes
- Risk: subtle gating regressions in dirty-root or invalid lineage behavior.
- Rollback: revert micro-optimizations and keep current explicit gate checks.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created from meld discovery hotspot #5. Next step is to define a focused
microprofile harness for gate-heavy paths before code edits.
Activated after closure of `TASK-2026-02-13-meld-override-shape-hotpath`.
Implementation update (2026-02-14):
- Added per-frame cached change-control manager lookups in
  `Meld._get_cached_change_control_manager(...)` and wired
  `_gated_validation_required(...)` to use cached managers while preserving
  per-call dirty-root checks (`is_root_dirty` still runs every call).
- Added unit coverage for cache behavior:
  `test_gated_validation_required_reuses_cached_change_control_manager`.
- No change to validation-gate outcomes for valid/unknown/gated/invalid states;
  existing gate tests continue to pass.
User confirmed acceptance and directed progression to the next ticket.
