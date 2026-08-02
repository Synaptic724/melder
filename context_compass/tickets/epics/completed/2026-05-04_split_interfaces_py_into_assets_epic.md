# Epic: Split Interfaces.py Into Per-Interface Asset Files
- Completed: 2026-05-10T00:06:36Z
- Summary: Closed after the interface surface was split into one-file-per-
  interface assets and the aggregator/import surface validated cleanly.

## Metadata
- Epic ID: EPIC-2026-05-04-split-interfaces-py-into-assets
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-04T23:22:58Z
- Updated: 2026-05-10T00:06:36Z
- Target Window: 2026-Q2
- Related Program/Initiative: Interface-surface maintainability and runtime contract hygiene

## Problem / Opportunity
`src/melder/utilities/interfaces/interfaces.py` has grown into a single giant
surface. It is `10,416` LOC and currently contains about `81` top-level
interface classes. That is too large to maintain cleanly, makes review noisy,
and turns small interface changes into high-conflict edits.

The requested target state is:
- one file per interface class
- those files live under `src/melder/utilities/interfaces/assets/`
- `interfaces.py` remains the single explicit import lane
- `__init__.py` stays non-exporting

## MRP Alignment (Most Reasonable Product)
The MRP is not a brand-new interface architecture. The MRP is:
- one `assets/` folder under the interfaces surface
- one file per interface class
- one stable aggregator `interfaces.py`
- no semantic drift in the actual protocol contracts
- enough task structure that each interface move is durable and reviewable

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the split into an `assets` folder
  with one file per interface class and one aggregator import lane through
  `interfaces.py`.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/interfaces/interfaces.py`
  - `src/melder/utilities/interfaces/assets/`
  - focused tests and validation needed to prove the split still imports
    correctly
- DEPENDENCIES:
  - repo typing rules from the synaptic Python overlay
  - no `__init__.py` export wiring
  - current interface surface consumers across `src/melder`
- EXIT_GATE: the giant file is split into one-file-per-interface assets,
  `interfaces.py` is the single explicit aggregator, and focused validation
  proves the new surface imports cleanly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a subset of interfaces must
  keep co-location for inheritance or runtime import reasons that make the
  one-file-per-interface rule materially unsafe.

## Goals (Outcomes)
- Create `src/melder/utilities/interfaces/assets/`.
- Move each interface class into its own file.
- Keep `interfaces.py` as the single import lane.
- Keep `__init__.py` empty/non-exporting.
- Create one task per interface class for durable tracking.

## Non-Goals (Explicit Exclusions)
- Changing the actual public protocol names.
- Changing interface semantics unless required by the split.
- Re-export wiring in `__init__.py`.
- Refactoring unrelated runtime behavior.

## Scope Boundaries
- In scope:
  - interface file split
  - aggregator rewrite
  - import-path maintenance
  - per-interface task generation
- Out of scope:
  - unrelated runtime or spell/crystallizer semantics
  - public API redesign
  - folder-wide `__init__.py` export patterns

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the full asset split landed, the per-interface extraction
  task map was generated and closed, and the focused import/inheritance ring is green.

## Success Metrics
- `interfaces.py` stops being the only definition file.
- every interface class has its own file in `assets/`.
- the aggregator stays the only normal import lane.
- imports and focused tests stay green.

## Requirements (Functional + Non-Functional)
- Functional:
  - one file per interface class
  - one aggregator module
  - one task per interface class
- Non-functional:
  - maintainability improves
  - no `__init__.py` export wiring
  - no silent contract drift
  - import surface remains stable

## Constraints / Assumptions
- Some interfaces inherit from or annotate each other, so the split has to
  follow dependency order rather than a blind text chop.
- The repo's `__init__.py` export rule remains in force.
- The split should preserve current interface names and the aggregator import
  lane.

## Dependencies / External References
- `src/melder/utilities/interfaces/interfaces.py`
- `src/melder/crystallizer/spell_crystal.py`
- `src/melder/crystallizer/crystallizer.py`
- `src/melder/aether/aether.py`

## Milestones (Track Progress)
- [x] Milestone 1: epic + per-interface task breakdown exists
- [x] Milestone 2: assets folder and aggregator split land
- [x] Milestone 3: focused validation proves the refactor is stable

## Stories (Required to Complete)
- [x] Story: stage task breakdown for all interface classes
- [x] Story: split the definitions into `assets/`
- [x] Story: validate the aggregator/import surface

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: generate one backlog task per interface class in `interfaces.py`
- [x] Task: extract `ICleanable` into `assets/icleanable.py` and validate the first seam
- [x] Task: refactor the remaining interfaces into the new assets folder and aggregator
- [x] Task: verify import and test stability after the split
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- `assets/` exists under the interfaces surface.
- each interface class has its own file.
- `interfaces.py` aggregates the split files and remains the main import lane.
- per-interface backlog tasks exist.
- focused validation is green.

## Risks / Mitigations
- Risk: cross-interface inheritance/imports create split instability.
  Mitigation: keep `interfaces.py` as the aggregator and validate the import
  surface immediately after each tranche.
- Risk: the split changes protocol semantics accidentally.
  Mitigation: move definitions mechanically first and avoid semantic edits.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- compile validation over the split interface surface
- focused test/import validation over consumers that touch the shared
  interfaces lane

## Rollout / Adoption Plan
- create epic and task breakdown
- extract `ICleanable` first as the root base protocol
- continue one interface task at a time in dependency order
- keep `interfaces.py` stable as the aggregator import lane

## Open Questions
- Whether any subset of interfaces should later regroup by domain after the
  one-file-per-interface baseline lands.
- Whether the separate builder helper should remain public or narrow further.

## Decision Log
- 2026-05-04T23:22:58Z: Opened after the user explicitly requested an
  `assets/` folder with one file per interface class and one aggregator
  import lane through `interfaces.py`.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-04T23:22:58Z
  TYPE: FACT
  CLAIM: The current interface surface is large enough to justify the split as
    a maintainability refactor. `interfaces.py` is `10,416` LOC and contains
    about `81` top-level interface classes. Some of those interfaces also
    inherit from or annotate each other, which means the split has to follow a
    dependency graph and keep `interfaces.py` as the import aggregator rather
    than blindly chopping the file.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py
  - file_measure: `10,416 LOC`
  - class_inventory:
    `ICleanable` through `IChangeControlManager` (`81` classes)
  IMPACT: The refactor is large but mechanical, and it needs explicit ticket
    structure plus dependency-aware sequencing before implementation and
    validation.
  NEXT: generate the per-interface backlog tasks, route the first active task
    to `ICleanable`, then start the first extraction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-04T23:41:13Z
  TYPE: MEASURE
  CLAIM: The interfaces split is now landed as one full lower-case asset set.
    The restored `interfaces_old.py` was used as the source of truth, one
    lower-case asset file per interface was generated under
    `src/melder/utilities/interfaces/assets/`, `interfaces.py` was rewritten
    into the single explicit aggregator import lane with `__all__`, and the
    focused import/inheritance ring passed after the full copy. The generated
    per-interface extraction tasks were then closed and moved to completed
    because the work they described was satisfied by the bulk tranche.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces_old.py
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/utilities/interfaces/assets/
  - tests/unit/melder/utilities/interfaces/test_interface_inheritance.py
  - validation_result:
    python -m pytest -q -p no:cacheprovider tests/unit/melder/utilities/interfaces/test_interface_inheritance.py -> 23 passed
  IMPACT: The interface surface is no longer trapped in one 10k-line file and
    the import-lane question is now answered concretely by code instead of
    planning alone.
  NEXT: review whether any subset of the generated asset files should regroup
    later by domain, or accept the one-file-per-interface layout as-is.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the interfaces split into one-file-per-interface assets while
keeping `interfaces.py` as the single import lane.
