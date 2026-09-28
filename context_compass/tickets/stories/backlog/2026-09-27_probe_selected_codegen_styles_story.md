# Story: Probe-selected codegen styles - a probing creation context, a profile report, styles chosen by measurement

## Metadata
- Story ID: STORY-2026-09-27-probe-selected-codegen-styles
- Epic: EPIC-2026-09-27-adaptive-creation-contexts (moved from EPIC-2026-09-27-codegen-pgo-strategies, superseded)
- Status: blocked
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T22:44:20Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want a switch that turns optimization on, a probing creation context that times and maps
the node structure a conduit actually builds (per-site hits and misses, per-site and constructor times) and emits
that to a core area (the DevOps station, and the spell), and a selection step that, once enough data is gathered,
restructures the creation context per spell - trimming calls where the data says they are not needed - so that
DI-heavy applications (wide singleton consumers, deep transient trees) gain another 10-15% per creation on top of
the door fold, while the plain body and the default-off path stay byte-identical.

## Value / MRP Alignment
The mechanism exists in embryo: self-replacing executor slots, the opt-in singleton specializer (one style),
rebuild windows, per-key-set plans, a DevOps information registry. What is missing is the data (a probe), the
report, and the selection, so a style is swapped in only where it measured a win - the blind specializer showed
-14% on a wide singleton consumer and +20% on a chain. The MRP is: probe off = today; probe on = a bounded,
sampled cost; selection = never a regression the probe could see.

## Ticket Contract
- ENTRY_GATE: the epic; this row on `attention_board.md`; the owner's direction (2026-09-27, "a tool where we can
  turn on optimization, time and map out node structures from the conduit, emit that to a core area, optimize
  around it, a probing_creation_context that logs and stores it, maybe on the spell").
- EXECUTION_BOUNDARY: `spell_compiler/codegen_creation_system/` (emitters, hydrators, strategies), the creation
  context and factory, `Spell` (profile slot), the DevOps station (report surface), `SpellbookConfiguration`
  (switches), tests; nothing in the meld doors beyond what a style swap already uses; melder_0's claimed files
  are not touched without the mailbox.
- DEPENDENCIES: the closed exploration story's measurements; patch docs per task (system-impacting).
- EXIT_GATE: the switch, the probe body with a measured, bounded overhead, the report readable from the DevOps
  station and the spell, at least one style selected by measured delta with a differential and deopt test
  matrix, suites green, a measured win on a DI-heavy shape; default-off path byte-identical.
- FAILURE_ESCALATION: DECISION_REQUEST when a style's guard cost exceeds its saving on the probe's own numbers;
  BLOCKER if the probe cannot be made cheap enough to sample (target: under 2% of a creation, amortized).

## Requirements (Functional)
- Switch(es) on the configuration: profiling on/off, optimization on/off, sample window size.
- Probe style: the plain body instrumented per site (hit/miss, ns) and per constructor (ns), with a call count;
  the probe body swaps itself out for the plain body after its window (self-replacing slot contract).
- Profile store: a value-only record on the spell (and per conduit where the door differs) plus a DevOps report
  listing, per spell: sites, kinds, hit rates, ns per site, ns per creation, the selected style and its measured
  delta.
- Selection: a priority queue over (spell, style) by measured expected saving x call rate; candidates: plain,
  singleton-capture (the existing specializer), transient-inlining (new emitter); applied at a natural window;
  a style that measures no win is not applied; a style that deopts three times returns to plain (as today).
- Tool surface: a way to read the report (conduit/spellbook describe verb or the DevOps station), and to reset.

## Requirements (Non-Functional)
- Default-off path byte-identical to today; probe overhead bounded and sampled; every style guarded with a
  deopt to the plain body; overlay rules (`Optional`/`Union`, no `getattr`/`hasattr` on owned code, rich
  docstrings); VM numbers directional, owner-run gauntlet decides.

## Scope Boundaries
- In scope: the probe, the store, the report, the selection, the transient-inlining style, tests, docs.
- Out of scope: persistence of profiles across processes (later, if ever); Crystallizer/Nexus surfaces; API
  shape changes to `meld`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner's direction (2026-09-27T22:44:20Z); the design task opens first.

## Dependencies / Related Work
- tickets/stories/completed/2026-09-27_pgo_strategy_exploration_story.md (measurements; specializer numbers)
- tickets/tasks/completed/2026-09-27_meld_entry_cache_by_name_and_class_task.md (the door fold)
- artifacts/pgo_strategies_20260927/ (all runs)

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK-2026-09-27-probe-creation-context-design - read the emitters, hydrators, context factory and the
      DevOps station; design the probe body, the profile store, the report and the selection; prototype the
      probe in the experiment harness and measure its overhead; patch docs. tickets/tasks/backlog/2026-09-27_probe_creation_context_design_task.md
- [ ] Task: probe style + switches + store + report (implementation, tests).
- [ ] Task: selection + singleton-capture wiring by measured delta (tests, deopt matrix).
- [x] Task: transient-inlining style - RETIRED 2026-09-27T23:49:25Z: already the emitted shape; consumer
      specialization is its own story under the new epic.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Switch off: byte-identical behaviour and timing. Switch on: the report shows the node structure and timings of
  what a conduit built; at least one style is applied only where it measured a win; the differential/deopt
  matrix is green; a DI-heavy shape gains on the VM and, owner-run, on the gauntlet.

