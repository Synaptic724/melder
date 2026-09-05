# Component patch: candidate qualification

## Before and after
Before: preprod/prod perform local distribution checks; no index round-trip qualifies a candidate.
After: release-candidate.yml calls shared CI for the frozen branch, records package identity,
uploads to TestPyPI, and checks an exact downloaded wheel on Linux/Windows Python 3.14t.

## Interfaces
- ci.yml becomes callable and recognizes release_candidate PRs. Candidate pushes are handled by
  their dedicated caller, avoiding duplicate automatic runtime matrices for the same event.
- candidate artifacts contain candidate.json and dist/ with exactly one wheel and one sdist.
- A candidate helper records/verifies artifacts without importing Melder in publication jobs.
- TestPyPI upload remains a top-level job with testpypi environment and id-token: write.
- A reusable installed-candidate workflow downloads one named artifact/run, resolves the TestPyPI
  wheel with pinned version/hash, and invokes an isolated installed-package probe.

## State and failure
The Git tree is the source identity and distributions are the publication identity. Never infer
either from a branch name alone. Missing/extra files, invalid JSON, changed bytes, stale branch
identity, failed installs, and version mismatch refuse qualification. A failed run cannot produce
qualified-candidate evidence. A partially completed upload can continue with missing files only
after existing remote filenames, sizes, and hashes match the local candidate exactly.

## Ownership and validation
Temporary downloads and virtual environments are task/job-owned and cleaned deterministically.
Upload and install jobs are separate; installed package code receives no publication credentials.
Tests cover malformed records, directory escape, altered bytes, remote-file mismatch, retry behavior,
unsupported refs, and absence of source-checkout imports in the runtime probe.
