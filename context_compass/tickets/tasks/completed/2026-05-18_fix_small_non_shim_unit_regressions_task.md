# Task: fix small non-shim unit regressions

- Completed: 2026-05-22T00:19:54Z
- Summary: Closed during board cleanup after the small non-shim regression lane was removed from active routing.


## Metadata
- Task ID: TASK-2026-05-18-fix-small-non-shim-unit-regressions
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_1
- Priority: p1
- Created: 2026-05-18T13:14:46Z
- Updated: 2026-05-22T00:19:54Z

## Objective
Fix the next easy non-shim unit-test regressions from the broader `tests/unit`
ring without stepping into the large spell-crafter/shim bucket another agent is
already handling.

## Ticket Contract
- ENTRY_GATE: user explicitly asked to keep fixing other test problems while avoiding the shim lane
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/aether/test_aether.py`
  - `tests/unit/melder/aether/test_frame_acl_codegen_configuration.py`
  - `tests/unit/melder/aether/test_frame_acl_command_configuration.py`
  - `tests/unit/melder/aether/test_frame_acl_command_profile.py`
  - `tests/unit/melder/aether/test_nexus.py`
  - `tests/unit/melder/aether/test_nexus_frame_manager.py`
  - `tests/unit/melder/utilities/logger/test_safe_logger.py`
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/utilities/logger/safe_logger.py`
  - small runtime files only if the tests expose a real localized bug rather
    than a stale expectation
- DEPENDENCIES:
  - current unit-suite output after conduit/non-shim fixes
- EXIT_GATE:
  - the small Aether cleanup expectation bucket is resolved
  - the small ACL error-message expectation bucket is resolved
  - the next small Nexus / NexusFrameManager / SafeLogger expectation or
    localized runtime buckets are reduced
  - no work drifts into the giant spell-crafter failure cluster
- FAILURE_ESCALATION: raise `BLOCKER` if these failures actually mask a broader
  architectural/runtime break

## Scope Boundaries
- In scope:
  - small expectation updates where runtime semantics are already clear
  - tiny runtime fixups when a localized bug is directly evidenced
- Out of scope:
  - conduit/shim lane already stabilized separately
  - giant spell-crafter failure cluster
  - integration suite triage lane

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: broader unit rerun exposed a few easy non-shim buckets that
  can be fixed quickly without colliding with the shim agent

## Steps / Checklist
- [ ] confirm the small Aether cleanup expectation drift
- [ ] confirm the small ACL error-message expectation drift
- [ ] patch the smallest correct tests/runtime surfaces
- [ ] rerun the narrowed unit buckets
- [ ] document the reduced failure surface before picking the next bucket

## Deliverables
- fewer non-shim unit regressions in the broad unit ring

