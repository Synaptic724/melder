# Task: Preserve resolved disposal order through crystals and replay

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-crystal-replay
- Story: STORY-2026-09-04-ordered-disposal-persistence
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_persistence_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: in_progress
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T11:49:24Z

## Objective
Preserve the final method-list order in SpellCrystal and all existing active/staged
restore and graft paths, using the already established configuration and binding policy.

## Ticket Contract
- ENTRY_GATE: Configuration transport and runtime tasks verified; persistence patch read;
  activate this task on the board before implementation.
- EXECUTION_BOUNDARY: SpellCrystal metadata capture, RestoreEngine active/staged binds,
  GraftRunner selected/parked/merge binds, and targeted round-trip tests.
- DEPENDENCIES:
  `tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md`
  `tickets/tasks/2026-09-04_ordered_disposal_creations_task.md`
- EXIT_GATE: Preserved ordered names and policy across supported replay paths, with explicit
  evidence for identity joins and any differing-host case still unresolved.
- FAILURE_ESCALATION: Stop on a real host-policy/recorded-identity conflict; no silent mapping
  fix or assumed historical order. Record the exact case and ask only if a user policy is needed.

## Scope Boundaries
- In scope: existing replay grammar, ordered metadata, and missing disposal forwarding.
- Out of scope: new loader architecture, ownership-transfer policy, broader binding families.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner requested implementation of all remaining replay, docs/assets, and
  final verification pieces. Preserve existing policy, public verbs, and unrelated actor changes.

## Required Reading and Evidence
Navigate the Crystallizer component and graph rows, then read implementations in full before edits.
- `src/melder/crystallizer/crystals/spell_crystal.py:143-339` (sorted capture)
- `src/melder/crystallizer/crystals/spell_crystal.py:644-661` (property)
- `src/melder/crystallizer/crystals/spell_crystal.py:1064-1138` (describe entry)
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1822` (config before binds)
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1903-2002` (active/staged)
- `src/melder/crystallizer/crystal_loader_system/graft_runner.py:371-530` (selected/parked/merge)
- Source/test continuations for selection mapping must be read before assuming SHA stability.

## Steps / Checklist
- [ ] Capture ordered values in SpellCrystal without sorting and update its property contract.
- [ ] Preserve metadata in active replay and forward it in staged replay.
- [ ] Forward names for selected, parked, and merged graft members.
- [ ] Trace replay of already-resolved names through the new two-group composition rule;
      prove repeated composition under the same recorded config does not change final order.
- [ ] Trace grafting into a different host config, including anchor lookups by recorded SHA.
      Record any policy question instead of silently treating old/new IDs as interchangeable.
- [ ] Test both priority values, non-alphabetical names, missing/duplicate names, and staged members.
- [ ] Reuse the configuration transport task's evidence; do not add duplicate flag fields.
- [ ] Record results and outstanding compatibility limits before documentation work.

## Deliverables
Order-preserving crystal capture/replay and source-backed identity/selection behavior.

## Files / Paths Impacted
- `src/melder/crystallizer/crystals/spell_crystal.py`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
- `src/melder/crystallizer/crystal_loader_system/graft_runner.py`
- `tests/unit/melder/crystallizer/persistence/test_restore_engine.py`
- Relevant existing graft tests located through the test index.
- `tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py`
- Focused test additions within the existing Crystallizer hierarchy when necessary.

## Validation
- Diagnostic run: two current-behavior cases pass, proving the same/different-host discrepancy.
  This is a reproduced defect, not successful desired replay validation.
- Persistence source edits and full replay tests: Not run/pending the owner policy decision.
- Same recorded configuration -> same final ordered methods and appropriate new-world identities.
- Exercise both active and inactive members and all selected/parked/merge forwarding paths.
- Verify resulting cleanup calls, not only persisted list equality.
- Distinguish configuration-flag round trips from complete restored-instance disposal.

## Risks / Rollback Notes
Old SpellCrystal records sorted the names, and old frozenset fingerprints could vary with
hash seed. Do not promise recovery of lost original order. Treat legacy compatibility as
an evidenced data question, not a reason for an invented fallback or blanket ID rewrite.

## Applicable Anti-Patterns
- [ ] No hidden replay policy decision for differently configured hosts.
- [ ] No config enforcement or disposal execution added to the passive Crystallizer.

