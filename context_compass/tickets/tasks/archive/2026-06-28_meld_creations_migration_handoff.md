# Meld Creations Migration — Handoff (2026-06-28, optimizer_0)

## Goal
Migrate the phase-11 codegen executors OFF the old pre-selected-store contract
(`caller_creations` / `owner_creations` / `caller_creations_lock_held` params,
threaded in by the door) and ONTO the **meld contract**: the executor takes the
resolving `meld` and reads its OWN store off it, per existence. This fixes the
"scope not authoritative" bug where lineage/cluster/spellspace resolved from the
wrong store when reached as a dependency (the door pre-selected one store and
overloaded `owner_creations` for unique + lineage-root + cluster-leader).

## The contract (store + lock per existence)
Resolved off the meld, mirroring the meld front doors (`conduit_meld.py:317`,
`spellspace_meld.py:328`, `meld_existing_spell:537`):

| existence | store | lock (in the DOOR, not the inner) |
|---|---|---|
| `unique` | `spell._owner_creations` | `_spell._lock` (SPELL lock — special) |
| `unique_per_conduit` | `meld._conduit_creations` | store `._lock` |
| `unique_per_spell_space` | `meld._spellspace_creations` | store `._lock` |
| `unique_per_conduit_lineage` | `meld._root_creations` | store `._lock` |
| `unique_per_conduit_cluster` | `meld._cluster_creations.resolved_store()` | store `._lock` |
| `many` | `meld._spellspace_creations or meld._conduit_creations` | NONE (transient, lockless append) |
| `existing_creation` | `spell.user_created_object` | none |

Key facts established:
- `Creations._lock` is an `RLock` (re-entrant), so `caller_creations_lock_held`
  was a pure micro-opt (skip a redundant re-acquire). Removing it is safe;
  worst case is one re-entrant acquire. The meld does NOT hold the store lock —
  the get-or-create DOOR does, and always holds it when it calls the inner for
  cached routes. `many` has no door lock (not cached).
- `many` = transient (new instance per meld). Append is lockless by decision
  (owner: "many means transient, no lock"). no_overrides is lockless; the rare
  overrides path may keep its lock — both acceptable.
- The inner executors never lock; the door owns locking. So the migration is
  purely: signature → `meld`, route the store off the meld by existence, drop
  the `caller_creations`/`owner_creations`/`lock_held` params + the hoisted
  `caller_creations is None` guard + the `lock_held` spell-lock opt.

## Migration pattern (applied per compiler)
1. Emitted executor signature: drop `caller_creations`, `owner_creations`,
   `caller_creations_lock_held`; first param becomes `meld`. (Transient/fast
   path: `()` for solo many-fast, else `meld`.)
2. Replace per-step `target_kind` routing with existence→meld-store routing
   (the table above). Keep `ManyOnly/SpellGeneralizedCodegenPlanTargetKind`
   class + namespace entry (owner wants the selection flag kept, even if now
   unused).
3. Remove the hoisted `caller_creations is None` guard.
4. Remove the `lock_held` spell-lock optimization (`use_spell_lock = not (...)`
   → `use_spell_lock = True`).
5. `many` register → lockless `add_many_creations` (drop `with creations._lock:`).
6. Door / finalize / hydrator: stop passing `owner_creations=` to the shared
   `compile_creation_context_hooks_*` functions (those params were removed).
   The `execute_with_overrides` closure signature → `(meld, overrides)` and it
   calls the inner with `(meld, override_map, root_positional_override)`.

## DONE (migrated + py_compile OK via null-strip; NOT run on 3.14t)
- **solo**: `solo_no_overrides_codegen_creation_compiler.py`,
  `solo_overrides_codegen_creation_compiler.py`, `solo_hydrator.py`. unique →
  `spell._owner_creations`. Deleted dead `solo_finalize_creation_context_step.py`.
