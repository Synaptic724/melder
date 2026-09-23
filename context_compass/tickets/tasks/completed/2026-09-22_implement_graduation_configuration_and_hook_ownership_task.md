# Task: Implement normal Book setup and hook ownership during graduation

## Metadata
- Completed: 2026-09-22T14:41:23Z
- Summary: Graduation source, hook isolation and shared-frame behavior qualified and turned in; packaging held separately.
- Task ID: TASK-2026-09-22-implement-graduation-configuration-and-hook-ownership
- Epic: EPIC-2026-09-22-graduated-conduit-spellbook-ownership-and-configuration
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-22T11:00:19Z
- Updated: 2026-09-22T14:41:23Z

## Objective
Owner now authorizes completion of public upgrade integration and configuration-hook setup. The
private Spellbook conjure method and its direct tests are the implemented foundation.

Promote a lesser with independent normal-Book configuration, Bind hooks and registration ownership.
Apply ordinary configuration selection and initialize Conduit/Meld hooks from the selected policy.
Keep parent state isolated and preserve deterministic creation cleanup. Assets remain held.

## Ticket Contract
- ENTRY_GATE: Owner explicitly authorized source implementation after configuration research.
  Record and consume patch contracts before runtime edits.
- EXECUTION_BOUNDARY: Configuration initial hooks, Book/Bind construction and adoption, graduation,
  Meld/Space aliases, ward detachment, focused tests and authored patch documentation.
- DEPENDENCIES: 32 red ownership cases, normal configuration selection and existing hook contracts.
- EXIT_GATE: Public upgrade and configuration hooks pass ownership and lifecycle regressions;
  source is ready for owner review. Generated assets remain held.
- FAILURE_ESCALATION: Preserve the owner's empty-Book boundary. Raise any actual lifecycle obstacle
  without inventing inherited definitions or transferring the former Book.

## Scope Boundaries
- In: optional upgrade configuration; default local configuration; frame-owned adoption/refusal;
  initial Bind callback defaults; Conduit/Meld default hook setup; lifecycle/adoption isolation.
- Out: universal runtime-hook standardization, pool lease baseline redesign, callback serialization,
  generated assets and unrelated refactors.
- All ordinary meld hot paths remain unchanged; reference updates occur only at graduation/setup.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner requested turn-in after additional regression tests, which now pass.

## Work
- [x] Record patch contracts and source/test mapping for the current method slice.
- [x] Implement and test the owner-selected private existing-conduit conjure method first.
- [x] Implement initial configuration hooks and normal Book initialization.
- [x] Implement coherent graduation adoption with an empty independent Book.
- [x] Qualify Book/Bind/Conduit/Meld/Space ownership and cleanup against the red cases.
- [x] Review source, record results and leave generators held for owner review.

## Planned Source Owners
- src/melder/aether/spellbook/configuration/spellbook_configuration.py
- src/melder/aether/spellbook/bind/bind.py
- src/melder/aether/spellbook/spellbook.py
- src/melder/aether/spellbook/spellbook_creation_system.py
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
Final affected selection: 4118 passed, two existing owner-deferred skips, zero failures/errors in
16.96 seconds. Includes all 32 original public ownership regressions, 39 private-route cases,
configuration defaults, runtime ownership, teardown and failure/retry tests. The strengthened
second-drain rollback checks also pass in local/shared modes. New-test and source fatal lint pass.
Only five intended runtime files differ in the 592-file baseline; generated assets remain unchanged.
Full-repository suite and coverage: Not run. Read artifacts/graduation_configuration_20260922/upgrade_review.md.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/graduation_configuration_2026_09_22/
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
  - tickets/epics/completed/2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md
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

