# Architecture patch: frozen candidate and TestPyPI qualification

- Patch ID: release_candidate_testpypi_2026_09_05
- Owner: TASK-2026-09-05-release-candidate-testpypi-workflow

## Scope
Use dev -> preprod -> release_candidate -> prod. Preprod continuously validates the complete
supported suite, docs/assets, version agreement, distributions, and installed package. Candidate
advancement is an owner-selected promotion, never automatic mirroring of preprod.

## Boundaries and invariants
- Shared CI remains read-only and checks every PR to the four supported destination branches.
- release_candidate accepts only this repository's preprod; prod accepts only release_candidate.
- Candidate qualification runs only on the real release_candidate branch after shared CI succeeds.
- Only the TestPyPI upload job uses the testpypi environment and its OIDC publication permission.
- Candidate identity includes repository, commit, complete Git tree, package version, workflow run
  and attempt, and the exact wheel/sdist filenames, lengths, and SHA256 hashes.
- TestPyPI installation resolves the exact version and verifies downloaded bytes against that record.
- Only successful Linux/Windows installed-package checks produce a retained qualified artifact.
- Production chooses a successful candidate run once, then pins that run/attempt for all later jobs.
- The candidate tree must equal the final prod tree. A merge-commit SHA may differ without changing
  any source, configuration, or workflow input; different trees require new qualification.
- Final publication reruns full validation/build, verifies the retained candidate files, and publishes
  those files after checking live candidate/tag/prod identity. Earlier CI never replaces final tests.

## Version contract
Recommended/default mode stages the intended final package version on TestPyPI. The production
upload uses identical bytes. Actual rc1/rc2 package versions cannot be silently renamed to final.
A reused TestPyPI filename with different bytes refuses qualification; changes require a new
version. An existing identical upload may be reused only after every remote file digest is checked.

## Rollout and rollback
1. Land workflow/helper/test definitions through dev and preprod.
2. Owner promotes the chosen source/version into release_candidate and configures TestPyPI trust.
3. Observe the candidate check, then enable the candidate branch ruleset and updated prod route.
4. Promote the frozen qualified tree to prod; publish only after the fresh final checks.
Rollback callers, branch policy, and required rules together. Never bypass failed candidate identity.

## Non-goals and unknowns
No actual upload, account creation, signing, commit, push, or branch rename in local implementation.
No date/time scheduler yet. TestPyPI project ownership/trusted publisher and hosted runs remain
external setup/validation. Candidate artifacts are retained in GitHub rather than relying on TestPyPI
as permanent storage.

## Coverage
This task owns branch routing, candidate qualification, final provenance gates, focused regression
tests, and the operator guide. No runtime subsystem architecture or public Melder API changes.
