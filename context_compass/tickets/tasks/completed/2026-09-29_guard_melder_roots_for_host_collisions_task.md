

# Task: Make Melder's root configuration honest and guarded for hosts (M1-M4)

## Metadata
- Task ID: TASK-2026-09-29-guard-melder-roots-for-host-collisions
- Parent epic (MelderOps repository):
  priv_commandops:context_compass/tickets/epics/completed/2026-09-29_melder_host_configuration_collisions_epic_completed.md
- Source investigation: tickets/tasks/completed/2026-09-29_investigate_melderops_root_configuration_collisions_task.md
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-29T23:39:29Z
- Updated: 2026-09-30T15:40:12Z
- Completed: 2026-09-30T15:40:12Z
- Closure Basis: owner turn-in in chat (2026-09-30) of every finished lane: "yeah turn in the [lanes] you
  finished please, go ahead".
- Summary: Melder's root configuration is honest and guarded for hosts. M1 (0.2.8209): while frames exist
  Aether refuses a spell-id regime other than the one its first frame sealed. M2 (0.2.8210): an active Nexus
  refuses another configuration; restore stage 4 deactivates it first. M3 (0.2.8211): a refused recorded-world
  dynamic conjure leaves its frame unsettled. M4 (0.2.8212): get_configuration_dictionary() on the four root
  configurations. Notched 0.2.8209-0.2.8212, one per change; release-note sections "Aether refuses a spell-id
  regime it cannot apply", "A live Nexus keeps its policy", "Fixed: a refused dynamic conjure no longer settles
  its frame dynamic", "Compare root configurations by value" and a Packaging bullet; docs, graph, assets, LLM
  bundles and the verified 0.2.8212 wheel are current.

## Objective
Owner directive (chat, 2026-09-29): "implement all the fixes". The Melder half of the fix list from the
investigation's DECISION_REQUEST note:
- M1: while any frame exists the spell-id regime is sealed; `Aether.configure` / `Aether.activate` refuse a
  configuration whose `process_wide_unique_spell_ids` differs from it, so `Aether.configuration` can no longer
  report a regime that is not in force. The restore engine reports a sealed-regime mismatch as a shortfall
  instead of installing the recorded root configuration.
- M2: `Nexus.configure`, and `Nexus.activate(configuration)` with a different object, refuse while Nexus is
  active - the guard Crystallizer and MutationResearch already have.
- M3: a dynamic conjure refused by the active-Crystallizer configuration discipline is refused BEFORE the frame
  posture is settled, so the refusal leaves the frame as it was.
- M4: the four root configurations (Aether, Crystallizer, MutationResearch, Nexus) expose
  `get_configuration_dictionary()`, a snapshot of their property values, so a host can compare policies
  without private access (MelderOps already calls this name).

## Ticket Contract
- ENTRY_GATE: owner directive in chat; board row; patch docs under
  system_docs/patches/active/root_configuration_guards_2026_09_29/.
- EXECUTION_BOUNDARY: src/melder/aether/aether.py, src/melder/aether/aether_configuration.py,
  src/melder/crystallizer/configuration/crystallizer_configuration.py,
  src/melder/mutation_research/mutation_configuration.py, src/melder/nexus/configuration/nexus_configuration.py,
  src/melder/nexus/nexus.py, src/melder/aether/spellbook/spellbook.py,
  src/melder/crystallizer/crystal_loader_system/restore_engine.py; new tests; system docs, release note,
  version, build assets and LLM bundles.
- DEPENDENCIES: none inside Melder. The MelderOps half (F1-F6) consumes M1 and M4 through a new wheel.
- EXIT_GATE: each fix red-then-green under a test, the touched suites pass on 3.14t, docs and release note
  carry the changes, notched, assets and bundles rebuilt and checked, wheel built for MelderOps.
- FAILURE_ESCALATION: DECISION_REQUEST if an existing test pins the old behaviour for a reason beyond the
  collision (it is not rewritten silently).

## Scope Boundaries
- In scope: M1-M4 as stated.
- Out of scope: other failures after conjure settlement (validation errors, bad policy strings) - they still
  settle the frame, as today; Crystallizer late-activation catch-up (no world walk, by design); MelderOps code.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directive (chat, 2026-09-29) to implement all fixes from the investigation.
