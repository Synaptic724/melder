
# Task: cProfile rot-finding harness (crystallizer + MR first)

## Metadata
- Task ID: TASK-2026-07-12-cprofile-rot-harness
- Story: none (opens the post-1.0 performance program)
- Status: in_progress
- Owner: cowork
- Agent Name: mutation_0
- Priority: p1
- Created: 2026-07-12T12:05:00Z
- Updated: 2026-07-12T12:05:00Z

## Objective
Stand up `benchmarks/cprofile_testing/` (harness + tiered scenarios) and get
first owner-run numbers for the slow suspects: checkpoint load/save and the MR
verb family. Meld path EXCLUDED (owner ruling: already optimized). Next
surfaces after first numbers: linking + transaction admission.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-12 (this lane); benchmarks/ is not
  system-impacting (no patch gate; src untouched).
- EXECUTION_BOUNDARY: benchmarks/cprofile_testing/** only.
- DEPENDENCIES: green tree (persistence-loop epic turned in).
- EXIT_GATE: owner runs all tiers; rot findings triaged into fix tickets.
- FAILURE_ESCALATION: DECISION_REQUEST when a finding needs a src change.

## Scope Boundaries
- In scope: harness, crystallizer checkpoint scenarios, MR verb scenarios,
  linking/transaction scenarios (next slice), results interpretation.
- Out of scope: meld-path profiling; any src/melder edits (separate tickets).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: harness + first two scenario files implemented and
  committed; awaiting first owner tier runs.

## Steps / Checklist
- [x] Harness (ProfileScenario, dual measurement, tiered, .prof + report).
- [x] Crystallizer scenarios (seal / cache round-trip / load, fresh-state loads).
- [x] MR scenarios (record entries / residency joins / campaign view).
- [ ] Owner runs small/medium/large on 3.14t; paste summaries back.
- [ ] Triage: ratio table -> rot list -> fix tickets.
- [ ] Linking + transaction-admission scenarios (next slice).

## Validation
- Not run. (Scenario scripts require the 3.14t runtime; container lacks it.)
- Recommended commands: see benchmarks/cprofile_testing/README.md.

## Notes
- DATETIME: 2026-07-12T12:05:00Z
  TYPE: PLAN
  CLAIM: Rot detection = tier-ratio comparison (wall-clock, profiler-free)
    with cProfile tottime tables naming frames; checkpoint_load runs
    fresh-state-per-repeat because a load consumes its world.
  EVIDENCE:
  - benchmarks/cprofile_testing/profile_harness.py:1-60
  IMPACT: One consistent method across all future performance lanes.
  NEXT: Owner tier runs; then triage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Harness + two scenario files committed. Owner runs tiers, pastes summaries;
findings become fix tickets. Linking/transactions scenarios are the next
slice. Board row pending (board replica still poisoned this session).
