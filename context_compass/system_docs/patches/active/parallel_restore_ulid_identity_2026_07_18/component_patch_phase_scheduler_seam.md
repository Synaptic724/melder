# Component Patch: PhaseScheduler explicit-config seam (S2)

Lane: parallel_restore_ulid_identity_2026_07_18. Ticket: STORY-2026-07-18-phase-scheduler-config-seam.

## Before
- PhaseScheduler reads worker count and barrier timeout exclusively from
  SpellbookConfiguration keys (phase_scheduler.py:170-217) and is constructed only by
  spellbook creation lanes; world-scope owners (the crystallizer loader) cannot construct
  one without a spellbook configuration.

## After
- __init__ accepts keyword-only worker_count / barrier_timeout_ms overrides (validated
  positive ints, bool-rejected, same validation style as the config readers). When
  supplied, the configuration readers are skipped; when omitted, behavior is byte-identical
  to today. No execution-semantics change: pool, queue, latch, cancellation untouched.
- CrystallizerConfiguration gains restore_scheduler_workers and
  restore_scheduler_barrier_timeout_milliseconds (class-level defaults via the builder; no
  module constants), consumed by CrystalLoaderSystem in S4.

## Interface Deltas
- PhaseScheduler.__init__(..., worker_count: Optional[int] = None,
  barrier_timeout_ms: Optional[int] = None) - additive keyword-only.
- CrystallizerConfiguration(+builder): two new keys with schema defaults.

## State / Failure Deltas
- None at runtime; construction-time ValueError/TypeError parity with existing readers.

## Dependency / Ordering
- Independent of S1; prerequisite for S4's loader-owned scheduler; S3 consumes the pool's
  thread identities for cohort enrollment.

## Validation Expectations
- Existing spellbook scheduler suites pass untouched (config path proof). New unit rows:
  explicit construction, invalid values raise, precedence (explicit beats config), docstring
  contract updated. Density >= 10/100 LOC.

## Delta 2026-07-19 (S4 REOPEN): fail-fast quiesce
- The fail-fast error path now quiesces in-flight stragglers before raising; full
  control-flow contract in code_description_patch_phase_scheduler_quiesce.md (authored
  BEFORE code per the concurrency-sensitive trigger). PhaseLatch gains the additive
  wait_all_reported(timeout) verb. Pool, queue, config seam, and timeout preemption
  semantics unchanged.
