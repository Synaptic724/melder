# Epic: Adaptive creation contexts - probe, harvest, report, regenerate

## Current Backlog Disposition
- Parked: 2026-09-28T00:57:27Z
- Disposition: backlog_by_owner; no active work.
- Owner's reason: it feels powerful, but the scan of the objects that exist says most have few dependencies -
  Melder's own composition is 58% width 0 / 23% width 1, depth <= 5; commandops' cache is 47 singleton roots
  (warm melds are door hits) and 4 `many` roots of width 1 and 5 - so the data-driven levers have little to work
  on there. Recorded for later: fifteen stories, the concrete strategies with predictions, the seam in source.
- What stands without this epic: the registration trim (S1) and the existing-object constants (S2a) need no PGO
  data - only the rows - and are the two measured/predicted wins on the real shapes; they can be picked up as
  plain tasks if the owner wants them without reopening the epic.
- Reopen trigger: an application with wide singleton consumers, deep transient trees or multi-thread creators,
  or the owner's word.

## Metadata
- Epic ID: EPIC-2026-09-27-adaptive-creation-contexts
- Status: blocked
- Owner: cowork
- Agent Name: fable_0
- Priority: p3
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z
- Target Window: opened 2026-09-27 on the owner's direction; idea collection first, one story at a time after
- Related Program/Initiative: SpellCompiler codegen (phases 8-11), Meld runtime, Creations, DevOps station,
  creation caches
- Supersedes: tickets/epics/backlog/2026-09-27_codegen_pgo_strategies_epic.md (its measurements and its open story move
  here; the owner widened the direction from "strategies" to a creation context that observes, reports and
  regenerates itself)

## Problem / Opportunity
A Melder creation context is compiled once per spell from static knowledge - existence, sockets, defaults -
and never from what happens at runtime: which singletons are already stored when a consumer is built, which
override key sets recur, which transients are built by which threads for which consumers, which scopes come and
go. dishka and dependency-injector compile a provider once and can never change the object that builds; Melder
can. The executor slots of a `CreationContext` are self-replacing (cold -> hot -> specialized), a spell's context
and plan can be rebuilt inside a rebuild window that freezes and drains the spell-index gate, override melds
compile one plan per key set on first use, and the DevOps station carries a fact registry with information
strategies. That is the substrate for a creation context that observes itself for a window (a probe), records
who built what, for whom, on which thread, harvests that into a profile with a report, and emits a new version
of itself specialized to the observed shape - swapped in at a natural window, guarded, with the plain body
always one deopt away.

The proof gathered on the owner's real application (commandops, 2026-09-27) sets the scale honestly: 47 of its
51 cached roots are singletons whose warm melds are door hits (already folded to ~150-180 ns); its 4 `many`
roots pay 400-690 ns of a 650-1220 ns meld in disposal registration, and the singleton-capture style recovers
2-7% there. So the program has one proven lever today (the registration trim) and a set of data-dependent levers
whose worth on DI-heavy shapes (wide singleton consumers, deep transient trees, multi-thread creators) the probe
is meant to establish before anything is emitted.

EVIDENCE:
- src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:600-758
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:119-165
- src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:385-507
- artifacts/pgo_strategies_20260927/vm_commandops_melc_ledger_gil0_20260927.md
- artifacts/pgo_strategies_20260927/vm_commandops_shapes_gil0_20260927.md
- artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md

## MRP Alignment (Most Reasonable Product)
The core is a runtime that gets faster the longer it runs without trading correctness for speed: the default
path with everything off stays byte-identical; a probe costs a bounded, sampled amount and then removes itself;
every regenerated version is guarded and deopts to the plain body; a version is selected only where its own
measurement says it wins; the report is the user-visible truth of what the runtime did. Discovery and
measurement come first, one story at a time, and the owner-run gauntlet decides.

## Ticket Contract
- ENTRY_GATE: the owner's direction (2026-09-27T23:42Z); this epic routed on `attention_board.md` through its
  active story/task.
