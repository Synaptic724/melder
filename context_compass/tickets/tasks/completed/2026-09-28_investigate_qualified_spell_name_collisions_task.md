# Task: Correct duplicate-name validation for qualified bindings

## Metadata
- Task ID: TASK-2026-09-28-investigate-qualified-spell-name-collisions
- Story: none; standalone investigation and correction
- Status: done
- Owner: codex
- Agent Name: workflows_0
- Priority: p1
- Created: 2026-09-28T00:43:28Z
- Updated: 2026-09-28T08:31:05Z
- Completed: 2026-09-28T08:27:12Z
- Summary: Qualified same-name registrations use canonical address validation; regressions demonstrated
  red then green (147 passed, 2 pre-existing XPASS). Notched 0.2.8206; documented in release section
  "Fixed: same-named classes can use distinct spell addresses". Final asset and bundle checks passed.

## Objective
Permit same-named spells at distinct canonical lookup addresses while preserving real collision
diagnostics. Add regressions first, verify failures, then implement and qualify the correction.

## Problem / Context
The owner supplies a consumer investigation on installed Melder 0.2.82: distinct module spellframes
or qualified binding names permit registration, but conjure reports DUPLICATE_SPELL_NAME because
the validator groups by class __name__. The error recommends qualifiers which reportedly do not
affect its collision key. Discoverable definitions also trigger it. Independently reproduced against
local source 0.2.8204 on Python 3.14.7 with the GIL disabled; see the validation evidence below.

## Ticket Contract
- ENTRY_GATE: Existing workflows_0 onboarding/certification retained; current repository policy,
  contribution guide and shared boards read; check-in and this active route established.
- EXECUTION_BOUNDARY: DuplicateSpellNameStrategy, canonical binding/lookup identity, visible pools,
  related tests, validation documentation, release note, graph descriptor and generated assets.
- DEPENDENCIES: Owner authorized the recommended fix and red-before-green tests on 2026-09-28.
  Patch id: qualified_spell_name_collisions_2026_09_28; workflows_0 owns the strategy source edit.
- EXIT_GATE: Regressions demonstrated red before production changes, corrected tests green,
  canonical docs and release updated, source notched and generated assets verified last.
- FAILURE_ESCALATION: Do not rename application classes, weaken tests, disable validation or claim
  alias/contract behavior from class names alone. Record unsupported reproductions explicitly.

## Scope Boundaries
- In scope: distinct classes sharing __name__, frames/binding names, resolvable=False, own/contracted
  visible pools, valid aliases and actual lookup collisions.
- Out of scope: bare-class identity lookup correction, caller-input work, lookup precedence/schema
  redesign and concurrent scope-exit/probe/performance changes owned by other agents.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Authorized implementation, red/green tests and documentation delivered; generated
  assets are the mandatory post-turn-in finalization step under the contribution guide.

## Steps / Checklist
- [x] Read current binding/validation component slices and actual source.
- [x] Locate the consumer probe and lead decision/ledger context.
- [x] Reproduce distinct qualified names, discovery-only variants and cross-book visibility.
- [x] Compare the candidate correction with canonical lookup identity and genuine collisions.
- [x] Deliver findings and the smallest correct next implementation scope.
- [x] Add and run corrected-behavior regressions before changing runtime source.
- [x] Implement canonical-key collision validation and qualify affected suites.
- [x] Promote docs, notch the source change and update the release note.
- [x] Finalize generated assets after turn-in; both asset and LLM bundle checks passed.

## Deliverables / Acceptance
- Exact current source paths and behaviors explaining bind-versus-conjure disagreement.
- Bounded pytest/probe evidence with actual interpreter, version and import location.
- Recommendation based on lookup semantics rather than an arbitrary tuple of display fields.

## Validation
- Supplied public-API reproduction: all seven reported outcomes reproduced on local src/ 0.2.8204.
- Existing intended-behavior Fault-A tests with --runxfail: 2 failed, 4 deselected (expected bug evidence).
- Existing contracted-name characterizations: 2 passed, confirming the current incorrect verdict.
- Additional normalized-key, discoverable-key ownership, cross-book and cross-frame controls: 4 passed.
- The new controls first had four keyword-only bind setup errors; corrected and rerun. Both logs retained.
- Interpreter: .venv_new/Scripts/python.exe, Python 3.14.7 free-threaded, GIL disabled.
- Implementation regression baseline: 35 failed, 112 passed, 2 XPASS across eight affected modules.
- After the strategy fix: 147 passed, 2 unchanged Fault-B XPASS across those same modules.
- Source, component and test indexes are current; focused diff check passes; preservation reports
  account for every removed documentation line. Full suite and coverage: Not run (bounded change).
