# Epic: Give graduated conduits independent Spellbooks and explicit configuration

## Metadata
- Completed: 2026-09-22T14:41:23Z
- Summary: Graduation source, hook isolation and shared-frame behavior qualified and turned in; packaging held separately.
- Epic ID: EPIC-2026-09-22-graduated-conduit-spellbook-ownership-and-configuration
- Status: done
- Owner: user
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-22T10:28:54Z
- Updated: 2026-09-22T14:41:23Z
- Related discovery: TASK-2026-09-22-investigate-pooled-conduit-hook-reset

## Completed Delivery
Source, regressions and scoped canonical documentation are turned in under the owner's instruction.
Public upgrade uses the separate PRIVATE Spellbook conjure route, optional configuration follows
normal selection, and each new Book owns its Bind registry. Runtime defaults can be configured
before a Book ID exists. Broad source qualification passed 4118 tests with two existing skips;
the final 157-test selection includes twelve additional hook-isolation/shared-frame scenarios.
Packaged build generation remains held in TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved.
Review: artifacts/graduation_configuration_20260922/upgrade_review.md.

2026-09-22 implementation is now authorized in
tickets/tasks/completed/2026-09-22_implement_graduation_configuration_and_hook_ownership_task.md.
Use normal Book setup for configuration and Bind/Meld/Conduit hooks. Generated assets remain held.
Earlier research-only boundaries below describe the completed discovery/red-test phase.

The owner requests failing regression tests and a new epic for discussion. Runtime repair and
generated assets are held. Graduation should own its Book, its bindings and its cleanup; bind
hooks start empty. The owner also proposes an optional SpellbookConfiguration argument on
upgrade_to_normal for configuring the new local Book. Exact argument and precedence rules remain
discussion items. Frame-wide configuration remains a distinct legitimate shared owner.

Latest direction: graduation should support ordinary normal-Book setup. In local mode an omitted
configuration means fresh defaults, not a copy of the parent configuration. Bind hooks should start
empty unless explicitly supplied through configuration. Research the actual frame-wide adoption
and hook behavior before runtime changes; that investigation is now active.

## Problem / Opportunity
upgrade_to_normal calls create_new_preset_spellbook but discards its return. The newly normal
Conduit and Meld still reference the parent Book. Bind-hook facades consequently mutate the
parent's Bind, later binds register there, and normal cleanup retires that parent Book.
Assigning the returned Book alone leaves cached Meld/Space lookup references and Book attachment
inconsistent. The factory also shares configuration by reference, although local configuration
cleanup treats a non-frame-owned configuration as Book-owned.

Evidence:
- src/melder/aether/conduit/conduit.py:1961-2140
- src/melder/aether/conduit/conduit.py:3098-3179
- src/melder/aether/conduit/conduit.py:757-866
- src/melder/aether/conduit/meld/meld.py:228-264
- src/melder/aether/conduit/spell_space/spell_space.py:166-208
- src/melder/aether/spellbook/spellbook.py:496-505
- src/melder/aether/spellbook/spellbook.py:6387-6423

## MRP Alignment
Graduation must establish one coherent owner for registration, execution and teardown. Preserve
existing creations deliberately, keep configuration ownership explicit, and avoid modifying the
parent merely because the child became a root.

## Ticket Contract
- ENTRY_GATE: Owner-authorized regression task routed; source findings reviewed before repair.
- EXECUTION_BOUNDARY: Red tests and this design record now. Later implementation requires a
  reviewed graduation/configuration contract and patch documents.
- DEPENDENCIES: Book/Bind ownership, Conduit/Meld/Space aliases, ward topology, frame configuration,
  transaction identity, recorded Book/Conduit twins and existing graduation creation contracts.
- EXIT_GATE: Accepted implementation proves isolation and lifecycle behavior across local/shared
  configuration, with focused tests and owner-approved documentation/assets. Source qualifies now;
  asset generation still awaits approval.
- FAILURE_ESCALATION: Record unresolved definition visibility and configuration precedence rather
  than changing tests or runtime to hide them.

