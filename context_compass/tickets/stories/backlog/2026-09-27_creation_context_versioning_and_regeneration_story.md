# Story: Creation context versioning and regeneration - emit a new version from the profile, swap it in, deopt to plain

## Metadata
- Story ID: STORY-2026-09-27-creation-context-versioning
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want a spell's creation context to carry versions - plain, probe, and specialized
bodies emitted from the harvested profile - with a regeneration step that emits the next version and swaps it
in at a natural window, guarded, and a deopt that returns to plain, so that the runtime puts out faster code
for the shapes it has seen, the thing a fixed provider cannot do.

## Value / MRP Alignment
The mechanism every optimizing story plugs into. The self-replacing slots, the specializer's swap and three-
miss deopt, the rebuild windows and the natural windows (pool return, reset, warm conjure) already exist; this
story makes them one contract with a version key and a history the report can show.

## Ticket Contract
- ENTRY_GATE: owner's pick; patch docs (architecture: version lifecycle and swap windows; component: Meld
  Resolution Runtime, SpellCompiler codegen strategies; code description: swap and deopt) before src.
- EXECUTION_BOUNDARY: `creation_context.py` (version slots and history), the hydrators' publish points, the
  specializer's swap/deopt path generalized, the natural windows as swap points, tests.
- DEPENDENCIES: STORY-2026-09-27-probe-creation-context-harvest (the profile); a first style to regenerate
  (the styles story).
- EXIT_GATE: a version swapped in at a natural window on a measured win, deopting to plain on guard failure
  or three misses; history visible; differential and deopt matrices green; default off byte-identical.
- FAILURE_ESCALATION: BLOCKER if a swap cannot be proven safe against purge, transfer, notch, cleanup and
  pool return; DECISION_REQUEST on the version key vocabulary.

## Requirements (Functional)
- Version key per emitted body: plain, probe, `<style>@<profile hash>`.
- Tournament (owner, 2026-09-28): regeneration tries 3-5 candidate versions (plain always among them), runs
  one timed window each, keeps the best by median ns per creation when it clears the margin over plain.
- Attempt budget (owner, 2026-09-28): the spell logs the attempt count and the best measured ns; the count
  rides the manifest so hydration restores it, and a spell that spent its budget is left alone until its
  shape changes; the context logs each version's measured window into the spell.
- Regenerate: emit the next version from the profile through the existing family hydrators; publish through
  the self-replacing slot at a natural window or inside a rebuild window.
- Guard and deopt: the existing epoch/context guards; three misses re-pin plain (as the specializer does
  today).
- History: the last N versions with their measured delta, value-only, for the report.

## Requirements (Non-Functional)
- Swaps never under a meld holding a build lock; never on the warm path of another thread.
- Default off: only the plain version exists and nothing else is emitted.

## Scope Boundaries
- In scope: the version contract, the swap points, the history, tests, docs.
- Out of scope: which styles exist (their stories); persistence (its story).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.

## Dependencies / Related Work
- Self-replacing slots: src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110
- Specializer swap and deopt: src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/
  generalized/hydration/generalized_hydrator.py:600-758
- src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK design the version contract, the swap points and the history; patch docs.
- [ ] Task: TASK implement versions and the generalized swap/deopt; differential and deopt matrices.
- [ ] Task: TASK measure swap cost and the first regenerated version on the VM; owner-run gauntlet.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A spell with a harvested profile gets a regenerated version at the next natural window, measured faster on
  the shape that earned it, and returns to plain on a forced guard failure; the report shows the history.

## Validation / Test Plan
- Component tests on swap timing and deopt; the differential matrix; the deopt matrix (purge, cleanup,
  transfer, notch, pool return); VM and owner-run runs.

## UX / API / Data Notes
- No public API change; version keys visible through the report only.

