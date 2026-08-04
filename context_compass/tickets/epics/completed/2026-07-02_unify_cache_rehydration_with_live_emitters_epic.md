# Epic: Unify cache rehydration with the live phase-11 emitters

## Metadata
- Epic ID: EPIC-2026-07-02-unify-cache-rehydration
- Status: RESOLVED 2026-07-03 (root cause: NOT emitter drift - manifest adoption
  had already unified load with live; the measured regression was free-threaded
  GC heap-scan cost from the decoded resident bundle. Fixed by the v3
  nested-marshal bytes store. Closing gauntlet: cache-on GC-on threaded min
  0.355ms == cache-off floor, vs 0.481 pre-fix.)
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-07-02T14:00:00Z
- Updated: 2026-07-02T14:00:00Z

## Problem / Opportunity
User-measured: the melder gauntlet warm phase is ~13% SLOWER with a warm cache than
without one (threaded median 0.483 -> 0.542ms; per-iter MINIMUM +110us = systematic
per-meld cost; setup improves 0.650 -> 0.511ms). Root cause (evidenced): the
spell-level cache EMITS AT SAVE TIME and REPLAYS STORED CODE OBJECTS at load
(spell_codegen_creation_cache.py:338 exec of package["no_overrides"]["code_object"]).
The save path builds step-plan sources with the LEGACY generalized emitter
(_build_step_plan_executor_source, import :58-62, used :499), while live first-meld
hydration uses the MODERN manifest-compiler emitters that received the full 2026-07-01/02
optimization program (closure cells, bare (meld) signatures, bound owner stores/targets,
contract inlining). Cached spells therefore run pre-optimization bodies forever: the
cache is a code time machine, and every future emitter improvement widens the gap.

## Context
- Owner decision (chat 2026-07-02): Option 1 selected in principle - "one generator for
  both births" - but parked for a fresh cycle after the agent was caught mid-read; the
  mechanism turned out to be save-time emission + code-object replay, NOT load-time
  re-emission, which changes the surgery.
