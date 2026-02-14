Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Task: Enforce Strict Meld Creations Routing

## Metadata
- Task ID: TASK-2026-02-07-meld-strict-creations-routing
- Story: standalone
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Remove implicit fallback behavior in meld resolution/registration paths so creations routing is deterministic and fails fast when required scope containers are missing.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/meld.py` strict routing for creations and spellspace paths.
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py` strict target-kind routing and strict creations requirements.
- Eliminate owner/caller fallback chains in internal resolution/registration helpers.
- Keep `Existence.unique_per_spell_space` caller-scoped end-to-end.
- Out of scope:
- Public API redesign.
- Non-meld modules.
- Broad test rewrites outside direct fallout of this routing change.

## Steps / Checklist
- [ ] Audit all internal fallback branches for creations/owner routing in `meld.py` and `meld_engine.py`.
- [ ] Remove fallback selection in internal helpers and replace with strict route contracts.
- [ ] Ensure fast paths treat `ExecutionPlanTargetKind.SPELLSPACE` as caller-scoped and do not fall through to owner routing.
- [ ] Make missing required creations contexts explicit runtime errors (no silent reuse/registration bypass).
- [ ] Update touched docstrings to reflect strict contracts.
- [ ] Run focused meld unit tests and report results.

## Deliverables
- Deterministic creations routing in meld and meld engine without implicit fallback behavior.
- Spellspace routing isolated to caller scope for borrowed `unique_per_spell_space` spells.
- Updated internal docstrings matching strict routing contracts.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`
- `context_compass/tasks/2026-02-07_meld_strict_creations_routing_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld_2.py`

## Risks / Rollback Notes
- Strict routing may surface hidden lifecycle inconsistencies previously masked by fallback behavior.
- Existing tests that assert fallback semantics will fail and must be updated or removed per strict contract decision.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
User-directed behavior change: remove fallback semantics for spell/creations routing in meld internals. The expected contract is explicit route ownership (caller vs owner), explicit spellspace caller scoping, and fail-fast errors on missing required contexts.

