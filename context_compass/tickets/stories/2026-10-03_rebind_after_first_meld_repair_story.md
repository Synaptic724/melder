

# Story: Rebind after first meld - reproduce on current source, locate the readiness transition, repair it

## Metadata
- Story ID: STORY-2026-10-03-rebind-after-first-meld-repair
- Epic: EPIC-2026-10-03-rebind_after_first_meld
- Status: in_progress
- Owner: user
- Agent Name: fable_1
- Priority: p1
- Created: 2026-10-03T19:13:22Z
- Updated: 2026-10-03T21:08:00Z

## User Narrative
As a Melder host that registers and replaces definitions at runtime (MelderOps Actions), I want
`bind -> meld -> cleanup_spell -> bind the same class at the same address -> meld` to return a new
product, so that replacing a definition needs no private cache edits or extra conjure from the caller.

## Value / MRP Alignment
Dynamic late registration and removal are ordinary lifecycle operations; a replacement that only works
when the first definition was never used is a trap in the core. The fix must keep the original product
alive until its scope cleans it and keep the CreationContext guard that caught this.

## Ticket Contract
- ENTRY_GATE: the epic's evidence read (probe, finding, retest receipt, fixture); this story and its
  task routed on `attention_board.md`.
- EXECUTION_BOUNDARY: the bind/cleanup_spell/rebind/meld path - `spellbook.py` (bind, cleanup_spell,
  the structural/resolution reruns), `spellbook_creation_system.py` (target passes, flags),
  `spell.py` (artifacts, flags, context access), `meld.py` (the deferred lane and readiness), the
  creation-context factory/builder, `spell_system_states` - plus their tests and the system docs the
  change touches. Reads anywhere; edits only after a patch lane exists (work package B is
  system-impacting: lifecycle behaviour).
- DEPENDENCIES: TASK-2026-10-03-reproduce-rebind-after-first-meld; the epic's artifacts; fable_0's open
  S8 change set (site_plan_lowering.py, hydrators) stays theirs - no edit there.
- EXIT_GATE: the four-case probe passes on current source with a Melder-only fixture (the two controls
  stay green), the cause is a FACT with source evidence, the repair lands red-to-green with the guard
  and old-product lifetime intact, and the epic's work package C (consumer acceptance on the delivered
  wheel) is handed to the owner.
- FAILURE_ESCALATION: DECISION_REQUEST before any change to public API shape or to what
  `cleanup_spell` promises; CONFLICT if the cause lives in a file another live agent holds.

## Requirements (Functional)
- Second ordinary meld after removal + same-address rebind returns a new product (override honoured).
- The original product is untouched by definition removal; its scope cleans it later.
- Peer contract withdrawal/re-grant keep working around the replacement (linked variants).

## Requirements (Non-Functional)
- No change to warm-path cost; no new guard on the meld hot path without evidence.
- Regressions: the four-case matrix in the canonical Melder fixture plus the specific transition.

## Scope Boundaries
- In scope: the operation prefix above, its regressions, system-doc and release-note entries.
- Out of scope: MelderOps changes; purge semantics; removing the CreationContext guard; S8 lane files.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner directed the investigation in chat on 2026-10-03 ("this is important to fix");
  evidence handoff exists (EPIC-2026-10-03-rebind_after_first_meld).

## Dependencies / Related Work
- tickets/epics/2026-10-03_rebind_after_first_meld_epic.md
- artifacts/2026-10-03_rebind_after_first_meld/ (probe, finding, receipts, fixture snapshot)
- tickets/epics/completed/2026-09-30_injected_dependency_direct_resolution_epic.md (same message,
  different operation prefix; not reopened)

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-10-03-reproduce-rebind-after-first-meld - port the probe to a Melder-only fixture,
      run it on current source (working tree and HEAD), locate the transition that leaves the
      replacement without creation codegen. (review: cause FACT, prototype MEASURE, 2026-10-03)
      tickets/tasks/completed/2026-10-03_reproduce_rebind_after_first_meld_task.md
- [x] Task: TASK-2026-10-03-repair-rebind-after-first-meld - patch lane + repair + regressions + notch +
      note + rebuild. (review: landed at 0.2.8219, 2026-10-03)
      tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Probe matrix 4/4 green on the repaired source; the unchanged Actions case is the owner's work package C.
- Cause recorded as FACT with `path:start-end` into source, not into documents.

## Validation / Test Plan
- The ported probe (unit/component tier, Melder-only fixture) red on current source, green after.
- Affected suites: tests/unit and tests/integration for spellbook, meld, creation_context.

## UX / API / Data Notes
- None expected; if a public verb must change, DECISION_REQUEST first.

