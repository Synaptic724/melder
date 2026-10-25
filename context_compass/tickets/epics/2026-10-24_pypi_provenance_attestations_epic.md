# Epic: pypi_provenance_attestations - every Melder file on TestPyPI and PyPI carries verified provenance

## Metadata
- Epic ID: EPIC-2026-10-24-pypi_provenance_attestations
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-24T22:21:35Z
- Updated: 2026-10-25T15:43:10Z
- Target Window: 2026-Q4
- Related Program/Initiative: integrity of the published package (the owner's request, chat 2026-10-24, 16:16 MDT)

## Problem / Opportunity
Melder publishes to TestPyPI (`release-candidate.yml`, job `publish`, environment `pypitest`) and to PyPI
(`python-publish.yml`, job `pypi-publish`, environment `pypi`) with long-lived API tokens (`user: __token__`; the
environment secrets `melder_api_token` and `PYPI_API_TOKEN`) and with attestations switched off
(`attestations: false`). The contract tests pin that posture: the TestPyPI upload must use the token and
`attestations: "false"`, and no other release-candidate job may hold `id-token: write`. So nobody can check that a
wheel on PyPI was published by this repository's workflow, and the upload credential is a secret that lives until
someone revokes it.

PEP 740 attestations need Trusted Publishing: PyPI rejects attestations that do not come from a Trusted Publisher,
and `pypa/gh-action-pypi-publish` produces and uploads them by default when it publishes through one. The owner's
earlier OIDC attempt failed with `invalid-publisher` and he chose tokens (BRANCH_WORKFLOW.md); this epic returns to
Trusted Publishing on purpose, with each publisher's configuration checked before a workflow depends on it.

## MRP Alignment (Most Reasonable Product)
The core is a publication chain in which every uploaded file is signed with the publishing workflow's identity and
checked in CI before anything depends on it: TestPyPI first, where the release candidate's probes verify the
provenance of exactly what they install, then PyPI, then the tokens retired. Nothing ships half-switched: each index
moves to Trusted Publishing in one change with its contract tests and docs, and the token path stays documented
until both indexes have published with attestations.

## Ticket Contract
- ENTRY_GATE: the owner's go; the owner's Trusted Publisher on TestPyPI (before S1 and S2 reach release_candidate)
  and on PyPI (before S3 reaches prod), with the values in Decision Log D2; `.github/ci_cd/` read before any
  `.github` edit (special_instructions/ci_cd_guide.md); a story ticket and a board row for each story as it
  starts, one at a time.
- EXECUTION_BOUNDARY: the `publish` job of `.github/workflows/release-candidate.yml` and the `pypi-publish` job of
  `.github/workflows/python-publish.yml`; `.github/scripts/testpypi_candidate.py` and any standard-library script
  the checks need; the pinned verification tool and its lock under `.github/provenance/` (D6);
  `tests/unit/github_workflows/`; `.github/ci_cd/`; `.github/BRANCH_WORKFLOW.md`; a user-facing verification
  section (README or a docs page); the release note's Packaging section; the tests map where it describes these
  tests. No `src/` change, so no notch.
- DEPENDENCIES: the owner's TestPyPI and PyPI project settings and the GitHub environments `pypitest` and `pypi`;
  the promotion chain dev -> preprod -> release_candidate -> prod (BRANCH_WORKFLOW.md), which brings each change to
  the branch that runs it; hosted runs, which are the owner's.
- EXIT_GATE: every file of a released version on PyPI, and of its candidate on TestPyPI, has a PEP 740 provenance
  naming Synaptic724/melder with the expected workflow and environment; the RC install probe refuses a wheel whose
  provenance does not verify; neither upload job references an API token; contract tests pin the new posture;
  `.github/ci_cd/` and BRANCH_WORKFLOW.md describe it; users have a documented verification command; hosted-run
  evidence shared by the owner; the owner accepts the epic.
- FAILURE_ESCALATION: BLOCKER when a hosted run fails `invalid-publisher` (the publisher's values and the job's claims
  disagree: the owner rechecks D2); DECISION_REQUEST for D3 before S2 and for D4 before S6; CONFLICT if another lane
  holds `.github/`.

## Goals (Outcomes)
- Every file Melder uploads to TestPyPI and PyPI carries a PEP 740 attestation tied to this repository's publish
  workflow and environment.
- The release candidate verifies the provenance of the exact files it installs, before any final release.
- No long-lived upload token remains in GitHub or on either index.
- A user can check a Melder file's provenance with one documented command.

## Non-Goals (Explicit Exclusions)
- Changing how distributions are built, verified or smoke-tested (`build-distributions.yml`,
  `verify_distributions.py`, `smoke_wheel.py`), beyond what an attestation step needs.
- Making pip or uv verify attestations at install time; consumers verify with `pypi-attestations`.
- Signing commits or tags. GitHub build provenance of the build job is S6, only if D4 says so.
- Attesting versions already uploaded with tokens; they stay without provenance.

## Scope Boundaries
- In scope: the two upload jobs' authentication and attestations; provenance checks in the RC probe and after the
  PyPI upload; contract tests; the CI guide and BRANCH_WORKFLOW.md; a user-facing verification note; retiring the
  tokens.
- Out of scope: `src/`; the other workflows; GitHub rulesets; the owner's account settings themselves (he makes
  them; the epic gives the exact values); hosted runs ("Not run" until seen).

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the owner's go (chat 2026-10-24: "why don't you just check to see how deep it goes bro I don't
  know lets go super deep so we can properly build this out"); D3 and D4 are settled in the Decision Log and S1+S2
  starts as one story (D5). Earlier: draft -> ready when the epic was opened on his request (chat 2026-10-24,
  16:16 MDT: "can you make an epic to implement pypi provenance?").

