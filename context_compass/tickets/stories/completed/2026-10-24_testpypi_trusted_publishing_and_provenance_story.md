# Story: testpypi_trusted_publishing_and_provenance - TestPyPI uploads carry verified provenance

- Completed: 2026-10-25T00:38:43Z
- Summary: TestPyPI uploads by Trusted Publishing with PEP 740 attestations - the publish action pinned to its
  commit, `id-token: write` on that job alone, no secret - and RC / provenance verifies every built file's
  provenance in five layers before any probe installs it, with the signer's own toolchain from a hashed lock,
  proven each run on a recorded attestation and two tampered copies (681 workflow tests, GIL off and on). No src,
  no notch, no release-note entry; hosted runs Not run; the owner adds the TestPyPI publisher before promotion.

## Metadata
- Story ID: STORY-2026-10-24-testpypi_trusted_publishing_and_provenance
- Epic: EPIC-2026-10-24-pypi_provenance_attestations
- Status: done
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T23:21:18Z
- Updated: 2026-10-25T00:38:43Z

## User Narrative
As Melder's owner, I want every candidate file the release candidate uploads to TestPyPI to go up through Trusted
Publishing with a PEP 740 attestation, and the release candidate to verify that attestation against this exact run
before any probe installs the file, so that a candidate reaches prod only when its provenance proves it came from
this repository's release-candidate workflow at this commit.

## Value / MRP Alignment
Stories S1 and S2 of the epic as one change (D5): the upload switch ships with the check that proves it, so no
candidate is ever published with an attestation nobody verifies. The check is the epic's D3 depth: five layers,
every claim pinned, the tool proven on known answers in every run.

## Ticket Contract
- ENTRY_GATE: the owner's go (chat 2026-10-24: "why don't you just check to see how deep it goes bro I don't know
  lets go super deep so we can properly build this out"); the epic in progress; this story's board row;
  `.github/ci_cd/` read before the first `.github` edit (done 2026-10-24).
- EXECUTION_BOUNDARY: `.github/workflows/release-candidate.yml` (the publish job; a new provenance job; the install
  and package-ready needs); `.github/scripts/testpypi_candidate.py` (prepare-upload reports the files it stages),
  `.github/scripts/ci_policy.py` (`CANDIDATE_JOBS`) and a new standard-library `.github/scripts/testpypi_provenance.py`;
  a new `.github/provenance/` (the verifier that runs in the pinned tool environment, its hashed lock and the recorded
  known-good attestation); `tests/unit/github_workflows/`; `.github/ci_cd/`; `.github/BRANCH_WORKFLOW.md` (its
  TestPyPI sections); `context_compass/system_docs/tests_components.md` and its index; the asset and LLM-bundle
  rebuild last. Not `python-publish.yml` (S3), not `src/` (no notch), no release-note entry (users install from
  PyPI; S3 and S5 carry the user-facing line).
- DEPENDENCIES: the owner's TestPyPI Trusted Publisher (epic D2) before this change reaches release_candidate; the
  promotion chain; hosted runs are the owner's.
- EXIT_GATE: the acceptance criteria hold with `tests/unit/github_workflows` green with the GIL off and on and the
  verifier run locally against its controls; hosted runs reported "Not run" until the owner shares them; board and
  epic synced; the rebuild checks print only OK.
- FAILURE_ESCALATION: BLOCKER when the pinned closure cannot install on the helper release; DECISION_REQUEST when a
  D3 layer cannot be enforced as designed (for example a claim the certificate lacks); CONFLICT when another lane
  takes `.github/`.

## Requirements (Functional)
- The publish job uploads through Trusted Publishing (`id-token: write` on that job only; no `user`, no `password`, no
  secret anywhere in the workflow) with attestations on, through the publish action pinned to its commit (epic D7),
  and reports the files it staged and its run attempt as job outputs.
