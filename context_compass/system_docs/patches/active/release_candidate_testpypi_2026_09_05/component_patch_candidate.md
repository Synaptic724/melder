# Component patch: candidate qualification

## Before and after
Before: preprod/prod perform local distribution checks; no index round-trip qualifies a candidate.
After: release-candidate.yml calls the existing package builder for the frozen branch, records identity,
uploads to TestPyPI, and checks an exact downloaded wheel on Linux/Windows Python 3.14t.

## Interfaces
- ci.yml recognizes release_candidate PRs. Candidate pushes are handled by the dedicated workflow.
- Every job downloads the same run/attempt's verified wheel/sdist pair; reports record their hashes.
- A candidate helper verifies package/index identity without importing Melder in publication jobs.
- Shared builds normalize sdist tar/gzip metadata to the commit timestamp, preserving all file bytes.
  This closes measured same-source retry drift without weakening immutable-upload hash checks.
- TestPyPI upload remains a top-level job with pypitest environment and id-token: write.
- Linux/Windows install jobs resolve the TestPyPI wheel with pinned version/hash and invoke an
  isolated installed-package probe. Neither runs the whole source suite or obtains upload authority.

## State and failure
The Git tree is the source identity and distributions are the publication identity. Never infer
either from a branch name alone. Missing/extra files, invalid JSON, changed bytes, stale branch
identity, failed installs, and version mismatch refuse qualification. A failed run cannot produce
successful candidate evidence. A partially completed upload can continue with missing files only
after existing remote filenames, sizes, and hashes match the local candidate exactly.

## Ownership and validation
Temporary downloads and virtual environments are task/job-owned and cleaned deterministically.
Upload and install jobs are separate; installed package code receives no publication credentials.
Tests cover malformed records, directory escape, altered bytes, remote-file mismatch, retry behavior,
unsupported refs, and absence of source-checkout imports in the runtime probe.
