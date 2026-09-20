# Architecture patch: reproducible uv development environment

- Owner: TASK-2026-09-08-reproducible-uv-environment

## Boundary
Root uv.lock pins repository development dependency groups. Project runtime dependencies stay
empty and library consumers retain their own dependency resolution. The separate documentation
lock remains authoritative for the Sphinx toolchain. Existing environments are never replaced by
agent validation; use a task-owned UV_PROJECT_ENVIRONMENT.

## Contracts
Generate the lock with uv against public PyPI. Preserve declared requirements and all optional
groups. Use --locked to refuse dependency drift, and explicit free-threaded Python for runtime
work. Record the tested uv minimum in pyproject configuration so unsupported clients fail clearly.

## Deliverables and rollback
Provide lock, contributor instructions and a public README pointer. Owner selected CI adoption
with explicit preservation of the dynamic Python/OS matrix. Revert these
scoped development files together if declined; do not alter package APIs or publication authority.

## Validation
Check lock freshness, fresh isolated sync, installed runtime requirements, no-GIL interpreter,
focused existing tests and a verified wheel/sdist built with the locked build group.

## CI integration
Keep setup-python and the existing no-GIL matrix. Pass each selected interpreter path to locked
uv sync. Runtime jobs install the test group and project; distribution jobs install only the build
group and build without isolation. Run commands through the synced environment without re-resolution.
UV cache keys include lockfile and runtime/build context. Wheel probes remain isolated consumers.
Documentation retains its separate lock; stdlib-only discovery/policy jobs need no dependency sync.
