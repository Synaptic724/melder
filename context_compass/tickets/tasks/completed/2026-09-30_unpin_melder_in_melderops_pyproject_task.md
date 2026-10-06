# Task: Unpin Melder in MelderOps' pyproject so any installed Melder satisfies it

## Metadata
- Task ID: TASK-2026-09-30-unpin-melder-in-melderops-pyproject
- Story: none; follows tickets/tasks/completed/2026-09-30_deliver_0_2_8215_wheel_and_revalidate_melderops_task.md
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-30T21:47:32Z
- Updated: 2026-10-01T09:46:54Z

- Completed: 2026-10-01T09:46:54Z
- Summary: priv_commandops/pyproject.toml requires `melder` with no version (was `melder>=0.2.8212`); its
  comment keeps the history of the Melder APIs MelderOps calls and says to install the melder_private dist/
  wheel (PyPI's newest is 0.2.8207). command_0 told (M0-159). No source change.

## Objective
Owner direction (chat, 2026-09-30), after the 0.2.8215 delivery left MelderOps' floor at `melder>=0.2.8212`:
"yeah can't we unpin it so it doesn't matter? go ahead and fix the version so its anything". Change the Melder
requirement in `priv_commandops/pyproject.toml` from `melder>=0.2.8212` to `melder` (any version) and bring its
comment in line, so installing a new Melder build never needs a floor bump.

## Ticket Contract
- ENTRY_GATE: owner direction in chat; this board row; the PLAN note before the edit.
- EXECUTION_BOUNDARY: priv_commandops - the one dependency line and its comment in `pyproject.toml` (CRLF kept);
  melder_0's own note line and a NOTICE on its boards. No source, test, system-doc or patch-doc edits there.
- DEPENDENCIES: none.
- EXIT_GATE: pyproject parses (tomllib) with `melder` unconstrained; the comment says why; command_0 is told.
- FAILURE_ESCALATION: none expected; a parse failure reverts the edit from the saved copy.

## Scope Boundaries
- In scope: the dependency line and its comment.
- Out of scope: MelderOps' system docs and active patch docs that state a floor (their owners are told), the
  installed environments (their metadata only matters at install time), publishing.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-01T09:46:54Z) the owner turned it in in chat, confirming the acceptance criteria. Earlier:
  in_progress -> review and draft -> in_progress below.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-09-30T21:56:10Z) the edit parses and command_0 was told (MEASURE note);
  the owner's turn-in remains. Earlier: draft -> in_progress below.
- from_state: draft
- to_state: in_progress
- transition_reason: (2026-09-30T21:47:32Z) owner direction in chat; ticket and board row before the edit.

## Steps / Checklist
- [x] Save the current pyproject.toml; edit the dependency and its comment; parse check.
- [x] Update melder_0's note line on priv_commandops' attention board; NOTICE command_0.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- priv_commandops/pyproject.toml requiring `melder` with no version constraint.

## Files / Paths Impacted
- priv_commandops/pyproject.toml; priv_commandops/context_compass/attention_board.md (melder_0's note line and an
  alert); priv_commandops/context_compass/mailbox_board.md (one NOTICE).

## Validation
- tomllib parse of the edited file: dependencies greenlet==3.5.5 and melder; CRLF kept; the saved
  after-copy equals the live file. Not run: installs and MelderOps tests (the change only matters when an
  environment is resolved).

## Risks / Rollback Notes
- With no floor the resolver accepts any Melder: PyPI's newest is 0.2.8207, so a fresh environment that does not
  install the local wheel gets a Melder without the 0.2.8212 APIs MelderOps calls, and fails at runtime rather
  than at install. Rollback: restore the saved pyproject.toml.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No deleted comment: the floor history stays, updated.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed: the pyproject comment)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melderops_melder_unpin_20260930/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes

