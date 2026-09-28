# Component patch: Creations and SpellSpace - disposal failure collection (2026-09-27)

## Before
- `_attempt_cleanup` returned at the first failing method; the object's later declared methods never ran.
- The returned `RuntimeError` carried only `str(ex)`; the original exception, its type and traceback were dropped.
- The error text formatted the object with `str()` inside the except block; a raising `__str__` escaped the helper.
  cleanup() then recorded that one error and skipped every remaining object; clear_all() and purge() propagated it.

## After
- `_attempt_cleanup(entry) -> List[Exception]` runs every declared method in order and returns one `RuntimeError` per
  failing method ("Failed to dispose object <text> using method '<name>': <text>"), each with `__cause__` set to
  the raised exception.
- Object and exception text come from a helper that falls back to "<Type object at 0x...; str() raised Error>"
  when `str()` raises, so reporting cannot abort disposal.
- `_dispose_many_creations`, `_dispose_disposable_registry` and `purge` extend their error lists with every entry's
  errors; `_refuse_publish_into_cleaned_store` chains from the single error or from an ExceptionGroup of several.

## Interface deltas
- Private helper return type only; public raises keep their types (ExceptionGroup; RuntimeError for refusal).

## State and failure deltas
- More errors can appear in one group (one per failing method); none disappear.
- No state is added; registries are detached and released exactly as before.

## Dependency and ordering
- Conduit and SpellSpace teardown receive the group as before; Conduit logs it with exc_info, which now shows each
  original exception as the direct cause.

## Validation expectations
- Tests listed in the architecture patch fail on 0.2.79 and pass after; the creations, conduit, SpellSpace and
  crystallizer suites stay green on 3.14t and GIL.
