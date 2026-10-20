# Task: Repair ManagedSpellMode failures on early Python 3.14 releases

- Completed: 2026-10-19T22:35:14Z
- Summary: Restored Spell constructor/mock reflection by importing ManagedSpellMode at runtime;
  all 51 reported cases pass. Added four regression cases, notched 0.2.8264 and added the release-note
  section "Spell constructor reflection works on early Python 3.14 releases"; generated assets are current.

## Metadata
- Task ID: TASK-2026-10-19-fix_managed_spell_mode_test_failures
- Story: none (standalone owner-directed repair)
- Status: done
- Owner: Mark
- Agent Name: expert_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-19T21:42:12Z
- Updated: 2026-10-19T22:35:14Z

## Objective
Repair the common cause of the owner's 41 failures and 10 setup errors mentioning
ManagedSpellMode on Python 3.14 releases below 3.14.4, preserving the tests' behavioral contracts.

## Problem / Context / MRP
The supplied report lists 51 unsuccessful cases across ConduitWard unit tests, SpellSystemStates
unit tests and the annotation-introspection component tests. Every listed error is NameError for
ManagedSpellMode. This is reported evidence, not a fresh local result. Diagnose the actual call
path before selecting a runtime or fixture repair; retain supported Python 3.14 behavior.

## Ticket Contract
- ENTRY_GATE: Completed role reads and attestation; owner named expert_1 and explicitly directed
  the repair after the attestation. Own roster row and active attention route must exist.
- EXECUTION_BOUNDARY: The reported test modules, their immediate fixtures, Spell annotations and
  signature-reflection call paths. Select exact edits from the reproduced cause. Include required
  regression tests, user documentation/version/generated assets only if source changes warrant them.
- DEPENDENCIES: Existing annotation-reflection and managed-bind contracts; no new dependencies,
  project onboarding, subagents, runtime policy changes, public API changes or unrelated defect lanes.
- EXIT_GATE: Every reported case executes successfully on a locally available affected interpreter;
  relevant annotation/mock regressions and the required runtime suite pass on the final source;
  distinct self-review and applicable asset checks are recorded. Unavailable matrix cells stay explicit.
- FAILURE_ESCALATION: Record an actual source-custody collision, unavailable interpreter/check,
  consequential design choice or tool denial; hold only that dependent scope.

## Scope Boundaries
- In scope: Reproduce and repair the supplied ManagedSpellMode failures, plus the same proven cause.
- Out of scope: Unrelated correctness stories, dependency upgrades, CI policy edits, pushes,
  merges, publication and use of other agents or machines.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Original cases, complete runtime tiers, post-notch checks, generated assets and
  distinct author self-review passed; routine closure is authorized by the owner's repair request.

## Steps / Checklist
- [x] Read the supplied failure list and current role/backend instructions.
- [x] Reproduce the cause and record source-backed diagnosis.
- [x] Apply the smallest correct repair and meaningful regression coverage.
- [x] Run the required affected and broader checks; record actual results and limits.
- [x] Perform distinct self-review and synchronize closure records.
- [x] Use the Ticket Microcycle; preserve attributed findings before dependent work.

## Deliverables
- Focused repair with the reported assertions retained.
- Reproducible before/after test evidence and a clear supported-version limit.
- Contribution notch 0.2.8264, running release note and regenerated package/LLM assets.

## Files / Paths Impacted
- tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py (reported surface)
- tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py (reported surface)
- tests/component/melder/spellbook/test_type_checking_annotation_introspection.py (reported surface)
- src/melder/aether/spellbook/spell.py: Move the existing ManagedSpellMode enum import to runtime.
- tests/unit/melder/spellbook/test_spell_constructor_introspection.py: Four direct regressions.
- src/melder/__version__.py; release_docs/next_version_release.md; required generated assets.
- Scoped component/test documentation, indexes and the two changed-source graph descriptors.
- context_compass/mailbox_board.md; attention_board.md; this task and its linked evidence.

