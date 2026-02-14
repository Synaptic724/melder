# Task: Add Conduit MeldGate Enable/Disable

## Metadata
- Task ID: TASK-2026-01-30-meld-gate-enable-disable
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-31

## Objective
Add a shared MeldGate object owned by Conduit to deterministically block/unblock melds across a conduit tree, with a minimal-overhead bool check on the hot path and an event to block threads when disabled.

## Scope Boundaries
- In scope:
  - New MeldGate class with enable/disable + cleanup.
  - Conduit owns MeldGate and shares it with lesser conduits.
  - Conduit.meld blocks immediately after check_cleaned() when disabled.
  - Conduit enable_meld()/disable_meld() facade methods.
  - Upgrade-to-normal creates a new MeldGate for the upgraded tree and propagates it to lessers.
  - Update IConduit interface for new methods.
  - Document behavior in components doc.
- Out of scope:
  - Automatic trigger points for enable/disable (manual control only).
  - Changes to contract/link validation semantics.

## Steps / Checklist
- [x] Add MeldGate class and docstrings.
- [x] Wire MeldGate into Conduit init, create_lesser_conduit, cleanup.
- [x] Add Conduit enable_meld/disable_meld and gate check in meld.
- [x] Replace MeldGate on upgrade_to_normal and propagate to lessers.
- [x] Update IConduit interface.
- [x] Update components documentation to include MeldGate.
- [x] Add test coverage (blocking/unblocking).

## Deliverables
- MeldGate class + Conduit wiring
- Updated IConduit interface
- Documentation update
- Tests (not yet run)

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_gate.py` (new)
- `src/melder/aether/conduit/conduit.py`
- `src/melder/utilities/interfaces/interfaces.py`
- `components/src_components.md`
- `tests/component/melder/aether/conduit/test_conduit_component_meld_gating.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/component/melder/aether/conduit/test_conduit_component_meld_gating.py`

## Risks / Rollback Notes
- Risk: thread blocking if enable is never called.
- Rollback: revert MeldGate integration and remove new API methods.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Introduce a Conduit-owned MeldGate (shared across conduit tree) to block melds when disabled. Gate check is immediately after check_cleaned() in Conduit.meld; bool read is hot-path, event wait only when disabled. Upgraded conduits create a new gate and propagate to their lesser subtree. Manual enable/disable only.
