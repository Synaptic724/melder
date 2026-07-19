# Patch 1: Thread `meld` into the creation-execution path (plumbing only)

## Metadata
- Patch ID: PATCH-2026-06-23-thread-meld-creation-execution
- Program: "scope authoritative" (lane 1 — runtime store routing)
- Status: PROPOSED (awaiting certification)
- Owner: cowork
- Agent Name: optimizer_0
- Risk: medium (touches the threadsafe meld hot path + generated codegen signatures)
- Sandbox validation: NOT POSSIBLE (sandbox is Py3.10; melder is 3.14t-only)

## Objective
Make the resolving meld (`ConduitMeld` or `SpellSpaceMeld`) available inside the
creation-execution path by passing it as a NEW, ADDITIVE, UNUSED parameter
through the doors, `CreationContext`, and the generated executor signatures. This
is the enabling plumbing for the lane-1 fix; it does NOT change any store
selection. Behavior is intended to be byte-identical.

## Why (links to evidence)
The generalized step-plan executor selects each step's store from ONE
root-derived `caller_creations`/`owner_creations`
(`generalized_no_overrides_codegen_creation_compiler.py:711-712, 803, 808`), so a
dependency step of a different existence than the root gets the wrong Creations
object — the lineage/cluster fragmentation and the spellspace leak. The fix
(Patch 2) is to have each step pull its OWN store from the meld by existence. The
meld already is the store-selection authority on the direct path
(`conduit_meld.py:344-349`). This patch only gets the meld INTO the compiled code.

## Scope Boundaries
- IN: add a `meld` parameter (default sentinel/None) to the execution seam and
  the generated executor/door signatures; pass the resolving meld (`self`) from
  both door classes. NO reads of `meld`. NO store-selection changes.
- OUT (Patch 2): `_append_step_creations_target_source` rewrite to bind each
  step's `creations_i` from `meld._creations` / `meld._root_creations` /
  `meld._cluster_creations.resolved_store()` / spellspace scope store.
- OUT (later): `SpellSpaceScopeStrategy` (build-time gate) — spells longer-lived
  than `many` must not depend on spellspace; spellspace may depend on broader.

## Exact edit sites (additive `meld` param, behavior-preserving)
Python seam:
- creation_context.py: `execute` (164) and `execute_no_hooks` (209) — add `meld`
  param; forward it on the executor calls at 179, 181, 203, 205, 224, 226, 248, 250.
- conduit_meld.py: pass `meld=self` at 273 (fast no-ovr), 372 (execute_no_hooks),
  377 (no-ovr direct), 396 (overrides direct), 418 (execute hooks).
- spellspace_meld.py: mirror at 279, 374, 379, 400, 422.

Generated codegen (add `meld=None` to emitted `def ...` signatures; door forwards
`meld=meld` to inner executor):
- shared_assets/creation_runtime_door_compiler.py: door execution signatures
  (~467, ~498) + the inner-executor call (~1125-1127).
- strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py +
  solo_overrides_codegen_creation_compiler.py: every `_build_source` def.
- strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py
  (710-713) + generalized_overrides_codegen_creation_compiler.py.
- strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py +
  many_only_overrides_codegen_creation_compiler.py.

## Behavior-preservation argument
`meld` is added with a default and is never read in Patch 1. Every existing store
path (`caller_creations`, `owner_creations`, `_spell._owner_creations`,
`prebound_owner_creations`) is untouched. A missed call site still works because
the param defaults and is unused. Therefore execution results must be identical.

## Threadsafety (3.14t / no-GIL)
`meld` is the per-call resolving door; it is passed read-only and adds no shared
mutable state. The fast-door memoization entries are not changed in Patch 1.

## Caches to clear on apply (because emitted source changes)
- executor_code_cache (emitted-source code-object cache; source_name includes the
  signature, so new signatures key distinctly — but force-clear to be safe)
- executor_factory_cache / manifest caches if they retain compiled executors.

## Validation (acceptance test — MUST be byte-identical to baseline)
- Baseline (pre-patch) and post-patch, run on the 3.14t venv from repo root:
  - python -m pytest tests/integration/melder/conduit/test_conduit_integration_scope_ordering_matrix.py tests/integration/melder/conduit/test_conduit_integration_scope_resolution_alignment.py tests/integration/melder/conduit/test_conduit_integration_scope_structural_resolution.py tests/integration/melder/conduit/test_conduit_integration_spellspace_scope_safety.py -q
  - Plus a broad sanity sweep: python -m pytest tests/integration/melder/conduit -q
- PASS CRITERION: identical pass/fail set to the pre-patch baseline. ANY change
  (new failure, new error, collection error) = plumbing regression -> rollback.
- NOT a goal: fixing any red. Patch 1 fixes nothing; Patch 2 does.

## Rollback
Revert the parameter additions (single logical change); no data/state migration.

## Notes
- DATETIME: 2026-06-23
  TYPE: PLAN
  CLAIM: Patch 1 is plumbing only; the lineage/cluster/spellspace reds remain red
    until Patch 2 rewrites per-step store selection to read from `meld`.
  REREAD: REQUIRED
