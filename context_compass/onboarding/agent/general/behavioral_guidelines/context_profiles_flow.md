# context_profiles_flow

Purpose
- Explain how context profiles are built, consumed, reviewed, and resurveys are triggered.

Story steps
1) Survey
   - ToolCommandAPI command `context_profiles_survey` builds profiles from ctx JSON and work queues.
   - Profile inputs are hashed against live code/subtree hashes to detect drift.
   - If SQLite source roots are configured (`config_source_roots_*`), prod_overview/tests_overview profiles are emitted.

2) Read
   - ToolCommandAPI command `context_profiles_read` emits consolidated ctx JSON.
   - Usage counts increment and freshness is re-evaluated.

3) Review
   - ToolCommandAPI command `context_profiles_review` records grades and notes.
   - Poor/bad grades emit optimize/prune tasks.

4) Resurvey when stale
   - `context_profiles_read` emits `resurvey_context_profile` tasks when inputs drift.
   - ToolCommandAPI command `context_profiles_resurvey` rebuilds profiles and closes the task.

Artifacts touched
- SQLite user.db tables `context_profiles` + `context_profile_items`.
- SQLite user.db tables `context_profile_item_paths` + `context_profile_item_staleness_reasons`.
- SQLite user.db tables `work_queues` and `work_queue_items` (scope=branch, branch_name set, bucket=ready, work_kind=task).

Tools
- ToolCommandAPI commands: `context_profiles_survey`, `context_profiles_read`,
  `context_profiles_review`, `context_profiles_resurvey`.

References
- `context_compass/onboarding/agent/general/skills/context_profiles.md`
