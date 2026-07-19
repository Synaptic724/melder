# Task: Enforce Root Conduit Name Uniqueness For ACL Selectors

## Metadata
- Task ID: TASK-2026-04-04-enforce-root-conduit-name-uniqueness-for-acl-selectors
- Story: STORY-2026-04-02-profile-contracts-and-access-boundaries
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T18:44:16Z
- Updated: 2026-04-04T19:25:19Z

- Completed: 2026-04-04T19:25:19Z
- Summary: Root/normal conduit names are now a real frame-level invariant.
  They default to `"default"` when omitted, must be unique per frame, are
  unregistered on cleanup, and the grouped registry operations are protected by
  explicit lock boundaries.

## Objective
Make root/normal conduit names a real frame-level invariant so ACL selectors
can safely target conduits by name instead of relying on ambiguous lookup
behavior or cloud-only uniqueness.

## Ticket Contract
- ENTRY_GATE: the user approved the direction that persisted ACL selectors
  should use frame names, conduit names, and spell signatures instead of raw
  ULIDs.
- EXECUTION_BOUNDARY: runtime invariant change only for root/normal conduit
  naming and frame-level name registration/removal.
- DEPENDENCIES:
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - src/melder/aether/aether.py
  - src/melder/aether/aetheric_frame.py
  - src/melder/aether/conduit/conduit.py
- EXIT_GATE: root/normal conduit names are unique per frame, collisions fail
  fast, and cleanup/unregistration releases the name mapping.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if enforcing names on root/normal
  conduits forces broader runtime semantics the user has not approved.

## Scope Boundaries
- In scope:
  - frame-level conduit name registry
  - root/normal conduit add and remove paths
  - lesser -> normal upgrade path
  - focused unit coverage
- Out of scope:
  - ACL implementation
  - lesser conduit naming rules
  - broader UI/bootstrap work

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the invariant landed, the focused validation set passed,
  and the active work has moved back to ACL design.

## Steps / Checklist
- [ ] Add a frame-level conduit-name registry.
- [ ] Enforce uniqueness during root/normal conduit registration.
- [ ] Enforce the same rule during lesser -> normal upgrade.
- [ ] Release name mappings during conduit cleanup/removal.
- [ ] Add focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- frame-level root conduit name invariant
- focused tests

