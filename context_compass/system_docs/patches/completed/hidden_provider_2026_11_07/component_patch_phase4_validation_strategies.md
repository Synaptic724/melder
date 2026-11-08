# component_patch_phase4_validation_strategies

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Component: Spell Validation Strategies (Phase 4): `HiddenProviderStrategy` (new), `HiddenProviderReport` (new
  renderer), `SpellValidationSystem`, `RequiredHolesStrategy`, `AmbiguousProviderStrategy`
- Status: draft
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Component Purpose and Boundary
- Current boundary: strategies judge what Phases 1-3 recorded; UNRESOLVED_INPUT is a warning (RequiredHoles),
  AMBIGUOUS_INPUT an error (AMBIGUOUS_PROVIDER).
- Target boundary: plus one error strategy over UNRESOLVED_INPUT sockets that carry `hidden_spell_ids`; one shared
  renderer of hidden candidates (also used by Phase 6, UnresolvedInputError and Phase 3's fallback RuntimeError).

## Before/After Behavior Summary
- Before: such a socket is only an UNRESOLVED_INPUT warning ("... but no registered spell provides it ..."); conjure
  succeeds. AMBIGUOUS_PROVIDER offers an override remedy the meld gate refuses (measured: a meld with an override of
  an invalid spell raises SpellbookValidationError).
  EVIDENCE: required_holes_strategy.py:131-159; ambiguous_provider_strategy.py:100-118; validation_system.py:182-195.
- After:
  1. New module `src/melder/aether/spellbook/spell_compiler/validation/strategies/hidden_provider_strategy.py`:
     `HiddenProviderStrategy`, name "hidden_provider", description "Refuses a class lookup whose class is bound only
     under a spellframe or a binding name, and says where.", registered right after `AmbiguousProviderStrategy`.
     One error per UNRESOLVED_INPUT socket with `hidden_spell_ids`; reads the topology through
     `spell._spell_system_states`, the parameter through `context.requirements`, the candidates through
     `context.spellbook.find_spell_by_spell_id`; honours cancellation; never raises for an unknown id.
  2. New module `src/melder/aether/spellbook/spell_compiler/validation/hidden_provider_report.py`:
     `HiddenProviderReport` (static, pure): `describe(candidate_id, spell)`, `where(candidates)`, `entry(...)`,
     `lookup(candidate, *, shape)` with shape "single", "spellmap" or "list".
  3. `RequiredHolesStrategy`: skips an UNRESOLVED_INPUT socket whose `hidden_spell_ids` is non-empty (the error
     reports it; no "no registered spell provides it" warning beside it).
  4. `AmbiguousProviderStrategy`: text without the override remedy; docstring "the two ways out".

## Exact texts
Rendering rules (HiddenProviderReport):
- entry: `<spell_name> at (spellframe=<frame!r>, binding_name=<binding_name!r>) - use <lookup>`; frame rendered as
  AMBIGUOUS renders it (a category as itself, a Protocol by `__name__`, None when bare); entries joined by "; ",
  ordered by (spellframe, binding_name, spell_name), None first; an id the spellbook cannot find: `spell id <id>`.
- where: "under a spellframe" (all framed) | "under a binding name" (none framed) | "under a spellframe or a binding
  name" (mixed).
- single-socket lookup: Protocol P -> `SpellMap(spellframe=P, binding_name='b')`, or `SpellMap(spellframe=P)` for
  the default binding; category c -> `SpellMap(spellframe='c', binding_name='b')` / `SpellMap(spellframe='c')`;
  bare under b -> `SpellMap(<Name>, binding_name='b')`.
- "the SpellMap shown" for one candidate, "the SpellMap of the one it needs" for several; the Protocol clause
  ", or a P annotation while that spell is the only one bound under P" only when one distinct Protocol frame is among
  the candidates (", or an annotation with its Protocol while that spell is the only one bound under it" for several).

(1) Single socket (class annotation, a string's type part, `Optional[Class]` without a default):
"Parameter 'greeter' on spell 'Host' expects English, but a class lookup reaches English only where it is bound bare
(no spellframe, the default binding), and English is bound only under a spellframe: English at
(spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, binding_name='english'). Ask for it
where it is bound - the SpellMap shown, as the parameter's default, or a Greeter annotation while that spell is the
only one bound under Greeter - or bind English bare."  [HIDDEN_PROVIDER]
Category, default binding: "... English is bound only under a spellframe: English at (spellframe='greeters',
binding_name=None) - use SpellMap(spellframe='greeters'). Ask for it where it is bound - the SpellMap shown, as the
parameter's default - or bind English bare."
Bare under a name: "... English is bound only under a binding name: English at (spellframe=None,
binding_name='english') - use SpellMap(English, binding_name='english'). Ask for it where it is bound - the SpellMap
shown, as the parameter's default - or bind English bare."
Two (MCPScanner): "Parameter 'profile' on spell 'MCPScanner' expects ScanProfile, but a class lookup reaches
ScanProfile only where it is bound bare (no spellframe, the default binding), and ScanProfile is bound only under a
spellframe: ScanProfile at (spellframe='agents', binding_name='ScanProfile') - use SpellMap(spellframe='agents',
binding_name='ScanProfile'); ScanProfile at (spellframe='artificial_intelligence_tools',
binding_name='ScanProfile') - use SpellMap(spellframe='artificial_intelligence_tools', binding_name='ScanProfile').
Ask for it where it is bound - the SpellMap of the one it needs, as the parameter's default - or bind ScanProfile
bare."

