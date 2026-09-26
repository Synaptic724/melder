

# Task: Review how conjure reports broken spells (SpellbookValidationError)

## Metadata
- Task ID: TASK-2026-09-26-review-conjure-validation-error-reporting
- Story: none (owner request after a CommandOps failure report)
- Status: blocked
- Owner: user
- Agent Name: melder_1
- Priority: p2
- Created: 2026-09-26T14:47:51Z
- Updated: 2026-09-26T14:51:33Z

## Objective
The owner pasted a CommandOps conjure failure (SpellbookValidationError for CodecPacket and ClassProfile) and is
"not 100% sure if this is good for people or if its reasonable". Review, from source, what a user sees when
conjure refuses broken spells - what triggers it, how the message is built, what it includes (warnings as well as
errors), and how actionable it is - and bring the owner an evidence-based assessment with recommendations.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("lets review this next").
- EXECUTION_BOUNDARY: Read src/ and tests, run probes on VM copies. No src edits before owner confirmation of a
  DECISION_REQUEST.
- DEPENDENCIES: Phase-4 validation strategies, SpellbookCreationSystem structural/resolution error paths,
  SpellbookValidationError, the conjure(validation_warnings=...) opt-in.
- EXIT_GATE: Assessment with evidence delivered; owner picks a direction (or none); any change implemented with
  tests, docs and release note.
- FAILURE_ESCALATION: DECISION_REQUEST for any message or behaviour change (public error text is user-facing).

## Scope Boundaries
- In scope: SpellbookValidationError construction and rendering, the conjure/meld paths that raise it, what
  counts as broken versus warning.
- Out of scope: which shapes Phase 1 injects (settled in the guard lane); CommandOps code.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner asked for this review (2026-09-26T14:47:51Z).
- from_state: in_progress
- to_state: blocked
- transition_reason: Assessment done; DECISION_REQUEST on the report shape open (2026-09-26T14:51:33Z).

## Steps / Checklist
- [x] Read SpellbookValidationError and every raise site in full.
- [x] Reproduce the owner's failure shape on current source and on 0.2.54 and capture the rendered text.
- [x] Assess against what a user needs (why it failed, which parameter, how to fix) and record findings.
- [x] Bring the owner recommendations (DECISION_REQUEST).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence and probes under artifacts/validation_error_reporting_20260926/; an assessment and options.

## Files / Paths Impacted
- (investigation only so far)

## Validation
- Not run.

## Risks / Rollback Notes
- Error text is public behaviour; tests and downstream users may match on it.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/validation_error_reporting_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: ticket closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - What conjure tells a user when spells are broken.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.

## Notes
- DATETIME: 2026-09-26T14:49:51Z
  TYPE: FACT
  CLAIM: Source read in full. (a) The owner's failure is already fixed: every Melder frame in the pasted trace
    matches the melder 0.2.54 wheel line for line, and the UNSUPPORTED_COLLECTION_SHAPE container branch it hit is
    gone from HEAD (a67cd3b49); CommandOps runs an old install. (b) A spell is "broken" only when its Phase-4 result
    has an error-severity issue; warnings never break it. (c) SpellbookValidationError renders every Phase-4 issue
    of each broken spell in strategy order - warnings and errors interleaved, no counts, errors not first - each
    followed by a repr of its details dict that repeats the message; 64-hex spell ids appear twice per spell; the
    text uses pipeline vocabulary ("Phase 4 issues", "Phase 6 diagnostics") and always prints "Phase 6
    diagnostics: (none recorded)" when there are none. In the owner's paste, 8 REQUIRED_HOLE warnings precede the 2
    errors that actually broke CodecPacket. (d) The conjure-time resolution gate raises with the spells its ERROR
    diagnostics name, or, when none carry a spell id (cycles, coverage), with EVERY spell in the pool. (e) The
    local-rerun gate cleans the target's phase artifacts before raising; whether its Phase-6 diagnostics survive
    into the message is UNKNOWN. (f) scope_ordering_violation messages name spells by id, not name.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:79-287
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:147-147
  - src/melder/aether/spellbook/spellbook_creation_system.py:440-497
  - src/melder/aether/spellbook/spellbook_creation_system.py:1522-1536
  - src/melder/aether/spellbook/spellbook_creation_system.py:1897-1931
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:1-142
  - context_compass/artifacts/annotation_shape_guard_20260926/results/owner_trace_vs_wheel.txt:1-14
  IMPACT: The review is about the report's shape, not the guard. Candidates: errors first with counts, warnings
    summarised, details dropped when they repeat the message, names over ids, user vocabulary over phase numbers.
  NEXT: Probe the rendered text on current source for four shapes (owner's classes, a real Phase-4 error, a cycle
    among unrelated spells, a scope-ordering violation) and on 0.2.54 for the owner's classes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T14:51:33Z
  TYPE: MEASURE
  CLAIM: Rendered text, one fresh process per case (3.14.7t, -X gil=0; current source synced from the worktree vs the
    0.2.54 wheel; the renderer file is identical in both). Owner's shapes: current source conjures; 0.2.54 raises a
    46-line, 6.7 KB message with 16 warnings, 3 errors and 19 details lines. Two-spell cycle: both spells named
    (the two unrelated spells are not), but four errors for one cycle (CIRCULAR_DEPENDENCY and
    BINDING_RESOLUTION_CYCLE, once per spell), cycle paths written as 64-hex ids with the start id repeated
    twice at the end, and frame=None for the default frame. Scope violation (unique Holder on a
    unique_per_spell_space Leaf): SpellbookValidationError names Holder as broken and gives NO reason - Phase 4 and
    Phase 6 both "(none recorded)"; why the scope_ordering_violation diagnostic does not reach the message is
    UNKNOWN. Only tests/unit/.../test_spellbook_validation_error.py matches on the message text in this repo.
  EVIDENCE:
  - context_compass/artifacts/validation_error_reporting_20260926/results/rendered_owner_0254.txt:1-46
  - context_compass/artifacts/validation_error_reporting_20260926/results/rendered_cycle_cur.txt:1-16
  - context_compass/artifacts/validation_error_reporting_20260926/results/rendered_scope_cur.txt:1-8
  - context_compass/artifacts/validation_error_reporting_20260926/probes/probe_error_rendering.py:1-104
  - tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py:160-170
  IMPACT: The report buries the cause in noise when there are many caller inputs, and in one real case gives no
    cause at all. Changing the text is low-risk inside Melder (one unit test file); downstream matching is UNKNOWN.
  NEXT: Put the assessment and options to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T14:51:33Z
  TYPE: DECISION_REQUEST
  CLAIM: Proposed report shape (same exception type and broken_spells attribute; text only, plus one bug fix):
    (1) errors only, grouped per spell, errors first with a count line; (2) warnings not listed in a failure -
    one line "N warnings not shown; conjure(validation_warnings=True) lists them" (they stay on the spell's
    result for tooling); (3) no details-repr lines; (4) names instead of ids (spell name, and frame only when not
    the default), cycle paths as names, one cycle reported once, the doubled start node removed; (5) plain words
    instead of phase numbers, empty sections omitted; (6) the scope-violation case must say why (bug: reason lost).
    Alternatives: only (6) plus warnings removed (smallest), or leave the text and document it.
  EVIDENCE:
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:79-287
  - context_compass/artifacts/validation_error_reporting_20260926/results/rendered_scope_cur.txt:1-8
  IMPACT: Implementation waits for the owner's choice; (6) needs its cause traced first.
  NEXT: Discuss with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened 2026-09-26T14:47:51Z on owner direction. Investigation first; no src edits until the owner approves a direction.
Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
