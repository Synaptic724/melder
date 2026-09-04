# Task: Phase 1 - Disposal configuration, Bind, and Spell

## Metadata
- Task ID: TASK-2026-09-02-ordered-spell-disposal-contract-discovery
- Story: none
- Epic: EPIC-2026-09-02-ordered-live-spell-disposal
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-03T01:00:21Z
- Updated: 2026-09-04T21:33:23Z

## Objective
Explain how Spellbook configuration and per-bind disposal names become each Spell's
resolved disposal metadata. Establish selection, method matching, missing-name behavior,
storage, and fingerprint timing. Identify the values handed to compiler/Creations and
Crystallizer so the first implementation phase has a clear downstream contract.

## Ticket Contract
- ENTRY_GATE: Owner requested phases beginning with configuration, Bind, and Spell;
  the attention board routes to this task.
- EXECUTION_BOUNDARY: Configuration, Spellbook.bind/bind_inactive, Bind._bind_logic,
  Bind.sha256_profile, Spell initialization, and the existing class-profile method list.
  Compiler/Creations and Crystallizer reads are limited to the immediate handoff of names.
  Owner extension on 2026-09-04: map configuration schema/fluent API, Crystallizer
  configuration emission/reload, and Nexus configuration construction paths for the flag.
- DEPENDENCIES: Current Synaptic ownership/snapshot rules and existing reverse-creation
  cleanup contract.
- EXIT_GATE: Current selection and matching are explained with a concrete example;
  downstream handoffs are identified; the first correction is concrete and reviewable.
- FAILURE_ESCALATION: Stop on ambiguous ownership, hidden generated code, conflicting
  failure semantics, or a public API decision not established by source/user direction.

## Scope Boundaries
- In scope:
  - ordered Spellbook configuration vocabulary
  - per-bind selection and matching against existing class-profile method names
  - Spell storage and bind fingerprint inputs
  - direct handoffs into compiler, Creations, and SpellCrystal
- Out of scope:
  - source implementation before owner approval
  - unrelated cleanup ordering or object-lifetime redesign
  - implementation of later compiler, transfer, restore, and graft phases
  - defense against callers modifying internal attributes
  - commits, pushes, releases, or package publication

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Configuration/fluent, Crystallizer, and Nexus propagation are mapped;
  the Phase 1 design and planned checks are ready for review. Product code is unchanged.

## Steps / Checklist
- [x] Use indexed configuration/binding component sections to select the source methods.
- [x] Establish current source selection, filtering, absent-name behavior, and SHA timing.
- [x] Explain the direct handoff to Creations and Crystallizer.
- [x] Present the first phase's correction and distinguish it from existing behavior.
- [x] Map the flag through configuration defaults/validation, fluent APIs, Crystallizer,
      and Nexus configuration factories; identify edit versus unchanged generic paths.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A worked configuration-to-Spell example with exact source references.
- Phase 1 correction boundary and handoff requirements for phases 2 and 3.

## Phase 1 Findings

Owner constraint (2026-09-04): configuration names are established during configuration
creation, and each Spell's disposal policy is established during that Spell's creation.
Binding a different new Spell is a separate creation, not a later modification of an
existing Spell's disposal policy. Post-creation policy updates are outside this feature.

### Current configuration and selection
`SpellbookConfiguration` stores the provided `disposal_method_names` list. It has no
class profile and performs no method-existence matching. Its property setter enforces
write-once/frozen configuration rules. `add_disposal_methods` preserves first occurrence
order. Those are configuration operations; none calls cleanup methods on an instance.

Spellbook owns the selection between configuration and the argument to bind. On the
first `bind` or `bind_inactive`, `_configured_disposal_method_names` is unset. The call
chooses explicit names if present, else configured names, else empty, and freezes that
choice into the shared field. Subsequent binds reuse the field. They do not combine the
book names with explicit spell names, and later explicit arguments are ignored.

This separates two facts that earlier notes blurred: selection is latched once, but
matching runs independently on every class binding.

