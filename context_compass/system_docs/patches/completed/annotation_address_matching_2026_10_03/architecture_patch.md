# Architecture patch: Phase 3 resolves annotations by address key

- Patch id: annotation_address_matching_2026_10_03
- Status: active (entry gate for TASK-2026-10-03-resolve-annotations-by-address-key)
- Owner: fable_0
- Created: 2026-10-03T19:25:31Z

<!-- BEGIN ENTRY: "Annotation address matching: objective, non-goals, invariants" -->
## Objective
Phase 3 matches a DI annotation to candidate spells by key, the way the rest of the system addresses spells:
`normalize_frame_key(annotation)` (after the existing Optional/Union/ForwardRef normalization) against each
spell's address frame key (spellframe, else its own name) and its type key (`spell_name`; an instance's class
name). A spellframe is a category or a shape label, never a type: the matcher no longer compares objects by
identity, so a concrete class used as a frame is just a name, an existing object is matched by its class, and
a `TYPE_CHECKING`-only annotation (a string at runtime) resolves exactly as a runtime class object does.

## Non-goals
- The Autofac-strict rule (a framed spell reachable only by its frame): a breaking change, decided separately.
- `_resolve_spellmap_default` (explicit addressing); the structural snapshot's replayability rule.

## Invariants
- Nothing that resolves today stops resolving: the string path already matched by name; the object path's
  identity matches are a subset of name matches (a class is its own name; a frame object is its name).
- Ambiguity still raises in Phase 3 (two candidates for one single socket); Phase 4 still refuses two spells
  at one address. A same-name class at a different frame or binding name is a different key, as before.
- The pass-scoped candidate index is exact for every pool: keys are strings, so the eq-risky gate and the
  scan fallback for custom `__eq__` pools are unnecessary and removed.

## Interface deltas
- Public API: none. Behaviour: a bare existing object satisfies a consumer annotated with its class.
- Private: `CompilerPhase3._matches_annotation` keeps its signature; the index dict holds `by_key` only.

## Migration order
1. Matcher and index rewrite; unit tests re-pinned (identity cases become key cases) and extended.
2. Harness and S8 component test bind existing objects bare.
3. Structural-snapshot generation 18 (`annotation_address_matching`): a bundle captured under the identity
   matcher may hold unresolved rows that the key matcher resolves.
4. Docs (component, architecture invariant, README DI paragraph), release note, notch, assets last.

## Rollback
Restore the identity branches; keep the generation bumped.

## Ticket coverage matrix
| patch section | ticket | validation |
| --- | --- | --- |
| matcher + index | TASK-2026-10-03-resolve-annotations-by-address-key | phase-3 unit tests, component conjure |
| harness bindings | same | harness runs |
| generation 18 | same | cache-history pin |
<!-- END ENTRY: "Annotation address matching: objective, non-goals, invariants" -->
