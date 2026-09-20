# Component Patch: SpellbookCreationSystem local phase registration

<!-- BEGIN ENTRY: Deferred local cancellation argument -->
## Purpose and Before/After
The creation system registers local compiler phases on a borrowed persistent scheduler. Currently
its registration callback captures the previous cancel_event in the positional args. After this
repair the single-phase helper optionally injects cancel_event when its factory creates the unit.

## Interfaces, State and Failures
Add an internal default-False pass_cancel_event option; enable it for local root-blueprint and
system-validation phases. Keep the other local calls and their arguments unchanged. No new state
or cleanup ownership. Previous cancellation no longer raises in a fresh run; current cancellation
continues through existing scheduler errors without suppression.

## Ordering and Validation
Register phase closure -> scheduler creates run signal -> factory reads current event -> worker
calls compiler. Prove failed-run recovery with a real Spellbook and prove cancellation stops a
running phase body. Existing churn/creation-system/scheduler tests must pass. No open decisions.
<!-- END ENTRY: Deferred local cancellation argument -->
