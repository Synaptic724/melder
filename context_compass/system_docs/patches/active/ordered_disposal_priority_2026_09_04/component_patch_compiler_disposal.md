# Component patch: Compiler disposal-list propagation

## Purpose and boundary
The compiler turns bound Spell metadata into records, plans, and executable namespaces.
This delta changes disposal-list ownership only; matching remains at Bind.

## Before / after
- Before: processor, generalized builders, many-only arrays, and solo normalization copy names.
- After: these boundaries retain the established Spell list directly.
- Generalized and many-only namespace builders already retain inner list references; keep them.

## Interface deltas
SpellRuntimeRecord.disposal_method_names becomes list[str]. ManyOnlyNoOverridesPlan accepts
an outer list of list[str] and exposes an outer tuple containing those same inner references.
Solo normalization retains a supplied nonempty list and preserves its empty-to-None result.
No public Meld signature, emitted calling convention, or existence routing changes.

## State and lifecycle
Model and plan cleanup MUST release their outer maps/arrays without clearing borrowed names.
Single and dual generalized builders MUST retain the same list as the fitted runtime record.
No new setter, mutation callback, cache, lock, reflection probe, or policy lookup is added.

## Failure modes
Existing presence/register flags, no-disposal fast paths, and construction errors stay intact.
Do not introduce fallbacks for arbitrary private mutation or obsolete collection types.

## Dependency and ordering
The verified producer result precedes this change. Only six source files require edits:
runtime record, runtime processor, generalized plan, many-only plan, and both solo compilers.
Hash/schema helpers remain unchanged: they intentionally emit ordered plain-value tuples.
Executor hydration continues resolving Spells from the current bound lookup.

## Validation expectations
Prove reference retention and exact order in record/plan/registration outputs, for empty and
nonempty lists. Exercise generalized single/dual, standalone many-only, both solo variants,
and cached executor hydration. Run existing family/cache tests and later actual Creations tests.

## Unknowns and open decisions
None in this six-file correction. Full durable replay and Creations ownership have separate tasks.