## Goals and Scope
- Graduated conduit owns an independent Book and new bindings. Bind hooks start empty unless
  explicitly seeded by the selected configuration under the forthcoming agreed configuration API.
- Parent and graduated bind hooks can be added/cleared independently.
- Each normal conduit cleans its own Book, bindings and creations.
- Frame-owned shared configuration remains shared and survives individual Book cleanup.
- Local configuration has explicit ownership; graduation can accept a caller-configured object.
- ConduitMeld and pre-existing/pooled SpellSpaces follow the correct post-upgrade Book.
- Parent/child detachment and failure ordering do not leave accidental teardown ownership.

## Non-Goals
- Pool hook-baseline repair, universal hook APIs or callback serialization.
- Runtime changes or asset generation in the current red-test pass.
- Silently removing old spell visibility or transferring parent-owned definitions.
- Inventing a second Bind registry on a Conduit while still sharing the parent's Book.

## Configuration Distinctions for Discussion
| Concern | Existing owner / required distinction |
| --- | --- |
| Bind lifecycle hooks | Book-owned Bind callback tuples; separate Books start empty even with shared configuration. |
| Configured Conduit/Meld hooks | Configuration stores hooks by Book ID; sharing the configuration object alone does not establish a new Book's effective hooks. |
| Frame-wide rich configuration | Canonical frame-owned object when sharing is enabled; individual Books must not clean it. |
| Local rich configuration | Book-owned policy; copying/borrowing/adopting on graduation needs an explicit lifecycle contract. |

Proposed public capability: optional SpellbookConfiguration on upgrade_to_normal. Discuss the
keyword name, omission default, frame matching, freeze/activation timing and behavior when the frame
already owns shared configuration. Do not silently let a supplied local object override frame policy.
The shared mode's configured runtime-hook inheritance must be stated independently of clean Bind hooks.

## Open Questions
- Resolved: omitted local configuration uses fresh defaults, per owner direction on 2026-09-22.
- When frame-wide sharing is enabled, must an explicit argument be the canonical object, be rejected
  if different, or be ignored with a documented contract? Existing Book construction rejects mismatch.
- Which configured Conduit/Meld hooks should a new Book ID inherit in shared/local modes?
- Resolved by owner: the upgraded normal conduit has no parent and no inherited spells. Its new Book
  starts empty. No Book transfer, registry copy or implicit borrowing. Legacy old-ID resolution tests
  reflect the defect and must be corrected; creation-store retention is a separate lifecycle concern.
- Can active manual/managed Spaces cross graduation, or must that shape fail before mutation?
- Keep the existing childless-only ward rule or support descendants in a separate future change?

## Normal Configuration Research (2026-09-22)
The ordinary Spellbook constructor already provides the selection policy graduation should reuse.
Frame posture and rich Spellbook configuration are distinct objects: the frame posture contains
shared_framewide_spellbook_configuration, which defaults to False and becomes immutable on freeze.

| Effective frame policy | Upgrade configuration input | Existing ordinary Book behavior |
| --- | --- | --- |
| Local configuration | Omitted | Creates a fresh same-frame SpellbookConfiguration and loads defaults. |
| Local configuration | Supplied object | Retains the supplied object after checking its frame name; ordinary validation/freeze still applies. |
| Shared configuration already published | Omitted or the canonical object | Adopts the exact frame-owned object and marks configuration locked. |
| Shared configuration already published | Different object, even equivalent values | Raises RuntimeError for a mismatched configuration; no local override is installed. |
| Sharing enabled, no object published yet | Omitted or supplied | Initially selects like a local Book; the first conjure publishes the canonical object and later publishers adopt it. |

The last row describes general Book creation. During a normal lesser graduation the original root
has already conjured, so an enabled shared configuration should already have its canonical object.
The constructor ignores any stored rich configuration when frame sharing is disabled.

Activation/ownership behavior:
- Conjure validates/freezes unlocked rich configuration, binds frame posture, and conditionally
  publishes rich configuration. Defaults fill missing keys without replacing explicit values.