## Files / Paths Impacted
- `tests/unit/melder/aether/test_aether.py`
- `tests/unit/melder/aether/test_frame_acl_codegen_configuration.py`
- `tests/unit/melder/aether/test_frame_acl_command_configuration.py`
- `tests/unit/melder/aether/test_frame_acl_command_profile.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_aether.py`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_frame_acl_codegen_configuration.py tests\unit\melder\aether\test_frame_acl_command_configuration.py tests\unit\melder\aether\test_frame_acl_command_profile.py`

## Risks / Rollback Notes
- Low to medium risk. These look like localized expectation drift, but if they
  hide a broader cleanup/error-model contract change we need to stop and raise.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No drift into the big spell-crafter cluster.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Noting Behavior
- Note focus: small factual buckets, exact evidence, and one next step at a time.

## Notes
- DATETIME: 2026-05-18T13:14:46Z
  TYPE: FACT
  CLAIM: After the conduit/unit cleanup, the next easy non-shim buckets in the
    broad unit ring are small Aether cleanup expectation drift and small ACL
    error-message expectation drift. The giant spell-crafter cluster remains
    large and should stay out of this slice.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit`
  - tests/unit/melder/aether/test_aether.py:157-157
  - tests/unit/melder/aether/test_aether.py:425-438
  - tests/unit/melder/aether/test_frame_acl_codegen_configuration.py:54-55
  - tests/unit/melder/aether/test_frame_acl_command_configuration.py:95-96
  - tests/unit/melder/aether/test_frame_acl_command_profile.py:80-80
  IMPACT: These are good next targets because they are small, isolated, and do
    not require colliding with the shim/spell-crafter lane.
  NEXT: inspect those specific tests and the corresponding runtime semantics,
    then patch the smallest correct expectation/runtime surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:23:45Z
  TYPE: MEASURE
  CLAIM: The small non-shim Aether/ACL tranche is materially reduced. The
    ConduitCloud unit ring is passing on the new frame-facade contract, the
    Nexus cold-start singleton teardown bug is fixed, the Aether cleanup tests
    are aligned to delete-on-clean semantics, and the small ACL expectation
    drift is mostly gone. The broad unit ring is now down to 272 failures and
    is dominated by the large spell-crafter cluster rather than these small
    Aether/ACL buckets.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_conduit_cloud.py`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_aether.py tests\unit\melder\aether\test_frame_acl_configuration.py tests\unit\melder\aether\test_frame_acl_profile.py tests\unit\melder\aether\test_frame_acl_view_configuration.py tests\unit\melder\aether\test_frame_acl_profile_builder.py tests\unit\melder\aether\test_frame_acl_compiler_contracts.py tests\unit\melder\aether\test_frame_acl_validator.py`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit`
  - src/melder\aether\nexus\nexus.py:170-176
  - src/melder\aether\conduit_cloud.py:30-74
  IMPACT: The easy non-shim noise floor is lower now. The next meaningful work
    should either continue the remaining small Aether/Nexus/ACL expectation
    buckets or deliberately enter the much larger spell-crafter failure cluster.
  NEXT: choose the next non-shim bucket explicitly before widening into the
    spell-crafter mass-failure set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:38:05Z
  TYPE: MEASURE
  CLAIM: After the conduit-unit and small Aether/ACL reductions, the next small
    non-shim buckets in the broad unit ring are `Nexus` / `NexusFrameManager`
    expectation drift and two `SafeLogger` channel-path tests. The broad unit
    ring is still dominated by the giant spell-crafter failure cluster, but
    these smaller buckets remain cheap to shave without entering that lane.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit`
  - tests/unit/melder/aether/test_nexus.py:820-820
  - tests/unit/melder/aether/test_nexus.py:3697-3697
  - tests/unit/melder/aether/test_nexus.py:6012-6012
  - tests/unit/melder/aether/test_nexus_frame_manager.py:364-437
  - tests/unit/melder/utilities/logger/test_safe_logger.py:114-151
  IMPACT: The next focused slice can keep reducing non-shim noise without
    touching the spell-crafter/shim mass-failure area.
  NEXT: inspect the current Nexus / NexusFrameManager runtime behavior and the
    SafeLogger channel-path behavior, then patch the smallest correct runtime
    or test expectations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T13:38:05Z
  TYPE: FACT
  CLAIM: The next reduced non-shim buckets are now explicit: `Nexus` later
    constructor calls ignore explicit logger overrides despite the docstring
    claiming they may refresh the logger, `NexusFrameManager` tests still use
    a fake Nexus surface without the public `configuration` property that the
    runtime now reads, and the remaining `SafeLogger` failures are isolated to
    the channel-path tests.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit`
  - tests/unit/melder/aether/test_nexus.py:808-820
  - src/melder/aether/nexus/nexus.py:144-176
  - tests/unit/melder/aether/test_nexus_frame_manager.py:152-181
  - src/melder/aether/nexus/nexus_frame_manager.py:1055-1062
  - tests/unit/melder/utilities/logger/test_safe_logger.py:114-151
  - src/melder/utilities/logger/safe_logger.py:120-191
  IMPACT: These are still small enough to fix without entering the giant
    spell-crafter cluster, and at least one of them (`Nexus` logger override)
    is a real runtime/docstring mismatch rather than just stale tests.
  NEXT: run the narrowed Nexus/NexusFrameManager/SafeLogger tests and patch the
    smallest correct runtime or test surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T19:50:10Z
  TYPE: FACT
  CLAIM: The narrowed rerun separates the remaining work cleanly. The
    `SafeLogger` ring is now green. `test_nexus.py` is down to one stale
    static-command expectation and one real external frame-cleanup regression.
    `test_nexus_frame_manager.py` is mostly fake-surface drift: the fake root
    conduit spellbook only exposes `id`, the fake Nexus still lacks
    `_get_required_frame_descriptor(...)`, and the cleanup-matrix assertions
    still expect lists where the real manager contract returns tuples.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_nexus.py`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_nexus_frame_manager.py`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\logger\test_safe_logger.py`
  - tests/unit/melder/aether/test_nexus.py:3697-3701
  - tests/unit/melder/aether/test_nexus.py:6004-6012
  - tests/unit/melder/aether/test_nexus_frame_manager.py:47-62
  - tests/unit/melder/aether/test_nexus_frame_manager.py:175-213
  - tests/unit/melder/aether/test_nexus_frame_manager.py:736-792
  - src/melder/aether/nexus/nexus_frame_manager.py:584-664
  - src/melder/aether/nexus/nexus_frame_manager.py:1114-1115
  - src/melder/aether/aetheric_frame.py:119-146
  - src/melder/aether/conduit/conduit.py:397-405
  - src/melder/aether/conduit_cloud.py:363-389
  IMPACT: The next patch split is now clear. The frame-cleanup failure is a
    localized runtime regression in the post-conduit-migration detach path,
    while most of the frame-manager failures can be reduced by aligning the
    tests and fakes to the real manager contract.
  NEXT: restore the last-root-conduit frame cleanup callback through
    `ConduitCloud`, then patch the `NexusFrameManager` test doubles and tuple
    expectations before rerunning the narrowed bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
