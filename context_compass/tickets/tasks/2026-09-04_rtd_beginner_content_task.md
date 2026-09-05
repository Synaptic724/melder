# Task: Implement Beginner chapters and all 41 lesson presentations

## Metadata
- Task ID: TASK-2026-09-04-rtd-beginner-content
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-beginner-curriculum
- Story Path: ../stories/2026-09-04_rtd_beginner_curriculum_story.md
- Status: in_progress
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-05T10:09:36Z

## Objective
Deliver the complete Beginner learning path, public vocabulary, current cleanup explanation, capstone, and every saved Beginner lesson.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: docs/beginner/, Beginner lesson editorial metadata/wrappers, related reference links, and evidence-backed documentation/example corrections in 01_beginner only.
- DEPENDENCIES: S1/S2; settled disposal source contract from codex_1's lane.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: review
- to_state: in_progress
- transition_reason: Owner requests a corrected capstone: self-mediated binding, separate Python
  modules/bootstrap/consumer, and TYPE_CHECKING annotations where consumer code melds its objects.

## Steps / Checklist
- [ ] Read the exact inputs and record one bounded implementation decision.
- [ ] Complete required patch contracts when the change is system-impacting.
- [ ] Implement the scoped deliverable with notes before the next tranche.
- [ ] Validate meaningful behavior/content and record actual outcomes.
- [ ] Synchronize parent story and hand off or close after acceptance.

## Acceptance Criteria
- [ ] Every blueprint Beginner chapter and all 41 lessons are accounted for.
- [ ] The first useful result and capstone can be followed from their stated prerequisites.
- [ ] Current address/lifetime/disposal claims are source-backed.
- [ ] Code matches canonical source and all navigation links resolve.
- [ ] Applicable existing example/probe checks run or concrete blockers are recorded.

## Validation
- Not run. Implementation task just created.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/rtd_validation_20260904/beginner.xml
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement Beginner chapters and all 41 lesson presentations
- IF_UNKNOWN: none

## Noting Behavior
- Finish a coherent read/work unit and append evidence, impact, and one next action.
- Keep notes append-only; label unverified claims explicitly.