- DATETIME: 2026-09-22T11:33:10Z
  TYPE: FACT
  CLAIM: Owner requests a full conjure trace before source work. The public Book door admits a
    CONJURE transaction before taking its lock. The one-run creation helper prepares configuration,
    classifies cache state and mints a conduit ID for resolution BEFORE _build_conduit allocates.
    Conduit construction registers the root and Book spell ownership. _activate_conjured_conduit
    subsequently sets Book attachment/conjured state, fires hooks, publishes and registers risk state.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:6494-6745
  - src/melder/aether/spellbook/spellbook_creation_system.py:202-347
  - src/melder/aether/spellbook/spellbook_creation_system.py:857-1018
  - src/melder/aether/conduit/conduit.py:295-420
  - src/melder/aether/conduit/conduit.py:1366-1384
  - src/melder/aether/aetheric_frame/aetheric_frame.py:340-378
  IMPACT: Adoption must reuse the target ID before phases and replace only the allocation step
    with in-place promotion/registration. Setting Book flags or skipping all conjure is insufficient.
  NEXT: Trace empty-Book phases, cache behavior, publication and CONJURE scope admission; record the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T11:42:08Z
  TYPE: DECISION
  CLAIM: Owner explicitly rejects an optional-target branch throughout ordinary conjure and any
    Conduit-owned conjure method. Add a NEW PRIVATE SPELLBOOK CONJURE ROUTE for the supplied existing
    Conduit. Duplication is acceptable; reuse helpers where valid and prioritize correctness.
    Full normal trace, adoption-stage responsibilities and qualification points are now recorded.
  EVIDENCE:
  - Owner's separate-private-conjure and Spellbook-ownership corrections.
  - artifacts/graduation_configuration_20260922/conjure_adoption_trace.md
  - src/melder/aether/spellbook/spellbook.py:6536-6745
  - src/melder/aether/spellbook/spellbook_creation_system.py:202-347
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/conjure_transaction_strategy.py:22-158
  IMPACT: The target ID is supplied before resolution. A Book-owned adoption stage replaces
    allocation, including constructor-side registration. Do not move orchestration into Conduit.
  NEXT: Read native target gate/lifecycle protection, then implement the dedicated Book route and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T11:59:29Z
  TYPE: DECISION
  CLAIM: Owner narrows current implementation to the new private Spellbook conjure method and
    direct tests. Target status is already normal before entry. Normal runtime promotion remains
    caller preparation; this method owns Book conjure, runtime attachment and normal activation.
    The existing public upgrade and new configuration-hook APIs are following slices.
  EVIDENCE:
  - Owner's latest single-method instruction.
  - system_docs/patches/completed/graduation_configuration_2026_09_22/code_description_patch_existing_conjure.md
  - src/melder/utilities/synchronization/creation_gate.py:540-604
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:142-302
  IMPACT: Configuration selection already comes from the receiving Book. Gate parking is temporary;
    restore admission before user activation hooks. Foreign-thread managed-scope quiescence belongs
    to the trusted private caller because those stacks are thread-local, not globally enumerable.
  NEXT: Implement the private Book method and direct component tests, then run focused qualification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T12:01:44Z
  TYPE: DECISION
  CLAIM: Consumed the single-method patch. Map Book admission/configuration/phases to direct
    conjure tests; map runtime attachment/cache invalidation to old-ID and retained-Space tests;
    map normal activation to lifecycle hooks, RiskManager and record tests. The existing public
    conjure and upgrade are unchanged in this slice. Input status must already be normal.
  EVIDENCE:
  - system_docs/patches/completed/graduation_configuration_2026_09_22/code_description_patch_existing_conjure.md
  - src/melder/aether/spellbook/spellbook.py:6536-6745
  - src/melder/aether/spellbook/spellbook_creation_system.py:202-347
  - src/melder/aether/spellbook/spellbook_creation_system.py:955-1018
  IMPACT: Required patch/source mapping is complete for this bounded method. Post-attachment
    publication failures follow normal conjure cleanup responsibility; preflight/phase failures
    must not replace the target's Book or reopen an already parked gate.
  NEXT: Add the private method and test it through real prepared normal targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T12:09:05Z
  TYPE: MEASURE
  CLAIM: First direct-method run: 22 pass, 2 disposal assertions fail. Source shows the binding
    profiler records methods from the concrete class dictionary, while the shared regression
    fixture inherited cleanup without declaring it. Those fixtures had no matched disposal method.
    This is a fixture defect, not evidence that adoption lost a registered disposal entry.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/method_first.log
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:111-136
  - src/melder/aether/spellbook/bind/bind.py:676-694
  IMPACT: Declare cleanup on the actual fixture classes and assert disposal admission before
    exercising ownership. Correct the shared fixture rather than changing runtime disposal.
  NEXT: Fix those declarations, narrow the frame lock to root publication, and rerun the method tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T12:15:53Z
  TYPE: MEASURE
  CLAIM: All 24 direct cases pass after concrete disposal declarations corrected the fixture.
    Attachment now holds the frame lock only through root publication, releasing it before
    Aether dispatch and record callbacks. Added refusal-before-phases and failure/retry/record
    tests to qualify the new method's non-happy paths, including locked shared configuration.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/method_corrected.log
  - src/melder/aether/spellbook/spellbook.py:6631-6850
  - tests/component/melder/spellbook/test_spellbook_conjure_existing_conduit.py
  IMPACT: The single private route is operational. Public upgrade remains unchanged; configuration
    hook defaults remain a future slice. Qualification is not complete until the expanded run passes.
  NEXT: Run the expanded method tests and ordinary conjure compatibility selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T12:20:02Z
  TYPE: MEASURE
  CLAIM: Delivered the private Spellbook method first, as requested. Combined qualification passes
    387 tests, including 37 direct method cases. Tests exercise configuration modes, exact object/id
    retention, registered/new definitions, old-ID cache refusal, local Space rebinding, selected
    lifecycle/Meld hooks, both gate postures, timeout/phase failure, retry, input refusal and recorder
    identity. No public upgrade or configuration-hook default API was changed in this slice.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/method_compatibility.log:1-7
  - artifacts/graduation_configuration_20260922/method_compatibility.xml
  - artifacts/graduation_configuration_20260922/method_source_changes.json:1-7
  - artifacts/graduation_configuration_20260922/method_tests_lint.log:1-1
  - artifacts/graduation_configuration_20260922/method_fatal_lint.log:1-1
  - artifacts/graduation_configuration_20260922/method_review.md
  IMPACT: This bounded method is ready for source review. The public upgrade and broad configuration
    hook API work remain separate next steps; assets remain held. No full-suite/coverage claim.
  NEXT: Owner reviews the new private Book method, then selects the caller integration slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T12:28:37Z
  TYPE: MEASURE
  CLAIM: Final selection passes 389 tests with zero failures/errors/skips, including 39 direct
    cases after adding late public bind/hook/purge checks on an initially empty receiving Book.
    The corrected public-upgrade regression fixture still reports 32 intended failures because
    that public caller remains unchanged. Source comparison again shows only spellbook.py changed
    among 592 src Python files. New tests and source fatal checks pass lint.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/method_final.log:1-7
  - artifacts/graduation_configuration_20260922/method_final.xml
  - artifacts/graduation_configuration_20260922/public_upgrade_still_red.log
  - artifacts/graduation_configuration_20260922/public_upgrade_still_red.xml
  - artifacts/graduation_configuration_20260922/method_source_changes.json:1-7
  IMPACT: The exact requested single-method slice is complete and tested. No new configuration
    APIs, public upgrade integration, generated assets or broad runtime changes are included.
  NEXT: Review this private method before the next caller-integration slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T12:58:23Z
  TYPE: DECISION
  CLAIM: Owner authorizes finishing public graduation. Consumed configuration and existing-conjure
    patch contracts. Config seed methods map to Bind constructor injection and ordinary/graduated
    Book tests; default event getters map to Conduit/Meld setup and recording presence tests.
    Public promotion must drain before changing status and pass original gate posture into adoption
    so activation hooks can meld after attachment. Roll back only before the new Book is attached.
  EVIDENCE:
  - system_docs/patches/completed/graduation_configuration_2026_09_22/architecture_patch.md:1-64
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:692-927
  - src/melder/aether/spellbook/bind/bind.py:190-362
  - src/melder/aether/spellbook/spellbook.py:6631-6846
  - src/melder/aether/conduit/conduit.py:1961-2140
  IMPACT: Fresh defaults or canonical shared configuration select the new Book. No old root
    resolution verdicts or definitions transfer. Generated assets remain held.
  NEXT: Implement the configuration seed foundation, then wire the public graduation caller.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T13:09:57Z
  TYPE: FACT
  CLAIM: Source now seeds each Bind from configuration tuples, merges runtime defaults with exact
    Book events, and emits effective hook markers. Public upgrade creates a fresh Book, drains and
    detaches the lesser, prepares root resources and delegates to the private Book conjure route.
    Pre-attachment failures restore lineage/gates; parent configuration is never implicitly adopted.
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py
  - src/melder/aether/spellbook/bind/bind.py:197-236
  - src/melder/aether/spellbook/spellbook.py:6635-6855
  - src/melder/aether/conduit/conduit.py:1961-2170
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:526-585
  IMPACT: Ready for the first real public/private graduation run; no passing result is claimed yet.
  NEXT: Run the existing ownership and private-conjure regression suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T13:09:57Z
  TYPE: MEASURE
  CLAIM: First public run passes all 32 previously red ownership cases. All 39 direct-method cases
    fail at one fixture-only double removal: repaired ward conversion now removes the old parent
    entry that the fixture previously removed itself. Updated the fixture to use conversion's
    reciprocal detach under the required parent ward lock.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/public_first.log
  - tests/component/melder/spellbook/test_spellbook_conjure_existing_conduit.py:76-96
  IMPACT: Public Book/binding/hook/cleanup isolation now works. Additional configuration and failure
    qualifications remain; obsolete seed-state unit expectations must become current contracts.
  NEXT: Add configuration/default-hook and public upgrade failure/admission tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T13:16:07Z
  TYPE: MEASURE
  CLAIM: Expanded run timed out in the new test's activation callback because it attempted Bind
    inside the still-active CONJURE transaction (embargo admission wait). This route deliberately
    retains the normal activation helper and transaction boundary. Adjusted the test to probe Meld
    lookup during activation and perform binding after upgrade returns. Pre-attachment private-route
    failures now leave a caller-preparked gate closed until public rollback completes.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/public_expanded.log
  - src/melder/aether/spellbook/spellbook.py:6836-6860
  - src/melder/aether/spellbook/spellbook_creation_system.py:955-1018
  IMPACT: Do not widen activation semantics to support recursive structural registration. No pass
    count is claimed for the timeout-terminated run. Constructor identity publication was deferred
    until initialization succeeds so rejected config selection cannot leak a registered partial Book.
  NEXT: Rerun the expanded configuration and graduation suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T13:17:07Z
  TYPE: MEASURE
  CLAIM: Corrected expanded run completes with 237 passes and three new-test failures caused by
    omitted required existence arguments in the shared-seed test. Supplied those arguments. Gate
    drain, all public ownership regressions, private-method compatibility, config batch atomicity,
    frozen seeds, recording and failure rollback otherwise pass in that run.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/public_expanded_retry.log
  - tests/component/melder/aether/conduit/test_conduit_graduation_configuration.py:84-106
  IMPACT: Remaining qualification includes legacy upgrade assertions that expected the defective
    preset-factory call/root-state copy. Replace those with equivalent real lifecycle outcomes.
  NEXT: Run the broader affected Book/Conduit selection to identify remaining mismatches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T13:18:22Z
  TYPE: MEASURE
  CLAIM: Broader affected selection passes 315 tests and fails 15 legacy graduation tests. Eleven
    use mocked wards/factory calls from the discarded-Book implementation; four expect prior spell
    resolution or copied root verdicts. Those assertions contradict the owner's empty independent
    Book ruling. New actual-runtime ownership/configuration/failure cases all pass.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/affected_first.log
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:292-446
  - tests/unit/melder/aether/conduit/test_conduit_dynamic.py:580-673
  - tests/unit/melder/aether/conduit/test_conduit_upgrade_validate_before_mutate_regression.py:1-140
  IMPACT: Migrate healthy-upgrade and invalid-hook qualification into the real component suite;
    retain unit admission checks. Replace root-verdict inheritance with empty-state checks and
    explicit later compilation. Retained-creations tests assert storage/disposal, not old-ID lookup.
  NEXT: Update these bounded legacy tests and rerun the affected selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T13:22:20Z
  TYPE: MEASURE
  CLAIM: Revised selection passes 342 cases; four test assumptions remained: pooled shells have
    pooled_lesser status (refused before detached-lineage inspection), and normal validation of
    an empty Book returns no resolution state. Updated the pooled error assertion and extended
    the resolution tests to bind/meld a new local definition before checking independent verdicts.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/affected_updated.log
  - src/melder/aether/conduit/conduit.py:565-590
  - src/melder/aether/conduit/conduit.py:5187-5306
  IMPACT: Legacy tests now assert actual empty-Book semantics rather than synthesizing inherited
    state. No production workaround was introduced to satisfy obsolete expectations.
  NEXT: Qualify the full affected unit/runtime surfaces and run scoped lint.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T13:27:25Z
  TYPE: MEASURE
  CLAIM: Full affected qualification completes 4,120 cases: 3,967 pass, two skip and 151 fail in
    one legacy Book unit module because its configuration doubles lack the new get_bind_hooks
    constructor contract. Added the empty seed getter to DummyConfig and _TxnConfig; no runtime
    fallback/probe was added. A focused rerun after the first double update passed 151/152 and
    isolated the second double; all graduation component/integration checks were green already.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/qualification.log
  - artifacts/graduation_configuration_20260922/book_stub.log
  - tests/unit/melder/spellbook/test_spellbook.py:422-590
  - tests/unit/melder/spellbook/test_spellbook.py:1538-1561
  IMPACT: The constructor API delta is now represented in both isolated doubles. Runtime behavior
    remains strict; no compatibility guard on a known owned configuration contract.
  NEXT: Rerun the affected qualification and complete source/test lint and asset hash checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T13:35:54Z
  TYPE: MEASURE
  CLAIM: Public graduation and configuration defaults are fully implemented. Final affected run
    reports 4118 passed, two existing owner-deferred skips and zero failures/errors. Strengthened
    second-drain fault injection also passes in both configuration modes, proving the private
    route does not reopen admission before public rollback restores the lesser. Scoped lint passes.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/qualification_final.log
  - artifacts/graduation_configuration_20260922/qualification_final.xml
  - artifacts/graduation_configuration_20260922/rollback_gate_final.log:1-2
  - artifacts/graduation_configuration_20260922/upgrade_tests_lint.log:1-1
  - artifacts/graduation_configuration_20260922/upgrade_source_lint.log:1-1
  - artifacts/graduation_configuration_20260922/upgrade_source_changes.json:1-13
  - artifacts/graduation_configuration_20260922/upgrade_review.md
  IMPACT: Source is ready for owner review. Five intended runtime files changed; all recorded build
    asset hashes remain unchanged. Existing deferred skips concern shared-context revalidation,
    not this implementation. Full repository suite/coverage: Not run. Earlier completion-pass
    timestamps were corrected from estimates to recorded checkpoint/artifact UTC times.
  NEXT: Owner reviews source before any canonical-doc promotion or generated-asset work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T14:22:51Z
  TYPE: DECISION
  CLAIM: Owner requests additional regressions proving Bind/Conduit/Meld decoupling, a detailed
    explanation of frame-wide configuration, and graduation epic turn-in after qualification.
    Extend public tests across inherited per-Book maps, lesser/Space runtime overlays, shared
    configured defaults and failure/retry. A new Book always remains independent and empty.
  EVIDENCE:
  - Owner's current additional-tests, shared-configuration and epic turn-in request.
  - src/melder/aether/spellbook/spellbook.py:5581-5698
  - src/melder/aether/spellbook/spellbook.py:6768-6849
  IMPACT: Runtime additions from the old Book/lesser must be dropped. Shared configuration may
    intentionally reseed default callbacks, without sharing the Book's mutable Bind registry.
  NEXT: Add targeted public regression tests for these hook and frame-wide ownership boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-22T14:27:03Z
  TYPE: MEASURE
  CLAIM: Added twelve hook-isolation/frame-policy scenarios. First run passed ten and rejected
    two shared-default cases at an unrelated duplicate-name guard because the test rebound the
    same class under another binding name. Replaced that fixture input with a distinct class.
    All old per-Book/default-local callbacks and lesser/Space overlays were discarded as expected.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/hook_isolation_first.log
  - tests/component/melder/aether/conduit/test_conduit_graduation_hook_isolation.py
  IMPACT: Shared configured seeds are intentional; runtime changes remain isolated. Complete the
    corrected shared-policy cases before claiming the additional matrix passes.
  NEXT: Run the new matrix with the existing graduation and configuration regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-22T14:29:56Z
  TYPE: MEASURE
  CLAIM: All 157 graduation/configuration tests pass, including twelve added hook-isolation cases.
    These qualify old per-Book hooks, local Conduit/Meld/Space overlays, intentional shared default
    seeding, explicit canonical-config input, failure/retry and isolation across different frames.
    No runtime source changed in this final test tranche.
  EVIDENCE:
  - artifacts/graduation_configuration_20260922/hook_isolation_final.log:1-4
  - tests/component/melder/aether/conduit/test_conduit_graduation_hook_isolation.py:130-359
  IMPACT: Owner-requested conditions for graduation epic turn-in are met. Promote the scoped
    architectural/component notes and archive graduation tickets. Packaged build assets remain
    held; updating ContextCompass document indexes does not run Melder's build-asset runner.
  NEXT: Promote graduation/configuration documentation, then close the three graduation tickets.
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