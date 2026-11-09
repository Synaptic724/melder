# component_patch_unresolved_input_error

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Component: `UnresolvedInputError` (utilities/custom_exceptions; raised by the Meld Resolution Runtime)
- Status: draft
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Component Purpose and Boundary
- Current boundary: built by `for_unsupplied` before construction when an UNRESOLVED_INPUT parameter is not
  supplied; the text says "nothing registered provides it".
- Target boundary: unchanged in when it is raised and in its type, fields and attribution; its text names where the
  class is bound when spells of the expected class exist where a class lookup does not reach.

## Before/After Behavior Summary
- Before (measured 0.2.8280): "[MELD] Execution failed for spell 'SingleClass' (<id>) at node <id> (parameter
  'greeter'): SingleClass.greeter expects English, but nothing registered provides it and this meld did not supply
  it. Supply it with override={'greeter': ...} when melding SingleClass, a path key ending in '>greeter' (or
  '**greeter') when SingleClass is built as a dependency, or bind a provider for English."
  EVIDENCE: src/melder/utilities/custom_exceptions/unresolved_input_error.py:223-262 (text at :243-248).
- After: `_from_missing_sockets` computes, on its failure path only, the hidden candidates of the FIRST missing
  socket live: the constructor annotation already read by `_constructor_expected_type` is normalized and classified
  with Phase 3's static helpers (`_normalize_annotation_for_matching`, `_annotation_kind`, `_annotation_key`; a local
  import, no cycle) and matched over `spell._spellbook._spell_id_pool` with `CompilerPhase3._hidden_type_key`
  (single-socket rule: no method spells). With candidates (rendered by `HiddenProviderReport`, single-socket lookups):
  "Host.greeter expects English, but this meld did not supply it and a class lookup reaches English only where it is
  bound bare (no spellframe, the default binding), while English is bound only under a spellframe: English at
  (spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, binding_name='english'). Supply
  it with override={'greeter': ...} when melding Host, a path key ending in '>greeter' (or '**greeter') when Host is
  built as a dependency, ask for it where it is bound, as shown, or bind English bare."
  (prefixed by MeldExecutionError's "[MELD] Execution failed for spell 'Host' (<id>) at node <id> (parameter
  'greeter'): "; " Also not supplied: ..." unchanged). Without candidates (a Protocol annotation, a class bound
  nowhere, an unreadable signature) the text is byte-identical to today.
- Why live, not from the socket: a socket that recorded hidden ids refuses its spell in Phase 4, so it never reaches
  construction. The error still arises with candidates only where Phase 3 ran before they existed and nothing
  re-gated the consumer: a race between a meld and a framed bind's commit, or an arrival path that announces no type
  key (with D1 = B, bind, notch and contract grant all do).

## Interface Deltas
- Inputs: none new (the consumer spell and its sockets, as today).
- Outputs: the text above; optional new slot `hidden_spell_ids: Tuple[str, ...]` (empty when none) for tooling.
- Error semantics: unchanged type (`MeldExecutionError` subclass), `expected_type`, `unresolved_params`, `inner=None`.

## State and Lifecycle Deltas
- Owned state changes: the optional `hidden_spell_ids` slot.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: "nothing registered provides it" when the class is registered under a frame or a name.
- Changed failure mode: text only.

## Dependency and Ordering Constraints
1. Uses the Phase 3 predicate and the renderer; the computation never raises (an unreadable pool or signature leaves
   today's text).

## Validation Expectations
- Added: unit tests of `_from_missing_sockets` with a stub spell whose pool holds a framed English - the exact text;
  a bare-named English - "under a binding name"; none - today's text; a Protocol annotation - today's text.
- Added (integration): a dynamic world where the consumer compiled before English was bound under Greeter by a path
  that does not announce (or a white-box call of `for_unsupplied`) shows the naming text.
- No existing test pins "nothing registered provides it" (grep 2026-11-07).
- Evidence target 1: the full suite, the GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: whether any production arrival path leaves a consumer un-gated once D1 = B lands (the mode-2 run and the
  S1 matrix re-run will tell); the text is the safety net either way.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: none beyond text.
- Next entrypoint: `UnresolvedInputError._from_missing_sockets`.
