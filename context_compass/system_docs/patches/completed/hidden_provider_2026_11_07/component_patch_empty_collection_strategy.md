# component_patch_empty_collection_strategy

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Component: System Validation (Phase 6) - `EmptyCollectionStrategy`
- Status: draft
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Component Purpose and Boundary
- Current boundary: one `collection_socket_no_providers` diagnostic per required collection socket with no target,
  ERROR when the Book is not dynamic, WARNING (and `[]` injected) when it is.
- Target boundary: unchanged in kind, severity and policy (D3); the text names the bindings when the socket carries
  `hidden_spell_ids` (recorded by Phase 3 for an empty required `list[Class]` only).

## Before/After Behavior Summary
- Before (measured 0.2.8280, English only under Greeter):
  ERROR: "Spell 'ListClass' parameter 'greeters' is a required list[...] dependency, but no provider is wired into
  it. Bind at least one implementation under its frame, make the parameter optional, or run the book in dynamic mode
  if members arrive via contracts."
  WARNING: "Spell 'ListClass' parameter 'greeters' is a required list[...] dependency, but no provider is wired into
  it. An empty list will be injected at construction; bind implementations under its frame or add them via a
  post-conjure contract to populate it."
  EVIDENCE: src/melder/aether/spellbook/spell_compiler/system/validation/empty_collection_strategy.py:162-191.
- After, when `socket.hidden_spell_ids` is non-empty (candidates rendered through `spell_lookup`, falling back to the
  id; `T` = the first candidate's spell_name; list lookups: Protocol P -> `list[P]`, category c -> `list['c']`, bare
  under a name -> `list['T']`, which gathers the bare spells named T under any binding name):
  ERROR (Book not dynamic): "Spell 'Host' parameter 'greeters' is a required list[...] dependency, but no provider is
  wired into it: list[English] gathers English only where it is bound bare (no spellframe, the default binding), and
  English is bound only under a spellframe: English at (spellframe='Greeter', binding_name='english') - use
  list[Greeter]. Gather it where it is bound, as shown, bind English bare, or make the parameter optional."
  WARNING (dynamic): "Spell 'Host' parameter 'greeters' is a required list[...] dependency, but no provider is wired
  into it: list[English] gathers English only where it is bound bare (no spellframe, the default binding), and
  English is bound only under a spellframe: English at (spellframe='Greeter', binding_name='english') - use
  list[Greeter]. An empty list will be injected at construction; gather it where it is bound, as shown, or bind
  English bare to populate it."
  Without hidden ids both texts are byte-identical to today.

## Interface Deltas
- Inputs: `SpellSocketDescriptor.hidden_spell_ids`; `spell_lookup` (already passed).
- Outputs: the texts above; `details` gains "hidden_candidates" (the rendered candidate dicts of
  `HiddenProviderReport`), "spell_id" and "param_name" unchanged.
- Error semantics: unchanged (code, severity, the conjure refusal in a Book that is not dynamic, `[]` in a dynamic one).

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: the misleading remedy "Bind at least one implementation under its frame" for a class bound
  only under a frame or a name.
- Changed failure mode: text only.

## Dependency and Ordering Constraints
1. Reads what Phase 3 records; lands with component_patch_compiler_phase_3.md and the renderer
   (component_patch_phase4_validation_strategies.md).

## Validation Expectations
- Added: a unit test of `EmptyCollectionStrategy` with a stub topology carrying hidden ids - both severities, the exact
  texts, details, an unknown id; a socket without ids keeps today's texts byte for byte.
- Added (integration, in the probe-matrix file): automatic `list[English]` with English under Greeter refuses with
  the ERROR text; dynamic injects `[]` and `validate_resolution().list_diagnostics()` holds the WARNING text.
- No existing test pins the old remedy text (grep 2026-11-07).
- Evidence target 1: the full suite, the GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (D3: dynamic stays WARNING + `[]`).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: none beyond text.
- Next entrypoint: `EmptyCollectionStrategy.run`, the diagnostic block.
