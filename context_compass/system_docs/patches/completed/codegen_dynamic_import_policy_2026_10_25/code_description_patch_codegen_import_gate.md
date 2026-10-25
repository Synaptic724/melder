# Code-description patch: static import-name denial and the runtime import wrapper

## Metadata
- Patch ID: codegen_dynamic_import_policy_2026_10_25
- Components: FrameACLCompiler._compile_codegen_static_import_name_control,
  CodegenBuiltinPolicyStrategy.validate, CodegenNameResolutionStrategy._collect_allowed_builtin_names,
  CodegenBuiltinsStrategy.build_namespace_entries
- Status: active
- Owner: Mark; melder_0 (synaptic_python_developer) (patch)
- Created: 2026-10-25T09:57:57Z
- Updated: 2026-10-25T09:57:57Z

## Trigger justification
New/changed policy-gate pipeline: the `__import__` name gains a static-only denial path that two gates read, and
the runtime `__builtins__['__import__']` becomes a wrapper with its own control flow and error semantics. Both
run in the room's own process as policy and defence in depth, not isolation (review C6.1; wording rule C6.4).

## Control flow

`FrameACLCompiler`: a new static helper
`_compile_codegen_static_import_name_control(imports_enabled, allowed_import_module_roots,
denied_import_module_roots) -> Set[str]`:
1. Return `set(IMPORT_BUILTIN_NAMES)` (that is, `{"__import__"}`) when `imports_enabled` is True AND at least
   one of the allowed or denied import-root sets is non-empty.
2. Otherwise return `set()`. (Imports off -> `__import__` is already added to `denied_builtin_names` by
   `_compile_codegen_builtin_controls`; full_access -> imports on with no list, so `__import__` stays usable.)
The compiled surface stores it sorted as `static_only_denied_builtin_names`; it is NOT merged into
`denied_builtin_names` and is NEVER removed from the runtime builtins.

`CodegenBuiltinPolicyStrategy.validate` (A, call form): compute
`denied = set(config.denied_builtin_names) | set(config.static_only_denied_builtin_names)`, then, for each
`ast.Call` whose `func` is an `ast.Name` whose id is in `denied`, reject with
"Builtin '<id>' is not allowed in this codegen mode." A `__import__('x')` call is an `ast.Call` with func Name
`__import__`, so it is refused under a listed posture. Ordering unchanged: the import gate runs before this gate,
so an import statement of a denied root is still refused there first.

`CodegenNameResolutionStrategy._collect_allowed_builtin_names` (A, reference form): subtract the same union from
`vars(builtins)`, so `__import__` is not an available name under a listed posture and a bare `f = __import__`
Load is refused with "Name '<id>' is not available in the codegen namespace." Because the builtin gate runs first,
a `__import__(...)` call reports the builtin-gate message; a non-call reference reports this one.

`CodegenBuiltinsStrategy.build_namespace_entries` (B, runtime):
1. `builtins_dict = dict(vars(builtins))`; pop each name in `config.denied_builtin_names` (unchanged). The
   static-only names are NOT popped, so `__import__` stays present.
2. When `config.imports_enabled` is True AND (`config.allowed_import_module_roots` or
   `config.denied_import_module_roots` is non-empty), replace `builtins_dict["__import__"]` with a guarded
   wrapper built by a private helper that closes over the real `builtins.__import__` and the two root tuples.
   full_access (imports on, no list) and safe (imports off) install no wrapper.
3. Return `{"__builtins__": builtins_dict}`.

The guarded wrapper `_build_guarded_import(real_import, allowed_import_module_roots,
denied_import_module_roots)` returns a function with the `__import__` call shape
`(name, module_globals=None, module_locals=None, fromlist=(), level=0)`:
1. `root = name.split(".")[0] if name else name`.
2. Denied when `root in denied_import_module_roots` OR (`allowed_import_module_roots` non-empty AND
   `root not in allowed_import_module_roots`) - the same rule as
   `CodegenImportPolicyStrategy._import_root_is_denied`.
3. Denied -> raise `ImportError("Import root '<root>' is not allowed in this codegen mode.")`.
4. Allowed -> `return real_import(name, module_globals, module_locals, fromlist, level)`, so an import statement
   of an allowed root loads normally (the IMPORT_NAME opcode calls `__builtins__['__import__']` positionally).

## Edge and error semantics
- The two static messages are the existing gate texts; B's text is a new ImportError naming the root.
- A relative import (level != 0) is already refused at validation by the import gate; if the wrapper is ever
  reached with an empty name its root is "" which no allow list contains, so it is refused - consistent, not a new
  path exercised in practice.
- full_access reaches neither A (no static-only name) nor B (no wrapper), so `__import__('melder')` is accepted
  and loads, by design.

## Invariants and idempotency
- `static_only_denied_builtin_names` is read-only on both carriers and compiled per projection; nothing mutates
  it at run time.
- The wrapper is pure per call (no captured mutable state beyond the real import and two immutable tuples) and is
  rebuilt per namespace build, so two builds never share one wrapper object.
- No lock or lock-order edge is added; the gates and the builtins strategy keep their existing instance locks.

## Explicit non-goals
- Not an OS or process boundary; the wrapper runs in the room's own process (defence in depth).
- Does not change the import gate's statement checks, the reflection gate's `importlib` coverage, or any
  allow/deny list's contents.