### Current matching and Spell ownership
`Bind._bind_logic` obtains the existing class binding profile. It keeps method names
found in the selected candidate collection. Names missing from that profile are skipped.
The matched names are deduplicated by frozenset construction, included in the bind SHA,
and passed to Spell. The Spell stores them and sets `has_disposal_methods` from whether
the collection is empty. The profile lists callable entries in the class's own namespace;
this phase preserves that matching boundary.

The user instance is not given new methods. The Spell is the metadata record for which
existing methods should later be called. Conjure's existing metadata check verifies type
and boolean consistency; it does not select additional names from configuration.

### Worked example
Assume the book config contains `["flush", "close", "shutdown"]`, each class defines
the listed methods itself, and no explicit bind argument replaces the initial candidates.

| Class | Methods available | Current matched membership | Desired method order |
| --- | --- | --- | --- |
| Connection | close, flush | close and flush (unordered) | flush, then close |
| Worker | shutdown | shutdown | shutdown |
| Calculator | calculate | empty | no disposal call |

Connection does not need `shutdown`; Worker does not need `flush` or `close`. A missing
candidate is skipped during matching. This is how one configured vocabulary serves
different user types. The order fix preserves this selection behavior.

### Consumer contracts for later phases
The runtime processor reads the Spell flag and names. Compilers pass them with each
new instance to `Creations.add_creation` or `add_many_creations`. Creations has no
configuration dependency and does not perform the profile match again. When the flag
is true, it records the instance plus the supplied method names. At cleanup it calls
those methods on the user instance in stored order, without arguments. The current loop
ends that instance's chain on the first exception; the enclosing registry continues with
other entries and collects failures.

The current registration methods copy the names into lists; this is an existing Phase 2
contact, not a recommendation to add copies. Phase 2 should consume the Spell-owned
resolved list directly through owned runtime paths under the Synaptic rules.

`SpellCrystal` records the resolved Spell names, currently using `sorted`. It does not
select methods or invoke disposal. Configuration also emits the book's configured
values at its existing freeze/emission boundary. Phase 3 must preserve the order of
both the configured vocabulary and each resolved Spell sequence during persistence.

The observed Bind and Creations paths use `has_disposal_methods` and matched names as
their gate. They do not consult the separate configuration `disposal` boolean. This is
recorded as current behavior; changing that flag's semantics is not part of the order fix.

## Phase 1 Design - Ordered Lists and Configurable Group Order
Owner direction on 2026-09-04 replaces the tuple/default-override proposal. This section
defines the next implementation; product code still has the current behavior above.

- Configuration and explicit per-spell names BOTH contribute to the new Spell's list.
- Configuration property: `enforce_priority_disposal_methods: bool`, default `False`.
- Suggested fluent setter: `with_enforce_priority_disposal_methods(enabled: bool = True)`.
  Calling the setter with True opts into priority; leaving the setting unset keeps it off.
- False: spell-specific names retain priority; matching book names append afterward.
- True: matching book names go to the front in configuration order, followed by the
  remaining spell-specific names in their supplied order.
- A name present in both groups occurs once at its first position. Enabling priority
  therefore moves shared names to the configuration-defined position as well.
- Use the configuration's existing setup/freeze lifecycle. The default False must not
  prevent opting into True during configuration assembly. Avoid a set-once default trap.
- Remove the first-bind shared-candidate latch. A new Spell receives the configured
  names and its own explicit names at that Spell's bind, in the selected group order.
- Bind builds ONE resolved list from the two groups using the existing class profile.
  Missing names are skipped. For the expected few names, membership checks against the
  existing profile list and the growing result list are sufficient; no set is needed.
- Keep the first occurrence of each matched name so a method shared by both groups
  executes once at its first position. This preserves current duplicate suppression.
- `None` or `[]` for spell-specific names means that group contributes nothing. It
  does NOT suppress the book's names; the earlier empty-list opt-out proposal is withdrawn.
- Spell directly retains the resolved list and computes its existing presence flag once.
  No tuple/frozenset storage or repeated defensive copies are introduced for this metadata.
