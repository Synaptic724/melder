# Story: Survey compiler phases 1-11 for the value-only IR boundary

## Metadata
- Story ID: STORY-2026-08-03-phase-pipeline-survey
- Epic: EPIC-2026-08-03-comptime-ir-phase-pipeline
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-25T21:23:55Z
- Updated: 2026-09-26T00:08:30Z

## User Narrative
As the Melder owner, I want every compiler phase's real inputs, outputs and live-object holds
established from source, so that the IR schema is designed against behavior rather than the
architecture document's description of intent.

## Value / MRP Alignment
The epic moves phases 1-10 onto a value-only IR with phase 11 as the sole hydration boundary. Its
largest recorded risk is that its description of the phases comes from `src_architecture.md` and
the module layout, not from the phase source. A schema designed on that basis encodes intent, and
the mismatch surfaces mid-port where it is expensive. This story closes that gap first; the epic's
entry gate says nothing else may start until it is accepted.

## Ticket Contract
- ENTRY_GATE: Epic claimed by fable_0; owner approves this story's scope; the active board row
  routes to the current tranche task.
- EXECUTION_BOUNDARY: Read-only over `src/melder/aether/spellbook/spell_compiler/**`, the Spellbook
  conjure call sites that drive it, and `tests/`. Writes limited to this story, its tasks, and
  `artifacts/ir_phase_survey_20260925/`. No `src/`, `tests/` or patch-lane edits. AMENDED
  2026-09-25: owner authorized updating `system_docs/src_architecture.md` and
  `system_docs/src_components.md` where the survey finds them wrong or incomplete; each edit is
  source-evidenced and both indexes regenerate in the same pass.
- DEPENDENCIES: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md; `src_components.md`
  sliced at `Component: SpellCompiler and Validation Pipeline` and
  `Subcomponent: SpellCompiler Phase Artifacts` for navigation only.
- EXIT_GATE: All three tranche tasks in review with per-phase records; `summary.md` lists every
  object-bound point with `path:start-end`; owner accepts; epic Milestone 1 checked.
- FAILURE_ESCALATION: BLOCKER if a phase's behavior cannot be established from source;
  DECISION_REQUEST when a hold looks identity-bearing rather than nameable; CONFLICT when source
  contradicts `src_architecture.md` or the epic's phase description.

## Requirements (Functional)
- Per phase 1-11: entry symbol(s), consumed inputs (type, producer, storage location), produced
  outputs (type, consumer, storage location), and every point where a live object is held.
