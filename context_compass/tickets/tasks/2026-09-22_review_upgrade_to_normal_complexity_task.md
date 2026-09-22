# Task: Review upgrade_to_normal ownership, imports, and failure handling

## Metadata
- Task ID: TASK-2026-09-22-review-upgrade-to-normal-complexity
- Story: none
- Status: in_progress
- Owner: codex
- Agent Name: updater_1
- Priority: p1
- Created: 2026-09-22T22:54:06Z
- Updated: 2026-09-22T22:54:06Z

## Objective
Review the complete lesser-to-normal graduation change and explain which imports,
references, validation, and rollback mechanisms serve real contracts and which can simplify.
The owner specifically questions Spellbook/SpellbookConfiguration references and rollback complexity.

## Context
The graduation ownership/configuration work is completed; this is an owner-requested source review.
The working tree contains concurrent changes. Existing packaging holds and other agents' work remain.
MRP alignment: preserve independent root ownership with the smallest correct lifecycle implementation.

## Ticket Contract
- ENTRY_GATE: Certified updater_1; this ticket has an active attention-board route.
- EXECUTION_BOUNDARY: Review graduation source, direct lifecycle dependencies, tests, and prior contracts.
  Writes are limited to this review ticket and the shared routing/check-in entries for updater_1.
- DEPENDENCIES: Completed graduated-conduit ownership/configuration epic and its implementation task.
- EXIT_GATE: Source-backed findings, concrete simplification recommendations, and validation limits delivered.
- FAILURE_ESCALATION: Record unresolved contract ambiguity or inaccessible source before dependent conclusions.

## Scope Boundaries
- In scope: Conduit.upgrade_to_normal; Spellbook existing-conduit conjure/attachment; ward conversion;
  Meld/SpellSpace rebinding; configuration and hooks; directly relevant tests and history.
- Out of scope: Runtime edits, packaged asset generation, unrelated refactors, and other agents' lanes.

## Requirements and Acceptance Criteria
- Explain each questioned runtime import versus typing-only dependency.
- Establish which references own resources and which are borrowed or temporary.
- Trace mutation ordering, failure sites, rollback coverage, and concurrency admission.
- Review test intent for graduation behavior and distinguish excessive scaffolding from necessary coverage.
- Provide actionable findings with source ranges and a simpler recommended design.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner explicitly requested review after onboarding and certification.

## Steps / Checklist
- [ ] Read supplied excerpt and completed graduation contracts; locate all affected changes.
- [ ] Trace actual source and callers for imports, ownership, and rollback.
- [ ] Inspect graduation tests and relevant validation evidence.
- [ ] Record findings and deliver review with prioritized recommendations.

## Deliverables
- Evidence-backed review in ticket notes and owner-facing response.

## Files / Paths Impacted
- context_compass/tickets/tasks/2026-09-22_review_upgrade_to_normal_complexity_task.md
- context_compass/attention_board.md
- context_compass/mailbox_board.md

## Validation
- Not run. Initial scope is source review; run targeted reproduction only if needed to settle a finding.

## Risks / Mitigations
- Documentation may lag source: use verified index slices for navigation and source for behavior claims.
- Concurrent changes: preserve other agents' modifications and record the reviewed source boundaries.

## Applicable Anti-Patterns
- [ ] No behavior claim based only on documentation or search hits.
- [ ] No runtime edits from this review request.
- [ ] No closure without owner acceptance.

## Done Checklist
- [ ] Review completed and recommendations delivered.
- [ ] Findings carry source ranges and one concrete NEXT step.
- [ ] Validation status recorded truthfully.
- [ ] Acceptance criteria reviewed with owner.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: graduation imports, ownership, failure handling, simplification
- IF_UNKNOWN: none

## Noting Behavior
- Append findings after each complete source/call-path read, before the next investigation tranche.
- Evidence covers the described logic; unknown behavior stays UNKNOWN.

## Notes
- DATETIME: 2026-09-22T22:54:06Z
  TYPE: PLAN
  CLAIM: Review the graduation path against its independent-Book contract and the owner's complexity concerns.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:679-692
  - context_compass/system_docs/src_architecture.md:847-859
  IMPACT: The review must explain necessary ownership transitions without assuming existing rollback is justified.
  NEXT: Read the supplied excerpt and completed implementation task, then descend to indexed components/source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-22T22:56:30Z
  TYPE: FACT
  CLAIM: The completed implementation record requires a new empty independent Book and a separate
    private Book-owned existing-conduit conjure route. It records rollback only before attachment,
    with normal-root cleanup responsibility after attachment. These are recorded design decisions;
    their actual source behavior remains to be reviewed.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-22_implement_graduation_configuration_and_hook_ownership_task.md:1-494
  IMPACT: Removing independent Book ownership would restore the original defect. Import checks and
    rollback implementation should be judged separately from that ownership requirement.
  NEXT: Read indexed graduation components and graph, then the current source and complete diff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T22:58:14Z
  TYPE: FACT
  CLAIM: Current upgrade adds a local Spellbook import to construct a new Book. SpellbookConfiguration
    was already imported for constructor isinstance validation; upgrade now adds another isinstance
    check. Ordinary Book selection already handles omitted/default, supplied-frame and shared identity
    configuration policy. Upgrade and private conjure both drain the same gate; an extra parameter
    carries its original enabled state across those two owners. Restoration reaches into Ward state.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:47-58
  - src/melder/aether/conduit/conduit.py:2087-2304
  - src/melder/aether/spellbook/spellbook.py:5582-5707
  - src/melder/aether/spellbook/spellbook.py:6635-6858
  IMPACT: Runtime type policing is separable from configuration ownership. The existing factory shares
    the parent's configuration and cannot replace new construction unchanged. Failure handling spans
    two layers and restores topology because promotion precedes normal Book preparation/compilation.
  NEXT: Trace concrete pre/post-attachment failure points, ownership rewiring and focused regression coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Certified updater_1 is reviewing graduation complexity at the owner's request. No runtime edits authorized
by this review scope. Begin with the pasted excerpt and completed implementation contracts, then trace source.
