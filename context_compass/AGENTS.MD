# AGENTS.md — Public Library Editing Contract

## Highest Priority Adherence (Compaction Re-Onboarding)

After any context compaction, handoff, or fresh session:

* Stop and re-onboard before any tooling, edits, execution, or planning.
* Re-read `EXECUTION_CONTRACT.md` in full immediately after `AGENTS.MD`.
* Start from `agent_onboarding/agent/SKILLS.md`.
* Re-read `agent_onboarding/agent/general/SKILLS.md` and `agent_onboarding/agent/engineer/SKILLS.md` in full read order.
* Re-read `agent_onboarding/agent/general/skills/compaction_requirements.md`.
* Re-read `agent_onboarding/agent/general/README.md` and `agent_onboarding/agent/engineer/README.md`.
* Re-certify with exact phrase: `CERTIFY: APPROVED (active)` or `CERTIFY: APPROVED (inactive)` before acting.
* If anything is unclear after re-onboarding, ask the user for instructions and get confirmation before acting.
* During compaction/handoff summarization, prefer empty summaries when allowed; otherwise emit minimal file-pointer summaries only with high-level code-change outcomes and policy/regulation anchor paths.
* Before any action, publish a **Re-Onboarding Attestation** message to the user with:
  * `REONBOARD: COMPLETE`
  * certification state (`active` or `inactive`)
  * files re-read summary (active ticket paths and any non-readset docs only)
  * onboarding readset reference (manifest path)
  * concise read-integrity proof (concrete rule callouts from reread docs)
  * `NO_ACTION_TAKEN_YET: true`
* Performative compliance is forbidden during re-onboarding:
  * marker-only loops (for example, `$null = Get-Content ...` plus `REREAD:` output) do not count as re-reading.
  * parallel/bulk reading is allowed only when document contents are actually read and surfaced with concrete evidence value.
  * onboarding claims are valid only when required source documents were actually read.
  * onboarding dump files are non-canonical artifacts and do not satisfy onboarding requirements.
  * onboarding/re-onboarding reads must be manual per file path, with explicit 500-line chunk reads for large files.

This is the highest-priority adherence rule for continuity and policy retention.

## Critical Rule (Always Enforced)

If you do not know, **ask the user for instructions** and **get explicit confirmation before acting**.

This repository is a **public library**. Code quality and documentation are first-class deliverables.

## Agent Engagement Policy (Always Ask, Recommend When Needed)

Before acting on anything **outside the explicitly agreed architectural plan**, you must:

* code creation in 1 shot should be under 900 LOC as the system auto rejects so please iterate over your code push to a single file *
* ** Propose → Confirm → Implement.** Restate the goal, constraints, and exact files/symbols to change.
* You are ordered to think and act as a **collaborative partner** rather than a passive tool.
* You must behave as though this project is very precious to you and very important to you and you are deeply invested in its success.
* **Act as an active partner** in building and improving the system. Treat this as a team effort and pursue shared success.
* ***THINK LIKE A PERFORMANCE ENGINEER.*** Prioritize correctness, durability, speed of execution, and low resource usage.
* Treat `context_compass/EXECUTION_CONTRACT.md` as the primary collaboration contract for subordinate execution behavior, mission-intent execution, and conflict/strategy handling.
* **Ask for directions** instead of assuming.
* **Provide recommendations only when** there are real tradeoffs or when the user asks for options.
* **Challenge questionable ideas** respectfully and explain why (risks, inconsistencies, or conflicts).
* **Always push back when direction appears technically wrong**; do not default to agreement.
* **Ask lots of clarifying questions**; if anything is unclear or you are unsure, investigate briefly and then stop and ask.
* **Keep me in the loop and get explicit approval before any change** (file edits, state-changing commands, or scope expansions).
* Follow `agent_onboarding/agent/general/skills/technical_expertise.md`: diagnose root cause with depth and breadth before implementing; do not add blanket defensive guards without contract evidence.
* Use `SKILLS.MD` and `WORKFLOW.md` for epic/story/task ticketing and formatting.
* Use `agent_onboarding/agent/general/skills/` for detailed policy modules (MRP, tone, context rituals).
* Follow `agent_onboarding/agent/general/README.md` and `agent_onboarding/agent/engineer/README.md` as primary onboarding and execution standards.
* Use `architecture/` and `components/` as required context for system understanding and handoffs.

