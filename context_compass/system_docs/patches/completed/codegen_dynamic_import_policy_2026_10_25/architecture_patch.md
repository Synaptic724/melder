# architecture_patch

## Metadata
- Patch ID: codegen_dynamic_import_policy_2026_10_25
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T09:56:38Z
- Updated: 2026-10-25T09:56:38Z
- Ticket: TASK-2026-10-10-enforce-import-policy-on-dynamic-imports (D-11), parent
  EPIC-2026-10-25-codegen_room_policy_defects

## Patch Scope and Non-Goals
- Objective: under every codegen posture that enables imports with an allow or deny list - hybrid, the precision
  overlay and permissive - a `__import__(...)` call must answer to the same compiled import roots as an import
  statement, instead of loading any root. The owner's decision (chat 2026-10-25) is A + B. A (static): wherever an
  import list applies, the two static name gates refuse a reference to the `__import__` name, naming it. B
  (runtime): the room's runtime `__builtins__['__import__']` becomes a wrapper that checks each import's root
  against the compiled allowed and denied roots and raises ImportError naming the root, so an import statement of
  an allowed root keeps working and a denied root is refused at run time. full_access stays unconstrained (no
  list, so no static denial and no wrapper). safe is already covered (imports off makes `__import__` a denied
  builtin). Every route is pinned by a symptom-named test, and the four strict xfails in
  test_codegen_core_boundary_integration.py pass without their marker.
- Non-goals: an OS boundary (separate process or user; review C6.3); the contents of the allow and deny lists
  (an owner decision under D2); `open` (D-10, landed 0.2.8270); materialize_codegen (D-20). Nothing here is
  protection or isolation: the gates and the wrapper run in the process whose code they check, so they are policy
  and defence in depth (review C6.1; wording rule C6.4).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Nexus Descriptor And ACL Managers - `FrameACLCompiler` + `CompiledFrameACLAccessSurface` + `stdlib_import_sets` | modify | compile a new `static_only_denied_builtin_names` set (`__import__` when imports are on and a list applies) and carry it on the compiled surface; one name tuple `IMPORT_BUILTIN_NAMES` in the leaf module | none |
| Codegen Internal Engine - validation strategies, `CodegenNamespaceConfiguration`, `CodegenBuiltinsStrategy`, `CodegenSystem` default | modify | A: the builtin gate and name resolution read `denied_builtin_names` united with `static_only_denied_builtin_names`. B: the builtins strategy keeps the name present and wraps it. The default posture carries the new field. | the compiler's new field |

A `code_description_patch` accompanies this patch: it adds a new policy-gate control-flow element (B's runtime
`__import__` wrapper) and a new static-only denial path through two existing gates.

## Interface and Boundary Deltas
- No public signature changes. New internal field `static_only_denied_builtin_names: Tuple[str, ...]` on
  `CompiledFrameACLAccessSurface` and `CodegenNamespaceConfiguration` (default `tuple()`), plus its accessor.
- Behaviour (Breaking for room code that used `__import__` under a listed posture): under hybrid, precision (as
  profile or overlay) and permissive, a call `__import__('subprocess')` is refused by the builtin gate with
  "Builtin '__import__' is not allowed in this codegen mode."; a bare reference (`f = __import__`) by name
  resolution with "Name '__import__' is not available in the codegen namespace." (the builtin gate runs first on a
  call). Under full_access both are accepted. At run time, under a listed posture, the room's
  `__builtins__['__import__']` is a wrapper that raises ImportError "Import root '<root>' is not allowed in this
  codegen mode." for a denied or unlisted root and delegates allowed roots to the real import.
- `CompiledFrameACLAccessSurface.static_only_denied_builtin_names` is `('__import__',)` for hybrid, precision
  and permissive, and `()` for full_access and safe (safe keeps `__import__` in `denied_builtin_names` via the
  imports-off path, so it is fully denied there).
- New import edge: `frame_acl_compiler.py` and `codegen_builtins_strategy.py` import `IMPORT_BUILTIN_NAMES`
  from `nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py`, the same leaf module D-10 uses.

## Cross-Component Invariants
- Every import answers to the compiled roots, statement or call: statements through B's wrapper, `__import__`
  references through A's two static gates, and dynamic forms the static gates miss through B's wrapper at run time.