- DATETIME: 2026-09-30T21:47:50Z
  TYPE: PLAN
  CLAIM: MelderOps requires `melder>=0.2.8212` on pyproject.toml line 112, under a comment (lines 82-111) that
    records why each earlier floor was raised and which Melder APIs MelderOps calls (0.2.79 root lookups, 0.2.8206
    address keys, 0.2.8208 frame lookups, 0.2.8212 get_configuration_dictionary). The file is CRLF. Edit: the line
    becomes `"melder",`; the comment keeps that history (it tells which build carries what MelderOps calls) and its
    last floor sentence is replaced by the unpin and its consequence. Measured consequence: PyPI's newest Melder is
    0.2.8207 - an empty 3.14t env resolves `melder` to 0.2.8207 and refuses `melder>=0.2.8212` - so without a
    floor a fresh install that does not take the local wheel gets a Melder lacking 0.2.8212's APIs and the 0.2.8215
    fix, and fails at runtime instead of at install. The owner chose this tradeoff; the NOTICE says it.
  EVIDENCE:
  - context_compass/artifacts/melderops_melder_unpin_20260930/pyproject_before.toml:82-113
  - context_compass/artifacts/melderops_melder_unpin_20260930/pypi_probe.log:1-13
  IMPACT: A new Melder build installs into MelderOps' environments without a pyproject change.
  NEXT: Edit the dependency line and comment (CRLF kept) and parse-check the file.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T21:56:10Z
  TYPE: MEASURE
  CLAIM: priv_commandops/pyproject.toml requires `melder` with no version: line 116 reads `"melder",` (was
    `"melder>=0.2.8212",`). The comment above it keeps the floor history, adds what 0.2.8215 fixes and closes with
    an UNPINNED paragraph (owner direction; install the melder_private dist/ wheel; PyPI's newest is 0.2.8207).
    tomllib parses the dependencies as greenlet==3.5.5 and melder; the file stays CRLF with no bare LF, and the
    saved after-copy matches the live file byte for byte (re-checked after re-onboarding). melder_0's note line
    on priv_commandops' attention board says unpinned, and NOTICE M0-159 tells command_0, naming the system-doc
    floor lines and the active foundation_packages patch that still describe a floor. Not run: no install and
    no MelderOps tests - the change only matters when an environment is resolved.
  EVIDENCE:
  - context_compass/artifacts/melderops_melder_unpin_20260930/apply_unpin.log:1-2
  - context_compass/artifacts/melderops_melder_unpin_20260930/pyproject_after.toml:82-116
  - ../priv_commandops/context_compass/attention_board.md:224-226
  - ../priv_commandops/context_compass/mailbox_board.md:186-196
  IMPACT: New Melder builds install into MelderOps without a pyproject change; checking that the installed build
    carries the APIs MelderOps calls moves from the resolver to whoever installs it.
  NEXT: The owner turns the task in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T09:46:54Z
  TYPE: DECISION
  CLAIM: The owner turned the task in (chat: "yeah ok turn in all your shit please and close it"), confirming the
    acceptance criteria. The candidate set for "all" is this task, the only active row carrying melder_0 in
    melder_private. Not closed, because their work is unfinished and the owner has not seen them listed: two
    parked backlog tickets carrying melder_0 (the atomic frame retirement story, the host read surface promotion
    task) and two priv_commandops rows carrying melder_0 from 2026-08-16 (a blocked design story and a ready task
    of six threading findings); they go to the owner for a decision.
  EVIDENCE: context_compass/artifacts/melderops_melder_unpin_20260930/turn_in_candidates.txt:1-11
  IMPACT: This lane closes with nothing left in it; the other four stay where they are until the owner decides.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done 2026-10-01T09:46:54Z: the owner turned it in. priv_commandops/pyproject.toml requires `melder` with no version
(line 116), the comment says why and what to install, and command_0 was told (M0-159). Nothing is left here.
Opened 2026-09-30T21:47:32Z on the owner's direction to unpin Melder in MelderOps.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
