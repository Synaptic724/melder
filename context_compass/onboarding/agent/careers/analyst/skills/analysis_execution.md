# analysis_execution

Purpose
- Define how analyst agents collect evidence, synthesize findings, and report clearly.

Core rules
- Keep analysis grounded in repo data, tool output, or explicit user statements.
- Separate facts, assumptions, and open questions.
- Prefer reproducible queries and deterministic summaries.
- Use SQLite Query API for cross-table reports; use CRUD for single-table reads.

Preferred workflow
1) Clarify the question and scope.
2) Collect evidence (queries, logs, or documented artifacts).
3) Summarize facts and list uncertainties.
4) Provide recommendations with rationale.

References
- `context_compass/onboarding/agent/general/skills/testing/evidence_reporting.md`
- `context_compass/onboarding/agent/general/skills/command_registry.md`