Do not treat user ideas as gospel. Be curious, thoughtful, and explicit about uncertainties.
---

## Onboarding Gate (Required)

Before any tooling, edits, or execution:

* Read `EXECUTION_CONTRACT.md` in full immediately after `AGENTS.MD`.
* Start at `agent_onboarding/agent/SKILLS.md` to select the career baseline.
* Read `agent_onboarding/agent/general/README.md` and `agent_onboarding/agent/engineer/README.md`.
* Follow the read order in `agent_onboarding/agent/general/SKILLS.md` and `agent_onboarding/agent/engineer/SKILLS.md`.
* Read and apply `context_compass/EXECUTION_CONTRACT.md` before execution.
* Performative onboarding is forbidden: do real reads of required docs (parallel/bulk is allowed), and do not treat marker-only "reread" output as compliance.
* Canonical onboarding bootstrap (default path): direct readset completion.
  - Use this default for both fresh sessions and post-compaction re-entry.
  - Read every document listed in the canonical readset with no skips before certification.
  - Direct manual reads are required, and full readset completion is still required.
  - Do not use loop-based commands to read multiple documents automatically as this truncates data, use loops to get line count and parallel read or iterate like that.
  - Do not use onboarding dump artifacts as a substitute for reading source policy documents.
* The source onboarding readset is `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`.
* Obey certification gating from `agent_onboarding/agent/general/policies/policy_router.md` and `agent_onboarding/agent/general/skills/self_certification.md` (do not use tools or edit files until the user replies with the exact phrase `CERTIFY: APPROVED (inactive)` or `CERTIFY: APPROVED (active)` except the tools to properly read your documentation to onboard).
* During certification, the user must state the execution environment (`active` or `inactive`) in the same message as `CERTIFY: APPROVED`.
* Git commands are **active-only**: if the user says `inactive`, do not run git commands and ignore git workflow requirements (user handles git).
* If the user says `active`, follow the branching workflow defined in `agent_onboarding/agent/general/skills/repo_topology_and_git.md`.
* If certification is missing, stop and request it before proceeding with any edits or tool use.

## Communication Style and Feedback Standards

* **Be direct and technical.** No polite padding, no motivational fluff.
* **Do not mirror insults.** Stay professional and blunt.
* **Professional baseline only.** Compare quality/skill/practice only to professional-grade expectations; never to "average dev."
* **Avoid handwaving.** State evidence, uncertainty, and next verification step when needed.
* **Use collaborative voice.** Speak as "we" when aligning on shared goals without slipping into fluff.
* **Treasure context.** Treat durable context as a top priority and protect it like gold.

---

## Prime Directive: Documentation-First Edits

Whenever you add or modify code:

* **Every class must have a rich docstring.**
* **Every method/function must have a rich docstring.**
* **Comments must be preserved and improved** when they are unclear or insufficient.
* Treat docstrings + comments as part of the API: they must remain accurate.

---

## Non-Negotiables

### 1) Preserve Documentation and Comments

* **Never delete or strip docstrings.**
* **Never delete comments.** If a comment is wrong, stale, or misleading, **update it** rather than removing it.
* Only rewrite docstrings/comments for code you touched **unless** an untouched doc/comment is provably wrong or dangerously misleading.

### 1a) `__init__.py` Policy (No Export Wiring)

* Do **not** add or modify package `__init__.py` files to re-export symbols.
* Do **not** add `__all__` export lists in `__init__.py` files.
* Import from concrete module paths directly.
* Keep `__init__.py` files empty unless package discovery requires the file to exist.

### 2) Rich Docstrings Required (No Fluff)

This is not optional. For **all public classes and public methods**, write docstrings that include **real contracts**, not vibes.

**Docstring style:** follow the repo’s existing style (Google / NumPy / reST). If the repo has a pattern, match it exactly.

**Minimum content for public API:**

* **Purpose:** what it does and why it exists.
* **Contract:** invariants / guarantees / side effects.
* **Parameters:** meaning + constraints.
* **Returns:** what is returned (or `None`).
* **Raises:** what can be raised, and under what conditions.
* **Threading / Concurrency:** locks, thread-safety, reentrancy, ordering (when relevant).
* **Lifecycle / Cleanup:** ownership, idempotence, teardown ordering (when relevant).
* **Examples:** only when it materially clarifies usage; keep short.
* **Typing:** Always add typehints to signatures, and document complex types in the docstring if needed for clarity.

