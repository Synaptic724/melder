# Story: OCE S1 - Package root document surfaces (exemplar diff)

## Completion
- Completed: 2026-07-23T00:30:00Z (done_pending_owner_run)
- Summary: Guard sentinel + Subsystem/System Context landed on the root document surfaces (the
  exemplar diff). The open DECISION_REQUEST (persist per-instance agent_purpose) is a behavior
  change the program's non-goals exclude - deferred to owner, not implemented.
- TESTS NOT RUN by agent. Filed done_pending_owner_run.

## Metadata
- Story ID: STORY-2026-07-19-oce-root-document-surfaces
- Epic: EPIC-2026-07-19-oce-package-root
- Status: in_progress
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-19T01:55:00Z
- Updated: 2026-07-19T01:55:00Z

## Objective
Bring `StaticSystemDocument` and the four packaged hardcopy modules to full Object Contract
compliance, producing the reference diff the other nine child epics copy.

## Ticket Contract
- ENTRY_GATE: program epic contract read; base-class guard exclusions verified clean
  (`Cleanable`, `Sync`, `AbstractElasticPool` all unguarded); import chain proven acyclic.
- EXECUTION_BOUNDARY: `src/melder/system_document.py`, `src/melder/__architecture__.py`,
  `src/melder/__components__.py`, `src/melder/__graph_network__.py`,
  `src/melder/__graph_details__.py`.
  EXCLUDED: `__init__.py`, `__melder_registration_guard__.py`.
- DEPENDENCIES: THE OBJECT CONTRACT + THE MRO LAW in the program epic.
- EXIT_GATE: `StaticSystemDocument` carries all five contract items; owner rules on the
  discarded-`agent_purpose` finding below.
- FAILURE_ESCALATION: DECISION_REQUEST for anything requiring a behavior change.

## Scope Boundaries
- In scope: guard sentinel, docstring enrichment (Subsystem + System Context), module
  docstrings on the four hardcopy modules.
- Out of scope: populating placeholder hardcopy payloads; persisting per-instance
  `agent_purpose` (raised as DECISION_REQUEST, not implemented).
- Guard classification: `StaticSystemDocument` = MELDER KERNEL -> guarded. It is an
  import-time immutable carrier Melder constructs; a user would never ask Melder to inject
  one. Not a base class, so the MRO law does not apply.

## Steps / Checklist
- [x] Verify base-class exclusions are clean.
- [x] Verify import chain acyclic before adding the guard import.
- [x] Add guard sentinel to `StaticSystemDocument`.
- [x] Enrich class docstring with Subsystem Context + System Context.
- [x] Enrich the four hardcopy module docstrings.
- [ ] Owner ruling on the discarded `agent_purpose` (DECISION_REQUEST below).
- [ ] Guard regression: `bind(StaticSystemDocument)` refused; user `Cleanable` subclass
      accepted.

## Validation
- Not run. (`py_compile` only; the 3.14t suite is the owner's run.)
- Recommended: `pytest tests/unit/melder/utilities -q`

## Notes
- DATETIME: 2026-07-19T01:55:00Z
  TYPE: DECISION_REQUEST
  CLAIM: `StaticSystemDocument.__init__` accepts `agent_purpose` and then DISCARDS it
    (`_ = agent_purpose`, :84). All four hardcopy modules pass a specific, useful purpose
    string - "Query this first for top-down system understanding", "Query this for
    graph-network topology" - and every one is thrown away. Because `__agent_purpose__` is a
    class attribute, all four instances report the same generic
    StaticSystemDocument purpose instead of their own. This directly defeats the program's
    stated goal that an agent can query an object and learn what it is for.
  EVIDENCE:
  - src/melder/system_document.py:52-54
  - src/melder/system_document.py:84-84
  - src/melder/__architecture__.py:11-14
  IMPACT: The four most agent-facing objects in the package cannot describe themselves
    individually. Fix is small: add `_agent_purpose` to `__slots__`, store the argument, and
    expose a read-only `agent_purpose` property that falls back to the class-level string.
  NEXT: Owner ruling. NOT implemented in this story because the program epic's non-goals
    forbid behavior changes, and persisting a previously discarded argument is one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Exemplar story. Guard + Subsystem/System Context docstrings landed on the root document
surfaces. One open owner decision: whether to persist per-instance `agent_purpose`, which is
a behavior change this program's own non-goals exclude.
