

# Story: Type annotations select type providers; spellframes stay categories

## Metadata
- Story ID: STORY-2026-10-03-annotation-type-vs-category-matching
- Epic: EPIC-2026-10-03-annotation_category_provider_collision
- Status: in_progress
- Owner: user
- Agent Name: fable_1
- Priority: p1
- Created: 2026-10-03T23:52:00Z
- Updated: 2026-10-04T01:25:00Z

## User Narrative
As a Melder host that groups many definitions under one spellframe category (MelderOps: 14 framework classes
under "spectrum") and declares its consumers with truthful type annotations (`spectrum: Spectrum`), I want a
type annotation to select the provider of that type and nothing else, so that a category sharing the type's
name never turns its members into providers or raises an ambiguity at bind/conjure time.

## Value / MRP Alignment
Ordinary type injection must identify providers without silently broadening a category into a type; the
0.2.8218 address-key matcher does exactly that for class annotations. One coherent contract for class,
string and ForwardRef annotations, existing objects, and the indexed and scan resolvers, with explicit
addressing (SpellMap/SpellContract, meld by address) left as the intentional category selection.

## Ticket Contract
- ENTRY_GATE: the epic's evidence read (public-API probe, receipt, binding context); this story and its
  task routed on `attention_board.md`; the owner's category ruling on record in the epic.
- EXECUTION_BOUNDARY: Phase 3 annotation matching - `compiler_phase_3.py` (`_annotation_key`,
  `_spell_keys`, `_matches_annotation`, the candidate index and scan paths, `_resolve_single_by_annotation`,
  the local-frame DAG caller), `general_helpers.normalize_frame_key` as read, the structural snapshot's
  generation pin, their tests, and the system docs the change touches. Reads anywhere; edits only after a
  patch lane exists and the owner confirms the semantics (system-impacting: resolution contract).
- DEPENDENCIES: fable_0's 0.2.8218 lane (closed; its patch docs under
  system_docs/patches/completed/annotation_address_matching_2026_10_03/ state the current contract);
  fable_0's open flat_warm_body lane holds site_plan_lowering.py, the hydrators, caching_system.py - no edit
  there without a handoff; the epic's external evidence in priv_commandops (hashes recorded in the epic).
- EXIT_GATE: the four-case public-API probe passes on current source with a Melder-only fixture (both
  category-collision cases green, both controls green); the semantics are a DECISION the owner confirmed;
  the repair lands red-to-green with regressions for class, string, ForwardRef, existing-object, class-frame
  and string-frame cases on both the indexed and scan paths; docs, notch, note, rebuild; work package
  (consumer acceptance: the unchanged Actions replacement test on the delivered build) handed to the owner.
- FAILURE_ESCALATION: DECISION_REQUEST before changing what a string or Protocol/shape-frame annotation
  resolves; CONFLICT if the cause lives in a file another live agent holds.

## Requirements (Functional)
- `spectrum: Spectrum` selects the Spectrum spell when other classes share spellframe "spectrum".
- Explicit addressing (SpellMap/SpellContract defaults, meld by spellframe/binding_name) is unchanged.
- Class and string annotations resolve the same binding; existing objects still match their class.

## Requirements (Non-Functional)
- No new hot-path cost in meld; Phase 3 cost stays O(candidates) per socket.
- Indexed and scan candidate membership agree (one predicate).