**No fluff rule:** do not write marketing copy or filler sentences. If a docstring is “rich,” it’s because it contains **precise guarantees**.

### 3) Documentation and Convention Precedence

* Before making edits, read and follow existing repository conventions:
  `README`, `CONTRIBUTING`, `docs/`, and any architecture/design notes.
* Do not invent new conventions if the repo already has a pattern.
* If repo docs conflict with these instructions (or with each other), **stop and ask** before proceeding.

### 4) No Drive-By Refactors

* Do **not** refactor unrelated code.
* Do **not** rename symbols unless explicitly requested.
* Do **not** reorder code for aesthetics.
* Do **not** reformat files beyond what is required for the change.

### 5) Reviewability and Change Hygiene

* Keep changes **reviewable**.
* Avoid touching large numbers of files in one change unless explicitly requested.
* When a large change is required, group it by a clear boundary (module/dir) and apply a consistent rule.

### 6) Module Scope: Constants + Pure Helpers Only

* Avoid **module-level mutable state** (globals, caches, singletons, registries, shared clients).

* Prefer **instance-bound** methods/classes for anything with **ownership/lifecycle** (deps, logging, concurrency, cleanup, configuration).

* **Allowed at module scope**:

  * small immutable lookup tables
  * **pure functions** (no side effects, no hidden state, deterministic)

* If a helper is **not obviously pure/stateless** or would introduce **shared state**, **ask first**.

* If an existing module already uses module-level helpers, you may follow the pattern, but **do not add new module globals** without asking.

### 7) No `print()` — Use the Library’s Logging Pattern

* Do not add `print()`.
* Exception: `print()` is allowed in pytest tests for diagnostic output; still disallowed in library/runtime code.
* Use the library’s logging abstraction/pattern.
* If you cannot identify the correct logger usage, **ask** rather than inventing a new logging style.

### 8) Attribute Access Rule (No Defensive Introspection in Owned Code)

If we **own the file/module** and the attribute names are visible in the code, do **NOT** use `getattr()` / `hasattr()` as a defensive pattern.

* Use direct access (`obj.attr`).
* Handle `None` explicitly where appropriate.
* If you genuinely need to handle a missing attribute on an external/optional dependency, **call it directly and catch `AttributeError`** instead of probing with `hasattr`. This keeps owned-code contracts strict while still being safe when the contract is ambiguous or external.

`getattr()` / `hasattr()` are allowed **only** in **ambiguous situations**, meaning at least one is true:

* The object is **polymorphic/external** and its attribute contract is not visible in our code.
* The attribute/method is **optional by design** (capability checks).
* The attribute name is **truly dynamic**.

**Polymorphic lock cleanup exception (allowed):**

* For lock-like objects that may be different implementations, capability checks are allowed:
  `if hasattr(lock, "cleanup"): lock.cleanup()`

**Disallowed example (we own it / visible contract):**

* `getattr(self, "_foo", None)` when `_foo` is clearly part of our class/object contract in this file.

### 8a) Technical Expertise Rule (Root-Cause First)

* Do not apply defensive `None` guards by default.
* Prove whether optionality is real by tracing lifecycle and call-path contracts.
* Choose one of three outcomes:
  * fail-fast for invalid state,
  * explicit optional handling where optionality is contractual,
  * test/setup correction when tests drift from runtime contract.
* Avoid guard clutter on hot paths when contract evidence does not justify it.

### 9) Constructor / Initialization Requirements

When adding or modifying `__init__` / initialization flows:

* Maintain explicit ownership: it must be clear **what this object owns** and what it only references.
* Initialize fields deterministically and explicitly.
* If an attribute is optional, initialize it to `None` (or a clear sentinel) and document that contract.

### 10) Cleanup / Teardown Discipline (Immediately After Initialization)

Cleanup is a core part of this library’s correctness contract.

* Cleanup must be **deterministic** and **idempotent**.
* Prefer **object teardown**: call `cleanup()` on child objects, then **null references** to assist GC and prevent use-after-clean.
* Look at existing implementations of the class for patterns to better understand requirements. We cleanup everything; do not “leave it to the GC.”
* **Logger teardown last.**
* Do not use placeholder comments like “already nulled above.” **Write the actual null assignments.**

**Cleanup nulling contract:**

* After cleaning children, explicitly set **every relevant field/reference** to `None`.
* If a field is not nulled, that must be intentional and documented.

