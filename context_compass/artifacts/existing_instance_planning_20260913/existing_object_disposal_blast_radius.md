# Existing-object disposal: implementation blast radius

Status: deferred source map; runtime and regression changes have NOT been applied.
The owner superseded its narrow implementation estimate with
EPIC-2026-09-13-existing-object-lifecycle-ownership on 2026-09-13. Read that epic before resumption;
transfer, rollback and the larger custody model must be settled before implementing the flag.
Owner: updater_0. Contract accepted by the project owner on 2026-09-13.
Task: TASK-2026-09-13-repair-existing-instance-planning.
Paths below are relative to the Melder repository root unless explicitly marked otherwise.

## Accepted contract

Add `existing_objects_configured_dispose_applied`, a boolean defaulting to False, to
SpellbookConfiguration. Add the fluent setter
`with_existing_objects_configured_dispose_applied(enabled: bool = True)` returning self.

| Flag | Explicit bind names | Book names | Effective policy for an existing instance |
| --- | --- | --- | --- |
| False | absent/empty | any | No disposal methods; retain/inject the borrowed value. |
| False | supplied | any | Match explicit names only, preserving their order. |
| True | absent/empty | supplied | Match the book group. |
| True | supplied | supplied | Match both groups using existing priority/overlap rules. |
| either | unmatched only | unmatched/disabled | Empty result; no disposable-registry entry. |

Example: book names `[flush, close]`, explicit names `[close, stop]`:
- Flag False: `[close, stop]`, irrespective of the book-priority flag.
- Flag True, priority False: `[stop, flush, close]`.
- Flag True, priority True: `[flush, close, stop]`.

Configure before the affected binds. Each Spell retains one resolved list. Changing configuration
later must not retroactively rewrite that list. Normal configuration freeze still seals all settings.
The separate `disposal` boolean remains stored metadata; this feature must not repurpose it as a gate.

## Core production edits: three files

### 1. SpellbookConfiguration

File: `src/melder/aether/spellbook/configuration/spellbook_configuration.py`.

- `__init__`: eager False value and `available_properties` boolean registration. Raw configurations
  already reach Bind before default loading; the new property must be readable there too.
- `clear_properties`: restore False, preserving the existing reassembly contract.
- `_OPTIONAL_PROPERTY_DEFAULTS`: keep defaults-free configuration assembly valid.
- `load_default_dictionary` / `with_defaults` documentation: populate missing only; never overwrite opt-in.
- Add the fluent setter beside the existing disposal setters. Preserve the shared validation,
  frozen-state and cleaned-state checks; do not coerce arbitrary truthy values into booleans.
- `load_recorded_dictionary`: account for an omitted eager default in the existing backfill report,
  as disposal priority already does. A fresh restore of an old record gets False and reports it.
- Extend configuration docstrings so this knob is visibly a bind-time policy for existing objects.

Evidence: this file, lines 112-156, 206-263, 440-493, 567-675, 1069-1179.

### 2. Spellbook active and inactive binding

File: `src/melder/aether/spellbook/spellbook.py`.

- `bind` and `bind_inactive`: explicitly pass the configuration value into the internal Bind call.
- Extend both disposal argument contracts with the prebuilt-object rule.
- Keep the policy on configuration. No separate public per-bind toggle or metadata workaround.
- Preserve existing post-conjure registration, transactions, ownership and crystal emission.

Evidence: this file, lines 4752-4949 and 5026-5260.

### 3. Bind-time disposal matching

File: `src/melder/aether/spellbook/bind/bind.py`.

- `bind`: add the internal policy argument and forward it through direct and decorator paths.
- `_bind_logic`: support existing-object profiles when matching requested disposal names.
- Apply book candidates to an existing object only when the flag is True. Explicit candidates
  remain effective in both modes. Reuse book overlap ownership, deduplication and block ordering.
- Determine callable members from the actual supplied instance at bind time, limited to the requested
  names. No constructor reflection, object reconstruction or disposal-method invocation at bind.
- Proposed lookup rule: normal callable member lookup on this external object; ignore absent or
  non-callable members. Unexpected descriptor-access errors remain binding errors, not silent fallback.
  Include inherited instance methods in those tests; this does not widen class-profile discovery.
- Retain the final list before SHA generation and pass the same list into Spell.
- Preserve current class-profile matching and callable/factory classification. A callable object is
  still a factory under the existing classifier; this feature does not add a factory-result policy.

Evidence: this file, lines 228-522 and 573-672;
`src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:42-136`.

No new fields are required in InstanceBindingProfile, Spell, execution-plan records or Creations.
Keeping the narrow member check in Bind avoids expanding general profile/fingerprint discovery.

## Lifecycle extension: staged objects need explicit handling

There is a source-confirmed gap beyond selecting names:

- Active prebuilt bindings are registered into Creations during conjure or immediately on late bind.
- `bind_inactive` retains its value but does not register it into Creations.
- Conjure's `define_conduit_into_spells` walks active `_spells` only.
- `_reactivate_owned_spell` / `_apply_notch` promote metadata without registering that value.
- Direct existing-object executors return the object without creating a registry entry.