## Files / Paths Impacted
- src/melder/aether/aether.py
- src/melder/aether/aetheric_frame.py
- src/melder/aether/conduit/conduit.py
- tests/unit/melder/aether/
- tests/unit/melder/aether/conduit/
- codex/context_compass/tickets/tasks/2026-04-04_enforce_root_conduit_name_uniqueness_for_acl_selectors_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/aetheric_frame.py src/melder/aether/aether.py tests/unit/melder/aether/test_aether.py tests/integration/melder/aether/test_aether_integration_registry_ops.py tests/integration/melder/aether/test_aether_integration_error_paths.py tests/integration/melder/conduit/test_conduit_integration_lifecycle.py tests/integration/melder/conduit/test_conduit_integration_public_api.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/spellbook/spellbook/test_conjure_phase_invocation_counts.py`
  - `python -m pytest -q tests/unit/melder/aether/test_aether.py tests/integration/melder/aether/test_aether_integration_registry_ops.py tests/integration/melder/aether/test_aether_integration_error_paths.py tests/integration/melder/conduit/test_conduit_integration_lifecycle.py tests/integration/melder/conduit/test_conduit_integration_public_api.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/spellbook/spellbook/test_conjure_phase_invocation_counts.py`

## Risks / Rollback Notes
- Risk: we accidentally force naming behavior on lesser conduits or other
  internal paths that should remain unnamed.
  Rollback: keep the invariant narrowly scoped to root/normal conduit
  registration and upgrade only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-04T19:09:49Z
  TYPE: MEASURE
  CLAIM: The grouped lock correction is landed and focused validation still
    passes. The root conduit registry operations in `Aether`
    (`_get_conduit_by_name`, `_get_conduit_by_id`, `_add_conduit`,
    `_remove_conduit`) now resolve the frame under the Aether lock and guard
    the coupled `_conduits` / `_conduit_ids_by_name` operations under the
    frame lock. The same focused validation set still passed `307` tests after
    that correction.
  EVIDENCE:
  - src/melder/aether/aether.py:613-736
  - tests/unit/melder/aether/test_aether.py:1-376
  - command:python -m py_compile src/melder/aether/aether.py tests/unit/melder/aether/test_aether.py
  - command:python -m pytest -q tests/unit/melder/aether/test_aether.py tests/integration/melder/aether/test_aether_integration_registry_ops.py tests/integration/melder/aether/test_aether_integration_error_paths.py tests/integration/melder/conduit/test_conduit_integration_lifecycle.py tests/integration/melder/conduit/test_conduit_integration_public_api.py tests/unit/melder/aether/conduit/test_conduit_dynamic.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/spellbook/spellbook/test_conjure_phase_invocation_counts.py
  IMPACT: The root/normal conduit naming invariant is now both semantically and
    mechanically sound enough to leave in review as the ACL selector
    prerequisite.
  NEXT: get user acceptance on this runtime invariant and continue the ACL
    builder/storage design on top of it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T19:08:56Z
  TYPE: FACT
  CLAIM: The root conduit name invariant still has one correctness gap: the
    grouped frame registry operations (`_get_conduit_by_name`, `_get_conduit_by_id`,
    `_add_conduit`, `_remove_conduit`) are updating or reading the coupled
    `_conduits` and `_conduit_ids_by_name` structures without a shared lock
    boundary. In Python 3.14t the individual dict operations are protected, but
    these are multi-step invariants and should be guarded as grouped state
    transitions.
  EVIDENCE:
  - src/melder/aether/aether.py:613-736
  - user_instruction: "its fine if your just doing a dictionary insert thats threadsafe but make sure your operations are thread safe in general like if your doing a few mutations"
  IMPACT: Without a grouped lock boundary, concurrent readers/writers could
    observe the id map and name map out of sync during add/remove/name lookup.
  NEXT: add frame-level locking around the root conduit registry operations and
    rerun the focused validation set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T18:59:20Z
  TYPE: FACT
  CLAIM: The root conduit name invariant now has the ergonomic default the user
    wanted. Root/normal conduit creation no longer requires every caller to
    spell out a name manually; `SpellbookCreationSystem` now assigns
    `"default"` when `conjure(name=...)` omits a name, and
    `Conduit.upgrade_to_normal(name=...)` now also falls back to `"default"`
    when no name is supplied. The frame-level uniqueness rule still applies, so
    a second unnamed root/normal conduit in the same frame now collides on the
    `"default"` name and fails fast.
  EVIDENCE:
  - src/melder/spellbook/spellbook_creation_system.py:28-60
  - src/melder/spellbook/spellbook_creation_system.py:289-328
  - src/melder/aether/conduit/conduit.py:46-70
  - src/melder/aether/conduit/conduit.py:1249-1308
  - tests/integration/melder/aether/test_aether_integration_error_paths.py:326-355
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:612-629
  - tests/integration/melder/conduit/test_conduit_integration_public_api.py:74-102
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:319-380
  IMPACT: Automatic mode keeps its simple single-root experience, while the
    frame-level name invariant still blocks ambiguous second roots in dynamic
    scenarios. This is a better fit for ACL selector ergonomics than hard
    requiring an explicit name at every root creation call site.
  NEXT: fold the new default-name rule back into the ACL builder/storage design
    and decide whether `"default"` should be treated as a reserved implicit root
    selector in the user-facing ACL API.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T18:52:21Z
  TYPE: MEASURE
  CLAIM: Focused validation for the root conduit name invariant is clean. The
    owning runtime path now enforces a frame-level root/normal conduit name
    index and the touched unit/integration surfaces passed after updating the
    stale unnamed-root expectations. The current focused validation set passed
    `276` tests.
  EVIDENCE:
  - command:python -m py_compile src/melder/aether/aetheric_frame.py src/melder/aether/aether.py tests/unit/melder/aether/test_aether.py tests/integration/melder/aether/test_aether_integration_registry_ops.py tests/integration/melder/aether/test_aether_integration_error_paths.py tests/integration/melder/conduit/test_conduit_integration_lifecycle.py tests/integration/melder/conduit/test_conduit_integration_public_api.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/spellbook/spellbook/test_conjure_phase_invocation_counts.py
  - command:python -m pytest -q tests/unit/melder/aether/test_aether.py tests/integration/melder/aether/test_aether_integration_registry_ops.py tests/integration/melder/aether/test_aether_integration_error_paths.py tests/integration/melder/conduit/test_conduit_integration_lifecycle.py tests/integration/melder/conduit/test_conduit_integration_public_api.py tests/unit/melder/spellbook/test_scan_bind.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/spellbook/spellbook/test_conjure_phase_invocation_counts.py
  IMPACT: The runtime prerequisite for conduit-name ACL selectors is stable
    enough to treat as review-ready instead of speculative.
  NEXT: get user acceptance on the root conduit naming invariant, then fold the
    result back into the ACL builder/storage design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T18:51:39Z
  TYPE: FACT
  CLAIM: The runtime invariant patch is now landed in the owning path. `AethericFrame`
    now carries a `_conduit_ids_by_name` registry, `Aether._add_conduit(...)`
    requires a non-empty root conduit name and rejects duplicate names per
    frame, `Aether._get_conduit_by_name(...)` resolves through the frame-level
    name map instead of scanning root conduits, and
    `Aether._remove_conduit(...)` releases the name mapping during cleanup.
    Focused unit and integration tests were updated to reflect the new root
    conduit contract, including duplicate-name rejection and the fact that
    unnamed root conjure is no longer valid.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:17-92
  - src/melder/aether/aether.py:613-736
  - tests/unit/melder/aether/test_aether.py:39-373
  - tests/integration/melder/aether/test_aether_integration_registry_ops.py:151-214
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:312-370
  IMPACT: Root/normal conduit names are now close to being safe ACL selectors
    at the frame ownership level instead of being only a cloud-level optional
    property.
  NEXT: run focused validation on the touched Aether/conduit/spellbook test
    surfaces and inspect any remaining unnamed root-conduit fallout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T18:44:16Z
  TYPE: FACT
  CLAIM: Current runtime identity rules are not enough for persisted ACL
    selectors. Frame names are stable and unique because `Aether._ensure_frame`
    keys frames by name and reuses existing frames. Root conduit ids are unique
    per frame, but conduit names are only hard-unique inside `ConduitCloud`;
    the main frame conduit registry does not currently enforce name uniqueness,
    and `Aether._get_conduit_by_name(...)` just scans root conduits and returns
    the first match. That is too weak for ACLs that want conduit names as
    stable selectors.
  EVIDENCE:
  - src/melder/aether/aether.py:319-368
  - src/melder/aether/aether.py:613-705
  - src/melder/aether/conduit_cloud.py:74-110
  - src/melder/aether/conduit/conduit.py:783-827
  - src/melder/aether/conduit/conduit.py:1172-1312
  IMPACT: We need a frame-level root/normal conduit name registry and fast-fail
    collision checks in the root add/upgrade/remove paths before conduit names
    are safe ACL selectors.
  NEXT: patch `AethericFrame`/`Aether`/`Conduit` to add the name registry and
    enforce it for root/normal conduits only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to turn root/normal conduit names into a real frame-level
runtime invariant so ACL selectors can rely on conduit names safely.