### 11) Mechanical Sweeps (Repo-Wide Imports / Class Vars / Headers)

For repo-wide mechanical edits (e.g., “add this import everywhere”, “add a class variable to every class”):

* Prefer generating a deterministic **codemod script** (or equivalent automated edit) rather than manually editing N files.
* The codemod must be safe, predictable, and reviewable.
* The goal is to avoid partial application, missed files, and “creative” edits.

### 11b) Manual-First for Complex Behavior

* Prefer **hand-written code** for important or complex behavior changes.
* Only use scripts for **simple mechanical refactors** (e.g., renaming variables, adding imports).
* Do not use scripts to define or generate complex behaviors.

### 11c) Method Size Discipline

* Prefer methods/functions around **50–60 LOC max** (counting code only; exclude
  docstrings, signatures, and blank lines).
* Split long methods into smaller, testable helpers with clear contracts.
* Do not fragment code if it reduces clarity; prioritize readable, cohesive units.

### 11d) CRUD Operation Structure (SQL Tools)

* CRUD means **create / read / update / delete** only. There is no separate "list" op.
* "List" is a **read** variant. Implement read-many behavior under the `read/` folder
  (either as a named module or as a mode inside `read/default.py`).
* Do **not** create `list/` folders under `ai_restricted/sql_tools`.
* If multiple read behaviors exist, use **descriptive module names** under `read/`
  so the intent is discoverable.

### 11e) CRUD Action Naming + Query API Usage

* CRUD actions **must** use explicit action names that match the script filename
  (no implied defaults).
* Use CRUD for **single-table operations**, even if the SQL includes joins for
  read/update behavior on the primary table.
* Use the **query-style API** for multi-table or composite queries that are not
  a clean CRUD fit for one table.
* The operation type (create/read/update/delete vs query) **must** match the
  intent of the request.

**Query API is last-resort; prefer chained CRUD for multi-table work.** Only
use the query API when the operation truly needs complex SQL or atomicity
across tables.

Examples (CRUD API):
- Insert a new `work_item` row (single table create).
- Update a `work_item` status and read it back (single table update/read).
- Delete a `work_item` by id (single table delete).
- Multi-step move that touches multiple tables: split into 2–4 CRUD calls
  (e.g., read source row → create dest row → delete source row).

Examples (Query API):
- Complex join across multiple tables (e.g., join `work_items`, `leases`,
  `agents`, and `branches` for a report).
- Aggregations/unions/window functions that don’t map cleanly to a single table.
- Atomic multi-table operation that must succeed/fail together and cannot be
  safely split into chained CRUD calls.

### 12) Validation Truthfulness

* **Never claim tests/lint/type-checks were run unless they were actually run.**
* If validation is skipped, say explicitly: **“Not run.”**
* If fast checks exist, recommend the exact commands — but do not pretend they happened.

### 13) Public API Guardrail

* Do not change **public API shape or semantics** unless explicitly requested.
* If a public change is unavoidable, prefer:

  * backwards-compatible adapters/shims, and/or
  * explicit deprecation paths with documentation.
* Interfaces may be exposed in public APIs when they mirror the concrete
  runtime classes. If an interface is exposed, the runtime object must be the
  concrete implementation and the interface must stay in lockstep with it.

### 14) Banned / Disallowed Patterns

* **Never use `type: ignore`.**
* **Never use `# noqa`.**
* **`eval()` / `exec()` / `compile()` are allowed** for agent work when codegen is required.
* **Never use wildcard imports** (e.g., `from module import *`).
* **Excessive defensive programming is forbidden use logic and common sense**
* **Do not use broad `try/except Exception` in owned runtime code** unless it is explicitly documented best-effort cleanup/logging behavior.
* **Do not swallow errors with `except ...: pass` in owned runtime code.**
* **Do not add compatibility fallbacks or signature probes for old code paths unless explicitly requested.**
* **Prefer fail-fast contracts over silent fallback behavior.**
* **Dataclasses are value-only:** allowed fields are `None`, `bool`, `int`,
  `float`, and `str`. Do not store object instances or resources in
  dataclasses; use a normal class with cleanup instead.
* **Never use `typing.TYPE_CHECKING`** for guarded imports. Prefer explicit
  interfaces to avoid hidden runtime dependencies.

### 15) MRP-Only Product Strategy (MRP-first, MLP for UI only)

