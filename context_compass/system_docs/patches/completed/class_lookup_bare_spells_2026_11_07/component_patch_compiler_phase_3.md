# component_patch_compiler_phase_3

## Metadata
- Patch ID: class_lookup_bare_spells_2026_11_07
- Component: SpellCompiler Phase 3 (`CompilerPhase3`) and the SpellMap descriptor's docstring
- Status: completed (merged into src_architecture and src_components 2026-11-07; moved to patches/completed/)
- Owner: Mark (owner); written by melder_0 (synaptic_python_developer)
- Created: 2026-11-07T13:48:07Z
- Updated: 2026-11-07T13:48:07Z

## Component Purpose and Boundary
- Current boundary: `CompilerPhase3` resolves each constructor socket of a spell to provider spells - by annotation
  kind for SINGLE_BY_ANNOTATION and COLLECTION_BY_ANNOTATION (`_spell_keys_for`, `_matches_annotation`, the
  four-bucket candidate index) and by descriptor for SPELLMAP_DEFAULT (`_resolve_spellmap_default`).
- Target boundary: unchanged. Only which spells answer a class lookup changes.

## Before/After Behavior Summary
- Before (0.2.8277): the type row of the matching table compared a class annotation with every spell's type key
  whatever its spellframe or binding name, so `x: English` resolved an English bound under the Protocol `Greeter`
  or under a binding name, and `SpellMap(spell=English)` reached an English at any address.
  EVIDENCE: src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:349-386 (`_spell_keys_for`),
  :472-519 (`_build_candidate_index`), :844-856 (the explicit-spell branch).
- After: a spell answers a class lookup only when it is bound with no spellframe and the default binding
  (`_answers_class_lookup`). Kind TYPE: type key only for such a spell, single and collection alike. Kind NAME on a
  single socket: the type key only for such a spell, the contract keys for every spell, and - for a spell that is
  itself a Protocol definition - its definition key whatever its binding (amended 2026-11-07T14:20Z after the
  rewritten unit tests showed a string naming a Protocol had stopped finding the Protocol's own definition bound
  under a binding name or spellframe, while the Protocol object still found it: definition matching is unchanged by
  the owner's settled point 5, and a `TYPE_CHECKING` string resolves as the class object does). The index path reads
  `by_definition` for a single-socket name too. Kind NAME on a collection and kind CONTRACT: unchanged. `by_type`
  holds only such spells; `by_label`, `by_contract`, `by_definition` unchanged. `SpellMap(spell=X)` with no spellframe: only an X bound with no spellframe - with no binding_name, only
  the default binding; with `binding_name=b`, only X bound bare under `b`. `SpellMap(spell=X, spellframe=F, ...)`:
  unchanged.

## Interface Deltas
- Inputs: none (no signature changes).
- Outputs: candidate maps exclude framed and named spells for class lookups; a single socket left with no candidate
  is recorded UNRESOLVED_INPUT by the unchanged `_build_local_frame_dag` path.
- Error semantics: unchanged types and texts. A SpellMap default that now finds nothing raises the existing
  RuntimeError "SpellCrafter Phase 3: SpellMap default could not be resolved ..."; T3 part (a) is where the message
  learns to name where the class is bound.

## State and Lifecycle Deltas
- Owned state changes: none. The candidate index stays pass-scoped in `resolution_pass_cache`; its keys stay
  pass-invariant (spellframe, binding name and spell_name are fixed at bind).
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none new in kind; more consumers reach the existing UNRESOLVED_INPUT path (a class annotation of
  a framed or named class) and the existing SpellMap miss (`SpellMap(Class)` of a framed or named class).
- Removed failure mode: the S1 key split for class annotations - a consumer compiled before its framed provider
  waited under the class name while the provider's bind announced its frame (14 strict xfails).
- Changed failure mode: an AMBIGUOUS_PROVIDER between a bare English and a framed English for `x: English` no longer
  arises (only the bare one is a candidate).

## Dependency and Ordering Constraints
1. The predicate is applied on both the scan path (`_spell_keys_for`, read by `_matches_annotation`) and the index
   path (`_build_candidate_index`'s `by_type`, read by `_index_buckets_for`), in the same change, so the two paths
   stay equal (cross-component invariant 4).
2. The creation-cache generation moves to 26 in the same change set, so no bundle replays phase 3-4 rows computed by
   the old rule (component_patch_creation_cache_generation.md).
3. The tests and docs listed in the architecture patch land in the same change set as the src change.

## Validation Expectations
- Test/validation item 1: tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py asserts, for
  the scan and the index path alike: a class annotation and `list[Class]` skip a framed spell and a named bare spell
  and find a bare default-binding spell; a single string annotation keeps the contract keys of a framed spell;
  Protocol, definition and label lookups are unchanged; `SpellMap(spell=X)` reaches only bare X (default binding
  without a name, the named binding with one) and `SpellMap(spell=X, spellframe=F)` is unchanged.
- Test/validation item 2: the S1 regression file (tests/component/.../test_conduit_component_waiting_consumer_wakes_for_its_provider.py)
  asserts the class consumer of a framed provider stays unresolved where it held 14 strict xfails.
- Evidence target 1: the full suite the GIL off and on; the S1 matrix and interface-check re-runs.

## Unknowns and Open Decisions
- UNKNOWN: none for this component.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet; this patch fixes the contract.
- Remaining risks: a test whose fixture relies on the old rule in a way T1 did not see (T1 ran the whole suite under
  the probe, so the measured list is the expectation; any extra failure is investigated, not converted blindly).
- Next entrypoint: `CompilerPhase3._spell_keys_for`.
