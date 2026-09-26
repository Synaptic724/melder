

# Story: Supplied overrides skip construction through one site-plan lowering (design v2)

## Metadata
- Story ID: STORY-2026-09-26-implement-override-site-plan-lowering
- Epic: EPIC-2026-09-24-override-execution-performance
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T11:28:08Z
- Updated: 2026-09-26T18:21:24Z

## User Narrative
As a Melder user, I want `meld(Root, override={"a": obj})` to use `obj` without building A or anything only
A needed, and to run about as fast as a normal meld, so that overrides are a cheap, predictable way to pass
objects into a graph.

## Value / MRP Alignment
Replaces two override compilers and a per-call targeting runtime with one site graph, one plan per key set
and one lowering shared with normal melds. The core becomes smaller and uniform instead of gaining a
parallel path; the prototype showed the behavior and speed on 3.14t and GIL before any production change.

## Ticket Contract
- ENTRY_GATE: Owner approval of design_v2.md and Q1-Q5 (2026-09-26T11:26Z); patch lane
  override_site_plan_2026_09_26 open; board row routes to the active child task.
- EXECUTION_BOUNDARY: One step task at a time (S1-S6), each within its task's declared files and its patch
  docs. No step starts code before its patch docs and file list are confirmed by the owner.
- DEPENDENCIES: design_v2.md, prototype_results.md, melder_1's regression matrix, the shipped slot guards,
  fable_0's compiler tranche (shared_compiler_executions, phase-8 keys, cache payload gate).
- EXIT_GATE: S1-S6 done; epic success metrics met (3-of-5 supplied builds 2 + consumer; deep both branches
  builds the root only); suites green on 3.14t and GIL; docs, graph, assets and release note current.
- FAILURE_ESCALATION: DECISION_REQUEST for any semantic change not listed as B1-B8; CONFLICT when source
  contradicts the design; BLOCKER for asset rebuilds without owner approval.

## Requirements (Functional)
- Supplied dependencies and everything only they need are never constructed.
- Key grammar, ranks and bad-key errors unchanged; P1 cuts, P2 errors, P3 static operands, E1 equality.
- Normal melds run through the same lowering (empty key set).
- Unresolved inputs are decided in the plan.

## Requirements (Non-Functional)
- Override melds with root keys within the measured prototype range (76-106% of normal on small graphs).
- No new locks; warm hits stay lock-free; free-threaded and GIL builds both qualified.
- Conjure cost does not grow with logical path count after S5.

## Scope Boundaries
- In scope: Phase 9 site graph, override key resolution, Phase 10/11 plans and lowering, CreationContext
  override dispatch, family manifests and cache generation, Phase-5 overlay retirement, docs and assets.
- Out of scope: new public API, value validation of supplied objects, hook standardization, the comptime IR
  epic (fable_0), existing-object ownership redesign.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved design v2 after the E1-E4 prototype ("fucken send it"),
  2026-09-26T11:26Z.

## Dependencies / Related Work
- tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md (design record)
- artifacts/melder_override_design_20260926/design_v2.md, prototype_results.md
- system_docs/patches/active/override_site_plan_2026_09_26/

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-09-26-build-site-graph-and-override-key-resolver - S1 site graph, resolver, oracle (done;
  tickets/tasks/completed/2026-09-26_build_site_graph_and_override_key_resolver_task.md)
- [ ] Task: TASK-2026-09-26-fix-collection-member-many-sharing - defect: collection members share many deps
- [ ] Task: S2 shared lowering for normal melds (opens after S1)
- [ ] Task: S3 key-set plans and dispatcher; retire override emitters and targeting runtime
- [ ] Task: S4 unresolved inputs decided in the plan
- [ ] Task: S5 retire the Phase-5 per-path overlay
- [ ] Task: S6 qualification: docs, graph, assets, release note
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Epic examples: 3 of 5 supplied builds 3 objects; deep graph with both branches supplied builds only the
  root.
- Behavior matches B1-B8 in design_v2.md and nothing else changes (regression matrix, Codex corpus).
- Measured throughput on the existing experiment graphs at or above the prototype results.
- Full unit, component and integration suites pass on 3.14t and GIL.

## Validation / Test Plan
- Per step: unit and component tests named in the step's patch docs; S2/S3 run the full suites on both
  builds, the override performance experiment and the slot-guard lock probes.

## UX / API / Data Notes
- No public API change. `override=(...)` over DI-injected root parameters starts working (B5).

