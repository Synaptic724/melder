# Architecture patch: readable conjure validation reports (2026-09-26)

Ticket: tickets/tasks/completed/2026-09-26_review_conjure_validation_error_reporting_task.md (owner approved all three steps).

## Objective
When conjure (or a meld-time revalidation) refuses spells, the SpellbookValidationError message says which spells
failed, why, and how to fix it - by name, in plain words - and never says "broken" without a reason.

## Non-goals
- No change to what is valid: no strategy starts or stops producing an error, except the two misfires below.
- No change to exception types, `broken_spells`, issue/diagnostic codes, severities or `details` payloads.
- No change to `conjure(validation_warnings=True)` logging beyond the wording of the messages it prints.

## Changed components
- SpellbookValidationError (utilities/custom_exceptions): new renderer; optional keyword `system_diagnostics`.
- SpellbookCreationSystem: the conjure gate and the local-rerun gate pass the conduit resolution diagnostics.
- Phase-4 strategies: CircularDependency, DanglingDependencies, SelfDependency, ContractProviderPresence,
  ParameterPolicy, AnnotationShapeGuard, RequiredHoles (message text; two misfires fixed).
- Phase-6 producers: ScopeOrdering, CycleDetection, VisibilityGap, EmptyCollection, BrokenSpellInDag strategies,
  CompilerPhase6's two local visibility guards, SpellbookCreationSystem.record_local_resolution_visibility_failure.
- SpellInputUtils (utilities/helpers): `describe_spell_id` display helper.

## Invariants
- A refused spell's message carries at least one reason when any is recorded (Phase 4, Phase 6 on the spell, or the
  conduit diagnostics handed in); otherwise it says plainly that none was recorded.
- Errors only in the body; warnings are counted, never listed (they never block conjure).
- Names, not ids: a spell id appears only when no name is available (short 12-character form).
- Melder bookkeeping codes are shown as internal errors to report, code kept.
- Rendering never raises (existing contract).

## Misfires fixed (behaviour)
- ParameterPolicyStrategy treated `*args: Any` / `**kwargs: Any` as DI and broke the spell (VARIADIC_DI_UNSUPPORTED);
  `typing.Any` is not a DI target, matching Phase 1 and the guard.
- LIST_ELEMENT_NOT_DI_TARGET and the REQUIRED_HOLE list-only hint fire only when a user class sits inside the
  annotation (someone may have expected injection); plain data such as list[str] or dict[str, Any] gets neither.

## Interface deltas (additive)
- `SpellbookValidationError(broken_spells, *, system_diagnostics=None)`.
- `SpellInputUtils.describe_spell_id(spell_id, spells) -> str`.

## Migration order
Helper -> strategies and producers -> exception renderer -> gates -> tests -> docs, graph, release note.

## Rollback
Inverse hunks only (shared worktree); no data, cache or persisted format involved.

## Coverage matrix
| change | validation |
| --- | --- |
| renderer | rewritten unit tests for the exception (errors-only, counts, internal, dedupe, resilience) |
| gates pass diagnostics | component test: scope-ordering conjure names both spells and the fix |
| strategy messages | strategy unit tests on names and the cycle path |
| misfires | unit tests: `*args: Any` not flagged; list[str]/dict[str, Any] no notice; dict[str, UserClass] hint |
| probes | before/after renders for owner/cycle/scope shapes |
