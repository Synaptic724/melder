# Task: fix conduit interface truth and annotation cluster

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-conduit-interface-truth-and-annotation-cluster
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T15:40:12Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the current `conduit.py` mypy cluster by correcting stale interface drift,
adding the real missing collaborator surfaces, and tightening the local
annotation/narrowing issues without adding shims.

## Ticket Contract
- ENTRY_GATE: the user-provided `conduit.py` cluster includes interface-surface
  gaps (`ISpellbook`, `INexus`, `IConduit`, `IMeld`, `IConduitResolutionState`,
  `IConfiguration`), abstract-class complaints (`Meld`, `ConduitWard`,
  `Creations`), and local annotation/narrowing errors.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - directly implicated interface files only where the surface is real:
    - `src/melder/utilities/interfaces/ispellbook.py`
    - `src/melder/utilities/interfaces/inexus.py`
    - `src/melder/utilities/interfaces/iconduit.py`
    - `src/melder/utilities/interfaces/imeld.py`
    - `src/melder/utilities/interfaces/iconduitresolutionstate.py`
    - `src/melder/utilities/interfaces/iconfiguration.py`
    - `src/melder/utilities/interfaces/iconduitward.py`
    - `src/melder/utilities/interfaces/icreations.py`
  - directly implicated concrete files only if interface truth requires them:
    - `src/melder/aether/conduit/meld/meld.py`
    - `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
    - `src/melder/aether/conduit/creations/creations.py`
- DEPENDENCIES:
  - current conduit runtime ownership model
  - no shims, no casts, no fake local protocols
- EXIT_GATE:
  - the targeted `conduit.py` cluster is gone
  - stale/lying interface requirements are corrected at the source
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any interface appears to expose
  the wrong architectural responsibility and the correct ownership boundary is ambiguous

## Scope Boundaries
- In scope:
  - stale interface truth causing this `conduit.py` cluster
  - the local `Conduit` annotation and narrowing fixes tied to that truth
- Out of scope:
  - unrelated repo-wide mypy debt
  - broader interface redesign beyond the directly implicated surfaces

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user supplied a bounded conduit cluster and the first
  investigation pass showed two clearly stale interfaces plus several honest
  missing surfaces

## Steps / Checklist
- [ ] correct the clearly stale interfaces (`IConduitWard`, `ICreations`) first
- [ ] add the missing truthful surfaces to the relevant interfaces
- [ ] patch the local `Conduit` annotations and narrowings
- [ ] rerun targeted mypy on the conduit ring
- [ ] continue only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a bounded conduit interface-truth fix
- a bounded conduit annotation/narrowing fix

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py`
- `src/melder/utilities/interfaces/ispellbook.py`
- `src/melder/utilities/interfaces/inexus.py`
- `src/melder/utilities/interfaces/iconduit.py`
- `src/melder/utilities/interfaces/imeld.py`
- `src/melder/utilities/interfaces/iconduitresolutionstate.py`
- `src/melder/utilities/interfaces/iconfiguration.py`
- `src/melder/utilities/interfaces/iconduitward.py`
- `src/melder/utilities/interfaces/icreations.py`
- only if required by the truthful fix:
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
  - `src/melder/aether/conduit/creations/creations.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit\conduit.py`

## Risks / Rollback Notes
- Medium risk. A few interfaces are clearly stale, so I need to correct them
  without widening into unrelated interface cleanup.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-18T15:40:12Z
  TYPE: FACT
  CLAIM: The conduit cluster contains two clearly stale interfaces plus several
    honest missing collaborator surfaces. `IConduitWard` currently claims
    `has_live_creation(...)` / `describe_live_creation_status(...)`, which are
    conduit/meld responsibilities, and `ICreations` still declares fake
    internal cleanup surface and fake owner/spellspace protocol shims that the
    real `Creations` class does not implement.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitward.py:1-90
  - src/melder/utilities/interfaces/icreations.py:1-140
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1-220
  - src/melder/aether/conduit/creations/creations.py:1-220
  - src/melder/aether/conduit/conduit.py:181-252
  IMPACT: This cluster should be fixed by correcting interface truth, not by
    forcing the concrete classes to satisfy bullshit methods they do not own.
  NEXT: patch the stale interfaces first, then add the missing truthful
    surfaces and clean the local `Conduit` typing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T15:40:12Z
  TYPE: FACT
  CLAIM: After the interface-truth patch, the remaining `conduit.py` errors are
    purely local typing issues. The stale protocol/fake-surface layer is no longer
    the blocker.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit\conduit.py 2>&1 | Select-String 'src\\melder\\aether\\conduit\\conduit.py:'`
  - src/melder\aether\conduit\conduit.py:582-601
  - src/melder\aether\conduit\conduit.py:1015-1026
  - src/melder\aether\conduit\conduit.py:1468-1488
  - src/melder\aether\conduit\conduit.py:1716-1728
  - src/melder\aether\conduit\conduit.py:2317-2319
  - src/melder\aether\conduit\conduit.py:4049-4098
  IMPACT: I can finish this lane inside `conduit.py` without inventing more interface hacks.
  NEXT: patch the remaining local Conduit typing/narrowing sites and rerun targeted mypy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T15:40:12Z
  TYPE: MEASURE
  CLAIM: The targeted `conduit.py` cluster is green.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitward.py:1-220
  - src/melder/utilities/interfaces/icreations.py:1-220
  - src/melder/utilities/interfaces/imeld.py:1-40
  - src/melder/utilities/interfaces/iconfiguration.py:1-40
  - src/melder/utilities/interfaces/iconduitresolutionstate.py:1-180
  - src/melder/utilities/interfaces/inexus.py:280-340
  - src/melder/utilities/interfaces/ispellbook.py:1-40
  - src/melder/utilities/interfaces/ispellbook.py:220-420
  - src/melder/utilities/interfaces/iconduit.py:1-80
  - src/melder/utilities/interfaces/iaether.py:1-120
  - src/melder\aether\conduit\conduit.py:181-252
  - src/melder\aether\conduit\conduit.py:526-601
  - src/melder\aether\conduit\conduit.py:1015-1028
  - src/melder\aether\conduit\conduit.py:1468-1490
  - src/melder\aether\conduit\conduit.py:1716-1728
  - src/melder\aether\conduit\conduit.py:2292-2319
  - src/melder\aether\conduit\conduit.py:3428-3778
  - src/melder\aether\conduit\conduit.py:4049-4098
  - validation_result: `.\.venv_new\Scripts\python.exe -m mypy --show-error-codes --show-column-numbers --no-error-summary src\melder\aether\conduit\conduit.py 2>&1 | Select-String 'src\\melder\\aether\\conduit\\conduit.py:'` -> no output
  IMPACT: The user-supplied conduit cluster is fixed without adding shims. The two fucked spots were corrected at the source: `IConduitWard` stopped claiming conduit/meld responsibilities, and `ICreations` stopped pretending to expose stale fake cleanup surfaces.
  NEXT: wait for the next exact cluster or widen only if the user points at the next file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active conduit cluster lane. Current evidence says the right order is:
1. fix stale interfaces,
2. add real missing surfaces,
3. patch local Conduit typing.