- Each held object classified: value-expressible (a name or id suffices), identity-bearing (the
  object's identity is load-bearing), or runtime-only (callable, lock, thread state, instance).
- Each phase's side effects on runtime objects (Spell, Spellbook, SpellSystemStates, frame)
  recorded; those are where compile time and runtime are currently the same objects.
- `shared_compiler_executions.py` and `utility.py` covered wherever a phase delegates into them.
- The phase-11 emit surface recorded precisely: what it consumes and what it hands the runtime.

## Requirements (Non-Functional)
- Unknown-first: every claim carries `path:start-end` covering the logic, or stays UNKNOWN.
- No design decisions in this story: candidates for the identity question are listed, not chosen.
- Search locates; reading evidences. No claim rests on a grep hit or a document section.

## Scope Boundaries
- In scope: `spell_compiler/phases/*.py`, `spell_compiler.py`, `spell_compiler_artifact.py`, and
  the delegate packages a phase calls (spell_requirements_finder, symbolic_graph, dag, validation,
  blueprints, system, topology, spell_analyzer, artifact_processor, codegen_planner,
  codegen_creation_system) to the depth needed to name what crosses a phase boundary.
- Out of scope: meld and the runtime lane, Creations, ConduitWard, Crystallizer, MutationResearch,
  any schema design, any code change.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Opened by fable_0 on epic assignment (2026-09-25); owner scope approval pending.
- from_state: ready
- to_state: in_progress
- transition_reason: Task 1 moved to in_progress on the owner's go (2026-09-25); story follows its
  child-task state.

## Dependencies / Related Work
- tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md
- tickets/epics/2026-09-24_override_execution_performance_epic.md (updater_0 and updater_1 hold
  review-stage proposals touching phases 8-11; this story is read-only alongside them)
- tickets/tasks/completed/2026-05-24_investigate_phase_scheduler_and_spell_compiler_pipeline_task.md
  (historical pipeline investigation; re-verify against current source before citing)

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-09-25-survey-compiler-phases-1-4 - driver plus phases 1-4
  tickets/tasks/2026-09-25_survey_compiler_phases_1_to_4_task.md
- [ ] Task: TASK-2026-09-25-survey-compiler-phases-5-7 - root blueprints, system validation,
  change control (opened when tranche 1 reaches review)
- [ ] Task: TASK-2026-09-25-survey-compiler-phases-8-11 - occurrence, injection, patch maps,
  execution plan, phase-11 emit surface (opened when tranche 2 reaches review)
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery.

## Acceptance Criteria
- Eleven per-phase records plus a driver record exist under `artifacts/ir_phase_survey_20260925/`,
  each with inputs, outputs, classified holds, runtime side effects, and evidence ranges.
- `summary.md` tabulates every object-bound point across phases 1-10 and states, per point,
  whether a symbolic id can replace it or an identity concept is required.
- Every contradiction between source and `src_architecture.md` is a CONFLICT note.
- Remaining UNKNOWNs are listed with the file:symbol to investigate.
- Owner accepts; epic Milestone 1 checked.

## Validation / Test Plan
- Source reads are the evidence. No tests run in this story: "Not run."

## UX / API / Data Notes
- None. Read-only.

## Risks / Mitigations
- The override-performance epic proposes compiler changes in phases 8-11; source may move under
  this survey. Mitigation: cite ranges with dates, re-verify before the schema story, and notify
  updater_0 that this lane is read-only.
- Delegate packages are large; following every call exhausts context. Mitigation: read a delegate
  only to the depth needed to name the type crossing the phase boundary; record deeper questions
  as UNKNOWN with a file:symbol pointer.
- The VM shell runs Python 3.10.12 against a 3.14 project floor. Nothing executes in this story.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No behavior claim from `src_architecture.md`, the epic text, or a search hit.

## Open Questions
- Does any phase hold an object whose identity, not its name, is load-bearing? (epic identity
  question; evidenced here, decided in the schema story)
- Does `dynamic=True` change what phases 1-10 carry? (epic open question; record what source shows)

## Decision Log
- 2026-09-25: Story ID kept as the epic pre-named it (STORY-2026-08-03-...) so the epic's checklist
  link resolves; the file name carries the creation date. Do not rename either.
- 2026-09-25: Owner authorized system-document corrections from this survey ("if you're finding
  weird things in the documentation feel free to update src_arch and src_comp").
- 2026-09-25: Three tranche tasks mirror the epic's port tranches (1-4, 5-7, 8-10 plus 11) so each
  record hands directly to its port story.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/ir_phase_survey_20260925/ (created by the first tranche task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at story closure; findings promote into the schema story.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: compiler phase inputs and outputs; live-object holds; phase-11 emit surface.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-25T21:23:55Z
  TYPE: PLAN
  CLAIM: Survey runs in three read-only tranches (driver plus 1-4, 5-7, 8-11), one task each, one
    artifact file per phase plus a cross-phase summary. Inputs, outputs, holds and runtime side
    effects are recorded from source before any schema work.
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:75-80
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:163-168
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:199-204
  IMPACT: Closes the epic's largest recorded UNKNOWN before design; keeps each tranche inside one
    context window.
  NEXT: Owner approves scope; task 1 moves to in_progress and reads spell_compiler.py first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:23:55Z
  TYPE: FACT
  CLAIM: The phases directory holds two files the epic's evidence list does not name:
    shared_compiler_executions.py (1516 lines) and utility.py (44 lines). Eleven phase modules
    total 3544 lines; phase 3 (1035) and phase 5 (713) are the largest.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1-1516
  - src/melder/aether/spellbook/spell_compiler/phases/utility.py:1-44
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1-1035
  IMPACT: Phase bodies may live in the shared module; a survey of the phase files alone would
    describe wrappers rather than behavior.
  NEXT: Task 1 follows delegations from compiler_phase_1.py into the shared module as they occur.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-25T21:23:55Z
  TYPE: RISK
  CLAIM: updater_0 and updater_1 hold review-stage proposals that change phases 8-11 and the
    creation runtime door; the melder verification story excludes the compiler-IR epic from its
    scope. No other lane writes IR work today, but tranche-3 source may move on owner selection.
  EVIDENCE:
  - tickets/stories/2026-09-25_verify_override_writer_and_contract_story.md:51-52
  - attention_board.md:89-92
  IMPACT: Tranche-3 findings may need re-verification before the schema story; a future port must
    be sequenced after or coordinated with the override implementation.
  NEXT: With owner approval, send updater_0 one NOTICE that this lane is read-only over
    spell_compiler/**.
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
Opened 2026-09-25 by fable_0 on owner assignment of the epic. Read-only survey in three tranche tasks;
task 1 (driver plus phases 1-4) is created and routed, awaiting owner scope approval. Nothing under
`src/` has been read beyond line counts. Resume from task 1's latest NEXT.
UPDATE 2026-09-25: the epic's Context / Handoff Summary now carries a dated state-of-knowledge
section (owner direction, source facts, measurements, design synthesis); read it first. Task 1
step 1 is done; the per-phase record shape gained reflection points, Python-callback points and
world reads. Resume at task 1 step 2 (driver read).

STATE 2026-09-25T22:51:29Z (fable_0), written ahead of a context compaction - resume from here:
- Done: task 1 steps 1-2. Components index verified and SpellCompiler slices read; driver read
  complete (`spell_compiler.py`, `spell_compiler_artifact.py`, the IR seams in
  `shared_compiler_executions.py` ranges 1-400/400-640/1018-1100/1278-1516, phases 9 and 10 whole,
  conjure cache paths in `spellbook_creation_system.py` 215-520). First deliverable landed:
  artifacts/ir_phase_survey_20260925/driver.md (artifact_board row active).
- Key results (evidence in task 1 notes and driver.md): world-read surface by signature (1, 2, 9, 10
  closed; 3-8 and 11 read the world); a dormant, signed, value-only phase 2-5 export reserved by
  phase 2's NOTE for incremental recompile; phase-11 step rows are consumed and memoized; the
  transient plan is int arrays with call targets factored out; full cache hit skips only 8-11 and
  phases 1-7 run on every conjure; signature hazards (unsorted set pickling, `repr` fallback on user
  contract payloads) and a duplicated serializer; phase-1 requirements may be borrowed from a
  bind-time resolution profile (level-0 lead).
- Docs corrected on owner authorization: src_architecture.md boot step and conjure sequence;
  src_components.md SpellCompiler component (IR seams block, Key Files) and conjure flow; both
  indexes regenerated and current. Packaged hardcopies now lag the docs (owner-run build assets).
- Next (updated 2026-09-25T22:53:13Z): resolution_profile.py and compiler_phase_1.py are read and phase_01.md
  exists as PARTIAL. Level 0 at bind is source-backed (bind runs the requirements finder; phase 1
  borrows it; `SpellResolutionProfile` is a documented execution-model-independent phase 1-4
  payload with only requirements populated). Read `spell_requirements_finder.py` (1333, three
  chunks) and `spell_requirements.py`, complete phase_01.md, then phases 2, 3 (three chunks), 4.
- Open for the owner: regenerate build assets; a determinism test for the signature path; tranche
  reorder proposal (structural snapshot before any phase port) recorded on the epic.
STATE 2026-09-26T00:08:30Z (fable_0): re-onboarded after compaction; task 1 phase 1 is complete
(phase_01.md, level-0 answer: extraction, not rename; no world reads in phase 1). Next: phase 2.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