- `static_only_denied_builtin_names` is denied by the static gates only and is NEVER removed from the runtime
  `__builtins__` (that is what keeps the name present for import statements and for B's wrapper). `open` and
  the other `denied_builtin_names` are still stripped from the runtime builtins as before.
- B installs its wrapper exactly when imports are enabled and an allow or deny list applies; full_access (imports
  on, no list) keeps the real `__import__`.
- A frame's own `builtin_names` allow rule can still re-allow a name in `denied_builtin_names`; it does not
  touch `static_only_denied_builtin_names`, which is derived from the import-list posture, not from builtin
  rules.
- Nothing persisted, cached or recorded reads the deny/allow lists or the new field (each projection compiles its
  own), so no cache generation or record version moves. No lock or lock-order edge is added.

## Migration and Rollout Order
1. Red: remove the four strict xfail markers so the dynamic-import tests fail on their assertion; add the new
   symptom-named cases (hybrid/precision/permissive `__import__` of denied and unlisted roots refused; allowed
   root and import statements still work; full_access accepts; the B runtime wrapper refuses a denied root).
2. Add `IMPORT_BUILTIN_NAMES = ("__import__",)` to stdlib_import_sets.py.
3. Compiler: compute `static_only_denied_builtin_names` and carry it on the compiled surface; thread the field
   through `CodegenNamespaceConfiguration` and `CodegenSystem` default.
4. A: builtin gate and name resolution read `denied_builtin_names | static_only_denied_builtin_names`.
5. B: builtins strategy keeps stripping `denied_builtin_names` only, then wraps `__import__` when a list
   applies.
6. Remove the xfail markers (tests pass); codegen unit, component and integration tiers green, GIL off and on;
   measure that an allowed import keeps its cost.
7. src_components, src_architecture, tests_components, the graph, the release note; notch; closure; rebuild last.

## Rollback Strategy
- Rollback trigger: a runtime guard changes import-statement behaviour for allowed roots (the ticket's
  FAILURE_ESCALATION), or an existing test depends on `__import__` under a listed posture.
- Rollback steps: drop the `static_only_denied_builtin_names` reads from the two gates, stop installing the
  wrapper, remove the field, restore the four strict xfail markers, revert the release-note entry. No persisted
  state is involved.
- Post-rollback verification: the reproducer reports `__import__` of denied roots accepted again under hybrid.

## Validation Expectations and Evidence Plan
- The four strict xfails `test_hybrid_refuses_dynamic_imports_of_its_denied_roots` pass without their marker.
- New symptom-named tests pin: `__import__` of subprocess/socket/importlib/melder refused under hybrid,
  precision and permissive (criteria 1-2); an allowed-root `__import__` and import statements still work
  (criterion 3); full_access accepts `__import__('melder')` (criterion 2); and B's runtime wrapper refuses a
  denied root with ImportError naming it while delegating an allowed root (criterion 4).
- Tiers: the codegen/ACL unit files, tests/component/melder/aether and tests/integration/melder/aether on
  3.14.7t, the GIL off and on; the reproducer codegen_probe2.py rerun reports refusals. Windows and hosted CI:
  Not run until seen.

## Ticket Coverage Map
- Epic: EPIC-2026-10-25-codegen_room_policy_defects
- Story: none
- Tasks: TASK-2026-10-10-enforce-import-policy-on-dynamic-imports

## Unknowns and Decision Requests
- DECISION (the owner, chat 2026-10-25, answering the decision request): A + B, the recommended option, with A
  static-only (it must not reuse `denied_builtin_names`, which also strips the runtime name an import statement
  needs). Recorded in the ticket's DECISION note of 2026-10-25T00:37:11Z and his go of 2026-10-25.
- FACT (no action proposed): with A denying the `__import__` name and the import gate denying import statements
  of denied/unlisted roots, no plain source construct reaches a denied import that B uniquely catches; B is the
  runtime backstop, pinned by a component test that invokes the installed wrapper directly (criterion 4) plus an
  end-to-end test that an allowed import statement executes through it (criterion 3).

## Context / Handoff Summary
- What changed: nothing yet (patch docs first).
- What remains: red tests, A + B, the graph, notch, release note, closure, rebuild.
- Next entrypoint: `IMPORT_BUILTIN_NAMES` in stdlib_import_sets.py and `FrameACLCompiler`.
