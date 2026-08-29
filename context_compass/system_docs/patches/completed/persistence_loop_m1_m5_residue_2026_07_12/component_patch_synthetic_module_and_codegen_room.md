# Component Patch: SyntheticModule + CodegenCommandSystem
# (persistence_loop_m1_m5_residue_2026_07_12)

## SyntheticModule Loader Machine (M1)

### Before
- `__init__` sets `self.__file__ = "<synthetic:{name}>"` (:277) - trips
  linecache's angle-bracket guard, so inspect.getsource/pdb/traceback source
  display fail with OSError on every synthetic class.
- `_SyntheticModuleImportLoader` implements only create_module/exec_module -
  no `get_source`, so even a stat-miss cannot fall back to retained source.
- unpublish/cleanup/execute_source leave stale linecache entries behind.

### After
- `__file__ = "synthetic://{name}.py"` - non-`<>`, never stat-resolvable.
- Loader gains `get_source(fullname)`: registry lookup under `_registry_lock`,
  returns the live `source_text`; ImportError names unregistered modules.
- `import linecache` at module head; `linecache.cache.pop(self.__file__, None)`
  in `unpublish_from_sys_modules`, in `cleanup`, and in `execute_source`
  (re-exec must not serve v1 lines for v2 source).
- Package `__path__` keeps carrying `__file__` (form change only).

### State / Failure Deltas
- No new owned state; one new read-only loader method.
- Failure surface: `get_source` raises ImportError for unknown names (importlib
  InspectLoader contract); nothing else changes.

### Dependency / Ordering
- None; the loader remains registry-driven and lock-disciplined.

## CodegenCommandSystem (M5)

### Before
- The room can validate, execute (throwaway namespace), preview, and
  synthesize - but has NO promotion lane; executed definitions evaporate.

### After
- `materialize_codegen(code, *, module_name, frame_name)`:
  1) input contract: non-empty strings; `module_name` must be dotted-identifier
     legal (each segment `isidentifier()`).
  2) standard verb envelope: action-hook scope, rift-gate ticket, room lock,
     one memory record on completion (validation-result form).
  3) validation-gated: delegates to the attached engine's
     `validate_codegen_request`; a rejected result returns the reporter payload
     marked `materialized: False` - nothing is registered/published.
  4) accepted: builds one SyntheticModule (sentinel pre-bind identity, sha256
     of the source) and runs `materialize(install_import_hook=True)` -
     register -> parent shells -> publish -> exec -> importlib metadata.
  5) R8: exec failure -> best-effort `module.cleanup()` (full teardown), then
     re-raise; no half-published module survives.
  6) payload: `materialized: True`, module_name, source_sha256, `__file__`,
     export names (public non-dunder namespace names), validation payload.
- `_CODEGEN_COMMAND_METHOD_NAMES` gains "materialize_codegen" (advertised).
- SyntheticModule import is method-local (aether `_get_mutation_research`
  precedent) to keep the nexus module import chain flat.

### State / Failure Deltas
- No new owned state on the command system.
- New failure modes: ValueError (empty/illegal inputs), the engine's own
  validation refusal payload, re-raised exec errors after teardown.

### Dependency / Ordering
- Verb depends only on the already-attached CodegenSystem + SyntheticModule.
- No transaction-plane interaction: materialization is a world-object act, not
  a structural mutation; bind (the structural act) stays on Spellbook where the
  admission plane already governs it.

## Validation Expectations
- Unit (introspection): materialize -> inspect.getsource returns source;
  traceback filename is the synthetic:// form; unpublish clears the linecache
  entry; re-exec serves updated source.
- Unit (verb): mocked engine - accepted path materializes + advertises payload
  keys; rejected path refuses without registry mutation; exec-failure path
  tears down; empty/illegal inputs raise ValueError.
- Agent reports "Not run." for anything not executed; owner runs the 3.14t tree.
