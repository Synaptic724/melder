# Story: Harvest-driven regeneration - feed the profile into the phase cycle and rebuild the executor through it

## Metadata
- Story ID: STORY-2026-09-28-harvest-driven-phase-regeneration
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-28T00:18:56Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want a harvested profile to be handed into the compiler's phase cycle on a
revalidation, so that the planner (phase 10) and the codegen creation step (phase 11) see what the runtime
measured, choose the profiled style, emit the specialized executor, and the existing rebuild machinery
publishes it - the second part of PGO: the harvest is the first, this is how it becomes code.

## Value / MRP Alignment
This is the part that makes the whole thing real, and it runs on rails Melder already has. A spell already
carries a per-spell rebuild path: `resolution_required` makes the next meld run exactly one deferred 8-11 pass
under the rebuild window and the spell lock, both the dynamic admitted lane and the automatic cold lane call
it, and phases 10 and 11 are discovery-driven with a first-class `candidate_codegen_style_ids` list that phase
11 selects from. So 'pass the profile into the cycle' is: put the profile where phase 10 and 11 discovery can
read it, mark the spell for the deferred pass with a PGO reason, and let the rebuild window publish the
result. No new pipeline, no second compiler.

## Ticket Contract
- ENTRY_GATE: owner's pick; the harvester story defines the profile and the cycle-end call; patch docs
  (architecture: harvest-driven regeneration; component: SpellCompiler and Validation Pipeline (phases 8-11,
  planner and codegen discovery), Meld Resolution Runtime (regeneration trigger), Binding Pipeline (Spell
  profile slot); code description: trigger, deferred pass, publication ordering) before src.
- EXECUTION_BOUNDARY: `spell.py` (the profile slot and a PGO regeneration verb), `meld.py` /
  `conduit_meld.py` / `spellspace_meld.py` only where the existing trigger is read (no new door logic),
  `spellbook_creation_system.py` deferred 8-11 entry, `spell_compiler_artifact.py` (profile carried on the
  artifact), `codegen_planner/` discovery (profiled candidate styles), `codegen_creation_system/` discovery
  (profiled selection), the family strategies that emit the chosen style, `spell_state_change_reason.py` (a
  PGO reason), tests.
- DEPENDENCIES: STORY-2026-09-27-pgo-harvester-cycle-and-emission (the profile and the cycle end);
  STORY-2026-09-27-probe-selected-codegen-styles (the first profiled style); melder_0's claimed meld doors
  stay untouched until its lane closes.
- EXIT_GATE: a harvested spell's next meld runs one deferred 8-11 pass that emits the profiled style and
  publishes it through the existing window; phases 1-7 do not rerun; automatic and dynamic worlds both
  regenerate; PGO off is byte-identical; differential and deopt matrices green; measured on the VM and
  owner-run.
- FAILURE_ESCALATION: DECISION_REQUEST on whether the regeneration pass is 8-11 or a narrower 10-11 pass;
  BLOCKER if automatic worlds cannot be regenerated without marking the lineage structurally gated.

## Requirements (Functional)
- Two trigger paths to one flag: (a) inside the context at cycle end when PGO is on (the context holds its
  spell); (b) a system verb - harvest now and regenerate one spell, or every spell holding a profile, lazily
  on each spell's next meld or eagerly under the rebuild window (the all-spells shape to be settled).
- Trigger: at cycle end the harvester stores the profile on the spell and requests regeneration - the
  deferred pass only (`resolution_required=True`, a door-epoch bump so warm entries fall to the cold lane),
  with a new `SpellStateChangeReason` (for example `pgo_profile_harvested`) so the report answers 'what just
  happened'; it must not mark the lineage structurally gated (that would rerun phases 1-4) and must work in
  automatic worlds, unlike `invalidate_spell`, which is dynamic-only today.
- Carrier: the profile reaches phase 10 and 11 discovery through the `SpellCompilerArtifact` (read from the
  spell at the start of the deferred pass) so the phases stay pure functions of their inputs.
- Phase 10: planner discovery derives candidate codegen style ids from the profile (profiled styles first,
  plain last) and records the profile hash in the plan metadata.