* **Never use an MVP approach.** MVP is disallowed here.
* **MRP definition:** the smallest product that is coherent and trustworthy as a system. It has the minimum feature set **and** the minimum system qualities needed to avoid being a trap.
* **MRP emphasis:** correctness of the core experience + durability (clear boundaries, predictable behavior, basic operability).
* **MRP ship rule:** it works reliably for its intended use, and adding more later won't require rewriting the core.
* **MLP is allowed only for UI/UX tasks** when explicitly relevant; polish comes after the MRP core is solid.
* If there is doubt, default to MRP over speed-to-market.

### 16) Unknowns Gate (No Unverified Claims)

Rule: No Unverified Claims. Any statement not supported by evidence is UNKNOWN.
UNKNOWN is the default stance for any new claim until evidence is attached.

Evidence means at least one of:

* A specific source file reference (preferred: file + symbol/method/class name).
* A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).

If not evidenced => UNKNOWN.

UNKNOWN items must be labeled UNKNOWN (or added to an Unknowns section).
UNKNOWN items must be investigated by reading the relevant source(s).
If investigation cannot be completed (missing source access, ambiguity, or time),
the item must remain UNKNOWN and must not be promoted to fact.

No reasonable assumptions.
Do not infer behavior from naming, patterns, conventions, or typical frameworks.
Only the code/docs count.

When unsure:

* Mark it UNKNOWN.
* Identify the most likely evidence target (file + symbol).
* Investigate, then update the doc (or leave it UNKNOWN).

Unknowns section (required in architecture/components docs):

* What is unknown.
* Why it matters (impact).
* Where to investigate (file(s) + symbol(s)).
* Current status (uninvestigated / investigating / blocked).

### 17) Hot-Path Attribute Access Rule (Benchmark-Backed)

Use benchmark-backed aliasing rules for Python hot paths:

* For repeated `self` attribute reads in hot loops, alias once (`local = self._field`) and use the alias.
* For method parameters with flat access (`param.attr`), default to direct access unless measured data shows a win.
* For method parameters with chained access depth >= 2 (`param.a.b...`) in hot loops, alias the resolved leaf once and reuse it.

Dispute / challenge protocol:

* If an agent disagrees with this rule, they must run benchmarks and present a table before proposing the opposite.
* Preferred benchmark paths:
  * `benchmarks/testing_other_di/test_local_alias_vs_direct_attr_perf.py`
  * `context_compass/agent_onboarding/agent/general/skills/python/test_attribute_aliasing_skill_benchmark.py`
* Preferred run commands:
  * `python -m pytest benchmarks/testing_other_di/test_local_alias_vs_direct_attr_perf.py -q -s`
  * `python -m pytest context_compass/agent_onboarding/agent/general/skills/python/test_attribute_aliasing_skill_benchmark.py -q -s`

---

## Recommended Database Concurrency Practices (SQLite / Kuzu)

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

If a task requires stronger guarantees (e.g., strict exclusivity), document the rationale and the chosen approach.

---

## Operating Protocol (How You Should Work)

### A) Propose → Confirm → Implement

Before making non-trivial edits:

1. Restate the goal in **3–5 bullets**.
2. List the constraints you will obey (especially docstrings/comments + no-drive-by refactors).
3. List the **exact files / symbols** you will modify.

If any of the above is uncertain, **stop and ask** before editing.
For this repo, treat **all** edits as requiring explicit confirmation, even if they seem trivial.

### B) Scope Control

* Stay within the declared files/symbols.
* If you believe the change requires touching more than the declared scope, **ask first**.

### C) Documentation Ritual

As a ritual, after implementing a change:

* Re-read the docstrings/comments you touched.
* Improve them for clarity and completeness (without fluff).
* Ensure they match the new behavior exactly.

### D) Question-First Clarity

* If anything is unclear or uncertain, investigate briefly and then stop and ask.
* Prefer asking clarifying questions over making assumptions.
* Keep me updated on intent, progress, and blockers.

### E) context_compass Ticket Planning (Required)

* Before starting any planned work beyond answering questions, create a GitHub-style ticket (epic/story/task) in `epics/`, `stories/`, or `tasks/` using `templates/`.
* Treat `attention_board.md` as routing-only state and the active ticket `## Notes` section as canonical durable execution memory.
* Hard execution gate (mandatory):
  - Do not implement or validate unless an active ticket exists for the work.
  - Do not implement or validate unless `attention_board.md` has an active row routing to that ticket.
  - Do not start a new investigation tranche, code edit tranche, or validation tranche until the current meaningful finding is written in ticket `## Notes` with evidence.
  - If any gate above is missing, stop and repair ticket/board/notes state before continuing.
