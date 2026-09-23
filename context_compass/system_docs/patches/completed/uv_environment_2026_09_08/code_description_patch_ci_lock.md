# Code-description patch: matrix-aware locked CI

## Runtime
Checkout -> setup selected Python/architecture with freethreaded=true -> setup uv -> sync --locked
--no-default-groups --group test with the selected python-path -> uv run --no-sync test driver.
The existing PYTHON_GIL=0 scope, coverage naming/selection, JUnit retention and result gates remain.

## Distribution
Checkout -> setup supported free-threaded Python -> setup uv -> sync --locked --only-group build
using that interpreter -> uv run --no-sync build --no-isolation -> normalize and inspect artifacts.
An independent uv-created environment installs only the exact built wheel with --no-deps and runs
the isolated smoke script. The publishing job still receives only verified distribution artifacts.

## Failure and validation
Stale lock fails during sync, before tests/build. No --frozen escape, lock upgrades, or global pip
mutation in CI. Preserve every matrix cell and propagate command failures. Cache configuration
tracks uv.lock and separates runtime Python/architecture from build contexts. Verify parsed workflow
wiring, real locked group sync and isolated wheel behavior; preserve final publication checks.