## Success Metrics
- After S1 and S2: one RC run with `RC / installed-package` green on every cell, the probe's provenance check
  among its steps, and TestPyPI showing provenance for each uploaded file.
- After S3: the next final release has provenance for its wheel and sdist on PyPI, and the post-upload check
  passes.
- After S4: no `secrets.melder_api_token` or `secrets.PYPI_API_TOKEN` anywhere in `.github/workflows/`, enforced by a
  contract test.

## Requirements (Functional + Non-Functional)
- Functional: both upload jobs authenticate by OIDC (`id-token: write` on those two jobs only, no `user` or
  `password` input) and keep the action's attestations on; the TestPyPI upload of only the missing files stays; the
  RC probe fetches each installed file's provenance from TestPyPI and verifies it against the file and the expected
  identity before installing; the PyPI job checks the uploaded files' provenance after the upload, unless the owner
  accepts the RC check as the gate (Open Questions).
- Non-functional: `.github/scripts/` stays standard-library only (CI rule 3), so a cryptographic check runs a pinned
  tool in an isolated environment, installed with no resolver from a manifest like the test manifests; every refusal
  names the file, the expected identity and what was found; nothing floats; `id-token: write` reaches no other job
  (contract test).

## Constraints / Assumptions
- PyPI accepts attestations only from Trusted Publishers, and `pypa/gh-action-pypi-publish` generates and uploads
  them by default when it publishes through one (docs.pypi.org, "Producing attestations").
- A GitHub Trusted Publisher names the repository owner and name, the workflow filename and, optionally (strongly
  recommended), the environment; the job's OIDC claims must match them (docs.pypi.org, "Adding a publisher").
- Consumers verify with `pypi-attestations verify pypi --repository https://github.com/<owner>/<repo> <file URL>`,
  which reads the provenance through the Integrity API (docs.pypi.org, "Consuming attestations").
- UNKNOWN: whether `pypi-attestations verify pypi` accepts TestPyPI file URLs, or the RC probe needs the Integrity
  API plus a lower-level verify; S2 investigates first.
- UNKNOWN: how a version first uploaded by token behaves (its files have no provenance, and the RC skips identical
  files already uploaded); S1 runs on a fresh version number either way.
- The GitHub repository is public (the project URLs point at github.com/Synaptic724/melder). Attestations are
  recorded in Sigstore's public transparency log, which names the repository, workflow and ref.

## Dependencies / External References
- https://docs.pypi.org/attestations/producing-attestations/
- https://docs.pypi.org/attestations/consuming-attestations/
- https://docs.pypi.org/trusted-publishers/adding-a-publisher/
- `pypa/gh-action-pypi-publish` (its `attestations` input and OIDC publishing) and `pypi/pypi-attestations`
- `.github/BRANCH_WORKFLOW.md`: the TestPyPI credential table and the earlier `invalid-publisher` failure

## Milestones (Track Progress)
- [x] Milestone 1: TestPyPI publishes with attestations through Trusted Publishing (S1; the owner's first RC run,
  2026-10-25).
- [x] Milestone 2: the RC probe verifies provenance before it installs (S2; RC / provenance green in the owner's
  first RC run, 2026-10-25).
- [ ] Milestone 3: PyPI publishes with attestations and the upload's provenance is checked (S3).
- [ ] Milestone 4: tokens retired; CI and user documentation complete (S4, S5).

## Stories (Required to Complete)
- [x] Story: S1 testpypi_trusted_publishing (one story with S2: STORY-2026-10-24-testpypi_trusted_publishing_and_
  provenance, D5; turned in 2026-10-25, hosted run Not run) - `release-candidate.yml`'s publish job uploads by OIDC
  with attestations; the secret check and the token inputs go; contract tests and docs follow; the first run uses a
  fresh version number.
- [x] Story: S2 rc_probe_verifies_provenance (in the same story) - built as its own job, RC / provenance
  (`testpypi_provenance.py verify`), between the upload and `probe-install` rather than inside it: every built
  file's provenance (Synaptic724/melder, `release-candidate.yml`, `pypitest`) checked in D3's five layers before any
  probe installs it; accept and refuse paths tested on recorded and synthetic answers; the tool pinned (D6).