## Validation
- Red: Four new regressions failed with the reported NameError on Python 3.14.2, GIL disabled.
- Green: 183/183 selected cases passed on Python 3.14.0 and 3.14.2, GIL disabled.
- Four constructor/spec cases also passed on 3.14.2 GIL enabled and 3.14.7 in both GIL postures.
- Corrected isolated 3.14.2 environment: 192/192 cases passed, including the nine library-digest cases.
- Complete runtime tiers: 14393 passed, 28 skipped, 17 xfailed, 3 xpassed; zero failures/errors;
  native driver exit 0 in 706.32s on local pinned Python 3.14.2, free-threaded with GIL disabled.
- The functional candidate ran at 0.2.8263; its spell.py hash is unchanged at landing. After the
  required metadata notch to 0.2.8264 and asset rebuild, 274 affected/version/cache cases passed.
- Source assets and all three LLM corpora check current; new regression source included explicitly.
- Earlier canceled attempts are preserved in Notes and are not counted as full-suite successes.
- Other OS CI cells and Python 3.14.1/3.14.3: Not run. Coverage measurement: Not run.
- A shutdown RuntimeWarning about an unawaited coro was emitted after the full passing summary;
  no failure, error or GIL-guard violation occurred. No warning suppression was added.
- Required: Reported modules and relevant reflection/mock regressions, then runtime suite.
- Base checkout: ada07499e5a8144e148b9e0caefbb12a3b2332a9.
- Existing unrelated dirty files at entry: Context Compass MANIFEST.md, general codex_mcp.md,
  issue_board.md and mailbox_board.md. Preserve their contents; expert_1 added only its roster row.

## Risks / Rollback Notes
- A fixture workaround could hide a production reflection contract; reproduce before selecting it.
- Do not widen concrete types, remove assertions, skip failures or change the Python support floor.
- Revert only this task's edits if a repair fails; preserve concurrent and pre-existing work.

## Applicable Anti-Patterns
- [x] No implementation from unevidenced diagnosis.
- [x] No accepted closure with failed/unrun required checks.
- [x] No assertion weakening or unexplained compatibility fallback.

## Done Checklist
- [x] Criteria met and evidence linked.
- [x] Necessary documentation/assets current.
- [x] Validation and limitations recorded truthfully.
- [x] Self-review identified as self-review.
- [x] Canonical route and artifact state reconciled.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/managed_spell_mode_failures_20261019/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain the input report, reproduction and final check receipts on closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: []
- CONTEXT_TOPICS: []
- IF_UNKNOWN: none

## Noting Behavior
- Tactical source findings, effects, limits and one next action; preserve history.
- Record each meaningful result once with source ranges and a usefulness score of at least 7.

## Contribution Attribution
- Ticket/Work Author(s): expert_1; synaptic_python_developer; intake and repair; this task.
- Published By: Local Codex file tools on Mark's machine; no remote publication.
- Independent Review: Not performed or required; expert_1 completed distinct author self-review.

