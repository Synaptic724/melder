# architecture_patch

## Metadata
- Patch ID: codegen_open_builtin_posture_2026_10_25
- Status: decided - `open` (D2) and hybrid's pathlib route (B; the owner, chat 2026-10-25, "focus on B")
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T02:10:23Z
- Updated: 2026-10-25T08:06:02Z
- Ticket: TASK-2026-10-10-deny-file-access-under-safe-codegen (D-10), parent EPIC-2026-10-25-codegen_room_policy_defects

## Patch Scope and Non-Goals
- Objective: room code under the safe, hybrid and precision codegen postures can no longer call or name the `open`
  builtin. Each refuses it at validation and leaves it out of the runtime `__builtins__` (the owner's D2 decision,
  2026-10-25). The engine's no-projection default posture, today a literal copy of the safe deny list, denies it
  too and from now on reads the safe tuple itself. Permissive and full_access keep `open` and say so. Hybrid's
  import list drops `pathlib` (the owner's answer B): it moves from the common root list to the permissive
  extras, so hybrid refuses `import pathlib` and permissive keeps it. Every profile's file posture - `open`,
  `io.open`, `os.open` and pathlib writes - is pinned by a symptom-named test.
- Non-goals: an OS boundary (separate process or user, read-only mounts; review C6.3, D2 item 4); D-11
  (`__import__`) and D-20 (materialize); ProtocolCrafter's writers; any other allow- or deny-list entry (only
  `pathlib` moves, B below). Nothing here is protection: the profiles and gates run in
  the process whose code they check, so they are policy and defence in depth (review C6.1; wording rule C6.4).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Nexus Descriptor And ACL Managers - codegen profiles (`nexus/acl/configurations/profiles/codegen/`) | modify | `open` joins the denied-builtin tuple safe, hybrid and precision share; `pathlib` moves from the common import-root list to the permissive extras (B); each profile docstring states its file posture | none |
| Codegen Internal Engine - `CodegenSystem` default posture | modify | the no-projection default takes `__import__` plus the safe tuple instead of a hand-kept copy, so it denies `open` and cannot fall behind safe again | the codegen profiles' tuple |

No code_description_patch: the gate pipeline (compiler -> compiled surface -> namespace configuration -> the two
static gates and the runtime builtins strategy), its error texts, ordering and locking are unchanged; only the
deny list's contents and the default posture's source change.

## Interface and Boundary Deltas
- No signature changes. Behaviour (Breaking for room code that used `open`): under safe, hybrid, precision (as
  profile or overlay) and the no-projection default, a call `open(...)` is refused by the builtin gate with
  "Builtin 'open' is not allowed in this codegen mode."; a bare reference (`f = open`) by name resolution with
  "Name 'open' is not available in the codegen namespace." (the builtin gate runs first); and `open` is absent
  from the room's runtime `__builtins__`, so a form the static gates miss raises NameError at run time.
- `CompiledFrameACLAccessSurface.denied_builtin_names` for those postures gains "open" (the tuple stays sorted).
- Hybrid (B): `import pathlib` is refused by the import gate with "Import root 'pathlib' is not allowed in this
  codegen mode."; hybrid's compiled `allowed_import_module_roots` loses "pathlib" (`HYBRID_IMPORT_MODULE_ROOTS`
  is the common list); `PERMISSIVE_IMPORT_MODULE_ROOTS` - the common list plus the extras - keeps it; precision's
  own list never had it.
- New import edge: `nexus/rift/codegen_system/codegen_system.py` imports `SAFE_DENIED_BUILTIN_NAMES` from
  `nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py`, a leaf module that imports nothing.

## Cross-Component Invariants
- The engine's no-projection default posture denies exactly `__import__` plus what the safe profile denies.
- The deny list reaches validation and run time through one path, unchanged: profile rule -> `FrameACLCompiler`
  (denied minus explicitly allowed) -> compiled surface -> namespace configuration -> `CodegenBuiltinPolicyStrategy`,
  `CodegenNameResolutionStrategy` and `CodegenBuiltinsStrategy`.
- A frame's own `builtin_names` allow rule can still re-allow `open` for that frame (the compiler's existing
  "denied minus allowed"); this patch changes the presets, not that mechanism.
