# architecture_patch

## Metadata
- Patch ID: codegen_signature_determinism_2026_09_26
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T10:42:09Z

## Patch Scope and Non-Goals
- Objective: make the compiler's codegen signature path ONE implementation that is deterministic across
  interpreter processes for every input the creation cache may persist, and remove the per-root
  pool-sized hashing in phase 8 by hoisting the pass-invariant digest into the analysis pass cache.
  Tranche T1 of the improvement plan (candidates C-H and C-A), owner-approved 2026-09-26.
- Non-goals: no change to phases 5-7 registration or schedule (owner deferred C-B); no change to the
  `.melc` envelope, its generation number or `caching_system.py`; no change to step rows, transient
  schema, manifests, emitters, hydration or the meld door; no change to what invalidates the phase-8
  analysis (phase 5's attach still nulls it every pass).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler and Validation Pipeline (IR seams: signature path) | modify | one leaf implementation of serialize/hash/freeze; canonical freeze only for address-bearing `repr`s (callables, default-`object.__repr__` instances); canonical set handling; every other input byte-identical | none |
| SpellCompiler and Validation Pipeline (phase 8 occurrence analyzer strategy) | modify | pool-invariant rows hashed once per pass; root rows built once; skip check tests the analysis slot first | signature path (hash function) |
| Codegen creation system (shared assets helper facade) | modify | `CodegenCreationSchemaHelpers` delegates its three helpers to the leaf module; keeps its public names | signature path |
| Codegen creation system (creation-cache emission: `manifest_creation_cache.build_package`, `spell_codegen_creation_cache.build_package`, `Spellbook._emit_spell_cache`) | modify | owner option B (2026-09-26): a plan whose contract payload values cannot be replayed from the frozen rows is not emitted into the `.melc`; the call site treats the refusal as "nothing staged" | Interface delta 2a |

## Interface and Boundary Deltas
- Boundary delta 1: a new leaf module `spell_compiler/shared_assets/codegen_signature.py` that imports
  only the standard library. `phases/shared_compiler_executions.py` (phase-side facade) and
  `codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py` (phase-11 facade) both
  import it. The phase-11 subsystem still does not reach back into the phase helper surface (its
  documented rule), and the phase helper surface does not import the phase-11 subsystem: the leaf sits
  below both.
- Interface delta 1: `serialize_codegen_signature_part`, `hash_codegen_signature` and
  `freeze_phase11_schema_value` keep their names, signatures and return types on both facades.
- Interface delta 2 (AMENDED 2026-09-26, implemented rule): `freeze_phase11_schema_value` canonicalizes
  ONLY values whose previous `repr` carried a memory address - functions, bound methods and builtin
  callables render as `("__callable__", module, qualname)`; instances whose type does not override
  `object.__repr__` render as `("__object__", module, qualname of the type)`. Classes, enum members,
  dataclasses and every other value with an address-free `repr` keep their previous bytes, and
  `frozenset` joins the sorted `set` branch. Top-level `set`/`frozenset` parts reaching the serializer
  are frozen (sorted) before pickling (no call site passes one today; the rule closes the hazard).
  Nested containers are not rebuilt by the serializer, because rebuilding changes pickle memo bytes
  for inputs that were already deterministic. The earlier draft rule (classes/enums canonical,
  `__unhashable_object__` marker) is withdrawn: it would have changed bytes for deterministic inputs
  and forced a cache generation bump.
- Interface delta 2a (LIMIT, found at task 2 U3): the frozen payload values are not only hashed. The
  cache-load path hydrates plan steps from the persisted rows and passes `contract_payload_items`
  values to constructors (`_hydrate_steps_from_rows`, manifest compiler bindings), while the hot
  in-process path compiles from the live plan with the raw values. For a non-value payload the two
  paths therefore disagree, before and after this patch: an object payload reached the constructor
  as its `repr` string after a cache hit; it now arrives as the `("__object__", ...)` tuple. Pending
  the owner's ruling (task 2 RISK note: keep and document / refuse cache emission for such spells /
  raise at plan time), this patch changes nothing on that seam.
  RULED 2026-09-26 (owner, option B) -> Interface delta 4.
  CORRECTED 2026-09-26 (owner suite run): the "hot in-process path uses raw values" half is true only
  for the legacy plan compiler. Manifest-first families (generalized, solo, many_only) publish lazy
  doors that hydrate from the manifest rows in-process at first meld, so the frozen projection is
  bound on the hot path as well. Delta 4 is therefore the cache half of the fix; the in-process half is
  an open owner decision (fail fast on non-replayable payload values, or a raw-value side table for
  in-process hydration).