## Risks / Mitigations
- Constructor order changes (B2): documented in the release note; suites catch order dependence.
- Deep normal 2-5% slower in the prototype (R5): S2 parity gate investigates before switching.
- Concurrent compiler work (fable_0): mailbox notices before touching shared files.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Cache generation 13 lands with S2 or S3 (whichever first changes emitted code); generation 12 was
  taken by melder_1's complete_bundle_restage (M1-12, recorded in the S1 task notes 2026-09-26T11:49:56Z).

## Decision Log
- 2026-09-26: Owner approved design v2 and Q1-Q5 as recommended (P2 error kept, P3 static operands, key
  names checked once per key set with no value checks, B2/B5/B7 accepted, build order S1-S6).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/override_site_plan_2026_09_26/
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure after durable deltas merge into the canonical docs.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Override site-plan lowering implementation
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-26T11:28:08Z
  TYPE: DECISION
  CLAIM: Owner approved design v2 after reviewing prototype_results.md ("oh yeah that looks great fucken
    send it"). melder_0 takes this as approval of Q1-Q5 as recommended and of the S1-S6 build order; the
    patch lane override_site_plan_2026_09_26 is opened with S1 contracts, and S1 source edits wait for the
    owner's confirmation of the S1 file list.
  EVIDENCE:
  - artifacts/melder_override_design_20260926/design_v2.md:451-459
  - artifacts/melder_override_design_20260926/prototype_results.md:17-30
  IMPACT: Implementation proceeds step by step behind patch lanes; semantics are fixed by B1-B8.
  NEXT: Owner confirms the S1 file list; then implement S1 in the VM copy and on the device tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T12:09:44Z
  TYPE: FACT
  CLAIM: S1 is in review: site graph section, OverrideKeyResolver and oracle are in the device working tree
    (nine declared files, uncommitted), with 31 new passing tests and no other outcome changed on 3.14t or GIL.
    Carried into S2/S3: cache generation 13 (M1-12), contract payloads as live descriptor reads and U1 answered
    as "contract-backed dependency stays a dependency edge" (F0-6), about 7% extra setup on the deep
    many-graph, and a pre-existing behavior for the owner: many-existence dependencies of collection members
    are one shared object (path ids keyed by parameter names).
  EVIDENCE: tickets/tasks/2026-09-26_build_site_graph_and_override_key_resolver_task.md
  IMPACT: S2 can start from a verified site graph once the owner accepts S1.
  NEXT: Owner review of S1; then open the S2 task with its patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T12:13:26Z
  TYPE: DECISION
  CLAIM: Owner accepted S1 and ruled that a many object shared across collection members is a defect ("a many
    is not meant to be shared like that"); owner instruction: keep working until done. The defect is fixed
    first (new task), because S2's lowering follows instance keys; then S2-S6 in order, each with its file
    list and patch docs recorded before code.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_build_site_graph_and_override_key_resolver_task.md
  - tickets/tasks/2026-09-26_fix_collection_member_many_sharing_task.md
  IMPACT: Story order is S1 done -> collection fix -> S2 -> S6.
  NEXT: Trace Phase-8 path minting for the collection fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T18:21:24Z
  TYPE: FACT
  CLAIM: Cross-task state. S2-S5 ran inside TASK-2026-09-26-build-site-plan-lowering (one lane, step notes there):
    S3 key-set plans and dispatcher (old override lane retired, cache generation 14), S2 normal melds on the same
    lowering (parity gate met), S4a unresolved inputs decided in the plan for the plan families, S5a Phase-5
    per-path overlay retired (conjure linear in sites: 15-site binary chain 117 -> 7 ms). Open, all owner-gated:
    S4b (solo lane and the failure-path hook), one retirement pass for code these steps left unused (S2b-3 list
    plus SpellOverrider, targeting engine, SocketRefSanityStrategy, blueprint socket API, resolve_path_registry,
    Phase-5 capture rows), and S6 (docs promotion, asset rebuild, release note). Version 0.2.65 uncommitted.
  EVIDENCE: tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: Behavior work for the story is done except S4b; the rest is deletion and qualification.
  NEXT: Owner decisions on S4b and the retirement pass; S6 inventory meanwhile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
Opened 2026-09-26T11:28Z after owner approval of design v2. S1 (site graph + resolver + oracle, no
runtime change) is the active task; its patch docs are in the patch lane. Later steps open one at a time.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