- Nothing persisted, cached or recorded reads the deny lists (they are compiled per projection), so no cache
  generation or record version moves.

## Migration and Rollout Order
1. Red: the strict xfail's assertion fails today; add the per-profile file-posture tests and the no-projection
   default tests, and see the safe/hybrid/precision/default `open` cases fail.
2. Add "open" to `SAFE_DENIED_BUILTIN_NAMES` (hybrid and precision alias it). After the owner's B: move
   "pathlib" from `_COMMON_SAFE_IMPORT_MODULE_ROOTS` to `_PERMISSIVE_EXTRA_IMPORT_MODULE_ROOTS`, the hybrid
   pathlib row flipped to refused and seen red first.
3. The engine default reads `("__import__",) + SAFE_DENIED_BUILTIN_NAMES`.
4. Profile docstrings state each file posture; the default posture's docstring states its rule.
5. Remove the strict xfail marker (its test passes); codegen unit, component and integration tiers green, GIL off
   and on.
6. src_components and src_architecture, tests_components, the release note; notch; closure; rebuild last.

## Rollback Strategy
- Rollback trigger: a supported room workflow needs `open` under safe, hybrid or precision (the ticket's
  FAILURE_ESCALATION, a DECISION_REQUEST).
- Rollback steps: remove "open" from the tuple; restore the strict xfail; move "pathlib" back to the common
  list and flip the hybrid row back; revert the release-note entries. The default posture can keep reading the
  safe tuple.
- Post-rollback verification: the pinned file-posture tests for those postures fail as expected (they pin the
  refusal) and the reproducer reports the writes accepted.

## Validation Expectations and Evidence Plan
- `test_safe_profile_refuses_writing_files` passes without its marker (tests/integration/melder/aether/
  test_codegen_core_boundary_integration.py).
- New symptom-named tests pin each posture's `open` (call, read, bare reference), `io.open`, `os.open` and pathlib
  write, and the no-projection default (unit and integration).
- Tiers: the codegen/ACL unit files, tests/component/melder/aether and tests/integration/melder/aether on 3.14.7t,
  the GIL off and on; the reproducer `codegen_probe.py` rerun reports refusals under safe, hybrid and
  hybrid+precision. Windows and hosted CI: Not run until seen.

## Ticket Coverage Map
- Epic: EPIC-2026-10-25-codegen_room_policy_defects
- Story: none
- Tasks: TASK-2026-10-10-deny-file-access-under-safe-codegen

## Unknowns and Decision Requests
- DECISION (the owner, chat 2026-10-25: "yeah do that stuff", then "focus on B"): B. The request it answers,
  as it was put - hybrid's import allow list includes `pathlib`
  (it is the shared "common" root list), so after this patch hybrid code still reads and writes files through
  `pathlib.Path` - measured at 0.2.8267: pathlib-write accepted under hybrid, refused under safe (imports off) and
  hybrid+precision (precision's list leaves it out). Options:
  (A) keep `pathlib` on hybrid's list; document hybrid as the rung that allows file I/O through pathlib only.
  (B) move `pathlib` from the common list to the permissive extras: hybrid loses it (pure path arithmetic
      included), permissive keeps it, precision and safe are unchanged.
  Recommendation: B. Hybrid's docstring says it denies direct mutation, and the owner denied `open` there; with
  A, hybrid's file posture still depends on which module the code imports.
- FACT (no action proposed): hybrid also allows `inspect`, which reads the source text of objects the code can
  reach. That is the C3.2 read permission (agents may read source), not a file-write route.
- Resolved at the red run (2026-10-25T02:16:35Z): the `io.open` and `os.open` refusals under hybrid and
  precision come from their allow lists ("Import root 'io' is not allowed in this codegen mode.").

## Context / Handoff Summary
- What changed: the `open` change, the engine default and the docs landed (ticket Notes of 2026-10-25); the
  owner chose B for pathlib.
- What remains: B's move and its red/green run; the graph; notch, release note, closure, rebuild.
- Next entrypoint: the red tests in test_codegen_core_boundary_integration.py and the codegen unit matrix.