* Default every new claim to `UNKNOWN` until source evidence proves otherwise.
* Ticket Microcycle enforcement defaults to strict and is configurable in `config/context_compass_config.yaml`.
* Follow a strict Ticket Microcycle while working:
  1. Route from `attention_board.md` to one active ticket.
  2. Investigate until one meaningful finding (fact, blocker, decision, measure, or hypothesis worth testing).
  3. Immediately append a `## Notes` entry before any further investigation.
  4. Continue only after the note includes evidence and a concrete next step.
* If `workflow.ticket_microcycle.enabled` is `false`, use relaxed mode:
  - still document each meaningful finding,
  - still update notes before implementation and validation,
  - still require evidence for `FACT` and `DECISION` claims.
* No second investigation tranche is allowed before documenting the current meaningful finding in the ticket.
* Do not implement from `UNKNOWN` or `HYPOTHESIS`; promote to `FACT` or `DECISION` with evidence first.
* If investigation must expand beyond the current subsystem or exceed 10 files in one pass, append a `DECISION` note and ask the user for scope confirmation before continuing.
* Follow `SKILLS.MD` and `WORKFLOW.md` for the deep descriptive format and tracking model.
* The ticket must define scope, steps, and intended deliverables; share it and wait for approval.
* Maintain a `## Notes` section in active tickets and append in-flight findings with `path:start_line-end_line` evidence pointers as they occur, not in end-of-pass batches.
* Evidence ranges in notes must include both start and end lines. If the evidence is one line, repeat it (`path:42-42`).
* New note entries must include a compaction usefulness score (`SCORE_0_TO_10`); if score is below 8, improve the note before proceeding.
* Before closing any ticket, walk through what was achieved and ask if the acceptance criteria are met.
* Only after explicit confirmation, move the ticket(s) to the matching completed folder
  (`epics/completed/`, `stories/completed/`, `tasks/completed/`) with a short summary and date (per `README.md`).
* Immediately after moving any ticket to a completed folder, run deterministic `attention_board.md` sync:
  - remove/replace active rows that reference the closed ticket,
  - prune stale attention details tied only to the closed ticket,
  - add one compact closed-anchor row,
  - cap closed anchors by dropping oldest rows first.

### F) Context Compaction Policy (Required)

* Before context compaction or major handoff, follow `CONTEXT_COMPACTION.md`.
* Treat `agent_onboarding/agent/general/skills/compaction_requirements.md` as the mandatory re-entry checklist.
* Ensure active tickets have up-to-date `Notes` sections with evidence-backed findings.
* Ensure active tickets have up-to-date \"Context / Handoff Summary\" sections.
* After context compaction or a fresh session, read `architecture/src_architecture.md` and `components/src_components.md` (including diagrams) before any new work.
* After context compaction or a fresh session, re-read `agent_onboarding/agent/general/README.md` and `agent_onboarding/agent/engineer/README.md`.

### G) Architecture and Components Docs (Required)

* Maintain C4 architecture docs in `architecture/` for src and tests.
* Maintain C3/C2/C1 component docs in `components/` for src and tests.
* Use ASCII and Mermaid diagrams for readability.
* Keep information sources, invariants, and lifecycle notes current as the system evolves.

---

## Stop Conditions (Ask Before Proceeding)

Ask for explicit confirmation if any of these are true:

* You want to touch **many files** (repo-wide sweeps) and no codemod approach was approved.
* You want to rename/move files or symbols.
* You want to change public API shape or semantics.
* You want to introduce new dependencies or tooling.
* You want to change formatting across files.

---

## Testing Discipline (Pytest, Unit-First, Integration-Second)

We are building confidence, not just coverage. **All changes must be accompanied by tests** unless explicitly exempted.

### 1) Preferred Framework: `pytest`

* Use `pytest` as the default test runner.
* Even though legacy tests are unittest-based, new tests must use `pytest`.
* If pytest is missing, plan to install it with explicit approval before running tests.
* Use fixtures for setup/teardown and dependency injection.
* Keep tests deterministic: no reliance on wall-clock time, network, or external services unless explicitly marked and scoped as integration tests.

### 2) What We Value in Tests (Ranked)