- EXECUTION_BOUNDARY: `spell_compiler/codegen_creation_system/` (emitters, hydrators, strategies), the creation
  context and its factory and rebuild window, `conduit/creations/` (registration and disposal), `Spell` (a
  value-only profile slot), the DevOps station (report), `SpellbookConfiguration` (switches),
  `utilities/caching_system/` (manifest generation) - each story names its files; files claimed by another
  lane on the mailbox are not touched until that lane closes.
- DEPENDENCIES: artifacts/pgo_strategies_20260927/ (the proof); patch docs per story (system-impacting);
  the persistent gauntlet (`benchmarks/testing_other_di/`) owner-run for every ranking number.
- EXIT_GATE: every story accepted or parked with its numbers; a differential test proving the default-off path
  identical; the registration trim and the probe/report shipped with measured, owner-run wins; both canonical
  system documents updated and indexed.
- FAILURE_ESCALATION: DECISION_REQUEST before any change to what a warm meld does with the switches off;
  BLOCKER when a safe swap or harvest window cannot be evidenced for a version.

## Goals (Outcomes)
- One switch family on the configuration: profiling on/off, optimization on/off, window sizes.
- A probe creation context that samples itself for a window, then swaps itself out, harvesting per-site
  hits/misses and ns, per-constructor ns, and the creator context (thread, conduit/space, consumer root,
  override key set) into a value-only profile.
- A DevOps report that shows, per spell, the structure a conduit actually built, who built it, and which
  version of its context is live with its measured delta.
- Regeneration: a new version of a creation context emitted from the profile, swapped in at a natural window,
  guarded, deopting to plain; a version history the report can show.
- The proven lever shipped: `many` disposal registration trimmed to one append with per-key methods.
- Every idea in the catalogue below carried as its own story with a measured verdict: ship, park, or drop.

## Non-Goals (Explicit Exclusions)
- No always-on profiling; no change to the meld API; no JIT or bytecode tricks - codegen is the mechanism.
- No persistence of profiles until the persisted-profiles story earns it with numbers.
- MutationResearch, Crystallizer and Nexus observe; they do not optimize.

## Scope Boundaries
- In scope: the probe, the capture, the report, versioning/regeneration, the registration trim, data-selected
  styles, thread-affine stores, consumer-specialized transients, key-set prediction, persisted profiles.
- Out of scope: door changes beyond what a version swap already uses; anything a story has not opened.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner asked for the epic and one story per idea (2026-09-27T23:42Z); the design task of the
  styles story is the active lane.
- from_state: in_progress
- to_state: blocked
- transition_reason: Parked by the owner (2026-09-28T00:57:27Z): little value on the shapes that exist;
  everything recorded for later.

## Success Metrics
- Probe window: at most +11% per creation while open (measured +4..+11% count-only), 0 after the self-swap.
- Registration trim: >= 25% off a disposal-bearing `many` meld on the VM, confirmed owner-run on the gauntlet.
- A selected version never regresses the probe's own measurement; three deopts re-pin plain.
- Default-off path byte-identical (differential test) and within noise on the gauntlet.

## Requirements (Functional + Non-Functional)
- Every version carries a guard whose failure returns to the plain body with the same result.
- Swaps only at natural windows (post-success on the building thread, pool return, SpellSpace reset, warm
  conjure, revalidation) or inside a rebuild window; never under a meld that holds a build lock.
- Profiles are value-only (JSON-able): ints, floats, strings, tuples of those.
- Overlay rules: `Optional`/`Union`, no `getattr`/`hasattr` on owned code, rich docstrings, pytest unit-first,
  "Not run." until the owner reports.

## Constraints / Assumptions
- 3.14t free-threaded is the target; guards are single compares.
- Agent-side timing is directional (2-core VM); ranking numbers are owner-run.
- A story that touches a file claimed on the mailbox waits for that lane.

