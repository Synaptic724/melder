# Qualified spell-name collisions: architecture patch

## Scope and non-goals
Patch id: qualified_spell_name_collisions_2026_09_28. Correct Phase-4 validation to use the
canonical normalized address. Bare-class identity checking and new lookup precedence are out of scope.

## Changed-components matrix
| Component | Change | Owner |
| --- | --- | --- |
| Spell Validation Strategies | Compare normalized addresses, preserve diagnostic code | workflows_0 |

## Interface and boundary deltas
Same-named registrations at distinct addresses MUST pass this strategy. Keep its registration name,
DUPLICATE_SPELL_NAME code, error severity and collision details, adding the normalized lookup key.
Runtime lookup, binding admission, capability and constructors retain their existing contracts.

## Cross-component invariants
Validation MUST use SpellInputUtils.make_spell_key_from_parts exactly as address registration does.
All visible active registrations participate regardless of resolvable; distinct display names MUST
NOT hide an equal normalized address. Existing frame-wide and contracted-key admission stays intact.
One copied pool per validation pass preserves the existing concurrent-writer protection.

## Migration and rollout order
Add tests and demonstrate failures; implement the validator; qualify affected tests; promote docs and
graph; read/notch the live version; add the release entry; turn in; rebuild and check assets last.

## Rollback strategy
Revert only this change's validator/tests/docs if required, preserving concurrent work. The existing
release-stamped cache admission will rebuild when the source version changes; no record migration.

## Validation expectations and evidence plan
Unit checks cover normalized-key equality, defaults, case, different names, pass caching and genuine
collisions. Public checks cover both qualifier forms, discoverable twins, contract sharing and exact
returned types. Record red/green logs under artifacts/qualified_spell_name_collisions_20260928/.

## Ticket coverage map
TASK-2026-09-28-investigate-qualified-spell-name-collisions owns tests, implementation and promotion.

## Unknowns and decision requests
None blocking the address fix. Bare-class identity remains a separately verified lookup issue.