- A provided config is not automatically default-filled by construction. Normal validation requires
  its mandatory properties; users may prepare it with with_defaults and setters before upgrade.
- Aether serializes first-publication selection. Book publication adopts a winner and cleans a losing
  local candidate instead of replacing the frame-owned object.
- Book cleanup skips the canonical shared configuration. Frame cleanup owns its final disposal.
- Local configuration is Book-owned. The existing preset factory always borrows the parent's object,
  so it does not implement the requested fresh-default graduation policy.

Hook behavior verified in source:
- Configuration admits only Conduit/Meld/link/contract hook names, indexed by Spellbook ID.
- Conjure and Conduit construction look up the new Book's exact ID. A shared configuration is not
  a default hook list for every Book. An unknown Book ID produces an empty map.
- Configuration hook setters refuse writes after freeze, including in shared mode.
- Bind pre/activation/post callbacks live in Bind._lifecycle_hooks and begin as empty tuples.
  Configuration has no callable-bearing Bind hook setter or initialization path today.
- origin_bind_hook_names on freeze is value-only recording metadata supplied by the Book; it does
  not configure callbacks and must not be mistaken for a hidden Bind hook setup API.

Recommendation for the owner's explicit configuration requirement (not implemented):
- Reuse ordinary Book configuration selection during graduation rather than creating another set
  of precedence rules or sharing the parent's local configuration implicitly.
- Add explicit configuration defaults for Bind callbacks if callbacks must be selectable before
  the new Book exists. These are initial callbacks, independent of the Book-ID runtime-hook maps.
- Each new Book initializes its own Bind callback tuple from the selected configuration. Callback
  objects may be referenced by multiple Books, but subsequent Book/Conduit add/clear affects only
  that Book's Bind. Configuration defaults and parent runtime modifications must remain unchanged.
- Defaults contain no Bind callbacks. A frame-owned configuration may deliberately supply common
  initial callbacks, while each Book still owns subsequent registration changes and cleanup.
- Apply any configuration-seeding behavior equally to ordinary Books and graduated Books.
  Preserve marker-only Crystallizer recording and the existing source-participation restore contract.

Research evidence:
- src/melder/aether/aetheric_frame/aetheric_frame.py:214-269
- src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:648-699
- src/melder/aether/aether.py:1503-1575
- src/melder/aether/spellbook/spellbook.py:5577-5696
- src/melder/aether/spellbook/spellbook.py:5866-5999
- src/melder/aether/spellbook/spellbook.py:496-505
- src/melder/aether/spellbook/configuration/spellbook_configuration.py:78-164
- src/melder/aether/spellbook/configuration/spellbook_configuration.py:265-415
- src/melder/aether/spellbook/configuration/spellbook_configuration.py:445-479
- src/melder/aether/spellbook/configuration/spellbook_configuration.py:580-607
- src/melder/aether/spellbook/configuration/spellbook_configuration.py:692-927
- src/melder/aether/spellbook/spellbook_creation_system.py:289-317
- src/melder/aether/spellbook/spellbook_creation_system.py:1243-1276
- src/melder/aether/conduit/conduit.py:334-363
- src/melder/aether/spellbook/bind/bind.py:190-223
- tests/component/melder/spellbook/test_spellbook_component_configuration.py:83-274

No runtime or test changes were made during this research pass. The earlier 32 red regressions and
3 passing controls remain the last execution evidence; no additional test execution is claimed.

## Proposed Work Sequence
1. Capture current failures with real component regressions; keep plain failing tests, no xfail.
2. Agree configuration precedence and inherited-definition visibility before repairing adoption.
3. Implement coherent Book attachment, lookup rebinding, ward detachment and owned cleanup.
4. Qualify new bindings through Conduit/Space, both cleanup orders and refusal before mutation.
5. Verify recording identity/presence and replay implications; promote docs/assets only when approved.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner requested turn-in after additional regression tests, which now pass.

