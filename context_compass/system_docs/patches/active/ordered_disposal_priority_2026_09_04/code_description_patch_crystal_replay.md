# Code-description patch: ordered replay and live binding joins

## Trigger
Binding order affects content identity; replay has dependent member and selection joins.

## Control flow
1. SpellCrystal copies the established ordered name values into its detached record without sorting.
2. Restore reloads book policy, binds active custody with recorded names, and maps any changed SHA.
3. Restore resolves the translated anchor, forwards staged names, and maps the staged result if changed.
4. Selection resolves the translated exact owned member, not the index's current active projection.
5. Contract detail replay uses the same existing report translation before its public grant verb.
6. Fresh graft uses the index returned from its anchor bind when parking recorded siblings.
7. Merge forwards every member's names and remembers the selected member's returned live SHA;
   adoption resolves that exact member only when it actually grafted.

## Edge / error behavior
Absent name metadata contributes no explicit names; normal book policy still applies.
Same-policy new records preserve final order and SHA. A changed receiving policy may change SHA;
never force the old value onto a newly bound Spell. Missing targets retain existing shortfall behavior.

## Invariants and idempotency
All replay binds use the same composition owner. No matching at disposal, global alias map, cache
fallback, or owned-list snapshot is introduced. Detached crystal values remain a real serialization
boundary. Graft stays per-verb admitted; restore retains existing sequential/parallel and rollback laws.

## Non-goals
No source hydration redesign, unique-existence copy-policy change, or recovery of lost historical order.

## Validation focus
Distinct active/staged lists, both book placements, reordered receiving book, fresh and merge graft,
adoption disabled/missing, changed-ID restore anchors/selections/grants, and real cleanup calls.