- A provenance job (RC / provenance) after publish, and before install, checks every built file: (1) TestPyPI holds a
  provenance; (2) its one bundle's publisher record names `Synaptic724/melder`, `release-candidate.yml` and
  `pypitest`; (3) Sigstore verifies its one attestation on the production trust root; (4) the certificate's identity
  matches claim by claim, this run's id and the publish attempt for the files this run uploaded, another run of this
  repository at the same commit for files TestPyPI already had; (5) the statement names exactly the file and its
  sha256 with the PyPI publish predicate. Before the candidate it proves the tool: a recorded known-good attestation
  must verify and two tampered copies must be refused.
- `package-ready` requires six stages (`CIPolicy.CANDIDATE_JOBS` with `provenance`).

## Requirements (Non-Functional)
- `.github/scripts/` stays standard-library only, enforced by a new contract test that names its two existing
  environment-bound exceptions (`run_runtime_tests.py`: pytest; `smoke_wheel.py`: melder).
- The tool installs from exact pins with hashes (`--require-hashes --no-deps --only-binary=:all:`) into a fresh
  environment of the helper release; nothing floats.
- Unit tests make no network calls; every refusal names the file, what was expected and what was found.

## Scope Boundaries
- In scope: the boundary above.
- Out of scope: PyPI publication (S3), token retirement (S4), user documentation (S5), build provenance (S6).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: every acceptance criterion holds locally (Notes from 2026-10-25T00:09:35Z); the exit gate
  leaves hosted runs Not run until the owner shares them; the owner's gates move to the epic. Earlier: draft ->
  in_progress, opened on the owner's go as the epic's first story (D5).

## Dependencies / Related Work
- EPIC-2026-10-24-pypi_provenance_attestations (D2, D3, D5, D6, D7).