- from_state: in_progress
- to_state: review
- transition_reason: M1-M4 landed, notched 0.2.8212, documented, assets and LLM bundles rebuilt and checked,
  wheel verified and installed in MelderOps' environments (2026-09-30T10:43:20Z); awaiting the owner's acceptance.
- from_state: review
- to_state: done
- transition_reason: (2026-09-30T15:40:12Z) owner turn-in in chat; M1-M4 accepted as landed, patch docs archived.

## Steps / Checklist
- [x] Patch docs (architecture, per-component, conjure control flow) and read-order mapping note.
- [x] M4 get_configuration_dictionary on the four root configurations + tests.
- [x] M1 Aether sealed-regime guard (configure, activate) + tests; restore-engine change withdrawn (dead code).
- [x] M2 Nexus active guard (configure, activate with another configuration) + tests; restore stage 4.
- [x] M3 pre-settlement Crystallizer discipline refusal in conjure + tests.
- [x] Touched suites green; red-then-green evidence recorded.
- [x] Notch (one per change), release note sections, system docs, graph descriptors where wiring changed.
- [x] Build assets and LLM bundles rebuilt last and checked; wheel built for MelderOps.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Source and tests for M1-M4; docs; release note; notch; assets; wheel. Evidence under
  artifacts/root_configuration_guards_20260929/.

## Validation
- Run (device VM copy of the tree, CPython 3.14.7t, PYTHON_GIL=0): red-then-green per fix (m1/m2/m3/m4 logs);
  full suite 13281 passed, 0 failed (full_suite_landed.log); the six new files also pass with PYTHON_GIL=1.
- Run: asset --check and LLM --check (--include-untracked) OK on the device; verify_wheel and the CI smoke
  script OK for dist/melder-0.2.8212-py3-none-any.whl.
- Not run: docs tests needing sphinx (absent in the VM venv). Coverage: Not run.

## Risks / Rollback Notes
- M1 refuses a call that used to succeed (installing a different regime after the first frame). Callers that
  relied on it were already getting a regime that was not in force; the refusal message names the fix.
- M2 refuses reconfiguring a live Nexus; tests that re-activate with another configuration may need a
  deactivate first. Rollback: revert the guard.

## Applicable Anti-Patterns
- [x] No behaviour claim from a document or a search hit; read the code.
- [x] No blanket defensive guards: each guard closes an evidenced collision.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/root_configuration_guards_20260929/
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs: promoted at landing,
  archived to system_docs/patches/completed/ at turn-in)