- Feed the same ordered result into SHA at the current bind boundary. Identity timing
  remains unchanged; disposal policy is established once at Spell creation.
- Keep the current class-profile matching boundary and method-failure behavior.

### Examples of the new composition rule
Assume all listed methods are present in the class profile.

| Book names | Spell names | enforce_priority_disposal_methods | Final Spell list |
| --- | --- | --- | --- |
| flush, close | disconnect | False (default) | disconnect, flush, close |
| flush, close | disconnect | True | flush, close, disconnect |
| flush, close | close, release | True | flush, close, release |
| flush, close | close, release | False | close, release, flush |
| flush, close | close, stop, flush | True | flush, close, stop |
| flush, close | empty | either | flush, close |

With duplicate names, first occurrence wins under the configured group priority.

### First implementation boundary
- `spellbook_configuration.py`: bool property/default/fluent setter plus ordered names.
- `spellbook.py`: replace shared candidate selection in `bind` and `bind_inactive` with
  separate book and per-spell inputs; retire the frozenset-specific conjure expectation.
- `bind/bind.py`: forward both groups and order policy, match into one list, suppress
  duplicates in first-occurrence order, and fingerprint that list.
- `spell.py`: direct storage of the resolved list and its existing presence flag.

The downstream compiler/Creations and persistence changes belong to phases 2 and 3.
Phase 1 cannot by itself establish ordering across recorded/restored worlds.

## Configuration Change Map

### Owner and fluent API - required source edits
One production file owns the property schema and fluent API:
`src/melder/aether/spellbook/configuration/spellbook_configuration.py`.

| Surface | Required change |
| --- | --- |
| `__init__` / `available_properties` | Register `enforce_priority_disposal_methods` as bool. Establish default availability before bind. |
| `_OPTIONAL_PROPERTY_DEFAULTS` | Add False so defaults-free configurations are not rejected for omitting an opt-in flag. |
| `load_default_dictionary` | Include False in the ordinary defaults/reload path; preserve explicitly configured True. |
| Fluent methods | Add `with_enforce_priority_disposal_methods(enabled: bool = True)`, delegate to `set_property`, return self. |
| `with_defaults` documentation | Describe default False and its relationship to the two ordered method groups. |
| Existing disposal-name methods | Keep list input/order; any deduplication remains first-occurrence based. |
| `freeze` / `finalize` / `build` | Keep their existing configuration lifecycle; no disposal matching moves here. |

Default availability is a real creation-path issue, not private-mutation defense.
`Spellbook._initialize_configuration` keeps a supplied config without validating or
loading defaults. A caller can therefore bind before `_OPTIONAL_PROPERTY_DEFAULTS`
has been applied. Adding only a defaults-table entry and then unconditionally calling
`get_property` during bind would fail for that currently supported path.

Recommended implementation: establish False as configuration-owned state during setup,
including reassembly after `clear_properties`, and keep the new flag configurable while
the configuration is being assembled. Do not put a seeded default into the current
set-once `_idempotent_keys` behavior, which would prevent setting True. Keep initialization,
ordinary defaults, optional validation defaults, and recorded reload coherent inside this
configuration class. Existing partial-configuration iteration expectations need review if
the new default becomes immediately visible.

If eager default initialization is used, preserve the reload diagnostic contract:
recorded True/False must win; a missing recorded flag uses False. Check the existing
`backfilled` accounting, which currently compares property keys before and after default
loading; an eagerly present value must not be mistaken for a recorded value.

### Fluent binding - existing passthrough
`SpellBinder` is distinct from the configuration's fluent methods. It already supports
`with_kwargs(disposal_method_names=[...])`, and `finalize` forwards those kwargs into
`Spellbook.bind`. There is no separate SpellbookConfigurationBuilder to update.

No new priority flag belongs on SpellBinder: it is configured on the book configuration.
The existing per-spell names passthrough must be covered when Bind composition changes.
Do not pass the priority flag as arbitrary bind kwargs; that is a different metadata path.

