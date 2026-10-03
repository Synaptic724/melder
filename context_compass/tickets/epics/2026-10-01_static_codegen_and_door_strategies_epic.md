# Epic: Static codegen and door strategies - the certified, data-free wins on the emitted bodies and the door

## Metadata
- Epic ID: EPIC-2026-10-01-static-codegen-and-door-strategies
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-10-01T00:53:45Z
- Updated: 2026-10-03T21:31:58Z
- Target Window: opened 2026-10-01 on the owner's split; one strategy lane at a time, S1 first
- Related Program/Initiative: SpellCompiler codegen (phases 8-11, site-plan lowering), Creations, the meld doors
- Split from: tickets/epics/2026-09-27_adaptive_creation_contexts_epic.md (now the PGO epic), on the owner's
  directive 2026-10-01: "split this up into 2 separate epics ... non-pgo strategies and pgo strategies ... go with
  non-pgo first". This epic carries every strategy that needs no runtime profile; the PGO epic keeps the rest.

## Problem / Opportunity
The certification harness measured the concrete strategies on the real emitted bodies (VM, 3.14t, GIL off; two
runs within 5%). Three of them win on every shape they apply to, never lose, and need nothing but the phase-11
rows and the store shape - no probe, no harvest, no profile:
- S1 registration trim: a disposal-bearing `many` creation registers with one append into one bucket and the
  disposal side reads the spell's method list recorded once per key. Standalone 305-384 -> 103-120 ns (lock
  kept); -11..-49% of the plan alone.
- S8 lazy instance_results: a dict-mode root (any generic step, e.g. an existing object) builds
  `instance_results = {}` and stores every step into it on EVERY warm creation although only a miss reads it.
  Building it inside the misses only is -18..-24% of the plan on ContextRoot and wide8 over existing objects.
- S2a existing-object constants: an existing-object site is read through its owner store on every creation
  (`c = spells[i]._owner_creations; v = c._creations.get(sid); if v is None: ...`) although the object cannot
  change in an automatic world; a namespace constant bound at hydration is -11..-17% on those sites.
Combined with S2b and S4 (ALL): the plan -40..-67% and the whole meld -30..-52% on all five shapes, the two
commandops shapes included. For the 0-2 object melds most users make, the door is the cost (~130-180 ns of
every meld, the whole of a warm singleton meld at 164-177 ns); the four door strategies D1-D4 are predicted,
not measured, and get the same treatment: a door harness first, then the certified ones.

EVIDENCE:
- artifacts/pgo_strategies_20260927/vm_strategy_certification_gil0_20260930.md:1-60
- tests/experimentation/codegen_strategy_certification.py:1-452
- tickets/tasks/2026-09-30_build_codegen_strategy_certification_harness_task.md:150-222

## MRP Alignment (Most Reasonable Product)
Each strategy is a shape change with a contract that does not move: the same objects are built, disposed in the
same order with the same errors, returned from the same doors. Nothing is switched on at runtime and nothing
observes itself; the win is static and lands in the emitter, the store or the door. One lane at a time, each
with patch docs, a differential test against the plain body, a cache generation bump where executors change,
VM numbers for direction and the owner-run gauntlet for the ranking.

## Ticket Contract
- ENTRY_GATE: the owner's split directive (2026-10-01); this epic routed on `attention_board.md` through its
  active story/task.
- EXECUTION_BOUNDARY: `conduit/creations/` (registration and disposal), `spell_compiler/codegen_creation_system/`
  (site-plan lowering, hydrators, strategies), `utilities/caching_system/` (generation), the warm lanes of
  `Conduit.meld` and `SpellSpace.meld` for the door strategies; tests; the two canonical system documents and
  their indexes; the release note and `__version__` per the contribution guide. Each story names its files.
- DEPENDENCIES: the certification table (artifacts/pgo_strategies_20260927/); patch docs per story (every one
  is system-impacting: registry shape, emitted bodies, doors); the persistent gauntlet owner-run for ranking.
- EXIT_GATE: S1, S8 and S2a shipped and turned in with their notches, release-note sections, docs and assets;
  the door harness table landed and the certified door strategies shipped or dropped with numbers; a
  differential test per strategy; both canonical documents updated and indexed.