## Done Checklist
- [ ] Capture/replay changes and focused tests verified.
- [ ] Compatibility limits and actual identity joins documented.
- [ ] Documentation task unblocked; owner accepts closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `artifacts/2026-09-05_disposal_graft_policy_probe.py`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: accepted closure; replace diagnostic expectations with approved regression behavior first

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: recorded configuration, final names, replay identities, graft
- IF_UNKNOWN: none

## Noting Behavior
Record exact payload/host conditions and identity evidence before choosing a replay correction.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: SpellCrystal sorts names, while staged restore and parked/merge graft omit disposal args.
  EVIDENCE:
  - `src/melder/crystallizer/crystals/spell_crystal.py:273-284`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1945-2002`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:421-530`
  IMPACT: Producer order alone cannot establish the complete recorded-world contract.
  NEXT: Read the persistence patch and complete capture/replay implementations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:01:28Z
  TYPE: FACT
  CLAIM: Current source confirms sorted SpellCrystal capture and direct ordered output of
    that stored list. Active restore and selected graft forward recorded names, but staged
    restore, parked graft, and merged graft omit them. Restore maps new index ULIDs yet
    resolves members/selections using recorded Spell SHA values. Fresh graft finds the
    selected result by new SHA initially, then parks siblings using the recorded selected SHA;
    merge adoption also looks up the recorded SHA.
  EVIDENCE:
  - `src/melder/crystallizer/crystals/spell_crystal.py:143-339`
  - `src/melder/crystallizer/crystals/spell_crystal.py:644-661`
  - `src/melder/crystallizer/crystals/spell_crystal.py:1064-1162`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1820`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1903-2095`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:226-326`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:371-554`
  IMPACT: Order is an identity/replay join concern as well as cleanup behavior. Same-policy
    replay must prove that reapplying book names to a recorded resolved list is idempotent.
    A different host's names/priority can change the resolved list and therefore its SHA;
    the recorded-ID joins above must be tested before choosing any fix. No silent ID
    translation or host-policy override is authorized by this read. Old sorted records
    cannot reveal their original supplied order. The graph/component fresh-index-only
    wording is stale: current GraftRunner also has an explicit public-verb merge mode.
  NEXT: After producer changes, reproduce same-policy and differing-host replay cases,
    preserving current public-verb admission and treating actual policy conflicts explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:54:45Z
  TYPE: PLAN
  CLAIM: Begin ordered capture/replay after 2,797 runtime checks and 59 configuration
    transport/default checks. Current source sizes are SpellCrystal 1,162 lines, RestoreEngine
    2,669, and GraftRunner 645. Same-policy and differing-host identity behavior require direct proof.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_creations_task.md`
  IMPACT: No persistent identity-policy change is implied by the completed runtime work.
  NEXT: Read the capture/replay implementations and existing real restore/graft setup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:54:45Z
  TYPE: FACT
  CLAIM: Full GraftRunner read confirms an identity seam: selected bind resolves its returned
    new SHA, but subsequent parking searches by recorded selected SHA. Merge adoption likewise
    searches the recorded SHA. Host configuration may change resolved disposal order at bind,
    making those identities different. Same-policy versus changed-host behavior must be reproduced
    before choosing a mapping or policy override. No persistence source has been edited.
  EVIDENCE:
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:226-326`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:371-554`
  IMPACT: This is the task's explicit policy/identity escalation boundary, not a missing None guard.
  NEXT: Run a minimal real Bind/GraftRunner diagnostic isolating host-policy changes from capture sorting.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:08:48Z
  TYPE: MEASURE
  CLAIM: Real Bind/GraftRunner diagnostic isolates target policy from capture sorting.
    Same policy [close, flush] preserves SHA and grafts one selected plus one parked member.
    Target book [flush, close] with priority=True changes the selected SHA, binds that member,
    then skips its sibling with anchor_index_unresolvable_member_skipped. No persistence source
    was changed. Both diagnostic assertions passed because they describe current behavior only.
  EVIDENCE:
  - `context_compass/artifacts/2026-09-05_disposal_graft_policy_probe.py:18-88`
  - Command: .venv_new/Scripts/python.exe -m pytest -o pythonpath=src context_compass/artifacts/2026-09-05_disposal_graft_policy_probe.py -q -s -p no:cacheprovider --tb=short
  - Result: 2 passed in 0.30s; matching host bound=1/parked=1/no shortfalls;
    changed host bound=1/parked=0/anchor_index_unresolvable_member_skipped.
  - GraftRunner complete-read SHA256: e675056c3297eb0e3b203a83d430075b223348571831d8a24a54bfdd14741cf6.
  IMPACT: The task's explicit host-policy/identity escalation gate is reached.
  NEXT: Owner decides whether target book policy wins and graft follows returned live spell IDs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:08:48Z
  TYPE: DECISION_REQUEST
  CLAIM: Recommend honoring receiving-book policy (normal bind semantics) and carrying the
    resulting live identity through fresh-graft parking and merge-selection adoption. Do not
    force recorded SHAs onto differently configured Spells or silently override host policy.
  EVIDENCE:
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:371-554`
  - `context_compass/artifacts/2026-09-05_disposal_graft_policy_probe.py:18-88`
  IMPACT: Requires the owner decision mandated by this task before ID mapping is implemented.
  NEXT: Await owner approval of target-policy/new-ID behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:08:48Z
  TYPE: UNKNOWN
  CLAIM: codex_2 reports a separate prebuilt AppConfig instance DI failure at plan_group
    (not callable), using class bindings as the verified capstone path. Not investigated here.
  EVIDENCE:
  - Incoming notice from codex_2, citing artifacts/2026-09-05_beginner_capstone_revision.md:28-40.
  IMPACT: Preserve this reported issue for later assessment; do not fold it into disposal/graft work.
  NEXT: Keep the current lane on the reproduced graft policy decision.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-05T11:37:10Z
  TYPE: DECISION
  CLAIM: Owner clarified book authority and requested implementation: shared names belong
    to the book block regardless of placement; False places it last, True first. The producer
    prerequisite is corrected and 2,807 selected tests pass, including same-policy order/SHA
    idempotence. Receiving-book policy must not be bypassed to preserve a recorded ordering.
  EVIDENCE:
  - Owner clarification and implementation approval, active conversation, 2026-09-05.
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  IMPACT: Policy is settled; this task can resume scoped public-verb replay and follow the live
    binding identities it creates. No global ID mutation or per-Meld compatibility path is added.
  NEXT: Read complete SpellCrystal/RestoreEngine/GraftRunner source and author replay contracts
    before implementing ordered capture, all forwarding paths, and local anchor/adoption joins.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:49:24Z
  TYPE: PLAN
  CLAIM: Owner explicitly requested remaining pieces. Begin three-file crystal/replay work,
    then docs/assets and final verification. Current sizes are SpellCrystal 1,162 lines,
    RestoreEngine 2,669, and GraftRunner 645. Other agents have active workflow/docs/assets changes.
  EVIDENCE:
  - Owner instruction, active conversation, 2026-09-05.
  - `context_compass/attention_board.md`
  IMPACT: All edits stay within the epic; no commit/push or unrelated cleanup. Coordination
    notices sent to codex_2 and workflows_1 before making generated proofs stale.
  NEXT: Read the three implementations completely, record the exact replay correction, and stage tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:49:24Z
  TYPE: FACT
  CLAIM: Complete GraftRunner and SpellCrystal reads confirm the focused correction. Crystal
    capture sorts the live names; its existing serialization boundary already copies values.
    Fresh graft obtains the new selected SHA but parks by the old one. Merge ignores bind_inactive's
    result then looks up the recorded SHA for adoption. Park/merge also omit disposal arguments.
  EVIDENCE:
  - `src/melder/crystallizer/crystals/spell_crystal.py:143-339`
  - `src/melder/crystallizer/crystals/spell_crystal.py:644-661`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:226-554`
  IMPACT: Use existing ordered value capture and local returned identities, not a global alias
    registry, private index mutation, or new resolution check. Preserve public per-verb admission.
  NEXT: Complete RestoreEngine reading to settle active/staged identity and selection joins.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
READY after receiving-book ordering approval and the verified overlap correction. No persistence source edits.
Configuration transport is verified separately (59 tests). Full GraftRunner was read and its SHA
is recorded above. SpellCrystal/RestoreEngine still require complete reads before their edits.
The temporary 88-line diagnostic uses real source binds and GraftRunner with recorded-value inputs,
deliberately excluding capture sorting. Same host policy succeeds; changed host policy creates a new
SHA and causes sibling parking to skip on the old-ID lookup. Its passing assertions describe the bug.
Recommendation: target policy wins; follow live IDs returned by bind/park for anchors and adoption.
Next: author persistence contracts, implement capture/order forwarding and local live-binding joins,
replace the diagnostic with desired-behavior regressions, then validate replay and regenerate docs/assets.
