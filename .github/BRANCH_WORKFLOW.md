# Branch CI and release workflow

Contributions enter `dev` through a pull request. Promotion proceeds through
`dev -> preprod -> release_candidate -> prod`, with the merge result checked at every boundary.

## Required checks

`CI / merge-ready` remains the stable required status. The branch route selects
which checks must run; the final gate independently verifies that selection.

| Event | Full runtime matrix | Other required work |
| --- | --- | --- |
| Feature PR into `dev` | Yes | Hygiene, source/repository assets and documentation |
| `dev` PR into `preprod` | Yes | The same checks plus distribution verification |
| `preprod` PR into `release_candidate` | No | Hygiene and exact-tree full preprod proof |
| `release-fix/*` PR into `release_candidate` | Yes | Full checks and distribution verification for changed contents |
| `release_candidate` PR into `prod` | No | Hygiene and exact-source successful TestPyPI qualification |
| Manual `CI` on a permanent branch | Yes | Full checks; distributions on every branch except dev |
| Ordinary branch push | No source CI | RC pushes retain their dedicated package workflow |
| Final publication | Yes | Fresh package validation and final tag/prod checks |

The checks enforce these contracts:

- Branch policy: contributions target dev; preprod accepts this repository's dev,
  release_candidate accepts preprod, and prod accepts release_candidate. Forks
  cannot impersonate promotion branches. Permanent-branch synchronization PRs
  may return to dev. Same-repository `release-fix/*` PRs can prepare or fix the
  frozen candidate; keep their scope narrow and carry fixes back to dev.
- Source assets in full CI: the existing build-asset runner verifies committed manifests.
- Repository assets in full CI: the LLM builder verifies committed bundles and indexes.
- Repository hygiene: tracked filenames must not collide case-insensitively.
- Documentation in full CI: the shared documentation validation workflow must succeed.
- Full runtime tests: unit, component, and integration tiers on Linux, Windows, and macOS,
  using the latest stable patch of every supported Python minor, with the GIL disabled
  in the actual pytest process.
  The macOS job uses `macos-latest` on native Apple Silicon (arm64).
- Distribution verification in full CI outside dev: wheel and sdist boundaries,
  source/metadata/asset versions, and an isolated installed-wheel smoke test.
- Prod candidate proof: the exact source head must have successful TestPyPI
  qualification, a final package version, and the same tree as the merge result.
  This runs last inside `CI / merge-ready`, after the other required checks succeed.
- Source qualification: unchanged preprod promotions must prove that their entire
  merge tree passed full CI before the source suite may be skipped.

The final status fails for missing evidence, failure, cancellation, or an
unexpected skipped job. Optional jobs may succeed or be explicitly skipped, never
fail or disappear from the result map. Profile flags are derived from the event;
repository variables cannot waive a required check. Helpers remain
manually runnable. `ci.yml` owns source CI; `release-candidate.yml` owns candidate pushes.

Scope `PYTHON_GIL=0` to the runtime-test and installed-package probe steps. Do not
set it for the whole job: macOS Python setup runs a standard-Python certificate
installer that cannot start with the GIL disabled. The test driver and wheel probe
still reject an unsupported interpreter or an enabled GIL during qualification.

## Supported Python versions

Runtime discovery reads the Python floor from `project.requires-python` in `pyproject.toml`
(currently `>=3.14`) and GitHub's official `actions/python-versions` release manifest.
It selects the latest stable patch of every matching minor: 3.14, then 3.15 once stable,
and subsequent stable versions automatically. Alpha, beta and release-candidate Python builds
are excluded. Historical patch releases are not separate matrix entries.

Every selected version runs on Linux x64, Windows x64 and macOS arm64. Runtime tests and
RC installation probes use `freethreaded: true` with the discovered exact Python version.
The test driver verifies free-threading support and GIL-off state before and after pytest;
the installed-package probe also verifies GIL-off state. Discovery, asset and policy tooling
may use ordinary Python because those jobs do not qualify Melder's runtime behavior.

The discovery helper refuses empty/malformed catalog data, missing support for the declared
floor, and a selected release lacking free-threaded assets on a required platform. Setup errors
on the actual runner also fail the matrix. No missing version/platform silently disappears.
Each runtime/RC run retains its selected OS/version matrix as a JSON artifact for 90 days.
Tests, coverage and installed-package reports include OS, exact Python version and run/attempt.