- FAILURE_ESCALATION: DECISION_REQUEST on any contract that would move (the cleaned-store refusal, disposal
  order, what a door returns after purge/cleanup/notch); BLOCKER when a strategy cannot keep it.

## Goals (Outcomes)
- S1 shipped: one append per disposal-bearing `many` creation, per-key methods, same disposal behaviour.
- S8 shipped: no `instance_results` dict on the warm path of a dict-mode root; misses build their own.
- S2a shipped: existing-object sites are hydration-bound constants in automatic worlds (epoch-guarded in dynamic).
- The door harness: D1-D4 measured on the live conduit over the real entries; the certified set named.
- The certified door strategies shipped behind the same gates.

## Non-Goals (Explicit Exclusions)
- Nothing that needs a runtime profile: S2b (hit rate), S3 (miss-first), S5 (purge count), S6 (creator thread),
  S7 (observed key sets), the probe, harvest, report and regeneration - those are the PGO epic's.
- S4 (single-door prologue): dropped, within noise in the harness.
- No change to the meld API, to Existence semantics or to what disposal does.

## Scope Boundaries
- In scope: S1, S8, S2a, the door harness, D1-D4 as certified.
- Out of scope: anything a story has not opened; the PGO epic's stories.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened on the owner's split directive (2026-10-01T00:53:45Z); S1's implementation task is
  the active lane.

## Success Metrics
- S1: >= 25% off a disposal-bearing `many` meld on the VM (Worker-shaped), confirmed owner-run; roots without
  disposal unchanged.
- S8: >= 15% off the plan of a dict-mode root on the VM; direct-mode roots byte-identical.
- S2a: >= 10% off the plan of a root with existing-object sites; no guard in automatic worlds.
- Doors: a measured table before any door edit; a shipped door strategy never changes a result.

## Requirements (Functional + Non-Functional)
- Every strategy ships with a differential test: plain vs new on the same objects, same disposal order, same
  ExceptionGroup shape, same errors.
- Executor-changing strategies bump the creation-cache generation so older executors are retired.
- Patch docs under `system_docs/patches/active/<patch_id>/` before any src edit; promoted at closure.
- Overlay rules: `Optional`/`Union`, no `getattr`/`hasattr` on owned code, rich docstrings, pytest unit-first,
  "Not run." until the owner reports.

## Constraints / Assumptions
- 3.14t free-threaded is the target; the GIL build must not regress.
- Agent-side timing is directional (2-core VM); ranking numbers are owner-run.
- A story that touches a file claimed on the mailbox waits for that lane.

## Dependencies / External References
- artifacts/pgo_strategies_20260927/ (the proof and the certification runs)
- tickets/epics/2026-09-27_adaptive_creation_contexts_epic.md (the PGO epic; sequenced after this one)
- tickets/tasks/backlog/2026-09-27_probe_creation_context_design_task.md (the commandops proof notes)

## Milestones (Track Progress)
- [x] Milestone 0: the certification table (S1-S8 measured on the emitted bodies).
- [x] Milestone 1: S1 shipped and turned in at 0.2.8216 (VM-measured; owner-run gauntlet Not run at turn-in).
- [x] Milestone 2: S8 shipped and turned in at 0.2.8217 (VM-measured; owner-run gauntlet Not run at turn-in).
- [ ] Milestone 3: the flat warm body (S9 + S11) shipped and turned in; S2a parked (owner, 2026-10-03).
- [ ] Milestone 4: the door harness table landed; the certified door set named.
- [ ] Milestone 5: the certified door strategies shipped or dropped with numbers.

## Stories (Required to Complete)
- [x] Story: STORY-2026-09-27-many-registration-trim (S1) - one append per `many` creation, per-key disposal
      methods. tickets/stories/completed/2026-09-27_many_registration_trim_story.md
- [x] Story: STORY-2026-10-01-lazy-instance-results (S8) - no instance_results dict on the warm path of a
      dict-mode root. tickets/stories/completed/2026-10-01_lazy_instance_results_story.md
