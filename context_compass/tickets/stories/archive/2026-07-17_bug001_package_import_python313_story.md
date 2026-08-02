# Story: BUG-001 - package import crashes on advertised Python 3.13

## Metadata
- Story ID: STORY-2026-07-17-bug001-package-import-python313
- Epic: EPIC-2026-07-17-bugfix-package-python-compat
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p0
- Created: 2026-07-18T09:20:17Z
- Updated: 2026-07-18T12:50:51Z

## User Narrative
As a developer installing `melder` on a Python version its own package metadata advertises,
I want `import melder` to succeed, so that the library is usable at all on that interpreter.

## Value / MRP Alignment
A library that crashes on `import` on an advertised interpreter has zero MRP value on that
interpreter - every other correctness property is unreachable. This is the single highest-impact
finding in the whole audit; it gates first use.

## Ticket Contract
- ENTRY_GATE: Package epic routed to helper_0 (attention_board row in_progress); this story owns BUG-001 only.
- EXECUTION_BOUNDARY: `pyproject.toml` version/classifier metadata AND/OR the annotation sites that reference TYPE_CHECKING-only names. No unrelated refactors.
- DEPENDENCIES: Owner decision on the fix direction (see Decision Log) - this story is BLOCKED on that call.
- EXIT_GATE: `import melder` succeeds on every interpreter the (possibly updated) `requires-python` advertises, proven by a suite run on that interpreter; regression guard in place.
- FAILURE_ESCALATION: This story is a DECISION_REQUEST - it does not proceed to implementation until the owner picks Option A or Option B.

## Requirements (Functional)
- `import melder` must not raise `NameError` on any interpreter allowed by `requires-python`.

## Requirements (Non-Functional)
- Fix must obey synaptic craft rules: `from __future__ import annotations` is BANNED; PEP 604 unions banned; TYPE_CHECKING-first typing is the house style.

## Scope Boundaries
- In scope: `pyproject.toml`; `src/melder/crystallizer/asset_management/asset_management_system.py` param annotations at lines 84 and 455; any sibling modules with the same import-crash pattern IF Option B is chosen.
- Out of scope: functional behavior of AssetManagementSystem; other package_python_compat bugs (BUG-266-269, separate story).

## State Transition Event
- from_state: blocked
- to_state: review
- transition_reason: Owner chose Option A (2026-07-18); fix applied to pyproject.toml; story moves to review pending a user suite run on 3.14t.

## Dependencies / Related Work
- Audit evidence: `codex/2026-07-17_melder_bug_audit.md` (BUG-001), `codex/2026-07-17_melder_bug_audit_python313_compatibility.md`.

## Tasks (Implementation Checklist)
- [x] Task: Reproduce/confirm the mechanism against current source (done - see Notes).
- [x] Task: Verify annotation eval semantics empirically on an eager-annotation interpreter (done - 3.11.15).
- [x] Task: OWNER DECISION - Owner chose Option A (declare 3.14+), 2026-07-18.
- [x] Task: Apply the chosen fix - pyproject.toml requires-python/classifier/description to 3.14.
- [ ] Task: Add/confirm an `import melder` smoke test in the suite; user runs it on the min supported interpreter.
- [ ] Enforce Ticket Microcycle across all linked tasks.

## Acceptance Criteria
- `import melder` succeeds on the minimum interpreter advertised by `requires-python` (user-verified run).
- No `from __future__ import annotations` introduced; synaptic typing rules respected.

## Validation / Test Plan
- Minimal-repro (already run here) proves the mechanism + that quoting a param annotation removes the def-time NameError.
- Full validation requires a suite run on the min supported interpreter (3.14t for Option A; 3.13 + 3.14t for Option B). Agent cannot run the melder suite in-container: report "Not run" until the user runs it.

## Risks / Mitigations
- Risk (Option B): this file is one of potentially many with the same 3.14-native pattern; fixing only this file may leave `import melder` crashing at the next such module. Mitigation: Option B requires a repo-wide sweep of TYPE_CHECKING-only names used in param/return annotations, not a one-file change.
- Risk (Option A): narrows advertised support from the go-to-market "3.13+" story. Mitigation: it only removes a version the code never actually supported; genuine 3.13 support can be a separate future epic.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No implementation before the owner resolves the DECISION_REQUEST.
- [ ] No `from __future__ import annotations` (profile-banned) as the fix.

## Open Questions
- Does Melder Core officially support Python 3.13, or is it 3.14t-only? (The whole fix hinges on this.)