## Notes
- DATETIME: 2026-09-04T23:42:53Z
  TYPE: DECISION
  CLAIM: Owner handles all commits and pushes because signing needs their PGP passphrase.
    Continue the already-authorized documentation implementation and local validation only.
    Re-entry reads are complete for general -> engineer -> synaptic_python_developer;
    retain the owner's existing codex_2 identity and certification under runtime instructions.
  EVIDENCE:
  - Owner message on 2026-09-04: do not attempt commits; owner will commit.
  - attention_board.md:83-85
  IMPACT: No commit, push, signing-key access, or passphrase prompt belongs to this lane.
  NEXT: Read the existing curriculum implementation and recover its saved validation results.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:07:46Z
  TYPE: PLAN
  CLAIM: Implement this bounded part of the accepted documentation program under its existing story.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:293-344
  - Owner implementation instruction on 2026-09-04.
  IMPACT: The complete program now has explicit execution tasks and dependency boundaries.
  NEXT: Activate this task when its dependency milestone is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:31:19Z
  TYPE: FACT
  CLAIM: Added twelve Beginner chapters, explicit README-section selection, authored setup/registration/
    error/capstone guidance, and exact links into the existing lesson catalog. The strict site build
    passes at 158 pages. Read both test-document indexes and their verified bootstrap/isolation slices,
    plus the complete example conftest and Beginner harness. The actual fixture resets MutationResearch,
    Crystallizer, Nexus, and Aether and rebinds Spellbook/Conduit before and after each test.
  EVIDENCE:
  - docs/curriculum.toml
  - docs/tools/curriculum.py
  - UX_and_AIX_experiences/pytest_examples/conftest.py:39-74
  - UX_and_AIX_experiences/pytest_examples/test_beginner_examples.py:1-36
  - system_docs/tests_architecture.md:238-275
  - system_docs/tests_components.md:171-213
  - system_docs/tests_components.md:835-842
  IMPACT: The chapter sources and existing verification setup are understood. A separate free-threaded
    environment now has editable Melder 0.2.3, pytest 9.1.1, and the project test group installed.
  NEXT: Run the Beginner examples and the corpus metadata contract with a contained working directory.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:45:10Z
  TYPE: MEASURE
  CLAIM: Recovered the saved runtime report: all 41 Beginner scripts passed. The combined run had
    308 tests, 305 passed and 3 failures, with no errors/skips. Metadata failures name Intermediate
    cluster lesson 25 and Advanced logging lesson 04; the third failure is the aggregate floor.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/beginner.xml:1-1
  - docs/curriculum.toml:1-105
  - docs/tools/curriculum.py:15-152
  IMPACT: Beginner runtime verification is green. Later tasks must add meaningful source-backed
    assertions to the two named examples; no unrelated runtime change is authorized.
  NEXT: Extend the same curriculum registry through Intermediate, with direct lesson links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:09:36Z
  TYPE: DECISION
  CLAIM: The saved capstone currently puts registrations under with book and calls that an atomic
    registration batch. It defines all objects in one script and leaves resolved locals untyped.
    The chapter displays only main(), so imports and module boundaries are invisible to readers.
    Use three flat helper modules (models, bootstrap, application) plus the existing numbered entry.
    The catalog already downloads all flat Python helpers; no catalog format change is needed.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/40_beginner_capstone.py:1-65
  - docs/beginner/capstone.md:1-23
  - docs/tools/curriculum.py:99-151
  - docs/tools/example_catalog.py:97-133
  - docs/tools/example_catalog.py:233-257
  - UX_and_AIX_experiences/pytest_examples/test_beginner_examples.py:17-36
  IMPACT: Revise only the capstone chapter, its canonical script/helpers, its curriculum display flag,
    and the Beginner harness's sibling-import setup. Use ordinary constructor injection, shared config/
    pool, fresh handlers, meaningful outcome/cleanup assertions, and TYPE_CHECKING in the consumer.
  NEXT: Verify Spellbook.bind's admission/lock path before writing the new bootstrap explanation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:13:20Z
  TYPE: FACT
  CLAIM: Spellbook.bind executes registration within self.transaction('bind'); transaction opens/
    ends admission and marks failure on exceptions. Bind's strategy claims the book's scope before
    conjure. Spellbook.__enter__/__exit__ only acquire/release its lock. The capstone therefore must
    not teach with book as a requirement for normal binding or as an atomic registration guarantee.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5026-5290
  - src/melder/aether/spellbook/spellbook.py:4451-4548
  - src/melder/aether/spellbook/spellbook.py:738-781
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py:86-194
  IMPACT: Use direct registrations of config/pool/handler, plain constructor injection, and spell-name
    resolution so the consumer can import its concrete annotation types only under TYPE_CHECKING.
    Display every module through literalinclude; keep constructor dependency classes runtime-visible.
  NEXT: Implement the four-file application and run both its direct entry point and existing harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:18:51Z
  TYPE: FACT
  CLAIM: The first direct run reached conjure and failed to resolve RequestHandler.config.
    Phase 3 matches a concrete annotation against the bound object or its explicit spellframe,
    not type(instance). A prebuilt AppConfig therefore needs spellframe=AppConfig to advertise
    the constructor dependency shape; this is a registration correction, not a runtime defect.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/capstone_direct_20260905.log
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:175-246
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:272-337
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-504
  IMPACT: Teach the real configured-instance contract alongside constructor injection. Keep the
    consumer's concrete type imports under TYPE_CHECKING and its runtime lookup explicit.
  NEXT: Bind the configured instance under its AppConfig type and rerun the capstone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:21:29Z
  TYPE: FACT
  CLAIM: Adding the explicit AppConfig frame resolves the first dependency match but the current
    plan_group compiler then rejects the configured instance as not callable. Keep this capstone on
    ordinary class bindings with constructor defaults, which still teaches the requested module,
    bootstrap, typed consumer, injection, lifetime, and cleanup structure. Prebuilt-instance injection
    is a separately recorded runtime case; do not modify the concurrently changing compiler here.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/capstone_fixed_20260905.log
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:175-246
  IMPACT: Bind AppConfig as a class with its ordinary app_name default. Remove the unverified
    configured-instance explanation and verify the complete actual application before publication.
  NEXT: Run the class-bound capstone and then its isolated Beginner harness row.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:23:51Z
  TYPE: MEASURE
  CLAIM: The class-bound four-file capstone passes directly on the free-threaded interpreter.
    It returns all three expected order messages, proves shared config/pool and fresh handlers,
    and confirms pool.closed with three queries after shutdown. The guide now source-includes all
    four modules and explicitly explains self-mediated binding and TYPE_CHECKING consumer imports.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/capstone_class_20260905.log:1-5
  - UX_and_AIX_experiences/01_beginner/capstone_application.py:1-35
  - UX_and_AIX_experiences/01_beginner/40_beginner_capstone.py:1-44
  - docs/beginner/capstone.md:1-113
  IMPACT: The requested pattern is executable and the expected output is now observed. Existing
    harness and download-source checks remain before refreshing the browser and offline formats.
  NEXT: Run the Beginner harness/metadata checks and rebuild the public source/site.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:27:29Z
  TYPE: MEASURE
  CLAIM: All 308 combined Beginner execution/metadata checks pass, including all 41 runnable lessons.
    The only warning is pytest's shared cache directory creation race. All 36 documentation tests
    pass and strict HTML rendering completes at 294 pages with the four capstone source files included.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/capstone_beginner_20260905.xml:1-1
  - artifacts/rtd_validation_20260904/capstone_beginner_20260905.log
  - artifacts/rtd_validation_20260904/capstone_docs_tests_20260905.log:1-7
  - artifacts/rtd_validation_20260904/capstone_html_20260905.log:1-5
  IMPACT: The canonical application and harness integration are verified. Check the published
    helper downloads and refreshed page, then rebuild affected offline outputs and corpus assets.
  NEXT: Validate the complete HTML links and run the capstone from its extracted collection download.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Twelve Beginner chapters and the 41-lesson catalog are implemented. All 41 Beginner scripts pass on
Python 3.14t. The combined metadata run was 305 passed / 3 failed: two other-level scripts lack
behavioral assertions, plus the aggregate floor. Intermediate lesson 25 and Advanced lesson 04 own
those follow-ups. Finish integrated chapter/API navigation and final quality checks before acceptance.
Owner handles all commits/pushes; do not attempt signing or request a passphrase.