## Scope Boundaries
- In scope: the matching predicate, its index, regressions, docs, note, notch.
- Out of scope: renaming the MelderOps category; Any/default workarounds; the Autofac-strict rule; the
  rebind lifecycle (landed at 0.2.8219).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner assigned the epic to fable_1 in chat (2026-10-03 17:46 local: "theres a new epic
  for you about spectrum ... its a correctness bug again with spellframes").

## Dependencies / Related Work
- tickets/epics/2026-10-03_annotation_category_provider_collision_epic.md
- system_docs/patches/completed/annotation_address_matching_2026_10_03/ (the 0.2.8218 contract)
- tickets/epics/2026-10-03_rebind_after_first_meld_epic.md (distinct, repaired at 0.2.8219)

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-10-03-reproduce-annotation-category-collision - Melder-only reproduction of the
      four-case probe on current source, the matcher read in full, the semantics options with evidence
      (STRATEGY_DISCUSSION), the owner's DECISION.
      tickets/tasks/2026-10-03_reproduce_annotation_category_collision_task.md
- [ ] Task: TASK-2026-10-04-repair-annotation-kind-matching - the decided change set: spellframe kind on the
      binding, concrete-class frame refusal, kind-aware Phase 3, crystal frame kind, generation 20, sweep,
      docs, notch, note, rebuild.
      tickets/tasks/2026-10-04_repair_annotation_kind_matching_task.md
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Probe 4/4 green on the repaired source; the unchanged Actions replacement test is the owner's acceptance.
- The contract is written in src_architecture/src_components and the README DI paragraph.

## Validation / Test Plan
- The ported probe red on current source, green after; phase-3 unit tests (indexed and scan parity);
  component conjure cases; the four tiers.

## UX / API / Data Notes
- No public API change expected; a behaviour change in what a string annotation matches needs the
  owner's DECISION first.

## Risks / Mitigations
- Breaking a supported Protocol/shape-frame pattern: survey the suites for frame-name resolution before
  choosing the predicate; run the prototype against all tiers.
- fable_0 authored the 0.2.8218 semantics and is mid-lane elsewhere: their files are not touched; the owner
  relays the change.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No implementation before the patch lane exists and the owner confirmed the semantics.

## Open Questions
- (answered 2026-10-03 19:00 local) A string frame is a category and satisfies no annotation; a Protocol frame
  is a category and a contract and satisfies a Protocol annotation; a concrete class is not a valid frame.

## Decision Log
- 2026-10-03 17:46 local (owner, chat): fable_1 takes the epic; it is a correctness bug with spellframes.
- 2026-10-03 18:22-19:00 local (owner, chat; recorded on the reproduce task, DECISION 2026-10-04T01:00Z): a
  spellframe is a label; a Protocol frame is a label and a contract; concrete classes are refused as frames; the
  binding records the kind; Phase 3 matches by kind (class -> type, Protocol -> implementers, string -> type or
  contract, collections -> the group their kind names); follow-ups (deeper Protocol check, `implements=`) are
  separate tickets.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/annotation_category_collision_20261003/ (created by the task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: kept with the epic's evidence at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - annotation/provider versus category semantics
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-10-03T23:52:00Z
  TYPE: PLAN
  CLAIM: Reproduce first with a Melder-only probe (Spectrum unique at ("spectrum","Spectrum"); Toolbox in the
  same category vs another; class and string annotations), then read the matcher and the 0.2.8218 patch
  docs in full, survey the suites for frame-name resolution, and write the options (type key only; type key
  + class-object frames; keep name matching with type-preference) as a STRATEGY_DISCUSSION for the owner.
  EVIDENCE:
  - tickets/epics/2026-10-03_annotation_category_provider_collision_epic.md:14-60
  - system_docs/patches/completed/annotation_address_matching_2026_10_03/component_patch_spellcompiler_phase3.md:7-24
  IMPACT: the fix is a semantics decision before it is an edit; the owner rules on it with evidence.
  NEXT: open the reproduction task and run the probe on current source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T01:25:00Z
  TYPE: DECISION
  CLAIM: Gate transition: the reproduce task delivered the reproduction, the rule as FACT, the option-B prototype
  survey, the class-frame survey and the owner's DECISION; the repair task opened with its patch lane
  (annotation_kind_matching_2026_10_04: architecture, binding pipeline, Phase 3, crystallizer frame kind, code
  description). The crystallizer is in scope because restore and graft rebind frames by NAME, which the kind rule
  would read as a category.
  EVIDENCE:
  - tickets/tasks/2026-10-03_reproduce_annotation_category_collision_task.md:240-291
  - tickets/tasks/2026-10-04_repair_annotation_kind_matching_task.md:1-170
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2173-2190
  IMPACT: the story's remaining gates are the repair's landing and the owner's consumer acceptance.
  NEXT: the repair task's red run.
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
STATE 2026-10-03T23:52:00Z: IN_PROGRESS. Lane opened on the owner's word; the reproduction task carries the work.
Resume from its latest note's NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
