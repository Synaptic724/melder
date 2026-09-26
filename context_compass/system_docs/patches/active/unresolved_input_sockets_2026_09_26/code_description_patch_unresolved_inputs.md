# code_description_patch_unresolved_inputs

## Metadata
- Patch ID: unresolved_input_sockets_2026_09_26
- Status: draft for owner review

## Control Flow

```text
conjure / late bind
  Phase 1  work_callable: Package  -> SINGLE_BY_ANNOTATION (unchanged)
  Phase 3  candidates(Package)
             one resolvable        -> NORMAL edge (unchanged)
             none resolvable, one non-resolvable definition -> OVERRIDE_REQUIRED (unchanged)
             two or more           -> RuntimeError (unchanged)
             none at all           -> UNRESOLVED_INPUT socket (new), dependency_key kept
  Phase 4  warning UNRESOLVED_INPUT; conjure logs one INFO line listing them
  Phase 9  source "unresolved_input" (no edge, override_key = name)
meld
  override supplies the name (root key, path key or broadcast) -> constructor receives it by identity
  override does not supply it -> constructor call raises at argument binding
     -> failure path: UnresolvedInputError.from_failed_construction(...) -> raise it from exc
later bind of a provider with the same frame key
  -> consumer marked dependency-changed -> next meld re-runs structural phases -> NORMAL edge
```

## Edge and Error Semantics
- `Optional[T]` without a default is an unresolved input; supplying None satisfies it (presence).
- Positional supply: a socket whose position is below the supplied positional count counts as supplied.
- A stored (reused) consumer never runs its constructor, so it never raises this error.
- A constructor TypeError unrelated to argument binding, with every unresolved input supplied, keeps the
  existing error path and message.
- Kernel-guarded types (Package, Conduit) can never be bound, so their parameters stay unresolved until
  supplied; the guard is unchanged.
- The conjure INFO line is emitted once per conjure listing consumer.parameter -> expected type.

## Invariants / Idempotency
- Phase 3 is deterministic for a given registry; re-running it after a bind is the only way a socket
  changes kind. No runtime path mutates socket kinds.

## Explicit Non-Goals
- No type check of supplied values. No change to hooks or their order. No new configuration key.
- No change to targeting: selectors already address these parameters through the socket overlay.