### Crystallizer configuration transport - generic paths
The flag belongs in the book twin's `configuration_payload`. It is not a new setting on
CrystallizerConfiguration or an extra top-level field on every SpellCrystal.

Current flow:
1. Configuration freeze emits through `_emit_spellbook_twin_when_recording` when origin
   identity and recording/dynamic posture permit it. Its scalar branch preserves bools;
   its collection branch preserves list iteration order.
2. `SpellbookCrystal.__init__` and `describe` carry the configuration property mapping.
3. `PersistenceProfile.record` stores the book twin. `capture_segment_since` and
   `capture_formation_slice` obtain the book's describe payload without filtering keys.
4. `PersistenceCrystal` stores and exports the captured payloads through `to_cached_item`,
   `from_cached_item`, and `replay_data` without interpreting book property names.
5. `RestoreEngine._replay_one_book` hands `configuration_payload` to
   `SpellbookConfiguration.load_recorded_dictionary` before reconstructing that book's binds.

No per-flag branch is needed in these carrier/engine paths. Registering the key in the
configuration schema allows recorded True/False to be accepted on reload. Missing-key
defaulting and its report remain the configuration class's responsibility.

Resolved method-name recording remains a separate Phase 3 item: `SpellCrystal` currently
sorts its list. Recording the bool alone does not fix that sorting or the staged/graft
argument omissions. The book record must carry its flag/vocabulary and each Spell record
must preserve its final order; verify both in the later round-trip tests.

### Nexus - inspected, no duplicate property required
The actual managed-frame path is:
`NexusFrameBuilder.build/create` -> `NexusFrameConfiguration` ->
`NexusFrameManager._conjure_root_conduit_for_configuration` ->
`NexusFrameConfiguration.to_spellbook_configuration` -> ordinary `with_defaults` ->
`Spellbook(configuration=...)` -> conjure.

Once normal Spellbook defaults contain the flag, Nexus-created books inherit False.
The frame builder carries frame posture, metadata, immutability, and root conduit name;
it has no current rich Spellbook-property override input. Its metadata bag does not
forward disposal settings. A test should verify the default on the produced book config.

No edit is required to NexusConfiguration, AethericFrameConfiguration, the Nexus root,
or the frame builder just to carry the default. Exposing custom rich Spellbook settings
through the Nexus frame builder would require an additional API for configuration input,
including method names; it is not silently added as part of this flag.

### Consumption and focused verification
The producer work already planned in `spellbook.py`, `bind/bind.py`, and `spell.py`
must consume this configuration flag once per new Spell. No reader is added to Creations
or the disposal loop for the flag. The resolved list expresses the selected priority.

Planned tests, not executed in this mapping pass:
- `tests/unit/melder/spellbook/configuration/test_configuration.py`: normal/defaults-free
  False, explicit True preserved by defaults, correct bool validation, fluent self return,
  frozen lifecycle, and partial-config/clear/reassembly default availability.
- `tests/component/melder/spellbook/test_spellbook_component_configuration_core.py`:
  public configuration construction and default availability before the first bind.
- `tests/unit/melder/aether/test_configuration_reload_lanes.py`: recorded True and False,
  absent flag -> False with accurate backfill reporting, and sealed configuration on return.
- `tests/unit/melder/aether/test_nexus_frame_configuration.py`: default False on
  `to_spellbook_configuration()`; no new Nexus-owned priority field.
- Focused book-twin/checkpoint coverage: the flag and non-alphabetical names survive
  emitted configuration -> book crystal -> cached checkpoint -> configuration reload.
- Later Phase 1 binding tests: per-spell names through SpellBinder passthrough and both
  priority modes against book names. Later Phase 3 tests cover full active/staged replay.