(2) `SpellMap(Class)` default:
"Parameter 'greeter' on spell 'Host' has the default SpellMap(English), a class lookup that reaches English only where
it is bound bare under the default binding, but English is bound only where that lookup does not reach: English at
(spellframe='Greeter', binding_name='english') - use SpellMap(spellframe=Greeter, binding_name='english'). Point the
SpellMap at the address it means, as shown, or bind English bare."  [HIDDEN_PROVIDER]
With `binding_name='b'`: "... has the default SpellMap(English, binding_name='b'), a class lookup that reaches English
only where it is bound bare under the binding name 'b', ... or bind English bare under the binding name 'b'." A bare
registration under another name renders `- use SpellMap(English, binding_name='x')`, under the default
`- use SpellMap(English)`.

Details (both forms): {"spell_id", "parameter_name", "lookup": "annotation" | "spellmap", "expected_type" (annotation)
or "spellmap" (its rendering), "dependency_key", "candidates": [{"spell_id", "spell_name", "spellframe",
"spellframe_kind", "binding_name", "use"}]}.

(3) AMBIGUOUS_PROVIDER after (D4): "Parameter 'greeter' on spell 'ByProtocol' expects Greeter, but 2 registered
spells provide it: English at (spellframe='Greeter', binding_name='english'); French at (spellframe='Greeter',
binding_name='french'). Select one with a SpellMap default on the parameter (SpellMap(spellframe=...,
binding_name=...)), or bind only one provider of this type."

## Interface Deltas
- Inputs: the descriptor fields from Phase 3.
- Outputs: SpellValidationIssue(severity="error", code="HIDDEN_PROVIDER", ...); one fewer UNRESOLVED_INPUT warning per
  such socket; the shorter AMBIGUOUS text.
- Error semantics: HIDDEN_PROVIDER makes the spell broken (`CompilerPhase4` sets `_is_broken`; the SpellIndex goes
  `invalid`). Conjure raises SpellbookValidationError; a dynamic late bind raises it from the post-conjure structural
  run and the spell stays registered and invalid; every meld after raises the same report (the meld gate's hard
  block on `invalid`), override or not - as AMBIGUOUS_PROVIDER (measured). Rendering in the report is unchanged
  ("  - <message> [HIDDEN_PROVIDER]"); no change to INTERNAL_CODES, GATING_WARNING_CODES, RESTATING_CODES,
  SUPERSEDED_BY.

## State and Lifecycle Deltas
- Owned state changes: none (strategies are stateless; the renderer is pure).
- Lifecycle/cleanup changes: the new strategy follows `SpellValidationStrategy` cleanup.

## Failure Mode Deltas
- New failure mode: HIDDEN_PROVIDER (error) for the shapes above.
- Removed failure mode: the UNRESOLVED_INPUT warning for those sockets.
- Changed failure mode: AMBIGUOUS_PROVIDER text.

## Dependency and Ordering Constraints
1. Registered after AmbiguousProviderStrategy (issues read RequiredHoles warnings, AMBIGUOUS, then HIDDEN).
2. Lands with Phase 3's recording (same change set).

## Validation Expectations
- Added: tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_hidden_provider_strategy.py - name,
  description; no topology, other kinds, a socket without ids -> nothing; one error per socket; the exact texts above
  for Protocol default and named, category default and named, bare named, mixed, two candidates ordered; the SpellMap
  forms (default and named); an unknown id renders by id; details; cancellation. A renderer test for
  `HiddenProviderReport` (where words, lookups per shape, ordering). RequiredHoles: a hidden socket emits no warning.
- Updated by design: test_ambiguous_provider_strategy.py::test_ambiguous_socket_names_every_candidate_address_and_the_remedies
  (assert the override remedy is absent; "three remedies" -> two).
- Rewritten - the 30 tests the emulated rule flips (measured: affected_diff_gil0.txt, affected_diff_gil1.txt, same
  30 both modes; examples 0 of 627):
  - tests/component/melder/aether/conduit/test_conduit_component_waiting_consumer_wakes_for_its_provider.py (10):
    A2-class-category, A3-class-protocol, A5-object-category, A8-name-category, A9-name-protocol, C1-protocol-index,
    C2-category-index, test_waiting_consumer_stays_unresolved_for_a_version_notched_in_under_a_category,
    G2-protocol, G3-category - the late twin is refused at bind; under D1 = B the waiting consumer is refused at its
    next meld too (one answer: refused).
  - tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py (9):
    test_spectrum_annotation_does_not_reach_a_spectrum_filed_under_a_category x6,
    test_two_framed_providers_of_the_annotated_type_leave_the_class_lookup_unresolved,
    test_two_same_named_classes_in_two_categories_leave_the_class_consumer_unresolved (MCPScanner),
    test_many_category_members_never_become_providers_for_the_type (MelderOps override shape, D2).
  - tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py (1):
    test_c4_a_class_annotation_never_reaches_a_framed_index_while_its_frame_follows_every_notch.
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_break_matrix.py (3):
    test_b1_dependency_only_under_binding_defers_and_conjures, test_e2_concrete_default_binding_missing_defers_and_conjures,
    test_b3_spellmap_without_binding_name_fails_conjure_on_binding_only_registration (PhaseExecutionError ->
    SpellbookValidationError [HIDDEN_PROVIDER]).
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_more.py (2):
    test_type_hint_di_concrete_class_bound_only_under_binding_names_is_unresolved,
    test_spellmap_explicit_class_with_wrong_binding_name_raises.
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py (5): see component_patch_compiler_phase_3.md.
  - Option B's 9 extra flips (tests/unit/melder/spellbook/test_spellbook.py) belong to the announce:
    component_patch_change_control_announcing.md.
- Evidence target 1: the full suite, the GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: none for this component.
- DECISION_REQUEST: none (name and severity settled, chat 2026-11-07).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: worlds that relied on override supply (D2) - the release note carries the migration paths.
- Next entrypoint: `HiddenProviderReport`, then `HiddenProviderStrategy.validate`.