## Tasks (Implementation Checklist)
- [x] The workflow, the policy list and prepare-upload's output.
- [x] `testpypi_provenance.py`, the verifier, the lock and the control.
- [x] Tests: contract, policy, publication, provenance.
- [x] Docs: `.github/ci_cd/`, BRANCH_WORKFLOW.md, the tests map (and tests_architecture, its stale extent).
- [x] Turn in; the rebuild runs last, after this closure, and its result goes in the epic.
- [x] Enforce Ticket Microcycle across all linked tasks (no child tasks; the story's Notes carry each tranche).
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Contract tests pin: the publish job's permissions and inputs, the pinned action, no secret in the workflow,
  `id-token` on no other job, the provenance job's wiring, install and package-ready needing it.
- Unit tests prove every layer's accept and refuse paths on recorded and synthetic certificates, the retries, the
  control decision and the report, with no network.
- The verifier verifies the recorded control and refuses both tampered copies in a tool environment built from the
  lock (run locally).
- The CI guide and BRANCH_WORKFLOW.md describe the new posture; the tests map covers the new test file.

## Validation / Test Plan
- `python -X gil=0 -m pytest tests/unit/github_workflows -q` and the same with `-X gil=1`.
- The verifier against its controls in a tool environment built from the lock.
- Hosted: the first RC run on a fresh candidate version after the owner adds the TestPyPI publisher ("Not run").

## UX / API / Data Notes
- No public API change. New report artifact: `candidate-provenance-<run>-<attempt>`.

## Risks / Mitigations
- TestPyPI's Integrity API route is UNKNOWN until a hosted run (epic Open Questions): a 404 is retried, then refused
  with a message naming each file and the likely causes.
- Fulcio or GitHub changes a claim (a new runner label, an OIDC subject template): the refusal names the claim, the
  expected and the found value; the policy lives in one class.
- The tool closure is large (33 distributions): exact pins with hashes, the signer's own versions, its own
  environment, proven by the controls each run.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence (no child tasks; Notes carry the evidence).
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None blocking; the TestPyPI route is UNKNOWN (Risks).

## Decision Log
- The epic's D3 (depth), D5 (one story), D6 (the tool) and D7 (the pinned action) govern this story.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_2 (synaptic_python_developer); prose, design, implementation, test; this story.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none; the owner's commit review and the first hosted RC run are the remaining gates

## Notes
- DATETIME: 2026-10-24T23:21:18Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The current wiring. The publish job holds `contents: read`, checks `secrets.melder_api_token` and uploads
    `upload/` with the token and `attestations: false` through `pypa/gh-action-pypi-publish@release/v1`; install
    needs authorize, build and publish; package-ready needs the five `CIPolicy.CANDIDATE_JOBS`, and
    `require_candidate_success` says "all five stages". prepare-upload stages only the files TestPyPI lacks and
    writes only `upload-required`. Same-commit rebuilds hash the same (SOURCE_DATE_EPOCH, normalized sdist), so a
    file TestPyPI already has came from an earlier run at this commit. Third-party actions are pinned by commit
    (`astral-sh/setup-uv@20cfd1bf...`); `actions/*` by major tag.
  EVIDENCE:
  - .github/workflows/release-candidate.yml:55-160
  - .github/scripts/ci_policy.py:14-24
  - .github/scripts/ci_policy.py:198-205
  - .github/scripts/testpypi_candidate.py:161-172
  - .github/scripts/testpypi_candidate.py:276-291
  - .github/workflows/build-distributions.yml:46-63
  IMPACT: The change set is the publish job, a new job, two needs lists, one tuple, one message and one output.
  NEXT: Write the PLAN note, then implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T23:21:18Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Goal: (1) TestPyPI uploads by OIDC with attestations; (2) every built file's provenance verified in five
    layers before install; (3) the tool pinned and proven each run; (4) contract and unit tests; (5) docs. Files and
    symbols: release-candidate.yml (publish; provenance; install and package-ready needs); ci_policy.py
    (`CIPolicy.CANDIDATE_JOBS`, `require_candidate_success`); testpypi_candidate.py (`prepare_upload`, `main`);
    new testpypi_provenance.py (`ProvenancePolicy`, the fetch, `CertificateClaims` - a strict DER reader of the
    certificate's extensions - the five checks, the tool environment, the controls, the report); new
    `.github/provenance/verify_attestations.py`, `requirements.txt`, `known_good_provenance.json`; tests:
    test_workflow_contracts.py, test_ci_policy.py, test_candidate_publication.py, new test_candidate_provenance.py;
    docs: the six `.github/ci_cd/` pages as needed, BRANCH_WORKFLOW.md, tests_components.md. Constraints: the
    standard-library rule, Optional/Union, class-level constants, rich docstrings, no network in tests.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-24_pypi_provenance_attestations_epic.md:196-218
  IMPACT: Fixes the order: workflow and policy, then the scripts, then tests, docs, rebuild.
  NEXT: Send the lane-open NOTICE, then write testpypi_provenance.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T23:44:53Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The verifier does what layers 3 and 4 need. Method: a CPython 3.14.6 (GIL build) environment installed
    from the lock exactly as `tool_environment` installs it (`--require-hashes --no-deps --only-binary=:all:`,
    then `pip check`, clean), the verifier run with `-I` and `--offline` (the bundled trust root: the container
    reaches no Sigstore TUF mirror). The three controls `control_entries` builds split as required: the recorded
    attestation verified; another digest refused ("subject does not match distribution digest"); another expected
    SAN refused. A sweep built on the control: each of the 17 exact claims .8-.24 changed by one character was
    refused naming that claim (sigstore's own policies for .8-.22, `ExtensionEquals` for .23 and .24); a pattern
    for .21 matching the run verified, one naming another repository refused; a claim the certificate lacks (.99)
    refused; another issuer refused - 21 entries, 20 refused, all as designed. Not run: the online trust-root
    refresh CI uses (no `--offline`) and Python 3.14.7; the first hosted run exercises both.
  EVIDENCE:
  - .github/provenance/verify_attestations.py:120-220
  - .github/scripts/testpypi_provenance.py:621-668
  IMPACT: The pinned tool enforces every expected claim and the controls tell a working tool from a lax one, so
    the tool side of D3 is proven before any workflow depends on it.
  NEXT: Re-read and edit release-candidate.yml, ci_policy.py and testpypi_candidate.py (the wiring).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T23:49:21Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: D7's commit pin works with the action's container. v1.14.3's composite step builds its Docker action
    from `github.action_ref` (`create-docker-action.py`: `docker://ghcr.io/pypa/gh-action-pypi-publish:<ref>`),
    so a commit pin pulls the image tagged with that commit, and the action's image workflow pushes a tag for
    every commit of a release branch (`IMAGE_SHA`, `ghcr.io/$GITHUB_REPOSITORY:${GITHUB_SHA}`); certifi pins it
    the same way (`@cef22109... # v1.14.0`, `attestations: true`). ghcr.io itself is not reachable from here
    (proxy 403), so the image's presence is seen on the first hosted run. Also: release-candidate.yml is mixed CRLF
    (87 lines) and LF (73) in this checkout, git stores it LF, and validating.md says keep each file's endings,
    so its edits keep each replaced line's ending.
  EVIDENCE:
  - create-docker-action.py:16-23 (gh-action-pypi-publish 7245906f, v1.14.3)
  - action.yml:126-155 (gh-action-pypi-publish 7245906f, v1.14.3)
  - .github/workflows/build-and-push-docker-image.yml:52-83 (gh-action-pypi-publish 7245906f, v1.14.3)
  - .github/ci_cd/validating.md:55-56
  IMPACT: The pinned `uses:` needs nothing else; a missing image would fail the upload step loudly, not silently.
  NEXT: Edit release-candidate.yml: the publish switch, the provenance job, the two needs lists.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T23:50:45Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The wiring is in (implementation, not yet tested). publish: `id-token: write` beside `contents: read`, the
    outputs `uploaded` (prepare-upload's staged names) and `attempt` (`github.run_attempt`), no secret check, and
    the upload through `pypa/gh-action-pypi-publish@7245906f... # v1.14.3` with only `repository-url`,
    `packages-dir`, `attestations: true` and `print-hash`. A new `provenance` job (RC / provenance) needs build
    and publish, runs `testpypi_provenance.py verify` on the helper release with both outputs in its env and keeps
    `candidate-provenance-<run>-<attempt>`; install and package-ready need it; `CANDIDATE_JOBS` names it and the
    refusal says six stages; `prepare_upload` returns the staged names and `main` writes `uploaded=<json list>`
    beside `upload-required`.
  EVIDENCE:
  - .github/workflows/release-candidate.yml:55-145
  - .github/workflows/release-candidate.yml:179-179
  - .github/scripts/ci_policy.py:21-22
  - .github/scripts/ci_policy.py:199-202
  - .github/scripts/testpypi_candidate.py:161-177
  - .github/scripts/testpypi_candidate.py:281-299
  IMPACT: The workflow side of S1 and S2 is complete; every existing contract and unit test that pinned the token
    posture now fails until the tests are rewritten, which is the next tranche.
  NEXT: Rewrite the contract, policy and publication tests, then write test_candidate_provenance.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:09:35Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Tests written and run on the device (CPython 3.14.7t, `-X gil=0`): `tests/unit/github_workflows` 680
    passed, 1 failed - the guide-coverage test, which waits for the docs. New: test_candidate_provenance.py (163
    cases: the DER reader and certificate identity on the real control and on certificates built byte by byte,
    every claim, the legacy claims, run context, upload record, the Integrity API's retries and redirect, layers 2
    and 5, the lock, the controls, the tool environment, the verifier process, the verdicts, the whole check end to
    end with its report, the CLI, the policy against the workflow, the verifier read as source); in the contracts:
    the publish job, RC / provenance, the only id-token holder, the commit pin and the standard-library rule; the
    policy and publication tests for six stages and the staged names. Each new rule bites: 19 mutations (workflow,
    policy, prepare-upload, script, verifier) each failed its tests, and every file came back byte for byte.
  EVIDENCE:
  - tests/unit/github_workflows/test_candidate_provenance.py:1-1169
  - tests/unit/github_workflows/test_workflow_contracts.py:624-774
  - tests/unit/github_workflows/test_candidate_publication.py:363-416
  IMPACT: S1+S2's behaviour is pinned by tests that fail for a real regression; only the docs remain before the
    full suite is green.
  NEXT: Write the .github/ci_cd/ pages and BRANCH_WORKFLOW.md, then rerun the suite with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:26:45Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The docs are in and the suite is green. `.github/ci_cd/` describes the posture: the flow (README), the
    publish, provenance, install and package-ready rows and the re-run rule (workflows.md), the script, its five
    layers, prepare-upload's outputs and the `provenance/` folder (scripts.md), the secrets rule and "Change the
    provenance tool" (extending.md), four symptom rows and the report artifact (validating.md), the tool's own
    environment (python_versions.md); BRANCH_WORKFLOW.md gives the Trusted Publisher's four values, the
    retirement of `melder_api_token`, the fresh candidate version, RC / provenance and the re-run. Run on the
    device (CPython 3.14.7t): `tests/unit/github_workflows` 681 passed with `-X gil=0` and 681 with `-X gil=1`,
    the guide-coverage test included (it requires each `.github/provenance/` file by path). Not run: any hosted run.
  EVIDENCE:
  - .github/ci_cd/README.md:36-60
  - .github/ci_cd/workflows.md:69-77
  - .github/ci_cd/scripts.md:84-131
  - .github/ci_cd/extending.md:27-73
  - .github/ci_cd/validating.md:44-56
  - .github/ci_cd/python_versions.md:92-95
  - .github/BRANCH_WORKFLOW.md:367-409
  - .github/BRANCH_WORKFLOW.md:427-444
  IMPACT: Every acceptance criterion but the tests map holds locally; what remains is the tests map, the closure and
    the rebuild.
  NEXT: Update tests_components.md for the new and changed github_workflows tests, then regenerate its index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:33:26Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The tests map changes and one more file. tests_components: the Unit Test Suite's protects line, its tier
    count (516 of 519, recounted) and its tooling-tree count (11; github_workflows 9); the Repository Tooling Unit
    Cluster's protects bullet for the provenance gate and the standard-library rule, and `test_candidate_provenance.py`
    (1169 lines, 163 tests) as a key file; the core map's new entry and four remeasured (`conftest.py` 79,
    `test_workflow_contracts.py` 1048, `test_candidate_publication.py` 565, `test_ci_policy.py` 604); the union
    283 and the tiers' 865 modules; a call flow for the end-to-end harness; sources, handoff, Metadata.
    tests_architecture.md joins the boundary: this change made two of its facts stale (the github_workflows
    conftest's 73 lines, in its boot sequence and its core map), and its CI/CD bullet and inventory describe what
    changed. It is a repair of this change's own staleness (staleness_protocol), not new scope; nothing else moves.
    Read first: the whole test module and script, the conftest, the four new contract tests.
  EVIDENCE:
  - tests/unit/github_workflows/test_candidate_provenance.py:1-1169
  - .github/scripts/testpypi_provenance.py:1-790
  - tests/unit/github_workflows/conftest.py:1-79
  - tests/unit/github_workflows/test_workflow_contracts.py:624-774
  - context_compass/system_docs/tests_components.md:344-468
  - context_compass/system_docs/tests_components.md:1434-1467
  - context_compass/system_docs/tests_architecture.md:233-250
  - context_compass/system_docs/tests_architecture.md:340-347
  IMPACT: Both tests documents describe the suite as it stands after this story, so neither carries a stale extent.
  NEXT: Edit both documents (baseline multisets captured before the first edit), regenerate both indexes, check.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:38:40Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Both tests documents are current. tests_components carries the cluster's provenance bullet and key file,
    the end-to-end call flow, the core map (283 entries, equal to the key-file union) and a dated handoff entry;
    tests_architecture its CI/CD bullets, the conftest's 79 lines, the recounted inventory and a handoff entry.
    Checks: both indexes regenerated and `--check` OK (71 sections over 4344 lines; 32 over 1113); every cited
    path exists; no path into the tooling and no absolute path; no wrapped heading; no new line over 120; the
    preservation gate (multisets captured before the first edit) loses only the 17 and 11 lines replaced by their
    updated values - old extents, counts, dates and the rewrapped bullets. Found on the way: the integration tier
    holds `test_conduit_integration_windows_held_cache_bundle.py`, which no tests_components cluster lists
    (another lane's module; named in the handoff entry, melder_0 to hear).
  EVIDENCE:
  - context_compass/system_docs/tests_components.md:1434-1478
  - context_compass/system_docs/tests_components.md:2118-2142
  - context_compass/system_docs/tests_components.md:3190-3195
  - context_compass/system_docs/tests_components.md:3957-3972
  - context_compass/system_docs/tests_architecture.md:232-254
  - context_compass/system_docs/tests_architecture.md:926-933
  IMPACT: Every acceptance criterion holds locally; the closure, the board and epic sync and the rebuild remain.
  NEXT: Turn the story in: completion summary, state, checklist, move to completed/, board and epic sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:38:43Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Turned in. Every acceptance criterion holds locally: the contract tests pin the publish job, the pinned
    action, no secret, the one id-token holder and RC / provenance's wiring; 163 unit tests prove each layer's
    accept and refuse paths with no network; the verifier verified the recorded control and refused both tampered
    copies in an environment built from the lock; the CI guide, BRANCH_WORKFLOW.md and both tests documents
    describe it; `tests/unit/github_workflows` 681 passed with the GIL off and on. The exit gate leaves hosted runs
    "Not run" until the owner shares them, so the story closes on its own gate; what only the owner can do moves to
    the epic: the TestPyPI Trusted Publisher, the commit and promotion, the first RC run on a fresh version, and
    then deleting `melder_api_token` and revoking it. No src/, so no notch and no release-note entry; the rebuild
    runs after this closure and its result goes in the epic.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:624-774
  - tests/unit/github_workflows/test_candidate_provenance.py:1-1169
  - .github/workflows/release-candidate.yml:55-141
  - .github/BRANCH_WORKFLOW.md:367-409
  IMPACT: The release candidate cannot install a file whose provenance does not name this run's workflow, and the
    upload holds no stored credential; the hosted proof is the owner's next step.
  NEXT: Move the story to completed/, sync the board (closed anchor, the epic's own row) and the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user (the closing report, 2026-10-25)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded (the
  closing DECISION Note; the owner's gates in the epic)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S1+S2 of EPIC-2026-10-24-pypi_provenance_attestations - Trusted Publishing to TestPyPI with attestations,
  and the release candidate's five-layer provenance check before install. State: done (2026-10-25), melder_2.
- Delivered: the publish job (OIDC, the pinned action, attestations, its outputs); RC / provenance with
  `testpypi_provenance.py` and `.github/provenance/` (verifier, hashed lock, recorded control); six candidate
  stages; the tests (681 passed, the GIL off and on); `.github/ci_cd/`, BRANCH_WORKFLOW.md, both tests documents.
- Not run: any hosted run; the verifier's online trust-root refresh and Python 3.14.7 (the first hosted run).
- Owner-owed: the TestPyPI Trusted Publisher (Synaptic724 / melder / release-candidate.yml / pypitest), the commit
  (`git add -A`) and promotion, the first RC run on a version TestPyPI has never seen; after it publishes, delete
  the `melder_api_token` environment secret and revoke its token.
- Next: the epic - S3 (PyPI) on the owner's word, after his PyPI publisher.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
