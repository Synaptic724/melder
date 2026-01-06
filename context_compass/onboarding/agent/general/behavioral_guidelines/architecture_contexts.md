# architecture_contexts

Purpose
- Describe the survey/check/resurvey flow for architecture and component contexts.

Story steps
1) Build architecture/component contexts (survey)
   - Run the survey tools for prod and test scopes.
   - Surveys derive content from directory ctx only and rebuild the citation matrix.

2) Scan for drift
   - Scan evaluates the matrix against current directory ctx hashes.
   - If drift is detected, scan emits resurvey tasks.

3) Respond to drift
   - If stale: warn the user and recommend a resurvey.
   - If faulty: resurvey immediately and confirm the artifact state returns to good.

Artifacts touched
- SQLite user.db table `architecture_context` (branch_name + kind=architecture_context/test_architecture_context).
- SQLite user.db table `component_contexts` (branch_name + kind=component_contexts/test_component_contexts).

Tools
- `context_compass/system/ai_restricted/context_management/context_architecture_survey.py`
- `context_compass/system/ai_restricted/context_management/context_component_survey.py`
- `context_compass/system/ai_restricted/context_management/context_architecture_check.py`
- `context_compass/system/ai_restricted/context_management/context_component_check.py`
- `context_compass/system/ai_restricted/context_management/context_architecture_resurvey.py`
- `context_compass/system/ai_restricted/context_management/context_component_resurvey.py`
