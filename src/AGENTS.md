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

### 6) No Module-Level Functions or Globals

* Avoid module-level functions and module-level state.
* Prefer instance-bound methods, classes, and locally-scoped helpers.
* If an existing module already uses module-level helpers and you must add one, **ask first**.

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
* **Never import `RLock` directly.**

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

## Summary

* This is a public library.
* Documentation is part of the API.
* Do precise, scoped edits.
* Avoid ambiguous/dynamic patterns in owned code.
* Initialize explicitly, then clean up deterministically.
* Logger teardown last.
