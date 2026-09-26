

# Story: Verify native writer coordination and override contract before implementation

- Completed: 2026-09-26T00:15:00Z
- Closure Basis: owner directed turn-in after accepting the deadlock fix.
- Summary: Store/Spell deadlock confirmed and fixed with per-slot build guards (next release, 0.2.53); override
  contract items 1-8 verified with a regression matrix; items 4 (a) and 5 (c) chosen; open items carried.

## Metadata
- Story ID: STORY-2026-09-25-verify-override-writer-and-contract
- Epic: EPIC-2026-09-24-override-execution-performance
- Status: done
- Owner: user
- Agent Name: melder_0, melder_1
- Lead Agent: melder_0
- Priority: p1
- Created: 2026-09-25T20:52:31Z
- Updated: 2026-09-26T00:15:00Z

## User Narrative
As the Melder owner, I want the joint alpha proposal's native-lock claim and behavior contract verified
against current source, so that the implementation decision rests on evidence rather than prototypes.

## Value / MRP Alignment
The proposal reports a lock-order inversion in current production: a per-conduit or lineage root holds
its store lock while waiting for a unique child's Spell lock, and purge takes the two in the opposite
order. If real, that is a correctness defect independent of the optimization. MRP: settle correctness
and contracts before selecting the construction-graph implementation.

## Ticket Contract
- ENTRY_GATE: Owner approval 2026-09-25; melder_0 and melder_1 certified; both task rows routed.
- EXECUTION_BOUNDARY: Read src/, tests/ and existing artifacts. Write only these tickets and task-owned
  artifacts. No src/, tests/, canonical system_docs, version or build-asset edits.
- DEPENDENCIES: joint_alpha_proposal.md, native_runtime_boundary.md, compact_structure_proposal.md;
  epic owners updater_0 and updater_1 notified through the mailbox.
- EXIT_GATE: Both tasks in review with evidence-backed verdicts; owner reviews writer options and matrix.
- FAILURE_ESCALATION: CONFLICT when source contradicts the proposal; DECISION_REQUEST for policy items
  (contract item 4, equality contract, claim lifetime/fairness); BLOCKER if CPython 3.14 is required
  for a probe and cannot be obtained.

## Requirements (Functional)
- Confirm or refute the store/unique-Spell inversion from source read in full, cited path:start-end.
- Enumerate which existence/scope pairs can form the cycle; leave unqualified pairs UNKNOWN.
- Draft writer-coordination options (narrow ordering fix vs full claim protocol) with tradeoffs.
- Verify behavior-contract items 1-8 against current compiler and meld source; record current vs proposed.
- Produce the regression matrix (proposal implementation step 1) as a test plan, not test code.

## Requirements (Non-Functional)
- Unknown-first: no behavior claim from documents or search hits alone.
- No performance claim; none is expected from this story.

## Scope Boundaries
- In scope: Creations, Meld/ConduitMeld/SpellSpaceMeld purge doors, the creation runtime door compiler,
  generalized creation compilers, compiler phases carrying override sockets, existing artifacts.
- Out of scope: Production edits, compact-graph implementation, cache format, hook standardization,
  the Mojo/compiler-IR epic and the existing-object ownership redesign.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved the melder-pair verification lane with melder_0 leading, 2026-09-25.
- from_state: in_progress
- to_state: done
- transition_reason: All four tasks done; owner directed the contract task and story turn-in, 2026-09-26T00:15:00Z.

## Dependencies / Related Work
- tickets/epics/2026-09-24_override_execution_performance_epic.md
- tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md (updater_0)
- tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md (updater_1)
- artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-09-25-verify-native-writer-lock-order (melder_0, done)
  tickets/tasks/completed/2026-09-25_verify_native_writer_lock_order_task.md
- [x] Task: TASK-2026-09-25-verify-override-behavior-contract (melder_1, done)
  tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md
- [x] Task: TASK-2026-09-25-add-meld-lock-order-deadlock-regression-tests (melder_0, done)
  tickets/tasks/completed/2026-09-25_add_meld_lock_order_deadlock_regression_tests_task.md
- [x] Task: TASK-2026-09-25-implement-creation-slot-build-guards (melder_0, done)
  tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery.

## Acceptance Criteria
- The inversion is FACT or refuted, with source ranges covering both complete lock paths.
- The writer-options artifact states the contract each option satisfies and what it leaves UNKNOWN.
- Each contract item 1-8 has current-behavior evidence and a proposed regression case.
- Policy choices reach the owner as explicit DECISION_REQUEST notes.

## Validation / Test Plan
- Source reads are the primary evidence. Probe re-runs need CPython 3.14; otherwise "Not run."

## UX / API / Data Notes
- No public API change is proposed by this story.

## Risks / Mitigations
- Proposal ranges may have drifted since 2026-09-24: re-read source and record drift as a finding.
- The melder_0 shell has Python 3.10; the project floor is 3.14: never run probes on 3.10.
- Concurrent updater edits: the melder pair writes only its own tickets and artifacts.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Contract item 4: inactive-path policy for rules below a supplied or reused constructor (owner).
- Equality contract for arbitrary objects at equal-rank active inputs (UNKNOWN).
- Claim-record lifetime, retirement, reentrancy and fairness (UNKNOWN).