## Notes
- DATETIME: 2026-10-19T21:42:12Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner's report lists 41 failures and 10 errors, all naming ManagedSpellMode, on
    Python releases below 3.14.4. The report has no traceback and does not identify exact cells.
    Mark named expert_1 and authorized this repair after the completed onboarding attestation;
    this is direct owner authorization, not an invented literal certification-token receipt.
  EVIDENCE:
  - artifacts/managed_spell_mode_failures_20261019/input_report.txt:1-58
  - Owner message in this chat, 2026-10-19, assigning expert_1 and directing the test repair.
  IMPACT: Diagnose one common failure before altering 51 cases; preserve initial matrix uncertainty.
  NEXT: Reproduce one failing fixture on an affected installed interpreter and read its call path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T21:46:47Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Reproduced MagicMock(spec=Spell) raising NameError on local Python 3.14.2 free-threaded,
    GIL disabled. unittest.mock._get_signature_object reads Spell.__init__ through the default
    inspect.signature VALUE format; its managed_spell_mode annotation names the enum imported
    only under TYPE_CHECKING. The enum is a dependency-free value type, not an injected collaborator.
    Move that existing import beside Existence. Preserve annotations, fixtures, assertions and
    runtime control flow. Add four constructor/spec regressions before the source edit.
  EVIDENCE:
  - artifacts/managed_spell_mode_failures_20261019/reproduce_mock_3142.txt:1-57
  - src/melder/aether/spellbook/spell.py:1-61
  - src/melder/aether/spellbook/spell.py:319-347
  - src/melder/aether/spellbook/existence/managed_spell_mode.py:1-91
  - tickets/stories/completed/2026-10-15_managed_bind_options_story.md:279-304
  IMPACT: This restores the earlier managed-bind introspection decision for Spell, missed by the
    recorded import changes. No lifecycle, ownership, API signature or compiler behavior redesign.
    Full Spell source (2027 lines), enum and the relevant reflection path have been read.
  NEXT: Run the four new tests red on 3.14.2, then move the import and rerun all reported modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T21:50:00Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: All four new constructor/spec regressions failed with the original ManagedSpellMode
    NameError on Python 3.14.2 before the source edit. Moving the enum import to runtime made
    all 183 cases in the four selected modules pass on both 3.14.0 and 3.14.2 (GIL disabled).
    The four new cases also pass on 3.14.2 with the GIL enabled and 3.14.7 in both postures.
    The original three test modules and their assertions are unchanged. The complete runtime
    driver is now running on 3.14.2; its result is still pending.
  EVIDENCE:
  - artifacts/managed_spell_mode_failures_20261019/red_3142.xml
  - artifacts/managed_spell_mode_failures_20261019/affected_3140_gil0.xml
  - artifacts/managed_spell_mode_failures_20261019/affected_3142_gil0.xml
  - artifacts/managed_spell_mode_failures_20261019/constructor_3142_gil1.xml
  - artifacts/managed_spell_mode_failures_20261019/constructor_3147_gil0.xml
  - artifacts/managed_spell_mode_failures_20261019/constructor_3147_gil1.xml
  IMPACT: One source import fixes the shared setup failure without changing the tested contracts.
    The optional enum retains its concrete type and keyword-only None-default signature.
  NEXT: Complete broader verification, then finish required version/documentation/assets and self-review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T22:03:04Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The first broad run observed four failures in test_spell_code_digest_libraries.py, not
    in the reported cases. Its setup borrowed .venv_new/site-packages through PYTHONPATH, outside
    the selected interpreter's recognized site roots, so installed packaging code was treated as
    application code. Reproduced all four separately, then created an isolated local 3.14.2 venv
    and copied the nine already-installed distributions matching CI's exact 3.14.2 manifest pins.
    No network, dependency upgrade, digest edit or test weakening. All 192 cases (affected modules,
    constructor regressions and library-digest module) pass in the corrected environment.
    The invalid broad run was canceled; a complete rerun began in the corrected venv at 22:03Z.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_code_digest.py:1170-1246
  - artifacts/managed_spell_mode_failures_20261019/environment_diagnosis.txt
  - artifacts/managed_spell_mode_failures_20261019/environment_preparation.json
  - artifacts/managed_spell_mode_failures_20261019/cleanenv_3142_gil0.xml
  - artifacts/managed_spell_mode_failures_20261019/verification_receipt.json
  IMPACT: All 51 original node IDs are verified passing on both 3.14.0 and 3.14.2; the broader
    acceptance remains pending a complete, correctly configured runtime run.
  NEXT: Complete the corrected runtime run and final contribution checks before accepting closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T22:14:49Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The corrected sandbox run passed the library-digest and constructor regressions, then
    stalled before the coroutine body in test_async_cleanup_defers_to_cleanup. The 120-second
    fault dump shows asyncio creating its self-pipe through socket._fallback_socketpair, blocked
    in socket.accept. The run was canceled. Through the supported per-command approval route,
    that exact test passed outside the sandbox in 0.27 seconds. An approved full local rerun
    began at 22:13Z in the same pinned 3.14.2 environment and has cleared the stalled area.
    No test, sandbox configuration, firewall rule, account or model setting was changed.
  EVIDENCE:
  - artifacts/managed_spell_mode_failures_20261019/runtime_cleanenv_3142_gil0.txt:9146-9161
  - tests/unit/melder/utilities/general_base/test_cleanable.py:35-44
  - artifacts/managed_spell_mode_failures_20261019/socket_check_unsandboxed.xml
  - artifacts/managed_spell_mode_failures_20261019/runtime_local_3142_gil0.txt
  IMPACT: The loopback-dependent check has a verified execution path on Mark's machine;
    full-runtime acceptance still waits for the approved run's terminal result.
  NEXT: Follow native exec session 71106 to completion, then finish contribution assets and self-review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T22:23:46Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Distinct intentional functional self-review completed against the exact source diff
    and the full new regression file. Production diff is solely the existing enum import moved
    out of TYPE_CHECKING; method bodies, annotations and lifecycle code are unchanged. The three
    original reported test modules have no diff. New cases check real VALUE-format signatures,
    keyword-only/None defaults and retained Mock/MagicMock member restrictions; no skip, xfail,
    assertion weakening, Any fallback or dependency change. Full-runtime acceptance is pending.
    Documentation preservation permits only measured inventory replacements; all 280 actual
    catalog key-file references match existing C1 records. Regenerated indexes and graph check.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1-61
  - tests/unit/melder/spellbook/test_spell_constructor_introspection.py:1-53
  - artifacts/managed_spell_mode_failures_20261019/verification_receipt.json
  IMPACT: The candidate meets the intended narrow repair; this is author self-review, not
    independent review or accepted full-runtime completion. Final version/assets remain to finish.
  NEXT: Complete native exec 71106, then take the contribution notch and verify generated assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T22:35:14Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: ACCEPTANCE authorized for this bounded owner-directed repair. VALIDATION recorded:
    all 51 original node IDs pass on 3.14.0 and 3.14.2 and in the complete approved local runtime
    run (14393 passed, 28 skipped, 17 xfailed, 3 xpassed; zero failures/errors, exit 0, 706.32s).
    Source import fix hash remains 1ed5801af785e9d54c7c2e275e19a97b3e902f8835e3502b1c504cd8adf6834f.
    Notched 0.2.8264; the post-notch affected/version/cache selection passed 274 cases. All package
    assets and three LLM corpora rebuilt and checked current. Final diff self-review confirms
    original test modules unchanged, the one import move, new four-case regression and only
    required contribution metadata/docs/generated outputs. CHILDREN none. ROUTING reconciled
    in this closure pass; retained input, red/green and final verification evidence, removed only
    task-owned temporary environments, graph staging, caches and pytest scratch directories.
  EVIDENCE:
  - artifacts/managed_spell_mode_failures_20261019/verification_receipt.json
  - artifacts/managed_spell_mode_failures_20261019/runtime_local_3142_gil0.xml
  - artifacts/managed_spell_mode_failures_20261019/landing_3142_gil0.xml
  - artifacts/managed_spell_mode_failures_20261019/assets_check.txt
  - artifacts/managed_spell_mode_failures_20261019/llm_check.txt
  - release_docs/next_version_release.md
  IMPACT: The common annotation failure is repaired with preserved test strength and supported
    Python floor. This closes this repair only, not unrelated correctness work or the hosted matrix.
    Source/version/build checks were actually executed; self-review is not independent review.
  NEXT: Return the completed repair and verification limits to Mark; no dependent work remains.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
expert_1 owns the ManagedSpellMode repair from base ada07499e5a8144e148b9e0caefbb12a3b2332a9.
Completed at 0.2.8264. The source change moves the existing ManagedSpellMode enum import to runtime;
all 51 original node IDs pass. Complete runtime tiers passed 14393 cases with no failures/errors;
274 post-notch affected/version/cache cases also passed. Four regression cases, scoped docs,
indexes, graph metadata, running release note and generated assets are current. Earlier canceled
runs and the shutdown warning are preserved above; no false full-matrix/coverage/independent-review
claim. Input and test/build receipts are retained; temporary test setup was removed. No source
push, merge, release publication, account change or other-agent execution. Other agents' original
dirty Context Compass files remain preserved. No remaining repair action.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
