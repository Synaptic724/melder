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
- `context_compass/branch_management/<branch>/state/architecture_context.json`
- `context_compass/branch_management/<branch>/state/component_contexts.json`
- `context_compass/branch_management/<branch>/state/test_architecture_context.json`
- `context_compass/branch_management/<branch>/state/test_component_contexts.json`

Tools
- `context_compass/tools/context_architecture_survey.py`
- `context_compass/tools/context_component_survey.py`
- `context_compass/tools/context_architecture_check.py`
- `context_compass/tools/context_component_check.py`
- `context_compass/tools/context_architecture_resurvey.py`
- `context_compass/tools/context_component_resurvey.py`