Consequently, forwarding the flag into bind_inactive is necessary but insufficient to establish
cleanup custody for its supplied value. This is a source finding; no new runtime reproduction has run.

Recommended complete scope: explicitly track managed prebuilt values once a root exists, including
owned parked values. That means late bind_inactive adopts immediately; pre-conjure staged values are
adopted at conjure. Promotion/re-promotion must not register the same Spell twice. Borrowed values must
not acquire disposal merely because a borrower or lesser scope resolves them.

This would add one production file to the three above:
`src/melder/aether/spellbook/spellbook_creation_system.py:define_conduit_into_spells`, plus staged
registration work in the already-listed `Spellbook.bind_inactive`.

Confirm that ownership-start recommendation when implementing. In particular:
- A book cleaned before it ever conjures has no Creations owner today. Disposal before conjure would
  be a separate ownership expansion, not something this boolean alone supplies.
- Cleanup is per registered entry. Registering the identical object through multiple owning bindings
  can request multiple cleanup chains. No global identity deduplication/reference counting is proposed.
- Cleaning a Spell's metadata currently drops its method-list reference without clearing lists still
  retained by Creations. Preserve this until runtime scope teardown; do not eagerly dispose on metadata cleanup.

Evidence:
- `src/melder/aether/spellbook/spellbook_creation_system.py:1188-1240`.
- `src/melder/aether/spellbook/spellbook.py:1507-1565`.
- `src/melder/aether/spellbook/spellbook.py:3681-3821`.
- `src/melder/aether/spellbook/spellbook.py:4752-4949`.
- `src/melder/aether/spellbook/spellbook.py:5206-5237`.
- `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234`.
- `src/melder/aether/spellbook/spell.py:505-606`.

## Existing carriers and consumers: verify, do not duplicate policy

| Area | Existing mechanism | Planned treatment |
| --- | --- | --- |
| Spell | Retains ordered names and derives has_disposal_methods | No new flag on Spell. |
| Conduit registration | Forwards names/boolean to Creations.add_creation | Test eager and late adoption. |
| Creations | Separate live/disposal registries, ordered method calls and error aggregation | Reuse unchanged. |
| Lesser / SpellSpace | Scope cleanup has existing ownership routing | Prove owner value survives borrowed-scope cleanup. |
| Linked borrower | Resolves an owner-supplied instance | Borrower's configuration must not rematch provider disposal. |
| SpellBinder | with_kwargs/finalize delegates to Spellbook.bind | Test explicit names; no new adapter setter. |
| Conduit bind facades | Forward kwargs into the corresponding book methods | No duplicate configuration field. |
| Nexus frame setup | Creates SpellbookConfiguration and loads defaults | Inherit False; no parallel Nexus property. |
| Bind SHA / compiler signatures | Already contain resolved ordered disposal metadata | Normal invalidation; no manual cache deletion or new flag-only hash. |

Evidence:
- `src/melder/aether/spellbook/spell.py:432-440`.
- `src/melder/aether/conduit/conduit.py:1386-1427`, `3097-3278`.
- `src/melder/aether/conduit/creations/creations.py:150-358`, `393-514`, `516-607`.
- `src/melder/aether/spellbook/spellbinder.py:641-660`, `826-870`.
- `src/melder/nexus/nexus_frame_configuration.py:334-349`.
- `src/melder/nexus/nexus_frame_manager.py:994-1030`.
- `src/melder/aether/spellbook/bind/bind.py:573-672`.
- `src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1150-1198`.

### Storage is already present; cleanup admission is separate

The supplied value remains on Spell.user_created_object, with the Spell retained in the book's
active or inactive maps. Direct existing-value executors return this field; active admission also
stores the same object reference in Creations. No object copy or new storage wrapper is required.
The staged gap concerns admission to cleanup tracking, not a missing reference to the value.
Existing-object live probes inspect that Spell field too, so they cannot by themselves prove disposal
registration. Verify actual cleanup calls and scope ownership in the new tests.

Evidence: `src/melder/aether/spellbook/spell.py:412-415`;
`src/melder/aether/conduit/meld/conduit_meld.py:541-546`, `724-735`;
`src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234`.

## Crystallizer and compatibility

The current generic configuration transport needs the new registered property, not a new crystal schema:

1. Configuration freeze emits all plain property values, including booleans.
2. SpellbookCrystal carries/describes the configuration dictionary.
3. Checkpoints retain that payload; RestoreEngine reloads it before binds.
4. Registered properties/default loading determine acceptance and legacy backfill.

SpellCrystal already captures the final ordered method list. Restore/graft already pass recorded
names through ordinary binding. Existing instances remain `replay_required`: recording the policy
does not serialize or recreate the external object. Preserve that limitation and test it explicitly.

