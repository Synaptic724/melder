# context_profiles_flow

Purpose
- Explain how context profiles are built, consumed, reviewed, and resurveys are triggered.

Story steps
1) Survey
   - `context_compass/tools/context_profiles_survey.py` builds profiles from ctx JSON and work queues.
   - Profile inputs are hashed against live code/subtree hashes to detect drift.
   - If `source_roots.json` is configured, prod_overview/tests_overview profiles are emitted.

2) Read
   - `context_compass/tools/context_profiles_read.py` emits consolidated ctx JSON.
   - Usage counts increment and freshness is re-evaluated.

3) Review
   - `context_compass/tools/context_profiles_review.py` records grades and notes.
   - Poor/bad grades emit optimize/prune tasks.

4) Resurvey when stale
   - `context_profiles_read` emits `resurvey_context_profile` tasks when inputs drift.
   - `context_compass/tools/context_profiles_resurvey.py` rebuilds profiles and closes the task.

Artifacts touched
- `context_compass/branch_management/<branch>/state/context_profiles.json`
- `context_compass/branch_management/<branch>/work_management/active/tasks.json`

Tools
- `context_compass/tools/context_profiles_survey.py`
- `context_compass/tools/context_profiles_read.py`
- `context_compass/tools/context_profiles_review.py`
- `context_compass/tools/context_profiles_resurvey.py`

References
- `context_compass/skills/context_profiles.md`
