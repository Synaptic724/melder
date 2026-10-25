# architecture_patch

## Metadata
- Patch ID: codegen_materialize_namespace_2026_10_25
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T11:34:22Z
- Updated: 2026-10-25T11:34:22Z
- Ticket: TASK-2026-10-10-refuse-materializing-over-live-modules (D-20), parent
  EPIC-2026-10-25-codegen_room_policy_defects

## Patch Scope and Non-Goals
- Objective: `materialize_codegen` must never replace or shadow a live module, and every exit must leave
  `sys.modules` and the parent package attribute as found. The owner's decisions (chat 2026-10-25): the generation
  namespace is a codegen ACL capability rule; materialized code runs with the room's filtered builtins; a frame
  with no namespace rule does not fail closed - the hard refusals below apply under every posture and a declared
  rule only narrows.
- Hard refusals, checked at the verb after validation accepts and before anything is registered or published:
  (1) the name is already in `sys.modules`; (2) its top-level root is the protected core root `melder`; (3) its
  top-level root is in `sys.stdlib_module_names`; (4) its top-level root is an installed import name
  (`importlib.metadata.packages_distributions()`); (5) it is under a denied generation root; (6) the frame
  declares allowed generation roots and the name is under none of them. A refusal is a payload
  (`materialized` False plus `refusal`, the reason naming the name), like a validation refusal.
- Non-goals: live in-place module replacement as a feature (review D7); the crystallizer's own restore,
  rebuild and graft semantics (they publish outside any room's posture, so the name policy sits at the verb);
  an OS boundary (review C6.3). This is policy and defence in depth, not isolation.

## Changed-Components Matrix
| component | change |
| --- | --- |
| Nexus Descriptor And ACL Managers | `materialize_modules` capability operation (validator, builder), compiled into `generation_module_roots` (None when no allow rule) and `denied_generation_module_roots` on the compiled surface; both surface clones carry them |
| Codegen Internal Engine | `CodegenSystem.build_materialize_builtins(context)`: the room's filtered builtins mapping (deny list stripped, D-11 import guard installed) |
| RiftSpace Workstation And Command Surface | `materialize_codegen` name policy, room builtins for the module, failure path removes parent shells it created |
| SyntheticModule Runtime | publish and attach record a displaced non-synthetic module / parent attribute; unpublish, detach and cleanup put it back |

## Interface and Boundary Deltas
- New ACL operation `materialize_modules` (capability ruleset), conditions `module_roots` (non-empty, dotted-legal),
  effects allow and deny; fluent `allow_materialize_module_roots(*roots)` / `deny_materialize_module_roots(*roots)`.
- `CompiledFrameACLAccessSurface.generation_module_roots: Optional[Tuple[str, ...]]`,
  `denied_generation_module_roots: Tuple[str, ...]`. Allowed roots intersect across allow-bearing rulesets (an
  overlay narrows the preset) minus the denied union, as import roots do.
- `materialize_codegen` payload gains `refusal` on a policy refusal. A name is under a root when it equals the root
  or starts with `root + "."`; roots may be dotted.
- `PROTECTED_GENERATION_MODULE_ROOTS = ("melder",)` in stdlib_import_sets.py.

## Cross-Component Invariants
- A successful materialize never changes an entry that existed in `sys.modules` before it.
- A failed materialize leaves `sys.modules` and every parent attribute exactly as before (module and the parent
  shells it created removed).
- Cleanup or unpublish of a SyntheticModule that displaced a non-synthetic module or parent attribute restores it;
  a displaced SyntheticModule is not restored (crystallizer world replacement stays the crystallizer's).
- Materialized code reaches what the room's own code reaches: the same builtins mapping as `execute_codegen`.

## Migration and Rollout Order
1. stdlib_import_sets constant; validator + builder operation.
2. Compiler + compiled surface fields; the two surface clones (`Nexus._clone_compiled_access_surface`,
   StaticFrameViewer) carry them - D-11's integration RED came from a clone dropping a new field.
3. SyntheticModule restoring exits.
4. `CodegenSystem.build_materialize_builtins` + `CodegenNamespaceBuilder.build_builtins`.
5. The verb.
6. Tests, docs, release note, notch, rebuild.

## Rollback Strategy
- Revert the verb, SyntheticModule, engine and ACL edits; nothing persisted or cached reads the new fields.

## Validation Expectations and Evidence Plan
- Red first: symptom-named integration tests (core, `csv`, `json`, `pytest`, `melder.injected_probe`, an unimported
  stdlib and installed name, the failure path, the namespace rule, the builtins) fail on today's code.
- Green: materialize verb, crystallizer restore/rebuild/graft, codegen and ACL tiers, the GIL off and on; the
  probes report every refusal; the expert examples still run.

## Ticket Coverage Map
- N11 -> hard refusals 1-4; C1.4 -> refusals 5-6; R6 -> failure path + SyntheticModule exits; builtins -> engine.

## Unknowns and Decision Requests
- UNKNOWN: none. DECISION: namespace as ACL rule, room builtins, rule narrows (the owner, 2026-10-25).
- Known limit: a successful materialize of a dotted name under a new root leaves its parent shell after the
  module's own cleanup (shells are shared package structure); the failure path removes them.

## Context / Handoff Summary
D-20's name policy at the verb, restoring exits in SyntheticModule, the room's builtins for materialized code.