## Validation / Test Plan
- Unit-first on the emitters and the selection policy; component tests on the probe window swap and the report;
  the differential matrix (plain vs each style, same objects, same errors); the deopt matrix (purge, cleanup,
  transfer, notch where dynamic); the experiment harness with a DI-heavy shape set.

## UX / API / Data Notes
- Switches on `SpellbookConfiguration`; the report through the DevOps station and a describe verb; the profile
  record is value-only (JSON-able) so it can ride a crystal later if wanted.

## Risks / Mitigations
- Probe cost eats the win -> sampled window, then self-swap to plain; measured before anything else.
- A style regresses (chain8) -> selection by measured delta only; three deopts re-pin plain.
- Stale style after a structural change -> the existing epoch/context guards and rebuild windows; a rebuilt
  context starts plain and re-probes.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No style applied blind; no probe that runs unsampled on the warm path.

## Open Questions
- Profile granularity: per spell, or per (spell, conduit) where the route differs? Probably per spell with the
  route key in the record.
- Where the profile lives: on the spell (value-only) and mirrored into the DevOps registry, or registry only.
- The owner's "trim calls in one direction and support the other": to be pinned down with the owner (read
  as:
  optimize the creation direction, keep disposal/purge/transfer semantics intact).

## Decision Log
- 2026-09-27T22:44:20Z (owner): the direction - a switch, a probing creation context that times and maps node
  structures,
  emitted to a core area, styles selected by measured data; Melder's own narrow composition is not the target
  (Melder does not use DI internally); user shapes are.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (prior runs; new probe runs land here)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps as the styles ship.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - probing creation context; profile store; DevOps report; style selection; transient inlining
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T22:44:20Z
  TYPE: PLAN
  CLAIM: Order: design task first (reads + probe prototype + overhead number + patch docs), then the probe/report
    task, then selection with the existing specializer as the first style, then the transient-inlining style.
    Known from the closed story: 16 ns per singleton site recoverable, ~20 ns per transient frame, the
    specializer's swap/deopt lifecycle, the self-replacing slot contract, and that timing a site costs more than
    the site (so the probe samples a window and swaps itself out).
  EVIDENCE:
  - tickets/stories/completed/2026-09-27_pgo_strategy_exploration_story.md:200-300
  - artifacts/pgo_strategies_20260927/vm_opt_in_specializer_by_name_gil0_20260927.md
  IMPACT: The first task decides the shape of everything after it.
  NEXT: open the design task and read `site_plan_lowering.py` emission, the hydrators and the DevOps registry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T23:49:25Z
  TYPE: DECISION
  CLAIM: Owner direction (23:42Z): an epic and one story per idea. This story moves under
    EPIC-2026-09-27-adaptive-creation-contexts as the "styles selected by data" story; the probe body, the creator
    capture, the report, the versioning and the transient-inlining/consumer specialization each got their own story
    there, so this one narrows to selection + the singleton-capture style (today's specializer made data-driven).
    Its task list is revised at opening; the design task keeps its proof and stays the active lane.
  EVIDENCE:
  - tickets/epics/backlog/2026-09-27_adaptive_creation_contexts_epic.md:1-120
  - tickets/tasks/backlog/2026-09-27_probe_creation_context_design_task.md:250-360
  IMPACT: No duplicate scope across the ten stories; the fourth task ("transient-inlining style") is retired here
    because that is already the emitted shape (design task FACT 22:49:38Z).
  NEXT: owner picks the first story to open.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:47:00Z
  TYPE: HYPOTHESIS
  CLAIM: Why the blind specializer lost 20% on chain8: it is emitted by a different, older emitter. The plain
    normal plan is the flat site-plan lowering (one function per root, `SitePlanOverrideRuntime`, 2026-09-26);
    `build_specialized_no_overrides_executor` lives in the manifest-step compiler
    (`generalized_manifest_no_overrides_compiler.py`), which never references the site-plan lowering and emits
    per-step `creations_i` aliases, generic `_construct_spell_instance` calls and per-site epoch guards
    (`spell._door_epoch` compare, captured epoch-before-instance). So capture today trades a 23 ns store read for
    a ~15 ns epoch read PLUS a body that lost the lowering's flattening - the regression is the emitter, not
    the idea. The singleton-capture style this story owns must be a per-site variant INSIDE the site-plan
    lowering (guarded constant in place of the read), which makes it a deterministic ~8-16 ns per site win.
    To verify: diff the two emitted bodies for chain8_singleton and wide8_singleton in the harness.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:1376-1470
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:557-758
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:364-420
  - artifacts/pgo_strategies_20260927/vm_opt_in_specializer_by_name_gil0_20260927.md
  IMPACT: Removes the one counter-example to "strategies are deterministically helpful": once capture is emitted
    inside the lowering, the style needs no per-spell timing, only its precondition (all captured sites unique or
    existing objects, hit rate 100% over the window).
  NEXT: the investigation task diffs the bodies and prices the guarded constant inside the lowering.
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
STATE 2026-09-27T22:44:20Z: IN_PROGRESS. Opened on the owner's direction; the design task is first. Resume from
the task's latest STATE line.
STATE 2026-09-27T23:49:25Z: IN_PROGRESS. Moved under the adaptive-creation-contexts epic; scope narrowed to
data-selected styles (singleton capture first). Resume from the design task's latest STATE line.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