- Final asset builder and --check: all three families OK at 0.2.8206. LLM builder and --check
  with --include-untracked: src, tests and other fingerprints/output proofs all match.

## Risks / Rollback Notes
- Multiple agents are active. Preserve their rows, messages and source changes.
- Source landing follows the contribution guide: read the live version, notch once and rebuild assets last.
- Use GIT_OPTIONAL_LOCKS=0 for read-only Git operations, following the shared workspace notice.

## Applicable Anti-Patterns
- [x] No class-name-based inference of canonical lookup identity.
- [x] No disabling the reported validator to claim a passing public integration.
- [x] Production fix is now explicitly authorized; bare-class resolution remains a separate issue.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/
  - context_compass/system_docs/patches/completed/qualified_spell_name_collisions_2026_09_28/architecture_patch.md
  - context_compass/system_docs/patches/completed/qualified_spell_name_collisions_2026_09_28/component_patch_validation.md
  - context_compass/system_docs/patches/completed/qualified_spell_name_collisions_2026_09_28/code_description_patch_validation.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain reproduction, red/green logs and preservation evidence; archive promoted patch contracts.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: duplicate-name validation and qualified lookup keys
- IF_UNKNOWN: none

## Noting Behavior
- Record coherent source traces and measurements before the next tranche.
- Preserve the owner's 30-second PowerShell wait cadence if peer messaging becomes necessary.

