# Task: Melder core __init__ composition + wheel hand-off to CommandOps (strategy)

## Metadata
- Task ID: TASK-2026-07-19-melder-init-wheel-strategy
- Status: in_progress
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
- Priority: p1
- Created: 2026-07-19T09:58:00Z
- Updated: 2026-07-19T09:58:00Z

## Problem / Opportunity
The owner wants (1) a composition ruling for the core `src/melder/__init__.py` and (2) the
path to building melder as a wheel consumed by CommandOps. The init currently mixes public
API re-exports, metadata, guardrail warnings, a hardcoded DEBUG_MODE version mutation, and
an import-time world boot; version truth lives in three disagreeing places.

## Ticket Contract
- ENTRY_GATE: owner request 2026-07-19 ("figure out what to do about the core melder init
  ... turning this into a wheel and moving it into commandops").
- EXECUTION_BOUNDARY: STRATEGY ONLY in this task - reads + one strategy note + owner
  decision capture. Implementation gets its own ticket(s) + patch lane (the init and the
  Spellbook._aether seam are system-impacting).
- DEPENDENCIES: none.
- EXIT_GATE: owner picks an option per decision point; follow-up implementation lane
  opened or explicitly deferred.
- FAILURE_ESCALATION: DECISION_REQUEST rows below; no code edits from this task.

## Scope Boundaries
- In scope: __init__.py, pyproject.toml, __version__.py, packaging/hand-off mechanics.
- Out of scope: any code edit; CommandOps-side changes (separate repo).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: investigation executed in-lane with the owner present.

## Noting Behavior
- Task notes: tactical findings, immediate impacts, one-step continuation.

## Notes
- DATETIME: 2026-07-19T09:58:00Z
  TYPE: FACT
  CLAIM: Investigation complete over the three packaging surfaces. (1) IMPORT-TIME WORLD
    BOOT IS STRUCTURAL, NOT JUST THE INIT LINE: __init__.py calls Aether() at import, but
    spellbook.py:119 pins `_aether: ClassVar[Aether] = Aether()` at CLASS-BODY time - the
    singleton world (AetherUtilitySystem + Crystallizer + Nexus roots) is born the moment
    spellbook.py imports, which the init's own re-export chain triggers anyway. This class
    -level capture is also why every test must patch `Spellbook._aether = aether` after
    singleton resets (stale-instance trap). (2) VERSION TRUTH IS TRIPLED AND DISAGREES:
    pyproject [project] version = "0.1.0" (static), __version__.py = "0.1.0", and
    __init__.py:45 mutates via hardcoded DEBUG_MODE = True -> "0.1.0.dev0", while the
    pre-existing failing test expects base + "-dev". (3) WHEEL POSTURE IS ALREADY CLOSE:
    src layout + setuptools configured, requires-python >=3.14, license Apache-2.0
    (matches the 2026-07-02 pivot), dependencies == [] (ULID generator is internal -
    zero-dep pure-Python wheel, py3-none-any; free-threading needs no special ABI for
    pure wheels). Gaps: NOTICE not declared in license-files (Apache distribution duty),
    init docstring references dead "ThreadFactory" framing, guard singleton instantiated
    a SECOND time at package level (the module's own instance at
    __melder_registration_guard__.py is the one internals import), and context_compass/
    tests/benchmarks correctly excluded from the wheel by src-layout.
  EVIDENCE:
  - src/melder/__init__.py:1-107
  - src/melder/aether/spellbook/spellbook.py:119-119
  - pyproject.toml:1-98
  - src/melder/__version__.py:1-12
  - tests/unit/melder/test_package_version_metadata.py:11-16
  IMPACT: The wheel is nearly free; the real decisions are init composition, the
    import-time boot seam, and version truth - all owner rulings.
  NEXT: Present the strategy discussion (4 decision points, recommendation per point);
    capture rulings as DECISION rows; open the implementation lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T11:52:30Z
  TYPE: DECISION
  CLAIM: Implementation lane opened and landed per the four captured rulings:
    STORY-2026-07-19-melder-init-composition behind patch lane
    melder_init_composition_2026_07_19 (init loaded flat/eager; guard sentinel early;
    version single truth + pyproject dynamic; license-files declared; dev-suffix test
    retired for the equality law). The Spellbook._aether class-body seam remains the
    separate patch-gated follow-up per the original boundary. This task's exit gate is
    met pending the owner's build walkthrough.
  EVIDENCE:
  - context_compass/tickets/stories/2026-07-19_melder_init_composition_story.md:1-1
  IMPACT: Strategy lane closes into the implementation story.
  NEXT: Close at the owner's acceptance walkthrough alongside the story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Strategy-only lane for the init/wheel/CommandOps hand-off program. Findings above;
awaiting owner rulings on the four decision points presented in-session.
