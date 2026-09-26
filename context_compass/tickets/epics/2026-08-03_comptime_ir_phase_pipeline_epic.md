# Epic: Move compiler phases 1-10 onto a value-only IR and make phase 11 the sole hydration boundary

## Metadata
- Epic ID: EPIC-2026-08-03-comptime-ir-phase-pipeline
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-08-03T01:45:00Z
- Updated: 2026-09-26T18:13:08Z
- Target Window: claimed 2026-09-25; STORY-1 survey is the active lane
- Related Program/Initiative: SpellCompiler / Crystallizer / MutationResearch

## Problem / Opportunity

The conjure pipeline is a compiler. It runs requirements finding, symbolic graph
construction, local frame resolution, validation, root blueprints, system
validation, change control, occurrence analysis, injection processing, patch
maps and execution planning, and then EMITS an executor at phase 11 which the
runtime dispatches into. One file per phase exists on disk.

EVIDENCE:
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py
- context_compass/system_docs/src_architecture.md:628-640
- context_compass/system_docs/src_architecture.md:641-651

The compiler's intermediate state is carried in LIVE RUNTIME OBJECTS rather than
in a symbolic representation. Owner statement, 2026-08-03: phases 1-7 use "real
objects" where an IR of strings/values would represent the same structure and be
managed through explicit hydration targets instead of intrinsic object identity.
Owner refined the boundary in the same exchange: **phases 1-10 could use the IR
entirely, and phase 11 computes the rest.**

Four consequences follow from having no IR, and only the first is the one
usually noticed:

1. **The compiler cannot run without the runtime.** Compile-time state and
   runtime state are the same objects, so the phases cannot be exercised,
   tested, or reasoned about in isolation from a live world.
2. **The plan is not an artifact.** It exists only as object graph and
   evaporates. The Crystallizer records source and structure; MutationResearch
   diffs source and structure; NEITHER can see the compiled plan, because there
   is nothing to record.
3. **Restore recompiles from scratch.** A restored world re-runs the phase
   pipeline rather than rehydrating a plan it already computed once. Bulk graph
   construction is the one path where Melder's per-object cost is user-visible
   (see Constraints).
4. **Incremental recompile is hard to make correct.** Change control marks roots
   dirty and triggers revalidation; without a hashable plan there is no cheap
   way to decide what actually needs rebuilding.

## MRP Alignment (Most Reasonable Product)

This is foundational, not additive. `mrp_policy.md` defines MRP as the smallest
product coherent and durable enough that shipping it does not create a trap, and
says explicitly: if the core would need rework immediately after release to
become trustworthy, it is not MRP yet.

The phase pipeline is the core. Every capability layered above it - crystallizer
restore, MutationResearch diffing, codegen, agent-driven structural evolution -
reads or rebuilds compiler state. Doing this after those consumers harden means
retrofitting an IR under live dependents. Doing it now means they are built
against the IR from the start.

There is also an existing standard this lands on rather than inventing: the
project's own dataclass rule already describes an IR node. `init_and_ownership.md`
and `banned_patterns.md` restrict dataclasses to value types - `None`, `bool`,
`int`, `float`, `str` - and forbid storing object instances or resources in
them. An IR built from those dataclasses is compliant by construction, and any
node that cannot be expressed that way is a node still holding a live object.

## Ticket Contract

