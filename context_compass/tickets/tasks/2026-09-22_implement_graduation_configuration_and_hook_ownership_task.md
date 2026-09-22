# Task: Implement normal Book setup and hook ownership during graduation

## Metadata
- Task ID: TASK-2026-09-22-implement-graduation-configuration-and-hook-ownership
- Epic: EPIC-2026-09-22-graduated-conduit-spellbook-ownership-and-configuration
- Status: in_progress
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-22T11:00:19Z
- Updated: 2026-09-22T11:00:19Z

## Objective
Promote a lesser with independent normal-Book configuration, Bind hooks and registration ownership.
Apply ordinary configuration selection and initialize Conduit/Meld hooks from the selected policy.
Keep parent state isolated and preserve deterministic creation cleanup. Assets remain held.

## Ticket Contract
- ENTRY_GATE: Owner explicitly authorized source implementation after configuration research.
  Record and consume patch contracts before runtime edits.
- EXECUTION_BOUNDARY: Configuration initial hooks, Book/Bind construction and adoption, graduation,
  Meld/Space aliases, ward detachment, focused tests and authored patch documentation.
- DEPENDENCIES: 32 red ownership cases, normal configuration selection and existing hook contracts.
- EXIT_GATE: Selected desired behavior passes regressions and compatibility checks; code ready for
  owner review; generated assets remain unchanged.
- FAILURE_ESCALATION: Preserve the owner's empty-Book boundary. Raise any actual lifecycle obstacle
  without inventing inherited definitions or transferring the former Book.

## Scope Boundaries
- In: optional upgrade configuration; default local configuration; frame-owned adoption/refusal;
  initial Bind callback defaults; Conduit/Meld default hook setup; lifecycle/adoption isolation.
- Out: universal runtime-hook standardization, pool lease baseline redesign, callback serialization,
  generated assets and unrelated refactors.
- All ordinary meld hot paths remain unchanged; reference updates occur only at graduation/setup.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner authorized configuration and hook implementation using normal Book rules.

## Work
- [ ] Record patch contracts and source/test mapping.
- [ ] Implement initial configuration hooks and normal Book initialization.
- [ ] Implement coherent graduation adoption with an empty independent Book.
- [ ] Qualify Book/Bind/Conduit/Meld/Space ownership and cleanup against the red cases.
- [ ] Review source, record results and leave generators held for owner review.

## Planned Source Owners
- src/melder/aether/spellbook/configuration/spellbook_configuration.py
- src/melder/aether/spellbook/bind/bind.py
- src/melder/aether/spellbook/spellbook.py
- src/melder/aether/conduit/conduit.py
- src/melder/aether/conduit/meld/meld.py
- src/melder/aether/conduit/spell_space/spell_space.py
- src/melder/aether/conduit/spell_space/spell_space_pool.py
- src/melder/aether/conduit/conduit_ward/conduit_ward.py
- Focused configuration/graduation/Bind tests and existing affected doubles.

## Resolved Graduation Contract
The owner explicitly corrected the visibility question: the promoted conduit is a normal root with
no parent and no inherited spells. Adopt a new empty Book. Do not transfer the former Book, copy
registries or introduce implicit borrowing/contracts. Existing creations are distinct from registered
definitions; preserve their store and disposal responsibility without inventing definition inheritance.
Legacy tests resolving old spell IDs after upgrade must be corrected to this documented contract.

## Validation
Not run for implementation yet. Use uv offline/no-sync with .venv_new, Python -X gil=0. Regression
baseline is 32 expected failures plus 3 passing existing controls. Preserve ordinary Bind snapshots,
configuration freeze, frame sharing and no-hook execution behavior.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/graduation_configuration_2026_09_22/
  - artifacts/graduation_configuration_20260922/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes
- DATETIME: 2026-09-22T11:00:19Z
  TYPE: DECISION
  CLAIM: Owner authorizes configuration, Bind/Meld/Conduit hook implementation so graduation
    follows ordinary normal-Book setup. Fresh local defaults and shared-frame constructor policy
    are established. Inherited-definition visibility was asked separately; no reply yet.
  EVIDENCE:
  - Owner's current implementation instruction.
  - tickets/epics/2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md
  IMPACT: Source work may proceed under patch contracts. Generators remain held for code approval.
  NEXT: Write the configuration/hook patch contract and consume relevant graph/source slices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T11:09:31Z
  TYPE: DECISION
  CLAIM: Owner explicitly resolves the question in chat: graduation creates an independent normal
    conduit with no parent and a new empty Book. The factory docstring states that bindings, spell
    indexes and conduit attachment do not transfer. Previous test expectations were incorrectly
    treated as a design requirement; they must not drive an implicit inheritance model.
  EVIDENCE:
  - Owner's consecutive no-parent, no-spells and docstring-direction corrections.
  - src/melder/aether/spellbook/spellbook.py:6387-6423
  - src/melder/aether/conduit/conduit.py:1961-2024
  IMPACT: No visibility decision remains. Keep creation retention separate from Book definitions;
    revise legacy expectations and all pending-gate prose before implementation resumes.
  NEXT: Resume the authorized normal-setup implementation after answering the owner's clarification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Owner correction is definitive: new normal root, no parent, empty new Book, no transferred or
implicitly borrowed spells. Retained Creations are not inherited definitions. Follow the factory
docstring and correct the legacy tests. Optional configuration and initial hooks follow normal Book
setup. Patch docs exist and were read; no runtime source edits have been made yet. Assets stay held.
