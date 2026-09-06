# Architecture Patch: Human Meld Identity API

<!-- BEGIN ENTRY: "Human meld identity boundary" -->
## Objective
Restore the canonical public resolution boundary: humans address spells by
SpellName strings, machines supply opaque SHA identities explicitly, and
per-call construction inputs use the concise public `override=` keyword.

## Non-Goals
- No change to constructor DI, SpellMap, collection DI, existence, or compiled execution.
- No change to SHA generation, SpellIndex membership, hot-door guards, or storage routing.

## Changed Components
- Public `Conduit.meld` facade.
- Public `SpellSpace.meld` facade.
- Public `CapabilityCommandSystem.meld` wrapper.
- Repository-owned public callers, README/UX examples, tests, and system documentation.

## Invariants
- Internal concrete Meld doors remain ID-oriented and receive IDs positionally.
- `spell_id=` takes the existing direct ID path with no name-resolution attempt.
- A positional string is always a human SpellName at the public facade.
- Concrete class/function and spellframe resolution remain supported.
- Supplying both `spell` and `spell_id` is a caller error.
- Public `override=` forwards unchanged to internal `spell_override=`.
- Dynamic gate admission, scope routing, override semantics, hooks, validation,
  and cleanup do not change.

## Interface Delta
Before:

```python
conduit.meld(spell, *, spell_name=None, spellframe=None, binding_name=None, spell_override=None)
```

After:

```python
conduit.meld(spell, *, spell_id=None, spellframe=None, binding_name=None, override=None)
```

The same override-keyword delta applies to `SpellSpace.meld` and
`CapabilityCommandSystem.meld`. Internal Meld signatures retain
`spell_override=`.

## Migration Order
1. Add focused facade regressions.
2. Change Conduit and SpellSpace dispatch/docstrings.
3. Migrate repository-owned callers from `spell_name=`, ID-in-`spell`, and
   public `spell_override=` forms.
4. Rewrite human README/UX examples to positional SpellNames.
5. Update authored system docs and regenerate indexes/assets.
6. Run focused, supported, example, and asset validation.

## Rollback
Revert the facade signatures, call-site migration, authored docs, and regenerated
assets as one atomic change. Do not retain mixed semantics.

## Coverage Matrix
| Contract | Implementation | Validation |
| --- | --- | --- |
| Positional string is SpellName | `Conduit.meld`, `SpellSpace.meld` | focused integration + experiment |
| Explicit ID bypasses name lookup | same facades | mock/delegation and real-ID regression |
| Conflicting inputs fail | same facades | unit/integration error assertion |
| Public override is concise | three public surfaces | delegation + override suites |
| Human docs execute | README and UX examples | example harness |
| Internal fast door unchanged | concrete Meld doors untouched | component fast-door suite |
<!-- END ENTRY: "Human meld identity boundary" -->