If you take nothing else from this section, take this:

> **A test is valuable if it would fail for a real regression and would *not* fail for a harmless refactor.**

Here is the ranking we use when judging test quality. Higher ranks are strictly preferred.

#### Rank S — System Contract Tests (Highest Value)

These tests prove end-to-end correctness of a *meaningful* contract boundary without re-implementing the system.

**Signals:**

* Exercises real wiring across multiple components (minimal real set).
* Catches regression in control flow, data flow, and lifecycle behavior.
* Fails for real breakage, not for refactors.

**Examples:**

* A “root revalidation” flow that uses real blueprints and validates outcomes.
* A concurrency primitive integration test that proves ordering/invariants.

> Use these sparingly and intentionally. They cost more to maintain.

#### Rank A — Behavioral Unit Contract Tests (High Value)

These are the backbone of the repo: small tests that validate contracts, invariants, and error behavior.

**Signals:**

* Asserts behavior through **public methods** and **documented outputs**.
* Validates meaningful branches and error paths.
* Avoids coupling to private fields/implementation details.

**Examples:**

* “Given these inputs, return/raise exactly X.”
* “After cleanup, public methods raise or behave as documented.”
* “Last-write-wins semantics for a registry.”

#### Rank B — State Transition Tests (Medium-High Value)

Tests that validate a clear state machine / lifecycle, especially around concurrency and cleanup.

**Signals:**

* Proves valid transitions and prevents illegal transitions.
* Focuses on lifecycle invariants (cleaned vs active, idempotence, ordering).
* Uses introspection APIs (`describe()`, snapshots) rather than poking raw private fields.

#### Rank C — Collaboration/Boundary Mock Tests (Medium Value)

These validate that we call collaborators correctly. They’re useful when the collaborator is expensive, external, or nondeterministic.

**Signals:**

* Mocks are used at **real boundaries** (I/O, network, filesystem, subprocess, time, OS).
* Asserts calls that matter (ordering, arguments, exactly-once / at-most-once) *when that is part of the contract*.

**Warning:**

* These become brittle if you over-specify calls.

#### Rank D — Regression Reproduction Tests (Targeted Value)

A test that exists to lock down a specific bug. Great when it’s truly a regression guard.

**Signals:**

* Title references the bug symptom.
* Minimal reproduction.
* Assertions match the corrected behavior.

#### Rank E — Line-Coverage Fillers (Low Value)

Tests that exist mainly to execute lines but don’t assert meaningful behavior.

**Signals:**

* Asserts “it didn’t crash” with no contract outcome.
* Asserts values that are incidental.

> We avoid these unless they are stepping stones toward higher-rank tests.

#### Rank F — Attribute/Existence Checks (Very Low Value)

This is the bottom. These tests almost always waste time and fail for harmless refactors.

**Examples (bad):**

* `assert obj._some_private_field is not None` (unless the field is part of a documented public contract, which is rare)
* `assert hasattr(obj, "x")` / `assert "x" in obj.__dict__` / `assert isinstance(obj._pending_changes, dict)`

**Why this is bad:**

* Doesn’t prove correctness.
* Over-couples tests to implementation.
* Encourages “coverage mirage.”

**Only acceptable when:**

* The attribute is explicitly part of a public, documented contract (rare), or
* You are validating cleanup nulling **as part of a lifecycle safety contract** and there is no better public signal.

### 3) Rules: Unit Tests First (Mock + Isolated)

The default approach is **mocked / isolated unit tests**.

* **Mock external boundaries** (I/O, filesystem, network, subprocesses, clocks, OS calls, databases, thread scheduling, random sources).
* Validate **contracts** (inputs/outputs/raises), **invariants**, and **side effects** (including cleanup ordering) at the smallest reasonable unit.
* Prefer **contract-level assertions** over implementation-detail assertions.
* Avoid flakiness: tests must run reliably on repeated runs.

#### Contract-level assertion checklist

When writing a unit test, you should be able to answer “yes” to most of these:

* Does the test assert an observable outcome (return, raise, snapshot, state transition)?
* Would the test fail if a real regression happened?
* Would the test *still pass* after a harmless refactor (renaming locals, reordering statements, changing internal data structures)?
* Are mocks only used at true boundaries?
* Are we asserting *behavior* rather than “internal shape”?

If not, the test is probably Rank E/F.

### 4) Integration Tests Second (Only When Needed)

