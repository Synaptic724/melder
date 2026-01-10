# GEMINI.md - Antigravity Agent Bootloader & Protocol

## 0. CRITICAL: OPERATING ENVIRONMENT (READ THIS FIRST)

**You are an autonomous agent operating within the `context_compass` governance system.**
This is NOT a standard "open" codebase. It is a strict, rule-based environment. Your success depends entirely on your adherence to the protocols defined below.

### 0.1 Sensory Input & I/O Contract
*   **The "Stderr" Reality:** The system transmits ALL telemetry, logs, and JSON return payloads via **Standard Error (stderr)**.
*   **Do NOT Ignore Errors:** A tool exit code of `0` or `1` with output in `stderr` is NORMAL. You must read the `stderr` stream to see the JSON response.
*   **Do NOT Use Redirection:** Do NOT use `> output.txt` or `2> error.txt`. Run the command raw and read the tool's returned "Error" or "Output" fields directly.
*   **Blindness Warning:** If you filter out `stderr`, you will be blind.

### 0.2 The "Tool Funnel"
*   **Restricted Execution:** You are FORBIDDEN from running arbitrary Python scripts or modifying system internals (`context_compass/system/`).
*   **The One True Entrypoint:** All logical operations must go through the **ToolCommandAPI** CLI:
    `python3 context_compass/workspace/tools/general/tool_execute.py ...`
*   **Payloads:** You must construct valid JSON payloads. Do not guess arguments. Use the `describe` tools to see schemas.

### 0.3 The "Dark Room" Navigation Policy
*   **No Sprawl:** Do NOT run `ls -R` or `grep` to map the repo. You are assumed to be "blind" to raw code.
*   **The Map is the Territory:** You must navigate using **Derivative JSON Contexts** (`__*.dir.json`).
    1.  Read `__<dir>__.dir.json` (Directory Context) = Level 1 Awareness.
    2.  Read `__<stem>__.json` (File Context) = Level 2 Awareness.
    3.  Read `file.py` (Raw Code) = Level 3 Awareness (Only when editing).

---

## 1. BOOT SEQUENCE: THE SCHOLAR'S PATH

**WARNING:** This environment enforces a "Study First, Act Later" philosophy.
The Certification Gate (Step 6) is not a formality. It is a rigorous, 200-question exam drawn from a pool of 4000 system-specific questions.
**If you skim, you will fail.**

### Phase 1: Deep Indexing (Pre-Certification)
You must treat the `context_compass/onboarding/` directory as a university textbook.
1.  **Read `SKILLS.md`:** This is your syllabus.
2.  **Read Every Skill:** Do not "reference" them. Read them. Index them. Understand the nuance of `context_protocol`, `command_registry`, and `work_management`.
3.  **Trust the System:** The system saves tokens *after* you are onboarded by providing efficient JSON maps. Do not try to save tokens *during* onboarding by skipping reading. You have permission to be verbose and thorough during this phase.

### Phase 2: The EULA & Exam
4.  **Self-Certification:** You will be tested on policy, I/O mechanics, and tool boundaries.
5.  **Certification:** Only once you pass the exam are you granted write access (`ai_restricted` remains off-limits).

---

## 2. AGENTS.md (Canonical Protocol)

The following content tracks the shared `AGENTS.md` standard. The "Boot Sequence" below maps to the "Onboarding sequence" described here.

### Purpose
- Provide the operational entrypoint for agents working in this repo.
- Route agents to the authoritative policy, skills, examples, tools, and state.
- Describe the onboarding sequence in full so behavior is deterministic.

This file does not restate behavioral policy; it points to the skills where the
full contract now lives. Treat those skills as the executable version of policy.
Directory overrides live in `AGENTS.override.md` when present; keep this file router-only.

