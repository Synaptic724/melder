# Branch CI and release workflow

Contributions enter `dev` through a pull request. Promotion proceeds through
`dev -> preprod -> release_candidate -> prod`, with the merge result checked at every boundary.

## Required checks

`CI / merge-ready` is the stable status to require in GitHub. It depends on:

- Branch policy: contributions target dev; preprod accepts this repository's dev,
  release_candidate accepts preprod, and prod accepts release_candidate. Forks
  cannot impersonate promotion branches. Permanent-branch synchronization PRs
  may return to dev. Same-repository `release-fix/*` PRs can prepare or fix the
  frozen candidate; keep their scope narrow and carry fixes back to dev.
- Source assets: the existing build-asset runner verifies committed manifests.
- Repository assets: the LLM builder verifies committed bundles and indexes.
- Repository hygiene: tracked filenames must not collide case-insensitively.
- Documentation: the shared documentation validation workflow must succeed.
- Runtime tests: unit, component, and integration tiers on Linux and Windows,
  using Python 3.14t with the GIL disabled in the actual pytest process.
- Distribution verification for preprod/release_candidate/prod: wheel and sdist boundaries,
  source/metadata/asset versions, and an isolated installed-wheel smoke test.
- Prod candidate proof: the exact source head must have successful TestPyPI
  qualification, a final package version, and the same tree as the merge result.

The final status fails for missing evidence, failure, cancellation, or an
unexpected skipped job. Only dev intentionally skips distribution building.
Repository variables cannot disable mandatory asset checks. Helpers remain
manually runnable. `ci.yml` owns source CI; `release-candidate.yml` owns candidate pushes.

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

CI runs on PR updates, including a changed PR base, and on dev/preprod/prod
pushes. Candidate pushes run the slim package workflow below. Heavy CI does not
also run on every feature push before its PR. New PR
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

## Release candidate and TestPyPI

Select a green preprod revision through a PR into `release_candidate`. Keep
this branch on one candidate while preprod continues receiving new work.
Every push to release_candidate runs `release-candidate.yml`; no GitHub Release
or tag is required. Manual dispatch must select the same branch.

The workflow reuses the package builder, uploads to TestPyPI, then checks a
fresh installation on Linux and Windows Python 3.14t. It does not run the whole
source suite again after upload. The probe requires the expected package version,
metadata, import origin in site-packages, packaged assets, and a small public
bind/conjure/resolve/cleanup scenario. The exact downloaded wheel SHA256 must
match this run's built wheel. No editable installation or repository conftest is used.

Use these exact values for the TestPyPI Trusted Publisher:

| Field | Value |
| --- | --- |
| Project | `melder` |
| GitHub owner | `Synaptic724` |
| Repository | `melder` |
| Workflow filename | `release-candidate.yml` |
| GitHub environment | `pypitest` |

Create `pypitest` under repository Settings -> Environments and allow deployments
only from the branch `release_candidate`. The upload job alone receives
`id-token: write`. No TestPyPI API token secret is needed with Trusted Publishing.
The production `pypi` environment and its existing authentication stay separate.

The package version comes from `src/melder/__version__.py`; CI does not rewrite
it or create version commits. For example, use `0.2.4rc1`, then `0.2.4rc2` for
changed candidates. Regenerate source and repository assets after version changes.
The version metadata test accepts the canonical `rcN` suffix.
The build uses the commit timestamp and normalizes sdist timestamp/ownership
headers so unchanged package contents do not acquire different hashes on retry.

When finalizing, use a reviewed `release-fix/*` PR from the frozen candidate to
set the final version, for example `0.2.4`, and regenerate assets. That push runs
TestPyPI qualification again. Only the final-version candidate may enter prod.
The final Git tag, for example `v0.2.4`, must match the package version; a tag
cannot turn an rc1 wheel into a final wheel.

TestPyPI filenames are immutable. A changed package requires a new version.
An identical retry is verified by filename, size, and hash; a partial upload
stages only missing files after checking the existing ones. Different remote
bytes fail rather than being hidden by `skip-existing`. Use **Re-run all jobs**
for fresh same-run/attempt artifacts. Download retries are bounded for index
propagation; failed consumer tests are not retried or ignored.

`RC / package-ready` reports explicit success only when authorization, build,
upload, and both platform probes succeeded. Prod's existing required CI gate
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
