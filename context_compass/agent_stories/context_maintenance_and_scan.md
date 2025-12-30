# context_maintenance_and_scan

Purpose
- Keep directory and file ctx JSON fresh so agents prefer ctx over code.

Story steps
1) Scan for staleness
   - Confirm repo_state.json allows scan; if tooling_policy is restricted, stop and request enablement.
   - Run `context_compass/tools/scan.py` or read the latest scan output.
   - Scanner computes code/subtree hashes and updates ctx computed fields.
   - Missing/stale/needs_review/blocked ctx items become tasks.
   - Architecture/component contexts are checked against their citation matrix and can emit resurvey tasks.

2) Resolve ctx tasks first
   - Generated tasks land in the ready branch queue.
   - Move ready items into active before executing them.
   - Refresh or regenerate ctx before feature work.
   - Refresh file ctx before regenerating dir ctx; dir ctx is derived from file ctx, not code.

3) Perform feature work
   - Use ctx JSON as primary truth.
   - Use directory ctx as the sole source of structural understanding.
   - If directory ctx is insufficient, stop and refresh dir ctx before proceeding.
   - Open code only when ctx is missing or insufficient.

4) Restore freshness after edits
   - Do not manually edit ctx JSON after code changes.
   - Run scan to emit refresh tasks, then resolve them.
   - Re-scan or validate so freshness_state returns to fresh.

5) Validate (optional CI)
   - `context_compass/tools/validate.py` checks schema + staleness.

Artifacts touched
- `__<stem>__.json` and `__<dir>__.dir.json`
- `context_compass/branch_management/<branch>/state/scans/scan_*.json`
- `context_compass/branch_management/<branch>/state/repo_state.json`
- `context_compass/branch_management/<branch>/work_management/ready/tasks.json`

Tools
- `context_compass/tools/scan.py`
- `context_compass/tools/validate.py`
- `context_compass/tools/update_state.py` (scan metadata)

References
- `context_compass/skills/context_protocol.md`
- `context_compass/skills/staleness_protocol.md`
