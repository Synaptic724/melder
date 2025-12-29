# dir_ctx_prompt

Purpose
- Generate or refresh a __<DirectoryName>__.dir.json dir_ctx artifact.
- Use dir_ctx_prompt_tests.md for directories under test_roots.

Required sections
- identity (dir_path, ctx_path, name)
- agent.summary, agent.architecture, agent.inventory
- agent.integration, agent.testing
- computed (preserve scanner-owned fields)

Do not include
- Volatile timestamps in agent.*
- Full file listings outside inventory
- Operational metrics

Output rules
- Emit minified JSON only.
- Use json.dumps(..., separators=(",", ":"), ensure_ascii=False, sort_keys=True, allow_nan=False).
- Output must be parse-valid JSON with no extra text.

Short example (agent.summary)
- one_liner: "Contains spellbook binding logic and config validation."
- detail: "Owns binding and configuration APIs; does not include aether runtime concerns."
