# Component Patch: Non-resolvable construction admission

<!-- BEGIN ENTRY: Spellbook plan and cache eligibility -->
## Boundary
SpellbookCreationSystem already decides which registered Spells need executable payloads and which
enter the plan group. Add native resolvable policy to these existing decisions.

## Before and After
Before, all non-existing spells need cache payloads and any such spell with a Phase-5 blueprint is
eligible for phases 8-11. After, False definitions require neither a cached executor nor plan work.
Structural declaration/profile capture remains available; no registry entry is removed.

## Interfaces and State
No public API or new state. Consume Spell.resolvable directly. Preserve scheduler ownership,
transaction boundaries, existing-instance behavior, cache miss/version semantics and post-conjure flow.
Direct compiler phase entry points must agree with the scheduler on False plan eligibility.

## Failures and Validation
False-only and mixed books can complete structural/conjure work without construction requirements
for definitions. Existing ordinary validation errors still propagate. Test pre/post-conjure paths,
target-local compilation, and independent cache eligibility; do not claim runtime meld enforcement.
<!-- END ENTRY: Spellbook plan and cache eligibility -->