- ENTRY_GATE: this epic is routed from `attention_board.md`; STORY-1 (phase
  survey) is complete and its findings are recorded before any other story
  opens. No design work proceeds on architecture-doc evidence alone.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/spell_compiler/**` and the
  Spellbook conjure call sites that drive it. Crystallizer and MutationResearch
  integration are SEPARATE downstream stories and are out of the first tranche.
- DEPENDENCIES:
  - `agent_onboarding/default/engineer/skills/patch_framework_gating.md`
    (system-impacting: patch docs required before implementation)
  - `system_docs/src_architecture.md`, `system_docs/src_components.md`
  - `agent_onboarding/user_defined/synaptic_python_developer/skills/python/init_and_ownership.md`
- EXIT_GATE: every required story accepted by the owner; both canonical system
  documents updated with the IR boundary and their `*_index.md` regenerated in
  the same pass; gauntlet regression gate green (see Validation).
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the IR cannot express a phase
  without holding an object reference. Raise `CONFLICT` if any IR symbol is
  found reachable from the meld hot path. Raise `BLOCKER` if a phase's current
  behavior cannot be established from source.

## Goals (Outcomes)

- Phases 1-10 operate exclusively on a value-only, serializable IR.
- Phase 11 is the ONLY hydration boundary: it consumes IR and emits the executor.
- The compiled plan becomes a durable, hashable, diffable artifact.
- Compile-time and runtime state are separable, so the phases can be tested
  without a live world.

## Non-Goals (Explicit Exclusions)

- **Meld throughput is not a goal.** Per-object cost is CPython's object model,
  not resolution overhead; the 3.15 JIT result measured +0.22% on this workload,
  which rules out interpreter dispatch as the constraint. Expect no meld speedup
  and do not justify this epic on one.
- No public API change to `Spellbook`, `Conduit`, or `Existence`.
- No change to the emitted executor's runtime semantics.
- Crystallizer plan persistence and MutationResearch plan-grain diffing are
  DOWNSTREAM: enabled by this epic, delivered by their own tickets.

## Scope Boundaries

- In scope: phase modules 1-10, the artifacts they exchange, the phase-11
  hydration boundary, the IR schema and its versioning.
- Out of scope: `meld` and the runtime lane, `Creations`, `ConduitWard`,
  persistence formats, MR diff strategies.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner directed the epic be authored and placed on the board
  unclaimed (2026-08-03). Scope boundary is owner-ruled (1-10 IR, 11 computes
  the rest). No agent has claimed it; STORY-1 is the entry point.
- from_state: ready
- to_state: in_progress
- transition_reason: Owner assigned the epic to fable_0 as the focus lane (2026-09-25); STORY-1
  opened as the entry point per the epic's own gate.

## Success Metrics

- 100% of phase 1-10 exchanged artifacts pass a value-only assertion walk.
- IR round-trip (build -> serialize -> deserialize -> hydrate) produces
  behaviorally identical resolution on the full existing test suite.
- Zero symbol lookups reachable from `meld`, demonstrated by benchmark parity
  rather than asserted.
- Recompile of an unchanged Spellbook becomes an IR-hash hit rather than a
  full phase run.

## Requirements (Functional + Non-Functional)

Functional
- IR nodes are value-only dataclasses per `init_and_ownership.md`; containers of
  value types are permitted, object references are not.
- Every IR node carries a stable symbolic id. Hydration resolves symbol -> real
  type exactly once, at phase 11.
- IR is serializable to plain JSON-compatible structures with no custom encoder.
- IR carries a version stamp consistent with the existing `RecordVersion`
  discipline for durable artifacts (`src_architecture.md:1084-1089`).
- IR is content-hashable so an unchanged plan can short-circuit recompilation.

Non-Functional
- Conjure wall time must not regress materially; if it does, the IR is being
  rebuilt where it should be memoized.
- No `getattr`/`hasattr` probing over IR nodes; the schema is owned and visible
  (`banned_patterns.md`).
- Type hints mandatory throughout; `Optional`/`Union`, never PEP 604
  (`typing.md`).

## Constraints / Assumptions

- **UNKNOWN, and this is the epic's largest risk:** the description of phases
  1-11 above is drawn from `src_architecture.md` and from the module layout on
  disk. It is evidence of INTENT and STRUCTURE, not of BEHAVIOR. No phase
  implementation has been read. `unknowns_gate_reference.md` forbids treating
  documents as evidence of behavior; STORY-1 exists to close this and nothing
  else may start first.
- Assumption to test, not to build on: each phase's inter-phase payload is
  already close to value-shaped, and the object references are incidental rather
  than load-bearing. If a phase genuinely needs identity (not just a name), the
  IR needs an explicit identity concept and that is a design decision, not an
  implementation detail.
- Where restore cost is user-visible: reconstructing large worlds. A 10M-object
  world costs seconds in Python; caching the plan removes the recompile half of
  that, not the construction half.

## Dependencies / External References

- `system_docs/src_architecture.md` - Boot and Configuration Sequence, phases
  1-11 and the conjure sequence
- `system_docs/src_components.md` - `Component: SpellCompiler and Validation
  Pipeline`, `Subcomponent: SpellCompiler Phase Artifacts` (slice via
  `src_components_index.md`)
- `agent_onboarding/default/engineer/skills/patch_framework_gating.md`

## Milestones (Track Progress)

- [x] Milestone 1: Ground truth - every phase's real inputs and outputs
      established from source, object-bound points named with file:line.
      (done 2026-09-26T13:27:19Z: survey story accepted; phases 1-7 plus the drivers and the seam; 8-11 deferred by owner)
- [ ] Milestone 2: IR schema ratified by the owner, with the identity question
      answered explicitly.
- [ ] Milestone 3: Phases 1-10 ported, existing suite green, gauntlet parity.
- [ ] Milestone 4: Phase 11 is the sole hydration boundary, proven not asserted.
- [ ] Milestone 5: IR hashing and comptime memoization landed.

Milestone status (2026-09-25): Milestone 1 in progress via STORY-1 tranche task 1 (driver plus
phases 1-4); component-map slices done, no phase source read yet. Milestones 2-5 not started.
Milestone status (2026-09-26): STORY-1 discovery steps S1-S11 executed; all three tasks and the story are in
review with nine records plus summary.md under artifacts/ir_phase_survey_20260925/. Milestone 1 is checked
on owner acceptance of summary.md (phases 8-11 deferred by the 2026-09-26 ruling). Milestones 2-5 not started.
Milestone status (2026-09-26T13:27:19Z): Milestone 1 DONE (owner turned in the survey story). The improvement-plan story
and tranche T1 are also closed. Milestones 2-5 not started; I-1 (structural snapshot) is the next implementation entry.

## Stories (Required to Complete)

- [x] Story: STORY-2026-08-03-phase-pipeline-survey - read `compiler_phase_1.py`
      through `compiler_phase_11.py` and record, per phase, what it consumes,
      what it produces, and every point where it holds a live object rather than
      a value. **Gate: no other story starts until this is accepted.**
      tickets/stories/completed/2026-09-25_ir_phase_pipeline_survey_story.md (fable_0; done
      2026-09-26T13:27:19Z: drivers, phases 1-7 and the seam; the phases 8-11 exhaustive survey is deferred)
- [x] Story: STORY-2026-09-26-phase-pipeline-improvement-plan - rank source-backed
      improvements to phases 1-11 and recommend the first tranche (opened on owner
      direction 2026-09-26). tickets/stories/completed/2026-09-26_phase_pipeline_improvement_plan_story.md
      (fable_0; done 2026-09-26T13:27:19Z: T1 chosen and shipped)
- [x] Story: STORY-2026-09-26-signature-determinism-phase8-digest - tranche T1 (C-H + C-A) as
      approved 2026-09-26; patch docs first; five tasks (two added on owner rulings).
      tickets/stories/completed/2026-09-26_signature_determinism_and_phase8_digest_story.md (fable_0;
      done 2026-09-26T13:14:31Z, owner accepted; docs promoted)
- [ ] Story: STORY-2026-09-26-structural-snapshot - I-1: a full creation-cache hit hydrates value rows
      for phases 1-7 and skips them; patch docs first, then capture / hydrate / invalidation parity / restore
      parity tasks. tickets/stories/2026-09-26_structural_snapshot_story.md (fable_0, opened 2026-09-26)
- [ ] Story: STORY-2026-08-03-ir-schema-design - define the node/edge schema,
      the symbolic id scheme, the version stamp, and the answer to the identity
      question. Owner ratification required.
- [ ] Story: STORY-2026-08-03-ir-port-phases-1-4 - requirements, symbolic graph,
      local frame, validation.
- [ ] Story: STORY-2026-08-03-ir-port-phases-5-7 - root blueprints, system
      validation, change control.
- [ ] Story: STORY-2026-08-03-ir-port-phases-8-10 - occurrence, injection,
      patch maps, execution plan.
- [ ] Story: STORY-2026-08-03-phase-11-hydration-boundary - phase 11 consumes IR
      and emits; add the test that fails if any symbol is reachable from meld.
- [ ] Story: STORY-2026-08-03-ir-hash-memoization - content-hash the IR and
      short-circuit recompile on an unchanged plan.

## Tasks (Cross-Cutting or Epic-Level)

- [ ] Task: Author the required patch docs before any implementation story opens
      (`patch_framework_gating.md` entry gate - this epic is system-impacting).
- [ ] Task: Capture a gauntlet baseline before the first port lands, so parity
      is measured rather than assumed.
- [ ] Task: Update `src_architecture.md` and `src_components.md` with the IR
      boundary; regenerate both `*_index.md` in the same pass.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories.

## Acceptance Criteria (Epic Done)

- A test walks every phase 1-10 artifact and FAILS on any non-value field.
- Round-trip test: IR serialized, deserialized, hydrated, and the resolved object
  graph is behaviorally identical to a non-round-tripped conjure.
- A test asserts no IR symbol type is reachable from the meld call path.
- Full existing test suite green on 3.14t, owner-run.
- Gauntlet parity: `test_melder_gauntlet.py` per-scope-cycle summary within run
  noise of the pre-port baseline. A regression here means IR reached the hot path.
- Recompiling an unchanged Spellbook is an IR-hash hit with no phase execution.
- Both canonical system docs updated and their indexes regenerated.

## Risks / Mitigations

- **RISK: IR leaks into the runtime lane.** Highest-severity failure mode; turns
  a maintainability win into a throughput regression.
  MITIGATION: the reachability test plus the gauntlet parity gate. Both are
  acceptance criteria, not follow-ups.
- **RISK: a phase needs object identity, not just a name.** Would force an
  identity concept into the IR mid-port.
  MITIGATION: STORY-1 surfaces it before any port begins; it is an explicit
  ratification item in STORY-2.
- **RISK: big-bang refactor of the most load-bearing code in the system.**
  MITIGATION: port in tranches (1-4, 5-7, 8-10), each keeping the existing suite
  green; `refactor_limits.md` scope discipline per story.
- **RISK: conjure gets slower because the IR is rebuilt where it should be
  cached.** MITIGATION: the memoization story, and conjure timing in the epic's
  success metrics.
- **RISK: the epic is justified on the wrong grounds.** It will be tempting to
  sell this as a performance fix. It is not one - see Non-Goals.

## Applicable Anti-Patterns

- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.
- [ ] No design decision taken from `src_architecture.md` alone - documents are
      evidence of intent, source is evidence of behavior.
- [ ] No implementation before the patch-framework entry gate is satisfied.

## Validation / Test Approach

- Value-only assertion walk over all phase 1-10 artifacts.
- IR round-trip behavioral equivalence test.
- Meld-path symbol reachability test (must fail loudly if violated).
- Existing spell_compiler unit/component suites, per tranche.
- Gauntlet regression gate:
  `python benchmarks/testing_other_di/test_melder_gauntlet.py`, baseline
  captured before the first port. Compare per-scope-cycle create/cleanup/total.
- All runs are OWNER-RUN. Agents report `"Not run."` until the owner reports
  output (`evidence_reporting.md`).

## Rollout / Adoption Plan

- Internal only; no public API surface changes, so no consumer migration.
- Land tranche by tranche behind a green suite; no flag, no dual path - a
  parallel legacy pipeline would double the surface and rot.
- Downstream tickets (crystallizer plan persistence, MR plan-grain diff) open
  only after Milestone 4.

## Open Questions

- Does the IR carry validation RESULTS, or only the structure that validation
  consumes? Results in the IR make the plan self-describing; they also make it
  stale-able independently of the structure.
- Version the IR under the existing `RecordVersion "1.0.0"` stamp, or a separate
  IR version line? Sharing the stamp couples plan format to record format.
- Is phase 11's existing codegen cache keyed on something that an IR hash could
  replace outright, or do they answer different questions?
  (`codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py`)
- Does `dynamic=True` change what the IR must carry, given link/sever/transfer
  mutate structure after conjure?
- (2026-09-25) Is reflection separable from classification inside phase 1
  (`spell_requirements_finder.py`)? Decides whether "level 0" is an extraction or a rename.
- (2026-09-25) Can phases 1-10 run CLOSED over a deserialized IR (user modules unimportable) and
  produce the identical plan? This is the Mojo-readiness proof; value-only fields do not prove it.
- (2026-09-25) What does the existing `phase8_11 codegen IR` export payload contain, and is the
  creation-cache key an IR hash already? (`shared_compiler_executions.py:1342-1477`,
  `spell_compiler_artifact.py`, `caching_system.py`). If yes, L4 exists in embryo.
- (2026-09-25) Which phase holds live objects for identity rather than for a name? First candidate:
  phase-1 requirement metadata retains the exact default object.
- (2026-09-25) Which direction is cheaper to bridge during a tranche port: IR->legacy after the
  ported tranche, or legacy->IR before it?
- (2026-09-25) Mojo claims to verify before the schema story ratifies anything: no runtime
  reflection (forces level 0 to stay Python-side) and AOT compilation (forces the L4 plan to be
  interpretable, with Python codegen demoted to an optimization lowering).
- (2026-09-25) The owner reports speed parity with competitors on a 5-minute gauntlet run; the
  output is not on file. Why parity arrives only after minutes is unexplained.

## Decision Log

- 2026-08-03 (owner): phases **1-10** move to the IR entirely; **phase 11
  computes the rest**. The hydration boundary is phase 11, not a phase-by-phase
  mix.
- 2026-08-03 (owner): the epic is placed on the board **unclaimed**.
- 2026-09-25 (owner): epic assigned to `fable_0` as the focus lane; STORY-1 opened with three
  read-only tranche tasks (driver plus 1-4, 5-7, 8-11).
- 2026-09-25 (owner): the motive for the IR is a planned migration of most of this code to Mojo.
  The IR must decouple the phases from Python objects while conveying the same meaning and
  intent. MLIR was considered and judged probably further than needed. Owner proposal to
  evaluate: gather all requirements in a phase before phase 1 ("level 0"), giving 12 phases,
  with better hydration as a goal.
- 2026-09-25 (owner, refinement): level 0 starts at bind, where the object is inspected and its
  details are already in hand; cache that capture first. After it, phases should need only the
  representation, never the references. Phases 5-7 matter but could be delayed to phase 11.
  Caveat raised by the owner: phases 1-4 allow late binding with partial validation steps, and
  the top-down compiler is more complex than the simple picture.
- 2026-09-25 (owner, reframing): the target is most or all of the pipeline in Mojo behind an
  interface, with as little CPython interaction as possible. "The current pattern isn't wrong,
  it's just slow." Owner supplied a gauntlet run showing setup 6.4x slower than two competitors.
- 2026-09-25 (owner): Mojo is deferred; the migration is a strangler-fig move in about a year. The
  live question is whether the structure can be improved now so Melder wins the gauntlet. Owner
  ran benchmarks/testing_other_di/test_real_world_gauntlet_cprofile.py and supplied the output.
- 2026-09-25 (owner): module/import cost is to be ignored for now; focus returns to the pipeline
  structure. Owner authorized correcting src_architecture.md and src_components.md where the
  survey finds them wrong; first corrections landed the same day (boot order, conjure cache
  paths, codegen IR export seams).
- 2026-09-25 (owner): hot-path call trimming is worth trying but NOT YET - another agent is
  working the hot paths now. The door-diet lane is not opened by fable_0; fable_0 stays on the
  compiler (survey, then the structural snapshot).

- 2026-09-26 (owner): build a discovery strategy aimed at implementation, make it durable enough to
  survive a compaction through this epic, then go into implementation. Discovery is re-sequenced
  toward the structural snapshot (hash -> hydrate for phases 1-7); the exhaustive phases 8-11 survey
  for the schema story is DEFERRED behind it. Strategy, done criteria and recovery protocol live in
  this epic's Context / Handoff Summary ("DISCOVERY STRATEGY AND RECOVERY").
- 2026-09-26 (owner): "your job is to figure out how we can improve the phases and all this stuff so keep
  working on it." Improvement-plan story opened; STORY-1 stays in review; no design ratification asked
  until the plan is presented once.
- 2026-09-26 (owner): improvement plan decided: C-H and C-A approved as the first tranche; C-B (fuse
  phases 5-7) rejected for now - the system-wide check and the single-spell dependency check must stay
  separately schedulable.
- 2026-09-26 (owner): creation-cache payload limit ruled as option B - refuse cache emission for spells
  whose persisted rows cannot replay their contract payload faithfully (T1 story, task 4). The
  structural snapshot inherits the constraint: replay rows must be lossless or carry a not-cacheable
  verdict.
- 2026-09-26 (owner): `SpellContract` override values are unrestricted (objects included) and ride the
  meld-overrides path, never a plan row or generated literal; `spell_override` renames to `override`.
  Task 5 under the T1 story designs it with the override lanes (melder_0 design v2); rows stay a hash
  surface. The structural snapshot inherits: contract override values are never row material.
- 2026-09-26 (fable_0, implemented): rows carry value-only references to the consumer's descriptor and the
  no-overrides hydration resolves them live; the option-B emission gate is retired; no cache generation
  bump. T1 story tasks 2-5 are all in review pending owner-run suites.
- 2026-09-26 (owner): tranche T1 accepted and closed (tasks 1-5 and the story); I-0 of the implementation
  entry is delivered (one serializer, determinism test). Canonical maps carry the tranche; the structural
  snapshot inherits the row rule (hash surface; contract override values are never row material).
- 2026-09-26 (owner): the survey story (Milestone 1) and the improvement-plan story turned in ("turn in your
  shit if your done"); their records stay under artifacts/ as reference. No fable_0 lane is routed after this.
- 2026-09-26 (owner): I-1 structural snapshot selected as the next lane; story opened with the patch-doc task
  first; four design rulings requested (custom-__eq__ frames, envelope vs sidecar, per-spell key extension,
  CCM dirty-root loop).
- 2026-09-26 (owner): I-1 design settled (1-4 per spell, no refusal, normal regeneration) and the patch docs
  approved; C-C is the first implementation task; release note and turn-in follow owner-run green suites.
- 2026-09-26 (owner): C-C landed and turned in (phase 3 without the per-spell DAG object; -31..-34% on phase 3 in the
  VM harness); the I-1 capture task is open behind a Propose->Confirm and melder_0's answer on the cache-path files.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - <patch docs to be authored under system_docs/patches/active/ at story start>
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_run_20260925.txt (owner-run gauntlet,
    retain_as_reference)
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt (owner-run
    cProfile gauntlet, 3.14, gil=enabled, retain_as_reference)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: durable deltas merged into `src_architecture.md` and
  `src_components.md` at epic closure; patch lane removed per
  `patch_framework_gating.md` closure gate.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - UNKNOWN
- IF_UNKNOWN: none

## Notes

- DATETIME: 2026-08-03T01:45:00Z
  TYPE: DECISION
  CLAIM: Owner ruled the IR boundary at phases 1-10, with phase 11 as the sole
    hydration and codegen step. Epic authored and boarded unclaimed.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py
  IMPACT: Fixes the scope boundary before design starts, so the IR schema is
    built for ten consumers rather than being negotiated per phase.
  NEXT: Claim the epic and open STORY-2026-08-03-phase-pipeline-survey.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T01:45:00Z
  TYPE: UNKNOWN
  CLAIM: Everything this epic states about what phases 1-11 currently DO is
    drawn from `src_architecture.md` and the module layout on disk. No phase
    implementation has been read. Under the Unknowns Gate a document is evidence
    of intent and only source is evidence of behavior, so the current-state
    description is UNKNOWN, not FACT.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:628-640
  - context_compass/agent_onboarding/default/general/skills/unknowns_gate_reference.md:38-41
  IMPACT: A schema designed from the architecture doc would encode intent rather
    than behavior, and the mismatch would surface mid-port when it is expensive.
  NEXT: STORY-1 reads `compiler_phase_1.py` through `compiler_phase_11.py` and
    promotes this to FACT with file:line evidence per phase.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T01:45:00Z
  TYPE: RISK
  CLAIM: The tempting justification for this epic is performance, and that
    justification is false. Measured on the gauntlet, CPython 3.15.0b2t against
    3.14.0t moved this workload +0.22% - noise - which rules out interpreter
    dispatch as the constraint and points the residual at object allocation and
    refcounting. An IR changes neither.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:316-325
  IMPACT: An epic sold on a speedup it cannot deliver gets judged against the
    wrong acceptance criteria and reads as a failure when it succeeds.
  NEXT: Keep the Non-Goals section intact through every status transition.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T21:24:27Z
  TYPE: DECISION
  CLAIM: Owner assigned the epic to fable_0 as the focus lane (2026-09-25). STORY-1 opened as
    tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md with three read-only tranche
    tasks (driver plus 1-4, 5-7, 8-11); task 1 is routed on the board and awaits scope approval.
  EVIDENCE:
  - tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md
  - tickets/tasks/2026-09-25_survey_compiler_phases_1_to_4_task.md
  IMPACT: The epic's entry gate (STORY-1 before anything else) is live work, not a parked note.
  NEXT: Owner approves the survey scope; task 1 reads the driver.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T21:24:27Z
  TYPE: FACT
  CLAIM: The phases directory carries shared_compiler_executions.py (1516 lines) and utility.py
    (44 lines) beside the eleven phase modules (3544 lines total); the epic's evidence names only
    phase files. The survey scope includes the shared module.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1-1516
  - src/melder/aether/spellbook/spell_compiler/phases/utility.py:1-44
  IMPACT: Phase bodies may live in the shared module; a survey of the phase files alone would
    describe wrappers.
  NEXT: Task 1 follows delegations from compiler_phase_1.py into the shared module as they occur.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-25T21:24:27Z
  TYPE: RISK
  CLAIM: The override-execution epic (updater_0 lead, updater_1) holds review-stage proposals that
    change phases 8-11 and the creation runtime door; the melder verification story lists the
    compiler-IR epic as out of its scope. No lane writes IR work today, but tranche-3 source may
    move once the owner selects an implementation.
  EVIDENCE:
  - tickets/stories/2026-09-25_verify_override_writer_and_contract_story.md:51-52
  - attention_board.md:89-92
  IMPACT: Tranche-3 findings may need re-verification before the schema story; a future port must
    be sequenced after or coordinated with the override implementation.
  NEXT: With owner approval, send updater_0 one NOTICE that this lane is read-only over
    spell_compiler/**; re-verify tranche-3 ranges at the schema story's start.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T21:28:51Z
  TYPE: DECISION
  CLAIM: Owner direction (2026-09-25): the IR exists to prepare a Mojo migration. It must decouple
    phases from Python objects while carrying the same meaning; MLIR is judged probably too far;
    a requirements-gathering phase before phase 1 ("level 0", 12 phases) and better hydration are
    the owner's candidate shape. This reframes Goals: portability of phases 1-10 off Python is now
    a first-class outcome, not a side effect of value-only fields.
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:310-314
  IMPACT: The schema story must design for a language-neutral IR, and the survey must record
    every point where a phase reflects over or calls into Python objects, not only what it stores.
  NEXT: Owner confirms the reframing; task 1 record shape gains "reflection points" and
    "Python-callback points" fields before tranche 1 starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:28:51Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Three candidate IR strategies were laid out for the owner: (A) adopt MLIR now;
    (B) a custom value-only IR as the epic already specifies; (C) option B designed as a layered
    dialect stack (L0 facts, L1 requirements, L2 graph, L3 resolution, L4 plan) with a verifier per
    level and a "closed over the IR" test (phases 1-10 run on a deserialized IR with user modules
    unimportable). fable_0 recommends C, with MLIR deferred to a post-port lowering inside Mojo.
    The "level 0" phase is recommended as the single Python-bound front end that captures facts,
    not decisions; whether it is an extraction or a rename depends on what the survey finds in
    spell_requirements_finder (UNKNOWN until read).
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:310-314
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:1-207
  IMPACT: Fixes the design frame the schema story starts from and adds one acceptance criterion
    (closure) that value-only fields alone cannot prove.
  NEXT: Owner decision on the frame; then tranche 1 begins with the extended record shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:36:42Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner refinement (2026-09-25) recorded at Decision Log :315-319. fable_0's synthesis
    for discussion: (1) after a complete bind-time capture, references are needed only to hydrate,
    to wire runtime callbacks, and to verify the capture is not stale (fingerprint check), never
    to compute; (2) the pipeline reads naturally as compile (0-4, per book, incremental per spell)
    -> link (5-6, per conduit, over IR plus a value-shaped world snapshot) -> plan (8-10) -> emit
    and wire (11 plus today's phase 7 revalidator registration); "delay 5-7" is about what those
    steps READ, not when they run, because conjure-time fail-fast is public behavior; (3) late
    binding makes this an incremental compiler: the IR needs first-class unresolved-socket nodes,
    per-node validity states mirroring SpellSystemStates, and hash-keyed invalidation so a new
    bind recomputes only the affected subgraph (query model rather than top-down passes).
    Behavioral claims about current phases remain UNKNOWN until source is read.
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:315-319
  - system_docs/src_architecture.md:663-671
  - system_docs/src_components.md:3022-3040
  - system_docs/src_components.md:3067-3072
  IMPACT: Adds a third survey record field, "world reads" (registry and spellbook state each phase
    consults), because the query surface is what a pure-function port must make explicit.
  NEXT: Owner reacts; survey proceeds with the three extra record fields (reflection points,
    Python-callback points, world reads).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:42:23Z
  TYPE: MEASURE
  CLAIM: Owner-run gauntlet (2026-09-25, gil=disabled, 5 singletons, 5000 iterations, 3 threads,
    hot_objects_per_iter_min=1880): setup melder 259.699ms vs dependency-injector 40.463ms vs
    dishka 40.143ms (6.4x). Hot path: hot_scopes/s melder 23,382 vs 35,491 vs 28,797 (1.52x and
    1.23x); threaded phase per-iter avg 2.454ms vs 1.564ms vs 1.954ms; melder max 20.871ms vs
    3.352ms and 7.331ms. Per-cycle request-scope whole-cycle: melder 0.012ms, dependency-injector
    0.019ms, dishka 0.008ms. Method: the gauntlet's own reporting; interpreter build, commit and
    machine are UNKNOWN (not in the paste). Setup composition is UNKNOWN: it may include Aether boot,
    bind reflection, phases 1-11, phase-11 codegen, creation-cache persistence and scheduler
    thread startup, and no profile splits them yet.
  EVIDENCE:
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_run_20260925.txt:1-49
  - benchmarks/testing_other_di/test_melder_gauntlet.py:316-325
  IMPACT: Setup (conjure) is the measured gap and is inside this epic's boundary; the hot path is
    outside it (Non-Goals) and the compiled competitor is only 1.5x faster there. A setup profile
    split is required before attributing the 220ms to compile compute that a Mojo port would remove.
  NEXT: Propose an owner-run profiling task that splits setup into boot, bind, phases 1-7, 8-10,
    codegen 11, cache persistence and scheduler startup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:49:41Z
  TYPE: MEASURE
  CLAIM: Owner-run cProfile gauntlet (3.14, gil=enabled, 25 iterations): setup melder 347.6ms vs
    dependency-injector 28.6ms vs dishka 61.6ms. In melder's setup the import of the package
    dominates: `_find_and_load` 617 calls / 477 `exec_module` (dependency-injector 24, dishka 67),
    `__init__.py:<module>` cumtime 0.270s of the 0.348s setup, `aether.py:<module>` 0.144s, and
    C-level file work alone is ~0.10s (marshal.loads 509 calls 0.034s, nt.stat 2672 calls 0.023s,
    open_code 477 calls 0.023s, read 0.020s). No compiler phase function appears in either top-40;
    `builtins.compile` (codegen) is 46 calls, 0.014s. Hot path (reliable columns are ncalls and
    tottime): melder 865,494 calls vs 264,649 and 409,350 for identical work; per scope cycle
    (1,625 cycles) RLock enter+exit 25,336 each (15.6/cycle), dict.get 69,042 (42/cycle),
    isinstance 47,860 (29/cycle), ulid_factory genexpr 27,054 (16.6/cycle); the codegen'd
    creation-context bodies cost ~6us each. Method caveats: the harness profiles via runcall on the
    main thread only and prints with strip_dirs; on 3.14 the `cleanup` frame carries the whole
    run's cumtime, which marks cross-thread interleaving, so cumtime inside the threaded phase is
    not trusted; the import rows precede any thread and are trusted. pytest's assertion-rewrite
    hook adds 615 calls / 0.041s to imports that production would not pay.
  EVIDENCE:
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:67-88
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:106-136
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:24-24
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:41-41
  - benchmarks/testing_other_di/test_real_world_gauntlet_cprofile.py:52-64
  IMPACT: On this workload the setup gap is import-time and eager boot, not the compiler; the IR
    epic's justification stays durability, hydration and the Mojo seam. Winning setup is an
    import/boot lane; winning the hot path is a scope-cycle call-count lane. Both are outside this
    epic's EXECUTION_BOUNDARY and need their own tickets.
  NEXT: Owner runs `python -X importtime -c "import melder"` (no pytest) and supplies the output;
    fable_0 attributes it per module and proposes the import/boot ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:49:41Z
  TYPE: HYPOTHESIS
  CLAIM: Setup can reach the competitors' range without touching the compiler by (a) deferring the
    import of subsystems the gauntlet never uses (Nexus, Crystallizer, MutationResearch, examiner
    profiles, protocol crafter) until first use, (b) constructing the Aether-hosted singletons
    lazily instead of at import-time boot, and (c) reducing the 477-file import footprint, since
    each file costs a stat/open/read/unmarshal on NTFS. Hot-path gains lie in the scope-cycle door
    (locks, ULID minting, isinstance and dict.get counts), not in the compiled executors, which
    are already at parity. Both are untested; (b) is a boot-sequence change and system-impacting.
  EVIDENCE:
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:72-88
  - system_docs/src_architecture.md:540-548
  - system_docs/src_architecture.md:610-616
  IMPACT: Reorders the "win" plan: import/boot first (largest, cheapest), scope door second, IR
    epic for durability and the Mojo seam in parallel.
  NEXT: Falsify with the importtime tree before proposing tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T21:55:45Z
  TYPE: DECISION
  CLAIM: Owner agreed (2026-09-25) that Crystallizer, Nexus and MutationResearch do not need eager
    construction and asked to develop the lazy-boot idea. Scope expansion recorded: fable_0 reads
    src/melder/__init__.py and the Aether boot path in src/melder/aether/aether.py (outside the
    survey task's spell_compiler/** boundary) to ground the discussion in source. Findings land
    here until the owner opens the import/boot ticket.
  EVIDENCE:
  - src/melder/__init__.py:1-260
  - src/melder/aether/aether.py:1-2057
  IMPACT: Keeps the expansion gate honest; the lazy-boot design gets source evidence, not doc
    evidence.
  NEXT: Read __init__.py in full, then the Aether boot ranges, and record what is constructed and
    imported eagerly.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-25T21:59:46Z
  TYPE: FACT
  CLAIM: The package root imports the whole AR, persistence and evolution surfaces at module level
    (Nexus, Rift, FrameViewer family, Crystallizer, CrystallizerBootstrap, ExternalPersistenceManager,
    MutationResearch, ResearchSet, DiffEngine, ProtocolCrafter) and then calls `Aether()` at import
    (src/melder/__init__.py:163). Its docstring calls the root "deliberately LOADED and flat" and
    states the concrete-path law: internals never import from the facade. `Aether.__init__`
    constructs, under `Aether._lock`: Crystallizer (:183), AetherUtilitySystem (:195), LoadGate
    (:208), AethericMediator (:222), MutationResearch (:237-239) and Nexus (:240). The MR
    construction carries an owner ruling (2026-08-03) that it MUST be eager: the earlier lazy
    version "saved a few milliseconds and cost a real invariant" because a bare
    `MutationResearch()` was a lookup for lucky callers and a ValueError for everyone else.
    The four hardcopy documents already load lazily (manifest only at import).
  EVIDENCE:
  - src/melder/__init__.py:50-140
  - src/melder/__init__.py:163-163
  - src/melder/aether/aether.py:120-134
  - src/melder/aether/aether.py:174-250
  - src/melder/aether/aether.py:826-870
  - src/melder/__graph_details__.py:39-49
  IMPACT: Any lazy-boot design must keep "Aether builds first" true through every door, including
    the bare constructors, or it repeats the reverted failure.
  NEXT: Design the lazy builders so the roots' `__new__` routes an unbuilt root through Aether.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:59:46Z
  TYPE: FACT
  CLAIM: Import coupling from the core into the three subsystems is narrow. MutationResearch:
    no core edge except aether.py:22. Nexus (123 modules, 64,842 lines): aether.py:23,
    spellbook.py:46 (module-level) and two spell_examiner profile modules; every Spellbook holds
    `self._nexus = Nexus()` at init (spellbook.py:266) and publishes spell records into it on
    bind and conjure (spellbook.py:5447, :6069-6089), gated by a cached passive-publication flag
    (:6053-6057). Crystallizer (61 modules, 29,804 lines): module-level imports in
    aetheric_frame_configuration.py:9-10, aether_configuration.py:6-7,
    spellbook_configuration.py:13-14, conduit.py:36, conduit_cluster.py:11-12, plus
    TYPE_CHECKING-only imports elsewhere; the configuration classes call the bare
    `Crystallizer()` lookup at freeze to emit a twin (e.g. spellbook_configuration.py:401-422),
    and Spellbook/Conduit/Frame hold non-owning `_crystallizer` references used at ~25 emit
    sites (spellbook.py 9, aether_utility_system.py 6, conduit_cluster.py 3, others 1-2).
    Subtree sizes: aether 320 modules / 137,911 lines; utilities 45 / 24,088; total 595 modules.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:46-46
  - src/melder/aether/spellbook/spellbook.py:266-266
  - src/melder/aether/spellbook/spellbook.py:6053-6089
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:401-422
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:483-496
  - src/melder/aether/conduit/conduit.py:448-448
  IMPACT: Deferring the three subsystems removes roughly 204 of the 477 executed modules and
    ~109k of ~320k lines from the cold import, but only if the emit and publication seams stop
    resolving the roots on every bind and conjure; otherwise the first Spellbook rebuilds them.
  NEXT: Owner supplies the importtime tree to rank the remaining core modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T21:59:46Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Proposed lazy-boot design in three layers. (1) Import: PEP 562 `__getattr__` on the
    package root for the Nexus/Crystallizer/MR export families (facade unchanged for users;
    internals already use concrete paths); aether.py and spellbook.py keep TYPE_CHECKING imports
    only and import the roots function-locally inside the builders. (2) Construction: Aether
    builders `_ensure_crystallizer/_ensure_mutation_research/_ensure_nexus` under `Aether._lock`,
    dependency-ordered (MR and Nexus builders call the Crystallizer builder first, preserving
    the canonical boot order); each root's `__new__` routes an unbuilt root through the Aether
    builder, so a bare `Crystallizer()`/`Nexus()`/`MutationResearch()` is always a safe lookup -
    the exact invariant the 2026-08-03 ruling protects; `cleanup` and the test reset skip unbuilt
    roots. (3) Seams: Spellbook/Conduit/Frame stop holding root references and read plain bools on
    Aether (`crystallizer_active`, `nexus_engaged`, the same idiom as
    `_process_wide_unique_spell_ids`), building twins and publishing only when set. Semantics:
    emit is already a no-op while inactive and Nexus publication is already flag-gated, so
    gating before the twin is built changes no observable behavior (R-A covenant intact) and
    removes twin allocations from bind/conjure even in eager worlds. Costs: ~25 emit sites plus
    the Nexus publication sites change shape; a function-local Aether import inside three
    `__new__` methods; a boot-sequence change, so patch-framework gated.
  EVIDENCE:
  - src/melder/aether/aether.py:187-191
  - src/melder/aether/aether.py:226-240
  - src/melder/aether/spellbook/spellbook.py:6053-6089
  - src/melder/__init__.py:41-46
  IMPACT: Candidate for the import/boot lane's first tranche; expected to remove roughly a third
    of cold-import work, with the remainder needing per-module attribution.
  NEXT: Owner reacts; run `python -X importtime -c "import melder"` and, as a one-minute sizing
    experiment, the gauntlet setup under `python -OO` to measure the docstring share of bytecode.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T22:04:38Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner (2026-09-25) is unsure the import/boot lane is worth the effort: the gauntlet is a
    15-second micro-benchmark, a 5-minute run reportedly reaches speed parity with the competitors
    (output not supplied; UNKNOWN), and the benchmark may not represent production. Owner asks
    whether a Mojo system compiled to .so extension modules behind an interface makes the
    import/boot cost vanish. fable_0 answer recorded in the session: it changes shape rather than
    vanishing (dependency-injector's own setup is ~24ms of `_imp.exec_dynamic` for two compiled
    modules, i.e. DLL load, not bytecode), so the number of extension modules and the width of
    the Python-visible surface become the cost drivers; the seam work (roots built on demand,
    flag-gated emit and publication, facade `__getattr__`) is migration-preparation that the
    strangler fig needs anyway, while bytecode-volume and module-consolidation work is
    Python-only and can be skipped if the migration is a year out.
  EVIDENCE:
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:24-26
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:41-41
  IMPACT: The import/boot lane is not opened; its evidence stays on this epic for a later
    decision. The IR survey remains the active lane.
  NEXT: Owner decides whether to park the import/boot work as a backlog ticket; survey continues.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-25T22:19:13Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: "Where we win" candidates from the driver survey (task 1 notes and
    artifacts/ir_phase_survey_20260925/driver.md carry the evidence): (1) the IR is latent, not
    greenfield - a signed value-only export of phases 2-5 exists and is dormant by design,
    reserved in phase 2's own NOTE for "a future incremental recompile path"; phase-11 codegen
    already consumes step rows and an int-array transient plan with call targets factored out;
    (2) warm conjure: a full creation-cache hit skips only 8-11 while 1-7 recompute every time,
    so a structural snapshot keyed by the dormant phase 2-5 signature (plus frame posture) turns
    warm conjure and restore into hash -> hydrate, with the spell id (bind fingerprint) already
    serving as the L0 hash; (3) the phase-11 signature path has two determinism hazards (unsorted
    set pickling; `repr` fallback on user contract payloads) and a duplicated serializer - a
    cheap determinism test and one serializer harden the cache the IR will stand on; (4) phases
    9-10 are closed at the call level and phase 10 already practices lazy import, so the closure
    criterion is achievable per phase rather than all-or-nothing. Tranche order implied:
    structural snapshot (2-7 hydration) before any phase port, since it pays in the regime the
    owner can feel and reuses the seam the code reserved.
  EVIDENCE:
  - artifacts/ir_phase_survey_20260925/driver.md:1-125
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:179-184
  - src/melder/aether/spellbook/spellbook_creation_system.py:226-247
  IMPACT: Reframes the first port tranche from "phases 1-4 onto dataclasses" to "structural
    snapshot and hydrator over the existing 2-5 export", a smaller, measurable first step.
  NEXT: Owner reacts; survey reads run_structural_phases and the resolution profile next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T22:57:31Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner asked whether compiling the Python would win, and where the wins are. fable_0's
    ranking from the evidence: compilation (Cython pure-Python mode or mypyc on the scope-cycle
    door only) is worth about what the compiled competitor shows, ~1.3-1.5x on the hot path,
    because the residual is C-level work (allocation, refcounts, locks, dict ops) that the JIT
    result (+0.22%) already showed is not dispatch-bound; it is a cheap, reversible experiment
    and the empirical business case for a native orchestrator, not the strategy. Wins, ranked:
    (1) the scope-cycle door diet - ~16 RLock pairs, ~17 ULID-genexpr iterations, 29 isinstance,
    42 dict.get per cycle against ~6us compiled creation bodies; language-independent and the
    free-threading scaling cap; (2) tail latency - 20.9ms worst iteration vs 3.4/7.3ms; likely
    allocation-driven collections or lock convoy; flag-gated crystallizer emit removes twin
    allocations per bind/conduit creation; (3) hash->hydrate for warm conjure and restore over the
    dormant phase 2-5 signature - the epic's payoff and the Mojo seam; (4) setup, parked.
    Caveats: door items are HYPOTHESIS until conduit.py/meld.py/spell_space.py are read; Cython
    and mypyc support on free-threaded 3.14t is UNKNOWN and must be verified; the 5-minute parity
    run remains unfiled and decides how much (1) matters versus (2) and (3).
  EVIDENCE:
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_run_20260925.txt:1-49
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:106-136
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:403-417
  IMPACT: Gives the owner a ranked, evidence-tiered menu; none of it changes this epic's scope
    except (3), which is its first tranche. (1) and (2) are separate lanes.
  NEXT: Owner picks; if (1)/(2), open a door-diet story with the contention and GC probes as
    its first measurements; if a compile experiment, verify free-threaded support first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T23:00:38Z
  TYPE: DECISION_REQUEST
  CLAIM: fable_0's recommended "decent win": the scope-cycle door diet, targeting 32-34k hot
    scopes/s (beat dishka's 28,797; within ~10% of dependency-injector's 35,491) and a worst
    iteration under 10ms (from 20.9ms), by roughly halving per-cycle call volume (16 RLock pairs,
    17 ULID-genexpr iterations, 29 isinstance, 42 dict.get) around ~6us compiled creation bodies.
    Rationale: the gap is call volume (dishka does identical work in pure Python with 47% of the
    calls); the lock count is also the free-threading scaling cap and likely the tail driver; the
    fix is structural and carries into Mojo. Preconditions: file the 5-minute run; run
    profile_scope_cycle_contention.py and test_melder_gauntlet_gc_probe.py once each. Shape: read
    the meld door end to end (spell_space.py, spellspace_meld.py, conduit_meld.py, meld.py,
    creations.py, creation gate, pooled-lesser return in conduit.py), produce a per-cycle cost map,
    then a story with three gauntlet-gated tasks (lock consolidation, lazy IDs for pooled lessers,
    meld-door check removal). Second, strategic: hash->hydrate snapshot (this epic's tranche 1).
    Decision needed: open the door-diet lane (separate story/epic, outside this epic's boundary),
    and whether to interleave it with or pause the survey.
  EVIDENCE:
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_run_20260925.txt:10-19
  - artifacts/ir_epic_gauntlet_baseline_20260925/owner_cprofile_run_20260925.txt:106-136
  IMPACT: Sets a measurable target and a gate for each change; keeps this epic focused on the
    snapshot while the runtime win runs in its own lane.
  NEXT: Owner decides; on go, fable_0 opens the door-diet story with the two probe runs as tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T23:13:05Z
  TYPE: DECISION
  CLAIM: Owner response to the 2026-09-25 DECISION_REQUEST: the scope-cycle door diet is deferred
    ("sure we can try that in the hot paths, just not yet"); another agent currently owns hot-path
    work. fable_0 does not open a door-diet lane, does not read or touch the meld door, and keeps
    the per-cycle call-count findings on this epic as input for whoever holds that lane. The
    strategic win in this epic's scope - the hash->hydrate structural snapshot over the dormant
    phase 2-5 export - remains the target, reached through the survey.
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:349-351
  IMPACT: Prevents a duplicate lane on the hot path; keeps fable_0 inside the epic's
    EXECUTION_BOUNDARY (spell_compiler/** and the conjure call sites).
  NEXT: Continue task 1 at the requirements finder; offer the owner the signature-determinism test
    as a small compiler-side task (not hot path).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:04:29Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner asked for a clearer picture of the structural snapshot (ASCII drawings given) and
    restated it as "cache rows 1-7, hydrate them, else run them". Confirmed with three precisions:
    (1) the cache holds the RESULTS of 1-7 as value-only rows (per-spell lineage, validity and
    dependencies from 1-4; per-conduit blueprints and change-control registrations from 5-7), never
    object references - the dormant phase 2-5 export already has that shape; (2) two tiers, not one
    blob: per-spell 1-4 rows key on the spell's own signature and hit individually, per-conduit 5-7
    rows key on (sorted live spell ids, frame posture), so `mixed` hydrates unchanged spells' 1-4
    and re-runs 5-7 while `full_hit` hydrates everything and goes straight to executor load; (3) a
    miss is today's path plus one capture. UNKNOWN and gating the design: phases 3, 4 and 7 write
    outside the artifact (SpellSystemStates, Spell.dependencies, change-control index and
    revalidators); the hydrate list is expected from docstrings and the component map, not read.
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:722-747
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:195-261
  - src/melder/aether/spellbook/spellbook_creation_system.py:226-247
  - src/melder/aether/spellbook/spellbook_creation_system.py:412-485
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:266-376
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:179-184
  IMPACT: Fixes the snapshot's key structure (two tiers) before the schema story and names the one
    read that decides whether it is sound: the runtime writes of phases 1-7.
  NEXT: After the finder, read `run_structural_phases` (spellbook_creation_system.py:1359+) and record
    every runtime write of phases 1-4 under "Mutates" in phase_01.md to phase_04.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:53:12Z
  TYPE: DECISION
  CLAIM: Owner directive (2026-09-26): build a discovery strategy, make it compaction-durable via this
    epic so a recovering agent can resume, then move to implementation. fable_0 re-sequenced the
    survey toward the structural snapshot: phases 1-7 plus the structural and resolution drivers, the
    cache seam, and the invalidation surface are in scope; the exhaustive 8-11 survey is deferred to
    the schema story. Story task list, exit gate and acceptance criteria amended; tasks 2 and 3
    created from the template and linked.
  EVIDENCE:
  - tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md
  - tickets/tasks/2026-09-26_survey_compiler_phases_5_to_7_task.md
  - tickets/tasks/2026-09-26_survey_structural_snapshot_seam_task.md
  IMPACT: Discovery now has a definition of done (D1-D6), eleven bounded steps, and a recovery
    protocol, instead of an open-ended eleven-phase survey.
  NEXT: Execute S2 (phase 2) on task 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:53:12Z
  TYPE: PLAN
  CLAIM: Discovery strategy (full text in the handoff section). Goal: an implementation-ready basis
    for the structural snapshot. Done criteria D1 phase records 1-7 plus driver; D2 hydrate
    obligations (every runtime write of 1-7); D3 snapshot key composition; D4 `.melc` cache mechanics;
    D5 invalidation surface; D6 what the full-hit load path consumes from phase 1-7 objects. Steps
    S2-S5 (task 1: phases 2-4, structural driver and SpellSystemStates write API), S6-S8 (task 2:
    phases 5-7, resolution driver, full-hit load path), S9-S11 (task 3: cache seam, invalidation,
    summary.md). Roughly 7,600 lines of source in ~500-line chunks, so several compactions are
    expected; the write order on every step is record file -> task note -> task STATE -> epic step
    table, and a recovering agent resumes at the first step whose table status is not done.
    Implementation entry after S11 and the owner's go: I-0 determinism test plus one serializer,
    I-1 the snapshot behind patch docs and gauntlet-gated tasks.
  EVIDENCE:
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:722-747
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:819-845
  - artifacts/ir_phase_survey_20260925/phase_01.md:1-166
  IMPACT: Bounds the reading to what the snapshot needs and makes progress measurable per step.
  NEXT: S2: read compiler_phase_2.py (184) and symbolic_graph/ (409); write phase_02.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:34:29Z
  TYPE: DECISION_REQUEST
  CLAIM: Discovery steps S1-S11 are executed; the three survey tasks and STORY-1 are in review with ten
    files under artifacts/ir_phase_survey_20260925/ (summary.md consolidates D1-D6). Headline: phases 1-4
    artifacts are transient and the registry rows are the durable form; phases 5-7 read registry only;
    a full hit still runs 5-7 and its hydration reads only the pool and the phase-5 path registry; every
    invalidation event already writes through the registry, so hydration by registry replay needs no
    new hooks. Four rulings are needed before I-1 can be designed: (1) frames with a custom `__eq__`
    (the one identity-bearing match) - accept name matching or define a canonical frame key; (2)
    snapshot placement - a structural section inside the `.melc` envelope (generation bump, one cold
    reset) or a sidecar with its own stamps; (3) whether the per-spell key adds a module fingerprint
    (a type moving module while keeping its rendered name keeps the spell id today); (4) whether the
    change-control dirty-root loop (`notify_spell_changed` -> meld gate -> revalidator) is public
    DevOps API or dead wiring, which decides the CONFLICT correction to src_architecture.md.
  EVIDENCE:
  - artifacts/ir_phase_survey_20260925/summary.md:1-142
  - tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md
  IMPACT: Accepting summary.md closes Milestone 1 (phases 8-11 deferred by ruling) and opens I-0; the four
    rulings bound the I-1 patch docs.
  NEXT: Owner accepts or redirects; on acceptance fable_0 runs closure sync for the story and tasks,
    checks Milestone 1, and opens the I-0 task (determinism test plus one serializer).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T07:38:41Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner challenge (2026-09-26): frames and snapshot placement are not the survey's scope. Correct.
    STORY-1's contract is read-only fact-finding with "candidates for the identity question listed, not
    chosen" and schema design out of scope; the identity ruling belongs to STORY-2 (schema design, owner
    ratification), and snapshot placement is a design decision of the same kind. The DECISION_REQUEST
    above is WITHDRAWN as an ask; its four items stay recorded in summary.md as candidates/UNKNOWNs for
    STORY-2. Also corrected: the structural-snapshot-first sequencing was fable_0's proposal (note of
    2026-09-25T22:19:13Z), not an owner ruling; the 2026-09-26 directive asked for a durable discovery
    strategy and then implementation. The survey records stand on their own; the only owner action
    pending in this lane is acceptance or redirect of the records.
  EVIDENCE:
  - tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md:54-58
  - tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md:59-66
  - tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:208-210
  - artifacts/ir_phase_survey_20260925/summary.md:1-142
  IMPACT: Removes an out-of-lane decision ask; keeps the survey inside its contract; the sequencing
    question (snapshot first vs the epic's story order) is the owner's to decide explicitly, later.
  NEXT: Owner accepts or redirects the survey records; fable_0 makes no design proposals until then.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T08:17:57Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Improvement plan for phases 1-11 (STORY-2026-09-26; artifacts cost_model.md and candidates.md).
    (1) Objective: make the conjure pipeline cheaper per regime without touching the hot path, in steps
    that also build toward the IR. (2) Constraints: read-only survey, owner-run measurements, hot paths
    and import cost out of scope, one decision ask, a Spellbook conjures once (so no memo below the
    creation cache can hit on a warm conjure). (3) Known facts: cold conjure is ~70% phases 8-11 (June,
    workers=1); warm conjure still runs 1-7 (~20ms of the 44ms profiled conjure) plus a one-time strategy
    import; phase 8 hashes a pool-sized signature per root that is discarded every pass (O(spells^2));
    the phase-3 DAG object has one production reader; phases 5-7 are three barriers and phase 7 repeats
    phase 5's CCM rebuild; the signature path has two determinism hazards and a duplicated serializer.
    (4) Unknowns: the unprofiled 1-7 share on the warm path; the signature share of plan_group; strategy
    statelessness for 33 unread strategy files; the four STORY-2 rulings C-G needs. (5) Options:
    T1 = C-H (determinism test + one serializer) + C-A (phase 8 hoist/None-first) + C-B (one foundation
    unit 5-7, phase 7 reduced to its guard); T1' = C-G structural snapshot now; T1'' = C-J cost-aware
    plan_group chunking (+ C-C, C-K). (6) Tradeoffs: T1 is small, measurable with the existing breakdown
    harness, no hot-path reach, and lands C-G's prerequisites, but its measured gain is modest (~0.1ms of
    barriers plus an unmeasured O(N^2) removal); T1' is the only large warm-path win but needs four
    rulings, patch docs and parity suites first; T1'' pays only at workers>1 on the cold path. Lane
    collisions: phase 8 files (updater_1, melder_0), shared_compiler_executions.py and possibly
    spellbook_creation_system.py (melder_0), the cache generation number. (7) Recommendation: T1 as one
    implementation story with three gauntlet-gated tasks, C-H first; T1'' next; C-G after the schema
    story's rulings. (8) Decision ask (single): approve T1 as the next implementation story (patch docs
    for C-B, NOTICEs to updater_1 and melder_0 before touching phase 8 and the shared module), or name
    T1' or T1'' instead, or redirect.
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/candidates.md:1-286
  - artifacts/ir_phase_improvement_20260926/cost_model.md:1-121
  - artifacts/ir_phase_survey_20260925/summary.md:1-142
  - tickets/tasks/completed/2026-06-12_phase_scheduler_v2_persistent_pool_task.md:164-232
  IMPACT: One decision opens implementation inside this epic's boundary; the survey rulings stay pending
    and are not re-asked here.
  NEXT: Owner picks T1, T1', T1'' or redirects; on T1 fable_0 opens the implementation story with patch
    docs and three tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:59:53Z
  TYPE: DECISION
  CLAIM: Owner ruling on the improvement plan (2026-09-26): T1 items 1 and 2 are approved (C-H signature
    determinism plus one serializer; C-A phase-8 None-first check plus a pass-hoisted pool digest). Item 3
    (C-B, fusing phases 5-7 into one unit) is NOT approved now: the owner wants the system-wide check
    (phase 6 frame-wide) to remain separately invocable, and a singular dependency check when a spell and
    its dependencies are invalidated (the local 5-7 path). C-B is deferred, not dropped; the next
    implementation story carries C-H and C-A only.
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/candidates.md
  - artifacts/ir_phase_survey_20260925/phase_06.md
  - artifacts/ir_phase_survey_20260925/structural_driver.md
  IMPACT: Implementation entry I-0 opens as a story with two tasks and patch docs; phases 5-7 keep their
    three-phase registration and both the frame-wide and local variants.
  NEXT: Open the implementation story (patch docs first), NOTICE melder_0 and updater_1, then propose the
    exact files and symbols for confirmation before any edit under src/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:04:10Z
  TYPE: DECISION_REQUEST
  CLAIM: T1 task 2 (one signature implementation, determinism test) is in review, committed as 6fc9af345
    with owner-run suites pending. Its investigation found a program-level fact for the structural
    snapshot: the phase-11 persisted step rows carry payload values in their FROZEN form, and the
    cache-load path executes them (dict -> sorted pair tuple, list -> tuple, enum -> repr text, object
    -> marker), while the in-process path uses raw values. Two consequences. (1) Owner ruling needed for
    the creation cache today: A keep and document; B refuse cache emission for spells whose rows carry a
    non-value payload (recommended - correctness kept, only those spells lose cross-process hits); C
    raise at plan time. (2) The structural snapshot's row schema (D2 hydrate obligations) must be
    lossless for every value it replays, or carry an explicit not-cacheable verdict; the current rows are
    a hash projection, not a replay format.
  EVIDENCE:
  - tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:296-341
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:316-340
  - artifacts/ir_phase_survey_20260925/summary.md
  IMPACT: Decision (1) may add a fourth task to the T1 story; consequence (2) becomes a constraint on the
    snapshot design story when it opens.
  NEXT: Owner rules A/B/C; fable_0 continues with T1 task 3 (phase-8 digest hoist) meanwhile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:42:09Z
  TYPE: DECISION_REQUEST
  CLAIM: T1 suites owner-run (1784 passed; new component fixture corrected). Program-level finding: the
    manifest-first phase-11 families bind the frozen row projection of SpellContract payload values
    IN-PROCESS (lazy doors hydrate from the manifest), not only after a cache hit; task 4's emission gate
    is the cache half. Owner choice for the in-process half: (1) fail fast on non-replayable payload
    values, or (2) raw-value side table for in-process hydration (recommended). The structural snapshot
    inherits the same rule: a row projection is a hash surface, not a replay surface, unless proven
    lossless per value.
  EVIDENCE:
  - tickets/tasks/2026-09-26_gate_cache_emission_on_replayable_payloads_task.md
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_lazy_door_step.py:15-130
  IMPACT: One more task under the T1 story on the owner's choice; no change to the phases 5-7 ruling.
  NEXT: Owner picks (1) or (2).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:17:13Z
  TYPE: FACT
  CLAIM: Tranche T1 closed on owner acceptance: one signature leaf (I-0 delivered: byte-compatible,
    two-process deterministic), phase-8 pool digest once per pass (-34% conjure at N=300 owner-run), and
    SpellContract/SpellMap `override` values as live meld operands with rows as a pure hash surface. Program
    consequence for the structural snapshot (I-1): its rows may carry value-only refs to descriptors exactly
    as phase-11 rows now do, and the determinism test is the acceptance guard for every signature-based skip.
    Open on the epic: owner acceptance of the survey story (S11, D1-D6) and the improvement-plan story (both
    in review); `src_graph.md` regeneration for the new leaf module (owner-run on 3.14).
  EVIDENCE:
  - tickets/stories/completed/2026-09-26_signature_determinism_and_phase8_digest_story.md
  - system_docs/src_components.md:3293-3330
  - system_docs/src_architecture.md:848-861
  IMPACT: The next lane is the owner's call: I-1 structural snapshot (patch docs first) or the deferred
    phases 8-11 survey; nothing is routed for fable_0 after this closure.
  NEXT: Owner selects the next lane; fable_0 opens it per the implementation entry order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:19:04Z
  TYPE: FACT
  CLAIM: Mailbox M0-25 (melder_0, 13:16:41Z) consumed: S3a is applied to the device tree (uncommitted) - the
    override runtime now reads the no-overrides rows through generalized `_hydrate_steps_from_rows` and the
    many_only equivalent, i.e. through the live contract-value resolution T1 landed; their suites are green on
    3.14t/GIL on a device-state copy. Program consequence: the "override lanes keep literalized rows until S3"
    caveat written into the canonical maps at T1 closure is being retired by melder_0's lane; that lane owns the
    doc update when S3 promotes. No action for fable_0.
  EVIDENCE:
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  - system_docs/src_components.md:3293-3330
  IMPACT: No collision: T1 is closed and its files are not being edited by fable_0; the caveat's retirement is
    melder_0's promotion item.
  NEXT: None; the next fable_0 lane waits on the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T13:27:19Z
  TYPE: FACT
  CLAIM: Owner turned in fable_0's remaining review tickets: the survey story with its three tasks (Milestone 1
    done: drivers, phases 1-7, the seam, summary.md D1-D6) and the improvement-plan story with its two tasks
    (cost model; thirteen candidates; T1 chosen and shipped). Records retained: artifacts/ir_phase_survey_20260925/
    and artifacts/ir_phase_improvement_20260926/ (retain_as_reference). The epic stays open with fable_0 as
    the focus lane; nothing is routed until the owner picks the next entry (I-1 structural snapshot, patch docs
    first, or the deferred phases 8-11 survey).
  EVIDENCE:
  - tickets/stories/completed/2026-09-25_ir_phase_pipeline_survey_story.md
  - tickets/stories/completed/2026-09-26_phase_pipeline_improvement_plan_story.md
  - artifacts/ir_phase_survey_20260925/summary.md
  IMPACT: Milestone 1 closed; Milestones 2-5 untouched; the recovery table's S11 row reads done.
  NEXT: Owner selects the next lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T15:01:13Z
  TYPE: FACT
  CLAIM: Mailbox M0-26 and M0-28 (melder_0, 13:43Z and 14:16Z) consumed: S3b-1 drops the manifests' "overrides"
    section and targeting serializers (MANIFEST_VERSION 4), unregisters the site-graph/override-targeting
    phase-9 processors, cache generation 14; S3b-2 (owner "1 and 2") makes `Spellbook._emit_spell_cache` cache
    manifest creations only, DELETES the legacy codec `spell_codegen_creation_cache.py` with the fallback
    no-overrides family, drops the `target_spec_count` export key, removes the legacy-package test from
    `test_contract_override_refs.py` and makes the determinism component test read manifest packages only.
    S3a delivers SpellMap payload objects by identity on override melds (probe-confirmed); melder_0's S6 release
    section retires the release-note caveat. T1's no-overrides row builders and hydrators are untouched.
    Doc consequence for melder_0's promotion (not fable_0's): the canonical "Deterministic signatures ..." block
    still says both `build_package` builders package (the legacy one is gone) and that the override lanes keep
    their rows until S3.
  EVIDENCE:
  - tickets/tasks/2026-09-26_build_site_plan_lowering_task.md
  - system_docs/src_components.md:3293-3330
  IMPACT: No fable_0 action; the T1 closure stands. The structural-snapshot lane, when opened, starts from the
    S3b tree (manifest-only cache path, generation 14).
  NEXT: None until the owner selects the next lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary

### DISCOVERY STRATEGY AND RECOVERY (2026-09-26, owner-directed) - read this FIRST after a compaction

GOAL - discovery is done when we hold an implementation-ready, source-backed basis for the
STRUCTURAL SNAPSHOT: a full creation-cache hit skips phases 1-7 the way it already skips 8-11, by
hydrating value rows keyed on the dormant phase 2-5 signature - plus the determinism-test task.
Everything below serves that goal. The exhaustive phases 8-11 survey for the schema story is
DEFERRED behind it (Decision Log 2026-09-26).

DONE CRITERIA - each becomes a section of artifacts/ir_phase_survey_20260925/summary.md:
- D1 phase records 1-7 plus the drivers: inputs, outputs, holds classified, runtime writes,
  reflection points, Python-callback points, world reads (Record Shape in task 1).
- D2 hydrate obligations: every runtime write of phases 1-7 - target object, writer `path:line`,
  value shape, ordering constraint, replayable-from-rows yes / no / UNKNOWN.
- D3 key composition: what a snapshot key must contain, from the cache-classification inputs and
  the phase 2-5 signature inputs (spell-id set, frame posture, configuration flags, release,
  Python tag), with evidence.
- D4 cache mechanics: how `.melc` envelopes are written, admitted and rejected; whether the snapshot
  shares the envelope or sits beside it.
- D5 invalidation surface: every event that must drop a snapshot (bind families, index mutations,
  link / sever / transfer, configuration freeze, release change) and the code that already marks
  validity gated or dirty for each.
- D6 full-hit consumption: what the cache-load path reads from phase 1-7 objects today, i.e. which
  hydrated rows must become objects and which can stay rows.

STEPS - one microcycle unit each. The status column is edited in place when a step closes.

| step | ticket | reads | must answer | status |
| --- | --- | --- | --- | --- |
| S1 | task 1 | driver; phase 1 (finder trio) | closure; level 0 | done 2026-09-26 |
| S2 | task 1 | compiler_phase_2.py (184); symbolic_graph/ (409) | identity vs name matching; phase-2 outputs and writes | done 2026-09-26 (no matching in phase 2; passes to S3) |
| S3 | task 1 | compiler_phase_3.py (1035, 3 chunks); dag/ and resolution_frame to the crossing types | world-read list; runtime writes; PLAIN default passing; late-binding partial validation | done 2026-09-26 (identity: by name for str, by id() for objects; 3 registry writes + context invalidation) |
| S4 | task 1 | compiler_phase_4.py (178); validation/validation_system.py (350); strategies by name | validity writes; what validation consumes | done 2026-09-26 (cross-spell; posture-dependent; one validity write) |
| S5 | task 1 | spellbook_creation_system.py run_structural_phases and the per-spell unit path; the spell_system_states.py methods they call (whole methods) | the 1-4 write surface a hydrate must replay | done 2026-09-26 (1-4 artifacts reset after every pass; registry state is what survives) |
| S6 | task 2 | compiler_phase_5.py (713, 2 chunks); blueprints/root_resolution_blueprint.py; system/ builders to the crossing types | publication onto spellbook._spells_by_id; socket and DAG rows vs the 2-5 export | done 2026-09-26 (reads registry only; value-shaped outputs; CCM closure is runtime-only) |
| S7 | task 2 | compiler_phase_6.py (509); system/spell_system_validation_system.py (268); compiler_phase_7.py (265); change_control_manager.py methods it calls | system-validity writes; component-of index; revalidator registration | done 2026-09-26 (per-conduit registry rows; CCM map; revalidator no-op after phase 5; loop unarmed in src) |
| S8 | task 2 | spellbook_creation_system.py _prepare_resolution_for_conjure and the full-hit branch; the codegen_creation_system cache-load entry | D6 | done 2026-09-26 (5-7 still run on a full hit; hydration reads only the pool and the phase-5 path registry; registry rows gate meld) |
| S9 | task 3 | utilities/caching_system/caching_system.py (618); capture_phase2_5_codegen_ir and hash_codegen_signature inputs (re-verify) | D3, D4 | done 2026-09-26 (envelope = 4 exact stamps + per-spell bytes; key: id covers the pool projection; dormant signature is a digest, not a key) |
| S10 | task 3 | transaction families; spell_system_states.py gated/dirty transitions (whole methods) | D5 | done 2026-09-26 (all writers via set_validity; per-event table; no new hooks needed; no raw index ULIDs in rows) |
| S11 | task 3 | consolidate summary.md; close tasks; story exit; Milestone 1 | D1-D6 accepted by owner | done 2026-09-26T13:27:19Z (owner turned in the story; Milestone 1 checked) |

Task 1: tickets/tasks/2026-09-25_survey_compiler_phases_1_to_4_task.md
Task 2: tickets/tasks/2026-09-26_survey_compiler_phases_5_to_7_task.md
Task 3: tickets/tasks/2026-09-26_survey_structural_snapshot_seam_task.md

RECOVERY PROTOCOL - after any compaction or handoff:
1. REONBOARD per policy (no shortcut).
2. Open this section. The first step whose status is not `done` is the resume point.
3. Open that step's task; its LAST `STATE` line names the file and chunk to resume at.
4. The record files under artifacts/ir_phase_survey_20260925/ are the durable knowledge; ticket
   notes are pointers. Write order on every step: record file -> task note -> task STATE line ->
   this table. A compaction mid-step therefore loses at most one file read.
5. Never re-read a file whose record is COMPLETE; cite the record. Large files are chunked at 500
   lines and each finished chunk is named in the task STATE line before the next is opened.
6. Owner rulings that bound the work: hot paths belong to another agent (do not open the meld door);
   module/import cost is ignored; system-doc corrections are authorized when source-evidenced.

UPDATE 2026-09-26T13:17:13Z (fable_0): tranche T1 (I-0 plus the phase-8 digest and the live contract operands) is DONE
and accepted; its story and five tasks are in completed/. No fable_0 lane is routed on the board after this closure;
the survey story (S11) and the improvement-plan story remain in review for the owner.
UPDATE 2026-09-26T13:27:19Z (fable_0): the survey story (Milestone 1) and the improvement-plan story are turned in by the
owner; every fable_0 story under this epic is now in completed/. Resume point after a compaction: this epic's
Decision Log and IMPLEMENTATION ENTRY; wait for the owner's lane selection.
UPDATE 2026-09-26T15:03:58Z (fable_0): I-1 opened - tickets/stories/2026-09-26_structural_snapshot_story.md, board row
ir_structural_snapshot routing to the patch-doc task; waiting on the owner's four rulings. Resume from the task's STATE line.
UPDATE 2026-09-26T16:12:08Z (fable_0): I-1 patch docs approved and task 1 completed; task 2 (C-C) is routed:
tickets/tasks/2026-09-26_drop_phase3_dag_object_for_id_rows_task.md. Resume from its STATE line.
UPDATE 2026-09-26T16:59:15Z (fable_0): C-C done and turned in (tickets/tasks/completed/2026-09-26_drop_phase3_dag_object_for_id_rows_task.md); task 3 (capture) is routed: tickets/tasks/2026-09-26_capture_structural_payloads_at_conjure_end_task.md.
UPDATE 2026-09-26T17:28:54Z (fable_0): task 3 (capture) landed on the device tree and is in REVIEW (seam module, envelope generation 15,
conjure-end capture, 33 tests; worktree green; owner-run pending); patch docs aligned. Next: the hydrate task under the same story.
UPDATE 2026-09-26T18:13:08Z (fable_0): task 4 (hydrate v1) landed and in REVIEW - a full structural hit replays phase 3-4 rows and skips
phases 1-4 (VM: warm conjure -27% at 29 spells); partial path is an owner decision. Next: the parity task.

IMPLEMENTATION ENTRY - after S11 and the owner's explicit go, in this order:
- I-0 signature-determinism test plus one serializer (small, compiler-side, protects today's cache;
  owner decides whether the serializer collapse needs patch docs). DONE 2026-09-26 (T1 story, accepted).
- I-1 structural snapshot: patch docs first (architecture_patch, component_patch for the
  SpellCompiler component, code_description_patch for the hydrator control flow), then a story with
  gauntlet-gated tasks (capture on miss, hydrate on hit, invalidation, restore parity).

### State of knowledge as of 2026-09-25 (fable_0) - read this before anything below it

Owner direction, in the order it arrived today (all in the Decision Log): the IR exists to prepare
a Mojo migration; then "level 0" at bind and representation-only phases after it, with 5-7 possibly
deferred; then Mojo deferred to a strangler-fig migration in about a year with the live question
being whether the structure can be improved now; then, after the profiles below, module/import cost
is to be IGNORED and attention returns to optimizing the pipeline structure itself.

What is now FACT from source (see the dated notes for `path:line` evidence):
- The package root imports the whole AR, persistence and evolution surfaces at module level and
  calls `Aether()` at import; `Aether.__init__` eagerly builds Crystallizer, utility system,
  LoadGate, mediator plane, MutationResearch and Nexus. MutationResearch was lazy once and was made
  eager by owner ruling 2026-08-03 because the bare constructor became a ValueError for unlucky
  callers. Any lazy design must route the bare constructors through Aether's builder.
- Import coupling into the three roots is narrow: MR only via aether.py; Nexus via aether.py and
  `spellbook.py:46/266` plus two examiner profiles; Crystallizer via three configuration classes,
  conduit.py, conduit_cluster.py and ~25 emit seams. This is also the strangler-fig boundary map.
- The phases directory carries `shared_compiler_executions.py` (1,516 lines) beside the eleven phase
  modules; the survey scope includes it. Phase 3 (1,035) and phase 5 (713) are the largest phases.

What is FACT from the component map (document tier - intent, to be confirmed in source):
- Phases 8-11 already export a serializable "phase8_11 codegen IR" with a dirty bit, capture/flush
  routines, ordered hash tuples and a creation cache whose executors "hydrate against current bound
  Spells". Phases 1-7 attach artifacts to Spell objects keyed by `selected_spell_id`; phase 5
  publishes onto `spellbook._spells_by_id`. So the epic's premise ("the plan is not an artifact")
  holds for 1-7 and is already partly false for 8-11.
- Phase 1 classifies parameters (explicit SpellMap/SpellContract defaults, then ordinary defaults as
  PLAIN, then annotation inference) and retains the annotation and the EXACT default object. Phase
  3 makes the world-dependent decisions (SpellMap default resolution over `_spell_id_pool`,
  collection DI by scanning all spells). Phase 5/8 already intern paths (PathRegistry/PathId) and
  sockets carry `param_path_id`. Existing-creation spells bypass 8-11. Phases run as per-spell
  units on PhaseScheduler worker threads with cancellation.

What was MEASURED (owner-run; artifacts under artifacts/ir_epic_gauntlet_baseline_20260925/):
- Gauntlet, gil=disabled, 5000 iterations: setup 259.7ms vs 40.5ms (dependency-injector) vs 40.1ms
  (dishka); hot_scopes/s 23,382 vs 35,491 vs 28,797; per-cycle create/cleanup competitive; worst
  iteration 20.9ms vs 3.4ms.
- cProfile gauntlet, 3.14, gil=enabled, 25 iterations: setup 347.6ms vs 28.6ms vs 61.6ms, of which
  `import melder` is ~270ms (477 modules executed vs 24 and 67; ~100ms is C-level file work). No
  compiler phase function appears in either top-40; codegen `compile` is 46 calls / 14ms. Hot path:
  865k Python calls vs 265k and 409k for identical work; per scope cycle ~16 RLock pairs, 42
  dict.get, 29 isinstance, 16.6 ULID-genexpr iterations; codegen'd creation bodies ~6us each.
  Caveat: on 3.14 the harness's cumtime interleaves across threads (the `cleanup` frame carries the
  whole run); trust ncalls/tottime and the single-threaded import rows only.
- Owner-reported, not on file: a 5-minute run reaches parity. UNKNOWN until the output is filed.

Conclusions the next reader can rely on:
- On this workload the compiler is NOT the setup bottleneck; import and eager boot are. The owner
  has chosen to ignore module cost for now. The IR epic is therefore justified on durability,
  hydration and the Mojo seam - never on setup or meld speed (Non-Goals stand).
- The hot-path gap is in the scope-cycle door (locks, ID minting, type checks), not in the compiled
  executors, and is outside this epic. A compiled orchestrator (dependency-injector) is only ~1.5x
  faster on the same object counts; that is the ceiling for "put the runtime in native code".
- A .so-compiled Mojo system moves the setup cost to dynamic-library load (dependency-injector's
  28ms is ~24ms of `_imp.exec_dynamic` for two modules); it does not remove it.

Design synthesis on the table (STRATEGY_DISCUSSION notes; nothing ratified):
- Option C: a custom value-only IR organised as a dialect stack - L0 facts (what Python told us),
  L1 requirements, L2 graph, L3 resolution, L4 plan - with a verifier per level, immutable nodes
  safe for parallel per-spell passes, and MLIR deferred to a post-port lowering inside Mojo.
- Pipeline reading: compile (0-4, per book, incremental per spell) -> link (5-6, per conduit, over
  IR plus a value-shaped world snapshot) -> plan (8-10) -> emit-and-wire (11 absorbing 7's
  revalidator registration). "Delay 5-7" is about what those steps READ, not when they run;
  conjure-time fail-fast is public behavior and stays.
- Level 0 = the bind-time capture of FACTS (signature, default kind, structured type refs, base
  chain, protocol members, spell kind, enums, fingerprints), cached by (module fingerprint,
  qualname). Decisions that need the world stay in passes over the IR. References are needed only
  to hydrate, to wire runtime callbacks, and to verify the capture is not stale.
- Late binding makes this an incremental compiler: unresolved sockets as first-class nodes, validity
  states on nodes mirroring SpellSystemStates, hash-keyed invalidation (a query model, not top-down
  passes). Failure mode to avoid: the same imperative control flow on dataclasses.
- Identity: spells by content SHA, indexes by binding key with ULIDs in a hydration-time translation
  map (the crystallizer's never-rehydrate-ULIDs law), existing instances and instance defaults as
  opaque handles bound at phase 11, callables as presence flags.
- Acceptance criterion to add on ratification: the closure test (phases 1-10 on a deserialized IR
  with user modules unimportable yield the identical plan).
- Survey record shape now carries three extra fields per phase: reflection points, Python-callback
  points, and world reads (registry/spellbook state consulted). The set of world reads is the
  query surface a pure-function port must make explicit.
- Parked, evidence attached: the lazy-boot lane (roots built on demand through Aether with the
  bare constructors routed through the builder; flag-gated emit/publication; PEP 562 facade).
  Worth doing when a subsystem is actually being strangled, not for import time.

UPDATE 2026-09-25 (late, before a compaction): the driver read is done and its results are in
task 1's notes and artifacts/ir_phase_survey_20260925/driver.md. Headlines: a dormant, signed
phase 2-5 export exists and phase 2's own NOTE reserves it for incremental recompile; phase-11
consumes step rows and an int-array transient plan; a full creation-cache hit skips only 8-11 while
1-7 run every conjure; the signature path has two determinism hazards and a duplicated helper;
phases 1, 2, 9, 10 are closed at signature/call level. Proposed tranche reorder: structural snapshot
and hydrator over the existing 2-5 export BEFORE any phase port. Owner authorized system-doc
corrections; boot order, conjure cache paths and the IR seams are now in the canonical maps.

LEVEL 0 (2026-09-25, source-backed): bind already runs the requirements finder and phase 1 borrows
the result through `spell.profile.resolution_profile`; `SpellResolutionProfile` is a documented
execution-model-independent phase 1-4 payload (only `requirements` populated, holds live objects).
The level-0 work is making that capture value-shaped, not adding a phase.

Where to resume: STORY-1 tranche task 1, step 3 - read `spell_requirements_finder.py` (three
chunks) and `spell_requirements.py`, complete `phase_01.md` (PARTIAL now), then phases 2-4.
Route: attention_board row `ir_phase_survey_1_4`; story and task handoff summaries carry the
step-level state.

Authored 2026-08-03 by `super_tester_0` on owner direction and left UNCLAIMED.
No agent owns it; no implementation has begun; nothing under `src/` was touched.

The idea came out of a benchmarking session, not a defect. Conjure is a compiler
and phase 11 already emits a compiled executor, which is why the 3.15 JIT gave
this workload +0.22%: the interpreter overhead was already removed at comptime.
What the compiler lacks is an IR, so its plan is object graph rather than
artifact - invisible to the crystallizer, undiffable by MutationResearch, and
recomputed from scratch on every restore.

Entry point is STORY-1, the phase survey, and it gates everything else for a
reason: this document describes what the phases are INTENDED to do, taken from
the architecture doc and the file layout. Nobody has read the phase source. Do
not design the schema until that is closed.

The two things most likely to go wrong: an IR symbol reaching the meld hot path
(there is an acceptance test for it, and a gauntlet baseline to catch it), and
this being pitched as a performance win when it is a durability and mutability
win.

UPDATE 2026-09-25 (fable_0): claimed on owner assignment. STORY-1 is open at
`tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md` with tranche task 1 routed on the
board and awaiting scope approval. Nothing under `src/` has been read beyond line counts; the
shared execution module beside the phases is now in the survey scope. Milestone 1 remains open.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
