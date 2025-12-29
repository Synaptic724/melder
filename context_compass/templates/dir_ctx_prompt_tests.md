# dir_ctx_prompt_tests

Purpose
- Generate or refresh a __<Directory>__.dir.json dir_ctx artifact for test directories.

Input sources (strict)
- Build dir ctx from file ctx artifacts within the test directory tree.
- Do not read test code directly unless file ctx is missing; refresh file ctx first.

Required sections
- identity (dir_path, ctx_path, name)
- agent.summary, agent.architecture, agent.inventory, agent.integration, agent.testing
- computed (preserve scanner-owned fields)

Test-specific guidance
- Describe which production areas this test directory covers.
- List shared fixtures/helpers and how they are intended to be used.
- Call out integration vs unit test boundaries.
- Explicitly note markers (pytest -m integration) if used.

Do not include
- Timestamps in agent.*
- Volatile counters in agent.*
- Raw file contents in agent.*

Output rules
- Emit minified JSON only.
- Use json.dumps(..., separators=(",", ":"), ensure_ascii=False, sort_keys=True, allow_nan=False).
- Output must be parse-valid JSON with no extra text.

Ownership rules
- agent.* is owned by the agent. Fill fully and explicitly.
- computed.* is owned by the scanner. Preserve existing computed.* values verbatim when refreshing.

Short example (agent.testing)
- commands: ["python -m pytest tests/unit -q"]
- required_when_changed: ["unit"]
- recommended_when_changed: ["integration"]
