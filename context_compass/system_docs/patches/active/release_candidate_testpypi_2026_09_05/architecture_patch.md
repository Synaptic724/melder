# Architecture patch: frozen candidate and TestPyPI qualification

- Patch ID: release_candidate_testpypi_2026_09_05
- Owner: TASK-2026-09-05-release-candidate-testpypi-workflow

## Scope
Use dev -> preprod -> release_candidate -> prod. Preprod continuously validates the complete
supported suite, docs/assets, version agreement, distributions, and installed package. Candidate
advancement is an owner-selected promotion, never automatic mirroring of preprod.

## Boundaries and invariants
- Shared CI remains read-only and checks every PR to the four supported destination branches.
- release_candidate accepts this repository's preprod and reviewed release-fix/* preparation PRs;
  prod accepts only release_candidate. Carry candidate fixes/version preparation back to dev.
- Candidate PRs receive shared CI. Candidate pushes run package qualification without another full suite.
- Only the TestPyPI upload job uses the pypitest environment and its OIDC publication permission.
- Candidate identity includes repository, commit, complete Git tree, package version, workflow run
  and attempt, and the exact wheel/sdist filenames, lengths, and SHA256 hashes.
- TestPyPI installation resolves the exact version and verifies downloaded bytes against that record.
- Only successful Linux/Windows installed-package checks produce the candidate-ready result.
- Prod PR checks require successful candidate qualification of the exact source head and matching tree.
- Final publication verifies that its prod merge came from that qualified candidate tree, then retains
  the existing fresh tests/build and live tag/prod guards. It publishes its own freshly verified files;
  no claim is made that changing rcN to final or rebuilding a package preserves candidate bytes.

## Version contract
Use the version explicitly committed in __version__.py; never rewrite it implicitly in CI. Stable
versions and rcN candidates are supported. Version changes require matching regenerated assets.
Finalization from rcN to final is a reviewed release-fix/* PR on the frozen branch; run this same
TestPyPI workflow for the final-version candidate before promotion. No candidate-version bypass.
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
This task owns branch routing, candidate qualification, a small source-provenance gate, focused regression
tests, and the operator guide. No runtime subsystem architecture or public Melder API changes.
