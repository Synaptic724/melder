# Component Patch: Generalized Family - Singleton Specialization Stage

- Patch ID: generalized_singleton_specialization_2026_07_01
- Component: codegen_creation_system / strategies / generalized (+ SpellbookConfiguration)
- Status: in_progress (guard policy APPROVED by owner in chat 2026-07-01; emitter + lazy overrides landed; specializer wiring pending)

## Before Behavior
- Hydration (first meld) builds ONE generic inner no-overrides executor from manifest rows;
  `compile_creation_context_hooks_no_overrides_executor` wraps it into the route-keyed door;
  cold->hot swap installs it into `CreationContext._no_overrides_executor`. The body walks
  every step on every call: per-step aliases (`spell_N = step_spells[N]`, `spell_id_N`,
  `creations_N`), then for OWNER-`unique` steps a lock-free `_creations.get` + None branch
  even when the instance has been live since cycle #1.
- EVIDENCE: generalized_manifest_no_overrides_compiler.py:186-505 (emission),
  generalized_hydrator.py:129-283 (hydration + swap).

## After Behavior
- Hydration unchanged when the config flag is OFF (default).
- Flag ON: the hot no-overrides door is wrapped in a one-shot specializer. First successful
  execution:
  1. Partition manifest rows: captured set = rows with `existence == unique`; rest unchanged.
  2. If captured set is empty -> swap plain hot door back; done (zero steady-state cost).
  3. Read each captured instance from `spell._owner_creations._creations[spell_id]`; if any
     missing -> keep wrapper for one retry on next call, then decline permanently.
  4. Capture each captured step's `spell._door_epoch`.
  5. Emit specialized inner via NEW `emit_specialized_step_plan_source(...)`:
     - prologue: `if dep_spell_K._door_epoch != captured_epoch_K: return _generic_inner(meld)`
       per captured step (all identity via default params; source remains identity-free and
       factory-cache shareable by shape),
     - captured steps contribute NO per-call work beyond the prologue compare,
     - non-captured steps emitted with today's emitters, with dependency reads on captured
       steps compiled to the captured default-param constants,
     - root-is-unique collapses the body to prologue + `return captured_root`.
  6. Wrap with the same route-keyed door compiler; swap into the context slot (existing
     self-replacing contract); the generic hot door remains the deopt target inside the
     specialized body closure.
- Deopt: any prologue mismatch tail-calls the generic inner (correct result, slower call);
  context rebuild (epoch bump + slot reset to cold doors) naturally triggers
  re-hydration + re-specialization.

## Interface Deltas
- NEW: `emit_specialized_step_plan_source(rows, captured_step_indexes, root_instance_key)`
  in generalized_manifest_no_overrides_compiler.py; pure function of rows + capture positions.
- NEW: `_install_specializing_door(...)` (hydrator-internal); public hydrator signatures gain
  one optional keyword flag with a behavior-preserving default.
- NEW config property on SpellbookConfiguration (default False), read at hydration only.

## State / Failure Deltas
- New state: specializer wrapper closure state (one lock, one attempt flag) - per hydration,
  short-lived, discarded after swap/decline.
- Failure modes added: specialization ATTEMPT failures are swallowed to a decline (plain hot
  door restored); guard-miss deopt is silent and correct by construction. No new raise paths
  on the meld hot lane.
- Threading: specialization runs post-execution on the calling thread under a dedicated
  wrapper lock; install races funnel through the existing slot-swap semantics (last writer
  wins; losers deopt via context-identity/epoch guards). nogil-safe: guards are frame-local
  int compares; no new shared counters.

## Dependency / Ordering
- Depends on manifest rows carrying `existence` (already present) and on the hydrator's
  self-replacing slot contract (already documented in creation_context.py).
- Must land AFTER owner signoff on the guard policy (architecture patch SS "Guard Policy").
- Overrides lane untouched; `SpellSpaceMeld` path works unchanged (captured `unique` deps are
  frame-global; non-captured steps keep live per-call store routing off `meld`).

## Validation Expectations
- Unit (agent-runnable, source-shape level): emitted specialized source for representative row
  sets (root-unique, mixed unique+many, mixed unique+caller-routed, zero-unique decline);
  prologue guard emission; deopt tail-call emission; factory-cache shareability (identity-free
  source; distinct shapes -> distinct sources).
- Component: specializer wrapper install/decline/retry; slot swap; differential equivalence
  flag ON vs OFF on a small real graph (instance identity, registration, disposal, errors).
