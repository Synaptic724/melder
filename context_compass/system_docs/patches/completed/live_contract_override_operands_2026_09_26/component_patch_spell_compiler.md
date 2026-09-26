# component_patch_spell_compiler

## Metadata
- Patch ID: live_contract_override_operands_2026_09_26
- Component: DI Descriptors and Contract Sockets; SpellCompiler and Validation Pipeline (phase 3,
  phase 9, planner data, phase-11 rows); Codegen creation system (no-overrides hydration); creation
  cache emission seam
- Status: implemented (owner-run suites pending)
- Owner: fable_0 (cowork)
- Created: 2026-09-26T11:57:20Z
- Updated: 2026-09-26T12:42:22Z

## Component Purpose and Boundary
- Descriptors: `SpellContract` (late-bound cross-conduit socket) and `SpellMap` (in-graph DI socket) each
  carry an optional construction payload for the provider (`dict` = kwargs, `list`/`tuple` = positional).
- Phase 9 (`spell_occurrence_contract_processor_strategy.py`) reads the consumer's live descriptors and
  records the normalized payload against the PROVIDER's child occurrence; the injection processor turns
  the payload keys into `kind="contract"` operands of the provider's instance spec.
- Phase 11 row builders project plan steps into schema rows; the families hydrate executors from rows.

## Before/After Behavior Summary
- Before (descriptor): keyword and slot `spell_override`; the docstring says values are "carried forward".
- After (descriptor): keyword and slot `override`; the docstring states the values are read live from the
  descriptor at meld and reach the provider by identity; no alias.
- Before (phase 9): only `SpellContract` defaults are compiled; `SpellMap.spell_override` is read once, by
  phase 3, to refuse it on a non-resolvable definition (`compiler_phase_3.py:900-912`), and never applied.
- After (phase 9): every payload entry also yields a REF `("__contract_override__", consumer_spell_id,
  param_name, key_or_index)`; `SpellMap` defaults carrying a payload are recorded against the phase-3
  dependency occurrence of that parameter with the same refs (P7).
- Before (rows): `contract_payload_items` = sorted `(param, freeze(value))`; `contract_positional_override`
  = `freeze(tuple)`; a dict, list, enum, callable or object value is mangled (sorted pairs, tuple, repr
  text, marker tuple) and executed in that form by every manifest-first lane and after a cache hit.
- After (rows): a non-scalar value is emitted as its REF; scalars unchanged (written as themselves, which
  is what every freeze returned for them); the generalized row and signature builders, the many_only
  helpers' two row builders and the many_only manifest row builder all call
  `CodegenSignature.project_contract_payload_entry`.
- Before (hydration): `_row_contract_value_binding`, `_hydrate_steps_from_rows` (generalized :309,
  many_only :425) copy row values verbatim into bindings / step adapters.
- After (hydration): the three sites resolve refs to live values through the consumer's descriptor (one
  FORWARDREF signature read per (consumer, parameter), memoized per hydration): the generalized manifest
  compiler resolves the ROWS once at its two entry points (`resolve_contract_payload_rows`), so runtime
  rows, bindings and the generic constructor path agree; the two legacy `_hydrate_steps_from_rows`
  resolve per row and give the adapter `contract_payload_refs` rebuilt from the raw row. The override
  lanes' copies are untouched and keep today's behaviour until v2 S3.
- Before (emission): both package builders return `None` for a non-replayable plan; `_emit_spell_cache`
  skips such spells (task 4).
- After (emission): the gate is removed; rows are replayable by construction.

## Interface Deltas
- Inputs: descriptor keyword renamed; row fields unchanged in name and shape.
- Outputs: refs in rows for non-scalar values; `build_package` never returns `None`.
- Error semantics: a ref whose consumer is not in the hydration lookup, or whose parameter carries no
  descriptor, raises `RuntimeError` naming the consumer spell id and parameter at hydration (a plan/row
  contract violation, not a user error); user payload shape errors are unchanged (`MeldExecutionError`).

## State and Lifecycle Deltas
- Owned state changes: `SpellOccurrenceContractAnalysis.contract_override_refs_by_occurrence` (cleaned
  with the analysis); `SpellInjectionInstanceSpec.contract_payload_refs`; planner steps'
  `contract_payload_refs`; no new runtime-owned state (the descriptor cache is a hydration local).
- Lifecycle/cleanup changes: none beyond the new slots' cleanup.

## Failure Mode Deltas
- New failure mode: hydration `RuntimeError` for a dangling ref (see above).
- Removed failure mode: silent payload mangling on the no-overrides lanes; the cross-process cache miss
  for object-payload books (they now package).
- Changed failure mode: none on the override lanes (documented limitation until v2 S3).

## Dependency and Ordering Constraints
1. Rename before refs (readers named in the rename touch the same lines).
2. Refs in the analysis/spec/steps before the row builders emit them.
3. Row builders before the hydration sites (a hydration site must never see a ref it cannot resolve).
4. Gate removal last, after the row builders guarantee scalar-or-ref rows.

## Validation Expectations
- Test/validation item 1: unit tests as listed in the architecture patch.
- Test/validation item 2: component identity tests (in-process; cross-process cache hit).
- Evidence target: owner-run suites; "Not run." until reported.

## Unknowns and Open Decisions
- UNKNOWN: whether any existing test asserts the old frozen-value row bytes for an object payload
  (expected: only task 4's tests, which are replaced).

## Context / Handoff Summary
- What changed (2026-09-26T12:42:22Z): implemented as described above; tests written; "Not run.".
- Next entrypoint: owner-run suites; promotion at story closure.
