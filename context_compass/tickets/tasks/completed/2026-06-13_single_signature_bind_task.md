

# Task: Single-signature bind (share one inspect.signature between profile and requirements finder)

- Completed: 2026-06-13T01:40:00Z
- Summary: Last reflection duplication in the bind pipeline eliminated. One Signature
  object computed per class bind, owned by the binding profile, borrowed by the
  requirements finder under an object-identity guard with fresh-compute fallback.
  Bind median 3.19 -> 2.71ms (-15%; session total 4.5 -> 2.7ms, -40%); 2,010 tests
  green with zero drift. User accepted on measured gains.

## Metadata
- Task ID: TASK-2026-06-13-single-signature-bind
- Story: none (follow-up to completed hot-path lane)
- Status: done
- Owner: claude
- Agent Name: compiler_strategy_0
- Priority: p2
- Created: 2026-06-13T00:55:00Z
- Updated: 2026-06-13T00:55:00Z

## Objective
Eliminate the last known duplication in the bind->phase-11 pipeline: v4 added a second
`inspect.signature` construction per bind (profile `init_signature` + requirements
finder), 58 calls for 29 binds, ~1/3 of bind cost combined. Compute once, share.

## Ticket Contract
- ENTRY_GATE: board row routes here; design note below documents the sharing direction.
- EXECUTION_BOUNDARY: `binding_profile.py`, `binding_profile_strategy.py`,
  `spell_requirements_finder.py`, matching unit tests. No phase/scheduler files.
- DEPENDENCIES: completed hot-path ticket (v4 fingerprint, requirements borrow).
- EXIT_GATE: user-run suites green + bind median drop in cycle benchmark.
- FAILURE_ESCALATION: CONFLICT note if finder's signature target differs from the
  profile's `inspect.signature(cls)` in any spell shape (would change classification).

## Scope Boundaries
- In scope: one Signature object computed at profile build, stashed on the binding
  profile, reused by the requirements finder with fresh-compute fallback.
- Out of scope: any change to signature CONTENT consumed by either side; callable/
  instance/other binding shapes unless provably identical targets.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: user accepted closure on measured gains ("yeah you measured
  gains close it up", 2026-06-13); validation green, objective met within boundary.

## Steps / Checklist
- [ ] Verify finder's `_resolve_call_target` signatures the same object as the
      profile's `inspect.signature(cls)` for class spells.
- [ ] Stash Signature object on ClassBindingProfile (slot + cleanup).
- [ ] Finder reuses stashed object when available; fallback computes fresh.
- [ ] Document each meaningful finding immediately in `## Notes`.

## Validation
- Not run. Recommended:
  - `.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook -q`
  - `.venv_new\Scripts\python.exe benchmarks\testing_other_di\profile_bind_conjure_cycle.py`

## Risks / Rollback Notes
- Signature objects are immutable -> thread-safe sharing; lifecycle owned by the
  profile (cleanup dels the slot). Fallback keeps all non-class shapes untouched.

## Applicable Anti-Patterns
- [ ] No implementation from UNKNOWN: target-identity must be verified first.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Note focus: tactical findings, concrete impacts, single-step continuation.

## Notes
- DATETIME: 2026-06-13T00:55:00Z
  TYPE: FACT
  CLAIM: Bind profile shows `inspect.signature` 58x / 29 binds: once in
    `_build_class_profile` (v4 `init_signature`) and once in the requirements finder;
    combined ~1/3 of bind cost. Warm conjure has zero inspect calls (borrow working),
    so this is the last reflection duplication in the pipeline.
  EVIDENCE:
  - benchmarks/testing_other_di/bind_conjure_cycle_profile.txt:1-1
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:96-100
  IMPACT: ~0.5-1ms off bind's 3.2ms once shared.
  NEXT: verify finder's signature target identity for class spells before edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T01:10:00Z
  TYPE: FACT
  CLAIM: Implemented. Verified first that `_resolve_call_target` returns the class
    object itself for class spells, so the finder's `inspect.signature(call_target)`
    and the profile's `inspect.signature(cls)` are the same computation. Profile now
    stashes the Signature object (`init_signature_object` slot, cleanup del); the
    finder borrows it via `_borrow_bind_time_signature` under the identity guard
    `binding_profile.original_object is call_target`, with fresh-compute fallback for
    every other shape (callables, stubs, cleaned profiles). Signature objects are
    immutable -> thread-safe sharing, profile retains sole ownership.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:299-325
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:96-102
  IMPACT: class-spell signature constructions per bind: 2 -> 1 (58 -> ~29 per
    29-bind pass); expected ~0.5-1ms off bind median.
  NEXT: user validation: spellbook suites + cycle benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T01:30:00Z
  TYPE: MEASURE
  CLAIM: Validated: 2,010 spellbook unit tests green; bind median 3.19 -> 2.71ms warm
    (2.63 disabled / 2.81 cold), ~-0.5ms across every posture as predicted. Warm setup
    8.29ms. Slowest single bind now 0.169ms (was 0.30ms at session start).
  EVIDENCE:
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:97-98
  IMPACT: bind session total 4.5 -> 2.7ms (-40%); the bind->phase-11 pipeline now
    computes every reflection-derived fact exactly once.
  NEXT: acceptance confirmation from user, then closure + board sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Small follow-up tranche under compiler_strategy_0. Direction: profile stashes the
Signature object; finder borrows with fallback. Verify target identity first.