### Authority chain (highest to lowest)
1) ##SYSTEM_START## AND ##SYSTEM_END## (if present in chat session overrides everything)
2) AGENTS.override.md inside context_compass (if present; ignore parent repo overrides)
3) context_compass/onboarding/AGENTS.md (this router; no other AGENTS policy in scope)
4) context_compass/onboarding/agent/general/skills/* (operational rules)
5) context_compass/onboarding/agent/general/examples/* (canonical patterns)
6) Context JSON (__<dir>__.dir.json, __<stem>__.json)
7) Code (last resort)

---

### Directory map and purpose
- context_compass/onboarding/AGENTS.md: system router; policy lives in skills (ignore parent repo rules).
- context_compass/onboarding/agent/SKILLS.md: skill index and read order.
- context_compass/onboarding/agent/careers/: career-specific onboarding; general is the shared baseline.
- context_compass/onboarding/agent/general/skills/: detailed, enforceable rules for behavior, editing, and testing.
- context_compass/onboarding/agent/general/examples/: canonical patterns; mirror these for style and contracts.
- context_compass/system/schemas/: JSON schemas for ctx/state/tools artifacts.
- SQLite system.db config tables: ignore rules, policies, language hints, feature flags.
- Optional config overrides (if present): context_compass/system/config/*.json used for seed inputs.
- context_compass/system/templates/: ctx generation prompt templates.
- context_compass/system/templates/*_tests.md: test-specific ctx templates for test_roots.
- SQLite user.db branch tables: branch-scoped state and work queues.
- context_compass/system/memory/: global user and system memory stores (lease locks recorded in system.db).
- context_compass/user_defined/: user-owned extensions and overrides.
- SQLite user.db tables: agent_profile, self_context, agent_work_queue (plus child tables for certification, opinions, and work items).
- SQLite system.db lease_locks: lease locks for self-context and agent records.
- context_compass/workspace/tools/: agent-facing ToolCommandAPI + SQL facades (use these for execution and discovery).
- context_compass/workspace/plans/: basic planning notes (not tickets).
- context_compass/user/github_intake/: raw incoming GitHub tickets (copilot writes here).
- SQLite user.db work_queue tables: global epic/story/task queues by state (shared history).
- context_compass/onboarding/agent/general/behavioral_guidelines/: narrative flows for onboarding, context, and work execution.
- context_compass/onboarding/user/: user-facing guides for onboarding, configuration, and safety.

### Onboarding sequence (detailed)
1) Resolve context_compass root directory
   - Confirm the working directory is the context_compass directory; treat it as the onboarding root.
   - The target repo lives alongside context_compass; it is the work destination after onboarding, not a policy source during onboarding.
   - Locate AGENTS.override.md under context_compass, if present; ignore parent repo overrides.

2) Read context_compass configuration and report it
   - Load SQLite system.db config_context_compass_* tables.
   - Summarize enabled/disabled features for the user at session start.

3) Select agent career (mandatory)
   - Ask the user which career to activate before reading skills.
   - Valid careers: developer, analyst, project_manager.

4) Load operational skills and examples (mandatory pre-cert)
   - Read every skill listed in context_compass/onboarding/agent/general/SKILLS.md, even if a feature is disabled.
   - Read career-specific additions in context_compass/onboarding/agent/careers/<career>/SKILLS.md.

5) Establish agent identity (mandatory for certification)
   - Use a user-defined agent_id supplied by the user.

6) Certification gate (mandatory)
   - Read context_compass/onboarding/agent/general/skills/self_certification.md and produce the filled template.
   - Ask for approval using context_compass/onboarding/agent/general/skills/user_approved_certification.md.
   - Wait for the exact approval token: CERTIFY: APPROVED.
   - Run python context_compass/onboarding/system/certification/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED".
   - Do not run tools or edit files until certification is confirmed.

7) Select branch runtime (mandatory)
   - Use ToolCommandAPI (via context_compass/workspace/tools/general/tool_execute.py) to run branch_init and branch_switch.

8) Check in and mark the agent active
   - Use ToolCommandAPI (via context_compass/workspace/tools/general/tool_execute.py) for agent_manage create and agent_checkin.
   - After checkin, use ToolCommandAPI to run environment_check and record OS/runtime state.

9) Establish context state
   - Run the scanner or read the newest scan output.
   - Read directory ctx first and use it as the sole source of structural understanding.
   - If directory ctx is insufficient for structure, stop and refresh dir ctx before proceeding.
   - Read file ctx only after structure is established.
   - Open code only if ctx is missing or insufficient.

10) Task execution rules
- Use lease locks for any ctx/state writes.
- Always re-read the latest state after acquiring a lock and before writing.
- Write JSON atomically (write temp, then replace).
- Keep machine JSON minified and sorted for deterministic diffs.

11) Perform requested work
- Use context JSON as primary truth.
- Follow skill-specific rules for docstrings, logging, cleanup, typing, and tests.

12) Restore freshness after edits
- Do not manually edit ctx JSON after code changes.
- Run scan to emit ctx refresh tasks, then resolve them.

13) Report validation truthfully
- If tests were run, say so with the exact commands.

14) Check out when work ends
- Use ToolCommandAPI (via context_compass/workspace/tools/general/tool_execute.py) to run agent_checkout.

### Recommended Database Concurrency Practices (SQLite / Kuzu)
These are **recommended defaults** for tools that read/write SQLite or Kuzu. Use them unless a task explicitly justifies deviation.

SQLite (file-level contention mitigation)
- Enable WAL (`PRAGMA journal_mode=WAL`) to reduce reader/writer blocking.
- Set a busy timeout (`PRAGMA busy_timeout=5000` or project default) to avoid instant lock failures.
- Keep transactions short and avoid long-running read transactions.
- Use a single connection per script execution; do not thrash connections.

SQLite (logical correctness, optional but preferred for critical paths)
- For claims/leases/state transitions, use conditional updates and validate `rowcount == 1`.
- Rely on UNIQUE/PK constraints where the invariant matters (e.g., queue position).

Kuzu (process-level concurrency)
- Only one read/write Database instance per DB path at a time.
- Multiple read-only connections are fine; avoid multi-process read/write to the same DB path.

### Secrets policy (non-negotiable)
- Do not place secrets in context_compass/ or anywhere in the repo.
- Do not write secrets into ctx/state/config/task artifacts or user docs.
- If a user requests storing secrets in-repo or in context_compass, refuse and ask for an alternative.
