# Bind hooks: source ready for review

## Public API

```python
book.add_bind_hooks(
    pre=[check_reference],
    activation=[configure_spell],
    post=[after_bind],
)
book.clear_bind_hooks()
```

The same public methods are available as conduit.add_bind_hooks(...) and conduit.clear_bind_hooks().
Normal conduits delegate to their owning Book's registry. Lesser and cleaned conduits refuse before
delegation. Hook setup has Book parity on automatic/dynamic roots and does not enable prohibited binds.

Pre receives the incoming reference and rejects by raising. Activation receives the actual newly
constructed Spell before profile completion/publication. Post receives the registered active or parked
Spell. Callback return values are ignored. Existing creation hooks supplied to bind still run at Meld.

Registration appends in order; repeated callables are repeated registrations. Clearing removes all
three stages for future binds. Add/clear work before or after conjure, including with frozen/shared
configuration. A bind retains one immutable callback set, so updates during a callback affect later
binds, including nested calls, without changing the current operation's remaining stages.

## Source review map

- src/melder/aether/conduit/conduit.py: matching normal-Conduit registration/clearing facades.
- src/melder/aether/spellbook/spellbook.py: add_bind_hooks, clear_bind_hooks, book-twin handoff,
  active/inactive completion dispatch, explicit Bind cleanup and unpublished refusal cleanup.
- src/melder/aether/spellbook/bind/bind.py: immutable callbacks, synchronous dispatch outside the
  construction lock, phase/name/cause errors and unpublished Spell/index retirement.
- src/melder/aether/spellbook/configuration/spellbook_configuration.py: optional value-only bind-stage
  names through origin freeze/re-freeze and complete book-twin replacement.
- src/melder/utilities/custom_exceptions/hook_execution_error.py: updated bind/Meld error contract.

One failure regression exposed a pre-existing duplicate-ID ordering gap: pre-conjure local duplicates
could reach map mutation before the owned-ID check rejected them. Both bind paths now check their
owned-ID set alongside Aether before publishing. Rejected activated allocations are cleaned without
removing the existing binding. Post failures retain already-published state under existing semantics.

## Persistence and lifecycle boundaries

Crystallizer records bind:pre, bind:activation and bind:post presence, never callback functions.
Late changes refresh the complete twin and preserve configuration/Meld/Conduit marker data. Existing
checkpoint, formation, JSON and emission-tap paths retain those values. Full restore reports missing
callback code; live graft executes its receiving Book's hooks. No new schema version or serializer.

Post is per-registration completion, not an outer-transaction commit notification. Application
callback effects have no new automatic rollback guarantee. Cleanup releases borrowed callback
references; it does not dispose callback objects or supplied application instances.

## Executed checks

- 729 tests passed, zero failures/errors/skips, in 21.78 seconds.
- 58 new cases: 45 lifecycle/component and 13 Crystallizer integration regressions.
- New test files pass Ruff with UP007/UP045 excluded to match the repository's Optional/Union policy.
- Fatal/undefined-name checks pass across all touched source/test files.
- The initial full Ruff run reported 253 findings across the selected files, including legacy
  style issues and suggestions conflicting with the role's union policy. Only the new test import
  ordering was fixed; full legacy-file lint remains unclean and no broad reformat was performed.
- All 15 build-asset Python files match the pre-implementation hashes.

Evidence: final_with_conduit.log, final_with_conduit.xml, new_test_lint.log, fatal_lint.log and
asset_hold_with_conduit.log in this folder. Earlier logs retain the pre-facade validation history.
Coverage and performance comparison were not measured; no claim is made for them.

## Approval hold and next lane

No build runner, graph/index generation, manifest refresh, wheel, commit or publication was performed.
Generated assets and canonical documentation promotion remain held for owner code approval; the
authored patch contracts retain the complete documentation delta in the meantime.

Conduit/Meld hook clearing and re-registration is recorded as a separate follow-up investigation.
That investigation is now EPIC-2026-09-21-runtime-hook-lifecycle-and-adjustment. It found that current
upgrade_to_normal discards the new-Book factory result. A normal facade therefore still delegates to
the Book actually attached; graduation does not currently reset its bind hooks. Complete ownership
adoption is documented as separate future work, with no runtime changes authorized in that lane.
