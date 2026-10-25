# Story: pypi_trusted_publishing_and_provenance - PyPI releases carry verified provenance

- Completed: 2026-10-25T03:19:56Z
- Summary: PyPI uploads by Trusted Publishing with PEP 740 attestations - `id-token: write` on pypi-publish, the
  action pinned to its commit, no user, password or secret - and Release / provenance checks every released file on
  PyPI after the upload in the candidate check's five layers with the release identity; no workflow names either
  upload token; users get a `pypi-attestations` command (752 workflow tests, GIL off and on). No src, no notch;
  hosted runs Not run; the owner adds the PyPI publisher before the first final release that carries this.

## Metadata
- Story ID: STORY-2026-10-25-pypi_trusted_publishing_and_provenance
- Epic: EPIC-2026-10-24-pypi_provenance_attestations
- Status: done
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-25T02:19:52Z
- Updated: 2026-10-25T03:19:56Z

## User Narrative
As Melder's owner, and as a user installing Melder from PyPI, I want every release file to go up through Trusted
Publishing with a PEP 740 attestation that the release run checks on PyPI after the upload, and a documented command
to check a file myself, so that anyone can prove a Melder wheel came from this repository's release workflow at the
released commit, and no long-lived upload token is left to steal.

## Value / MRP Alignment
Stories S3, S4's code and S5 of the epic as one change (D8): prod's upload switch ships with the check that proves
each released file, the contract that keeps tokens out, and the words a user needs. It reuses S1+S2's layers, tool,
lock and control, so the release check is the candidate check with the release's identity, not a second design.

## Ticket Contract
- ENTRY_GATE: the owner's go (chat 2026-10-24, 20:12 MDT: "yeah ok go ahead and implement everything you need
  to"), answering the plan in the epic's DECISION_REQUEST of 2026-10-25T01:56:46Z; the epic in progress; this
  story's board row; `.github/ci_cd/` read (2026-10-24, and its pages re-read at re-onboarding 2026-10-25).