## Notes
- DATETIME: 2026-09-28T00:43:28Z
  TYPE: PLAN
  CLAIM: Open the duplicate-name investigation using the owner's supplied 0.2.82 report. No addressed
    mailbox messages or active duplicate-name lane were found. Current policy adds the contribution
    guide; follow it if a later source change is authorized, without imposing a notch on discovery.
  EVIDENCE:
  - context_compass/special_instructions/agent_contribution_guide.md:9-22
  - context_compass/attention_board.md:100-105
  IMPACT: Keep this lane read-only for runtime source and isolate evidence from other active agents.
  NEXT: Read the current binding/validation maps and locate the consumer's same-name probe records.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T00:46:08Z
  TYPE: FACT
  CLAIM: Current DuplicateSpellNameStrategy groups every visible pool entry by spell_name alone;
    frame and binding appear only in diagnostic detail. It raises error-severity duplicates without
    consulting resolvable. SpellInputUtils defines the actual case-insensitive address as
    (normalized spellframe-or-name, normalized binding-or-default), not the proposed raw three-tuple.
    The current error's advice to add qualifiers cannot alter the validator's grouping.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:70-149
  - src/melder/utilities/helpers/general_helpers.py:224-425
  IMPACT: The reported mismatch is source-confirmed on the current checkout. A correct remedy must
    use actual lookup identity and respect local/contracted visibility precedence; raw tuple grouping
    is not yet an adequate design.
  NEXT: Trace registration claim and contracted lookup rules, then reproduce through public APIs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T00:52:01Z
  TYPE: FACT
  CLAIM: Meld normalizes address inputs, searches owned keys first, then contracted keys; it never
    searches the pool for all matching display names. A bare class is reduced to its __name__, with
    no class-identity guard. The newly supplied CommandOps report confirms the same source trace and
    identifies existing Fault-A xfails. Its proposed cross-contract collision example omits two gates:
    active signatures are unique across the AethericFrame, and public links reject different frames.
    Contract admission additionally rejects a key already held by a different contracted SpellIndex.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:1732-1985
  - src/melder/aether/aetheric_frame/lookup_container.py:92-127
  - src/melder/aether/spellbook/spellbook.py:2290-2370
  - src/melder/aether/spellbook/spellbook.py:3024-3082
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:765-863
  - tests/integration/melder/spellbook/test_spellbook_integration_di_validation_faults.py:1-172
  IMPACT: Distinct qualified addresses should not be rejected for a shared display name. Class-object
    identity is a separate lookup contract. Do not invent a new shadowing policy from an unreachable
    normal-registration scenario or exempt discoverable registrations from address ownership casually.
  NEXT: Run the supplied public-API reproduction against this checkout and the two existing Fault-A tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T00:53:45Z
  TYPE: MEASURE
  CLAIM: The supplied reproduction reproduces every reported outcome on this checkout: distinct
    frames, distinct bindings, both qualifiers and a discoverable twin all bind but fail conjure.
    Different-name and same-address-refusal controls behave correctly. An unregistered ModuleB.Repo
    passed as spell returns ModuleA.Repo. The two existing intended-behavior Fault-A tests fail when
    run with --runxfail: 2 failed, 4 deselected. Environment is local src/, Melder 0.2.8204,
    Python 3.14.7 free-threaded, GIL disabled.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/consumer_repro_results.json:1-154
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/existing_fault_a_runxfail.log:1-16
  IMPACT: Both symptoms are live, independently verified current behavior, not just a 0.2.82 report.
    Production and existing test sources remain unchanged.
  NEXT: Verify contracted-pool behavior and normalize/capability collision controls before the recommendation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T00:55:00Z
  TYPE: MEASURE
  CLAIM: The two existing contracted-name tests pass and explicitly assert the incorrect duplicate
    verdict for distinct owner/borrower bindings, including clearing after unlink. Four new diagnostic
    controls initially failed in their setup because my probe called keyword-only Spellbook.bind
    positionally. Corrected the probe to spell=; these setup failures are not product defects.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/boundary_and_contract_controls.log:1-24
  - tests/integration/melder/spellbook/test_spellbook_integration_validation_system.py:160-280
  - tests/integration/melder/spellbook/test_spellbook_integration_validation_system.py:572-702
  IMPACT: The issue crosses local/contracted pool visibility and some existing tests pin the defect.
  NEXT: Rerun the corrected four registration controls and finalize the bounded recommendation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T00:56:19Z
  TYPE: MEASURE
  CLAIM: All four corrected controls pass: case-normalized key collisions are refused for resolvable
    and discoverable owners, a second book cannot claim the same address in one AethericFrame, and
    roots in separate AethericFrames cannot link. These exercise ordinary public APIs without
    disabling the duplicate-name strategy. No new local/contracted shadowing policy is needed to
    unblock the reported qualified registrations.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/test_registration_boundaries.py:47-98
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/registration_boundary_controls.log:1-2
  IMPACT: The proposed fix must retain the existing address-ownership boundary for all registrations.
  NEXT: Present the correction scope below for the owner's implementation direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T00:56:19Z
  TYPE: PLAN
  CLAIM: Recommend changing DuplicateSpellNameStrategy to judge canonical normalized address keys
    using SpellInputUtils.make_spell_key_from_parts, and updating its contract/message accordingly.
    Keep the existing registration and contracted-key gates; do not add global uniqueness of display
    names, warnings for harmless twins, or a new resolvable=False address exemption. Re-enable the
    two Fault-A tests, invert tests that pin the false positive, and retain regressions for both
    qualifiers, case normalization, discoverable definitions, contracted visibility and genuine
    address refusal. Handle bare-class identity separately: lookup can return another class even
    when only one class was registered, so the duplicate guard cannot solve it. A class-request
    mismatch check needs explicit class/factory/instance/Protocol and warm-door regression coverage;
    do not introduce an automatic class-to-registration search in this bounded fix.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:13-149
  - src/melder/utilities/helpers/general_helpers.py:334-425
  - src/melder/aether/conduit/meld/meld.py:1732-1985
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/consumer_repro_results.json:1-154
  IMPACT: A small validation correction unblocks qualified CommandOps registrations without changing
    address selection, frame boundaries, discovery capability or override behavior. Production fix,
    documentation promotion, version notch and asset regeneration remain a subsequent change.
  NEXT: Owner selects the correction scope; investigation is ready for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T00:59:26Z
  TYPE: DECISION
  CLAIM: Owner explicitly authorized the proposed normalized-address fix and regression tests that
    fail before production changes. Scope is DuplicateSpellNameStrategy.validate/metadata, its unit
    tests, affected component/integration validation assertions and a public-API regression matrix.
    Canonical validation docs/graph, next release entry, version notch and asset rebuild accompany it.
    The separate bare-class identity hazard remains outside this implementation.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/existing_fault_a_runxfail.log:1-16
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/registration_boundary_controls.log:1-2
  IMPACT: Reopen the existing ticket for the accepted implementation; retain all investigation evidence.
  NEXT: Stage patch contracts, add corrected-behavior tests and capture a fresh red run before source edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T01:02:00Z
  TYPE: PLAN
  CLAIM: Read the staged architecture, validation component and code-flow contracts in order.
    Mapping: architecture address invariant -> normalized-key strategy -> unit collisions plus public
    conjure/meld cases; component pass-cache contract -> shared memo cases; component ownership rule ->
    existing genuine-address refusal controls; code-flow contract -> cancellation/empty-name tests.
    Source and graph agree on the affected strategy/helper. Patch entry gate is satisfied.
  EVIDENCE:
  - context_compass/system_docs/patches/active/qualified_spell_name_collisions_2026_09_28/architecture_patch.md:1-37
  - context_compass/system_docs/patches/active/qualified_spell_name_collisions_2026_09_28/component_patch_validation.md:1-29
  - context_compass/system_docs/patches/active/qualified_spell_name_collisions_2026_09_28/code_description_patch_validation.md:1-24
  IMPACT: Tests can now establish the red baseline; runtime source is still untouched.
  NEXT: Add the regression matrix and run it against the unchanged validator.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T01:05:00Z
  TYPE: MEASURE
  CLAIM: Regression-first baseline captured against unchanged production source: 22 failed,
    4 passed, 9 deselected. Ten public conjure cases fail with DUPLICATE_SPELL_NAME (both postures,
    four qualifier combinations and discoverable twins); eight fresh/cached distinct-key unit cases
    report false collisions; four genuine normalized-key unit cases with different display names
    incorrectly report none. Four genuine-address bind controls already pass.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/regressions_red.log:1-326
  - tests/integration/melder/spellbook/test_spellbook_qualified_same_name_regressions.py:1-131
  IMPACT: The tests distinguish the intended invariant from simply disabling the validator.
  NEXT: Align existing defect-pinning expectations, then correct the validator's grouping key.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T01:06:00Z
  TYPE: MEASURE
  CLAIM: Updated all located defect-pinning assertions before editing runtime source. The affected
    eight-module red run reports 35 failed, 112 passed and 2 pre-existing Fault-B XPASS outcomes.
    Failures are the newly required address behavior and diagnostic metadata/description; genuine
    registration controls remain green. The production strategy still matches the pre-change source.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/affected_suites_red.log:1-205
  IMPACT: Both new regressions and previously incorrect contracts now demand the same corrected behavior.
  NEXT: Replace bare-name grouping with canonical lookup-key grouping and rerun the identical suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T01:07:30Z
  TYPE: MEASURE
  CLAIM: The identical eight-module run is green after the strategy fix: 147 passed, 2 XPASS
    (the unchanged Fault-B markers). The strategy now keys its existing pass memo by the shared
    normalizer's tuple, includes the address in diagnostics, and retains code/severity and all
    prior detail fields. Qualified resolutions return exact classes in both postures, including
    borrowed bindings; resolvable=False still refuses direct meld and retains address ownership.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/affected_suites_green.log:1-4
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:1-166
  IMPACT: The red-to-green requirement is met without changing lookup or registration admission.
  NEXT: Review the diff, promote documentation, notch this source change and rebuild the generated assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T01:11:03Z
  TYPE: FACT
  CLAIM: Consumed M0-86 from melder_0: its active follow-up owns conduit_meld.py docstrings and the
    src_architecture/src_components Indexing portability edits, with its own asset rebuild waived.
    The live version has moved to 0.2.8205 while the release header still reads 0.2.8204. My source
    and regression diff is scoped and its focused whitespace check passes; an unscoped Git check
    found pre-existing permission/whitespace issues in other lanes, which I did not edit.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-28_finish_probe_and_doc_portability_followups_task.md:16-33
  - src/melder/__version__.py:12-12
  IMPACT: Hold shared source-document, version/release and graph assembly writes until melder_0
    releases the current pass. Work on tests documentation and my descriptor can continue.
  NEXT: Request the shared-document handoff through the mailbox and continue independent documentation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T01:14:08Z
  TYPE: FACT
  CLAIM: Consumed M0-90: melder_0 owns the 0.2.8205 notch for its ConduitMeld documentation pass;
    its rebuild waiver does not apply to this fix. Tests documentation and its index are current,
    and the strategy graph descriptor's authored prose now states address uniqueness. Shared
    source-document/release/assembly writes still wait for WF0-1's handoff; no competing write made.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-28_finish_probe_and_doc_portability_followups_task.md:16-33
  - context_compass/system_docs/tests_components.md:1238-1261
  IMPACT: Final landing must notch above 0.2.8205 and rebuild the complete current tree.
  NEXT: Await the shared-document release using the owner's 30-second PowerShell message protocol.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T08:22:09Z
  TYPE: DECISION
  CLAIM: WF0-1 remains unacknowledged; no handoff approval is inferred. Fresh source and melder_0's
    01:17 note establish that its Indexing edits and graph refresh finished, and its release entry
    is now present at 0.2.8205. Complete the owner's authorized fix using anchored edits only in
    disjoint validation/invariant sections, preserving the current Indexing and release content.
    Re-read shared files before each write and refresh baselines to include the peer's finished work.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-28_finish_probe_and_doc_portability_followups_task.md:147-182
  - release_docs/next_version_release.md:1-99
  IMPACT: Avoid an indefinite coordination wait without overwriting or taking over the peer's work.
  NEXT: Notify melder_0, apply the prepared documentation and notch above the observed live version.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T08:24:12Z
  TYPE: FACT
  CLAIM: Landed the accepted source change at 0.2.8206 after reading live 0.2.8205. Added release section
    "Fixed: same-named classes can use distinct spell addresses" and updated the header/rebuild stamp.
    Promoted the canonical address invariant, validator semantics and corrected stale bare-name prose
    to the source docs while preserving melder_0's current Indexing/portability edits. Both indexes rebuilt.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:84-113
  - context_compass/system_docs/src_components.md:3440-3443
  IMPACT: Public behavior, release notes and authored system documentation agree; assets remain to rebuild.
  NEXT: Refresh and verify the graph, finish preservation/diff checks, then turn in and rebuild assets last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T08:27:12Z
  TYPE: FACT
  CLAIM: Source/test docs and graph promotion are verified. Extraction skipped zero files; the two
    strategy nodes were read, accepted and assembled. All three edited document indexes pass.
    Preservation reports account for the metadata date and five stale bare-name lines replaced;
    every other baseline line survives, including the peer's completed portability edits. Focused
    code/test/release whitespace checks pass. Turn in the implementation, then build assets last.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/graph_extract.log:1-6
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/graph_assemble.log:1-4
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/source_doc_preservation.json:1-22
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/tests_doc_preservation.json:1-8
  IMPACT: Ready for the mandatory final packaging step; unrelated pre-existing graph staleness was not certified.
  NEXT: Run asset and LLM builders/checks; reopen this task if finalization fails and cannot be completed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T08:31:05Z
  TYPE: MEASURE
  CLAIM: Final builds/checks completed after turn-in: all three asset families report OK at 0.2.8206;
    all three LLM corpora report matching fingerprints and output proofs with --include-untracked.
    Consumed M0-91: melder_0 confirms its shared-doc/graph pass finished at 01:17 and releases its
    claim; its waived 0.2.8205 assets are now covered by this rebuild. My strategy nodes were already
    re-read, accepted and assembled. No required work remains for the address-validation correction.
  EVIDENCE:
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/build_assets_check.log:1-3
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/build_llm_check.log:1-3
  - context_compass/artifacts/qualified_spell_name_collisions_20260928/affected_suites_green.log:1-4
  IMPACT: Deliver the complete fix, tests, documentation and generated outputs. Bare-class identity
    remains a separate, explicitly recorded resolution issue; it was not silently bundled into this fix.
  NEXT: None for this task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implemented by workflows_0 at 0.2.8206: DuplicateSpellNameStrategy compares canonical frame/binding
addresses and preserves existing collision guards. Red-to-green evidence: 35 failed before, 147 passed
after, with 2 unchanged Fault-B XPASS outcomes. Eight test modules, including the new public matrix, qualify
automatic/dynamic frames, discoverable twins, contracted bindings, defaults/case and true collisions.
Docs, release and graph promoted; patch contracts archived and evidence retained. Bare-class identity
lookup is explicitly separate and unchanged. Assets and LLM bundles rebuilt after turn-in and all
checks passed at 0.2.8206. No commit, tag or publication performed. No remaining work in this task.
