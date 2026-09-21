# Bind lifecycle discovery and proposed implementation

- Owner: updater_0
- Task: TASK-2026-09-21-investigate-bind-lifecycle-hooks
- Epic: EPIC-2026-09-20-bind-lifecycle-hooks-and-reference-strategies
- Status: discovery complete; runtime implementation not started

## Expanded impact review (2026-09-21)

The current complete result lives in the parent epic, under Cross-Component Impact Map:
`tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md`.
Its Crystallizer, lifecycle, re-entry and regression sections extend this initial core-only plan.

Additional findings to carry into implementation:
- Hook marker production needs Book/Bind-to-emitter value plumbing, including origin re-freeze and
  the selected late-update policy. Generic record, JSON, formation and tap transport needs no new
  callback serializer; current preflight/restore already reports arbitrary names.
- Full restore has no hook attachment point before first replayed bind. Keep honest shortfalls unless
  the owner selects that extra loader seam. Graft uses callbacks configured on the receiving live Book.
- Book teardown currently deletes Bind without calling its cleanup; explicit child teardown is needed
  for new owned callback storage. Activation failure needs unpublished local Spell/index teardown,
  not public registered-book removal.
- A post callback at registration completion is not an outer-transaction commit notification.
  Explicit creation-hook kwargs attach after activation and replace only their supplied Spell lists.
- New preset/upgrade books receive fresh Bind storage; shared configuration does not share callbacks.
  Preserve native compiler/cache, Nexus and MR publication paths and their existing payload limits.

The expanded review is source-based. The 13 executed checks below remain characterization of the
current runtime; the proposed new callback feature and persistence behavior are not yet implemented.

## Owner's clarified contract

Register pre, activation and post bind hooks directly on Spellbook and associate them with its
existing Bind component. Activation receives the actual newly constructed Spell as its parameter,
mirroring Meld's activation callback for a newly created application object. Do not introduce a
restricted context copy, mutation whitelist or automatic identity-rebuilding framework for this.

The earlier suggestion to make a new SpellbookConfiguration hook category is superseded. These are
direct Spellbook setup hooks. Existing pre_hooks/activation_hooks/post_hooks supplied to bind keep
their current meaning: they are callbacks for later application-object creation/resolution.

## What the current runtime does

### Lesser binding

Both Conduit.bind and bind_inactive check for ConduitState.normal before delegation and raise
"Only normal conduits can bind spells" for a lesser. Normal post-conjure binding is additionally
gated by dynamic/frame posture. Bind_inactive also requires dynamic mode.

A lesser borrows its owning book's definitions. The characterization confirms that an already-live
lesser resolves a later binding made through that Spellbook or its normal root. Per-conduit objects
still live separately in the root and lesser. The hook feature does not need to enable lesser binding.

Evidence:
- src/melder/aether/conduit/conduit.py:3160-3197
- src/melder/aether/conduit/conduit.py:3264-3295
- src/melder/aether/conduit/conduit.py:2356-2395
- tests/experimentation/test_bind_lifecycle_discovery_experiment.py

### Configuration is not a universal pre-bind gate

Spellbook.__init__ supplies a default SpellbookConfiguration when one was not supplied or adopted.
An ordinary Spellbook().bind(...) succeeds while that configuration is mutable. The bind-family
gate allows pre-conjure binding unless disable_bind is set. After conjure, binding also requires
dynamic posture and enabled post-conjure transactions.

The special recorded-world rule is checked by conjure: dynamic plus active Crystallizer plus a
nonzero count of binds before configuration finalization causes refusal. Bind records the count;
it does not itself reject those early calls. Configure/finalize first in that recorded-world flow.

Evidence:
- src/melder/aether/spellbook/spellbook.py:3546-3568
- src/melder/aether/spellbook/spellbook.py:5202-5207
- src/melder/aether/spellbook/spellbook.py:5432-5477
- src/melder/aether/spellbook/spellbook.py:6513-6541

### Construction and registration are separate

Bind._bind_logic owns native admission, reflection, disposal matching, fingerprinting, SpellIndex
creation and the Spell constructor. It then completes the general profile and returns the Spell.
Spellbook.bind adds existing creation hooks, claims the lookup key, registers maps/ownership/state,
stages structural work and emits Crystallizer/MR/Nexus records as applicable. bind_inactive uses the
same constructor but parks the returned Spell and folds it into the target index instead.

This makes the new Spell constructor the activation seam, while successful registration belongs
to Spellbook. An activation callback is not a notification that the complete binding transaction
has already succeeded. A later native collision or registration failure can still occur.

Evidence:
- src/melder/aether/spellbook/bind/bind.py:339-551
- src/melder/aether/spellbook/spellbook.py:4753-4974
- src/melder/aether/spellbook/spellbook.py:5034-5292
- src/melder/aether/spellbook/spell.py:386-508

## Proposed small implementation

The public spelling is still a proposal; the owner has settled the ownership and activation subject:

```python
book.add_bind_hooks(
    pre=[check_reference],
    activation=[on_spell_created],
    post=[on_spell_bound],
)
```

