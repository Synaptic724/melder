# Architecture and Component Contexts

Purpose
- Provide a branch-scoped meta-layer above file/dir ctx.
- Summarize architecture and components using directory ctx only.
- Degrade deterministically as underlying ctx drifts.

Artifacts (branch-scoped)
- `context_compass/branch_management/<branch>/state/architecture_context.json`
- `context_compass/branch_management/<branch>/state/component_contexts.json`
- `context_compass/branch_management/<branch>/state/test_architecture_context.json`
- `context_compass/branch_management/<branch>/state/test_component_contexts.json`

Inputs (citations matrix)
- Each artifact stores a matrix of directory ctx citations:
  - ctx_path
  - subtree_hash_sha256
  - ctx_semantic_hash_sha256
  - freshness_state

Freshness thresholds (good ratio)
- > 0.90: good
- > 0.75: stale
- > 0.60: faulty
- <= 0.60: faulty

Survey vs scan
- Survey tools regenerate agent.* content and rebuild the matrix.
- Scan checks the matrix against current ctx, updates computed.*, and emits resurvey tasks.
- Scan does not rewrite agent.* content.

Tasks emitted by scan
- resurvey_architecture_context
- resurvey_component_contexts
- resurvey_test_architecture_context
- resurvey_test_component_contexts

Commands
- Build architecture context:
  `python context_compass/tools/context_architecture_survey.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
- Build component contexts:
  `python context_compass/tools/context_component_survey.py --repo-root . --agent-id <agent_id> --work-id <work_id>`
- Test variants:
  `python context_compass/tools/context_architecture_survey.py --repo-root . --agent-id <agent_id> --work-id <work_id> --target test`
  `python context_compass/tools/context_component_survey.py --repo-root . --agent-id <agent_id> --work-id <work_id> --target test`

Rules
- Do not read code directly when generating these artifacts.
- Refresh dir ctx before resurveying architecture/components.
- If tooling is restricted by repo_state, do not run surveys.
