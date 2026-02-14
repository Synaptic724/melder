# Task: Decide deep scan requirement and align meld contract docs

- Completed: 2026-01-17
- Summary: Documented deep scan and meld contract decisions; aligned meld docstrings to the multi-entry API.

## Metadata
- Task ID: TASK-2026-01-17-melder-di-contract-decisions-doc-alignment
- Story: STORY-2026-01-17-melder-architecture-components-docs
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-17
- Updated: 2026-01-17

## Objective
Record the approved decisions on post-init SpellMap deep scan and the
Conduit.meld public contract, then align architecture/components docs and
meld-related docstrings with those decisions (no behavior changes).

## Scope Boundaries
- In scope:
  - Document decisions in `context_compass/architecture/src_architecture.md`
    and `context_compass/components/src_components.md`.
  - Align `Conduit.meld` and `SpellSpace.meld` docstrings with the approved
    multi-entry resolution contract.
  - Update story checklist and move task to completed on delivery.
- Out of scope:
  - Runtime behavior changes.
  - Tests.
  - Any `__*.json` metadata.

## Steps / Checklist
- [x] Add task to story checklist.
- [x] Document deep-scan decision and meld contract in architecture/components docs.
- [x] Align Conduit/SpellSpace meld docstrings with the approved contract.
- [x] Update open questions to reflect resolved items and remaining gaps.
- [x] Move task to completed with summary.

## Deliverables
- Updated architecture and components docs with decision notes.
- Updated docstrings for `Conduit.meld` and `SpellSpace.meld`.

## Files / Paths Impacted
- `context_compass/architecture/src_architecture.md`
- `context_compass/components/src_components.md`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `context_compass/stories/2026-01-17_melder_architecture_components_docs_story.md`

## Validation
- Not run.
- Recommended commands:
  - None (documentation-only).

## Risks / Rollback Notes
- Risk: docstrings overstate supported entry modes; mitigate by citing sources
  and keeping behavior claims aligned to code paths.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- Decisions recorded in architecture/components docs; Conduit/SpellSpace meld
  docstrings aligned to multi-entry resolution contract; deep scan remains an
  explicit implementation gap.