## Risks / Mitigations
- Regeneration thrash -> hysteresis and one regeneration per window.
- A stale version after a structural change -> a rebuilt context starts plain.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Is regeneration synchronous on the building thread at the window, or deferred to the next natural window?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Collected from the owner's
  direction (modify the creation context and put out a new version).

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
  - versions; swap windows; deopt; history
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: FACT
  CLAIM: Executor slots are self-replacing (cold -> hot -> specialized) and the specializer swaps hot ->
    specialized on a later call with `_deopt_notify` re-pinning plain after 3 misses; holding an executor
    reference pins the cold door.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:600-758
  IMPACT: The version contract generalizes an existing path rather than adding a second one.
  NEXT: owner picks; then the design task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-28T00:33:12Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: Owner (00:3xZ): regenerate the spell from the creation context directly, unbind and rebind it while the
    gate is closed, then try 3-5 candidates and keep the best. Challenge, from source: unbind/rebind is the wrong
    primitive - `cleanup_and_remove_spell` unregisters the index from SpellSystemStates, removes the pool maps and
    cleans the Spell and SpellIndex (spellbook.py:591-640), and a bind after conjure is refused outright in
    automatic worlds ("Bind is disabled after conjure for the current frame posture", spellbook.py:5266-5273);
    in dynamic worlds it reruns phases 1-4 and mints a new index member. The regeneration we want keeps the
    Spell and its stored creations and replaces only the executors: the deferred 8-11 pass, run under
    `CreationContextRebuild` (the gate frozen and drained before the plan is touched, the rebuilt context
    published before it reopens - creation_context_rebuild.py:1-60) in dynamic worlds, under the spell's
    build switch on the cold lane in automatic worlds. "From the context directly": the context holds its spell
    and sets the flag; the next meld, which knows its conduit id, runs the pass - a synchronous
    `context.regenerate()` would need a conduit id the shared dynamic context does not own.
    ACCEPTED: the trial loop. Regeneration becomes a tournament: candidates = plain + the profiled styles (3-5),
    each emitted, run for one timed window, scored by median ns per creation; the best is kept, plain is always
    a candidate so the result cannot regress, and a win must clear a margin (>= 3%, to settle) over plain.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:591-640
  - src/melder/aether/spellbook/spellbook.py:5266-5273
  - src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:1-60
  - src/melder/aether/conduit/meld/meld.py:966-1020
  - artifacts/pgo_strategies_20260927/vm_opt_in_specializer_by_name_gil0_20260927.md
  IMPACT: The story's regeneration step gains a tournament requirement; unbind/rebind is recorded as rejected
    with the reasons so it is not re-proposed.
  NEXT: owner picks; the investigation task prices one trial (pass + timed window) per family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T00:47:00Z
  TYPE: DECISION
  CLAIM: Owner (00:4xZ): maybe no time at all - the things we remove are deterministically helpful; the strategies
    do the trick, and new optimizations become new strategies. Adopted as the default: a strategy is CERTIFIED
    once, at development time, by owner-run measurement on the target interpreter (it strictly removes work on
    the same emitter, or its guard is cheaper than what it replaces), carries a PRECONDITION the profile can
    check (hit rate, creator threads, door, disposal), and is applied at regeneration without a runtime timing
    window. The tournament becomes an opt-in verification mode (report only), and "attempts" reduce to "applied
    once per shape". Certified today: registration trim (fewer operations, same lock). Not yet: singleton
    capture (its emitter differs - see the styles story), thread-affine append (guard cost unmeasured),
    door specialization (per-door versions carry no guard; unmeasured). Certification is per interpreter
    version: a strategy proven on 3.14t is re-run when the floor moves.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
  - artifacts/pgo_strategies_20260927/vm_opt_in_specializer_by_name_gil0_20260927.md
  - tickets/stories/backlog/2026-09-27_probe_selected_codegen_styles_story.md:180-230
  IMPACT: No per-spell timing on the warm path; the count-only probe supplies the preconditions; the guard and
    deopt contract still protects a precondition that stops holding.
  NEXT: owner picks the first story; the versioning task list drops the tournament to opt-in at opening.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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
STATE 2026-09-27T23:42:45Z: DRAFT. Collected from the owner's direction; not routed. Opens when the owner
picks it; its first
task is the measurement plan and the patch docs.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