## Required Reading Before Implementation
Re-read src_architecture and verified src_components slices for Spellbook Core, Configuration,
Conduit Runtime, Conduit Hook Wiring, Meld Resolution and Creations/SpellSpace. Then read:
- src/melder/aether/conduit/conduit.py: upgrade_to_normal, bind facades, pool/Space lifecycle, cleanup.
- src/melder/aether/spellbook/spellbook.py: constructor, preset factory, configuration adoption,
  cleanup, bind/bind_inactive, transaction metadata and Bind marker emission.
- src/melder/aether/spellbook/spellbook_creation_system.py: _activate_conjured_conduit and owner wiring.
- src/melder/aether/spellbook/bind/bind.py: hook storage/capture and cleanup.
- src/melder/aether/conduit/meld/meld.py: Book aliases, lookup caches and cleanup.
- src/melder/aether/conduit/meld/conduit_meld.py and spellspace_meld.py: front-door ownership.
- src/melder/aether/conduit/spell_space/spell_space.py and spell_space_pool.py: retained collaborators.
- src/melder/aether/conduit/conduit_ward/conduit_ward.py: conversion, reciprocal detach and contracts.
- src/melder/aether/spellbook/configuration/spellbook_configuration.py: hook Book-ID keys and freeze.
- src/melder/aether/aetheric_frame/aetheric_frame.py: frame configuration and root registration.
- tests/component/melder/aether/conduit/test_conduit_graduation_ownership_regression.py.
- tests/component/melder/aether/conduit/test_conduit_component_creations.py.
- tests/integration/melder/conduit/test_conduit_integration_lifecycle.py.
- tests/integration/melder/spellbook/test_spellbook_integration_core.py.
- tests/component/melder/spellbook/test_bind_lifecycle_hooks.py.

## Acceptance Criteria
- New Book is attached and starts with no bind callbacks unless the selected configuration seeds them.
- Child bind/clear/add operations leave parent bindings and callbacks unchanged.
- New bindings carry graduated ownership and resolve through its Conduit and supported Space doors.
- Cleaning either independent normal conduit preserves the other's Book and independent bindings.
- Configuration reuse follows the accepted frame/local contract; shared configuration is not retired
  by an individual Book, and local configuration cannot be accidentally destroyed by its sibling.
- Existing creation/definition behavior follows an explicit accepted contract.
- Failed unsupported upgrades leave no partial adoption or leaked new Book.

## Validation / Risks
Use real component tests with isolated Aether/Nexus roots in local and shared-frame modes. The
current phase must remain red for the actual ownership failures, not setup or teardown mistakes.
Future repair also needs failed upgrade, inherited-definition and persistence qualification.

The first phase now confirms 32 intended assertion failures and 3 passing existing controls, with
zero errors/skips. All three Bind stages fail isolation in both configuration modes. Child teardown
retires the parent Book, parent teardown destroys the graduated root, and a new child unique is not
disposed by child cleanup. Fresh/pooled Spaces resolve through the wrong Book. Runtime code and
generated assets are unchanged. Exact evidence and commands belong to the linked regression task.

## Milestones
- [x] Red regressions confirmed and failure causes recorded.
- [x] Configuration and visibility decisions accepted.
- [x] Runtime repair implemented and qualified for owner source review.
- [x] Canonical documentation promoted; packaged build hold transferred to its own task.