- [ ] Story: STORY-2026-10-03-flat-warm-body-constants (S9 + S11) - site and store constants and live key
      objects on every shared site. tickets/stories/2026-10-03_flat_warm_body_constants_story.md
- [ ] Story: STORY-2026-10-01-existing-object-constants (S2a) - PARKED (owner, 2026-10-03: existing objects
      are rare). tickets/stories/backlog/2026-10-01_existing_object_constants_story.md
- [ ] Story: STORY-2026-10-01-meld-door-strategies (D1-D4) - a door harness, then the certified door
      strategies. tickets/stories/2026-10-01_meld_door_strategies_story.md
- [ ] Story: STORY-2026-09-28-codegen-strategy-certification-harness - the table that certified S1/S8/S2a
      (done; in review for the owner's closure).
      tickets/stories/2026-09-28_codegen_strategy_certification_harness_story.md

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: the differential test harness (plain vs strategy, same objects, same errors) shared by every story.
- [ ] Task: keep the certification table and the story verdicts aligned as landings re-measure.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- S1, S8, S2a and the certified door strategies shipped and turned in; each with its differential test, notch,
  release-note section, docs and assets; the owner-run gauntlet numbers recorded; the PGO epic's stories
  untouched.

## Risks / Mitigations
- S1: a build finishing after `cleanup()` must still be refused and disposed -> trimmed A keeps the store lock;
  B (lock-free) only with a written and tested refusal path.
- S1: extract/restore of many buckets and the disposal walk read the old `(object, methods)` tuples -> every
  reader migrates in the same change; the differential test covers purge, cleanup, clear_all, extract/restore.
- S8: a miss that builds its own dict must see the shared sites already read by the warm path -> the dict is
  built from the locals the plan already holds, then handed to `_construct_spell_instance`.
- S2a: a dynamic world can replace the object (notch) -> constant only in automatic posture; epoch-guarded
  constant otherwise.
- Doors: a stale entry after purge/cleanup/notch/transfer -> every retirement path must bump `_door_epoch`
  (D4's precondition is verified in source before it is built).

## Applicable Anti-Patterns
- [ ] No implementation before the story's patch docs and the owner's confirmation of the exact edit.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.
- [ ] No strategy without a differential test; no executor change without a generation bump.
- [ ] No closure while required stories are incomplete or unaccepted.

## Validation / Test Approach
- Unit tests on the store and the emitter; component tests on the emitted line through a real conjure;
  the differential matrix per strategy; the certification harness re-run after each landing; the owner-run
  gauntlet for ranking.

## Rollout / Adoption Plan
- S1 -> S8 -> S2a -> door harness -> certified doors; each its own lane with patch docs, a notch and a
  release-note section; assets rebuilt last per lane.

## Non-PGO Strategy Catalogue (owner request, 2026-10-01)
Every strategy that needs no runtime profile - decided from the phase-11 rows, the store shape and the frame
posture at conjure/hydration. One line each: ID, precondition, the change, the expected win (MEASURED on the VM,
3.14t GIL off, directional; otherwise HYPOTHESIS/UNKNOWN), the risk, how it is certified. Where a meld spends
its time today: a warm singleton meld is ALL door (164-177 ns); a transient tree is door (~170) + plan body
(reads, constructors) + registration (~200 per disposal-bearing many creation); a dynamic meld has NO warm lane
in `Conduit.meld` and pays the door frame, keyword marshaling, `_execute_admitted` and the index ticket on every
call.

### Door layer (every meld; the whole of a warm singleton meld)
- D1 Guard folding. Precondition: none (automatic doors). Change: fold the `_meld_hooks`, the spellbook-wide
  `_spellbook_validation_required` and `_cache_emit_required` reads into the spell's `_door_epoch` (every
  mutation of those bumps) so a hit reads entry, epoch compare, context identity. HYPOTHESIS -30..-40 ns. Risk:
  the hooks map is shared by reference and mutated in place; its writers must bump every door epoch (rare,
  O(spells)). In an automatic world the validation flag may be unable to flip after conjure (bind refused) -
  UNKNOWN, worth proving, then the read simply goes. Certified by the door harness.
- D2 Executor hold with epoch re-validation. Precondition: none. Change: the entry carries the executor; the
  cold -> hot slot swap re-mints the entry (or bumps the epoch) so the per-hit slot read goes. HYPOTHESIS
  -10..-20 ns. Risk: pinning a cold-door wrapper (the reason the slot is read per hit today). Door harness.
- D3 Route inline for singleton roots. Precondition: root Existence unique/unique_per_conduit (rows). Change: the
  entry carries the store and the sid; a hit is `store._creations.get(sid)` + None check in the door, no
  executor frame. HYPOTHESIS -60..-70 ns of ~170 (-35..-40%). Risk: the store identity per entry (lineage/
  cluster stores are repointed; those roots keep the executor). Door harness.
- D4 Instance at the door. Precondition: singleton root, automatic posture, and EVERY retirement path bumps
  something the door compares - purge, cleanup, transfer, notch AND a lesser's pool return, which resets its
  store with no spell-level epoch bump today (so D4 needs a per-store generation in the entry, not only the
  spell epoch). Change: the entry holds the object; a hit is unpack, compare, return. HYPOTHESIS ~80-90 ns per
  singleton meld (-50%). Risk: a stale object after a store reset; the audit comes first. Door harness.
- D5 Dynamic warm lane. Precondition: dynamic posture (today `Conduit.meld`'s warm lane is automatic-only:
  `not self.__dynamic_environment__`). Change: a mirror lane for dynamic conduits with the same guard ladder
  plus `resolution_required`, and the index ticket taken inline (`tickets.append(None)`, closed/enabled
  check, executor, `tickets.pop()`) exactly as `_execute_admitted` does. HYPOTHESIS -100..-200 ns per dynamic
  meld (the automatic lane measured 209 -> 111 ns on a solo meld). Risk: ticket pairing and the parked-rebuild
  re-check must be byte-identical; certified by the door harness in dynamic posture plus the rebuild-window
  tests. Likely the single biggest win for any application that runs dynamic worlds (Nexus frames do).
- D6 Cheaper ticket primitives. Precondition: dynamic. Change: `CreationGate.enabled` as a plain attribute if it
  is a property, `check_cleaned()` folded into the `_closed` read. HYPOTHESIS -10..-30 ns per dynamic meld.
  UNKNOWN until `creation_gate.py` is read whole. Rides with D5.
- D7 SpellSpace door parity. Precondition: none. Change: D1-D5 applied to `SpellSpace.meld`'s own entries
  (`spellspace_meld.py` mints them the same way). Same numbers per space meld. Door harness over a space.
- D8 Fused door-plan emission. Precondition: none. Change: emit the door with the plan so guard constants are
  literals in one function; invalidation re-emits through the existing slot swap. HYPOTHESIS -20..-40 ns beyond
  D1-D3; a new emission lane. Last; only if D1-D3 leave the door as the bottleneck.
- Dropped: none yet in this layer (melder_2's "single-check fast door" lever overlaps D1 - coordinate on the
  mailbox before any door edit).

### Plan body (generalized and many_only roots)
- S8 Lazy instance_results. MEASURED -18..-24% of the plan on dict-mode roots. Precondition: none. Story
  drafted.
- S2a Existing-object constants. MEASURED -11..-17% on roots with existing-object sites (automatic posture;
  epoch-guarded read in dynamic). Story drafted.
- S9 Site-object and owner-store constants. Precondition: the spell set of a plan is fixed per plan (any
  posture); the owner store `spells[i]._owner_creations` is fixed in automatic posture (transfer is dynamic-
  only). Change: bind `sI = spells[i]` and, in automatic posture, `cI = sI._owner_creations` as namespace
  constants at hydration; each shared site loses one tuple index and one attribute read. HYPOTHESIS -8..-12 ns
  per shared site. Risk: dynamic transfer repoints the store - keep the read there. Harness transform.
- S10 Subscript hits for long-lived stores. Precondition: the site's Existence is unique or unique_per_conduit
  (long-lived store; not per-space). Change: `v = d[sid]` in try/except instead of `.get` + `is None`.
  MEASURED micro: -4 ns per hit, +50 ns per miss (zero-cost exceptions: the KeyError path is 70 ns, not
  microseconds); net positive above ~12 hits per site per scope. Low value; harness transform.
- S11 Key-object identity at hydration. Precondition: cache-restored plans (marshal mints new str objects).
  Change: bind `sidN` to the live Spell's `spell_id` object so the dict lookup takes the identity fast path.
  MEASURED micro -1.5..-2 ns per lookup; free; rides with S2a/S9's hydrator pass.
- S12 Direct emission for the remaining generic step kinds (contract payloads with scalar/ref overrides,
  positional overrides, collection parameters). Precondition: rows. Change: emit them as direct steps so dict
  mode (and the generic `_construct_spell_instance` miss) disappears for more roots. HYPOTHESIS: the S8 saving
  again on those roots plus the generic call's own cost; needs `_is_direct` and the generic emitter read.
  Medium; after S8.
- S13 `list[T]` collection parameters over fixed members. Precondition: automatic posture, members all
  singletons. Change: build the list from constants (one list literal) instead of per-member reads. HYPOTHESIS
  small; UNKNOWN whether the list is rebuilt per creation today (it must stay fresh if callers mutate it).
- Dropped: S4 single-door prologue (within noise, measured 2026-09-30); S39 constant binding as default
  arguments or closure cells (globals are already the fastest on 3.14, measured 2026-10-01).

### Registration and the store
- S1 Registration trim. MEASURED 204-207 -> 104-111 ns standalone; -11..-49% of the plan. Active lane.
- S15 Explicit lock calls on the hot store verbs. Precondition: none. Change: `lock.acquire()` /
  `try/finally: lock.release()` instead of the with-statement on `register_many`, disposal-bearing
  `add_creation` and the purge detach. MEASURED micro -14 ns per locked operation (the with-statement's own
  cost). Style cost only; the A3 shape of S1. Ships with S1 if the owner takes A3.
- S17 Lock-free many append (trimmed B). Precondition: a refusal design - a post-append recheck of
  `_cleaned`/store identity that removes and disposes the stranded object without double-disposing it against
  a concurrent cleanup walk. MEASURED 62-63 ns standalone (-40 beyond A). Not safe yet: a design task before
  any ship.
- S18 Record-free whole-scope disposal (S5 as a static shape). Precondition: none if the purge verb builds the
  per-key index lazily (the first targeted purge pays O(n) once per scope). MEASURED plan increment -40..-60 ns
  beyond S1. Decide after S1 lands and the first-purge cost is measured; today filed under the PGO epic.
- Dropped: S22 store lock RLock -> Lock (a wash on 3.14t, measured 2026-10-01: 44 vs 43 ns with-statement,
  30 vs 31 explicit).

### Override melds (key-set plans)
- O1 Key-tuple construction per override meld. UNKNOWN: whether `SitePlanOverrideRuntime` sorts or
  canonicalizes the keys on every call; if so, an insertion-order tuple keyed lookup with canonicalization
  only on a miss saves the sort per call. HYPOTHESIS -20..-60 ns for two or more keys. Read first.
- O2 The dynamic lane (D5) covers override payloads as the automatic lane does.

### Scope lifecycle (melder_2's gauntlet lane; coordinate, do not duplicate)
- L1 thread-affine shell pools (melder_2 measured -6..-7% per cycle on Linux), L2 one-lock anonymous link, L3
  single-check fast door (overlaps D1). L4 (new, ours): with S1 the disposal-bearing SpellSpace exit still
  swaps both maps and walks the record; a thread-confined exit could dispose the record newest-first without the
  swap. HYPOTHESIS small.

### Cold path (conjure and first meld) - not meld-time, listed for completeness
- C1 Lazy per-root plan hydration at first meld instead of at conjure. UNKNOWN whether already lazy.
- C2 Structural snapshot replay and creation-cache full hits: SHIPPED (0.2.72-0.2.8215).

### Not static (PGO epic)
- S2b unique captures (hit rate), S3 miss-first (hit rate 0), S5 as owner-dependent (purge count), S6
  thread-affine append (creator thread), S7 key-set precompile (observed key sets).

## Recommendation (fable_0, 2026-10-01)
1. S1 now, in the A3 shape (explicit lock calls; measured, ten lines): the largest certified single lever on
   transient-with-disposal melds and the smallest blast radius (one store, three emitted lines).
2. One emitter lane next - "the flat warm body": S8 + S2a + S9 + S11 (+S10 and S12 if the harness certifies
   them). All four live in `site_plan_lowering.py` and the hydrator, each is a few lines, and together they
   remove every per-creation read that the rows already answer. Certify S9/S10/S11 in the harness first (an
   afternoon), then ship under one release-note section with one notch per strategy.
3. The door lane: the epoch audit (including a per-store generation for lesser pool returns), the door harness,
   then D1 + D2 + D3; D5 if the owner's applications run dynamic worlds (it is the only lever for them and the
   biggest); D4 only if the audit is clean. This is the only lever for 0-2 object melds.