- Integration (user-run 3.14t): deopt matrix - owner teardown, transfer_spell_ownership,
  hook attach on captured dep, context rebuild, concurrent meld during specialization; both
  gauntlets + contention sweep for the performance claim. Agent reports "Not run." until then.

## Addendum 2026-07-01: Lazy Overrides Runtime (landed same lane)
- Before: `hydrate_creation_executors` eagerly built the overrides execute
  runtime (targeting deserialize + runtime rows + door compile inputs) at
  FIRST MELD for every spell, even when no override is ever passed.
- After: `_build_lazy_overrides_door` publishes a cold overrides door; the
  first OVERRIDE meld hydrates once (leader/followers under a lock), builds
  the real door via the same door compiler, and self-swaps into the published
  context `_overrides_executor` slot. `GeneralizedHydratedExecutors.
  overrides_code_object` is now None (diagnostics-only field; family cache
  currency is the manifest, not code objects).
- Behavior delta: TIMING ONLY - overrides-lane hydration errors surface at
  first override meld instead of first meld. No-overrides lane unchanged.
- Verify on 3.14t: full unit tree + any consumer of overrides_code_object
  (grep shows hydrator-only at patch time) + both gauntlets (cold/first-meld
  numbers are the expe
## Addendum 2026-07-02: Door-Template get_creation Inlining (landed same lane)
- Motivation: probe v2/v2.1 measured the t5 ceiling in the DOOR lane (threads5_many8
  ~1.0 while t1 body wins ran 13-16%); the route-door warm short-circuit paid one
  bound-method materialization + call frame per warm scoped meld via
  `X.get_creation(_spell_id)`.
- Change: all 30 emitted-source sites in creation_runtime_door_compiler.py now inline
  `X._creations.get(_spell_id)` (15 lock-free warm reads + 15 locked miss re-checks).
  `Creations.get_creation` is a verified bare `._creations.get` (creations.py:269-278),
  so the transform is semantics-preserving; the body emitters made the identical call
  in their own lane previously ("two-call helper chain is pure overhead").
- Reach: every scoped route (unique / unique_per_conduit / spellspace / lineage /
  cluster), both template families (no-overrides + overrides-only), both variants
  (instance + hooks), every codegen family's doors, flag-independent.
- Verified (3.10 exec harness; melder itself needs 3.14t): all module-level templates
  compile post-transform; unique + unique_per_conduit doors exercise miss->construct->
  register then warm->short-circuit correctly; emitted source contains zero
  `.get_creation(` and 30 inlined reads.
- Expected observable: leaf / cycle lanes of the efficacy probe and gauntlet door
  rows improve in BOTH flag postures; user-run 3.14t validation required.

## Addendum 2026-07-02b: Collection-DI Inlinable Emission + Transient Body Cut
- Transient lane (shared builder, consumed by many_only family + cache rehydration):
  per-slot factory-time defaults replace N per-call target alias loads; per-step
  zero-cost handlers with constant attribution replace N per-call `__step_index`
  stores. Happy path = constructor calls only. many_only PRIVATE emitter copy
  (:1234-1278) still on old pattern - parity follow-up.
- Collection-DI inlining: `row_inlinable_common_shape` now returns uniform
  (param, key_tuple) pairs and admits multi-dep params; emission produces
  order-preserving list literals (locals mode: `h=[instance_i, instance_j]`;
  dict mode: flat-cursor instance_results reads; bindings step_dep_keys
  flattened to match). Parity with `_build_kwargs_no_overrides`: >=2 deps ->
  list, 1 -> scalar, 0 -> omitted. Graphs using `list[Frame]` collection DI now
  stay in locals mode instead of falling to the generic `_construct_spell_
  instance` dict path (dict alloc + tuple-hash per dep + type rederivation +
  double-splat per construction).
- Verified via stub harness: locals + dict emission shapes, runtime list order,
  scalar/omitted parity, specialized-emitter collection support, factory wrap.
  3.14t suites: Not run. INCIDENT: two more mount write truncations during this
  work (compiler tail x2), recovered from in-context content + fsync + verify.

## Addendum 2026-07-02c: Step-Plan Alias -> Signature-Default Hoisting
- Motivation: every generalized step-plan body statement of the form
  `spell_N = step_spells[N]` (and spell_id/disposal/plan_step/step_dep_keys/
  instance_key variants) re-executed per CALL what is constant per HYDRATION.
- Change: both emitters (generic + specialized) now emit these as per-slot
  SIGNATURE DEFAULT PARAMETERS built by the new shared helper
  `_step_alias_signature_params` (single source of truth mirroring the exact
  per-branch read conditions, so signature and body cannot drift). The factory
  wrapper evaluates each subscripted default once at def time; calls receive
  them via frame-setup default copies. Dict mode additionally hoists
  `instance_key_N` for every step (including captured seeds) and stores via
  `instance_results[instance_key_N]`.
- Reach: every generalized graph, warm AND miss paths, both flag postures.
  Width-8 many-over-uniques sheds ~17 per-call subscript statements.
- Source stays identity-free (indexes only): factory-cache sharing preserved;
  source-hash rekey means code/factory caches rebuild cleanly, no wipe needed.
- Verified (3.10 harness, real modules): 18 emission-contract + 9 wrapper
  tests green post-change; locals-mode executed end to end (cold construct+
  register -> warm store hit through the new signature); dict-mode and
  specialized-dict-mode sources carry the hoisted params, zero per-call alias
  statements, and compile. 3.14t suites: Not run.
- GATED follow-ups recorded in the ticket (NOT landed): target_N=spell.spell
  callable binding (needs in-place `.spell` swap audit), owner-store default
  binding for `unique` steps (needs `_owner_creations` reassignment audit),
  contract-payload constant inlining (dict-mode escape).

## Addendum 2026-07-02d: Owner-Store + Constructor-Target Signature Binding
- Audit basis (spell.py lifecycle, repo-wide grep): `_owner_creations` has ONE
  assignment site (ownership recording, :1109-1118) which runs
  `_cleanup_creation_context()` FIRST under the spell lock; `Spell.spell` is
  set only at __init__ and deleted only at cleanup (no in-place swap exists);
  `_cleanup_creation_context` bumps `_door_epoch`, destroys+nulls the
  published context, and resets the leader switch. Every executor therefore
  becomes unreachable before either value can change - identical staleness
  envelope to the existing `step_spells` binding. No new guards required.
- Change: two new frozen bindings (`step_owner_creations`, `step_targets`) in
  `_build_step_bindings` + `_STEP_BINDING_NAMES`; `unique` steps receive
  `creations_N=step_owner_creations[N]` via the signature helper (the per-call
  `spell_N._owner_creations` shared attr read is GONE from every warm unique
  hit); inlined constructions call `target_N(...)` via
  `target_N=step_targets[N]` (the per-call `.spell` attr load is GONE from
  every construction). The store's live `.get` read stays per call, so a
  cleared store degrades to miss/reconstruct, never a wrong result.
- Reach: both emitters (generic + specialized non-captured steps), both flag
  postures, warm + miss paths.
- Verified (3.10 harness, real modules): 18 emission + 9 wrapper tests green;
  locals-mode executed end to end (cold construct+register -> warm store hit);
  specialized partial-capture shape keeps `creations_N` for non-captured
  unique steps and nothing for captured ones. Executed-factory test bindings
  updated with the two new names. 3.14t: Not run.
- Remaining queue: (T3) contract-payload constant inlining (dict-mode escape);
  (T2c, unaudited) binding the store's `_creations` dict itself would need a
  Creations dict-identity audit - deferred, single attr read remaining.

## Addendum 2026-07-02e: Contract-Payload + Positional-Override Inlining (T3)
- Before: any row with a contract payload or positional override was
  non-inlinable, forcing the generic `_construct_spell_instance` path per call
  AND dragging the entire graph into dict mode (instance_results dict,
  tuple-hash reads, root presence check for every step).
- After: `_row_contract_call_extras` (new) resolves payload names + effective
  positional from row constants, mirroring `_build_kwargs_no_overrides` +
  `_construct_spell_instance` exactly: dict(items) dedupe (first position,
  last value), payload overwrites same-named dep params (dep read dropped -
  it was dead), payload `__args__` overwrites the positional override unless
  `uses_positional_override`, and a non-tuple/list effective positional keeps
  the row on the generic path so the per-call MeldExecutionError timing/type
  is preserved. Emission: leading `*positional_N` splat + trailing
  `name=contract_values_N[j]` keywords; VALUES ride two new frozen bindings
  (`step_contract_values`, `step_positional_args`) - source stays
  identity-free and factory-shareable. Both emitters covered via the shared
  helpers; `row` threaded through all five construct call sites.
- Known micro-divergence (documented in the emitter docstring): keyword ORDER
  is deps-then-payload, while the generic dict kept an overridden name at its
  original dep position - visible only to constructors introspecting
  **kwargs insertion order for payload-overridden names.
- Verified (3.10 harness, real modules): 24/24 emission tests (6 new:
  collision/precedence/fallback/locals-mode/zero-dep/specialized) + 9/9
  wrapper tests; executed graph proves `*("P0",)` splat + payload kwarg +
  dep threading through a hydrated factory. 3.14t: Not run.

## Addendum 2026-07-02f: Closure-Cell Hoist (supersedes 2026-07-02c/d mechanism)
- Probe verdict on the signature-default form (before/after user runs): WASH.
  CPython fills every default per call (pointer copy + incref per param, ~35
  on width-8), costing what the removed alias bytecode saved.
- Rework: `_step_alias_signature_params` -> `_step_alias_hoist_lines`. Alias
  assignments now execute ONCE per hydration at FACTORY level (lines emitted
  before the executor `def`); both executors' signatures shrink to bare
  `(meld)`; bodies reach aliases, fixed bindings, and cap_* slots as CLOSURE
  CELLS (LOAD_DEREF at use sites, zero frame-setup work); statics resolve via
  factory globals (cold/error paths only). Free-threading angle: no per-call
  incref/decref sweep over ~35 shared spells/stores - a contended-atomic
  reduction candidate for the t5 door-lane ceiling.
- The T1a/T1b/T2b/T3 CONTENT is unchanged (which aliases exist, unique
  owner-store binding, target binding, contract inlining) - only the
  delivery mechanism moved from defaults to cells.
- Verified (3.10 harness, real modules): 24/24 emission + 9/9 wrapper green;
  executed factory shows `__defaults__ is None`, co_argcount 1, populated
  closure, cold construct+register -> warm store hit. 3.14t: Not run.

## Addendum 2026-07-02g: Door-Lane Read Findings + Unique-Route Store Binding
- READ RESULT (creation_context.py in full + door compiler in full + call
  sites): the route doors were ALREADY closure-form - template factories take
  identity as factory parameters and the inner door defs are bare
  `(meld)` / `(meld, overrides)` (door compiler :449-490), so the staged
  "door-template closure hoist" lane is RETIRED: there is no default-fill tax
  in the door lane to remove. `meld` is the only per-call runtime argument;
  doors read caller stores off it per call (correct and untouchable).
- CUT LANDED (T2b-for-doors): the `unique` route was the one door still
  paying a hydration-constant walk per warm hit -
  `_spell._owner_creations._creations.get(_spell_id)` (6 emitted sites: 2
  no-overrides + 4 overrides variants). Templates now take `_owner_creations`
  as a factory param (uniform across routes; non-unique bodies ignore it),
  the four compile_* wrappers pass `spell._owner_creations` at door-compile
  time, and unique bodies read `_owner_creations._creations.get(_spell_id)`.
  Same audited invalidation envelope as the executor-body T2b: the only
  owner-store reassignment path tears down the creation context first, which
  recompiles the doors. Saves one shared-object attr read per warm unique
  meld system-wide (the probe's leaf lane measures exactly this door).
- RISK (flagged, untouched): `_build_with_overrides_lines` has dead
  `overrides_maybe_none=True` branches (sole caller passes False) whose
  unique_per_conduit/spellspace variants reference `caller_creations` WITHOUT
  assigning it - a latent NameError if that flag is ever exercised.
- Verified (3.10 harness): full module import compiles all 80 templates;
  unique hooks door miss->construct->register then warm->short-circuit OFF
  THE BOUND STORE (inner runs once; store-dict swap visible); upc door still
  routes off the meld; 24/24 + 9/9 regression green. 3.14t: Not run.

## Addendum 2026-07-02h: Dead overrides_maybe_none Variants Removed
- Owner-directed after the Existence read: existence semantics (existence.py,
  six declarative modes) give the maybe-none variants no reason to exist, and
  the door-selection contract already guarantees the overrides-only doors run
  ONLY with a normalized payload present ("Meld chooses this door only when
  an override payload exists"). The sole live caller passed
  `overrides_maybe_none=False` since inception.
- Change: `_build_with_overrides_lines` loses the `overrides_maybe_none`
  parameter; the 6 dead True-variant bodies (218 lines, including the two
  latently-broken ones referencing `caller_creations` unassigned) are
  removed; docstring records the contract that killed them. File 1432->1214.
- Proof of emission-neutrality: every LIVE route/variant combo (14 overrides
  + all no-overrides combos) emits byte-identical bodies vs git HEAD modulo
  the already-verified T2B store-binding transform (old module loaded from
  HEAD side-by-side and compared). Functional overrides door check green
  (create-under-lock + existing-override canonical raise). 24/24 + 9/9
  regression green. 3.14t: Not run.

## Addendum 2026-07-02i: Phase-10 Single-Pass Dual-Variant Build
- Gate closed by read: `_extract_param_keys_no_overrides` is a strict
  projection of `_extract_param_keys` (identical dependency structures over
  the same param_sources); the per-step variant delta is the extraction call
  plus five override-metadata fields; fast arrays are NO_OVERRIDES-only.
- Change: NEW `SpellGeneralizedCodegenPlanBuilder.build_dual()` walks the
  model ONCE, extracts once, and materializes both step lists (no-overrides
  steps take fresh projection copies; overrides steps own the full
  extraction; cross-plan aliasing matches the two-build baseline). Shared
  assembly helpers `_assemble_lane_plan` / `_build_fast_transient_plan_from_
  data` keep `build()` and `build_dual()` in field-for-field lockstep;
  `build()` and the solo/many_only surfaces are untouched. Strategy call
  site swapped to one builder + build_dual.
- PROOF: differential harness promoted to a permanent unit test
  (tests/unit/.../codegen_planner/test_generalized_dual_build_differential.py,
  4 model shapes, every step/plan/fast/transient field compared + identity
  aliasing checks). 4/4 + 24/24 + 9/9 green on the 3.10 harness.
- MEASURE (stub-model bench, width-8 mixed graph, 3.10): two-build 84.7us ->
  dual 74.9us, ratio 0.8846 (-11.5%). HONEST CORRECTION vs the ~45-50%
  estimate: step-object construction (30 fields x 2N steps, required by both
  paths) dominates the builder; the eliminated duplicate is the walk +
  extraction only. Real-model numbers may differ (live attribute reads).
- FOLLOW-UP LEVER (gated on a manifest-consumer read): sharing full-metadata
  step objects across both plans would halve step construction, but requires
  proof that the no-overrides manifest/emitter path never reads the override
  metadata fields off steps (or strips them at row b
## Addendum 2026-07-02j: Transient-Lane Closure Port + many_only Parity
- Owner redirect back to phase 11. The transient unrolled builder still used
  the defaults pattern the probe proved wash-at-best: ~40 signature defaults
  (root index + 36 dep arrays + targets + steps) filled per call on EVERY
  all-many meld - and the dep arrays are emission-time inputs never read by
  the body at all (pure dead frame-setup weight + shared-object increfs).
- Change 1 (shared builder, generalized legacy compiler): emits hoist lines
  `t{N} = transient_targets[{N}]` before a bare `def ...(meld):`; body
  unchanged; steps/MeldExecutionError resolve from the enclosing scope.
  Verified through BOTH consumer mechanisms: exec-namespace (many_only /
  legacy path - names become module globals) and factory-cache wrap
  (generalized + cache rehydration - true closure cells, __defaults__ None,
  co_argcount 1).
- Change 2 (many_only PRIVATE copy): full port from the OLD pattern (per-call
  t{N} loads + live __step_index stores + single tail handler) straight to
  the final form - the long-owed parity item. PROOF: the private copy now
  emits BYTE-IDENTICAL source to the shared builder for the same schema;
  functional exec + per-step constant error attribution verified.
- Regression: 24/24 emission (transient assertions updated to hoist form) +
  9/9 wrapper + 4/4 dual-build green. 3.14t: Not run.
- INCIDENTS: two more mount truncations (generalized legacy compiler tail,
  emission test file tail) - both writes VERIFIED byte-equal before the mount
  ate the tails afterward. New write protocol: temp file + fsync + os.replace
  + sleep + independent sha/wc/tail verification; both recoveries from git
  HEAD + patch replay.

## Addendum 2026-07-02k: Phase-10 Step Sharing Across Lane Plans
- Gate closed by reads: BOTH phase-11 row builders (codegen_creation_schema_
  helpers.build_phase11_step_ir_row + shared_compiler_executions twin) already
  strip override metadata at ROW build via include_override_metadata=False
  (manifest :115/:159, cache :141/:185 pass the flag per lane); lane-plan
  cleanup() clears its OWN lists and never steps, so shared step objects are
  teardown-safe.
- Change 1: `contract_keys` was the single UNGATED override-lane field in both
  row builders - now gated under include_override_metadata. Today's outputs
  are unchanged (no-overrides steps carried [] anyway); with sharing, the
  no-overrides rows stay byte-identical BY THE FLAG.
- Change 2: build_dual constructs ONE full-metadata step list shared by both
  plans (each plan owns its own list object over the same steps); the
  projection copies, second step construction, and per-plan disposal lists
  are gone. Contract change vs the two-build baseline is deliberate and
  documented: plan-level override fields on the no-overrides plan now carry
  full metadata; the equivalence contract moves to ROW level (strip point).
- PROOF: differential test upgraded - neutral-field step equality + ROW
  byte-equality under each lane's strip flag + explicit sharing assertions
  (distinct lists, identical step objects); 4/4 + 24/24 + 9/9 green.
- MEASURE (stub bench, width-8): two-build 83.8us -> build_dual 61.9us,
  ratio 0.7389 (was 0.8846 pre-sharing). Recurs on every conjure + dynamic
  revalidation. 3.14t: Not run.
- INCIDENTS: two more verified-then-truncated writes (lane plan file, dual
  test file); recovered from HEAD + full patch replay both times.

## Addendum 2026-07-02l: Dual Instance-Door Slot (owner-approved "send it")
- CreationContext gains `_no_overrides_instance_executor`: the instance-only
  twin of the tuple door (same inner executor, instance-variant route
  template, `(meld) -> instance`), documented in the door-facing contract;
  slots swap TOGETHER at every publish site, same self-replacing rules.
- Publishers (ALL updated): SpellCodegenCreation container (+slot);
  CreationContextBuilder (threads it, RAISES if unpopulated for constructed
  spells; existing-creation instance closure added); generalized hydrator
  (cold triple, hot swap x2, hydrated container field, SPECIALIZED instance
  twin published beside the specialized hooks door - plain instance door
  serves during the specialization window); many_only + solo hydrators
  (same pattern); all three lazy-door steps (triple unpack); all three
  family caches (lazy + eager loads); generalized + many_only finalize
  steps (eager/fallback; many_only instance door mirrors its family's
  fast_transient=False rule); spell-level cache loader.
- Consumers: ConduitMeld + SpellSpaceMeld fast lanes call the instance door
  with NO tuple/getitem; both non-dynamic no-overrides arms likewise;
  CreationContext.execute_no_hooks no-overrides branches use it (dynamic
  gate path included).
- Effect: one tuple allocation + one getitem removed from EVERY warm
  no-hooks meld system-wide (shared-allocator pressure under nogil).
- Verified (3.10 harness): every touched file individually py_compile +
  tail-verified; 24/24 + 9/9 + 4/4 + 2/2 suites green. compileall flagged
  conduit.py - REPLICA ROT ONLY (user-disk copy verified intact via file
  tool; file never edited). 3.14t: Not run. KNOWN user-run watchpoints:
  tests constructing HydratedExecutors containers directly need the new
  required field; builder now fail-fasts on stub SpellCodegenCreation
  objects that never populate the instance slot.

## Addendum 2026-07-02m: Specializer moved to the INSTANCE lane (regression fix)
- REGRESSION (caught by user-run component suite after 2026-07-02l): the
  specializing wrapper was installed on the HOOKS door, but the no-hooks
  meld lanes now execute `_no_overrides_instance_executor` only - the
  wrapper never ran, so specialization was silently disabled on the lanes
  that matter.
- FIX: `_install_specializing_door(plain_instance_door=...)` wraps the
  INSTANCE door; the wrapper keeps the instance contract
  (`(meld) -> instance`). On successful specialization it resolves the
  specialized INSTANCE door into its cell and publishes BOTH slots
  (`_no_overrides_instance_executor` = specialized instance door,
  `_no_overrides_executor` = specialized hooks door). On the 3-attempt
  decline it re-pins ONLY the instance slot; the hooks slot already holds
  the plain hooks door. The hydrated container carries the plain hooks
  door plus the final (possibly wrapped) instance door.
- Fix-up landed with it: cache-asset playground loader returns a
  (tuple-door, instance-door) pair and threads the instance door into
  `load_cached`; meld/context/builder test stubs gained the slot; builder
  tests pin the new `no_overrides_instance_executor` fail-fast; wrapper
  unit tests updated to the instance-lane contract.
- Verified (3.10 harness, /tmp shadow of the repo due to VM-replica rot on
  3 files - user disk intact): 24/24 + 9/9 + 4/4 + 2/2 green. 3.14t: user
  reruns --last-failed + component suites + probe/gauntlet pairs.