- Interface delta 4 (task 4, emission gate): `CodegenCreationSchemaHelpers` gains two pure helpers -
  `is_replayable_contract_payload_value(value)` (True for `None`/`bool`/`int`/`float`/`str` and for
  tuples of replayable values; False for everything else, because those are exactly the values
  `freeze_phase11_schema_value` returns unchanged and the row hydration passes through) and
  `plan_contract_payloads_are_replayable(plan)` (every `contract_payload` value of every step). Both
  `build_package` builders return `None` instead of a package when a lane plan fails the predicate;
  `Spellbook._emit_spell_cache` stages nothing for `None`, logs once at info level and returns False.
  Row format, manifest schema, hydration and `caching_system.py` are unchanged, so no generation bump.
- Interface delta 3 (phase 8): `analysis_pass_cache["phase8_pool_digest"]` (str) joins the two existing
  slots; the fast key becomes `(root_spell_id, ordered_node_ids, id(path_registry), blueprint_socket_rows,
  pool_digest)` and the input signature `hash(...same parts...)`. `id(path_registry)` remains the
  deliberate process-local part of the key (it scopes the memo to one blueprint object).

## Cross-Component Invariants
- Invariant 1 (byte-compatibility): every signature that was deterministic across processes before this
  patch has the same bytes after it. Consequence: no `.melc` generation bump, no cold reset. Proved by a
  corpus test that captures the gauntlet book's executor signatures BEFORE the change and compares
  after. If the corpus test fails, the patch is not byte-compatible and a generation bump becomes a
  DECISION_REQUEST (coordinated with melder_0's planned generation 11).
- Invariant 2 (determinism): the same book yields the same executor signatures (both lanes) in two
  interpreter processes with different `PYTHONHASHSEED`. A payload object with a default `repr` no longer
  makes a signature process-local; it renders as the stable `("__object__", module, qualname)` tuple
  (identity-only objects deliberately collapse to one value, since identity never reproduced across
  processes).
- Invariant 3 (phase 8 semantics): the occurrence analysis is rebuilt exactly when it was rebuilt before;
  the key and signature change exactly when the same inputs change (hash of a hash of the same rows).
- Invariant 4: no change to the dependency direction between the phase helper surface and the phase-11
  subsystem; the leaf module has no `melder.aether` imports.
- Invariant 5 (cache faithfulness, task 4): a persisted creation payload constructs with the same
  contract payload values the in-process executor constructs with. Enforced at emission: a plan that
  would violate it is never persisted, so such spells recompile phases 8-11 per process (classification
  `mixed`) instead of full-hitting with wrong values.

## Migration and Rollout Order
1. Freeze the shipped helper bodies verbatim as the byte-compatibility oracle
   (`tests/mocks/spellbook/codegen_signature_reference.py`) - this replaces the planned owner-run corpus
   fixture: the oracle is compared against live parts on every run instead of a captured file.
2. Land the leaf module and both facade delegations (task 2); unit tests; determinism and corpus tests.
   LANDED 2026-09-26 (commit 6fc9af345); not yet owner-run.
3. Owner runs the suites; corpus test must pass (Invariant 1) before step 4.
4. Land the phase-8 digest hoist (task 3); unit tests; owner runs the breakdown harness before/after.
5. Promote: `src_components.md` IR seams block (signature path, duplicated helper removed, phase-8 key
   path), regenerate `src_components_index.md`; archive this patch folder.

## Rollback Strategy
- Rollback trigger: corpus test failure that cannot be explained by a previously process-local input;
  any compiler suite regression; a determinism test that still fails after the change.
- Rollback steps: delete the leaf module, restore the two facade bodies from git (pure functions; no
  state), restore the strategy's key builders. No data migration exists to undo.
- Post-rollback verification: compiler suites green; the corpus test passes against the shipped code.

## Validation Expectations and Evidence Plan
- Validation item 1: unit tests for the serializer tags, the freeze cases (class, function, enum member,
  dataclass, default-repr object, nested dict/list/set), set handling and facade delegation identity
  (`tests/unit/melder/spellbook/spell_compiler/shared_assets/test_codegen_signature.py`).
- Validation item 2: component determinism test - two subprocesses, different `PYTHONHASHSEED`, equal
  no-overrides and overrides executor signatures for a plain book (regression guard) and for a book
  whose consumer carries an object-valued `SpellContract` payload through a contracted provider (the
  proof case) (`tests/component/melder/spellbook/test_codegen_signature_determinism.py`).
- Validation item 3: corpus byte-compatibility test (Invariant 1): every `hash_codegen_signature` call
  made through either facade while compiling the plain book is compared with the frozen reference
  digest for the same parts (same component test file).
- Validation item 4: phase-8 unit tests - digest built once per pass over N roots; None-first skip; key
  equality across passes with equal inputs; different digest when a topology row changes.
- Validation item 5 (task 4): predicate matrix (scalars and tuples True; list, dict, set, enum, object,
  callable False); both package builders refuse a probe plan with a non-replayable payload and package
  a replayable one; `_emit_spell_cache` stages nothing on refusal; component: the contract-payload book's
  recompiled plan (object payload) is refused, a string-payload variant is packaged.
- Evidence source 1: owner-run `pytest -q tests/unit/melder/spellbook/spell_crafter tests/component/melder/spellbook`.
- Evidence source 2: owner-run `python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py`
  (plan_group busy at workers=1 before and after task 3).
- All items: "Not run." until the owner reports.

## Ticket Coverage Map
- Epic: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md
- Story: tickets/stories/2026-09-26_signature_determinism_and_phase8_digest_story.md
- Tasks: tickets/tasks/2026-09-26_author_signature_patch_docs_task.md;
  tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md;
  tickets/tasks/2026-09-26_hoist_phase8_pool_digest_task.md

## Unknowns and Decision Requests
- RESOLVED (task 2 U3): the persisted rows' frozen payload values ARE consumed beyond comparison - the
  cache-load path executes them (Interface delta 2a). Expectation "none" was wrong.
- DECISION (owner, 2026-09-26): option B - refuse cache emission for spells whose rows cannot replay
  their contract payload. Implemented as task 4 (Interface delta 4); the verdict is read from the live
  plan, not from a new row field, so the persisted row format is untouched.
- DECISION_REQUEST (owner, open): the in-process projection of non-replayable contract payload values
  in manifest-first families - (1) fail fast at phase 9/11, or (2) raw-value side table for in-process
  hydration (recommended). Touches the generalized/solo/many_only hydrators (override lanes' files).

## Context / Handoff Summary
- What changed: task 2 landed (leaf `spell_compiler/shared_assets/codegen_signature.py`, both facades
  delegating, reference oracle, unit and component tests; commit 6fc9af345). Task 3 (phase-8 digest)
  not started. Interface delta 2 amended to the implemented rule; delta 2a records the cache-path limit.
- What remains: owner-run suites for tasks 2-4; task 3 (phase-8 digest) is in review; task 4 (emission
  gate) is in progress.
- Next entrypoint: tickets/tasks/2026-09-26_gate_cache_emission_on_replayable_payloads_task.md (G2).