### Evidence for the configuration map
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:114-160`
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:202-256`
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:258-481`
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:505-652`
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1049-1191`
- `src/melder/aether/spellbook/spellbook.py:5423-5474`
- `src/melder/aether/spellbook/spellbinder.py:641-661`
- `src/melder/aether/spellbook/spellbinder.py:826-870`
- `src/melder/crystallizer/crystals/spellbook_crystal.py:92-141`
- `src/melder/crystallizer/crystals/spellbook_crystal.py:240-264`
- `src/melder/crystallizer/persistence/persistence_profile.py:1028-1306`
- `src/melder/crystallizer/persistence/persistence_crystal.py:78-184`
- `src/melder/crystallizer/persistence/persistence_crystal.py:345-451`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1822`
- `src/melder/nexus/nexus_frame_builder.py:219-268`
- `src/melder/nexus/nexus_frame_configuration.py:334-349`
- `src/melder/nexus/nexus_frame_manager.py:994-1030`
- `tests/unit/melder/aether/test_configuration_reload_lanes.py:31-89`
- `tests/unit/melder/aether/test_nexus_frame_configuration.py:178-195`

## Files / Paths Impacted
- `context_compass/attention_board.md`
- This task.
- Product and test files remain read-only during discovery.

## Validation
- Not run; this is a read-only contract-discovery pass.
- Mapping verification: selected component indexes verified by the slice tool; edited
  task/epic sections reread; no whitespace errors or conflict markers found in the two
  ticket files; attention-board diff check passed. Product tests were not executed.
- Handoff verification (2026-09-04T21:09:45Z): all 19 source/test references under
  Evidence for the configuration map resolve to files with valid line ranges.
- Existing source read and component-index verification support the explanation.
- Earlier hash-seed output in the epic was a Python collection/hash-pattern probe.
  It was not a successful Melder bind reproduction: that attempt failed to import on
  the default Python 3.13. Future runtime verification must use the supported interpreter.
- Recommended commands after an implementation is approved:
  - focused disposal configuration/bind/Creations tests
  - persistence/restore round-trip tests
  - build-asset and repository-asset checks