Distribution building still produces one wheel/sdist pair. Its Python selection comes from
`pyproject.toml` with free threading enabled; the full compatibility matrix belongs to runtime
tests and RC installed-package checks. Existing full-test stages stay unchanged. Historical
source proof refers to its recorded full-CI run, while final publication discovers and tests
the currently available stable matrix afresh.

## Coverage reporting and README badges

The existing OS/version runtime runs also produce line/branch coverage XML for Melder.
They do not run the suite a second time. Each matrix cell retains a coverage artifact for 14 days;
one reporting job uploads those reports to Codecov after the full matrix succeeds.
It requires an XML file for every discovered OS/version from the same run/attempt; missing artifacts
leave a reporting warning/failure rather than publishing an incomplete matrix as the current result.
Tests and the current source/release checks remain required. Coverage delivery is nonblocking,
and codecov.yml disables extra coverage statuses and PR comments; no percentage threshold is added.

One-time setup:

1. Sign into Codecov with GitHub and enable the public Synaptic724/melder repository.
2. Copy that repository's Codecov upload token.
3. In GitHub, open Settings -> Secrets and variables -> Actions -> New repository secret.
4. Use the name CODECOV_TOKEN and paste the Codecov token as its value.

This is a repository Actions secret, not an environment secret or variable. No new GitHub
environment or id-token permission is needed. Do not reuse either PyPI token or store the token
in the checkout. CI and final publication explicitly pass only CODECOV_TOKEN to the reusable
workflow; only its credential check and Codecov upload steps receive it.
If the token is absent, a setup warning is emitted and reporting is skipped. Fork PRs retain
their test/coverage artifacts but skip credentialed uploads.

The README coverage badge tracks prod. It shows no percentage until the first prod report is
processed. Normal final-release tests populate it; the release tag is attributed to prod only
after the existing release gate verifies that tag against current prod HEAD. To seed the badge
without publishing a package, run Actions -> Runtime tests -> Run workflow on prod after these
files reach that branch. Do not run Publish Python Package merely to refresh coverage.

The CI badge uses GitHub's default-branch/latest-run behavior, not a hardcoded passing label.
Reference: https://github.com/codecov/codecov-action#usage

## Working on a feature

Create a short-lived branch from current dev and explicitly target dev when
opening the PR; prod remains the repository's default branch. Run:

```bash
python -m pytest -q tests/unit tests/component tests/integration
python src/melder/_build_assets/_build_asset_runner.py --check
python llm_support/_builder.py --check
```

If generated assets are stale, regenerate locally and commit them. Stage newly
added input files before running the repository builder so its tracked-file
inventory includes them. Never hand-merge generated bundles. After updating a
feature from dev, regenerate again when the combined source changed.

CI runs on PR updates, including a changed PR base, and explicit manual dispatch.
It does not repeat source CI after pushes to dev/preprod/prod. Candidate pushes
run the slim package workflow below. New PR
commits supersede old CI runs. Reusable helpers have no concurrency group that
could accidentally cancel their caller or a final release.

## Promotion and merge history

Prefer squash for disposable feature branches, and start the next feature from
current dev. Use merge commits between permanent branches. Do not repeatedly
squash between the permanent branches. Prod must preserve a normal two-parent
promotion merge so the final publisher can verify the candidate source.

The supplied dev ruleset requires an up-to-date branch. Promotion rulesets use
the current PR merge result with the one permitted source branch and merge
commits. They deliberately do not require dev to contain every preprod-only
merge commit, which otherwise creates a perpetual merge-back requirement.
Resolve conflicts on the source branch and rerun CI; carry release/hotfix changes
back into dev through a reviewed synchronization PR.

## Reusing full qualification

A successful full CI run retains `source-qualification-<run-id>-<attempt>` for
90 days. Its JSON record binds the repository, run/attempt, event/PR identity and
the actual tested checkout and Git tree. A PR run's head SHA is not assumed to
be its tested merge SHA.

`verify-source-qualification.yml` finds the full run behind the actual preprod
promotion, downloads one immutable artifact ID with read-only credentials, and
checks its record against the current tree. It refreshes the selection after
download so a changed attempt cannot reuse an old record. Light CI does not issue
full-runtime evidence. Historical GitHub run records may omit their PR association;
the downloaded record must still prove the correct PR, head and base.

