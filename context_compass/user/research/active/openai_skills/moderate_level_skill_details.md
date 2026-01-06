# [TICKET] Implement **OpenAI Skills-style** Skill Format + Loader Interface (from `openai/skills`)

## Why this ticket exists

We want our agents to ingest and execute “skills” the same way the `openai/skills` repo structures them.

This ticket documents:

* **The on-disk format** used by the repo (folders, files, naming rules)
* **The SKILL.md spec** (frontmatter schema + body conventions)
* **Bundled resources** patterns (`scripts/`, `reference/`, `examples/`, `evaluations/`)
* **What our agent interface must support** to be compatible (discovery, progressive loading, invocation, tool/connector awareness)

Source analyzed: `skills-main.zip` (repo snapshot) → `skills/` tree.

---

## Repository layout (what’s actually in there)

Top-level:

* `README.md` (explains the concept + installation)
* `skills/`
* `skills/.system/` (system skills; “always available / auto-installed” in Codex)
* `skills/.curated/` (curated skills)
* `skills/.experimental/` (experimental skills)



### Skills present in this snapshot (10 total)

| Category | Skill dir / name | metadata.short-description | Bundled resources |
| --- | --- | --- | --- |
| .system | skill-creator | Create or update a skill | scripts/ (init/validate/package) |
| .system | skill-installer | Install curated skills… | scripts/ (list/install helpers) |
| .experimental | create-plan | Create a plan | none |
| .experimental | linear | Manage Linear issues… | none |
| .curated | gh-address-comments | Address comments in PR review | scripts/ |
| .curated | gh-fix-ci | Fix failing Github CI actions | scripts/ |
| .curated | notion-knowledge-capture | Capture conversations into Notion pages | reference/, examples/, evaluations/ |
| .curated | notion-meeting-intelligence | Prep meetings with Notion context… | reference/, examples/, evaluations/ |
| .curated | notion-research-documentation | Research Notion content and produce reports | reference/, examples/, evaluations/ |
| .curated | notion-spec-to-implementation | Turn specs into plans/tasks/progress | reference/, examples/, evaluations/ |

---

## Skill folder anatomy (observed conventions)

A skill is a **single directory**.

**Always present (required by convention):**

* `SKILL.md` — the actual skill spec (YAML frontmatter + Markdown body)
* `LICENSE.txt` — per-skill licensing (varies by skill)

**Optional (common):**

* `scripts/` — helper scripts (usually Python) used by the agent (or by the user) to fetch/inspect state
* `reference/` — longer “aux docs” referenced from SKILL.md (templates, schemas, how-tos)
* `examples/` — example outputs or walkthroughs
* `evaluations/` — test scenarios (JSON) + a README describing what’s being tested

### Naming rules (as used in the repo)

* Skill directory name == YAML frontmatter `name` (1:1 match).
* Skill `name` is **hyphen-case** (lowercase letters/digits/hyphens).
* Category folders are **dot-prefixed** and treated as grouping only.

---

## SKILL.md format (the real spec)

Every skill file begins with **YAML frontmatter** followed by **Markdown**.

### 1) YAML frontmatter

Observed fields in all skills here:

```yaml
---
name: <hyphen-case-skill-id>
description: <human description + trigger guidance>
metadata:
  short-description: <1-line list label>
---

```

Key points:

* `name` is the unique identifier. In Codex-land, that’s the thing you invoke like `$skill-name`.
* `description` isn’t just “what it does” — it often includes **when to use it** and **constraints**.
* `metadata.short-description` is the “catalog display label”.

#### Validation rules (from `skill-creator/scripts/quick_validate.py`)

Frontmatter is validated with these constraints:

* Must start with `---` and include a closing `---`
* Frontmatter must parse into a YAML dictionary
* Allowed keys (validator allows more than this repo uses):
* `name` *(required)*
* `description` *(required)*
* `metadata` *(optional)*
* `license` *(optional, allowed by validator but unused here — repo uses `LICENSE.txt` instead)*
* `allowed-tools` *(optional, allowed by validator but unused here)*


* `name` constraints:
* regex: `^[a-z0-9-]+$`
* cannot start/end with `-`, cannot contain `--`
* max length: **64** chars


* `description` constraints:
* must be a string
* cannot contain `<` or `>`
* max length: **1024** chars



**Actionable takeaway:** our loader should enforce/validate these, or at least warn.

### 2) Markdown body

There is *no* rigid schema. But the repo is consistent in *style and intent*:

* First line is an H1 title: `# <Human Title>`
* Then a predictable set of sections depending on the skill type.

Common section patterns:

* **Overview / Goal**: what the skill is for
* **Prerequisites**: required tools / auth / MCP connectors
* **Quick start**: numbered “do this now” steps
* **Workflow**: step-by-step procedure with headings (often numbered)
* **Troubleshooting**: what to do when auth/tools fail
* **References and examples**: pointers to bundled docs

One big theme: the body is written as **an operational playbook** for an agent.

---

## Skill body structure patterns (as taught by `skill-creator`)

The `skill-creator` skill explicitly teaches 3 body archetypes:

### Pattern A — Workflow-Based (sequential)

Used when there’s a clear series of steps.
Examples in this repo:

* `gh-address-comments`
* `gh-fix-ci`
* Notion skills (quick start → step ladder)

Typical layout:

* `## Quick start`
* `## Workflow`
* `### 1) ...`
* `### 2) ...`
* ...



### Pattern B — Task-Based (menu of operations)

Used when the skill is more like a toolbox.
Example in this repo:

* `linear` (operations + common workflows)

Typical layout:

* `## Overview`
* `## Operations`
* “Create issue”
* “Update issue”
* “Search/list”
* …



### Pattern C — Reference / Guidelines

Used for “standards” skills.
Example in this repo:

* `skill-creator` itself (design principles + process)

Typical layout:

* `## Core principles`
* `## Do/Don’t`
* `## Templates`
* `## Process`

---

## Progressive disclosure (critical for our interface)

This repo (and Codex) assumes a **3-level loading model**:

1. **Metadata (name + description)** — always available (small)
2. **SKILL.md body** — loaded when skill triggers
3. **Bundled resources** — pulled only when needed (could be “unlimited” because scripts can run without being stuffed into context)

Operational meaning for *our* agent runtime:

* We should NOT auto-load every skill’s full body into context.
* We should load:
* *All skill metadata* at startup (for routing/search)
* *Only the selected skill body* on invocation
* *Only the referenced resources* if/when requested by the body



---

## Bundled resources: what they look like and how they’re referenced

### `scripts/`

* Python scripts (CLI-style) that produce structured output or inspect remote systems.
* Skills explicitly instruct when/how to run them.

Repo examples:

* `gh-address-comments/scripts/fetch_comments.py`
* `gh-fix-ci/scripts/inspect_pr_checks.py`
* `skill-installer/scripts/install-skill-from-github.py`
* `skill-creator/scripts/init_skill.py`, `package_skill.py`, `quick_validate.py`

**Interface implications:**

* We need a safe, consistent “run script” capability:
* choose interpreter (python)
* choose working dir
* capture stdout/stderr
* handle auth/network permission escalation if our sandbox has that concept



### `reference/`

* Markdown reference files: schemas, templates, best-practice docs.
* Skills point at them explicitly in “References and examples”.

Repo examples (Notion skills):

* database schemas, templates, citation rules, progress tracking templates

**Interface implications:**

* Provide a resource resolver: “open the file the skill references”
* Load reference docs lazily (don’t dump them unless needed)

### `examples/`

* Markdown examples that show end-to-end outputs.

**Interface implications:**

* Use for few-shot prompting (“here is an example output”) without bloating base context.

### `evaluations/`

Contains:

* `evaluations/README.md`
* one or more JSON files with scenario specs

Observed JSON schema (consistent across Notion skills):

```json
{
  "name": "<scenario title>",
  "skills": ["<skill-alias-or-name>"],
  "query": "<user prompt>",
  "context": "<optional extra context>",
  "expected_behavior": ["<bullets>", "..."],
  "success_criteria": ["<bullets>", "..."]
}

```

**Important gotcha:** In this snapshot, the `skills` list sometimes uses a short alias (e.g. `knowledge-capture`) rather than the full directory skill name (`notion-knowledge-capture`). So our evaluation harness should allow an alias map.

---

## “Tooling assumptions” embedded in skill text (we must support or translate)

Several skills assume integration points:

### External CLIs (GitHub)

* `gh-address-comments` / `gh-fix-ci` assume the GitHub CLI `gh`.
* They also explicitly say “ensure gh is authenticated” and instruct retry flows.
* They sometimes mention running with “elevated network access” (Codex sandbox concept).

**Our interface requirement:**

* We need a way for skills to request “networked command execution”, or we need to rewrite those instructions into our own permission model.

### MCP connectors (Notion, Linear)

* Notion skills call tools like `Notion:notion-search`, `Notion:notion-fetch`, `Notion:notion-create-pages`, `Notion:notion-update-page`.
* Linear skill assumes “Linear MCP server must be connected via OAuth”.

**Our interface requirement:**

* Map these tool names to our runtime’s connector APIs.
* Or: implement a generic “tool registry” where connector tools register as `Vendor:operation`.
* Skills need a way to detect “connector not configured” and trigger a setup flow.