## Risks / Mitigations
- fable_0's S8 edits are in the working tree: reproduce on HEAD too, so the result is not confounded.
- Same exception text as the closed injected-dependency epic: classify by operation prefix (done in the
  epic); do not reopen it.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No implementation before the patch lane exists (patch_framework_gating.md).

## Open Questions
- Which transition clears or never produces `spell_codegen_creation` for the replacement spell?
  ANSWERED 2026-10-03: none clears it - it is never produced, because the stale per-conduit `valid`
  verdict under the same content-stable id skips phases 5-11 (reproduce task note 19:32:35Z).
- M7: should a unique_per_conduit replacement inherit the surviving old product's slot (today, with the
  repair) or should definition removal retire that slot? RULED (a) by the owner 2026-10-03: the surviving
  product is deliberately left alive in its slot; pinned by a regression and documented.

## Decision Log
- 2026-10-03T19:13:22Z (owner, chat): investigate and fix; fable_1 takes the lane.
- 2026-10-03 14:31 local (owner, chat): the proposed two-file DevOps repair is approved.
- 2026-10-03 14:42 local (owner, chat): M7 = (a), the surviving product is deliberately left alive.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/rebind_after_first_meld_20261003/ (fable_1's reproduction runs and probes; created by the task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: kept with the epic's evidence at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - rebind after first meld; cleanup_spell; creation context readiness
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-10-03T19:13:22Z
  TYPE: PLAN
  CLAIM: Work package A first: port the four-case probe to Melder's own reset fixture
  (`Aether._reset_singleton_for_tests()` + rebinding `Spellbook._aether`/`Conduit._aether`, as
  tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py does), run it on the
  working tree and on HEAD 4ddf7530f in the VM on 3.14.7t, then trace the failing path from
  `CreationContextBuilder.build` backwards to the transition.
  EVIDENCE:
  - artifacts/2026-10-03_rebind_after_first_meld/test_native_rebind_probe.py:26-63
  - artifacts/2026-10-03_rebind_after_first_meld/rebind_retest_2026-10-03.json:1-30
  - tests/integration/melder/aether/conduit/test_human_spell_name_resolution.py:12-22
  IMPACT: establishes current-build behaviour before any source edit (the epic's first gate).
  NEXT: open the reproduction task and run the probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-03T20:14:00Z
  TYPE: DECISION
  CLAIM: Cross-task synthesis. The reproduction task found and proved the cause (per-conduit verdicts keyed by
  the content-stable id survive `unregister_index`; the same-id rebind is born structurally valid, so the
  meld-time structural gate never re-gates them) and prototyped the repair in the DevOps control plane:
  retire the id's conduit verdicts on `unregister_index` and on `register_index`. Measured in the VM mirror:
  probe 4/4, revalidation matrix 7/7 (M1/M3/M4/M5 red before), four test tiers green. The repair task is
  open with patch lane rebind_after_first_meld_2026_10_03 (three docs, indexed) and waits on the owner's
  confirmation of the exact edit; M7 (slotted-existence replacement meets the surviving product) is an owner
  ruling that does not block the landing.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-03_reproduce_rebind_after_first_meld_task.md:146-262
  - tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md:1-60
  - system_docs/patches/active/rebind_after_first_meld_2026_10_03/architecture_patch.md:1-74
  IMPACT: work package B is designed and evidenced; C (consumer acceptance) follows the landing.
  NEXT: owner confirms the edit; the repair task lands red-to-green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T21:00:00Z
  TYPE: DECISION
  CLAIM: Work package B is landed at 0.2.8219 (repair task in review): the two DevOps verbs and their call sites,
  37 regressions, four tiers green, release note, system docs, graph, assets and bundles. The EXIT_GATE's last
  clause - work package C, the unchanged five-case selection on the delivered build in priv_commandops - is the
  owner's; the epic closes on it. Both tasks are in review for turn-in.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md:208-254
  - artifacts/rebind_after_first_meld_20261003/fix/landing_results.txt:1-25
  IMPACT: the story's remaining work is acceptance, not engineering.
  NEXT: owner turns in both tasks and runs C; the story closes with the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-03T21:08:00Z
  TYPE: DECISION
  CLAIM: Both tasks turned in by owner directive (15:05 local) and moved to completed/; the patch lane is archived under
  system_docs/patches/completed/rebind_after_first_meld_2026_10_03/ after promotion; boards synced. The story stays
  in_progress until the owner reports work package C (board row rebind_after_first_meld_acceptance routes it).
  EVIDENCE:
  - tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md:1-30
  - attention_board.md:173-173
  IMPACT: no agent work is owed on this story until C is reported.
  NEXT: owner reports C; the story and epic close on 5 passes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-10-03T21:08:00Z: IN_PROGRESS (acceptance only). Repair landed at 0.2.8219; both tasks closed. Remaining: the owner's
work package C on the delivered build; the story closes with the epic on its result.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
