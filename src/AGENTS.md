# AGENTS.md — Public Library Editing Contract

This repository is a **public library**. Code quality and documentation are first-class deliverables.

> **Placement:** Put this file at the repository root. You may add per-directory variants when needed.
>
> * `AGENTS.md` — normal rules for the directory
> * `AGENTS.override.md` — directory-specific override/patch rules (highest priority)

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

  * constants / sentinels
  * small immutable lookup tables
  * **pure functions** (no side effects, no hidden state, deterministic)
* If a helper is **not obviously pure/stateless** or would introduce **shared state**, **ask first**.
* If an existing module already uses module-level helpers, you may follow the pattern, but **do not add new module globals** without asking.


### 7) No `print()` — Use the Library’s Logging Pattern

* Do not add `print()`.
* Use the library’s logging abstraction/pattern.
* If you cannot identify the correct logger usage, **ask** rather than inventing a new logging style.

### 8) Attribute Access Rule (No Defensive Introspection in Owned Code)

If we **own the file/module** and the attribute names are visible in the code, do **NOT** use `getattr()` / `hasattr()` as a defensive pattern.

* Use direct access (`obj.attr`).
* Handle `None` explicitly where appropriate.

`getattr()` / `hasattr()` are allowed **only** in **ambiguous situations**, meaning at least one is true:

* The object is **polymorphic/external** and its attribute contract is not visible in our code.
* The attribute/method is **optional by design** (capability checks).
* The attribute name is **truly dynamic**.

**Polymorphic lock cleanup exception (allowed):**

* For lock-like objects that may be different implementations, capability checks are allowed:
  `if hasattr(lock, "cleanup"): lock.cleanup()`

**Disallowed example (we own it / visible contract):**

* `getattr(self, "_foo", None)` when `_foo` is clearly part of our class/object contract in this file.

### 9) Constructor / Initialization Requirements

When adding or modifying `__init__` / initialization flows:

* Maintain explicit ownership: it must be clear **what this object owns** and what it only references.
* Initialize fields deterministically and explicitly.
* If an attribute is optional, initialize it to `None` (or a clear sentinel) and document that contract.

### 10) Cleanup / Teardown Discipline (Immediately After Initialization)

Cleanup is a core part of this library’s correctness contract.

* Cleanup must be **deterministic** and **idempotent**.
* Prefer **object teardown**: call `cleanup()` on child objects, then **null references** to assist GC and prevent use-after-clean.
* Look at existing implementations of the class for patterns to better understand requirements. We cleanup everything do not leave anything to the GC.
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

### 12) Validation Truthfulness

* **Never claim tests/lint/type-checks were run unless they were actually run.**
* If validation is skipped, say explicitly: **“Not run.”**
* If fast checks exist, recommend the exact commands — but do not pretend they happened.

### 13) Public API Guardrail

* Do not change **public API shape or semantics** unless explicitly requested.
* If a public change is unavoidable, prefer:

    * backwards-compatible adapters/shims, and/or
    * explicit deprecation paths with documentation.

### 14) Banned / Disallowed Patterns

* **Never use `type: ignore`.**

---

## Operating Protocol (How You Should Work)

### A) Propose → Confirm → Implement

Before making non-trivial edits:

1. Restate the goal in **3–5 bullets**.
2. List the constraints you will obey (especially docstrings/comments + no-drive-by refactors).
3. List the **exact files / symbols** you will modify.

If any of the above is uncertain, **stop and ask** before editing.

### B) Scope Control

* Stay within the declared files/symbols.
* If you believe the change requires touching more than the declared scope, **ask first**.

### C) Documentation Ritual

As a ritual, after implementing a change:

* Re-read the docstrings/comments you touched.
* Improve them for clarity and completeness (without fluff).
* Ensure they match the new behavior exactly.

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

Quality is enforced through tests. **All changes must be accompanied by tests** unless explicitly exempted.

### 1) Preferred Framework: `pytest`

* Use `pytest` as the default test runner.
* Use fixtures for setup/teardown and dependency injection.
* Keep tests deterministic: no reliance on wall-clock time, network, or external services unless explicitly marked and scoped as integration tests.

### 2) Unit Tests First (Mock + Isolated)

The default approach is **mocked / isolated unit tests**:

* **Mock external boundaries** (I/O, filesystem, network, subprocesses, clocks, OS calls, databases, thread scheduling, random sources).
* Validate **contracts** (inputs/outputs/raises), **invariants**, and **side effects** (including cleanup ordering) at the smallest reasonable unit.
* Prefer **contract-level assertions** over implementation-detail assertions.
* Avoid flakiness: tests must run reliably on repeated runs.

### 3) Integration Tests Second (Only When Needed)

Integration tests are required when behavior cannot be proven safely via mocks/unit tests.

Use integration tests when at least one is true:

* The correctness depends on real interactions across multiple components (e.g., concurrency scheduling, orchestration behavior, serializer/codec correctness across layers).
* Mocking would require re-implementing the system under test or would make the test meaningless.
* The integration is the contract (e.g., plugin wiring, adapter boundaries, real concurrency primitives).

Rules for integration tests:

* Keep them **scoped**: integrate only the minimal set of real components needed.
* Make them **explicit**: use clear naming and markers (e.g., `@pytest.mark.integration`) if the repo uses them.
* Ensure they remain **repeatable** and not environment-dependent unless explicitly documented.

### 4) Coverage Target: 95%+ (Non-Negotiable)

* Target **≥ 95% line coverage** across the library.
* Coverage must not be “gamed” (no meaningless tests whose only purpose is to execute lines).
* Focus coverage on:

  * public API contracts
  * critical branching logic
  * error paths
  * lifecycle/cleanup behavior
  * concurrency-sensitive behavior (as testable)

If a component cannot reasonably hit the coverage target (rare), document the reason and the mitigation (e.g., integration coverage, property tests, or explicit exclusion with rationale) **and ask before applying exclusions**.

### 5) Truthful Validation Reporting

When reporting validation status:

* Only claim unit/integration/coverage runs if you actually ran them.
* If not run, say **“Not run.”**
* If recommending commands, be specific and repo-consistent (e.g., `pytest`, `pytest -q`, `pytest -m integration`, `pytest --cov`, etc.), but do not invent a workflow that contradicts repository docs.

---

## Summary

* This is a public library.
* Documentation is part of the API.
* Do precise, scoped edits.
* Avoid ambiguous/dynamic patterns in owned code.
* Initialize explicitly, then clean up deterministically.
* Logger teardown last.
