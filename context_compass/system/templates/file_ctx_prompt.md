# file_ctx_prompt

Purpose
- Generate or refresh a __<FileStem>__.json file_ctx artifact.
- Use file_ctx_prompt_tests.md for files under test_roots.

Required sections
- identity (path, ctx_path, language, module if known)
- agent.summary, agent.role_in_system, agent.public_surface
- agent.behavioral_contract, agent.dependencies, agent.dependents
- agent.lifecycle, agent.testing, agent.examples
- computed (preserve scanner-owned fields)

Design and architecture capture
- Capture design patterns, structural roles, and behavioral contracts explicitly in agent.role_in_system and agent.behavioral_contract.
- Call out SOLID-style responsibilities and boundaries (single-responsibility, dependency direction, extension points).
- Note architectural constraints or invariants in agent.role_in_system.invariants and pitfalls.

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

Short example (agent.summary)
- one_liner: "Parses foo headers into a normalized model."
- detail: "Consumes raw header lines and returns a validated model; it does not read from disk."
