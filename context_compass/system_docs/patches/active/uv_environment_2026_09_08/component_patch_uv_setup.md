# Component patch: uv project setup

## Dependency declaration and resolution
pyproject retains broad direct requirements and existing dependency groups. uv.lock is generated
resolution truth, including environment markers, artifact hashes and the editable root project.
Do not hand-edit its entries or turn development packages into Requires-Dist runtime metadata.

## Contributor interface
CONTRIBUTING.md documents uv sync --locked with free-threaded Python, no-GIL test execution,
optional groups, asset verification and explicit dependency upgrades. README links this guide;
package-install instructions continue working independently of uv.

## Build and failure behavior
The default dev group includes the build group. Building without isolation uses that locked
toolchain; the existing distribution verifier remains the boundary check. Lock drift refuses
under --locked, and actual sync/build failures are reported rather than changing requirements.