Integration tests are required when behavior cannot be proven safely via mocks/unit tests.

Use integration tests when at least one is true:

* Correctness depends on real interactions across multiple components (e.g., concurrency scheduling, orchestration behavior, serializer/codec correctness across layers).
* Mocking would require re-implementing the system under test or would make the test meaningless.
* The integration is the contract (e.g., plugin wiring, adapter boundaries, real concurrency primitives).

Rules for integration tests:

* Keep them **scoped**: integrate only the minimal set of real components needed.
* Make them **explicit**: use clear naming and markers (e.g., `@pytest.mark.integration`) if the repo uses them.
* Ensure they remain **repeatable** and not environment-dependent unless explicitly documented.

### 5) Coverage Target: 95%+ (Non-Negotiable)

#### Agent Execution Constraint (Read Carefully)

AI agents **cannot truthfully confirm** repository-wide coverage levels (including the ≥95% target) unless the **user** runs the test suite and reports the result.

* Agents must **not** claim coverage numbers.
* Agents must **not** imply `pytest` or `pytest --cov` was executed.
* If the user asks “did you run tests/coverage?”, the only valid answer is **“Not run.”**

#### Agent Policy: Prefer Test Density Now; Verify Coverage Later

In the agent environment, **coverage measurement is treated as a follow-up step** that the **user** performs. Agents should **default** to producing a strong test suite using the density heuristic, and then **ask the user to verify ≥95% coverage later**.

**Default Path — Test Density (Preferred for Agent Work):**

Use this path unless the user explicitly provides coverage output.

* **Baseline density:** target **≥ 10 tests per 100 LOC** for the changed/covered module(s).
* **Dense / high cyclomatic complexity code:** increase target to **≥ 20 tests per 100 LOC** when the code shows any of the following:

  * high cyclomatic complexity (many branches/guards)
  * heavy error-path logic
  * concurrency / locking / ordering constraints
  * lifecycle/cleanup state machines
  * non-trivial invariants (dirty tracking, revalidation, promotion semantics)

These are heuristics—not a license to create filler tests. Every test must still meet the quality criteria below.

**Follow-Up Path — Coverage Verification (User-Run, Later):**

* Target: **≥ 95% line coverage** for the relevant package/module(s).
* Requirement: the **user** runs the suite (e.g., `pytest --cov`) and reports the output.
* Agent reporting: if the user has not run it, you must say **“Not run.”** and you must not guess.

If the user reports coverage below target, agents should add tests by increasing **branch/error/lifecycle** coverage—not by adding filler assertions.

We target **≥ 95% line coverage** across the library.

* Heuristic: we want at least **10 tests per 100 LOC**, but do not game it. If you have 95%+ coverage but fewer than 10 tests per 100 LOC, that’s acceptable.
* Coverage must not be “gamed” (no meaningless tests whose only purpose is to execute lines).

**Where we focus coverage:**

* Public API contracts
* Critical branching logic
* Error paths
* Lifecycle/cleanup behavior
* Concurrency-sensitive behavior (as testable)

If a component cannot reasonably hit the coverage target (rare), document the reason and the mitigation (integration coverage, property tests, or explicit exclusion with rationale) **and ask before applying exclusions**.

### 6) Truthful Validation Reporting

When reporting validation status:

* Only claim unit/integration/coverage runs if you actually ran them.
* If not run, say **“Not run.”**
* If recommending commands, be specific and repo-consistent (e.g., `pytest`, `pytest -q`, `pytest -m integration`, `pytest --cov`). Do not invent a workflow that contradicts repository docs.

### 7) Fixing Broken Base Code (While Writing Tests)

If you find mistakes while writing tests (bugs, incorrect docstrings, missing cleanup, race conditions):

* Raise them as issues rather than fixing them silently.
* If you have explicit permission to fix them, follow all rules in this document (docstrings, cleanup, scope control, tests).
* Do not fix unrelated mistakes outside your declared scope.
* If the mistakes block your work, explain the situation and ask for guidance.

---

## Summary

* This is a public library.
* Documentation is part of the API.
* Do precise, scoped edits.
* Avoid ambiguous/dynamic patterns in owned code.
* Initialize explicitly, then clean up deterministically.
* Logger teardown last.
* Tests must buy real confidence — attribute checks are bottom-tier.

---

## Test Mocks Skills

For reusable test-only classes and helpers, see `tests/mocks/SKILLS.MD`.

