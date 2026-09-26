# architecture_patch

## Metadata
- Patch ID: codegen_signature_determinism_2026_09_26
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T09:05:00Z

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
| SpellCompiler and Validation Pipeline (IR seams: signature path) | modify | one leaf implementation of serialize/hash/freeze; canonical freeze for classes, functions, enums; explicit marker for other objects; canonical set handling | none |
| SpellCompiler and Validation Pipeline (phase 8 occurrence analyzer strategy) | modify | pool-invariant rows hashed once per pass; root rows built once; skip check tests the analysis slot first | signature path (hash function) |
| Codegen creation system (shared assets helper facade) | modify | `CodegenCreationSchemaHelpers` delegates its three helpers to the leaf module; keeps its public names | signature path |

## Interface and Boundary Deltas
- Boundary delta 1: a new leaf module `spell_compiler/shared_assets/codegen_signature.py` that imports
  only the standard library. `phases/shared_compiler_executions.py` (phase-side facade) and
  `codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py` (phase-11 facade) both
  import it. The phase-11 subsystem still does not reach back into the phase helper surface (its
  documented rule), and the phase helper surface does not import the phase-11 subsystem: the leaf sits
  below both.
- Interface delta 1: `serialize_codegen_signature_part`, `hash_codegen_signature` and
  `freeze_phase11_schema_value` keep their names, signatures and return types on both facades.
- Interface delta 2: `freeze_phase11_schema_value` renders classes and functions as
  `"<module>:<qualname>"`, enum members as `"<module>:<qualname>:<name>"`, and any other non-primitive
  object as the marker tuple `("__unhashable_object__", "<module>:<qualname of its type>")` instead of
  `repr(value)`. Sets and frozensets reaching the serializer directly are sorted through the same freeze
  before pickling (today no call site passes one; the rule closes the hazard).
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
  makes a signature process-local; it makes it explicitly marked, which is a stable string.
- Invariant 3 (phase 8 semantics): the occurrence analysis is rebuilt exactly when it was rebuilt before;
  the key and signature change exactly when the same inputs change (hash of a hash of the same rows).
- Invariant 4: no change to the dependency direction between the phase helper surface and the phase-11
  subsystem; the leaf module has no `melder.aether` imports.

## Migration and Rollout Order
1. Capture the corpus fixture (executor signatures for the gauntlet book) with the shipped code
   (owner-run script under `artifacts/codegen_signature_determinism_20260926/`).
2. Land the leaf module and both facade delegations (task 2); unit tests; determinism and corpus tests.
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
  dataclass, default-repr object, nested dict/list/set), set handling and facade delegation identity.
- Validation item 2: component determinism test - two subprocesses, different `PYTHONHASHSEED`, equal
  no-overrides and overrides executor signatures for the gauntlet book.
- Validation item 3: corpus byte-compatibility test (Invariant 1).
- Validation item 4: phase-8 unit tests - digest built once per pass over N roots; None-first skip; key
  equality across passes with equal inputs; different digest when a topology row changes.
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
- UNKNOWN: whether any consumer relies on the exact `repr` of an object-valued contract payload inside a
  persisted manifest for anything other than signature comparison (grep at task 2 start; expected none).
- DECISION_REQUEST: none now. The freeze rule (Interface delta 2) is the default; the owner may replace
  the marker with a hard refusal (raise at plan time) in the component patch.

## Context / Handoff Summary
- What changed: nothing in `src/` yet; this patch defines the contract for tasks 2 and 3.
- What remains: tasks 2 and 3 after the owner confirms each Propose -> Confirm message.
- Next entrypoint: tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md (U1).