---

## What we need to implement in *our* repo (the interface)

### 1) Skill discovery + indexing

**Input:** a list of root directories (e.g. `skills/`)

**Output:** an in-memory index like:

* `skill_name → SkillManifest`
* `category → list[SkillManifest]`
* optional: keyword search over `name`, `description`, `short-description`

Minimal manifest fields:

* `name` (slug)
* `description`
* `short_description` (optional)
* `category` (folder)
* `path` (skill dir)
* `license_path` (LICENSE.txt)
* `skill_md_path` (SKILL.md)
* `has_scripts`, `has_reference`, `has_examples`, `has_evaluations`

### 2) Strict parsing + validation

At load time, parse:

* YAML frontmatter
* (optional) enforce validation rules listed above

**Failure policy recommendation:**

* For our repo: fail-fast (bad skills should not silently load)
* For third-party installed skills: warn + quarantine

### 3) Progressive loading (don’t bloat context)

Implement “load levels”:

* **Level 0:** metadata only
* **Level 1:** SKILL.md body
* **Level 2:** referenced resources (reference/examples)

### 4) Skill invocation protocol

Support BOTH:

* Explicit invocation: `$skill-name ...`
* Implicit routing: by classifier / rules using metadata + user prompt

When invoked, produce an “execution frame”:

* active skill manifest
* injected SKILL.md body
* resolved resources as needed
* tool permissions requested (if applicable)

### 5) Resource resolution

Given a skill directory:

* enumerate resource files
* open/read specific resource by relative path
* run scripts with controlled execution

### 6) Evaluation harness (optional but recommended)

Load `evaluations/*.json` and run:

* prompt = `query` (+ `context`)
* expected behavior + success criteria = rubric

Add alias mapping support for `skills` field.

---

## Edge cases & inconsistencies we must be robust to

1. **`reference/` vs `references/**`
* This repo uses `reference/` (singular).
* The `skill-creator` docs/scripts talk about `references/` (plural).
* Our loader should accept both.


2. **Optional frontmatter keys not used here**
* Validator allows `allowed-tools` and `license`.
* Repo uses `LICENSE.txt` instead.
* We should support the optional keys anyway (future-proof + third-party skills).


3. **Evaluation skill IDs**
* Evaluation JSON sometimes uses alias names not equal to folder `name`.
* Support alias mapping.


4. **Scripts requiring external auth / network**
* Some scripts inherently need tokens/network.
* Our runtime needs a consistent strategy for “this action needs permission”.



---

## Acceptance criteria

* [ ] Loader scans `skills/**/SKILL.md` and builds index
* [ ] YAML frontmatter parsed and validated (name/description rules)
* [ ] Skill directory name enforced to match `frontmatter.name`
* [ ] Catalog UI/CLI can list skills (category, name, short-description)
* [ ] Invocation loads only the selected skill body (progressive disclosure)
* [ ] Bundled resources can be opened by relative path
* [ ] Scripts can be executed in a controlled way (stdout/stderr captured)
* [ ] Evaluations JSON schema supported + alias mapping (optional)

---

## Implementation checklist (suggested work breakdown)

### A) Core parsing/index

* [ ] Implement `SkillManifest` + `SkillPackage`
* [ ] Implement `parse_skill_md()` (frontmatter + body)
* [ ] Implement validation rules (mirroring `quick_validate.py`)
* [ ] Implement directory scan + index build

### B) Invocation + context plumbing

* [ ] Explicit invoke (`$name`) parsing
* [ ] Router search over metadata (fallback for implicit)
* [ ] Context injector: attach SKILL.md body to agent prompt
* [ ] Lazy resource loading helpers

### C) Resource helpers

* [ ] `open_resource(skill, relpath)`
* [ ] `list_resources(skill)`
* [ ] `run_script(skill, script_relpath, args, permissions)`

### D) Eval harness (optional)

* [ ] Load `evaluations/*.json`
* [ ] Run scenario harness, record pass/fail against rubric

---

## Appendix: Concrete examples from this repo (what to copy)

### Frontmatter (universal)

* `name` == folder name
* `description` often includes “Use when…” trigger language
* `metadata.short-description` used for listing

### Body example types

* `create-plan`: contains an explicit output template (“Plan” section) and rules like “read-only mode”
* Notion skills: consistent “Quick start → Steps → References/examples” and explicit tool names (`Notion:...`)
* GitHub skills: explicit guidance for `gh` auth, scripts to fetch context (comments/checks), then ask user for selection/approval
* `skill-installer`: documents install behavior + scripts that implement it
* `skill-creator`: documents skill design principles + scripts to initialize/validate/package skills