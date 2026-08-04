# Task: Investigate conduit scan phase-4 validation gap

## Metadata
- Task ID: TASK-2026-07-01-conduit-scan-phase4-validation-gap
- Story: none
- Status: closed (orphan sweep 2026-07-11, melder_0, owner-directed:
  codex_0 does not exist; the investigated symptom is MOOT-BY-GREEN -
  the two failing scan tests ride the full tree and the owner's
  repeated 9702-green runs since prove they pass; the line-level fix
  history is UNKNOWN and stays that way - if the symptom ever returns
  it is new work with fresh evidence)
- Owner: codex
- Agent Name: codex_0 (closed by melder_0)
- Priority: p1
- Created: 2026-07-01T18:23:10Z
- Updated: 2026-07-01T18:23:10Z

## Objective
Define the root cause for why `conduit.scan(...)` after `Spellbook.conjure(...)`
returns bound spell ids but leaves `Spell.validation_result_phase4` unset for
the scanned spells.

## Ticket Contract
- ENTRY_GATE: `attention_board.md` routes this lane to the task and the initial
  failing-test evidence is recorded in `## Notes` before deeper tracing.
- EXECUTION_BOUNDARY: `tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`,
  `src/melder/aether/conduit/conduit.py`,
  `src/melder/aether/spellbook/spellbook.py`,
  `src/melder/aether/spellbook/bind/scan.py`,
  `src/melder/aether/spellbook/bind/bind.py`,
  phase-4-to-phase-7 compiler/validation surfaces, and directly related
  `ConduitWard` or change-control helpers only if the trace proves they are on
  the causal path.
- DEPENDENCIES: prior synaptic onboarding readset already completed, including
  `src_architecture.md`, `src_components.md`, and
  `readable_src_graph.json`.
- EXIT_GATE: root cause is evidenced with concrete file/line references and the
  minimal fix boundary is documented; if code changes later become necessary,
  validation status is recorded truthfully.
- FAILURE_ESCALATION: raise `DECISION_REQUEST`, `CONFLICT`, or `BLOCKER` before
  widening beyond the listed execution boundary or if repo state prevents a
  trustworthy trace.

## Scope Boundaries
- In scope:
  - post-conjure conduit-side scan/bind behavior
  - `Spellbook` init/bind/scan flow
  - compiler phases 4-7 at the high level
  - spell validation publication onto `Spell` / compiler artifacts
  - conduit link / `ConduitWard` understanding only where needed for causality
- Out of scope:
  - unrelated spell index structural rewrites
  - broader doc rewrites
  - implementation outside the minimal causal fix boundary unless evidence
    makes it necessary

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user requested investigation, certification is present,
  and the initial failing test has been captured as the active work item.

## Steps / Checklist
- [ ] Read the failing integration test and confirm the exact contract it
      expects from `conduit.scan(...)`.
- [ ] Trace `Conduit.scan(...)` into `Spellbook` / `Bind` / phase-4-to-phase-7
      compiler entrypoints and note where validation state should be published.
- [ ] Compare post-conjure bind/scan behavior against the normal conjure path.
- [ ] Identify the minimal causal gap and document the safe fix boundary.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Root-cause explanation for the missing phase-4 validation result.
- Minimal affected-file boundary for a fix.

## Files / Paths Impacted
- `tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/spellbook/bind/scan.py`
- `src/melder/aether/spellbook/bind/bind.py`
- phase-4-to-phase-7 compiler/validation files as the trace requires

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Risks / Rollback Notes
- The surrounding repo has multiple active lanes, so investigation should stay
  tightly scoped to the failing scan/bind path.
- Any eventual fix must avoid accidental behavior changes in normal conjure,
  link, or spell-index flows.

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
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - phase-4-to-phase-7 scan/bind validation propagation
  - `Spellbook` init / bind / scan / post-conjure behavior
  - `ConduitWard` and linking only if the trace requires it
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-01T18:23:10Z
  TYPE: FACT
  CLAIM: The failing integration test proves the post-conjure conduit scan path
    binds three objects into the spellbook and returns spell ids, but the first
    retrieved spell still has `validation_result_phase4 is None`.
  EVIDENCE:
  - `tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py:159-177`
  IMPACT: The scan/bind-after-conjure path is leaving the spell in a different
    validation-publication state than the test contract expects, so the trace
    must compare post-conjure scan/bind against the normal conjure/validation
    pipeline.
  NEXT: Read the failing test body and trace `Conduit.scan(...)` inward to the
    bind and phase-4-to-phase-7 compiler surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Active investigation lane for the failing post-conjure `conduit.scan(...)`
integration test. Current evidence shows spell binding succeeds but the scanned
spell does not expose a phase-4 validation result afterward. Next step is an
inbound trace from the test to `Conduit.scan`, `Spellbook`, `Bind`, and the
compiler/validation publication path.

- DATETIME: 2026-07-01T18:23:10Z
  TYPE: FACT
  CLAIM: The post-conjure scan path nests `Spellbook.bind(...)` calls inside one outer bind transaction, but each nested `Spellbook.begin_transaction(ChangeTransactionType.BIND)` unconditionally calls `_prepare_bind_transaction_state()`, which clears `_pending_structural_spells` before the current spell is restaged. The commit-time structural validator consumes only staged `binding_keys` and then runs `_run_post_conjure_structural_phases(...)` for those keys, so the outer scan commit can retain only the most recently staged scan bind target.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:3511-3540`
  - `src/melder/aether/spellbook/spellbook.py:3723-3742`
  - `src/melder/aether/spellbook/spellbook.py:3794-3863`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:737-752`
  - `tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py:169-177`
  IMPACT: This explains how `conduit.scan(...)` can return three spell ids while earlier scanned spells still have `validation_result_phase4 is None`: the post-conjure structural validator is driven by staged bind keys at commit, and nested bind-state resets can narrow that staged set to the last scanned spell.
  NEXT: Verify the nested bind/session behavior end-to-end against mediator nesting and inspect whether an existing test already codifies the intended accumulation semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-01T18:23:10Z
  TYPE: DECISION
  CLAIM: The minimal safe fix is in `Spellbook.begin_transaction(ChangeTransactionType.BIND)`: only the outermost bind window should call `_prepare_bind_transaction_state()`. Nested `Spellbook.bind(...)` calls inside an already-active scan/bind session must preserve earlier staged spells so the commit-time structural validator can validate the full scanned set.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:3531-3546`
  - `src/melder/aether/spellbook/spellbook.py:3794-3863`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:737-752`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1100-1124`
  IMPACT: This keeps `conduit.scan(...)` from collapsing the staged bind-key set down to the last nested bind call, which is the direct cause of earlier scanned spells missing phase-4 validation publication.
  NEXT: Validate the fix with the existing failing integration test and the new focused unit regression once unrelated collection blockers are cleared.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-01T18:23:10Z
  TYPE: MEASURE
  CLAIM: `py_compile` succeeded for the changed code and test, but targeted pytest validation is currently blocked during collection by an unrelated import-time error in `src/melder/nexus/frame_descriptor/frame_descriptor.py`: `NameError: AethericFrame is not defined` on the `frame_handle` annotation. This stops both the focused unit and integration scan-bind tests before execution.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:3531-3546`
  - `tests/unit/melder/spellbook/test_scan_bind.py:276-309`
  - `src/melder/nexus/frame_descriptor/frame_descriptor.py:153-153`
  IMPACT: The scan-bind fix compiles, but I cannot truthfully claim the targeted pytest tests passed in this environment because collection never reached them.
  NEXT: Report the unrelated collection blocker to the user and keep validation status explicit as blocked-at-collection rather than passed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