- Phase 11: codegen discovery selects the profiled style; the family strategies emit it; the plan metadata
  names the style and the profile hash it was built from.
- Publication: the rebuilt context is published by the existing path (rebuild window under dynamic
  ownership; the cold lane's build under automatic ownership) and starts in the regenerated version; the
  guard/deopt contract of the versioning story applies.
- Capture: the conjure-end cache capture records the selected style so a warm conjure hydrates it (hand-off
  to the persisted-profiles story).

## Requirements (Non-Functional)
- The regeneration pass is one deferred pass per harvest; no phase 1-7 work; measured cost of the pass
  recorded per family.
- PGO off: no profile exists, discovery behaves exactly as today (plain candidates), the pass is never
  requested.
- Overlay rules; every touched phase, discovery strategy and verb documented; the component map's phase
  table updated.

## Scope Boundaries
- In scope: the trigger verb, the reason, the artifact carrier, planner and codegen discovery inputs, the
  deferred pass, publication, capture hand-off, tests, docs.
- Out of scope: the probe body, the profile schema (harvester story), what each style emits (style stories),
  cross-process persistence beyond the capture hand-off.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's direction (2026-09-28T00:18:56Z); opens when the owner picks it.

## Dependencies / Related Work
- src/melder/aether/conduit/meld/meld.py:826-891 (`_execute_admitted`: every admitted dynamic meld re-checks
  `resolution_required` and runs the deferred path)
- src/melder/aether/conduit/meld/meld.py:966-1020 (`_ensure_runtime_resolution_ready`: exactly one deferred
  8-11 pass under the rebuild window and `spell._lock`)
- src/melder/aether/conduit/meld/conduit_meld.py:551-555 (the automatic cold lane calls the same two gates)
- src/melder/aether/spellbook/spellbook.py:7189-7222 (`_run_deferred_resolution_phases_for_target_spell`)
- src/melder/aether/spellbook/spell.py:1353-1420 (`invalidate_spell`: clears the context, sets
  `resolution_required`, marks the lineage; dynamic-only)
- src/melder/aether/spellbook/spell.py:690-722 (`_cleanup_creation_context` bumps `_door_epoch` before
  teardown)
- src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:60-145 (phase 10:
  discovery -> `candidate_codegen_style_ids`, strategy apply)
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:60-126
  (phase 11: discovery selects `selected_codegen_style_id`, strategies emit)
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strat
  egies/generalized_codegen_creation_discovery_strategy.py:60-100 (today: the first candidate wins)
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_state_change_reason.py:40-99 (the
  reason vocabulary)
- STORY-2026-09-27-pgo-harvester-cycle-and-emission; STORY-2026-09-27-creation-context-versioning;
  STORY-2026-09-27-probe-selected-codegen-styles

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (the regenerated context is what the
      deferred pass publishes) and in the phase cycle: read phases 8-11 whole, the deferred-pass orchestration in
      `SpellbookCreationSystem`, the artifact, and both discovery systems; decide 8-11 vs 10-11; patch docs.
- [ ] Task: the trigger - a PGO regeneration verb on `Spell` for both ownership modes, the change reason, tests
      that phases 1-7 do not rerun.
- [ ] Task: the carrier and the discovery inputs - profile on the artifact, profiled candidate styles in phase 10,
      profiled selection in phase 11, plan metadata; tests over the generalized and many_only families.
- [ ] Task: end to end - harvest -> trigger -> deferred pass -> publication -> capture, in a dynamic world with
      two conduits and in an automatic world; differential and deopt matrices; VM measurement; owner-run gauntlet.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- After a harvest, the next meld of the spell runs one deferred pass, the plan metadata names the profiled
  style and profile hash, the published context runs it, phases 1-7 are not rerun, and both ownership modes
  behave the same; PGO off matches today byte for byte.

## Validation / Test Plan
- Unit tests on the trigger verb and the discovery inputs; component tests on the deferred pass in both
  modes with phase-run assertions; the differential matrix; the deopt matrix; VM cost of the pass per
  family; owner-run gauntlet.

## UX / API / Data Notes
- No public API change; the report shows the reason, the style and the profile hash per spell.

## Risks / Mitigations
- The deferred pass reruns more than needed -> measure 8-11 vs a 10-11 pass on the retained artifact; pick
  by cost.
- Automatic worlds have no rebuild window -> the epoch bump routes warm melds to the cold lane, which
  already builds under the spell's switch; verified by tests with concurrent melds.
- A regeneration storm (every spell at once) -> one pass per harvest, harvests staggered by their own
  windows.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- 8-11 or 10-11: does the artifact retain the phase-8/9 model between passes so a narrower pass is possible?
- Profile on the artifact only for the pass, or also kept on the spell for the report and persistence?
- Should the trigger wait for a natural window in automatic worlds, or fire at cycle end as in dynamic ones?

## Decision Log
- 2026-09-28T00:18:56Z (owner): the second part - harvest the data upon revalidation and pass it into the
  cycle of phases 1-11 so the phases actually consume the harvest; this should work well. fable_0: from
  source it is phases 8-11 (10 and 11 are the consumers; 1-7 are structural and must not rerun), and the
  deferred per-spell pass and the discovery hooks already exist.

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
  - deferred 8-11 pass; planner discovery; codegen discovery; regeneration trigger; publication
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-28T00:18:56Z
  TYPE: FACT
  CLAIM: The regeneration seam exists: `resolution_required` makes the next meld run exactly one deferred 8-11
    pass under the rebuild window and the spell lock (`_ensure_runtime_resolution_ready`), the dynamic admitted
    lane re-checks it per meld and the automatic cold lane calls the same gate; phase 10's planner records
    `candidate_codegen_style_ids` from its discovery and phase 11's discovery selects
    `selected_codegen_style_id` (today: the first candidate) before the family strategies emit. `invalidate_spell`
    is the existing whole-spell trigger but it is dynamic-only and marks the lineage structurally gated, so PGO
    needs its own lighter verb.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:826-891
  - src/melder/aether/conduit/meld/meld.py:966-1020
  - src/melder/aether/conduit/meld/conduit_meld.py:551-555
  - src/melder/aether/spellbook/spell.py:1353-1420
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:60-145
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:60-126
  IMPACT: The profile enters the cycle as a discovery input plus a trigger; no new pipeline.
  NEXT: owner picks; the investigation task settles 8-11 vs 10-11 and the automatic-world trigger.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T00:28:44Z
  TYPE: FACT
  CLAIM: Owner's questions answered from source. (1) The context DOES hold its spell: `CreationContext.__init__`
    stores `self._spell = spell` and `self._spell_id` (cleaned in `cleanup`), so a trigger from inside the context
    is one attribute write away: `self._spell.resolution_required = True` plus a `_door_epoch` bump - the
    deferred pass, not `invalidate_spell`. (2) The deferred pass is exactly the four target-local phases
    registered by `_run_target_plan_resolution_phases`: occurrence_plan_local (8), injection_plan_local (9),
    patch_maps_local (10), execution_plan_local (11) - nothing from 1-7. (3) Phase 8 is `CompilerPhase8.run` ->
    `SpellAnalyzer.analyze_occurrence(spell, artifact)`, a strategy chain of one id today
    (`spell_occurrence_graph_analyzer`) that reads through the spell/artifact pair and publishes
    `artifact._occurrence_graph_analysis`; a second strategy in that chain reading the spell's profile is where
    "extra data at phase 8" enters, for 9 (model), 10 (plan, candidate styles) and 11 (emission) to consume.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:104-172
  - src/melder/aether/spellbook/spellbook_creation_system.py:1757-1830
  - src/melder/aether/spellbook/spellbook_creation_system.py:2386-2420
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:74-123
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:110-137
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:66-143
  IMPACT: Both triggers the owner asked for are the same flag set from two places: inside the context at cycle
    end (optional, PGO on) and from a system verb (per spell, or every spell with a profile - lazy on next meld,
    or eager under the rebuild window). The extra data rides the artifact from phase 8 on.
  NEXT: owner picks; the investigation task measures the four-phase pass per family and settles lazy vs eager
    for the all-spells verb.
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
STATE 2026-09-28T00:18:56Z: DRAFT. The second part of PGO, drafted from the owner's direction with the seam
located in source; not routed. Opens when the owner picks it.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
