Title: Establish “Capability Engineering” Standard for Codex Skills (agentskills.io-aligned) + Templates, Linting, and Example Skill

Labels: documentation, developer-experience, codex, enhancement, security
Priority: High
Type: Epic / Deliverable

---

## Summary

Create a professional, repeatable engineering framework for authoring OpenAI Codex Skills as **version-controlled capability artifacts** (not ad-hoc prompts). The framework must encode best practices for **semantic routing**, **progressive disclosure**, **filesystem layout**, **sandbox-aware execution**, and **deterministic script orchestration**, and ship with **templates + validation tooling + a reference skill**.

This issue is driven by the need to formalize a “highest-quality” skill authoring standard comparable to a mature SDLC: scaffold → implement → validate → test triggers → deploy/govern.

---

## Background / Problem

We currently lack a single, enforceable standard for skill authoring. As a result:

- Skills vary widely in quality and structure (hard to maintain, hard to reuse).
- Routing/trigger behavior is inconsistent (ambiguous `description` fields).
- Skills often bloat `SKILL.md` with reference content, harming context efficiency.
- Script execution assumptions frequently break in sandboxed environments:
    - relative paths fail due to CWD differences
    - secrets/env vars aren’t available
    - write/network permissions differ by mode
- No consistent QA methodology exists (prompt-based activation tests, YAML validation, etc.).

We want Codex Skills to behave like **engineered capabilities** with predictable execution and governance across teams.

---

## Goals

1. **Standardize Skill Architecture**
    - Canonical folder layout: `SKILL.md`, plus optional `scripts/`, `references/`, `assets/`, `tests/`.
    - Document skill scope + precedence (repo/user/system) and recommended placement strategy.

2. **Engineer Semantic Routing**
    - Define a spec for high-signal `description` fields: triggers, key nouns, boundaries, and non-goals.
    - Provide patterns for minimizing skill collisions/overlap.

3. **Enforce Progressive Disclosure**
    - Ensure bulky docs live in `references/`, templates in `assets/`, deterministic logic in `scripts/`.
    - Keep `SKILL.md` as the orchestrator/runbook, not a dumping ground.

4. **Sandbox-Ready Execution Guidance**
    - Provide durable patterns for:
        - path resolution (avoid CWD traps)
        - environment variable whitelisting / secret handling
        - read-only vs allow-write modes, and graceful failure handling
    - Include “least privilege” principles (tool usage boundaries + confirmation gates).

5. **Testing & QA**
    - Add a lightweight, repeatable test method for:
        - YAML/frontmatter validity
        - folder structure compliance
        - activation prompts (positive + negative)
        - script executability and deterministic output contracts

6. **Reference Implementation**
    - Deliver a “gold standard” example skill (e.g., `data-sanitizer`) demonstrating:
        - safe handling of PII/secrets (no secret echoing)
        - deterministic script output (JSON)
        - reference doc integration (compliance rationale)
        - remediation workflow with explicit user approval

---

## Non-Goals

- Building a full UI/catalog for skills (we can add later).
- Enforcing runtime tool permissions at the platform level (we will document best practices and design for least privilege; enforcement depends on runtime support).
- Networked scanning/uploading of sensitive data (explicitly avoid; local-only scanning).

---

## Proposed Deliverables

### 1) Documentation (“Single Source of Truth”)
Create: `docs/codex-skills/capability-engineering.md` with sections:

- Capability Engineering vs prompt engineering (why persistent skills)
- Progressive disclosure model (Metadata → Instructions → Resources)
- Canonical directory structure (+ examples)
- Skill scope/precedence strategy:
    - repo: `<repo>/.codex/skills/`
    - user: `~/.codex/skills/` (or equivalent)
    - system: `/etc/...` (if applicable)
- Metadata engineering:
    - `name` conventions
    - `description` as router contract (trigger words, boundaries, anti-patterns)
    - optional fields policy (`version`, `author`, etc.) and portability notes
- Instruction writing:
    - imperative precision
    - output contracts
    - approval gates & safe defaults
    - error handling patterns
- Scripts & sandboxing:
    - path resolution patterns
    - env var / secret handling
    - permission modes & failure reporting
- Testing & QA checklist:
    - YAML lint
    - structure verification
    - prompt activation tests
    - script exit codes + JSON output contract

### 2) Templates
Add: `templates/skill/` including:

