# Component patch: Spellbook Configuration and System State

## Component purpose and boundary
SpellbookConfiguration owns rich book policy and its existing property/fluent/freeze APIs.
This patch changes only that owner; it adds no policy state to consumers or frame roots.

## Before / after behavior
- Before: five schema properties; no disposal-priority setting; raw configurations start empty.
- After: the new bool exists as False at initialization and after clearing properties.
- Existing name-list storage, name matching, and invocation are unchanged here.
- Explicit priority values remain writable during configuration assembly and sealed at freeze.

## Interface deltas
- `get_property("enforce_priority_disposal_methods")` returns the stored bool by default.
- The fluent setter delegates to `set_property` and returns the same configuration instance.
- Preserve current type-validation timing: generic validation/freeze rejects non-bool values.
- False means spell-first group priority, not suppression of the book's method names.

## State and lifecycle deltas
- Seed only the new flag early, not every ordinary default.
- Include False in the normal and optional-default tables.
- Do not put this early default in `_idempotent_keys`; that would block opting in.
- `clear_properties()` restores this early default while clearing other configured values.
- Keep normal cleanup and freeze guards, including the existing owned-map teardown.

## Failure mode deltas
No new exception family. Unknown keys and frozen/cleaned mutation follow existing behavior;
invalid flag values fail during the ordinary validation boundary.

## Dependency and ordering constraints
- Raw supplied configurations must work before Bind, not only after validation.
- Reload preserves recorded True/False and the existing populate-missing behavior.
- An omitted flag still holding False counts as a schema-default backfill even when seeded at init.
- A preconfigured non-default True remains preserved under the existing reload behavior.
- No extra provenance registry, private-mutation protocol, or per-consumer fallback is introduced.

## Validation expectations
- Unit tests cover raw/defaults/clear/defaults-free construction, both explicit values,
  wrong types, fluent identity, default preservation, and frozen/cleaned refusal.
- Component tests exercise the real configuration fluent/freeze boundary.
- Reload tests cover absent and recorded values, correct diagnostics, and sealed returns.
- Existing name-list assertions remain ordered; only partial-key expectations gain the new key.

## Unknowns and open decisions
None for this slice. Binding composition and full crystal replay remain explicitly unimplemented.