4. Owner-run gauntlet after each lane; S18/S17 decided on those numbers; the PGO epic after.
Amended 2026-10-01 (owner: Melder's real use is dynamic; the dynamic checks stay): the door lane runs the
audit, then the harness in dynamic posture, then D5 (every dynamic guard kept inline, only the frames removed),
then D1-D3 on both lanes. S1 and the emitter lane are posture-independent and unchanged.
Expected on the VM when all three lanes land: transient trees -40..-75% of the plan (measured), warm singleton
melds -40..-50% (predicted), dynamic melds -30..-50% (predicted).

## Open Questions
- S5 (batched registration, lazy per-key index) is guarded by the purge verb itself, so it may be static-safe
  without a profile; decide after S1 lands and the index cost of a first purge is measured.
- D4's precondition: does every retirement path (purge, cleanup, notch, transfer, pool return) bump
  `_door_epoch`? To verify in source before the door story opens.

## Decision Log
- 2026-10-01T00:53:45Z (owner): split the work into two epics - non-PGO strategies and PGO strategies - and go
  with non-PGO first. fable_0: this epic carries S1, S8, S2a and the door strategies (all static: rows and store shape
  only); the adaptive-creation-contexts epic is retitled the PGO epic and queued behind it with S2b, S3, S5,
  S6, S7, the probe, harvest, report and regeneration stories; S4 dropped (noise). S1 opens first because it
  is the largest certified single lever and its design is already sketched (trimmed A).

- 2026-10-01T01:25:22Z (owner): list every non-PGO strategy you can think of; no implementation now. fable_0: the
  catalogue above (door D1-D8, plan S8/S2a/S9-S13, store S1/S15/S17/S18, overrides O1, lifecycle L1-L4, cold C1-C2);
  four micro-shapes measured on the way (S22 and S39 dropped, S10/S11/S15 sized); the recommendation
  section names the order. S1 stays proposed, not implemented.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (the certification table; shared with the PGO epic)
  - artifacts/many_registration_trim_20261001/ (verb shapes, the four static micro-shapes, the S1 apply script and
    landing logs, 2026-10-01 and 2026-10-02)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps as the stories ship.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - registration trim; lazy instance_results; existing-object constants; meld door strategies
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-10-01T00:53:45Z
  TYPE: PLAN
  CLAIM: Lane order from the certified table and the design state: S1 (largest certified lever, trimmed A sketched,
    store-side change with one emitted line), then S8 (emitter-only, no store change, -18..-24% on dict-mode
    roots), then S2a (hydrator constants, automatic-posture precondition), then the door harness (D1-D4 are
    predictions and the door is the whole cost of a 0-2 object meld), then the certified doors.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_strategy_certification_gil0_20260930.md:1-60
  - tickets/tasks/2026-09-30_build_codegen_strategy_certification_harness_task.md:150-222
  IMPACT: Decides which files move first (creations.py plus the one emitted line) and keeps the doors untouched
    until their own harness has numbers.
  NEXT: the S1 implementation task: read creations.py whole, the emitter's registration line and the hydrators'
    constants, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-02T18:01:21Z
  TYPE: FACT
  CLAIM: Milestone 1 reached pending the owner's run: S1 landed at 0.2.8216 (A3), docs, graph, assets and bundles
    current; the lane sits in review. Next lane per the recommendation: S8 (lazy instance_results), then S2a with
    S9/S11 in the same emitter pass; the door lane after, audit first. The owner's Codex MCP instruction
    (special_instructions/codex_mcp.md) replaces the mailbox for agent notices; melder_0/melder_2/muse_0 have no
    reachable chat today, so landings are announced through the tickets and the board until they do.
  EVIDENCE:
  - tickets/tasks/2026-10-01_implement_many_registration_trim_task.md:300-330
  - special_instructions/codex_mcp.md:1-20
  IMPACT: S8's story opens on the owner's word; nothing else in the epic moved.
  NEXT: owner turns S1 in; open the S8 task (patch docs first).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-02T19:09:13Z
  TYPE: DECISION
  CLAIM: Owner (2026-10-02): S1 turned in (task and story moved to completed/, closed by directive, gauntlet Not run)
    and "move onto other things". Milestone 1 is checked as landed; S8/S2a/doors stay drafted and unrouted; the
    epic keeps no board row until the owner names the next lane.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-01_implement_many_registration_trim_task.md:1-12
  - tickets/stories/completed/2026-09-27_many_registration_trim_story.md:1-10
  IMPACT: No active lane in this epic; nothing is in flight on the tree.
  NEXT: owner names the next lane (S8 per the recommendation, or other work).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-03T21:22:15Z
  TYPE: DECISION
  CLAIM: Owner (2026-10-03): S8 turned in (task and story moved to completed/, closed by directive, gauntlet Not
    run) together with two standalone defect lanes found on the way - annotation matching by address key
    (0.2.8218) and the executor-cache world stamp (0.2.8220). Milestone 2 is checked. Next lane per the
    recommendation: S2a with S9/S11 (one emitter pass; the harness certifies S9/S11 first), patch docs first;
    the epic keeps no board row until the owner names the next lane.
  EVIDENCE:
  - tickets/stories/completed/2026-10-01_lazy_instance_results_story.md:1-10
  - tickets/tasks/completed/2026-10-03_implement_lazy_instance_results_task.md:1-12
  IMPACT: No active lane in this epic; the tree is at 0.2.8220 with every landing's docs and assets current.
  NEXT: owner names the next lane (S2a per the recommendation, or other work).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-03T21:31:58Z
  TYPE: DECISION
  CLAIM: Owner (2026-10-03): "existing objects are very rare but sure, if it helps with everything in general ...
    implement the next steps, ignore the PGO epic, test it first." fable_0: the emitter pass is S9 + S11 (every
    shared site; certified in the harness before the patch docs), S2a is parked in the backlog, the door lane
    follows (audit, harness, D5 then D1-D3); the PGO epic stays queued and untouched.
  EVIDENCE:
  - tickets/stories/2026-10-03_flat_warm_body_constants_story.md:1-40
  IMPACT: Milestone 3 is redefined as the flat-warm-body story (S9/S11); S2a leaves the exit gate.
  NEXT: the certification/implementation task's investigation read.
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
STATE 2026-10-01T00:53:45Z: IN_PROGRESS. Opened on the owner's split; five stories (S1 moved in and active,
S8/S2a/doors drafted ready, the harness story in review). The S1 implementation task is routed on the board.
Resume from the task's latest STATE line.

STATE 2026-10-01T01:25:22Z: IN_PROGRESS. Non-PGO catalogue and recommendation recorded on the owner's request; S1's
exact edit is proposed and waits for the owner; nothing implemented. Resume from the S1 task's latest STATE line.

STATE 2026-10-02T18:01:21Z: IN_PROGRESS. S1 landed at 0.2.8216 and in review (owner-run suites and gauntlet pending); S8
next. Resume from the S1 task's latest STATE line.

STATE 2026-10-02T19:09:13Z: IN_PROGRESS (idle). S1 turned in; no routed lane; S8 opens on the owner's word with its patch
docs first.

STATE 2026-10-03T21:22:15Z: IN_PROGRESS (idle). S1 and S8 turned in; no routed lane; S2a (with S9/S11) opens on the owner's word
with its patch docs first.

STATE 2026-10-03T21:31:58Z: IN_PROGRESS. The flat-warm-body story (S9/S11) is the active lane; S2a parked; PGO epic ignored.
Resume from the task's latest STATE line.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