## Decision Log
- DATETIME: 2026-07-18T09:20:17Z
  TYPE: DECISION_REQUEST
  CLAIM: BUG-001 fix is a product-support fork. Option A: correct `pyproject.toml` to `requires-python = ">=3.14"` (+ classifier 3.13->3.14, description "3.13+"->"3.14+"). Zero source change; matches the authoritative `context_compass/AGENTS.md` "THIS IS PYTHON 314t" baseline and the code's actual 3.14-native idiom; makes the (currently false) 3.13 claim honest. Option B: keep `>=3.13` and make the code run on 3.13 - quote the two param annotations here (`persistence_system: "PersistenceSystem"`, `manager_configuration: "ExternalPersistenceManagerConfiguration"`) AND sweep the rest of the codebase for the same pattern (potentially many modules), since `import melder` crashes at the FIRST such site. `from __future__ import annotations` is BANNED by the profile, so it is not an option.
  RECOMMENDATION: Option A. The code is written to the synaptic 3.14 standard, the owner's own runtime baseline is 3.14t, and 3.13 is currently advertised falsely (import is broken). If the go-to-market "3.13+" story must hold, choose Option B and open it as a codebase-wide compat sweep epic.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-07-18T09:20:17Z
  TYPE: FACT
  CLAIM: BUG-001 reproduces against current source. `pyproject.toml` advertises Python 3.13, but `PersistenceSystem` and `ExternalPersistenceManagerConfiguration` are imported only under `if TYPE_CHECKING` and used in eager parameter annotations; on interpreters without PEP 649 lazy annotations they evaluate at def-time and raise NameError at import.
  EVIDENCE:
  - pyproject.toml:10-10
  - src/melder/crystallizer/asset_management/asset_management_system.py:28-34
  - src/melder/crystallizer/asset_management/asset_management_system.py:84-84
  - src/melder/crystallizer/asset_management/asset_management_system.py:453-456
  IMPACT: `import melder` fails on every advertised 3.13 interpreter before any API is reachable.
  NEXT: Owner picks Option A or Option B; then apply.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T09:20:17Z
  TYPE: MEASURE
  CLAIM: Empirically verified on CPython 3.11.15 (same eager-annotation behavior as 3.13): function PARAMETER and RETURN annotations evaluate at def-time (NameError for a TYPE_CHECKING-only name); `self.attr: T = v` and local `x: T = v` do NOT evaluate. So the crash sites are the param annotations at lines 84 and 455 only; line 108 (`self._persistence_system: PersistenceSystem`) is harmless.
  EVIDENCE:
  - src/melder/crystallizer/asset_management/asset_management_system.py:84-84
  - src/melder/crystallizer/asset_management/asset_management_system.py:108-108
  - src/melder/crystallizer/asset_management/asset_management_system.py:455-455
  IMPACT: Bounds Option B's per-file change to two quoted annotations, and confirms the sweep must target param/return annotations specifically.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T12:50:51Z
  TYPE: DECISION
  CLAIM: Owner chose Option A. pyproject.toml updated: requires-python >=3.13 to >=3.14, classifier 3.13 to 3.14, description 3.13+ to 3.14+. No source code changed; on 3.14t deferred annotations make the TYPE_CHECKING param annotations import-safe, so the advertised minimum imports.
  EVIDENCE:
  - pyproject.toml:8-10
  - pyproject.toml:37-37
  IMPACT: Removes the false 3.13 claim; advertised minimum (3.14) is the interpreter the code targets.
  NEXT: User runs the suite on 3.14t to confirm import, then accept + close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T12:50:51Z
  TYPE: MEASURE
  CLAIM: Not run. Agent cannot run the melder suite in-container (interpreter here is 3.11.15; melder not installed). Import verification on 3.14t is user-run.
  IMPACT: Validation status is Not run until the user executes it.
  NEXT: Run import melder (and pytest -q) on a 3.14t interpreter.
  REREAD: HELPFUL
  SCORE_0_TO_10: 6

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: the decision fork and its evidence; reference source line ranges, not tactical logs.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
BUG-001 confirmed against current source and empirically diagnosed. Story is BLOCKED on one owner
decision: Option A (declare 3.14+, recommended - zero source change, matches the 3.14t baseline) or
Option B (keep 3.13, requires a codebase-wide annotation-quoting sweep). Both fixes are specified in
the Decision Log. No source has been changed. On the owner's call this applies in minutes (A) or opens
a sweep story (B).
