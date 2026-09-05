# Task: Preserve resolved disposal order through crystals and replay

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-crystal-replay
- Story: STORY-2026-09-04-ordered-disposal-persistence
- Story Ticket: `tickets/stories/completed/2026-09-04_ordered_disposal_persistence_story.md`
- Epic Ticket: `tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: done
- Completed: 2026-09-05T14:22:02Z
- Summary: Preserved ordered capture and active/staged/fresh/merge replay with actual binding identity joins.
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T14:22:02Z

## Objective
Preserve the final method-list order in SpellCrystal and all existing active/staged
restore and graft paths, using the already established configuration and binding policy.

## Ticket Contract
- ENTRY_GATE: Configuration transport and runtime tasks verified; persistence patch read;
  activate this task on the board before implementation.
- EXECUTION_BOUNDARY: SpellCrystal metadata capture, RestoreEngine active/staged binds,
  GraftRunner selected/parked/merge binds, and targeted round-trip tests.
- DEPENDENCIES:
  `tickets/tasks/completed/2026-09-04_disposal_configuration_roundtrip_task.md`
  `tickets/tasks/completed/2026-09-04_ordered_disposal_creations_task.md`
- EXIT_GATE: Preserved ordered names and policy across supported replay paths, with explicit
  evidence for identity joins and any differing-host case still unresolved.
- FAILURE_ESCALATION: Stop on a real host-policy/recorded-identity conflict; no silent mapping
  fix or assumed historical order. Record the exact case and ask only if a user policy is needed.

## Scope Boundaries
- In scope: existing replay grammar, ordered metadata, and missing disposal forwarding.
- Out of scope: new loader architecture, ownership-transfer policy, broader binding families.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted delivery and requested this closure; completed at 2026-09-05T14:22:02Z.

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
- [x] Capture ordered values in SpellCrystal without sorting and update its property contract.
- [x] Preserve metadata in active replay and forward it in staged replay.
- [x] Forward names for selected, parked, and merged graft members.
- [x] Trace replay of already-resolved names through the new two-group composition rule;
      prove repeated composition under the same recorded config does not change final order.
- [x] Trace grafting into a different host config, including anchor lookups by recorded SHA.
      Record any policy question instead of silently treating old/new IDs as interchangeable.
- [x] Test both priority values, non-alphabetical names, missing/duplicate names, and staged members.
- [x] Reuse the configuration transport task's evidence; do not add duplicate flag fields.
- [x] Record results and outstanding compatibility limits before documentation work.

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
- [x] No hidden replay policy decision for differently configured hosts.
- [x] No config enforcement or disposal execution added to the passive Crystallizer.

## Done Checklist
- [x] Capture/replay changes and focused tests verified.
- [x] Compatibility limits and actual identity joins documented.
- [x] Documentation task unblocked; owner accepts closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false (closed)
- ARTIFACT_PATHS: none active
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: owner-accepted closure 2026-09-05T14:22:02Z
- Durable contracts: source architecture/components, source docstrings, README, configuration guide,
  and committed regression tests. Temporary patches/probes/validation scratch are removed at closure.
- Historical artifact citations in Notes are retained; tracked patches are recoverable from Git history.

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
  - `context_compass/tickets/tasks/completed/2026-09-04_disposal_configuration_roundtrip_task.md`
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_creations_task.md`
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
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md`
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

- DATETIME: 2026-09-05T11:56:36Z
  TYPE: FACT
  CLAIM: All three replay files are read completely. Restore reloads/finalizes configuration
    before active binds, then conjures, stages, and enforces selection. Active bind maps index
    ULIDs but not changed Spell SHAs; staged bind omits names; anchor, selection, and contract
    detail paths still consume recorded Spell IDs. RestoreReport already owns a locked identity map.
  EVIDENCE:
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1822`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1903-2095`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:2360-2450`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:250-290`
  IMPACT: Record changed Spell IDs in the existing translation map; unchanged IDs remain direct.
    Translate replay references, resolving exact owned staged members for selection. Graft can pass
    its newly bound anchor index directly and retain only the selected bind_inactive result for adoption.
    No new runtime registry/lock or global identity mutation is needed. Older sorted records cannot
    recover lost original order; receiving-book composition remains authoritative at each new bind.
  NEXT: Author the replay patch contract and add real capture, staged restore, and fresh/merge graft tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:56:36Z
  TYPE: PLAN
  CLAIM: Replay patch contracts are written. Mapping: ordered crystal values -> capture/JSON
    tests; all bind forwarding -> active/staged/fresh/merge tests; returned anchor/selected IDs
    -> changed-host graft tests; report translation -> changed-ID anchor/selection/grant tests.
    Existing process-wide unique-spell xfails remain out of scope; use released source worlds
    and many bindings for independent replay tests rather than weakening that restriction.
  EVIDENCE:
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_crystal_replay.md:1-37`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_crystal_replay.md:1-30`
  IMPACT: Three source files suffice; no recorder orchestration or new matching family.
  NEXT: Add focused desired-behavior regressions and establish the red baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:07:54Z
  TYPE: MEASURE
  CLAIM: The new 20-case replay suite ran outside the sandbox after pytest temp ACL failures.
    All 20 fail on unchanged source: capture order differs, fresh graft loses its anchor,
    and merge binds collide because omitted names erase the distinct member fingerprints.
    Six restore cases also reveal a fixture/world-record setup issue (missing book payload),
    which is not yet classified as a production defect and must be resolved separately.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/integration/melder/crystallizer/test_ordered_disposal_replay.py -q -p no:cacheprovider --tb=line --basetemp=context_compass/artifacts/ordered_disposal_validation_20260905/red3
  - Result: 20 failed in 58.03s. Earlier sandbox attempts failed before test execution.
  IMPACT: Capture/graft regressions evidence the planned correction. Do not broaden the source
    fix to explain a test setup issue or count unavailable fixture runs as a feature baseline.
  NEXT: Apply the three-file replay correction, then isolate the cached-world setup and rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:07:54Z
  TYPE: FACT
  CLAIM: Three-file replay implementation is present; capture and merge paths now pass.
    New tests inherited configure_aether_frame from a runtime-only helper, which freezes/locks
    rich configuration before _conjure_dynamic_hint exists. Conjure then skips the freeze
    emission, so the checkpoint lacks a book twin. This is an existing separate API ordering
    defect, not caused by disposal capture. Use the suite's recorded-world configuration setup
    for this feature and preserve the finding for follow-up. Fresh graft's initial name lookup
    also fails before notch; exact binding IDs are used to test the replay identity contract.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:6164-6221`
  - `src/melder/aether/spellbook/spellbook_creation_system.py:290-316`
  - `src/melder/aether/spellbook/spellbook.py:5709-5774`
  - `tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:143-158`
  - Result after replay source edits: 10 passed, 10 failed in 68.10s (green1).
  IMPACT: No unrelated configuration-emission or Meld name-registry fix is added. Correct
    test setup and failure teardown without weakening order, identity, or actual-cleanup assertions.
  NEXT: Rerun the complete focused replay suite with recorded-world setup and exact binding IDs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:20:00Z
  TYPE: MEASURE
  CLAIM: Capture, cached restore on both drivers, and changed-ID restore/selection cases pass
    (8 cases). Twelve graft cases reach teardown but the test tried retiring parked metadata
    after permanent conduit cleanup had already destroyed the index. Corrected the test to retire
    inactive members first, then permanently clean the conduit and assert actual method order.
  EVIDENCE:
  - `tests/integration/melder/crystallizer/test_ordered_disposal_replay.py`
  - Green3 result: 12 failed, 8 passed in 81.50s; failures are post-clean index reads in test teardown.
  IMPACT: No production cleanup or synchronization modification is justified by this test mistake.
  NEXT: Verify one fresh graft, then run the focused and surrounding replay suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:26:00Z
  TYPE: MEASURE
  CLAIM: All 23 focused replay cases pass in 90.25s on Windows 3.14t outside the sandbox.
    Covers ordered crystal/JSON capture, cached restore under sequential and parallel drivers,
    active/staged actual disposal, same/changed-host fresh/merge/adopt grafts, skipped resident
    selection honesty, changed-ID anchors/exact selection, and translated contract grants.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/integration/melder/crystallizer/test_ordered_disposal_replay.py -q -p no:cacheprovider --tb=short --basetemp=context_compass/artifacts/ordered_disposal_validation_20260905/focused_final
  - Result: 23 passed in 90.25s, exit 0.
  - `tests/integration/melder/crystallizer/test_ordered_disposal_replay.py`
  IMPACT: Corrected test teardown preserves all behavioral assertions. Existing legacy-link
    fixture uses sha-x/sha-z placeholders; its complete function was read and its exact report-key
    assertion now includes their actual bind translations, while still forbidding a contract key.
  NEXT: Run the surrounding Crystallizer suites, then promote docs and regenerate final assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T12:35:01Z
  TYPE: MEASURE
  CLAIM: The complete Crystallizer unit/component/integration ring passes 864 tests with
    3 existing xfails in 207.56s. All 23 new replay cases are included; no skip/xfail was added.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/crystallizer tests/component/melder/crystallizer tests/integration/melder/crystallizer -q -p no:cacheprovider --tb=short --basetemp=context_compass/artifacts/ordered_disposal_validation_20260905/crystal_suite
  - Result: 864 passed, 3 xfailed in 207.56s, exit 0.
  IMPACT: Replay is implemented/in review. Source docstrings and scoped diff checking are current;
    canonical/public docs and generated assets remain. Do not remove unrelated unique-copy xfails.
  NEXT: Complete docs/assets, then final verification and owner acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T14:22:02Z
  TYPE: DECISION
  CLAIM: Owner accepted this deliverable and requested closure of the ordered-disposal program.
    Preserved ordered capture and active/staged/fresh/merge replay with actual binding identity joins.
  EVIDENCE: tickets/tasks/completed/2026-09-04_ordered_disposal_end_to_end_validation_task.md
  IMPACT: Ticket history is retained under completed. Registered temporary artifacts are disposed
    at accepted closure; durable behavior is in canonical docs, examples, source, and regression tests.
    Linux/hosted checks and unrelated recording/name-lookup findings retain their documented scope.
  NEXT: none; this work item is closed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED: 2026-09-05T14:22:02Z. Preserved ordered capture and active/staged/fresh/merge replay with actual binding identity joins.
