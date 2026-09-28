# Story: Codegen cost model - a planner that guesses the speed of candidate bodies before any is emitted

## Metadata
- Story ID: STORY-2026-09-28-codegen-cost-model-planner
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-28T00:37:47Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want the phase-10 planner to carry a cost model that, from a spell's harvested profile
and its step rows, predicts the ns per creation of each candidate body (plain, capture, door-specialized,
thread-affine, key-set precompiled, and their combinations) without emitting any of them, so that the
tournament only emits and measures the few candidates the model ranks best, and the model gets recalibrated by
what the measurements then say.

## Value / MRP Alignment
The tournament is bounded (3-5 attempts per spell, the count kept on the spell and carried through hydration),
so which candidates get an attempt matters. A cost model turns the combinatorial space of styles into a ranked
shortlist for free: the melc ledger already prices a plan statically from its rows with measured VM prices per
site kind (door, shared read, guarded constant, constructor floor, registration, plan frame), and it
reproduced the live numbers within the VM's noise. The same arithmetic, fed the profile's hit rates and
creator counts, is the planner's heuristic; the tournament's measurements are its feedback.

## Ticket Contract
- ENTRY_GATE: owner's pick; the harvester's profile schema and the versioning story's tournament fixed;
  patch docs (component: SpellCompiler and Validation Pipeline - planner discovery; code description: the
  cost model and its calibration) before src.