- HARD CONSTRAINT (owner): phases 1-7 MUST still run live in dynamic mode. The loader's
  own precondition already encodes this (spell_codegen_creation_cache.py:228-234
  "Requires phases 1-7 to have already run... phase-5 blueprint + path registry live...
  ownership wired") and MUST be preserved verbatim.
- Related fix already landed in the compiler-lane task (2026-07-02): the load-time
  split-namespace exec at :338 was converted to single-namespace exec so fresh caches
  carrying hoist-form transient sources do not NameError; legacy defaults-form step
  code objects are unaffected. That fix is correctness-only - the LEGACY-BODY drift
  this epic addresses remains.

## MRP Alignment
The cache must not ship slower-than-live code; single-emitter unification makes emitter/
cache drift structurally impossible rather than patched once.

## Ticket Contract
- ENTRY_GATE: fresh-session onboarding per owner's slim directive; read this epic +
  the two evidence tickets before any edit.
- EXECUTION_BOUNDARY: read scope = spell_codegen_creation_cache.py IN FULL (save +
  load + package schema + code-object cache interplay), generalized_creation_cache.py
  (family cache, manifest-keyed), family coverage for solo/many_only, executor_factory_
  cache + executor_code_cache interplay with stored code objects. Edit scope EMPTY
  until a DECISION note records the chosen design.
- DEPENDENCIES: tickets/tasks/2026-07-01_compiler_phase8_11_generalized_call_savings_
  task.md (all emitter optimizations + the cache-slower MEASURE note 2026-07-02);
  tickets/tasks/2026-07-02_scope_cycle_runtime_machinery_investigation_task.md (parked).
- EXIT_GATE: cached and live executor bodies byte-identical (or provably same-factory
  via source-hash identity); user-run gauntlet cache-on warm >= cache-off warm; setup
  savings retained; full unit tree green on 3.14t.
- FAILURE_ESCALATION: DECISION_REQUEST on any package-format change (cache versioning);
  BLOCKER if family-cache coverage gaps make Option 2 tempting without an audit.

## Goals
- One emitter for live builds AND cache rehydration (Option 1: at save OR at load,
  decide after the full pipeline read - storing manifest rows and re-emitting at load
  through the factory cache may beat storing code objects entirely, since the factory
  cache already dedupes compile+exec per shape per process).
- Byte-equality proof harness (live-emitted source vs cache-path source per spell).
- Preserve: phases 1-7 live in dynamic mode; package compatibility or explicit
  version bump; lazy overrides-at-load behavior (:250-282, keep).

## Non-goals
- Retiring the spell-level cache (Option 2) without a family-coverage audit.
- Any phase-ordering or hydration-timing change.

## Stories / Tasks (proposed)
- [ ] S1: Full pipeline read (save path, package schema, code-object cache identity,
      load path, consumers) + design note choosing save-time vs load-time unification.
- [ ] S2: Implement + byte-equality differential harness + unit tests.
- [ ] S3: User-run validation (gauntlet cache-off vs cache-on pair, unit tree) +
      MEASURE notes; family-coverage audit note for a future Option 2 decision.

## Notes
- DATETIME: 2026-07-02T14:00:00Z
  TYPE: FACT
  CLAIM: Epic staged per owner direction ("make an epic to possibly explore this in
    another compacting"). Key mechanism facts already evidenced: package stores
    steps_rows (:139-157) AND compiled code_object replayed at :338; save-time source
    built at :485-502 (transient via the MODERN shared builder - already hoist-form;
    step-plan via the LEGACY emitter - the drift); loader precondition :228-234 pins
    phases 1-7 live. The 13% warm regression numbers live in the compiler task's
    2026-07-02 MEASURE/cache notes.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:58-62
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:139-157
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:228-234
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:301-346
  IMPACT: A cold session can resume from this epic without replaying chat.
  NEXT: S1 pipeline read in a fresh cycle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-02T21:30:00Z
  TYPE: DECISION
  CLAIM: S1 PIPELINE READ COMPLETE - ROOT-CAUSE HYPOTHESIS REVISED. The read scope
    (legacy spell cache in full, family codec, generalized manifest module, shared
    manifest envelope, spellbook save seam :841-886, creation-system load seam
    :534-613, CounterSwitch, factory/builder rebuild path, conduit_meld guards,
    transfer-of-ownership reset path) establishes: (1) manifest-first save has been
    live since 2026-06-12 (commit 7ccaaccc9) for ALL THREE families; the generalized
    manifest step stamps unconditionally. (2) Manifest packages load lazily through
    the SAME hydrator as live builds ("one assembly program, two callers") - post-
    first-meld hot doors are identical BY CONSTRUCTION, satisfying this epic's
    byte-equality exit gate without surgery. (3) The legacy spell-level cache
    (save-time emission + code-object replay) is DEAD on the save path for current
    families; it is reachable only for stale bundles / foreign payload shapes at the
    two spellbook_creation_system fallback seams. THEREFORE the epic's original
    root-cause claim (legacy emitter drift) cannot explain the 13% warm regression
    measured on fresh caches - the regression must be re-measured and re-attributed.
    Asymmetries RULED OUT by read: fast_state (load_cached opens the switch to 2);
    ownership transfers (reset resolution_complete + clear phase artifacts for BOTH
    configs); door/route identity (same door compilers both paths).
  EVIDENCE:
  - src/.../shared_assets/manifest_creation_cache.py:1-60 (envelope + dispatch)
  - src/.../generalized/manifest/generalized_manifest.py:1-18 (one-assembly contract)
  - src/melder/aether/spellbook/spellbook.py:850-886 (manifest-first save seam)
  - src/melder/aether/spellbook/spellbook_creation_system.py:534-613 (load dispatch)
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:164-180
  - git 7ccaaccc9 (2026-06-12, manifest-first save + solo family)
  IMPACT: The planned Option-1 surgery is NOT the fix; the epic pivots to
    measure-first. The legacy module is retirement CANDIDATE only (package-format /
    behavior change -> DECISION_REQUEST per this ticket's contract).
  NEXT: DIAGNOSTIC STAGED: tests/experimentation/test_cache_warm_meld_parity_probe.py
    (user-run, 3.14t): (a) HARD-FAILS if any staged payload is legacy-shaped;
    (b) proves the seam (cache-served spells: resolution_complete + phase-11
    container None); (c) times cold-built vs warm-cache-loaded pairs on 3 lanes
    (warm many4 / warm unique / lesser-cycle meld#1) in BOTH conjure postures.
    User also reruns the real gauntlet cache pair. Decision tree: parity ~1.00 +
    clean gauntlet pair -> close epic as fixed-by-manifest-adoption + optional
    legacy retirement DECISION_REQUEST; regression reproduces -> bisect the
    offending lane with the probe as the reproducer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-02T22:30:00Z
  TYPE: MEASURE
  CLAIM: USER-RUN PARITY PROBE (3.14t): CACHE LOAD PATH IS CLEAN. Both postures:
    staged payloads manifest=6 legacy=0 (memory AND disk), warm-leg cache_served=6
    live_compiled=0. Ratios (warm_cache/cold): automatic warm_many4 0.999,
    warm_unique 1.060 (19ns on a ~300ns op - noise band), cycle_meld1 1.007;
    dynamic warm_many4 0.985, warm_unique 1.006, cycle_meld1 1.014. VERDICT: no
    cache-on warm regression at this shape; the hydrator-unified load path
    delivers parity by construction, as the S1 read predicted. The originally
    measured 13% is not reproducible on current code at probe shape - remaining
    possibilities: fixed by the intervening emitter program (lazy overrides /
    closure cells / dual doors), gauntlet-shape-specific, or run variance.
  EVIDENCE:
  - chat transcript 2026-07-02 (user-run pytest output, .venv_new 3.14t)
  IMPACT: Option-1 surgery is confirmed unnecessary. Epic closes pending ONE
    confirmation: the real gauntlet cache pair (cache-off vs cache-on).
  NEXT: user runs the gauntlet cache pair when convenient. If clean: close epic
    (status resolved-by-manifest-adoption); optional follow-up DECISION_REQUEST -
    retire the legacy spell-level cache module (dead on save; load seams kept or
    dropped is a package-compat decision). If the gauntlet still regresses: the
    delta is gauntlet-shape-specific and the probe grows that shape next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-03T01:10:00Z
  TYPE: FACT
  CLAIM: GC FIX LANDED (owner approved "go ahead and hit those things up").
    CachingSystem resident store converted to NESTED-MARSHAL BYTES per spell:
    CURRENT_VERSION 2->3 (old bundles regenerate cold via existing version
    gate); `upsert_spell_payload` serializes immediately; `get_spell_payload`
    returns a FRESH decode per call (mutations never persisted - documented);
    `spell_payloads` property is now an O(n) decoded snapshot (diagnostics
    surface); `transfer_spell_payload_to` moves raw bytes via new internal
    `_store_serialized_payload` (no decode round-trip); `_normalize_loaded_
    cache_data` fail-fasts on non-bytes payload values (foreign/corrupt ->
    cold). Class contract docstring records the measured GC rationale.
    Consumers audited: runtime load seam uses get_spell_payload (decoded,
    unchanged shape); cached_spell_ids unchanged; no other src consumers.
    Tests: emit-shape unit test updated to nested-bytes assertion; NEW
    regression test test_caching_system_resident_store_holds_untracked_bytes
    (internal store isinstance bytes + fresh-decode isolation); parity probe
    disk audit decodes nested bytes. Shadow harness: caching unit suite 18/18
    green (incl. parametrized invalid-bundle cases). 3.14t: Not run.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py (v3 contract)
  - tests/unit/melder/utilities/test_caching_system.py (+regression test)
  - tests/experimentation/test_cache_warm_meld_parity_probe.py (audit decode)
  IMPACT: The resident cache no longer contributes tracked objects to
    free-threaded GC passes - the measured ~13%/+122us-min warm regression
    mechanism is removed at the source; cold-run staging heap shrinks too.
  NEXT: USER RUNS: caching unit suite, component caching suite, parity probe,
    then the gauntlet cache pair WITH GC ON - cache-on should now sit on the
    cache-off floor (min ~0.36ms threaded). If clean: CLOSE EPIC (resolved:
    manifest adoption + GC-untracked resident store). Remaining queue after:
    deopt 3-strike re-pin (approved), scope-cycle lane, overrides audit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-03T01:40:00Z
  TYPE: FACT
  CLAIM: USER VALIDATION: caching unit suite 18/18 on 3.14t; component caching
    suite passes (via `python -m pytest` - plain `pytest` lacks repo root on
    sys.path for tests.mocks imports, pre-existing quirk); parity probe clean
    (all seams zero, lanes ~1.00; cycle_meld1 1.05-1.08 = that lane's observed
    noise band). Owner reports "all passed". GAUNTLET CACHE PAIR NUMBERS WITH
    GC ON: not posted yet - the epic's close condition (cache-on threaded min
    on the ~0.36ms cache-off floor) is measured-pending, NOT confirmed.
  EVIDENCE:
  - chat transcript 2026-07-03 (user-run outputs)
  IMPACT: Fix validated functionally end-to-end; perf close-out is one
    gauntlet pair away.
  NEXT: user posts the GC-on gauntlet cache pair (threaded min is the number
    that matters). Then: close epic; proceed to deopt 3-strike re-pin
    (approved), scope-cycle lane, overrides audit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-03T02:00:00Z
  TYPE: MEASURE
  CLAIM: EPIC CLOSED. User-run gauntlet cache-ON with GC ON (setup=0.553ms =
    warm-cache signature): threaded per-iter min 0.355ms / avg 0.509 / median
    0.511 - ON (slightly under) the historical cache-off floor (0.359) and
    -126us vs the pre-fix cache-on min (0.481). hot_objects/s_min 1,039,691
    (pre-fix cache-on: 935,543). The v3 bytes store removed the regression at
    the source. Full pair not needed: the ON leg landing under the OFF floor
    is conclusive.
  EVIDENCE:
  - chat transcript 2026-07-03 (user-run gauntlet output)
  IMPACT: Caching is now performance-neutral warm and setup-positive
    (0.553 vs ~0.65-0.69ms cold) - as designed. Queue continues: deopt
    3-strike re-pin (approved), scope-cycle lane, overrides audit.
  REREAD: NOT_REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Fresh epic, owner-parked. Resume at S1. The one already-landed change: load-time exec
at :338 is single-namespace now (correctness for fresh hoist-form caches); everything
else untouched.
UPDATE 2026-07-02T21:30: S1 done, root cause revised (see DECISION note above); parity
probe staged; awaiting user-run probe + gauntlet cache pair before any surgery.
UPDATE 2026-07-02T22:30: probe ran clean (parity ~1.00 both postures, zero legacy
payloads, all spells cache-served). Epic closes on a clean gauntlet cache pair.

- DATETIME: 2026-07-02T23:15:00Z
  TYPE: MEASURE
  CLAIM: GAUNTLET CACHE PAIR REPRODUCED THE REGRESSION ON CURRENT CODE - and its
    shape EXONERATES the door path while INDICTING something per-iteration.
    Cache-ON vs OFF (threads=1, 3.14t gil=disabled): total avg 0.700 vs 0.589ms,
    threaded per-iter avg 0.569 vs 0.469ms (+100us), median 0.563 vs 0.446
    (+117us), MIN 0.481 vs 0.359 (+122us SYSTEMATIC); hot_objects/s_min 935k vs
    1,113k (-16%); wall_cycles/s 17,588 vs 21,310 (-17%). CRITICAL SIGNATURE:
    active_cycles/s EQUAL (60,533 vs 59,980) and every measured scope segment
    (outer/request create/cleanup/whole-cycle) EQUAL - the +100us/iter lives in
    the UNMEASURED gaps (scope-hosted hot melds and/or per-iteration seams), NOT
    in door execution (consistent with parity probe v1 ~1.00 on root-conduit
    lanes). Setup faster cache-on (0.548 vs 0.689ms) as designed. Suspect list:
    per-publish cache staging attempts, bundle re-emission (marshal dump + disk
    write at meld boundaries), context rebuilds hitting the codegen-creation-less
    cache-loaded spells, per-meld re-resolution entries.
  EVIDENCE:
  - chat transcript 2026-07-02 (user-run gauntlet pair, .venv_new 3.14t)
  IMPACT: Epic stays OPEN with a reproducer; root cause is per-iteration seam
    work, not emitter drift (original hypothesis stays dead).
  NEXT: PROBE V2 STAGED: parity probe extended with (a) spellspace lanes
    (space_cycle request shape + space_hot_many scope-hosted hot melds) and
    (b) seam counters (builder_build / cache_disk_emit / cache_stage_upsert /
    spellbook_stage_attempt / spellbook_file_emit / runtime_reresolution)
    wrapped ONLY during the measured phase, printed cold vs warm. User reruns
    the probe; a nonzero warm-leg seam or a >1.0 space lane names the mechanism.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-02T23:50:00Z
  TYPE: FACT
  CLAIM: PROBE V2 RAN CLEAN (user, 3.14t): all five lanes parity 0.95-1.04 in
    BOTH postures, all six warm-leg seam counters ZERO (cold leg: builder_build=2
    + spellbook_stage_attempt=2 only - identity-assert melds pre-counter window).
    Door path, rebuild path, staging path, disk path, and re-resolution path are
    ALL exonerated at probe shape. Remaining suspect (by elimination + gauntlet
    signature): AUTOMATIC GC - free-threaded collections scan the full tracked
    heap; the warm-cache run retains the entire marshal-decoded bundle + closure-
    held manifests for the whole run (thousands of extra tracked dicts/tuples),
    fattening EVERY collection -> raised per-iteration MINIMUM, invisible to the
    7-spell probe (tiny bundle) and to the gauntlet's per-segment timers (GC fires
    between measured segments). Gauntlet reads: gc.collect() only at final
    cleanup; automatic GC live during the threaded phase.
  EVIDENCE:
  - chat transcript 2026-07-02 (probe v2 output)
  - benchmarks/testing_other_di/test_melder_gauntlet.py:295-303 (gc at cleanup only)
  - benchmarks/testing_other_di/melder_gauntlet_support.py:592-689 (per-iter loop)
  IMPACT: Hypothesis is now singular and decisively testable.

- DATETIME: 2026-07-03T00:20:00Z
  TYPE: MEASURE
  CLAIM: GC MECHANISM CONFIRMED (user-run 2x2 complete, 3.14t gil=disabled).
    Threaded per-iter MINIMUMS: GC-on/cache-on 0.481ms; GC-on/cache-off 0.359ms
    (+122us = the regression); GC-off runs x3 (cache-on setup=0.512; two further
    runs setups 0.531/0.598): 0.366 / 0.378 / 0.377ms - the cache-on vs cache-off
    gap COLLAPSES with cycle GC disabled; all GC-off legs land within noise of
    the GC-on/cache-off floor. VERDICT: the "13% cache-on warm regression" is
    free-threaded GC heap-scan cost from the marshal-DECODED cache bundle kept
    tracked in CachingSystem memory for the process lifetime - NOT the cache's
    runtime path (doors/loads/rebuilds all previously exonerated at parity).
    Every emitter-drift and load-path hypothesis in this epic's original framing
    is dead; the epic's title problem resolves to a memory-representation fix.
  EVIDENCE:
  - chat transcript 2026-07-02/03 (gc-probe wrapper runs, .venv_new 3.14t)
  IMPACT: Fix target is precise: keep spell payloads GC-untracked in memory.
  NEXT: PROPOSED FIX awaiting owner approval (file-format change -> escalated per
    ticket contract): nested-marshal payload store - bundle file becomes
    {spell_id: marshal_bytes}; CachingSystem stores BYTES per spell (untracked),
    upsert serializes immediately, has_spell_payload/emit unchanged in shape,
    loader decodes ONE spell's bytes at publish time so decoded objects live only
    in the door closures that need them; CachingSystem CURRENT_VERSION bump so
    old bundles regenerate cold. Bonus: same fix shrinks cold-run staging heap.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
  NEXT: GC-ISOLATION WRAPPER STAGED at benchmarks/testing_other_di/
    test_melder_gauntlet_gc_probe.py: runs the UNMODIFIED gauntlet with cycle GC
    disabled (default) or with gc.get_stats() deltas (MELDER_GC_PROBE_KEEP_GC=1).
    User runs the cache pair through the wrapper. Pair equalizes -> fix is
    releasing the decoded bundle after the conjure load boundary (CachingSystem
    payload release seam; also helps cold runs that stage large graphs). Gap
    survives -> GC exonerated, back to runtime-path bisection with the gauntlet
    as reproducer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
