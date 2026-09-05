# Branch CI and release workflow

Contributions enter `dev` through a pull request. Promotion proceeds through
`dev -> preprod -> prod`, with the merge result checked at every boundary.

## Required checks

`CI / merge-ready` is the stable status to require in GitHub. It depends on:

- Branch policy: contributions target dev; preprod accepts this repository's dev,
  and prod accepts this repository's preprod. Forks cannot impersonate promotion
  branches. Same-repository preprod/prod synchronization PRs may return to dev.
- Source assets: the existing build-asset runner verifies committed manifests.
- Repository assets: the LLM builder verifies committed bundles and indexes.
- Repository hygiene: tracked filenames must not collide case-insensitively.
- Documentation: the shared documentation validation workflow must succeed.
- Runtime tests: unit, component, and integration tiers on Linux and Windows,
  using Python 3.14t with the GIL disabled in the actual pytest process.
- Distribution verification for preprod/prod: wheel and sdist boundaries,
  source/metadata/asset versions, and an isolated installed-wheel smoke test.

The final status fails for missing evidence, failure, cancellation, or an
unexpected skipped job. Only dev intentionally skips distribution building.
Repository variables cannot disable mandatory asset checks. Helpers remain
manually runnable but automatic PR/push triggering belongs to `ci.yml`.

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

CI runs on PR updates, including a changed PR base, and on permanent-branch
pushes. Heavy CI does not also run on every feature push before its PR. New PR
commits supersede old CI runs. Reusable helpers have no concurrency group that
could accidentally cancel their caller or a final release.

## Promotion and merge history

Prefer squash for disposable feature branches, and start the next feature from
current dev. Use merge commits between permanent branches. Do not repeatedly
squash dev into preprod or preprod into prod.

The supplied dev ruleset requires an up-to-date branch. Promotion rulesets use
the current PR merge result with the one permitted source branch and merge
commits. They deliberately do not require dev to contain every preprod-only
merge commit, which otherwise creates a perpetual merge-back requirement.
Resolve conflicts on the source branch and rerun CI; carry release/hotfix changes
back into dev through a reviewed synchronization PR.

## Final publication checks

Publishing a final GitHub release, or manually dispatching the publication
workflow on prod, starts a fresh qualification chain:

1. Require the event and checkout commit to equal fetched current prod HEAD.
   For release events, also require the live remote tag to resolve to that commit.
2. Rerun hygiene, both asset checkers, and the complete runtime matrix.
3. Build and inspect the wheel/sdist and smoke-test an isolated wheel install.
4. Enter the pypi environment and download this run attempt's verified artifacts.
5. Recheck distribution identity and the live remote release-tag target, then
   fetch/check prod again immediately before the PyPI upload action. Annotated
   tags use their peeled target; missing or moved tags refuse publication.

Earlier dev/preprod success does not replace these checks. A prod movement during
testing or environment approval refuses publication. GitHub prerelease events do
not trigger final publication. All publication runs share a serialization group.
Only the upload job uses the pypi environment and its PYPI_API_TOKEN secret.

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
gh api --method POST repos/Synaptic724/melder/rulesets --input .github/rulesets/prod.json
```

Confirm a failing PR is blocked and a passing PR can merge. Removing or renaming
the required status later requires a coordinated ruleset change.

## Continuous staging and dated candidates

This foundation validates promotion PRs and final publication. The next layer
can maintain a dev-to-preprod PR automatically using an appropriately scoped
GitHub App. A dated release must select an explicit green candidate SHA,
version, artifact hashes, approval, and timestamp; moving preprod must not change
the scheduled candidate. Candidate-specific routing, retained artifacts, and
scheduled publication are configured separately before that behavior is enabled.