- **shared door** `shared_assets/creation_runtime_door_compiler.py`: fully on
  meld; `owner_creations` param removed from all 4 compile fns; `lock_held` 3rd
  arg removed. Door many-fast now emits `_no_overrides_executor(meld)` (passes
  meld) — see RUNTIME FIX below.
- **base Meld** (`meld.py`/`conduit_meld.py`/`spellspace_meld.py`): removed the
  dead `creations` slot from `_fast_meld_doors` tuple (now `(spell, ctx, epoch)`)
  + the now-dead front-door store pre-selection; tuple annotation + `Creations`
  import updated.
- **many_only**: `many_only_no_overrides_codegen_creation_compiler.py` (resolve
  scope store once, lockless),
  `many_only_overrides_codegen_creation_compiler.py` (both source paths,
  existence→meld routing), `many_only_finalize_creation_context_step.py`
  (`owner_creations` dropped from door compiles; `execute_with_overrides` → meld).
- **generalized no_overrides** (LIVE path = manifest):
  `generalized_manifest_no_overrides_compiler.py` `emit_step_plan_source` +
  `_append_creations_target_source` (existence→meld routing, lockless many,
  lock_held removed); `generalized_hydrator.py` (owner_creations dropped from
  both shared-door calls). Transient source shared from
  `generalized_no_overrides_codegen_creation_compiler.py` (migrated). The eager
  `generalized_no_overrides_codegen_creation_compiler.py` step-plan builder is
  the LEGACY path behind the dead `GeneralizedFinalizeCreationContextStep` —
  migrated too (harmless), but not the live path.

