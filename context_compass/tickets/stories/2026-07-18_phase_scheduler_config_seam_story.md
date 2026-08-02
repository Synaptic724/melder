# Story: S2 - PhaseScheduler explicit-config seam (world-scope construction)

## Metadata
- Story ID: STORY-2026-07-18-phase-scheduler-config-seam
- Epic: EPIC-2026-07-18-parallel-restore-ulid-identity
- Status: review (code + regressions landed; pending owner 3.14t run)
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
- Priority: p1
- Created: 2026-07-18T22:30:00Z
- Updated: 2026-07-18T22:30:00Z

## Objective
Let non-spellbook owners construct a PhaseScheduler: keyword-only explicit
worker_count/barrier_timeout_ms overrides beside the existing configuration path, plus
crystallizer-owned configuration keys, so the restore lane owns a world-scope scheduler.

## Ticket Contract
- ENTRY_GATE: epic active; scheduler-seam component patch linked and read.
- EXECUTION_BOUNDARY: phase_scheduler.py __init__/_get_worker_count/_get_timeout_ms
  (additive overrides only), crystallizer_configuration(+builder) new keys
  (restore_scheduler_workers, restore_scheduler_barrier_timeout_milliseconds), tests.
  Spellbook call sites untouched.
- DEPENDENCIES: component_patch_phase_scheduler_seam.md.
- EXIT_GATE: existing spellbook scheduler suites untouched-and-green; new unit rows prove
  explicit-value construction, validation errors, and config precedence.
- FAILURE_ESCALATION: DECISION_REQUEST if any existing suite pins the config-only path.

## Scope Boundaries
- In scope: constructor seam + config keys + docstring truth updates.
- Out of scope: scheduler execution semantics (no barrier/queue/pool changes).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: patch authored; second tranche after S1.

## Steps / Checklist
- [ ] Keyword-only worker_count / barrier_timeout_ms overrides (validated ints).
- [ ] Crystallizer configuration keys + builder defaults (class-level, no module constants).
- [ ] Docstrings updated (scheduler is generic infrastructure, spellbook is one owner).
- [ ] Unit regressions for both construction paths.

## Validation
- Not run. Recommended: pytest -k phase_scheduler.

## Applicable Anti-Patterns
- [ ] No behavior drift in the config path; overrides are additive.

## Noting Behavior
- Story notes: cross-task synthesis and gate transitions.

## Notes
- DATETIME: 2026-07-18T23:32:37Z
  TYPE: MEASURE
  CLAIM: Implemented and committed. (1) PhaseScheduler.__init__ gained keyword-only
    worker_count / barrier_timeout_ms overrides with a shared _require_positive_override
    validator (bools rejected, positive ints only, config-reader strictness mirrored);
    half-explicit construction with no configuration refuses loudly with remediation text;
    _configuration annotation widened to Optional; class docstring now names both lanes.
    Config lane byte-identical when overrides are omitted. (2) CrystallizerConfiguration
    gained restore_scheduler_workers (default 4) and
    restore_scheduler_barrier_timeout_milliseconds (default 60000 - restore units import
    and bind real code; spellbook-scale timeouts would abort large-world loads); registered
    in available_properties, set in with_defaults, positive-int checked in validate();
    old records backfill through the reload lane's defaults floor (reported, never silent).
    (3) Five regressions appended to the scheduler unit suite: explicit lane runs phases,
    invalid overrides refuse, half-explicit refuses, explicit-beats-config precedence,
    config lane unchanged. AST + device py_compile green x3 (3.10 syntax check; behavior
    rides the owner's 3.14t run).
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_scheduler.py:126-250
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:83-97
  - tests/unit/melder/utilities/synchronization/test_phase_scheduler.py:336-460
  IMPACT: S4's loader-owned scheduler is unblocked; spellbook lane untouched.
  NEXT: S3 opens with its code_description patch (gate law: no gate code before it).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Mechanical seam; unblocks S4's loader-owned scheduler.
