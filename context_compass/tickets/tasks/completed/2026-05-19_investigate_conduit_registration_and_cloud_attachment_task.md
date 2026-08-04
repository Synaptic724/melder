# Task: Investigate Conduit Registration And Cloud Attachment
- Completed: 2026-05-20T08:58:57Z
- Summary: Closed after documenting the live conduit registration path: root conjure and lesser-to-normal both register first into the frame-owned root registry and then into cloud exposure only for named dynamic conduits.

## Metadata
- Task ID: TASK-2026-05-19-investigate-conduit-registration-and-cloud-attachment
- Story: none
- Epic: EPIC-2026-05-18-recompose-conduit-aether-spellbook-runtime-ownership
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-19T22:15:15Z
- Updated: 2026-05-20T08:58:57Z

## Objective
Trace how a conduit becomes known to Aether and ConduitCloud today, comparing
root conjure and lesser-to-normal upgrade paths so we can see whether the
registration/notification feature is intact or has drifted.

## Ticket Contract
- ENTRY_GATE: this task is routed on `attention_board.md` and the first evidence-backed note is recorded before broader discovery continues.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/aether.py`
  - `src/melder/aether/aetheric_frame/conduit_cloud.py`
  - `src/melder/aether/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/spellbook/spellbook.py`
- DEPENDENCIES:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/aether.py`
  - `src/melder/aether/aetheric_frame/conduit_cloud.py`
  - `src/melder/aether/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/spellbook/spellbook.py`
- EXIT_GATE: the current registration path into Aether and ConduitCloud is explicit for both root conjure and lesser-to-normal upgrade.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the registration path is split or inconsistent enough that the next cloud-removal cut needs redesign first.

## Scope Boundaries
- In scope:
  - root conduit registration during conjure
  - dynamic cloud registration during root conjure
  - lesser-to-normal upgrade registration path
  - current separation between Aether registry attachment and cloud exposure
- Out of scope:
  - implementation changes
  - removing conduit access in this lane
  - unrelated spellbook/spell/runtime concerns

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked how conduit registration/notification works today before further cloud untangling.

## Steps / Checklist
- [ ] Read the root conjure path from `SpellbookCreationSystem` into `Conduit`.
- [ ] Read the Aether and ConduitCloud registration helpers.
- [ ] Read the lesser-to-normal upgrade path and compare it to root conjure.
- [ ] Summarize the current registration story and any drift.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed explanation of how conduits register with Aether today
- evidence-backed explanation of when dynamic cloud registration happens
- comparison between root conjure and lesser-to-normal upgrade behavior

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-19_investigate_conduit_registration_and_cloud_attachment_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_conduit_cloud.py tests/unit/melder/aether/conduit/test_conduit_dynamic.py`

## Risks / Rollback Notes
- Risk: stale historical assumptions from older flat-path conduit_cloud tickets.
  Rollback: anchor all conclusions to the live `aetheric_frame/conduit_cloud.py`
  source and current conduit constructor path.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
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
- DATETIME: 2026-05-19T22:15:15Z
  TYPE: PLAN
  CLAIM: This lane exists to answer one narrow question: how a conduit becomes
    known to Aether and when it becomes visible through the frame-local
    ConduitCloud, comparing root conjure and lesser-to-normal upgrade.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:141-165
  - src/melder/aether/conduit/conduit.py:715-729
  - src/melder/aether/conduit/conduit.py:1400-1412
  - src/melder/aether/aether.py:1199-1217
  - src/melder/aether/aetheric_frame/conduit_cloud.py:305-370
  IMPACT: The next cloud-removal cut should not proceed until the current
    registration/visibility story is explicit.
  NEXT: read the conjure and upgrade slices directly and compare where Aether
    registration stops and cloud exposure starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-19T22:15:15Z
  TYPE: FACT
  CLAIM: Root conjure and lesser-to-normal upgrade both register a normal
    conduit the same two-step way: first into the frame-owned root registry,
    then into the dynamic cloud registry only when the runtime is dynamic and
    the conduit has a name. Aether itself is not directly "notified" by a
    separate event; the injected frame-owned `ConduitCloud` writes root-conduit
    registration into the borrowed frame-owned stores during conduit setup.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:180-196
  - src/melder/aether/conduit/conduit.py:724-730
  - src/melder/aether/conduit/conduit.py:1052-1057
  - src/melder/aether/conduit/conduit.py:1409-1412
  - src/melder/aether/aetheric_frame/conduit_cloud.py:309-319
  - src/melder/aether/aetheric_frame/conduit_cloud.py:370-390
  - src/melder/aether/aether.py:1199-1244
  IMPACT: The feature was not lost. The registration path just moved behind the
    injected frame-owned cloud surface, so root-frame visibility and dynamic
    cloud visibility are separate steps.
  NEXT: answer the user with the explicit root-conjure vs lesser-to-normal
    story, then decide the next bounded removal cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
New active lane for conduit registration and cloud attachment. The immediate job
is to map how root conduits and upgraded lesser conduits enter Aether and
ConduitCloud today.