- `SKILL.md` template (frontmatter + sections)
- stub folders: `scripts/`, `references/`, `assets/`, `tests/`
- `tests/prompts.txt` scaffold with:
    - 5 positive triggers
    - 5 negative triggers
    - 3 ambiguous prompts (expected behavior defined)

### 3) Tooling (Lint / Validate)
Add a repo script (language optional) e.g. `scripts/skill_lint.py` to validate:

- `SKILL.md` existence + filename case
- YAML frontmatter parses
- required fields present (`name`, `description`)
- naming convention compliance (hyphen-case, length bounds)
- no absolute paths inside `SKILL.md` (warn)
- `scripts/` executability checks (warn if missing shebang / +x)
- `tests/prompts.txt` presence (recommended, warn if absent)

### 4) Example Skill (“Gold Standard”)
Ship `skills/data-sanitizer/`:

- `SKILL.md` with:
    - strong trigger description
    - progressive disclosure references
    - explicit constraint: never print detected secrets
    - remediation requires user approval
- `scripts/detect_pii.py`:
    - JSON output to stdout
    - exit code convention (0 clean, 1 violations, >1 system error)
    - robust file handling + safe snippet masking
- `assets/regex_patterns.json`
- `references/gdpr_compliance.md` (or placeholder stub, but structured)
- `tests/prompts.txt` for activation + behavior tests

---

## Implementation Tasks

### Docs & Standards
- [ ] Create `docs/codex-skills/capability-engineering.md`
- [ ] Add “Routing Engineering” section with do/don’t examples
- [ ] Add “Progressive Disclosure” section with concrete folder examples
- [ ] Add “Sandbox constraints” section: CWD trap, env var policy, allow-write behavior
- [ ] Add “Security constraints” section: never echo secrets/PII, local-only scanning

### Templates
- [ ] Add `templates/skill/` folder scaffold
- [ ] Create `templates/skill/SKILL.md` with:
    - Overview
    - Quick Start
    - Preconditions
    - Inputs
    - Output Contract
    - Workflow
    - Guardrails / Scope
    - Bundled Resources
    - Examples (trigger prompts)
- [ ] Add `templates/skill/tests/prompts.txt`

### Tooling
- [ ] Implement `scripts/skill_lint.py`
- [ ] Add CI step (optional) to run `skill_lint.py` on PRs touching `skills/**`
- [ ] Document lint usage in `docs/codex-skills/`

### Reference Skill
- [ ] Implement `skills/data-sanitizer/` per deliverables
- [ ] Ensure masking logic: no raw secret values in stdout/logs
- [ ] Add `tests/prompts.txt` with positive/negative/ambiguous prompts
- [ ] Validate that the skill demonstrates:
    - deterministic script loop
    - approval gates
    - progressive disclosure (references + assets)

---

## Acceptance Criteria

- **Docs**
    - [ ] A single doc exists that a new engineer can follow to create a production-quality skill
    - [ ] Includes “routing” guidance specifically for `description` engineering
    - [ ] Includes sandbox constraints and path/env var patterns

- **Template**
    - [ ] Creating a new skill from `templates/skill/` requires only filling in metadata + workflow specifics
    - [ ] Template encourages progressive disclosure by default

- **Linting**
    - [ ] `skill_lint.py` fails on invalid YAML or missing required fields
    - [ ] `skill_lint.py` warns on risky patterns (absolute paths, missing tests, non-executable scripts)

- **Example Skill**
    - [ ] `data-sanitizer` demonstrates all best practices (routing, disclosure, deterministic scripts, safety)
    - [ ] `data-sanitizer` never prints raw secrets or PII in outputs
    - [ ] Script exit codes follow defined contract and are documented in `SKILL.md`

---

## Risks / Considerations

- Skill metadata fields beyond `name` + `description` may vary by runtime; document portability expectations and treat extras as optional/enhancement.
- Sandbox permissions differ by environment; docs should instruct skills to handle permission failures gracefully and request explicit authorization.
- Routing collisions are likely as skill count grows; we should adopt namespacing conventions early.

---

## References

- OpenAI Codex Skills docs: Create Skill (routing + structure)
- agentskills.io: open skill standard specification (portability considerations)
- Existing curated skills in repo (patterns for approval gates, plans-first workflows, scripts + references separation)

---