Program record: tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md
No active work remains in this ticket. Prior handoff text below is historical.

### Historical handoff at closure
Replay is implemented/in review: 864 passed and 3 pre-existing xfails. All three source files were read fully
before editing: SpellCrystal 1,162 lines; RestoreEngine 2,669; GraftRunner 645 (pre-edit sizes).
Capture preserves order; staged/park/merge paths forward names; graft carries the new index/selected
ID; RestoreReport maps changed SHAs and anchor/selection/grant lookups translate through it.
The new 23-case matrix passes capture/cache/changed-ID/graft/adoption/grant checks and actual cleanup.
Test setup/teardown mistakes were corrected without changing runtime cleanup or synchronization.
Use elevated pytest with a fresh --basetemp under artifacts/ordered_disposal_validation_20260905;
sandbox-created pytest directories hit WinError 5. Do not weaken or skip tests for this ACL issue.
Two unrelated findings are recorded above: pre-conjure configure_aether_frame suppresses book-twin
emission, and fresh graft name lookup fails before notch. Neither is patched in this epic.
Documentation/assets and final CI runtime verification are complete; see the final validation task.
Remaining: owner acceptance and ticket/temporary-artifact closure.
Owner approved the entire remaining epic; no further policy choice, commit, or push is required/authorized.