Suggested callback subjects are pre(reference), activation(spell), post(spell). Pre receives the
original class/callable/existing-object input. Activation receives the real Spell immediately after
construction. Post receives that same Spell after its normal registration path completes.

```text
Spellbook: register hooks -> associate with owned Bind
bind input -> pre(reference) -> normal admission/profile/Spell construction
           -> activation(new_spell) -> normal completion and book registration
           -> post(bound_spell) -> return existing spell_id result
```

1. Add one registration surface on Spellbook; retain the ordered callback lists on its existing
   owned Bind component. Validate callability, preserve registration order and release references
   through normal Bind cleanup. No process-global registry or callback manager is needed.
2. Invoke pre during the bind path before constructing the Spell. Invoke activation directly after
   Spell construction, following the existing Meld activation pattern and HookExecutionError style.
   A pre rejection stops construction. An activation failure must release the unpublished Spell
   and its newly allocated owned artifacts, then propagate; do not add a global rollback framework.
3. Let Spellbook signal post after active or inactive registration has completed. Keep existing
   transaction nesting semantics: success of one bind is not a promise that an outer batch is already
   committed. Do not promise automatic undo of published state or external callback side effects.
4. Include the new hook-presence names in existing SpellbookCrystal emission. Callables remain
   application code, as for current hooks. This is value-marker plumbing through the existing book
   emitter, not registration through configuration and not callable serialization. Restore already
   reports arbitrary recorded hook names as hook_requires_code_participation shortfalls.
5. Cover direct/normal-Conduit/fluent/scan and inactive paths through the common book/Bind owners.
   Preserve the lesser refusal. No new argument forwarding is needed in every registration wrapper.
6. Update focused tests, public docs, component descriptions and generated assets after implementation
   and owner review. The present discovery pass changes no production files or generated assets.

Native fingerprint/profile/key mechanics remain as they are. Receiving a Spell callback parameter
does not itself imply a new automatic rehash or compiler-rebuild protocol.

## Expected source scope

| Owner | Expected work |
| --- | --- |
| Spellbook | Direct hook registration, active/inactive completion dispatch, presence-marker handoff |
| Bind | Per-book callback storage, pre and activation execution, cleanup and exception context |
| Existing book-twin emitter | Add bind-hook presence to the existing hook_names value payload |
| HookExecutionError | Reuse its existing phase/name/cause reporting; no new exception hierarchy |
| Tests/docs/assets | Stage ordering, compatibility, failure behavior and generated public descriptions |

SpellBinder.finalize and Scan.scan_module already call Spellbook.bind. The restore and graft paths
also re-enter normal bind verbs, but callback code is not reconstructed automatically. Hooks attached
to a receiving live book naturally participate when its bind API is called.

Evidence:
- src/melder/aether/spellbook/spellbinder.py:851-875
- src/melder/aether/spellbook/bind/scan.py:328-371
- src/melder/aether/spellbook/configuration/spellbook_configuration.py:363-398
- src/melder/crystallizer/crystal_loader_system/restore_engine.py:1793-1824

## Implementation checks to retain

- Exact ordered pre/activation/post events, with the activation argument identical to the Spell
  subsequently registered. No application constructor is called by binding activation.
- Failed pre checks produce no Spell/public binding. Failed activation skips publication/post;
  cleanup releases its unpublished allocation. Post failures report their stage honestly.
- Active and inactive creation both receive activation; later notch/reuse/meld does not pretend
  to construct that Spell again. Existing application creation hooks preserve their current behavior.
- Books remain isolated; cleanup releases callback references. Empty hook lists add no Meld work.
- Normal root/book late binding remains visible to lessers; lessers themselves still cannot bind.
- Hook-presence recording and restore shortfalls remain explicit, without serializing callbacks.

Registration/removal method spelling, callback-list replacement versus append and late registration
behavior can follow the existing ordered-hook conventions when implementation is selected. These
are small API decisions, not reasons to add a field-level mutation framework.

## Executed characterization

13 passed in 0.47 seconds through uv --no-sync --offline and .venv_new, using Python -X gil=0.
The selection covers 12 new characterization cases plus the existing creation-hook integration test.
The earlier selection had 12 passes before the explicit default-configuration case was added.

- tests/experimentation/test_bind_lifecycle_discovery_experiment.py
- tests/integration/melder/spellbook/test_spellbook_integration_hooks.py
- characterization_final.log
- characterization_final.xml

These tests describe current behavior. They do not implement or verify the proposed bind callbacks.

## Re-entry reading pointers

Use the architecture orientation and indexed component slices for Spellbook Core, Binding Pipeline,
Spellbook Configuration and Conduit Runtime. Then read the code units above. Existing component
claims that unknown hook names register silently are stale: add_hook rejects unknown names.

For the callback implementation, reopen Bind._bind_logic and cleanup; Spellbook.bind/bind_inactive,
constructor/cleanup, transaction and configuration emission; Spell._set_hooks and constructor;
Meld._execute_hooks/_execute_activation_hooks; the current HookExecutionError; SpellbookCrystal
and restore hook shortfall handling. Activation ownership is already decided by the owner.
