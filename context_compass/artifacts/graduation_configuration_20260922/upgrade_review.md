# Upgrade to normal: completed delivery

The public upgrade is now wired to the separate private Spellbook conjure method. It preserves the
same Conduit object, ID and retained creation stores, while creating an independent normal root
with a new empty Book, its own bindings, configured hooks, pool and cluster facade. No parent,
old definitions, contracts or former-root resolution verdicts are inherited.

## Public setup

```python
lesser.upgrade_to_normal("independent")

configuration = SpellbookConfiguration("application").with_defaults()
configuration.with_bind_hooks(pre=[check_reference], activation=[inspect_spell], post=[record_bind])
configuration.with_hooks(on_meld_pre_resolve=before_meld)
lesser.upgrade_to_normal("configured", configuration=configuration)
```

The example configuration must use the lesser's existing frame. With no explicit configuration,
local mode uses fresh defaults; shared mode adopts the frame's canonical configuration. An explicit
different object cannot override shared policy. A local configuration already owned by the former
Book is rejected; supplying it would create two cleanup owners.

Bind defaults are empty. Configured Bind seeds are immutable tuples captured once per Book; adding
or clearing runtime Bind hooks changes only that Book. Configuration seed setters apply before
freeze and affect future Books only. Conduit/Meld defaults use the existing hook APIs with omitted
Book ID; exact Book event lists replace defaults for the same event. Recording retains presence
markers only, including effective default events and current Book Bind stages.

Explicit upgrade `hooks=` remains a local runtime addition after conjure activation. To run callbacks
during normal creation/activation, supply them through configuration. Normal CONJURE transaction
rules remain: structural binding belongs after upgrade returns, not inside its activation callback.

## Source review locations
- src/melder/aether/conduit/conduit.py:1961 - public upgrade, admission and pre-attachment rollback.
- src/melder/aether/spellbook/spellbook.py:220 - normal configuration/Bind setup and delayed identity publication.
- src/melder/aether/spellbook/spellbook.py:6635 - separate existing-conduit conjure and runtime attachment.
- src/melder/aether/spellbook/configuration/spellbook_configuration.py:702 - initial Bind hook APIs.
- src/melder/aether/spellbook/configuration/spellbook_configuration.py:834 - runtime defaults and Book precedence.
- src/melder/aether/spellbook/bind/bind.py:197 - immutable seed capture for a Book-local registry.
- src/melder/aether/conduit/conduit_ward/conduit_ward.py:526 - reciprocal parent detachment.

Meld/Space lookup aliases and input/fast-door caches are replaced only during adoption. Ordinary Meld
execution receives no new locks or checks. Existing stores keep retained objects/disposal metadata;
old spell IDs fail lookup after graduation. Cleaning either independent root preserves the other.

## Concurrency and failure boundary
Graduation drains the target gate before status changes. Its gate is reindexed under the new root
and original admission is restored before activation callbacks. A previously parked gate remains
parked. Pre-attachment failures restore the lesser before waking waiters and clean only new resources.
Publication failures after attachment retain normal conjure's caller-owned cleanup responsibility.

The caller must stop concurrent scope acquisition and lineage mutation/teardown, and return managed
SpellSpaces held on other threads. Those stacks are thread-local. Current-thread managed Spaces,
registered manual Spaces and idle pooled Spaces are rebound in place.

## Validation
- Final owner-requested hook-isolation qualification: 157 passed, including twelve additional
  scenarios across local/shared policy, retained Space modes, rollback/retry and separate frames.
- Affected unit/component/integration run: 4,118 passed, 2 skipped, zero failures/errors (16.96 seconds).
- All 32 original public ownership regressions pass; all 39 private-method cases pass.
- A strengthened second-drain failure test also passes in both local/shared modes, proving waiters
  remain parked until the public rollback completes.
- New/changed graduation tests pass Ruff; touched runtime files pass fatal-error lint.
- Source baseline comparison: 592 Python files checked, exactly five runtime files changed,
  no missing files and no generated build-asset changes.
- Full repository suite and coverage: Not run. Two existing tests are explicitly deferred by the
  owner for the separate shared-context revalidation investigation; no new skips were introduced.

Evidence: qualification_final.log/xml, rollback_gate_final.log/xml, hook_isolation_final.log/xml,
hook_isolation_lint.log, upgrade_tests_lint.log, upgrade_source_lint.log and upgrade_source_changes.json.

Legacy unit tests asserting discarded preset calls and copied root verdicts were replaced by real
component contracts. Their original bodies and the bounded migration script are retained here.
Book unit configuration doubles now expose the new empty seed getter; no runtime fallback was added.

## Frame-wide configuration in detail
The frame setting shares SpellbookConfiguration, not a Spellbook or its spell definitions. Upgrade
always constructs a new Book. During that constructor, _initialize_configuration consults the frame
posture and its canonical shared policy. The already-conjured original root established that policy.

| Frame policy and supplied input | Receiving Book configuration | Initial hooks |
| --- | --- | --- |
| Local, configuration omitted | Fresh defaults | Empty Bind/Conduit/Meld callbacks |
| Local, fresh matching object supplied | Supplied configuration | That object's seeds/default events |
| Shared, omitted or exact canonical object | Same frozen frame-owned configuration | Its seeds and effective default events |
| Shared, different supplied object | Rejected before promotion | Existing lesser remains unchanged |

Old Book-ID-specific Conduit/Meld event lists do not become defaults for the new Book ID. Runtime
Book/Conduit Bind mutations, lesser runtime overrides and retained Space Meld overrides do not cross
successful graduation. If configuration deliberately supplies defaults, the same callback objects may
appear again because those are the selected policy. Callback object/closure state is not cloned.

Each new Bind captures immutable seed tuples once. Its later add/clear operations replace its own
registry. Conduit/Meld local mutation APIs likewise preserve configuration-owned event lists. Direct
mutation of internal shared lists is outside that isolation contract; use the supported APIs.

The configuration is frozen: graduation cannot use a different local object to override shared frame
policy. Independent Book cleanup skips that canonical configuration; frame cleanup owns it. Other
AethericFrames select their own configuration and inherit none of these hooks.

## Turn-in and remaining build hold
The graduation epic and both tasks are closed under the owner's turn-in instruction. Scoped canonical
architecture/components, measured C1 ranges and graph descriptions were promoted; their indexes pass.
Original patch contracts and evidence are retained. The Melder build-asset runner was not invoked.
Packaged generation remains queued in TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved.
Broader pooled hook reset remains a separate task.