## Dependencies / External References
- artifacts/pgo_strategies_20260927/ (proof and runs)
- artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md (prior art: guard ladder, door epochs)
- tickets/epics/backlog/2026-09-27_codegen_pgo_strategies_epic.md (superseded; decision log and measurements)
- tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md (melder_2's thread-affine pools lever)

## Milestones (Track Progress)
- [x] Milestone 0: proof from a real application cache - the ledger, the live shapes, the registration split.
- [ ] Milestone 1: the registration trim shipped, default path identical, measured owner-run.
- [ ] Milestone 2: the probe + capture + report shipped default-off with the bounded, self-ending window.
- [ ] Milestone 3: the first regenerated version (data-selected singleton capture) shipped with the
      differential and deopt matrix and a measured win on a DI-heavy shape.
- [ ] Milestone 4: the remaining ideas measured and shipped, parked or dropped on their numbers.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-09-27-many-registration-trim - one append per `many` creation, per-key disposal methods.
      tickets/stories/backlog/2026-09-27_many_registration_trim_story.md
- [ ] Story: STORY-2026-09-27-probe-creation-context-harvest - the sampled, self-ending probe body and the
      trigger points that harvest it. tickets/stories/backlog/2026-09-27_probe_creation_context_harvest_story.md
- [ ] Story: STORY-2026-09-27-creator-thread-context-capture - who built it, where, for whom, on which thread.
      tickets/stories/backlog/2026-09-27_creator_and_thread_context_capture_story.md
- [ ] Story: STORY-2026-09-27-creation-profile-report - the DevOps report and its describe/reset verbs.
      tickets/stories/backlog/2026-09-27_creation_profile_report_story.md
- [ ] Story: STORY-2026-09-27-creation-context-versioning - regenerate a new version from the profile, swap
      at a natural window, deopt. tickets/stories/backlog/2026-09-27_creation_context_versioning_and_regeneration_story.md
- [ ] Story: STORY-2026-09-27-probe-selected-codegen-styles - styles chosen by measured data; singleton
      capture first (moved here from the superseded epic).
      tickets/stories/backlog/2026-09-27_probe_selected_codegen_styles_story.md
- [ ] Story: STORY-2026-09-27-thread-affine-creation-stores - per-thread registration when the profile shows
      single-thread creators. tickets/stories/backlog/2026-09-27_thread_affine_creation_stores_story.md
- [ ] Story: STORY-2026-09-27-consumer-specialized-transients - plans specialized to their door and consumer.
      tickets/stories/backlog/2026-09-27_consumer_specialized_transients_story.md
- [ ] Story: STORY-2026-09-27-override-key-set-prediction - precompile the key sets the profile saw.
      tickets/stories/backlog/2026-09-27_override_key_set_prediction_story.md
- [ ] Story: STORY-2026-09-27-persisted-creation-profiles - carry the profile and the chosen version in the
      `.melc` manifest. tickets/stories/backlog/2026-09-27_persisted_creation_profiles_story.md
- [ ] Story: STORY-2026-09-27-pgo-harvester-cycle-and-emission - PGO=true arms the harvester; a spell that
      finishes its cycle emits its harvest after the cycle into a durable spell-based slot and to its consumers.
      tickets/stories/backlog/2026-09-27_pgo_harvester_cycle_and_emission_story.md
- [ ] Story: STORY-2026-09-28-harvest-driven-phase-regeneration - the second part: the profile enters the phase
      cycle (a deferred 8-11 pass; planner and codegen discovery read it) and the rebuilt executor is published
      through the existing window. tickets/stories/backlog/2026-09-28_harvest_driven_phase_regeneration_story.md
- [ ] Story: STORY-2026-09-28-codegen-cost-model-planner - a phase-10 cost model that predicts each candidate
      body's ns from the profile and the rows, ranks the tournament's shortlist, and recalibrates from the
      measured windows. tickets/stories/backlog/2026-09-28_codegen_cost_model_planner_story.md
- [ ] Story: STORY-2026-09-28-codegen-strategy-certification-harness - measure S1-S7 on the emitted bodies
      before any system is built. tickets/stories/backlog/2026-09-28_codegen_strategy_certification_harness_story.md
- [ ] Story: STORY-2026-09-28-batched-many-registration-lazy-index - one scope list, lazy per-key index on
      the first purge (S5). tickets/stories/backlog/2026-09-28_batched_many_registration_lazy_index_story.md

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: keep the idea catalogue below and the story verdicts aligned as measurements land.
- [ ] Task: the differential test harness (plain vs any version, same objects, same errors) shared by every story.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Every story accepted, parked or dropped with numbers; Milestones 1-3 shipped default-off; owner-run gauntlet
  speedups recorded; deopt matrix green owner-run; canonical docs and indexes current; assets rebuilt last.

## Risks / Mitigations
- Probe cost eats the win -> sampled window that swaps itself out; measured before anything else.
- A version regresses (chain8 showed +20% for blind capture) -> selection by measured delta only; three deopts
  re-pin plain.
- Stale version after purge, transfer, notch, cleanup or pool return -> guards on the existing epochs and
  gates; differential test per version.
- Lock-free registration strands an object built after `cleanup()` -> the refusal contract is redesigned before
  trimmed B ships; trimmed A keeps the lock.
- Thread-affine state on Windows follows the OS thread -> measured per platform before shipping.

## Applicable Anti-Patterns
- [ ] No implementation before a story's measurement plan and the owner's pick.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.
- [ ] No version without a guard and a deopt test; no probe that runs unsampled on the warm path.
- [ ] No closure while required stories are incomplete or unaccepted.

## Validation / Test Approach
- Unit-first on emitters, registries and selection; component tests on the probe window swap, the harvest and
  the report; the differential matrix (plain vs each version, same objects, same errors); the deopt matrix
  (purge, cleanup, transfer, notch where dynamic, pool return); the experiment harness on DI-heavy shapes;
  the persistent gauntlet owner-run.

## Rollout / Adoption Plan
- Registration trim (proven) -> probe + capture + report (default-off tool) -> first regenerated version ->
  each further idea behind its own switch, measured, shipped or parked.

## The CreationContext Is the Host
Owner's rule (2026-09-27T23:54Z): every idea must fit the `CreationContext` object, so the optimization is
spell-based and can happen dynamically. Today the context is spell-owned (`spell._creation_context`, published
through `_creation_context_switch`), holds three self-replacing executor slots plus the dynamic gate handles, and
the meld doors hold the context and re-read its slots per call. Where each idea lands:
- PGO harvester: cycle state (window counter, one-shot emitted flag), the durable profile reference and the
  emission call at cycle end live on the context; PGO=true arms it at publication.
- Probe body: an executor variant installed into the same three slots for the window; cycle end swaps the plain
  or regenerated executors in place - the existing cold -> hot swap, extended.
- Creator/thread capture: fields of the probe body's counters, folded into the profile at harvest.
- Report: a DevOps information strategy that reads the profile the context emitted; no context change.
- Versioning: a version key on the context and a value-only history on the spell; a swap is an in-place slot
  write (doors untouched); replacing the context object is the rebuild path with its epoch bump.
- Data-selected styles, thread-affine stores, consumer specialization, key-set prediction: each is a
  regenerated executor the context installs into its slots, with the guard inside the executor.
- Registration trim: the store side; it changes the line the context's executor runs, not the context.
- Persisted profiles: `load_cached(...)` already builds a context from cache outputs; the persisted version
  and profile enter through it.
EVIDENCE:
- src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110
- src/melder/aether/conduit/meld/creation_context/creation_context.py:189-240
- src/melder/aether/spellbook/spell.py:483-490

## Concrete Strategies (certification candidates, 2026-09-28T00:51:22Z)
Owner's rule: define each strategy precisely and measure it in the harness BEFORE the system is built, so a
5k-LOC lane is not opened for nothing. Each line: precondition (from rows or profile), the exact change in the
emitted body, the predicted saving from the price model, how it is measured. Predictions are VM-directional.
- S1 Registration trim. Precondition: none (store shape). Change: `many_store.add_many_creations(sid, v,
  has_disposal_methods=True, disposal_methods=dm)` -> one append into one bucket; disposal reads the per-key
  method list recorded once (at hydration from the rows). Predicted: -200..-500 ns per disposal-bearing many
  creation. Measured standalone: 305-384 -> 103-120 (lock kept) / 62-63 (lock-free first-use double check).
- S2a Existing-object constants. Precondition: `spell_is_existing_creation` and automatic posture (a rebind after
  conjure is refused, so the instance cannot change). Change: `c1 = spells[1]._owner_creations; v1 =
  c1._creations.get(sid1); if v1 is None: ...` -> `v1 = k1` (a namespace constant bound at hydration). Predicted:
  -23 ns per site, no guard. commandops ContextRoot has 4 such sites (-92 of 1136-1219).
- S2b Unique captures inside the lowering ("cache first"). Precondition: unique site, hit rate 100% over the
  window (or dynamic posture, which needs the guard). Change: the read -> `if s1._door_epoch == e1: v1 = k1`
  else the read/miss path. Predicted: -8 ns per site (23 -> ~15). Replaces today's specializer, which emits
  through the older manifest compiler and lost the flattening (styles story HYPOTHESIS).
- S3 Miss-first ("does not exist, always make it"). Precondition: shared site with hit rate 0 over the window
  (short-lived per-space/per-conduit scopes). Change: skip the store read before the build. Predicted: -23 ns on
  a path that also pays a constructor and a registration - under 2%; listed for completeness, not pursued
  unless the profile shows scope churn.
- S4 Door-specialized prologue. Precondition: every meld in the window came through one door (conduit or
  SpellSpace). Change: `many_store = meld._spellspace_creations; if None: many_store = meld._conduit_creations`
  -> the one store read; a per-door version, no guard. Predicted: -15 ns per disposal-bearing plan run.
- S5 Batched registration with a lazy per-key index. Precondition: the profile shows no targeted purge of the
  spell (purge count 0) - cleanup disposes the whole scope. Change: append `(sid, v)` to one scope list, no
  per-key bucket; the first purge builds the per-key index once (O(n)) and switches the scope back. Predicted:
  -40..-60 ns beyond S1 (103 -> ~45). Guarded by the purge verb itself, not by the warm path.
- S6 Thread-affine append. Precondition: one creator thread over the window. Change: a `get_ident()` compare
  and a per-thread bucket instead of the store lock; a foreign thread deopts to the locked path. Predicted:
  -30..-40 ns (lock 57-67 -> compare ~20-30); contention at threads > 1 is the real target, owner-run.
- S7 Override key-set precompile. Precondition: key sets observed. Change: compile at harvest instead of first
  use. Predicted: cold-start only; no warm-path saving. Last.
Expected totals on the real shapes (S1+S2a+S2b+S4+S5): Worker 650-853 -> ~300-330 (-50..-60%); ContextRoot
1136-1219 -> ~500-560 (-55%); a wide8 many root over uniques -8 x 8 = -64 (~12%), over existing objects
-23 x 8 = -184 (~33%); singleton-root warm melds: 0 (door hits). PGO's own data buys S2b, S4, S5, S6; S1 and
S2a need only the rows.
Measurement before implementation: one harness module that captures the plain emitted body per shape (as the
probe prototype does), applies each strategy as a source transform, executes it, and times plain vs each and
all combined; results land in the artifacts and decide which strategies are certified.

## Idea Catalogue
One line per idea: the signal it needs, the mechanism, the guard, the expected win. Measured numbers are marked;
everything else is HYPOTHESIS until its story measures it.
- Registration trim (MEASURED): no signal needed; one append into one bucket, per-key methods; the store lock
  kept (A, 103-120 ns) or a double-checked lock-free append (B, 62-63 ns) against 305-384 today; 25-45% of a
  disposal-bearing `many` meld.
- Probe body (MEASURED cost): count-only +4..+11% per call while the window is open, timed +90..+130%; the
  window ends by self-swap; trigger points: N calls, elapsed time, or a natural window (pool return, reset,
  warm conjure).
- Creator/thread capture (HYPOTHESIS): per creation in the window record thread ident, door (conduit id or
  space id, root or lesser), consumer root spell id and override key tuple; cost of the capture UNKNOWN.
- Report (HYPOTHESIS): one information strategy over profile records held on spells, with a describe verb and
  a reset; shows structure, hit rates, ns, creators, live version and delta.
- Versioning/regeneration (HYPOTHESIS): a `CreationContextVersion` per emitted body (plain, probe, specialized
  by style key), swapped through the self-replacing slots at a natural window, guarded by the existing epochs;
  history in the report.
- Singleton capture selected by data (MEASURED blind): -14% wide8_singleton, +20% chain8_singleton, -2..-3%
  narrow; 2-7% on commandops; selection by hit rate and delta makes it safe.
- Thread-affine stores (HYPOTHESIS; melder_2 measured -6..-7% per cycle for thread-affine shell pools on Linux):
  per-thread `many` buckets and lock-free registration when the profile shows one creator thread per scope.
- Consumer-specialized transients (HYPOTHESIS): plans specialized to their door (drop the `many_store`
  prologue branch, ~15 ns), child-only transients kept inlined, providers proven stable pinned as constants.
- Override key-set prediction (HYPOTHESIS): compile the observed key sets at harvest instead of first use;
  pre-size operand tuples; key-set frequency in the report.
- Persisted profiles (HYPOTHESIS): the profile and the chosen version key ride the `.melc` manifest
  (generation bump) so the next process starts specialized - optimistic PGO across processes.
- Harvest-driven regeneration (FACT for the seam, HYPOTHESIS for the cost): `resolution_required` already runs
  one deferred 8-11 pass per spell under the rebuild window; phase 10 records candidate styles and phase 11
  selects one; the profile becomes a discovery input plus a lighter trigger that works in automatic worlds.
- Cost-model planner (MEASURED seed): the ledger's static prices reproduced the live commandops shapes; as a
  phase-10 heuristic it ranks candidate bodies before emission so a bounded tournament (attempt count on the
  spell, carried by hydration) measures only the top few.

## Open Questions
- Profile granularity: per spell, per (spell, door), per override key set?
- What is "the trigger point": a call count, elapsed time, or the natural windows - or all three, configurable?
- Where the profile lives: on the spell (value-only) mirrored into the DevOps registry, or registry only?
- Which levers pay on the owner's other applications (wide singleton consumers? multi-thread creators?) -
  the probe's first job is to answer this with the report.

## Decision Log
- 2026-09-27T23:42:45Z (owner): make an epic and a story per idea; the direction - unlike dishka and dependency-injector
  Melder can capitalize on a changing object: a probe-based creation context collected after a trigger point and
  harvested, capturing thread context, who made it (which conduit) and what it was made for, dynamic reporting,
  then a modified creation context and codegens put out as a new version for 5-10% or more.
- 2026-09-27T23:42:45Z (fable_0): this epic supersedes EPIC-2026-09-27-codegen-pgo-strategies; its exploration
  measurements stand, its open styles story and design task move here; the old epic goes to review pending the owner's
  closure word. Registration trim is the first story because it is the only measured >= 10% lever on the real
  cache; the probe/report is the owner's tool and the second.

- 2026-09-27T23:54:47Z (owner): PGO mode - turn it on, it harvests, then implements the result in a durable
  state, spell-based so it happens dynamically; every idea fits into the creation_context object (that is the
  play); a harvester armed by PGO=true; a spell that finishes its cycle actively emits its data after the
  cycle and shares it with some areas; a story to investigate each idea. Done: the host section above, an
  investigation task at the head of every story, and the harvester story.

- 2026-09-28T00:18:56Z (owner): the second part - harvest upon revalidation and pass the data into the cycle of phases
  1-11 so the phases consume it; this should work well. fable_0 located the seam in source (deferred 8-11 pass,
  planner/codegen discovery, the dynamic-only `invalidate_spell`) and drafted the twelfth story.

- 2026-09-28T00:28:44Z (owner): a flag triggered from inside the creation context (optional), plus a system way
  to harvest manually and revalidate one spell or all spells; not an invalidation - a full revalidation of phases 8-11
  only, with the extra data added at phase 8 so the later phases change how objects are created. fable_0:
  the context holds its spell, the deferred pass is exactly phases 8-11, phase 8's analyzer chain is the entry
  for the data (recorded in the harvest-driven regeneration story).

- 2026-09-28T00:33:12Z (owner): regenerate from the creation context directly, unbind/rebind under a closed gate, try 3-5
  candidates and keep the best (maybe 10%). fable_0: the trial loop is adopted as the tournament requirement of
  the versioning story; unbind/rebind is rejected from source (removal unregisters the index and cleans the
  Spell; bind after conjure is refused in automatic worlds) in favour of the 8-11 pass under the rebuild
  window, which is the closed-gate regeneration the owner means.

- 2026-09-28T00:37:47Z (owner): with PGO on the spell logs an attempt count that hydration carries so PGO stops after x
  tries and leaves the object alone; each attempt remakes the object and retests, the context logs the speed
  into the spell, the faster one is kept; in phases 8-11 a builder system can guess the speed of combinations
  from heuristics without generating code; the probe can tell what existed and what did not when the object
  was made, how often, and the order for uniques/singletons. fable_0: thirteenth story (cost-model planner);
  attempt budget on the versioning and persisted-profiles stories; scope is visible to the probe (stores carry
  their owner conduit and scope ids), recorded on the capture story.

- 2026-09-28T00:47:00Z (owner): maybe no time at all - the removals are deterministically helpful, the strategies do the
  trick, new optimizations become new strategies. Adopted: certified strategies with profile preconditions,
  applied at regeneration without runtime timing; the tournament is opt-in verification. fable_0: the one
  counter-example (blind capture +20% on chain8) is an emitter difference, not an inherent trade - recorded
  on the styles story with the ranges.

- 2026-09-28T00:51:22Z (owner): the strategies are little, well-defined things (does not exist -> always make
  it; cache first then take it; trim disposal registration for specific objects - the rows already carry the
  data); define them concretely and TEST them before implementing the ~5k-LOC system, so the 5-10% is known
  first. fable_0: the Concrete Strategies section above (S1-S7 with preconditions, transforms, predictions)
  and a proposed certification harness that measures them on the emitted bodies with no src change.

- 2026-09-28T00:57:27Z (owner): record everything in the epic, a story for every idea, and shelve it - it feels powerful
  but the scan of the objects that exist says most have few dependencies. fable_0: two more stories (the
  certification harness; batched registration), the parked disposition above, every story and the design
  task moved to backlog, the board row removed; S1 and S2a noted as the data-free wins that survive the park.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (proof and every run; created by the superseded epic's lane)
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md (prior art)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps as stories ship.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - probe; harvest; creator context; report; versioning; registration; styles
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: PLAN
  CLAIM: Tranche order from the numbers: (1) registration trim - the only measured lever >= 10% on the real
    cache, no probe needed; (2) probe + creator capture + report - the owner's tool, default-off, self-ending
    window; (3) versioning with data-selected singleton capture as the first regenerated version; (4) the
    rest measured through the report on the owner's applications. Each story opens with a measurement plan
    and patch docs before src.
  EVIDENCE:
  - tickets/tasks/backlog/2026-09-27_probe_creation_context_design_task.md:250-330
  - artifacts/pgo_strategies_20260927/vm_many_registration_split_gil0_20260927.md
  IMPACT: Order decides which files move first (creations.py + the one emitted line) and keeps the meld doors
    untouched while melder_0's lane holds them.
  NEXT: owner picks the first story to open; until then the styles story's design task stays the active lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
STATE 2026-09-27T23:42:45Z: IN_PROGRESS. Epic opened on the owner's direction with ten stories (nine new, drafted;
the styles story moved here with its active design task). Proof from the commandops cache is in the artifacts.
Resume from the active story's latest STATE line; the owner's pick of the first story is pending.
STATE 2026-09-27T23:54:47Z: IN_PROGRESS. Eleven stories; the CreationContext named as the host of every idea; the PGO
harvester story added. Owner's pick of the first story pending.
STATE 2026-09-28T00:18:56Z: IN_PROGRESS. Twelve stories; the harvest-driven regeneration story carries the
phase-cycle seam from source. Owner's pick of the first story pending.
STATE 2026-09-28T00:37:47Z: IN_PROGRESS. Thirteen stories; tournament with an attempt budget carried by hydration; the
cost-model planner drafted with the ledger as its seed. Owner's pick of the first story pending.
STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner). Fifteen stories drafted under this epic, all in stories/backlog/; the
design task in tasks/backlog/ with the proof notes; the superseded PGO epic parked beside this one. Reopen on the
owner's word or on an application whose shapes the scan did not show.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