- [x] Story: S3 pypi_trusted_publishing (one story with S4's contract test and S5, D8:
  STORY-2026-10-25-pypi_trusted_publishing_and_provenance, turned in 2026-10-25, hosted run Not run) -
  `python-publish.yml`'s pypi-publish job uploads by OIDC with attestations and checks the uploaded files'
  provenance; contract tests and docs.
- [ ] Story: S4 retire_upload_tokens (its contract test landed with the S3 story, D8; deleting and revoking the
  secrets stays the owner's: `melder_api_token` deleted 2026-10-25, its revocation unconfirmed; `PYPI_API_TOKEN`
  after the first attested release) - no workflow references a token; the owner deletes both environment secrets
  and revokes the tokens; a contract test forbids them.
- [x] Story: S5 document_provenance_for_users (in the S3 story, D8; turned in 2026-10-25) - the verification
  command for users (README or docs), the release note's Packaging line, BRANCH_WORKFLOW.md's credential sections
  rewritten for Trusted Publishing.
- [ ] Story: S6 build_provenance (D4; after S3) - GitHub artifact attestations of the built distributions in
  `build-distributions.yml`.

Story tickets are created as each starts, one at a time; S1 and S2 are one story (D5).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete stories S1-S6.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The EXIT_GATE holds with the owner's hosted-run evidence, and the owner has accepted the epic.

## Risks / Mitigations
- `invalid-publisher` again: the owner checks the four values of D2 on each index before the story that needs them
  merges; S1 replaces the token path in one change, so a failure is a red RC run on a fresh candidate version, not a
  broken release, and the rollback is reverting that job.
- Files uploaded by token have no provenance, so S2's check would refuse them: S1 and S2 run on a new candidate
  version.
- A failed-jobs re-run of the RC publish job requests a fresh OIDC token (fine); the PyPI job keeps refusing
  failed-jobs re-runs.
- A new pinned CI dependency (the verification tool and its sigstore/crypto closure, D3): exact pins with hashes at
  the versions the publishing action itself signs with (D6), installed in its own environment, never imported by
  the standard-library scripts; a recorded known-good attestation and two tampered copies prove it in every run.
- `id-token: write` spreading: contract tests keep it on the two upload jobs only.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Local: `python -m pytest tests/unit/github_workflows` - contract tests for permissions, inputs and secrets, and
  unit tests of the provenance check against recorded Integrity API answers, with no network.
