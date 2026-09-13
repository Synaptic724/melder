# Task: Verify named-binding lookup through public meld calls

## Metadata
- Task ID: TASK-2026-09-13-named-binding-meld-lookup-test
- Story: none
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T11:46:49Z
- Updated: 2026-09-13T12:09:53Z

## Objective
Test whether a class bound with binding_name="test" can be melded by its class name alone,
by name plus the binding qualifier, or by the binding name alone. Report exact outcomes.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requests this test; existing updater_0 certification remains active.
- EXECUTION_BOUNDARY: The existing human-name experiment and this ticket's evidence; no runtime changes.
- DEPENDENCIES: Current public Spellbook/Conduit APIs and .venv_new Python 3.14.7 free-threaded.
- EXIT_GATE: Executed tests establish return/error behavior and identity parity for successful calls.
- FAILURE_ESCALATION: Record unexpected behavior without changing production lookup semantics.

## Scope Boundaries
- In scope: omitted versus explicit binding qualifier; binding-only inputs; before/after a successful lookup.
- Cover automatic pre-conjure binding and dynamic pre/post-conjure binding.
- Include explicit string/type spellframes, missing frame qualifiers and matching frame/class-name keys.
- Out of scope: cache optimization, named-conduit implementation and API changes.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: All requested lookup variants and identity checks were executed successfully.

## Steps
- [x] Locate the recent human-name experiment and inspect the relevant component/source path.
- [x] Add scoped public-API tests with isolated lifecycle cleanup.
- [x] Execute on Python 3.14.7 and report exact successful and failing call forms.
- [x] Verify explicit spellframes and omission behavior across all three lifecycle modes.

## Deliverables
- Extended tests/experimentation/test_meld_human_spell_name_string_experiment.py.
- Test output and concise interpretation retained with this ticket.

## Validation
- 16 tests passed in 0.41 seconds on CPython 3.14.7 free-threaded; scoped Ruff and whitespace checks pass.
- Follow-up: 25 tests passed in 0.56 seconds, including all prior cases and nine frame cases.