## Decision Log
- 2026-09-25: Owner approved this verification lane; melder_0 leads, melder_1 partners. Recorded
  assumption: the melder pair works alongside updater_0/updater_1 on their epic, not as a takeover.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: Task-owned; see each task.
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner-directed disposition at story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Native writer lock order; override behavior contract.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-25T20:52:31Z
  TYPE: PLAN
  CLAIM: Split verification of joint_alpha_proposal.md: melder_0 verifies the store/unique-Spell
    inversion and drafts writer options; melder_1 verifies contract items 1-8 and drafts the
    regression matrix. Proposal claims stay UNKNOWN until each task cites source.
  EVIDENCE:
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md:61-106
  - artifacts/override_structural_discovery_20260924/native_runtime_boundary.md:32-52
  IMPACT: Separates a possible live correctness defect from the optimization decision.
  NEXT: Both tasks begin source reads; melder_0 starts with creations.py around lines 320-579.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T20:54:45Z
  TYPE: RISK
  CLAIM: Multi-file board writes are not atomic. A mailbox write aborted on a changed-content guard
    after the matching attention-board alerts were already written, leaving alerts without messages
    for about 20 seconds until repaired. Guarded read-modify-write worked; write order did not.
    Correction: the protocol already orders message first, alert second; melder_0 deviated from it.
  EVIDENCE: agent_onboarding/default/general/skills/mailbox_protocol.md:45-59
  IMPACT: A peer polling in that window could see an alert with no message and misread the protocol.
  NEXT: Post mailbox messages first and alert lines second in every future send.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-25T21:05:52Z
  TYPE: FACT
  CLAIM: Both tasks reached their first deliverable. melder_1 (M1-5): items 1-8 verified; current
    diverges on 1, 4, 5; CONFLICT on item 7 wording; two DECISION_REQUESTs; task in review.
    melder_0: store/unique-Spell cycle confirmed from source in both lanes and reproduced on 3.14.7
    for normal-root per-conduit/lineage; a meld-only variant (row 4) is source-derived, not reproduced.
  EVIDENCE:
  - tickets/tasks/2026-09-25_verify_override_behavior_contract_task.md
  - tickets/tasks/2026-09-25_verify_native_writer_lock_order_task.md
  - artifacts/melder_writer_lock_order_20260925/writer_options.md:1-113
  IMPACT: The owner decision set is now concrete: writer-fix sequencing plus melder_1's policy items.
  NEXT: Lead review of melder_1's notes and regression matrix, then one consolidated owner report.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T22:49:31Z
  TYPE: DECISION
  CLAIM: Owner expanded this story from verification to implementation of the deadlock fix (Idea A,
    per-slot build guards, store-side, every store). The story EXECUTION_BOUNDARY "no src/ or tests/
    edits" no longer holds for the new implementation task; the verification tasks keep it. The
    implementation task declares its own file list and patch docs.
  EVIDENCE:
  - tickets/tasks/2026-09-25_implement_creation_slot_build_guards_task.md
  - artifacts/melder_writer_lock_order_20260925/writer_options.md:151-213
  IMPACT: src/ and tests/ edits are in scope only through that task and its patch docs.
  NEXT: Implementation task proceeds; story closes after owner review of all four tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T23:28:41Z
  TYPE: FACT
  CLAIM: Story reached its fix: per-slot build guards implemented, 8 lock-order shapes pass on 3.14t and GIL,
    suites show no attributable regression, cold slotted builds cost ~4-7% more with trivial constructors
    (warm 0%). All four tasks are in review; melder_1's item-4/item-5 decision requests remain open.
  EVIDENCE:
  - tickets/tasks/2026-09-25_implement_creation_slot_build_guards_task.md
  - tickets/tasks/2026-09-25_add_meld_lock_order_deadlock_regression_tests_task.md
  - tickets/tasks/2026-09-25_verify_override_behavior_contract_task.md
  IMPACT: The joint-alpha override work can build on leaf store locks and slot guards.
  NEXT: Owner review of the implementation, then story closure walkthrough.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T23:47:39Z
  TYPE: FACT
  CLAIM: Owner accepted the deadlock fix; melder_0's three tasks closed and moved to completed (canonical docs,
    graph and next-release note updated, patch docs archived). The story stays in_progress only for melder_1's
    override-contract task, which waits on owner decisions for contract items 4 and 5 (and the item-7 wording).
  EVIDENCE:
  - tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md
  - tickets/tasks/2026-09-25_verify_override_behavior_contract_task.md
  IMPACT: Story closure needs the item-4/item-5 decisions or an owner call to close the contract task as-is.
  NEXT: Owner decides items 4 and 5 (or closes the contract task), then the story closure walkthrough.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:15:00Z
  TYPE: FACT
  CLAIM: Story closed on owner direction. All four tasks are done: the lock-order inversion is FACT and fixed by
    per-slot build guards with 12 regression cases; contract items 1-8 are source-verified with a regression
    matrix, item 4 (a) and item 5 (c) recorded as implementation inputs. Carried to the override implementation
    lane: item-7 per-family error wording, the R5d probe, nested unresolved-contract validation and R7c.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-25_verify_native_writer_lock_order_task.md
  - tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md
  - tickets/tasks/completed/2026-09-25_add_meld_lock_order_deadlock_regression_tests_task.md
  - tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md
  IMPACT: The override epic's joint alpha work starts from leaf store locks, slot guards and a decided matrix.
  NEXT: none in this story; the owner directs the override implementation next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Opened 2026-09-25 by melder_0 on owner approval. Two read-only verification tasks run in parallel.
No production code is in scope. Resume from the two task tickets' latest NEXT entries.
Closed 2026-09-26T00:15:00Z: the owner expanded the story to the deadlock fix (implemented) and directed turn-in. Open
override items are listed in the final note and belong to the override implementation lane.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