## Risks / Rollback Notes
- Missing one transformation or serialization seam could make live behavior ordered while
  fingerprints, compiled creation paths, or restored worlds still reorder methods.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - ordered disposal vocabulary and spell ownership
  - compiled/persisted cleanup metadata
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: exact ownership/transform points and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-03T01:00:21Z
  TYPE: PLAN
  CLAIM: Trace the disposal method sequence end to end before proposing edits,
    specifically rejecting defensive list snapshots and preserving the live
    spell-owned list contract requested by the owner.
  EVIDENCE:
  - Owner direction in the active conversation, 2026-09-03T01:00:21Z
  - `agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:29-36`
  IMPACT: The resulting change boundary will follow the actual runtime path and
    the repository's ownership rules rather than a container-type substitution.
  NEXT: Slice the binding, configuration, and creations components through the
    verified component index.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-03T01:01:59Z
  TYPE: FACT
  CLAIM: The canonical component map routes disposal configuration through
    `SpellbookConfiguration`, binding through `Bind` into spell-owned metadata,
    and runtime lifecycle through `Creations`; these are one subsystem boundary,
    not independent list substitutions.
  EVIDENCE:
  - `context_compass/system_docs/src_components.md:499-603`
  - `context_compass/system_docs/src_components.md:705-794`
  IMPACT: The source read must follow configuration ownership into Bind, Spell,
    compiled creation metadata, and Creations before proposing any edit.
  NEXT: Verify the graph index, slice those source nodes, then read the concrete
    implementations completely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-03T01:03:42Z
  TYPE: FACT
  CLAIM: The verified source graph routes disposal metadata through nine live
    source families: Spellbook/configuration, Bind, Spell, runtime analysis and
    generalized plans, Conduit/Creations, SpellCrystal, and both restore/graft
    replay paths. The graph is current at 25,706 lines and its recorded SHA256.
  EVIDENCE:
  - `context_compass/system_docs/src_graph.md:4696-4739`
  - `context_compass/system_docs/src_graph.md:5328-5701`
  - `context_compass/system_docs/src_graph.md:6448-6494`
  - `context_compass/system_docs/src_graph.md:9637-9773`
  - `context_compass/system_docs/src_graph.md:14636-14721`
  - `context_compass/system_docs/src_graph.md:16196-16883`
  IMPACT: A correct change cannot stop at replacing the two visible frozensets;
    compiled creation and replay carriers can otherwise retain stale ordering or copies.
  NEXT: Read the complete concrete source files for all nine families and inventory
    every disposal-method transformation inside them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:15:29Z
  TYPE: DECISION
  CLAIM: The owner split the work into phases and selected configuration, Bind,
    and Spell first. This task now owns that phase; consumers are inspected only
    at their interfaces. Earlier whole-pipeline and mutable-list plans above are
    historical and do not expand this phase.
  EVIDENCE:
  - Owner instruction in the active conversation, 2026-09-04
  IMPACT: Discovery follows the component map to the first phase's methods and
    produces a concrete explanation before later runtime/persistence development.
  NEXT: Read the indexed configuration component and verify the input-to-Spell methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:15:29Z
  TYPE: FACT
  CLAIM: Configuration supplies candidate names; Bind performs matching for EVERY
    class binding. Only candidate selection is latched once per Spellbook. The
    first bind picks its explicit names when supplied, otherwise configuration
    names, otherwise empty, and stores a shared frozenset. Later binds use that
    same candidate set but receive independently matched Spell metadata. Bind
    filters against the existing class profile, omits absent names, hashes the
    matched collection, and supplies it to Spell.__init__. Spell stores it and
    computes has_disposal_methods. Configuration freeze does not redo this match.
  EVIDENCE:
  - `context_compass/system_docs/src_components.md:705-794`
  - `src/melder/aether/spellbook/spellbook.py:5030-5304`
  - `src/melder/aether/spellbook/spellbook.py:4754-4970`
  - `src/melder/aether/spellbook/spellbook.py:5423-5474`
  - `src/melder/aether/spellbook/spellbook.py:5714-5776`
  - `src/melder/aether/spellbook/bind/bind.py:310-485`
  - `src/melder/aether/spellbook/spell.py:287-497`
  - `src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:67-132`
  IMPACT: Book-level names are an optional vocabulary across classes, not methods
    imposed on every created object. Missing names are expected to be filtered.
    The first-bind latch and frozensets are the two separate Phase 1 concerns:
    which input applies, and which order its matches retain.
  NEXT: Record the consumer handoff and a worked example distinguishing selected
    method membership from the requested execution order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:20:36Z
  TYPE: FACT
  CLAIM: The configured vocabulary is applied to Spell metadata at Bind. Creations
    later receives a concrete user instance, a presence flag, and the resolved
    names. It has no configuration dependency and invokes methods on that user
    instance in stored order. SpellCrystal records the resolved names and sorts
    them today. These are the direct consumer boundaries Phase 1 must serve.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:38-100`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:8-112`
  - `src/melder/aether/conduit/creations/creations.py:93-145`
  - `src/melder/aether/conduit/creations/creations.py:197-354`
  - `src/melder/crystallizer/crystals/spell_crystal.py:143-339`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:319-396`
  IMPACT: Matching can remain an existing setup operation; consumers need one
    established ordered sequence. Current copies/sorting are documented for later
    phases and are not permission to introduce defensive snapshots.
  NEXT: Review the Phase 1 proposed correction, especially explicit per-spell versus
    book candidate precedence, before developing the binding changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:28:00Z
  TYPE: DECISION
  CLAIM: The owner confirmed that configuration and Spell disposal policies are
    established only during their creation. The feature must resolve applicable
    names once per new Spell, then consume that established metadata at disposal.
    The remaining composition question concerns simultaneous book-level and
    explicit spell-level inputs at creation, not updates to existing metadata.
  EVIDENCE:
  - Owner instruction in the active conversation, 2026-09-04
  - `src/melder/aether/spellbook/bind/bind.py:310-485`
  - `src/melder/aether/conduit/creations/creations.py:197-354`
  IMPACT: Re-identification, mutation guards, and repeated runtime method checks
    are not part of this feature. Current code has one disposal execution chain;
    it does not independently run book names and spell names at cleanup.
  NEXT: Explain that single consumption chain and settle whether explicit spell
    names replace or supplement book names when both are supplied at creation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:38:15Z
  TYPE: DECISION
  CLAIM: The owner chose list storage and composition of BOTH book and explicit
    Spell names. Book methods go first by default; a configuration setter can
    place them after the Spell's methods. Each group's supplied order is kept.
    This replaces the tuple and per-spell-replaces-defaults proposals. Matching
    occurs once during Spell creation, then Spell owns the final resolved list.
  EVIDENCE:
  - Owner instruction in the active conversation, 2026-09-04
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:202-238`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1107-1159`
  - `src/melder/aether/spellbook/bind/bind.py:310-485`
  IMPACT: Phase 1 has a concrete composition contract and four source files in
    its proposed boundary. First-occurrence deduplication retains the existing
    execute-once semantics without a stored set. The ordering flag changes group
    placement; it is not a disposal on/off switch. Later phases consume the list.
  NEXT: Prepare the Phase 1 implementation contract and focused checks for both
    group orders, overlaps, missing names, and independent new Spell inputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:47:44Z
  TYPE: DECISION
  CLAIM: The owner named the setting enforce_priority_disposal_methods and chose
    False as the default. True places matching book methods at the front in the
    configuration's supplied order, including names also present in the Spell's
    own list. False preserves spell-specific priority and appends remaining book
    methods. Matching and first-occurrence deduplication still happen once at bind.
  EVIDENCE:
  - Owner instruction in the active conversation, 2026-09-04
  IMPACT: This supersedes the earlier disposal_methods_first name and default True.
    Both groups continue to contribute; False disables priority, not the book's
    disposal contribution. The configuration flag is consumed during Spell creation.
  NEXT: Prepare Phase 1 implementation with the named setting, default False,
    and regression cases for overlaps reordered by configuration priority.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:54:35Z
  TYPE: PLAN
  CLAIM: The owner requested the configuration change map, including the fluent API,
    Crystallizer, and any Nexus path that constructs or carries Spellbook configuration.
    Follow the configuration and Nexus builder component sections to their implementation;
    this remains a mapping pass for enforce_priority_disposal_methods default False.
  EVIDENCE:
  - Owner instruction in the active conversation, 2026-09-04
  - `context_compass/system_docs/src_components.md:705-794`
  - `context_compass/system_docs/src_components.md:4902-4961`
  IMPACT: The change map must cover actual configuration construction and persistence,
    including generic paths that need no new per-property code. Runtime matching stays
    in the existing Phase 1 boundary.
  NEXT: Read the configuration schema/reload functions and Nexus builder/configuration pair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T20:54:35Z
  TYPE: FACT
  CLAIM: SpellbookConfiguration owns its schema and fluent methods in one file.
    available_properties is also the required-property list unless a key is in
    _OPTIONAL_PROPERTY_DEFAULTS. Ordinary defaults, validation-only defaults, and
    recorded reload are distinct paths. set_property checks key/lifecycle; value
    type checking occurs during validate. Emission generically carries bools and
    lists into SpellbookCrystal.configuration_payload. NexusFrameBuilder stages
    frame posture only, and NexusFrameConfiguration.to_spellbook_configuration
    constructs SpellbookConfiguration().with_defaults().
  EVIDENCE:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:114-160`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:202-238`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:319-396`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:398-481`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:559-652`
  - `src/melder/crystallizer/crystals/spellbook_crystal.py:92-141`
  - `src/melder/crystallizer/crystals/spellbook_crystal.py:240-264`
  - `src/melder/nexus/nexus_frame_configuration.py:334-349`
  - `src/melder/nexus/nexus_frame_builder.py:219-268`
  IMPACT: Generic record carriers do not need a separate per-flag field. The new
    property must default correctly in each creation path. Raw configurations
    retained by Spellbook before validate require particular attention because
    get_property raises on an absent key.
  NEXT: Trace Nexus realization and Crystallizer reconstruction, then map pre-bind
    default availability and the focused configuration tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:02:10Z
  TYPE: FACT
  CLAIM: The priority bool can travel inside the existing book configuration payload.
    SpellbookCrystal.describe preserves the property mapping; profile checkpoint and
    formation capture use twin.describe; PersistenceCrystal cached/replay forms carry
    those payloads unchanged. RestoreEngine reloads the book configuration before its
    binds. Nexus-managed creation uses NexusFrameConfiguration.to_spellbook_configuration,
    which loads normal defaults, then passes that object into Spellbook. Nexus builders
    expose frame posture and root naming, not custom rich Spellbook properties. SpellBinder
    separately forwards per-bind names through with_kwargs/finalize and needs no flag field.
  EVIDENCE:
  - `src/melder/crystallizer/crystals/spellbook_crystal.py:240-264`
  - `src/melder/crystallizer/persistence/persistence_profile.py:1028-1162`
  - `src/melder/crystallizer/persistence/persistence_profile.py:1164-1306`
  - `src/melder/crystallizer/persistence/persistence_crystal.py:78-184`
  - `src/melder/crystallizer/persistence/persistence_crystal.py:345-451`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1822`
  - `src/melder/nexus/nexus_frame_configuration.py:334-349`
  - `src/melder/nexus/nexus_frame_manager.py:994-1030`
  - `src/melder/nexus/nexus_frame_builder.py:219-268`
  - `src/melder/aether/spellbook/spellbinder.py:641-661`
  - `src/melder/aether/spellbook/spellbinder.py:826-870`
  IMPACT: Required schema/fluent edits are in SpellbookConfiguration. The generic
    Crystallizer record and Nexus default-construction paths require verification,
    not duplicated priority flags. The downstream resolved-list sorting remains
    Phase 3 work. Raw supplied configurations still need the default before bind.
  NEXT: Finish the configuration change map with default-lifecycle requirements and
    tests distinguishing flag transport from later resolved-method replay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:06:17Z
  TYPE: PLAN
  CLAIM: Configuration mapping is complete and this discovery task enters review.
    Required owner edits are schema/default availability and the fluent setter in
    SpellbookConfiguration. Existing book-twin/checkpoint/reload transport carries
    the flag generically; Nexus-created configurations inherit the normal default.
    Source consumers in the existing Phase 1 boundary still need implementation.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:195-320`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:114-160`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1822`
  - `src/melder/nexus/nexus_frame_configuration.py:334-349`
  IMPACT: The reviewable map distinguishes actual schema changes, generic consumers,
    pre-bind default availability, and deferred final-method-list replay work.
  NEXT: Prepare Phase 1 implementation from the accepted composition rule and this
    configuration map, with focused configuration and binding verification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Execution successor: `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`.
The epic's Implementation Task Sequence links three stories and nine bounded tasks.
This discovery document stays in review as their shared evidence source.

Re-entry: complete the repository REONBOARD flow, then read Phase 1 Design,
Configuration Change Map, its Evidence section, and this summary. Earlier Notes retain
superseded tuple/default-True/override-only proposals as history; use the current design.

The configuration change map above is complete. Required configuration/fluent edits live
in SpellbookConfiguration: bool registry, False defaults available before Bind, optional
validation defaults, and with_enforce_priority_disposal_methods. Keep reload diagnostics
honest when defaults are initialized early. Generic Crystallizer book payloads carry the
flag and Nexus default construction inherits False; no duplicate root flags are needed.
SpellBinder already forwards explicit disposal names through with_kwargs/finalize.

Phase 1 combines book and per-spell names into one Spell-owned LIST at creation. False
keeps spell-specific names first; True moves matching book names to the front in config
order. The first occurrence wins for overlaps. Prepare implementation for configuration,
Spellbook, Bind, and Spell; later phases handle runtime propagation and final-list replay.
The Nexus frame builder has no existing custom rich-config input; exposing one is extra
API work and is not part of the default propagation map. Product code remains unchanged.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
