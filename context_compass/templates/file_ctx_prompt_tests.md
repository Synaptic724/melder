# file_ctx_prompt_tests

Purpose
- Generate or refresh a __<FileStem>__.json file_ctx artifact for test files.

Required sections
- identity (path, ctx_path, language, module if known)
- agent.summary, agent.role_in_system, agent.public_surface
- agent.behavioral_contract, agent.dependencies, agent.dependents
- agent.lifecycle, agent.testing, agent.examples
- computed (preserve scanner-owned fields)

Test-specific guidance
- Set agent.role_in_system.layer to "tests".
- In agent.testing, describe:
  - test_types (unit/integration/component/system)
  - fixtures used and why
  - mocks/stubs boundaries
  - coverage expectations (what must be validated when prod code changes)
- In agent.behavioral_contract, describe the production behavior verified and the failure signals.
- In agent.examples, include short pytest-style snippets only if they clarify usage.

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
- test_types: ["unit"]
- commands: ["python -m pytest tests/unit/test_widget.py -q"]
- fixtures: ["widget_fixture: stable widget configuration"]
- mocks: ["network calls to FooAPI"]
- coverage_expectations: ["updates to Widget.validate must update these tests"]