- Hosted (the owner's): one RC run after S1 and S2, one final release after S3; "Not run" until he shares them.

## Rollout / Adoption Plan
- S1 and S2 reach release_candidate through the promotion chain after the owner adds the TestPyPI publisher; S3
  lands for the next final release after he adds the PyPI publisher; S4 only after both indexes have published with
  attestations; S5 with S3 or S4.

## Open Questions
- D3 and D4 are answered (Decision Log, 2026-10-24).
- RESOLVED 2026-10-25 (the owner's first RC run, all green): TestPyPI serves the Integrity API at the PyPI route.
  Was UNKNOWN: TestPyPI serves the Integrity API at the PyPI route (`/integrity/<project>/<version>/<file>/provenance`);
  Warehouse serves both indexes and the publishing action attests for both, but neither CI environment here can
  reach test.pypi.org. The first hosted RC run settles it; a missing route reads as a refusal naming each file.
- Answered by D8: the PyPI job's upload is checked after it (Release / provenance), and the RC check of the same
  tree stays the gate before it.
- S6 (D4): kept or dropped - the owner's call, still open.

## Decision Log
- D1 (2026-10-24, the owner, chat 16:16 MDT): make an epic to implement PyPI provenance. The token-only posture in
  BRANCH_WORKFLOW.md stays in force until S1 and S3 land.
- D2 (proposed; the owner enters them): TestPyPI project `melder` -> Publishing -> GitHub: owner `Synaptic724`,
  repository `melder`, workflow `release-candidate.yml`, environment `pypitest`. PyPI project `melder` -> Publishing
  -> GitHub: owner `Synaptic724`, repository `melder`, workflow `python-publish.yml`, environment `pypi`.
- D3 (2026-10-24, the owner, chat: "why don't you just check to see how deep it goes bro I don't know lets go super
  deep so we can properly build this out"):
  the deepest check. Every uploaded file: a provenance exists; PyPI's publisher record equals D2; Sigstore verifies
  it on the production trust root; the signing certificate is checked claim by claim (issuer; repository with its
  numeric id and owner id; workflow, ref and commit; trigger; GitHub-hosted runner; public visibility; deployment
  environment and token subject; this run for the files it uploaded); and the statement names the exact bytes.
- D4 (melder_2, on the same message; the owner may veto): S6, GitHub build provenance, stays in the epic as its own
  story after S3: it needs `id-token: write` and `attestations: write` in `build-distributions.yml`, which holds
  read-only permissions by rule today, so it is its own change.
- D5 (melder_2): S1 and S2 are one story - the switch to Trusted Publishing ships only with the check that proves it.
- D6 (melder_2): the cryptographic check runs `pypi-attestations` 0.0.30 with sigstore 4.5.1, the versions
  `pypa/gh-action-pypi-publish` v1.14.3 signs with, from a hashed lock under `.github/provenance/`, in a fresh
  environment of the helper release. The standard-library script checks layers 1, 2, 4 and 5 itself (it decodes
  the certificate), calls the tool for 3 and 4 again, and first proves the tool on a recorded known-good
  attestation and two tampered copies of it.
- D7 (melder_2): the publish action is pinned to its commit (`7245906fb61fa33a13554f9d5fb856fe61758086`, v1.14.3),
  as `astral-sh/setup-uv` is, because that job alone holds `id-token: write`.
- D8 (2026-10-24, the owner, chat 20:12 MDT: "yeah ok go ahead and implement everything you need to", on the
  DECISION_REQUEST of 2026-10-25T01:56:46Z): S3, S4's contract test and S5 are one story,
  STORY-2026-10-25-pypi_trusted_publishing_and_provenance; PyPI's upload is checked after it by a Release /
  provenance job (the recommended option), and the RC check of the same tree stays the gate before it. S6 (D4)
  stays open for his keep-or-drop: this story does not touch `build-distributions.yml`.

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
- Ticket/Work Author(s): melder_2 (synaptic_python_developer); prose; created 2026-10-24T22:21:35Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-24T22:21:35Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Both uploads use tokens with attestations off, and the tests pin it. `python-publish.yml`'s pypi-publish
    job holds `contents: read` and `actions: read` and publishes with `user: __token__`, `secrets.PYPI_API_TOKEN` and
    `attestations: false`; `release-candidate.yml`'s publish job holds `contents: read`, checks
    `secrets.melder_api_token` and publishes with it and `attestations: false`. The contract test asserts the token,
    `attestations == "false"` and that no other release-candidate job holds `id-token: write`. BRANCH_WORKFLOW.md
    records the earlier OIDC run's `invalid-publisher` failure and the owner's choice of tokens.
  EVIDENCE:
  - .github/workflows/python-publish.yml:70-124
  - .github/workflows/release-candidate.yml:55-109
  - tests/unit/github_workflows/test_workflow_contracts.py:453-665
  - .github/BRANCH_WORKFLOW.md:366-392
  IMPACT: S1 and S3 replace these jobs' authentication and must update that contract test with them; the earlier
    failure makes the owner's publisher configuration the first thing to check.
  NEXT: On the owner's go and his TestPyPI publisher, open S1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T22:21:35Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: PyPI's documentation (read 2026-10-24): attestations require Trusted Publishing - "PyPI will reject
    non-Trusted Publisher attestations at upload time" - and `pypa/gh-action-pypi-publish` generates and uploads them
    by default with no other configuration; a GitHub publisher names owner, repository, workflow filename and an
    optional, strongly recommended environment; consumers verify with `pypi-attestations verify pypi --repository
    <repository URL> <file URL>`, which reads the provenance through the Integrity API. Not stated there: TestPyPI
    specifics, and whether pip or uv verify at install (both UNKNOWN, Constraints).
  EVIDENCE:
  - .github/workflows/python-publish.yml:118-124
  IMPACT: The two workflow changes are small (OIDC permission, drop the token inputs, attestations on); the real
    work is the owner's publisher setup, the verification in the RC probe (D3) and the docs.
  NEXT: As above.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-24T23:05:25Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Three NOTICEs taken in at re-onboarding, none asking an ACK. M1-56 and M1-60 (melder_1): 0.2.8267 is
    notched and rebuilt; the 0.2.8265 note is cut to release_docs/0.2.8265.md, and next_version_release.md holds
    only 0.2.8266-0.2.8267 (127 lines) with my pip bullet in Packaging and documentation; read it before adding to
    it. M3-5 (melder_3): src_architecture is at its spec - a change there states today's rule and its mechanism with
    no version history, component mechanics go to src_components, a C1 note is a description only, one dated
    handoff entry per lane at the top, no path into context_compass; tell melder_3 before writing src_components.
  EVIDENCE:
  - release_docs/next_version_release.md:106-127
  - context_compass/tickets/stories/completed/2026-10-24_src_architecture_trim_to_spec_story.md:1-12
  IMPACT: This epic lands no source, so no notch; its release-note line goes in the Packaging and documentation
    section before the rebuild line, and the rebuild runs last. It is not expected to touch src_architecture or
    src_components; if it does, M3-5's rules apply and melder_3 hears first.
  NEXT: Record D3 and D4, then open the S1+S2 story with its board row.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T23:19:30Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: How deep a check can go (read in the tools' source, 2026-10-24). `Attestation.verify` (pypi-attestations
    0.0.30) runs Sigstore's `verify_dsse` on the production or staging trust root - certificate chain to Fulcio,
    transparency-log entry, signature - with the caller's identity policy, then requires one statement subject whose
    parsed name and sha256 match the file and a known predicate type. Its GitHub publisher policy checks only the
    issuer, the repository URI and the Build Config URI. sigstore 4.5.1 has exact-match policies for Fulcio claims
    .8-.22 and none for .23 (Deployment Environment) or .24 (Token Subject), but a real PyPI attestation signed
    2026-07-28 carries both (`pypi`, `repo:pypi/pypi-attestations:environment:pypi`) beside .1-.6 and .8-.22. The
    CLI's `verify pypi` reads pypi.org only, so TestPyPI needs the Python API. The publishing action v1.14.3 signs
    every file in `packages-dir` with production Sigstore, and uses Trusted Publishing only with `user` left at
    `__token__` and no password.
  EVIDENCE:
  - pypi_attestations/_impl.py:234-321 (pypi-attestations 0.0.30, `Attestation.verify`)
  - pypi_attestations/_impl.py:449-526 (0.0.30, `_GitHubTrustedPublisherPolicy`)
  - pypi_attestations/_cli.py:382-391 (0.0.30, `_get_provenance_from_pypi`)
  - sigstore/verify/policy.py:42-331 (sigstore 4.5.1, the claim OIDs and policy classes)
  - attestations.py:121-148 (gh-action-pypi-publish 7245906f, v1.14.3)
  - twine-upload.sh:77-117 (gh-action-pypi-publish 7245906f, v1.14.3)
  IMPACT: Layers 1-5 of D3 are all enforceable for TestPyPI files; .23 and .24 need a custom policy; the stdlib
    script can check every claim itself from the certificate's DER, so the identity rules are unit-testable
    without the third-party closure.
  NEXT: Write the S1+S2 story with this design, then implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-24T23:19:30Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's go settles D3 (deepest check) and, on my reading, D4 (S6 stays, its own story after S3; his to
    veto). S1 and S2 become one story (D5) because a Trusted Publishing switch without the check would publish
    attestations nothing verifies. The tool is the signer's own toolchain at its exact versions, from a hashed lock
    (D6); the publish action is pinned to its commit (D7). Tranche order: S1+S2, then S3 (PyPI, after his PyPI
    publisher), then S4 (tokens), S5 (users), S6 (build provenance).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-24_pypi_provenance_attestations_epic.md:196-218
  IMPACT: The story's boundary is the RC workflow, its scripts and tests, `.github/provenance/`, the CI guide and
    BRANCH_WORKFLOW.md; `python-publish.yml` waits for S3.
  NEXT: Open STORY-2026-10-24-testpypi_trusted_publishing_and_provenance with its board row.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:40:15Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1+S2 is turned in (STORY-2026-10-24-testpypi_trusted_publishing_and_provenance, done). The publish job
    uploads by Trusted Publishing with attestations through the action pinned to its commit (D7), `id-token: write`
    on that job alone in every workflow and no TestPyPI secret anywhere; RC / provenance checks every built file in
    D3's five layers before the install matrix, with pypi-attestations 0.0.30 and sigstore 4.5.1 from a hashed
    lock (D6), proven each run on a recorded attestation and two tampered copies; package-ready requires six
    stages. S2 is its own job, not a step of probe-install: it runs once, and a refusal skips every probe cell.
    Tests: 681 passed, the GIL off and on; the verifier's controls split as designed locally (offline trust root).
    Not run: any hosted run. UNKNOWN until the first hosted RC run: TestPyPI's Integrity API route, and the
    action's image for the pinned commit on GHCR.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md:1-8
  - .github/workflows/release-candidate.yml:55-141
  - .github/scripts/testpypi_provenance.py:721-757
  IMPACT: Milestones 1 and 2 wait only on the owner's hosted run; S3 can reuse the design for PyPI.
  NEXT: Report to the owner; after his first RC run and on his word, open S3 (python-publish.yml) with its row.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:45:10Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The S1+S2 rebuild ran last, after the story's closure, on CPython 3.14.7t from the repository root:
    `_build_asset_runner.py` wrote the three asset manifests (v0.2.8267) and `--check` printed only OK lines;
    `llm_support/_builder.py --include-untracked` rewrote the tests and other bundles (src unchanged) and
    `--check --include-untracked` printed only OK lines. `--include-untracked` is needed until the owner commits:
    the story's five new files are untracked, as are `release_docs/0.2.8265.md` and another lane's integration
    test. context_compass/ is in no bundle and no asset, so this ticket write leaves both checks as they are.
  EVIDENCE:
  - llm_support/_builder.py:62-100
  - src/melder/_build_assets/_agent_documentation/_builder.py:181-195
  IMPACT: The change set is complete in the owner's checkout; what remains is his (commit, publisher, hosted run).
  NEXT: Report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T01:50:29Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner committed S1+S2: commit 982698ecc (2026-10-24 19:39:58 -0600) holds every file of the story -
    the five new files, the workflow, scripts, tests, CI guide, BRANCH_WORKFLOW.md, the tests pair and both
    tickets - and the rebuilt bundles, each equal to the working copy with line endings normalized (read-only
    git, compared file by file); dev merged into codex_features2 at d1c91e3d6. Owner-owed still: the TestPyPI
    Trusted Publisher, the promotion and the first RC run on a version TestPyPI has never seen, then the token's
    retirement. My 19:40 reminder to commit with `git add -A` came from an untracked-files check made before that
    commit; check `git log` before telling the owner what is uncommitted.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md:1-8
  IMPACT: The commit step is done; the next owner steps are the publisher and the RC run.
  NEXT: Wait for the owner's RC run link or logs; read RC / publish-to-TestPyPI and RC / provenance first.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T01:56:46Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The prod plan, asked for by the owner (chat 2026-10-24 19:54 MDT). Today `pypi-publish` uploads with
    `PYPI_API_TOKEN`, attestations off and the action by `@release/v1`; it runs on a published final release (ref
    `refs/tags/<tag>`) or a dispatch on prod (`refs/heads/prod`), always at prod HEAD, and refuses failed-jobs
    re-runs. Proposed S3, one story: `id-token: write` on `pypi-publish` alone (the contract's holder list grows by
    it), no user or password, attestations on, the action pinned to 7245906f (D7); a `pypi-provenance` job after
    the upload checking every released file on pypi.org's Integrity API in D3's five layers with the release
    identity (`python-publish.yml` at the run's ref, environment `pypi`, this run and attempt, prod's commit),
    sharing the candidate check's layers, verifier, lock and control; S4's code (a contract test forbidding
    `PYPI_API_TOKEN` and `melder_api_token`) and S5 (README verification command, the release note's Packaging
    line) folded in. Owner: the PyPI publisher (D2: Synaptic724 / melder / python-publish.yml / pypi) before the
    first final release that carries it; after that release, delete `PYPI_API_TOKEN` and revoke it. Decisions
    asked: the go for S3 as scoped; the post-upload check (recommended) or the RC check alone; S6 kept or dropped.
  EVIDENCE:
  - .github/workflows/python-publish.yml:1-124
  - .github/scripts/ci_policy.py:269-306
  - tests/unit/github_workflows/test_workflow_contracts.py:454-482
  IMPACT: S3 can land before the first RC run: prod publication already requires a successful RC run of the exact
    tree (check_candidate_run.py), so TestPyPI's check passes before any PyPI upload of that tree.
  NEXT: On the owner's go, open the S3 story with its board row and read the shared layers' callers first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:34:43Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's go answers the prod plan (D8): S3 with S4's code and S5 is one story, opened as
    STORY-2026-10-25-pypi_trusted_publishing_and_provenance with its board row; the PyPI upload switches to Trusted
    Publishing with attestations and a post-upload Release / provenance job checks every released file in D3's five
    layers; S6 is not part of the go and stays open. Owner-owed for prod, unchanged: the PyPI publisher (D2) before
    the first final release that carries this, then `PYPI_API_TOKEN` deleted and revoked.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-25_pypi_trusted_publishing_and_provenance_story.md:1-60
  - context_compass/tickets/epics/2026-10-24_pypi_provenance_attestations_epic.md:416-440
  IMPACT: Tranche order becomes S1+S2 (done), the S3 story, then S6 on the owner's word; S4 shrinks to the owner's
    secret deletion and revocation once both indexes have published with attestations.
  NEXT: Implement the S3 story; report to the owner at its turn-in.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T03:21:46Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S3 with S4's code and S5 is turned in (STORY-2026-10-25-pypi_trusted_publishing_and_provenance, done).
    `pypi-publish` uploads by Trusted Publishing with attestations through the action pinned to its commit (D7),
    with no user, password or secret and its attempt as an output; `id-token: write` is held by it and the RC
    upload alone. Release / provenance checks every released file on pypi.org after the upload in D3's five layers
    with the release identity (`python-publish.yml` at `refs/tags/<tag>` or `refs/heads/prod`, the run's commit,
    this run and the upload's attempt, `pypi`), reusing the candidate check's layers, lock, verifier and control,
    and keeps its report 90 days. No workflow names `PYPI_API_TOKEN` or `melder_api_token` (a contract test). The
    install guide gives users the `pypi-attestations verify pypi` command, the README links it, and the running
    note's Packaging bullet covers both indexes. 752 workflow tests, the GIL off and on; no src, no notch. Not run:
    hosted runs, the Sphinx build.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-25_pypi_trusted_publishing_and_provenance_story.md:1-8
  - .github/workflows/python-publish.yml:70-166
  - .github/scripts/pypi_provenance.py:208-251
  IMPACT: Milestones 3 and 4 wait on the owner: his PyPI publisher before the first final release that carries this,
    that release, then both tokens deleted and revoked; S6 stays his call.
  NEXT: Rebuild the assets and the LLM bundles, then report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T03:25:27Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The S3 story's rebuild ran last, after its closure and the board and epic sync, on CPython 3.14.7t from
    the repository root: `_build_asset_runner.py` wrote the three asset manifests at v0.2.8268 (agent documentation
    469 entries, bind guard 629, system documents 4) and `--check` printed only OK lines; `llm_support/_builder.py
    --include-untracked` rewrote the src, tests and other bundles (src's fingerprint had moved with another lane's
    working-tree source) and `--check --include-untracked` printed only OK lines. The system-documents asset ingests
    src_architecture, src_components and the graph, not the tests pair or tickets, and the bundles skip
    context_compass/, so this note and a later tests-pair edit leave both checks as they are.
  EVIDENCE:
  - src/melder/_build_assets/_system_documents/_builder.py:110-136
  - llm_support/_builder.py:62-100
  IMPACT: The change set is complete in the owner's checkout; what remains is his (commit with `git add -A`, the
    publishers, the hosted runs, the tokens, S6).
  NEXT: Report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:20:15Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner is promoting S1+S2: at the checkout's last fetch origin/preprod holds it (7bafb314f, PR #199,
    2026-10-25 02:05 -0600) and origin/release_candidate does not (0b443cc5f, 2026-10-20), whose RC publish job still
    requires `secrets.melder_api_token` and uploads with it, attestations off. He shared
    https://test.pypi.org/project/melder/#security (WebFetch refused it, robots_disallowed; nothing was read) and
    asked whether to remove `melder_api_token`. Answer given: yes, after the TestPyPI publisher (D2), the
    promotion to release_candidate and one green RC run on a version TestPyPI has never seen (its publish and RC /
    provenance jobs); then delete the pypitest secret and revoke the token on TestPyPI. Removed before the promotion,
    the old job's secret check fails any RC run. M1-65 taken in: melder_1 took 0.2.8269; this epic notches nothing,
    and the running note (now headed 0.2.8269) keeps my Packaging bullet.
  EVIDENCE:
  - .github/workflows/release-candidate.yml:81-101 (at origin/release_candidate 0b443cc5f)
  - release_docs/next_version_release.md:207-214
  - src/melder/__version__.py:12-12
  IMPACT: S4's TestPyPI half waits on the owner's promotion and first green RC run, not on code; PYPI_API_TOKEN
    waits on the first attested final release, as before.
  NEXT: Read RC / publish to TestPyPI and RC / provenance when the owner shares the run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:25:44Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The first hosted RC run, as the owner reports it (chat 2026-10-25 02:22-02:23 -0600): "it got out it worked
    I see the provenance" - TestPyPI took the upload by Trusted Publishing and shows each file's provenance, which it
    records only from a Trusted Publisher, so the run used the new publish job and the pinned action's image works
    (that UNKNOWN is resolved). He then deleted `melder_api_token` ("I deleted it now"); whether the token is also
    revoked on TestPyPI, and RC / provenance's own result, are not yet reported, and I have seen neither the run nor
    its report. S3 is committed: 1dd4470e7 (2026-10-25 02:08:16 -0600) holds every file of the story, and the working
    tree equals HEAD for each of them with line endings ignored (read-only git). PyPI: nothing has run yet.
  EVIDENCE:
  - .github/workflows/release-candidate.yml:55-141
  - context_compass/tickets/stories/completed/2026-10-25_pypi_trusted_publishing_and_provenance_story.md:1-8
  IMPACT: Milestone 1 holds on the owner's run; Milestone 2 and TestPyPI's Integrity API route wait on RC /
    provenance's result; S4's TestPyPI half is done once the token is revoked; the PyPI half waits on his publisher
    and the first final release that carries S3.
  NEXT: Ask the owner for RC / provenance's result and the token's revocation; read Release / provenance at the first
    attested final release.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:27:53Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner confirms the first hosted RC run was all green (chat 2026-10-25 02:27 -0600: "yeah it was all
    green"): RC / provenance passed before the install probes, so TestPyPI serves the Integrity API at the PyPI route
    (the check reads `https://test.pypi.org/integrity/melder/<version>/<file>/provenance` and refuses a missing one,
    UNKNOWN resolved), and the five layers with the pinned verifier, its hashed lock and its controls verified real
    Melder attestations. S1+S2's success metric holds on his run (RC green, the provenance check among its stages,
    TestPyPI showing each file's provenance), so Milestone 2 holds. The PyPI release check reuses those layers,
    lock, verifier and control; what only a final release can prove is PyPI's publisher (D2) and the release
    identity (the tag ref, the `release` event), pinned by tests against PyPI's real release certificate.
  EVIDENCE:
  - .github/scripts/testpypi_provenance.py:71-138
  - .github/scripts/testpypi_provenance.py:514-561
  - .github/scripts/testpypi_provenance.py:757-793
  IMPACT: S1 and S2 are proven end to end; the epic waits on the PyPI half (the owner's publisher and first attested
    release, then `PYPI_API_TOKEN` retired), the TestPyPI token's revocation (unconfirmed) and S6.
  NEXT: At the first final release that carries S3, read Publish to PyPI and Release / provenance first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:31:42Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner asks whether the posture is reasonable now (chat 2026-10-25 02:30 -0600). Answered yes: TestPyPI
    is proven, and PyPI reuses the proven layers, waiting only on his publisher and the first final release; a
    missing or mismatched publisher fails the upload with nothing published (recover with Re-run all jobs).
    Recommended for S6 (D4): drop it. Each PyPI file's PEP 740 attestation already names the release run that built
    (`release-build`, the reusable build-distributions.yml) and uploaded it, at the released commit, which is what a
    user verifies; GitHub build attestations would mainly serve files downloaded from GitHub, and would give a third
    job `id-token: write` with `attestations: write` in a workflow that is read-only by rule. Asked: drop or keep S6.
  EVIDENCE:
  - .github/workflows/python-publish.yml:63-68
  - .github/workflows/build-distributions.yml:27-28
  - context_compass/tickets/epics/2026-10-24_pypi_provenance_attestations_epic.md:218-220
  IMPACT: With S6 dropped, the epic closes on the owner's acceptance once Release / provenance passes on the first
    attested release and both upload tokens are revoked.
  NEXT: Record the owner's S6 answer; read the first final release's Publish to PyPI and Release / provenance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T15:04:54Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Eleven NOTICEs taken in, none asking an ACK and none touching this epic's open work. Notches since 0.2.8269:
    melder_0 took 0.2.8270 (D-10), 0.2.8271 (D-11), 0.2.8272 (D-20) and 0.2.8275 (the notch fan-out race), melder_1
    0.2.8273 (S2 of the correctness epic), melder_3 0.2.8274 (the creations store slots); this epic lands no src and
    notches none. Custody to respect if S6 or a fix reopens a shared file: melder_1 holds README.md, two docs pages
    and the UX/agent guides for S2 (M1-68, M1-71); the system documents are free again (M3-27, M0-240). The two
    root benchmark files the owner asked about (big_before.jsonl, big_after.jsonl: his native runs for
    TASK-2026-10-12-make_kernel_pools_elastic, read by nothing) he deleted himself in d8938890b.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/tickets/tasks/completed/2026-10-12_make_kernel_pools_elastic_task.md:440-446
  IMPACT: Nothing in this epic is blocked by another lane; it waits only on the owner's PyPI steps and S6.
  NEXT: Report the epic's state to the owner; read the first final release's Publish to PyPI and Release /
    provenance when he shares it.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T15:43:10Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner asks whether he must publish once with the new flow before retiring `PYPI_API_TOKEN` (chat
    2026-10-25 09:41 -0600). The only consumer is python-publish.yml as prod holds it (`password:
    secrets.PYPI_API_TOKEN`; dev, preprod and release_candidate carry the same old copy at the last fetch, but
    publication runs only at prod HEAD), and the S3 workflow (1dd4470e7, not yet on prod) cannot use a token at
    all. Answer given: he may retire it now if no release goes out from prod before S3 reaches it. Waiting keeps
    only a revert path; the PyPI-only failure left (`invalid-publisher`) is fixed on PyPI and uploads nothing, and
    the TestPyPI run proved the rest of the mechanism. If he retires it early, S4's PyPI half closes before the
    first attested release.
  EVIDENCE:
  - .github/workflows/python-publish.yml:121-129 (at origin/prod 2d6c75233)
  - .github/scripts/ci_policy.py:269-305
  - .github/workflows/python-publish.yml:124-132
  IMPACT: Retiring the token no longer waits on the first attested release, only on S3 reaching prod first.
  NEXT: Record the owner's choice; read the first final release's Publish to PyPI and Release / provenance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: PEP 740 provenance for every Melder upload to TestPyPI and PyPI, through Trusted Publishing, verified in the
  release candidate before anything depends on it; then the tokens retired. State: in_progress, melder_2.
- Decisions: D3 deepest check, D4 S6 in the epic, D5 S1+S2 one story, D6 the pinned tool, D7 the pinned action,
  D8 S3 with S4's code and S5 one story, checked after the upload.
- Holds: the owner's TestPyPI Trusted Publisher (D2) before S1+S2 reaches release_candidate; PyPI's before the
  first final release that carries S3.
- Done: S1+S2 (STORY-2026-10-24-testpypi_trusted_publishing_and_provenance; committed 982698ecc) and S3 with S4's
  code and S5 (STORY-2026-10-25-pypi_trusted_publishing_and_provenance; committed 1dd4470e7), both turned in
  2026-10-25; 752 workflow tests, the GIL off and on. Hosted: the first RC run uploaded to TestPyPI by Trusted
  Publishing and TestPyPI shows each file's provenance (the owner, 2026-10-25); he deleted `melder_api_token`.
  PyPI: nothing run yet.
- Owner-owed now: the token revoked on TestPyPI if only the GitHub secret went (unconfirmed); S3 (1dd4470e7)
  promoted to prod with its own RC run; the PyPI Trusted Publisher (D2) before the first final
  release that carries S3, then, after that release, `PYPI_API_TOKEN` deleted and revoked; S6 kept or dropped.
- UNKNOWN: the release identity on a real Melder release (proven against PyPI's real release certificate of the
  verifier). Resolved by the first RC run (all green): the pinned action's image and TestPyPI's Integrity API.
- Next: (1) at the first final release that carries S3, read Publish to PyPI and Release / provenance first, then
  he retires `PYPI_API_TOKEN` (S4); (2) S6 on his word.

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