Any difference in the Git tree—including source, dependencies, tests, workflow
configuration or generated assets—requires qualification of those contents.
Release-fix PRs therefore run full CI. An exact-commit manual CI run on the
expected branch provides explicit fresh evidence and takes precedence over
historical PR evidence; its latest failed or pending run cannot be bypassed.

For rollout, commit the new workflows, helpers, tests and regenerated bundles
together and promote through dev and preprod. Older green runs without the new
record do not qualify. If proof is absent, expired, or no longer matches the
historical merge, run **CI → Run workflow** with the updated workflow installed.
Choose `preprod` for its promotion PR, or `release_candidate` for the frozen
candidate's package workflow. Wait for full CI to pass, then retry the blocked step.
This manual CI builds/tests only; it does not upload to PyPI or TestPyPI.

A tree mismatch requires resolving the differing contents in preprod or a reviewed
release-fix PR. Repeating qualification of the old source cannot approve a different merge.

## Release candidate and TestPyPI

Select a green preprod revision through a PR into `release_candidate`. Keep
this branch on one candidate while preprod continues receiving new work.
The PR verifies full preprod qualification and identical merge contents. Merging it pushes the chosen
revision onto release_candidate and starts `release-candidate.yml`; no GitHub Release
or tag is required. Manual dispatch must select the same branch.

| Boundary | Work performed |
| --- | --- |
| `preprod -> release_candidate` PR | Verify the previously qualified preprod tree. |
| Merge lands on `release_candidate` | Recheck source proof, build, upload to TestPyPI, and run installed-package probes. |
| `release_candidate -> prod` PR | Verify exact-source RC success in the final merge-ready check. |

TestPyPI publication belongs to the RC stage. The prod promotion check does not
upload to TestPyPI; it blocks promotion until the earlier RC qualification succeeds.

Branch-route validation stays at the start. The lighter prod PR can finish before
RC upload/probes, so its final candidate check waits up to ten minutes for an
authentic pending run. Completed failure, wrong identity, missing evidence and API
errors still refuse. If the wait expires, finish/fix RC and rerun the failed CI
jobs. Elapsed time never substitutes for successful exact-source qualification.

The workflow reuses the package builder, uploads to TestPyPI, then checks a
fresh installation across the discovered stable no-GIL OS/version matrix. It does not run the whole
source suite again after upload. The probe requires the expected package version,
metadata, import origin in site-packages, packaged assets, and a small public
bind/conjure/resolve/cleanup scenario. The exact downloaded wheel SHA256 must
match this run's built wheel. No editable installation or repository conftest is used.

Configure the TestPyPI upload credential as follows:

| Field | Value |
| --- | --- |
| Project | `melder` |
| GitHub repository | `Synaptic724/melder` |
| Workflow filename | `release-candidate.yml` |
| GitHub environment | `pypitest` |
| Environment secret name | `melder_api_token` |
| Token issuer | `test.pypi.org` |

Create `pypitest` under repository Settings -> Environments and allow deployments
only from the branch `release_candidate`. Add the generated TestPyPI token under
Environment secrets with the name `melder_api_token`; do not put credentials in
Variables or repository files. Select the melder project scope when available.
Creating the first project with token authentication may require an account-scoped
TestPyPI token; replace it with a project-scoped token once the project exists.

This workflow uses explicit API-token authentication (`user: __token__`) and disables
OIDC-only attestations. Only its upload job references the secret. A missing secret
fails with a clear message rather than falling back to OIDC. A token issued by the
production pypi.org service cannot authenticate to TestPyPI. Production continues
using its independent pypi environment and PYPI_API_TOKEN credential.

The initial OIDC run failed with `invalid-publisher`; the owner subsequently chose
token authentication. Adding the secret alone does not change that old workflow.
Commit/promote this updated YAML into release_candidate to use token authentication.
Wait for package-ready to succeed, then rerun any prod PR check that already failed
while qualification was missing. The prod error includes the inspected RC run URL and status.

The package version comes from `src/melder/__version__.py`; CI does not rewrite
it or create version commits. For example, use `0.2.4rc1`, then `0.2.4rc2` for
changed candidates. Regenerate source and repository assets after version changes.
The version metadata test accepts the canonical `rcN` suffix.
The build uses the commit timestamp and normalizes sdist timestamp/ownership
headers so unchanged package contents do not acquire different hashes on retry.