## REMAINING — generalized OVERRIDES (the last big lane)
Live path = manifest (strategy chain is `GeneralizedManifestStep +
GeneralizedLazyDoorStep`; `GeneralizedFinalizeCreationContextStep` is DEAD).
1. `generalized_manifest_overrides_runtime.py` — the LIVE overrides runtime
   (replaces the dead finalize step's `_build_overrides_runtime`). Passes
   `owner_creations=` at ~284/389/447. Migrate its signature + inner calls to
   `meld` (same as many_only `execute_with_overrides`).
2. `generalized/hydration/generalized_hydrator.py::_hydrate_overrides_runtime`
   (~line 250) — the overrides hydrate path; check/strip `owner_creations`.
   (The `overrides_door` shared-door call already had owner_creations removed.)
3. `generalized_overrides_codegen_creation_compiler.py` — the overrides inner
   source (generic + shape paths, ~2500 lines). Apply the migration pattern:
   signature → `meld`, existence→meld-store routing, drop guard + lock_held opt,
   lockless many. Mirror what was done in
   `many_only_overrides_codegen_creation_compiler.py`.
4. Verify `generalized_manifest_overrides_compiler.py` if a separate manifest
   overrides source exists (parallels the no_overrides eager-vs-manifest split).

## Cleanup (lower priority, after overrides)
- Dead helpers referencing the old contract (never called):
  `generalized_no_overrides_codegen_creation_compiler.py::_select_creations_for_target_kind`,
  `many_only_overrides...::_append_overrides_shape_owner_creations_source`.
- Dead legacy step files: `generalized_finalize_creation_context_step.py`
  (parallels the deleted solo finalize). The eager generalized no_overrides
  compiler's step-plan builder.
- Stale comment `generalized_manifest_no_overrides_compiler.py:~371`.
- The dead `overrides_maybe_none=True` branches in the shared door compiler.

## 3.14t TEST RUN — two failure classes (owner ran, 2026-06-28)

### Class A — RUNTIME bug (FIXED)
`TypeError: _no_overrides_codegen_creation_executor() missing 1 required
positional argument: 'meld'` at door template
`<creation_context_no_overrides_only_template:many:1:1>`, via
`generalized_hydrator.py:204 _cold_no_overrides_door -> no_overrides_executor(...)`.
Root cause: the shared door's many-FAST route was emitting
`_no_overrides_executor()` (no args) — correct only for solo's old zero-arg
many-fast inner — but generalized/many_only transient inners take `meld`. The
door is shared, so it must pass `meld` and ALL transient inners must accept it.
FIX (done): door many-fast → `_no_overrides_executor(meld)`
(`creation_runtime_door_compiler.py`); solo many-fast inner →
`def _solo_no_overrides_codegen_creation_executor(meld):`
(`solo_no_overrides_codegen_creation_compiler.py`, both fast + non-disposal `many`
branches already on meld). Generalized/many_only already take meld. Re-run to
confirm.

### Class B — TEST pins the OLD 4-tuple (NOT yet done)
`ValueError: not enough values to unpack (expected 4, got 3)` /
`IndexError: tuple index out of range` (`entry[3]`) /
`AssertionError: scope_c fast entry captured a foreign store`
(`fast_entry[2] is scope_c._creations`, got an int) — all in
`tests/component/.../test_conduit_component_fast_meld_door.py`.
Root cause: we intentionally removed the `creations` slot from
`_fast_meld_doors`, so the tuple is now 3-element `(spell, ctx, epoch)`; epoch
moved from index 3 → 2. These tests still unpack 4 and assert the captured store
at index 2 — they pin the OLD design where the fast lane captured + used a
pre-selected store. That mechanism is gone by design (the fast lane now reads the
store off the meld at call time). DECISION NEEDED from owner: update these tests
to the 3-tuple (drop the store-capture asserts; epoch is `entry[2]`; the
scope-isolation guarantee is now proven by the executor reading
`meld._spellspace_creations` at runtime, not by a captured store), OR revert the
`_fast_meld_doors` slot removal if the captured store is still wanted as a debug
artifact. Recommend updating the tests — the slot removal was the owner's call
("why would creations show up in fast_doors").

### Class C — cache-bridge left on old contract (FIXED)
`test_melder_gauntlet` failed at `meld.py:822 SpellbookValidationError`
(`BootstrapDObject` invalid, EMPTY diagnostics) via `_ensure_resolution_resolvable`.
Empty diagnostics = an exception during phase-5..11 resolution was swallowed and
the spell marked invalid. Root cause: `codegen_creation/spell_codegen_creation_cache.py`
`load_creation_context` (the LIVE cache-reload door-wrap path) + its
`_build_missing_overrides_executor` were never migrated — they still passed
`owner_creations=spell._owner_creations` into the `compile_creation_context_hooks_*`
fns (whose `owner_creations` param we removed) → `TypeError: unexpected keyword
argument 'owner_creations'` at build, swallowed → invalid. BootstrapDObject hits
BOTH (no-overrides path -> line 246; no overrides payload -> missing-overrides
build -> line 433). FIX (done): removed both `owner_creations=` kwargs; migrated
`_lazy_execute_with_overrides` and the missing-lane `execute_with_overrides` from
`(caller_creations, overrides, caller_creations_lock_held, root_creations)` to
`(meld, overrides)` calling `override_runtime(meld, overrides)`. File compiles
(null-strip); only residual `owner_creations` is a docstring at line 234.
LESSON: grep the WHOLE `codegen_creation_system` tree for `owner_creations` /
`caller_creations` / `caller_creations_lock_held` — the door+inner compilers were
migrated but the cache-bridge that WRAPS them was missed. Still-flagged-but-DEAD:
`strategies/generalized/steps/generalized_finalize_creation_context_step.py`
(behind dead `GeneralizedFinalizeCreationContextStep`) — confirm dead before
trusting; if the gauntlet still fails after this, that's the next suspect.

## Verification
- Sandbox is Python 3.10 + the FUSE mount injects null bytes on read, so
  `py_compile` direct is a false negative. Use: `tr -d '\000' < file > /tmp/x.py
  && python3 -m py_compile /tmp/x.py`. The Read tool is authoritative.
- Owner runs the real tests on 3.14t (no-GIL). All "compiles" above are
  syntax-only; runtime/threadsafety validation is the owner's 3.14t run.