- EXECUTION_BOUNDARY: `.github/workflows/python-publish.yml` (`pypi-publish`; a new `pypi-provenance` job);
  `.github/scripts/testpypi_provenance.py` (its shared layers take the index as a policy; two refusal texts stop
  naming TestPyPI) and a new standard-library `.github/scripts/pypi_provenance.py`; `tests/unit/github_workflows/`;
  `.github/ci_cd/`; `.github/BRANCH_WORKFLOW.md` (its final-publication sections); `docs/beginner/install.md` and
  `README.md` (the verification command; install.md's stale "no runtime package dependencies"); one Packaging bullet
  in `release_docs/next_version_release.md`; `context_compass/system_docs/tests_components.md`,
  `tests_architecture.md` and their indexes; the asset and LLM-bundle rebuild last. Not `src/` (no notch), not
  `build-distributions.yml` (S6, still the owner's call), not the verifier, lock or control (unchanged).
- DEPENDENCIES: S1+S2 (done); the owner's PyPI Trusted Publisher (D2) before the first final release that carries
  this; the promotion chain; hosted runs are the owner's.
- EXIT_GATE: the acceptance criteria hold with `tests/unit/github_workflows` green with the GIL off and on; hosted
  runs "Not run" until the owner shares them; board and epic synced; the rebuild checks print only OK.
- FAILURE_ESCALATION: DECISION_REQUEST when a release claim cannot be pinned as designed; CONFLICT when another lane
  takes `.github/`, the README, the install guide or the running note; BLOCKER when a shared-layer change cannot keep
  the candidate check's behaviour.

## Requirements (Functional)
- `pypi-publish` uploads through Trusted Publishing: `id-token: write` beside its `contents: read` and `actions:
  read`, no `user`, no `password`, attestations on, the action pinned to its commit (D7), its run attempt an output.
- `pypi-provenance` (Release / provenance) runs after the upload and checks every built file on pypi.org's Integrity
  API in D3's five layers with the release identity: publisher record `Synaptic724/melder`, `python-publish.yml`,
  `pypi`; the certificate naming that workflow at the run's ref (the release tag for a published release, `prod` for
  a dispatch), prod's commit, this run and the upload's attempt, the `pypi` environment; the statement naming the
  file and its sha256. The tool is proven on its controls first; the report is retained.
- Contract: `id-token: write` on the two upload jobs only, both pinning the action; no `PYPI_API_TOKEN` or
  `melder_api_token` in any workflow.
- Users: the install guide and the README give the `pypi-attestations` command that checks a downloaded file.

## Requirements (Non-Functional)
- `.github/scripts/` stays standard-library only; the release script imports the candidate script's layers.
- The candidate check keeps its behaviour: its tests pass unchanged but for the two refusal texts.
- Unit tests make no network calls; every refusal names the file, what was expected and what was found.

## Scope Boundaries
- In scope: the boundary above.
- Out of scope: GitHub build provenance (S6); deleting `PYPI_API_TOKEN` and revoking it (the owner's, after the
  first attested release); `src/`.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: every acceptance criterion holds locally (Notes of 2026-10-25T03:19:56Z); the exit gate
  leaves hosted runs Not run until the owner shares them; the owner's gates move to the epic. Earlier: draft ->
  in_progress, opened on the owner's go as the epic's second story (D8).

## Dependencies / Related Work
- EPIC-2026-10-24-pypi_provenance_attestations (D2, D3, D6, D7, D8); STORY-2026-10-24-
  testpypi_trusted_publishing_and_provenance (done; its layers, tool, lock and control).

## Tasks (Implementation Checklist)
- [x] The shared layers take the index; `pypi_provenance.py`.
- [x] `python-publish.yml`: the upload switch and Release / provenance.
- [x] Tests: contract, candidate (messages), release provenance.
- [x] Docs: `.github/ci_cd/`, BRANCH_WORKFLOW.md, install guide, README, the running note, the tests pair.
- [x] Turn in; the rebuild runs last (after this closure; its MEASURE goes on the epic).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Contract tests pin `pypi-publish`'s permissions, inputs and pinned action, no secret, the two id-token holders,
  no token name in any workflow, and Release / provenance's wiring and evidence.
- Unit tests prove the release identity (release event and dispatch, every refusal), the release check end to end
  with its report, the shared layers on pypi.org, and the release rules against a real release certificate.
- The CI guide, BRANCH_WORKFLOW.md, the install guide, the README and the running note describe the new posture;
  the tests pair covers the new test file.

## Validation / Test Plan
- `python -X gil=0 -m pytest tests/unit/github_workflows -q` and the same with `-X gil=1`; the docs tests if the
  install guide's checks cover it.
- Hosted: the first final release after the owner adds the PyPI publisher ("Not run").

## UX / API / Data Notes
- No public API change. New report artifact: `release-provenance-<run>-<attempt>`. Users get one command.

## Risks / Mitigations
- A check after the upload cannot unpublish: a refusal fails the run loudly and says what to check; the gate before
  the upload stays the release candidate's verified TestPyPI files of the same tree.
- The release identity is first exercised by a real release: the claim rules are tested against PyPI's real release
  attestation of pypi-attestations (a `release` event at a tag, environment `pypi`).
- PyPI may answer 404 just after the upload: retried, as on TestPyPI.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- S6 (build provenance) stays the owner's to keep or drop; this story does not touch it.

## Decision Log
- The epic's D3, D6, D7 and D8 govern this story.

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
- Independent Review: none; the owner's commit review and the first attested final release are the remaining gates

## Notes
- DATETIME: 2026-10-25T02:19:52Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: What the release side holds today. `pypi-publish` keeps `contents: read` and `actions: read` (its candidate
    lookup) and uploads `dist/` with `user: __token__`, `secrets.PYPI_API_TOKEN`, `attestations: false` through
    `@release/v1`; it refuses a failed-jobs re-run. Publication runs on a published final release, whose ref is
    `refs/tags/<tag>` with the tag naming the version (`v` optional), or a dispatch on `refs/heads/prod`, always at
    prod HEAD (`validate_release`). The candidate script's layers hard-code TestPyPI in `fetch_provenance` (root,
    texts) and two refusal texts; `verified_files` and `package_version` are index-free. The install guide still says
    "Melder has no runtime package dependencies" though Melder declares pip (README, pyproject).
  EVIDENCE:
  - .github/workflows/python-publish.yml:70-124
  - .github/scripts/ci_policy.py:269-306
  - .github/scripts/verify_distributions.py:170-183
  - .github/scripts/testpypi_provenance.py:477-529
  - .github/scripts/testpypi_candidate.py:50-70
  - docs/beginner/install.md:23-35
  IMPACT: The change is the upload step, one new job and script, a parameter on the shared fetch, two texts, the
    contract tests and the docs; nothing in the candidate path changes its behaviour.
  NEXT: Write the PLAN note, send the lane-open NOTICEs, then implement the shared-layer parameter.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:34:43Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: In order. (1) `testpypi_provenance.py`'s shared layers take the index: `ProvenancePolicy` gains
    `INDEX_NAME`, `USER_AGENT`, `missing_provenance(name)` (the candidate's text, unchanged) and `workflow_uri(ref)`;
    `fetch_provenance` takes the policy, defaulting to the candidate's, since `CandidateRun.fetch` stands in for it
    with two arguments; `require_outcomes` takes the entry prefix (default `candidate`); the publisher-record and
    Sigstore refusals stop naming TestPyPI (the control's record is PyPI's anyway). (2) A new standard-library
    `pypi_provenance.py`: `ReleaseProvenancePolicy` (pypi.org's Integrity API, `python-publish.yml`, `pypi`, events
    release and workflow_dispatch), the release context (`refs/tags/<RELEASE_TAG>` or `refs/heads/prod`), the release
    identity (every file signed by this run's upload attempt), `verify`, its report. (3) `python-publish.yml`:
    `pypi-publish` with `id-token: write`, an `attempt` output and the pinned action without user or password;
    `pypi-provenance` (Release / provenance) after it. (4) Tests: the fixture, the contract tests, a new
    `test_release_provenance.py` with the real control as a release-event signer. (5) Docs: `.github/ci_cd/`,
    BRANCH_WORKFLOW.md, the install guide and README, one Packaging bullet, the tests pair. (6) Turn-in; the
    rebuild last. Taken in at re-onboarding: M3-8 (src_components at its spec; this story writes nothing there or in
    src_architecture) and M3-11 (0.2.8268 is melder_3's notch; this story lands no src, so it takes none).
  EVIDENCE:
  - .github/scripts/testpypi_provenance.py:67-111
  - .github/scripts/testpypi_provenance.py:487-531
  - .github/scripts/testpypi_provenance.py:534-564
  - .github/scripts/testpypi_provenance.py:700-718
  - .github/workflows/python-publish.yml:70-124
  - tests/unit/github_workflows/test_candidate_provenance.py:937-991
  - tests/unit/github_workflows/test_workflow_contracts.py:718-753
  IMPACT: The candidate check keeps its calls and messages but two refusal texts; the release check reuses its
    layers, verifier, lock and control, so nothing under `.github/provenance/` moves.
  NEXT: Edit the shared layers and run the candidate tests before writing `pypi_provenance.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:50:49Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Implemented and tested (docs next). The shared layers take the index: `ProvenancePolicy` holds `INDEX_NAME`,
    `USER_AGENT`, `missing_provenance` and `workflow_uri(ref)`, `fetch_provenance` its `policy` (the candidate's by
    default), `require_outcomes` its `prefix`; the publisher-record and Sigstore refusals no longer name TestPyPI.
    `pypi_provenance.py` (289 lines): `ReleaseProvenancePolicy`, `release_context` (a release at refs/tags/<tag>, a
    dispatch at prod with no tag), `publish_attempt`, `release_identity` (every claim exact: this run's upload
    attempt, its event, the run's ref and commit), `released_files` (the tag must name the version), `verify_release`
    and its report. `python-publish.yml`: `pypi-publish` holds `id-token: write`, outputs its attempt, uploads through
    the pinned action with attestations and no token; `pypi-provenance` (Release / provenance) checks after it and
    keeps `release-provenance-<run>-<attempt>`. Contract tests: the upload's posture, the provenance job, two
    id-token holders (the test renamed `test_only_the_two_upload_jobs_can_request_an_oidc_token`; nothing else names
    it), both pinned, neither token named in any workflow. `test_release_provenance.py`: 29 tests, 68 cases, the real
    control reproduced as a release signer claim for claim. 751 passed, the GIL off; the one failure is the CI guide
    test (no `pypi_provenance.py` in `.github/ci_cd/` yet). Ten mutations each failed their test and were restored
    byte for byte. M3-12 (ACK): melder_3 holds none of these files and rebuilds before my docs edits.
  EVIDENCE:
  - .github/scripts/testpypi_provenance.py:71-138
  - .github/scripts/testpypi_provenance.py:514-561
  - .github/scripts/testpypi_provenance.py:730-754
  - .github/scripts/pypi_provenance.py:1-289
  - .github/workflows/python-publish.yml:70-166
  - tests/unit/github_workflows/test_workflow_contracts.py:505-555
  - tests/unit/github_workflows/test_workflow_contracts.py:771-817
  - tests/unit/github_workflows/test_release_provenance.py:1-667
  IMPACT: The code side of S3 and S4 is done; what remains is the guide, BRANCH_WORKFLOW.md, the users' docs, the
    note, the tests pair, then turn-in and the rebuild. Hosted: Not run.
  NEXT: Update `.github/ci_cd/` (workflows, scripts, extending, validating, README) and rerun the suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T03:07:06Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Re-onboarded after a compaction (self-certified as melder_2 on the owner's standing preference). Two
    NOTICEs taken in, neither asking an ACK. M0-223 (melder_0, answering M2-44): for D-10 it holds tests_components'
    codegen core-boundary entry (description, Key Files line, C1 map row) and one dated handoff entry at the top,
    and in the running note a Breaking section before Packaging and documentation, one bullet there, and the header
    and rebuild-line version when it notches above 0.2.8268 (its notch waits on the owner); it edits by targeted
    replacement after a fresh read, so my entries stand. M1-63 (melder_1, re M2-42): it holds none of my files and
    adds its two test files to tests_components after my turn-in, and one section to the running note.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md:432-454
  - context_compass/tickets/stories/2026-10-25_probe_and_purge_reach_every_version_story.md:239-246
  - src/melder/__version__.py:12-12
  IMPACT: My tests_components edits stay off the codegen entry and add one handoff entry of mine after a fresh read;
    the running note's header and rebuild line stay at 0.2.8268 until melder_0 notches; melder_1 waits on my
    turn-in of the tests pair, so it goes early in the turn-in.
  NEXT: Run the workflow suite with the GIL on and off, then the tests pair.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T03:19:56Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Validated on 3.14.7t from the repository root. `tests/unit/github_workflows`: 752 passed with the GIL off
    and 752 with it on, after one docstring of mine in the contract tests was rewrapped under 120 characters (it
    moved the OIDC tests a line: 772-818, where the 02:50:49Z note cites 771-817). `tests/unit/architecture_and_design`
    and `tests/unit/llm_support`: 46 passed. `docs/tests`: 41 passed; 3 need Sphinx and `test_build_docs.py` needs
    jinja2, neither installed here (environmental; CI's docs.yml runs them). The tests pair: tests_components
    gains the cluster's release bullet and key file, a Release Provenance flow, the core map entry, the remeasured
    `conftest.py` (85) and `test_workflow_contracts.py` (1114), the union 284 and the tiers' 868 modules (two of
    them melder_1's, named as uncatalogued); tests_architecture its CI/CD bullets, the conftest's 85 lines, the
    inventory and a handoff entry. Both indexes rebuilt, `--check` OK; every cited path exists; no tooling or
    absolute path; no new line over 120; the preservation gate loses only the 13 and 10 lines replaced by their
    updated values. The quality rubric scores a creation, recomposition or review, so this entry update is not
    scored. Not run: any hosted run, the Sphinx build.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:505-556
  - tests/unit/github_workflows/test_workflow_contracts.py:772-818
  - context_compass/system_docs/tests_components.md:1439-1494
  - context_compass/system_docs/tests_components.md:2164-2190
  - context_compass/system_docs/tests_components.md:4020-4034
  - context_compass/system_docs/tests_architecture.md:232-256
  - context_compass/system_docs/tests_architecture.md:933-939
  IMPACT: Every acceptance criterion holds locally; the closure, the board and epic sync and the rebuild remain.
  NEXT: Turn the story in, sync the board and the epic, then rebuild.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T03:19:56Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Turned in under the owner's go (D8). Every acceptance criterion holds locally: the contract tests pin
    `pypi-publish`'s permissions, environment, attempt output and pinned action with attestations and no secret,
    Release / provenance's wiring and retained report, the two id-token holders and no `PYPI_API_TOKEN` or
    `melder_api_token` in any workflow; 29 tests (68 cases) prove the release identity for a release and a dispatch
    with every refusal, the release check end to end with its report, the shared layers on pypi.org and the release
    rules against PyPI's real release certificate; the guide, BRANCH_WORKFLOW.md, the install guide, the README and
    the running note describe the posture; the tests pair covers the new module. Self-checks only (ten mutations,
    02:50:49Z): no independent review; the owner's commit review and the first attested release are the remaining
    gates, held on the epic with his PyPI publisher, the token's retirement and S6.
  EVIDENCE:
  - .github/workflows/python-publish.yml:70-166
  - .github/scripts/pypi_provenance.py:1-289
  - tests/unit/github_workflows/test_release_provenance.py:1-667
  IMPACT: S3, S4's code and S5 are done; the epic keeps the owner-owed steps and S6.
  NEXT: Board and epic sync, NOTICEs, then the rebuild.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user (the closing report, 2026-10-25)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded (the
  closing DECISION Note; the owner's gates on the epic)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S3 with S4's code and S5 of EPIC-2026-10-24-pypi_provenance_attestations - Trusted Publishing to PyPI with
  attestations, Release / provenance after the upload, no token in any workflow, the users' command. State: done,
  melder_2.
- Done: the shared layers' index policy, `pypi_provenance.py`, `python-publish.yml`, the contract and release tests
  (752 workflow tests, the GIL off and on), the CI guide, BRANCH_WORKFLOW.md, the install guide, the README, the
  running note's Packaging bullet and the tests pair. No src, no notch. Hosted runs: Not run.
- Owner-owed (held on the epic): the PyPI Trusted Publisher (D2) before the first final release that carries this;
  after that release, `PYPI_API_TOKEN` deleted and revoked; S6 kept or dropped.
- Next: the rebuild (assets, then the LLM bundles) after this closure, recorded on the epic.

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