- CLEANUP_TRIGGER: task closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-29T23:39:29Z
  TYPE: PLAN
  CLAIM: Order: patch docs; M4 (pure addition, unblocks MelderOps F1); M1 (Aether guard plus the restore stage-1
    shortfall, because stage 1 installs a recorded root configuration whenever `configured` is False, which is
    also true of the default Aether policy the first frame seals); M2; M3 (hoist the discipline check out of
    `_conjure_within_transaction_window` into `conjure` ahead of `_settle_or_inherit_conjure_mode`, using the mode
    settlement would produce). Tests run in a VM copy of the tree on 3.14t. One notch per change at landing
    (0.2.8209-0.2.8212), then docs, release note, assets, bundles, wheel.
  EVIDENCE:
  - src/melder/aether/aether.py:972-1073
  - src/melder/aether/aether.py:2474-2533
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1340-1394
  - src/melder/nexus/nexus.py:803-910
  - src/melder/aether/spellbook/spellbook.py:6502-6620
  - src/melder/aether/spellbook/spellbook.py:6877-6935
  IMPACT: Fixes land in dependency order and MelderOps can adopt M1/M4 from one wheel.
  NEXT: Write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T23:44:09Z
  TYPE: DECISION
  CLAIM: Patch docs written and read in order (architecture, then the five component/code patches). Mapping, patch
    section -> implementation -> validation: root configurations value snapshot -> get_configuration_dictionary on
    the four configuration classes -> snapshot/independence/equality/cleaned tests; Aether sealed regime -> guard in
    configure and activate under the Aether lock -> mismatch after a frame raises, before a frame installs, mutated
    installed configuration refused at activate; RestoreEngine stage 1 -> pre-check with list_frame_names and the
    installed regime -> shortfall recorded, no raise; Nexus -> guard in configure and activate(configuration) ->
    active refuses, deactivated accepts, same object passes; conjure -> _effective_conjure_mode plus the moved
    refusal ahead of settlement -> posture unchanged after refusal, helper agrees with settlement.
  EVIDENCE:
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/architecture_patch.md:1-58
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/component_patch_root_configurations.md:1-24
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/component_patch_aether_singleton.md:1-41
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/component_patch_crystallizer_restore.md:1-24
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/component_patch_nexus_root.md:1-24
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/component_patch_spellbook_conjure.md:1-26
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/code_description_patch_spellbook_conjure.md:1-29
  IMPACT: Entry gate met; implementation follows the migration order.
  NEXT: Implement M4 and its tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T23:49:41Z
  TYPE: MEASURE
  CLAIM: M4 landed in the tree: `get_configuration_dictionary()` on AetherConfiguration, CrystallizerConfiguration,
    MutationResearchConfiguration and NexusConfiguration returns `dict(self._properties)` under the configuration
    lock after check_cleaned (applied by a script; the device files are CRLF and stay CRLF). New unit tests (22,
    parametrized over the four classes): 22 fail on the 0.2.8208 source with the methods stripped (AttributeError),
    22 pass with the change. Test runs use a VM copy of the tree because each device shell call is a fresh sandbox
    (background jobs die with the call), so suites run in slices under the call limit.
  EVIDENCE:
  - artifacts/root_configuration_guards_20260929/apply_m4_value_snapshots.py:1-69
  - artifacts/root_configuration_guards_20260929/m4_red_green.log:1-8
  - tests/unit/melder/aether/test_root_configuration_value_snapshots.py:1-197
  IMPACT: MelderOps' existing values() comparison becomes valid once it runs on this Melder.
  NEXT: M1 - the sealed-regime guard in Aether.configure/activate and the restore stage-1 shortfall.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T23:55:15Z
  TYPE: FACT
  CLAIM: The Aether twin never records the spell-id regime: AetherConfiguration's recording emits only
    channel_logger_activation_enabled and two presence flags, and from_recorded_payload rebuilds the default regime
    (True). Consequences: (a) restore stage 1 can never meet a regime mismatch - a live Aether it may configure
    (`configured` False) has sealed the same default - so the stage-1 pre-check planned for M1 is dead code and was
    removed again (restore_engine.py unchanged); (b) separate pre-existing gap, NOT fixed in this lane: a world
    recorded under per-frame spell ids restores under process-wide ids.
  EVIDENCE:
  - src/melder/aether/aether_configuration.py:872-920
  - src/melder/aether/aether_configuration.py:421-485
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1339-1394
  - artifacts/root_configuration_guards_20260929/revert_m1_restore_stage1.py:1-45
  IMPACT: M1 stays inside aether.py; (b) goes to the owner as a follow-up candidate.
  NEXT: Record the M1 red/green measure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T23:55:15Z
  TYPE: MEASURE
  CLAIM: M1 landed in aether.py: `_refuse_regime_change_while_frames_exist` (RuntimeError naming sealed and requested
    values and the remedy) runs under the Aether lock in `configure` before install and in `activate` before
    validate; the collapse docstring notes it. New component tests (6): 4 fail on the pre-M1 source (no refusal),
    all 6 pass with it; the new restore non-regression test passes on both (a checkpoint restored into a live world
    whose first frame sealed the regime completes, and stage 1 installs the recorded root configuration).
  EVIDENCE:
  - src/melder/aether/aether.py:972-1120
  - artifacts/root_configuration_guards_20260929/apply_m1_sealed_regime.py:1-253
  - artifacts/root_configuration_guards_20260929/m1_red_green.log:1-9
  - tests/component/melder/aether/test_aether_sealed_regime_guard_component.py:1-121
  - tests/integration/melder/crystallizer/test_restore_sealed_aether_regime_integration.py:1-121
  IMPACT: Aether.configuration now always reports the regime in force while frames exist.
  NEXT: M2 - the Nexus active guard.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T00:05:08Z
  TYPE: DECISION
  CLAIM: M2 is applied in nexus.py by apply_m2_nexus_active_guard.py, which ran right after a context compaction and
    BEFORE re-onboarding (disclosed in the REONBOARD attestation): configure raises RuntimeError("Cannot reconfigure
    Nexus while it is active. Deactivate it first.") under the Nexus lock while active; activate(configuration) raises
    the same while active when handed another object; activate(), activate(installed) and a deactivated Nexus behave
    as before. It matches component_patch_nexus_root.md. The only src caller of either verb is restore stage 4
    (_replay_nexus), which calls activate(<fresh reloaded configuration>) on the hosted Nexus: under M2 a world-scope
    load into a world whose Nexus is active would raise and roll the whole restore back. Stage 3 already meets the
    same refusal from MutationResearch by deactivating first ("a truthful recorded act"). Decision: stage 4 mirrors
    stage 3 - deactivate an active Nexus, then activate the reloaded configuration. restore_engine.py stage 4 joins
    this lane (NOTICE sent); the Crystallizer-restore and Nexus patch docs are updated.
  EVIDENCE:
  - src/melder/nexus/nexus.py:803-928
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1416-1507
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1509-1567
  - artifacts/root_configuration_guards_20260929/apply_m2_nexus_active_guard.py:1-134
  IMPACT: Without the stage-4 change M2 breaks live-world restores that carry a Nexus twin while the host's Nexus is
    active; with it, the restore replaces the Nexus policy through honest verbs, as it did silently before.
  NEXT: Apply the stage-4 change, then write the M2 tests (component guard; integration restore over an active Nexus).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T00:12:16Z
  TYPE: MEASURE
  CLAIM: M2 red/green. Stage 4 applied (apply_m2_restore_stage4.py): _replay_nexus deactivates an active Nexus before
    activating the reloaded configuration. New tests: 7 component (guard) + 2 integration (restore over an active
    Nexus, recorded enabled and recorded disabled). On the 0.2.8208 behaviour 4 component tests fail (the refusals),
    the integration pair passes (silent replace); with the guard but without stage 4 the integration pair fails
    (restore torn down, chained from "Cannot reconfigure Nexus while it is active"); landed: 9 pass. Suites on the
    landed tree: the 57 test files that call configure/activate near Nexus - 1166 pass, 2 fail; the remaining 150
    files of the lane selection - 2027 pass. The 2 failures are in tests/unit/melder/aether/test_nexus.py and use a
    live-Nexus swap as SETUP, not as the contract under test: test_target_frame_allow_and_deny_lists_are_enforced
    re-activates with a replacement policy under a live Rift to reach its allowed case, and
    test_shared_and_private_nexus_frames_are_realized_only_on_request re-activates the singleton (named
    "isolated_nexus") with one_per_workspace mode while the shared Rift lives. Decision (the ticket's Risks line
    foresaw it): insert nexus.deactivate() before each re-activation with a comment; what they assert is unchanged.
  EVIDENCE:
  - artifacts/root_configuration_guards_20260929/apply_m2_restore_stage4.py:1-64
  - artifacts/root_configuration_guards_20260929/red_m2_variants.py:1-50
  - artifacts/root_configuration_guards_20260929/m2_red_green.log:1-14
  - tests/component/melder/aether/test_nexus_active_reconfiguration_guard_component.py:1-160
  - tests/integration/melder/crystallizer/test_restore_over_active_nexus_integration.py:1-136
  - tests/unit/melder/aether/test_nexus.py:5749-5785
  - tests/unit/melder/aether/test_nexus.py:5950-5979
  IMPACT: M2 is proven; two setup steps that relied on the removed behaviour move to the documented remedy.
  NEXT: Insert the two deactivate() calls in test_nexus.py (its mixed line endings preserved), re-run it.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T00:19:06Z
  TYPE: MEASURE
  CLAIM: test_nexus.py re-run after the two deactivate() insertions (mixed endings kept: 6366 CRLF of 6377): 157 pass.
    M3 landed in spellbook.py (apply_m3_conjure_refusal_order.py): pure _effective_conjure_mode (mirrors settlement
    branch for branch) and _refuse_recorded_conjure_after_mutable_binds (the discipline check, message and log line
    unchanged, its comment moved with it). conjure() calls it on the predicted mode inside the transaction try, before
    _settle_or_inherit_conjure_mode. DECISION, a deviation from the code-description patch (patch updated): the
    window keeps the same check through the helper on the SETTLED mode instead of dropping it, because another Book
    in the same frame can settle the shared posture between prediction and settlement (Books are separate
    transaction identities) - a stale "automatic" prediction must not let a dynamic conjure through. New component
    tests (11): pre-M3 tree 10 fail (posture frozen after the refusal; the automatic retry refused; 8 prediction
    rows AttributeError), the settled-dynamic inheritance row passes on both; landed: 11 pass.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:6502-6653
  - src/melder/aether/spellbook/spellbook.py:6739-6767
  - src/melder/aether/spellbook/spellbook.py:6998-7042
  - artifacts/root_configuration_guards_20260929/apply_m3_conjure_refusal_order.py:1-250
  - artifacts/root_configuration_guards_20260929/red_m3_variant.py:1-32
  - artifacts/root_configuration_guards_20260929/m3_red_green.log:1-19
  - tests/component/melder/spellbook/test_conjure_refusal_leaves_frame_unsettled_component.py:1-148
  IMPACT: A refused recorded-world conjure no longer locks its frame dynamic; the discipline itself is unchanged.
  NEXT: Update the conjure code-description patch, then run the full suite on 3.14t in slices.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T00:24:12Z
  TYPE: MEASURE
  CLAIM: Full suite on the landed M1-M4 tree (VM copy of the device tree, CPython 3.14.7t, PYTHON_GIL=0, all 794
    test files in 5 slices): 13281 passed, 32 skipped, 12 xfailed, 2 xpassed (pre-existing), 0 failed. PyYAML was
    installed into the VM venv first (tests/unit/github_workflows imports it; an environment gap, not a code one). The
    six new test files also pass with PYTHON_GIL=1 (49). The conjure code-description, conjure component, Nexus and
    Crystallizer-restore patch docs and the architecture patch now match what landed.
  EVIDENCE:
  - artifacts/root_configuration_guards_20260929/full_suite_landed.log:1-11
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/code_description_patch_spellbook_conjure.md:1-33
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/component_patch_crystallizer_restore.md:1-54
  IMPACT: M1-M4 are complete and regression-free; the Melder side can be notched, documented and packaged.
  NEXT: Notch 0.2.8208 -> 0.2.8212 (one per change: M1 8209, M2 8210, M3 8211, M4 8212) and NOTICE the agents.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T00:38:48Z
  TYPE: MEASURE
  CLAIM: Landing bookkeeping done. __version__ read 0.2.8208 at 00:24:38Z and notched to 0.2.8212 (M1 8209, M2 8210,
    M3 8211, M4 8212; NOTICE M0-115..117). Release note: header 0.2.8212, four sections (two lead with Breaking change)
    and a Packaging bullet; its three examples run verbatim on the landed tree (the first used a setter that returns
    None and was corrected to with_process_wide_unique_spell_ids). System docs: src_architecture (boundary, boot,
    invariants, failure modes, code map, handoff), src_components (Aether, Spellbook, Crystallizer, AR entries, C2
    root configuration and conjure flow, code map; four nexus.py ACL-flow citations that were already stale
    remeasured), tests_components (six test files, clusters, code map), tests_architecture (three stale extents);
    all four indexes regenerated and --check OK; both citation recipes clean. Graph: extract --strict (no skips),
    the 8 nodes this lane changed re-read, given one responsibility each and accepted; the 4 nodes the 0.2.8208 host
    read surface changed stay SEMANTICS_STALE for its backlog task; reassembled (1211 nodes, 1394 edges).
    docs/advanced/nexus.md explains replacing an active Nexus's policy. Not run: docs/tests needing sphinx (absent in
    the VM venv); 17 other docs tests pass.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:153-246
  - artifacts/root_configuration_guards_20260929/release_examples_8212.log:1-9
  - artifacts/root_configuration_guards_20260929/edit_src_architecture.py:1-197
  - artifacts/root_configuration_guards_20260929/edit_src_components.py:1-269
  - artifacts/root_configuration_guards_20260929/edit_tests_components.py:1-138
  - artifacts/root_configuration_guards_20260929/graph_pass.log:1-25
  IMPACT: Melder's half is documented and versioned; only the asset/LLM rebuild and the wheel remain (last step).
  NEXT: MelderOps half: patch docs and red tests in priv_commandops, then F3-F6.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T10:40:18Z
  TYPE: MEASURE
  CLAIM: Build assets and LLM bundles are rebuilt last at 0.2.8212 and checked. Assets: rebuilt on the VM copy (460 /
    619 / 4 entries, --check OK there); five manifests and the three system-document payloads changed and were written
    back keeping the device's CRLF (copy_back_assets.py); asset --check on the device OK for all three. LLM bundles:
    built on the device with --include-untracked (src 576, tests 1041, other 379 files), --check OK for all three
    corpora, no stray .tmp (os.replace over an existing file was first probed inside .venv314/_to_delete/, where the
    probe file stays). Wheel: dist/melder-0.2.8212-py3-none-any.whl (uv, setuptools, 3.14t, fresh staging with the
    tracked __melder_cache__ marker), verify_wheel OK, 591 members - the same set as 0.2.8208 - sha256 019ba21e...8241;
    the CI smoke script passes in an isolated 3.14t venv with the GIL off, and there M1, M2 and M4 answer live. The VM
    ran out of disk mid-mirror (9.8G full); only this agent's stale VM scratch was removed (old tree copies, red trees,
    the 0.2.8208 wheel staging). Installed in both MelderOps environments (priv_commandops ticket carries it).
  EVIDENCE:
  - artifacts/root_configuration_guards_20260929/assets_rebuild_vm.log:1-7
  - artifacts/root_configuration_guards_20260929/assets_check_vm.log:1-3
  - artifacts/root_configuration_guards_20260929/copy_back_assets.py:1-45
  - artifacts/root_configuration_guards_20260929/assets_copy_back.log:1-8
  - artifacts/root_configuration_guards_20260929/assets_check_device.log:1-3
  - artifacts/root_configuration_guards_20260929/llm_build.log:1-4
  - artifacts/root_configuration_guards_20260929/llm_check.log:1-3
  - artifacts/root_configuration_guards_20260929/wheel_verify.log:1-14
  - artifacts/root_configuration_guards_20260929/wheel_smoke.log:1-6
  IMPACT: Melder's half is complete: code, tests, docs, release note, notch, assets, bundles and wheel.
  NEXT: Board and mailbox sync (NOTICE of the rebuild), then report to the owner for acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T15:40:12Z
  TYPE: DECISION
  CLAIM: The owner turned this lane in (chat, 2026-09-30, every finished lane). M1-M4 stay as landed at
    0.2.8209-0.2.8212 with their release-note sections, docs, graph, assets, LLM bundles and the 0.2.8212 wheel.
    The seven patch docs, promoted into src_architecture, src_components and tests_components at landing, are
    archived unchanged to system_docs/patches/completed/root_configuration_guards_2026_09_29/ (mv). The
    sole-writer claims M0-109..114 are released to melder_2, fable_0 and muse_0 (NOTICEs M0-126..128). Open,
    not filed: the Aether record does not carry the spell-id regime (FACT 2026-09-29T23:55:15Z).
  EVIDENCE:
  - tickets/tasks/completed/2026-09-29_guard_melder_roots_for_host_collisions_task.md:202-218
  - system_docs/patches/completed/root_configuration_guards_2026_09_29/architecture_patch.md:1-60
  - release_docs/next_version_release.md:153-224
  IMPACT: The Melder half of the host-collision epic is closed; the regime gap is the one follow-up left for
    the owner to schedule or drop.
  NEXT: Close the investigation task here and, in priv_commandops, the MelderOps task and the epic.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Closed 2026-09-30T15:40:12Z on the owner's turn-in. M1 (0.2.8209) Aether refuses a spell-id regime other than the
sealed one while frames exist; M2 (0.2.8210) an active Nexus refuses another configuration, restore stage 4
deactivates it first; M3 (0.2.8211) a refused recorded-world dynamic conjure leaves its frame unsettled; M4
(0.2.8212) get_configuration_dictionary() on the four root configurations. Docs, graph, release note, assets
and LLM bundles are current; dist/ holds the verified 0.2.8212 wheel, installed in both MelderOps environments.
Patch docs archived to system_docs/patches/completed/root_configuration_guards_2026_09_29/. Open follow-up, not
filed: the Aether record does not carry the spell-id regime, so a world recorded under per-frame ids restores
under process-wide ids.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
