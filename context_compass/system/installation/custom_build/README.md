# Custom Build Scripts

Purpose
- Provide user-defined or site-specific build steps executed by `installation/build_runner.py`.
- Extend installation without modifying core build scripts.

Contract
- Each script must implement `run(context: BuildContext) -> None`.
- Scripts must be deterministic and idempotent (safe to rerun).
- Use logging instead of print for output.
- Do not mutate `context` fields; treat them as read-only.
