# Component patch: production candidate provenance

## Slimmed scope accepted by owner
Keep the existing fresh production runtime/assets/build pipeline and its own verified distributions.
Add a read-only qualification check for the exact candidate source, rather than a new retained-artifact
promotion engine or another complete source-suite run after the TestPyPI installation.

## Promotion and release checks
For a prod PR, inspect the exact release_candidate head from the event. For publication, inspect
the second parent of the required prod promotion merge. In both cases require that candidate's tree
to equal the checkout tree and the latest candidate workflow run for that SHA to have succeeded.
Verify repository, workflow path, branch, event, and full commit identity in the API response.
Prod PRs/release also require a final package version, never an rcN package mislabeled with a final tag.

## Failure semantics
No matching candidate run, failed/pending qualification, mismatched tree, a direct prod commit, or
invalid API evidence blocks promotion/publication. The final publisher repeats this candidate check
before its existing live tag/prod check, which remains last. No package upload is used as local validation.

## Validation
Boundary tests cover valid merge/source identity, failed/pending/forged runs, and changed candidate
trees. Parsed workflow tests preserve fresh final runtime/build dependencies and environment isolation.