- EXECUTION_BOUNDARY: `codegen_planner/` (discovery: candidate style ranking by predicted ns; plan metadata:
  predictions), a value-only price table (defaults from the ledger, recalibrated from tournament results and
  kept on the frame's DevOps registry), tests; no emitter change.
- DEPENDENCIES: STORY-2026-09-27-pgo-harvester-cycle-and-emission (profile); STORY-2026-09-27-creation-
  context-versioning (tournament, attempt count); STORY-2026-09-28-harvest-driven-phase-regeneration
  (profile reaches phase 10).
- EXIT_GATE: the planner ranks candidates by predicted ns with the prediction recorded per candidate; the
  tournament emits the top-k; measured ns per candidate are fed back into the price table; on the harness
  shapes the model's ranking agrees with measurement on the winner in >= 80% of cases (to settle); PGO off
  unchanged.
- FAILURE_ESCALATION: DECISION_REQUEST if the model cannot separate candidates within the VM's noise on the
  owner's shapes (then the tournament runs all candidates and the model is only a report).

## Requirements (Functional)
- Price table: value-only ns per site kind (door, shared read, guarded constant, inline constructor floor,
  generic step, registration with and without disposal, plan frame, thread-affine append, key-set compile),
  seeded from the ledger's calibrated defaults, recalibrated from measured windows per frame.
- Prediction: for each candidate style combination, sum the priced sites the profile says the body will run
  (hit rate weighted: a site with a 100% hit rate prices as a read, or as a constant under capture; a many
  step prices as constructor plus registration), plus the door and the plan frame.
- Ranking: candidates ordered by predicted ns; the plan metadata records the predictions; the tournament
  takes the top-k (k = the attempt budget).
- Feedback: each measured window updates the price table for the site kinds the body contained (a bounded,
  monotone-safe update), and the report shows predicted vs measured per spell.
- Attempt budget: the spell keeps an attempt count that hydration restores from the manifest, so a spell
  that spent its budget is left alone in later processes until its shape changes.

## Requirements (Non-Functional)
- The model runs only inside the deferred pass (phase 10); nothing on the warm path.
- Prices and predictions are plain numbers; the report can print them.
- Overlay rules; the planner's docstrings carry the arithmetic.

## Scope Boundaries
- In scope: the price table, the prediction, the ranking, the feedback, the attempt budget wiring with the
  versioning story, tests, docs.
- Out of scope: emitting any style (style stories); the tournament mechanics (versioning story).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's direction (2026-09-28T00:37:47Z); opens when the owner picks it.

## Dependencies / Related Work
- artifacts/pgo_strategies_20260927/vm_commandops_melc_ledger_gil0_20260927.md (the static price model
  reproducing the live numbers)
- tests/experimentation/melc_cache_ledger.py:1-218 (the arithmetic and the calibrated defaults)
- src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:60-145 (phase 10
  discovery -> candidate styles)
- STORY-2026-09-27-creation-context-versioning (tournament); STORY-2026-09-27-persisted-creation-profiles
  (attempt count and best version in the manifest)

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (the context reports measured ns per
      version; the model lives in phase 10) and in the planner discovery; patch docs.
- [ ] Task: the price table and the prediction over the profile; unit tests against the ledger's numbers.
- [ ] Task: ranking into the plan metadata and the top-k hand-off to the tournament; feedback from measured windows.
- [ ] Task: agreement study on the harness shapes (predicted winner vs measured winner); owner-run on the gauntlet.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- For a profiled spell the plan metadata lists every candidate with its predicted ns; the tournament emits
  only the top-k; after the windows the report shows predicted vs measured; the agreement study meets the
  settled threshold.

## Validation / Test Plan
- Unit tests on the arithmetic (ledger parity); component tests on ranking and feedback inside the deferred
  pass; the agreement study in the experiment harness; owner-run gauntlet for the final numbers.

## UX / API / Data Notes
- No public API change; predictions and prices readable through the report.

## Risks / Mitigations
- The model is wrong on a shape -> the tournament still measures; plain is always a candidate; feedback
  recalibrates.
- Per-frame price drift (different machines) -> prices are per frame and recalibrated from the frame's own
  windows.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- k (the attempt budget): 3 or 5, and does a shape change reset it?
- Does the price table live on the frame's DevOps registry or on the book's configuration?

## Decision Log
- 2026-09-28T00:37:47Z (owner): during phases 8-11 a builder system that can guess the speed of a few
  different combinations without generating the code - heuristics and strategies to make the codegen better
  from the data; attempts bounded by a count the spell logs and hydration carries, so after x tries the
  object is left alone.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (proof and runs shared by the epic; new runs land here)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - cost model; price table; candidate ranking; attempt budget; feedback
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-28T00:37:47Z
  TYPE: MEASURE
  CLAIM: A static price model over the manifest rows (door 150, shared read 23 -> capture 7, constructor floor 60,
    registration ~600 in situ / 305-384 standalone, plan 25; VM, directional) reproduced the live commandops
    shapes: predicted Worker 858 vs measured 650-853, ContextRoot 950 vs 1136-1219 (the constructor's own five
    attribute stores are user code the floor does not price). That is the seed of the planner's heuristic.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_commandops_melc_ledger_gil0_20260927.md
  - artifacts/pgo_strategies_20260927/vm_commandops_shapes_gil0_20260927.md
  - tests/experimentation/melc_cache_ledger.py:1-218
  IMPACT: The model can rank candidates before emission; the tournament measures the top-k and recalibrates it.
  NEXT: owner picks; the investigation task settles k and the reset rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:42:24Z
  TYPE: MEASURE
  CLAIM: Owner's question - count calls instead of measuring time? Not equivalent, by the numbers already in hand:
    the opt-in specializer cut C calls on WorkerNoDisposal from 2 to 1 and on ContextRootNoDisposal from 6 to 1
    and got SLOWER both times (246-251 -> 256-277 ns; 528-534 -> 641-676 ns), while `add_many_creations` is one
    Python call plus a handful of C calls and costs 300-600 ns against ~25 ns for a `dict.get` C call. Calls
    have unequal prices (Python call ~50-100 ns, C call 15-40, lock 57-67, user constructor arbitrary) and a
    body can trade calls for bytecode. What calls ARE: deterministic, noise-free and known at emission time
    without any probe, so a weighted call count (kind x price) is the cost model's input and its ranking
    signal; time stays the arbiter, and a hybrid needs only two timed windows (predicted winner vs plain)
    instead of one per candidate.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_commandops_shapes_gil0_20260927.md
  - artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
  - artifacts/pgo_strategies_20260927/vm_probe_overhead_prototype_gil0_20260927.md
  IMPACT: The planner ranks by priced calls (free); the tournament confirms with time (measured); the timed
    cost drops from k windows to two.
  NEXT: owner picks; the investigation task fixes the price table's units as per-call-kind.
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
STATE 2026-09-28T00:37:47Z: DRAFT. The planner-side cost model, drafted from the owner's direction with the
ledger as its seed; not routed. Opens when the owner picks it.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
