

# Task: Deepen the Protocol contract check at bind (inherited members, annotation-only fields, callable arity)

## Metadata
- Task ID: TASK-2026-10-04-deepen-protocol-contract-check
- Story: STORY-2026-10-03-annotation-type-vs-category-matching
- Status: draft
- Owner: user
- Agent Name: unassigned
- Priority: p3
- Created: 2026-10-04T12:00:00Z
- Updated: 2026-10-04T12:00:00Z

## Objective
Since 0.2.8222 a Protocol spellframe is a contract the spell is checked against, but the check is the one that
existed before: the members declared DIRECTLY on the Protocol, presence and callability only
(`Bind._structurally_implements_protocol`). Decide with the owner, then implement, how much deeper the contract
goes: members inherited from parent Protocols, annotation-only fields (`name: str`), callable arity/signature
compatibility, and whether function spells (never checked today) are checked at all.

## Ticket Contract
- ENTRY_GATE: owner picks the depth (STRATEGY_DISCUSSION with the cost of each level on the bind path); routed
  on `attention_board.md`; a patch lane (binding pipeline) because it changes an admission contract.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/bind/bind.py` (`_structurally_implements_protocol` and its
  callers), its unit/component tests, the release note, the Binding Pipeline component entry.
- DEPENDENCIES: the 0.2.8222 kind rule (tickets/tasks/completed/2026-10-04_repair_annotation_kind_matching_task.md).
- EXIT_GATE: the chosen depth implemented red-to-green with a regression per level; no new cost on meld (bind only).
- FAILURE_ESCALATION: DECISION_REQUEST when a level would refuse a pattern the suites rely on.

## Scope Boundaries
- In scope: the bind-time structural check only.
- Out of scope: Phase 3 matching (settled at 0.2.8222); an explicit `implements=` argument (its own task).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: parked in the backlog at the owner's word (2026-10-03 19:00 local: follow-ups are separate tickets).

## Steps / Checklist
- [ ] STRATEGY_DISCUSSION: the four levels, what each refuses today that passes, and the bind-time cost.
- [ ] Owner DECISION on the depth.
- [ ] Patch lane, implementation, regressions, release note, component entry.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The deeper check and its regressions, or a recorded DECISION that the present depth is the contract.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY.

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/spellbook/bind -q -p no:cacheprovider`

## Risks / Rollback Notes
- A deeper check refuses bindings that pass today (Breaking if landed); each level needs a survey of the suites.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: delete_on_close

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
- DATETIME: 2026-10-04T12:00:00Z
  TYPE: FACT
  CLAIM: The present check covers the Protocol's direct public members (presence, callability) for class and
  existing-object spells; inherited Protocol members, annotation-only fields, signatures and function spells are
  outside it. Recorded on the reproduce task's STRATEGY_DISCUSSION from source.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-03_reproduce_annotation_category_collision_task.md:244-268
  IMPACT: the follow-up's starting point is known; nothing is owed until the owner picks it up.
  NEXT: STRATEGY_DISCUSSION when the owner opens the lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
STATE 2026-10-04T12:00:00Z: DRAFT, parked in the backlog. Opened as a follow-up of the 0.2.8222 kind rule.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
