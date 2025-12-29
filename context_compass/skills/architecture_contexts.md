# architecture_contexts

Purpose
- Maintain branch-scoped architecture/component context artifacts above file/dir ctx.
- Track freshness using a matrix of directory ctx citations and hashes.

Artifacts (branch-scoped)
- architecture_context.json
- component_contexts.json
- test_architecture_context.json
- test_component_contexts.json

Strict source rule
- Architecture and component contexts must be derived from directory ctx only.
- Do not read code directly for these artifacts.
- If directory ctx is insufficient, refresh dir ctx before resurveying.

Matrix model (computed lane)
- Matrix entries are stable citations:
  { ctx_path, subtree_hash_sha256, ctx_semantic_hash_sha256, freshness_state }
- inputs_hash is a stable hash of the matrix content.
- Holes are any entry that is missing, stale, needs_review, blocked, or hash-mismatched.

Thresholds (good ratio)
- good: > 0.90
- stale: > 0.75
- faulty: > 0.60 (and anything below)
- These thresholds are configurable in policies.json.

Survey vs scan
- Survey tools regenerate agent.* content and rebuild the matrix.
- Scan checks the matrix against current ctx, updates computed.*, and emits resurvey tasks.
- Scan does not rewrite agent.* fields.

Tasks emitted by scan
- resurvey_architecture_context
- resurvey_component_contexts
- resurvey_test_architecture_context
- resurvey_test_component_contexts

Checks
- check tools read computed state and warn when stale or faulty.
- If faulty, advise re-running scan, then resurvey.

References
- context_compass/user_documentation/context_and_scan.md