## Tasks
- TASK-2026-09-22-add-graduation-ownership-red-regressions.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- Test-run evidence is owned by the regression task.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes
- DATETIME: 2026-09-22T10:28:54Z
  TYPE: DECISION
  CLAIM: Owner requests red regressions and discussion of optional upgrade configuration before
    runtime edits. Independent Book/binding/cleanup is required; frame-owned shared configuration
    remains legitimate. Do not conflate configuration hooks with Book-owned Bind callbacks.
  EVIDENCE:
  - Owner's current regression-test and optional SpellbookConfiguration request.
  - src/melder/aether/spellbook/bind/bind.py:190-223
  - src/melder/aether/spellbook/spellbook.py:5577-5696
  IMPACT: Test work is authorized; optional-argument semantics and the actual repair remain discussion.
  NEXT: Add and run the linked component regressions without changing runtime source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:37:51Z
  TYPE: MEASURE
  CLAIM: The regression task delivers 32 intended failing cases and 3 passing existing controls
    across local/shared configuration. The failures make the ownership defects concrete without
    implementing the repair or assuming an optional configuration keyword.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-22_add_graduation_ownership_red_regressions_task.md
  - tests/component/melder/aether/conduit/test_conduit_graduation_ownership_regression.py
  IMPACT: The discussion can now distinguish confirmed ownership regressions from still-open
    configuration precedence, runtime-hook inheritance and prior-definition visibility choices.
  NEXT: Agree those graduation contracts before creating the runtime patch plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:42:48Z
  TYPE: DECISION
  CLAIM: Owner wants ordinary normal-Book setup on graduation and fresh defaults when local
    configuration is omitted. Bind hooks clear unless explicitly configured. Trace frame-wide
    configuration adoption and existing hook storage before implementing any runtime change.
  EVIDENCE:
  - Owner's current normal-setup/defaults/explicit-hooks and frame-wide research instruction.
  IMPACT: Parent-property cloning is no longer an open local-default choice. Configuration-hosted
    Bind hooks still need their actual API/read-path investigation; do not assert they exist today.
  NEXT: Trace normal construction, frame configuration publication/adoption, hook lookup and cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:45:27Z
  TYPE: FACT
  CLAIM: Ordinary Book creation already selects fresh local defaults, a matching supplied config,
    or the canonical frame-owned shared config. A different supplied object conflicts once a shared
    object exists. Configured Conduit/Meld callbacks remain keyed by Book ID; Bind callbacks are not
    configurable through SpellbookConfiguration. Its Bind fields are recording names only.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5577-5696
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:78-164
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:265-415
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:692-927
  IMPACT: Reusing ordinary constructor selection avoids custom graduation precedence. The requested
    configured Bind behavior needs an explicit seed API with independent per-Book mutable state.
  NEXT: Discuss configuration-provided Bind defaults and the recorded normal-setup policy before source edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T14:41:23Z
  TYPE: DECISION
  CLAIM: Owner explicitly requested additional hook-isolation tests and graduation epic turn-in.
    The added twelve cases pass within a 157-test focused selection; prior broad qualification
    remains 4118 passes and two existing owner-deferred skips. Source behavior did not change in
    the final test tranche. Graduation source, regressions and canonical documentation are complete.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/hook_isolation_final.log:1-4
  - artifacts/graduation_configuration_20260922/qualification_final.log
  - artifacts/graduation_configuration_20260922/upgrade_review.md
  - artifacts/graduation_configuration_20260922/documentation_preservation.json
  IMPACT: Close the graduation epic and its implementation/red-regression tasks. Retain evidence
    and archive promoted patch contracts. Packaged build generation remains explicitly held in
    TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved; no build runner was invoked.
  NEXT: None for graduation source. The separate packaged-asset task waits for owner authorization.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10
## Context / Handoff Summary
CLOSED by owner-requested turn-in after additional hook-isolation qualification. Graduation creates
an independent empty Book, preserves the Conduit/ID/creation stores, and resets old Book-specific
hooks and runtime overlays. Frame-wide rich configuration stays canonical and frame-owned; its
deliberately configured defaults may seed the new Book without sharing runtime registration state.

All twelve added scenarios pass within 157 focused tests. Prior affected qualification: 4118 pass,
two existing owner-deferred skips. Canonical architecture/components, measured ranges and the scoped
graph descriptions are promoted; document indexes validate. Packaged build assets remain untouched.
See artifacts/graduation_configuration_20260922/upgrade_review.md for behavior and concurrency limits.
Only TASK-2026-09-22-refresh-graduation-packaged-assets-when-approved remains queued for packaging.