## Risks / Rollback Notes
- A prior successful lookup must not mask a missing binding qualifier through input-cache aliasing.
- Use unique existence to distinguish identical target resolution from separate new instances.
- Preserve unrelated working changes and runtime behavior.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/named_binding_meld_20260913/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain the executable test evidence at owner-approved closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-13T11:46:49Z
  TYPE: FACT
  CLAIM: The recent human-name test binds MyService with binding_name="primary" and checks
    explicitly qualified positional/keyword names against spell_id. It does not omit the qualifier.
    Meld resolves normalized lookup keys exactly and raises KeyError for a missing key.
  EVIDENCE:
  - tests/experimentation/test_meld_human_spell_name_string_experiment.py:1-33
  - src/melder/aether/conduit/meld/meld.py:1247-1453
  - system_docs/src_components.md:2457-2591
  IMPACT: Extend the existing experiment; test missing qualifiers both before and after a
    successful explicit lookup to expose any input-cache aliasing.
  NEXT: Read key normalization and the public input guard, then add the requested test cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T11:46:49Z
  TYPE: FACT
  CLAIM: Key normalization uses (frame_or_name, binding_name_or_default), lowercasing both.
    Omitting binding_name selects __default__, whereas a named registration uses test.
    Meld performs an exact lookup rather than a fallback scan. Added real-API cases across
    automatic prebind and dynamic pre/postbind, including before/after successful lookup behavior.
  EVIDENCE:
  - src/melder/utilities/helpers/general_helpers.py:300-423
  - src/melder/aether/conduit/meld/meld.py:1247-1453
  - tests/experimentation/test_meld_human_spell_name_string_experiment.py:44-152
  IMPACT: Tests assert exact failure categories and unique-instance parity without altering runtime code.
  NEXT: Execute the extended experiment and capture all call outcomes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T11:51:07Z
  TYPE: MEASURE
  CLAIM: The original test passed; all 15 new cases stopped in fixture setup because the
    experiment omitted configure_aether_frame's required disposal and disposal_method_names
    arguments. No lookup behavior was exercised by those failed setup cases.
  EVIDENCE:
  - artifacts/named_binding_meld_20260913/setup_failure.log
  - src/melder/aether/spellbook/spellbook.py:6033-6059
  IMPACT: Correct the test fixture with the same explicit None values used in the prior benchmark.
  NEXT: Re-run the extended file after this two-argument setup correction.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-13T11:51:53Z
  TYPE: MEASURE
  CLAIM: Eleven cases passed before fail-fast stopped on a message-format assertion. Omitted
    binding raises KeyError before and after named resolution; explicit call forms return one
    unique object; binding keyword alone raises ValueError. The quoted assignment-text case also
    raised the expected KeyError, but str(KeyError) escaped its inner quotes and defeated the regex.
  EVIDENCE:
  - artifacts/named_binding_meld_20260913/message_assertion_failure.log
  IMPACT: Correct the test's message check to compare the raw exception argument, then finish all cases.
  NEXT: Re-run the full file with the raw-message assertion.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-13T11:53:50Z
  TYPE: MEASURE
  CLAIM: All 16 tests passed in 0.41 seconds. Omitting the named binding raises KeyError for
    __default__, before and after explicit success. Qualified name/class and SHA calls return
    the same unique instance. Binding-only keyword raises ValueError; positional binding value
    or assignment text raises KeyError. Results agree across automatic prebind and dynamic
    pre/postbind. Scoped Ruff correctness and git whitespace checks pass.
  EVIDENCE:
  - artifacts/named_binding_meld_20260913/results.xml
  - artifacts/named_binding_meld_20260913/results.log:1-18
  - artifacts/named_binding_meld_20260913/results.md:1-43
  - tests/experimentation/test_meld_human_spell_name_string_experiment.py:44-143
  IMPACT: The named registration does not create a default-binding alias and does not return
    blank/None when the qualifier is omitted. No runtime behavior was modified.
  NEXT: Owner reviews the observed lookup contract and retained tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T12:09:20Z
  TYPE: PLAN
  CLAIM: Owner extends the test to explicit spellframe registrations and requests meld with
    binding_name but without spellframe. Normalization selects spellframe over the class name,
    so test distinct frame names, frame-name positional input and the equal-normalized-name edge.
  EVIDENCE:
  - src/melder/utilities/helpers/general_helpers.py:332-423
  - src/melder/aether/conduit/meld/meld.py:1247-1453
  - Owner's explicit-spellframe follow-up in this conversation.
  IMPACT: Distinguish omission of the spellframe keyword from omission of the logical frame identity.
    Extend the same experiment and reuse its three lifecycle modes; preserve current runtime semantics.
  NEXT: Add framed binding cases, including failures before and after a fully qualified success.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-13T12:09:53Z
  TYPE: MEASURE
  CLAIM: The full file passes 25 tests in 0.56 seconds. A distinct spellframe changes the
    address: class-name plus binding_name without the frame raises KeyError before and after
    qualified success. Explicit frame plus binding succeeds; the frame name/type can also be
    positional. Binding-only keyword remains ValueError. A frame equal to the class name works
    without the keyword because the normalized key is identical. String/type frames and all
    three lifecycle modes pass; scoped Ruff and whitespace checks pass.
  EVIDENCE:
  - artifacts/named_binding_meld_20260913/framed_results.xml
  - artifacts/named_binding_meld_20260913/framed_results.log
  - artifacts/named_binding_meld_20260913/results.md:46-68
  - tests/experimentation/test_meld_human_spell_name_string_experiment.py:157-226
  IMPACT: Omission of the spellframe keyword is possible only if another supplied identifier
    produces the correct frame key. The runtime does not infer a frame from binding_name alone.
  NEXT: Owner reviews the explicit-frame lookup result; no runtime change was requested or made.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed and in review: 25 tests pass. Named bindings do not get a default alias. An explicit
spellframe replaces the class-name key; omitting a distinct frame fails even when binding_name
is supplied. Passing the frame identity positionally works, as does SHA lookup. Equal frame/class
names yield the same key. See the results artifact and framed_results logs for exact call forms.