When finalizing, use a reviewed `release-fix/*` PR from the frozen candidate to
set the final version, for example `0.2.4`, and regenerate assets. The release-fix
PR runs full CI; its merge triggers TestPyPI qualification again.
Only the final-version candidate may enter prod.
The final Git tag, for example `v0.2.4`, must match the package version; a tag
cannot turn an rc1 wheel into a final wheel.

TestPyPI filenames are immutable. A changed package requires a new version.
An identical retry is verified by filename, size, and hash; a partial upload
stages only missing files after checking the existing ones. Different remote
bytes fail rather than being hidden by `skip-existing`. Use **Re-run all jobs**
for fresh same-run/attempt artifacts. Download retries are bounded for index
propagation; failed consumer tests are not retried or ignored.

`RC / package-ready` reports explicit success only when authorization, source proof, build,
upload, and every selected OS/version probe succeeded. Prod's existing required CI gate
queries that exact candidate workflow revision; it never substitutes an older
green run for a newer failed or pending one. The upload/install reports include
source commit/tree, version, run/attempt, and both distribution hashes.

## Final publication checks

Publishing a final GitHub release, or manually dispatching the publication
workflow on prod, starts a fresh qualification chain:

1. Require the event and checkout commit to equal fetched current prod HEAD.
   For release events, also require the live remote tag to resolve to that commit.
   Verify the prod merge's candidate parent has the same tree and successful
   TestPyPI qualification for its exact SHA. Direct/squashed prod commits refuse.
2. Rerun hygiene, both asset checkers, and the complete runtime matrix.
3. Build and inspect the wheel/sdist and smoke-test an isolated wheel install.
4. Enter the pypi environment and download this run attempt's verified artifacts.
5. Recheck distribution identity and candidate qualification, then the live release tag,
   fetch/check prod again immediately before the PyPI upload action. Annotated
   tags use their peeled target; missing or moved tags refuse publication.

Earlier dev/preprod success does not replace these checks. A prod movement during
testing or environment approval refuses publication. GitHub prerelease events do
not trigger final publication. All publication runs share a serialization group.
Only the upload job uses the pypi environment and its PYPI_API_TOKEN secret.
Production builds and validates fresh final distributions; it does not relabel
or claim byte identity with an earlier rcN package.

Artifacts include the workflow run and attempt in their names. After a failed
publication, use **Re-run all jobs** to obtain fresh qualification and fresh
artifacts; rerunning only a failed upload must not reuse an earlier attempt's
unqualified artifact implicitly. Confirm PyPI state before retrying an upload
whose outcome is uncertain; existing package versions are never silently skipped.

## Activating GitHub enforcement

The JSON files in `.github/rulesets/` are reviewed configuration payloads;
checking them into Git does not activate GitHub rules. They require PRs and
`CI / merge-ready` from the verified GitHub Actions app (ID 15368), forbid force
pushes and branch deletion, and grant no bypass actors. Human approvals default
to zero so a sole maintainer can merge their own tested PR; review policy can be
strengthened separately.

Deploy the workflows first, run a PR through them, and confirm the exact status
name appears before applying these rules. Otherwise a missing required check
will block every merge. Inspect existing rulesets and update a matching one by
ID rather than creating duplicates. For an initial installation:

```bash
gh api repos/Synaptic724/melder/rulesets
gh api --method POST repos/Synaptic724/melder/rulesets --input .github/rulesets/dev.json
gh api --method POST repos/Synaptic724/melder/rulesets --input .github/rulesets/preprod.json
gh api --method POST repos/Synaptic724/melder/rulesets --input .github/rulesets/release_candidate.json
gh api --method POST repos/Synaptic724/melder/rulesets --input .github/rulesets/prod.json
```

Confirm a failing PR is blocked and a passing PR can merge. Removing or renaming
the required status later requires a coordinated ruleset change.

## Continuous staging and dated candidates

Candidate qualification is automated; selection and prod promotion remain
deliberate PR operations. Automatic dev-to-preprod PR maintenance and dated
publication are future work. A dated release must select an explicit green
candidate SHA, version, approval, and timestamp; advancing preprod must not
change that selected release. No scheduler is enabled by these workflows.