Compatibility cases:
- Old records missing the knob: fresh configuration backfills False and reports the schema default.
- New False/True records: preserve exact boolean, method order and frozen state through reload.
- Old Melder readers do not know this property; their existing unknown-property reporting still applies.
- Flag changes producing a different resolved list change the existing content fingerprint. The flag
  alone need not change identity when the effective disposal behavior is identical.
- Explicit disposal names formerly ignored for prebuilt objects now become effective even with False.
  This intentional behavior correction must be prominent in documentation and regression updates.

Evidence:
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:330-402`, `596-675`.
- `src/melder/crystallizer/crystals/spellbook_crystal.py:92-141`, `244-264`.
- `src/melder/crystallizer/crystals/spell_crystal.py:275-299`, `1067-1115`.
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1738-1818`, `1908-2015`, `2456-2517`.
- `src/melder/crystallizer/crystal_loader_system/graft_runner.py:458-477`.

## Regression map

| Tests | Required evidence |
| --- | --- |
| tests/unit/melder/spellbook/configuration/test_configuration.py | Eager False, setter return, both defaults orders, toggle/reset, bool validation, freeze/cleanup refusal. |
| tests/component/melder/spellbook/test_spellbook_component_configuration_core.py | Defaults-free assembly and shared configuration behavior. |
| tests/component/melder/spellbook/test_ordered_disposal_binding.py | Flag x priority x candidate groups; active/inactive/fluent paths; SHA/list identity and class/factory controls. |
| tests/integration/melder/spellbook/test_existing_instance_disposal.py (new) | Real disposal and exact identity before/after conjure; no-meld disposal; dependency-before-owner order; failures and repeated cleanup. |
| Same new integration file | Lesser, SpellSpace, linked borrower, parked/promoted values, separate bindings of one object, pre-conjure ownership boundary. |
| tests/component/melder/crystallizer/test_disposal_configuration_transport.py | Real twin/profile/checkpoint JSON round-trip for False/True/missing legacy flag; exact backfill reporting. |
| tests/integration/melder/crystallizer/test_ordered_disposal_replay.py | Restore configuration before active/staged binding; ordinary class replay remains correct. |
| tests/experimentation/test_existing_instance_gap_experiment.py | Replace the old instance-disposal-exclusion expectation; retain historical observation logs. |

Existing controls to retain/run where relevant:
- tests/integration/melder/conduit/test_ordered_disposal_runtime.py.
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_references.py.
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py.
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py.
- tests/integration/melder/spellbook/test_existing_instance_planning.py.
- tests/integration/melder/spellbook/test_existing_instance_additional_regressions.py.
- tests/integration/melder/spellbook/test_deferred_annotations.py.

Update only the prebuilt case of the old class-profile exclusion test. Preserve inherited-only
class and factory exclusions. Assert actual calls, identity, order and ownership; avoid filler tests.
Use distinct owner and borrower books for policy-isolation cases; their configurations may otherwise
be deliberately shared. Cached tests use isolated temporary cache roots and ordinary invalidation.

The original CommandOps/Iris test remains unchanged. Its ActivityBootstrap supplies no class disposal
names and the book uses an empty list; this flag cannot repair that separate configuration omission.
No claim of full downstream acceptance follows from passing this feature's native tests.

## Documentation and generated outputs

Authored updates:
- docs/intermediate/configuration.md: flag table, ordering examples, prebuilt exception, legacy policy.
- docs/beginner/registration.md: borrowed default and explicit/optional configured cleanup custody.
- context_compass/system_docs/src_components.md: Binding Pipeline, Configuration, Creations sections.
- context_compass/system_docs/src_architecture.md: operational disposal/adoption invariant.
- Production docstrings and appropriate new regression docstrings.

Generated updates, after source/docs settle:
- Regenerate indexes for changed authored system documents.
- Refresh descriptors for the three core source files and the creation-system file if extended.
- Reassemble src_graph.md plus its index; do not hand-edit generated graph output.
- Run src/melder/_build_assets/_build_asset_runner.py and its --check gate (all three builders).
- Rebuild/check llm_support src, tests and other corpora; public docs change the other corpus.
- Run the existing documentation/build checks appropriate to the changed public pages.

No version bump, replacement wheel, environment sync, named-conduit work, provider-artifact repair,
frame-validation repair or factory-result disposal is part of this design tranche.

## Implementation order and exit evidence

1. Finalize the staged-value ownership boundary and record the required patch contracts.
2. Add red regressions for configuration, explicit disposal, enabled book policy and staged tracking.
3. Implement configuration and bind-time matching; include the selected staged-adoption correction.
4. Verify real owner cleanup plus borrower/scope/order controls and record the results.
5. Verify configuration/checkpoint transport and unchanged external-object replay limitations.
6. Refresh authored docs, descriptors and all affected generated assets; run their check modes.
7. Report exact tests, remaining limitations and downstream status for owner review.

This map is complete as a design artifact. Tests were not run for this mapping pass; no disposal
source changes or test changes have been made. Earlier annotation/injection patches remain intact.
