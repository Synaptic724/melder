# Task: Persistent gauntlet duration/thread series and parallel promotion CI

## Metadata
- Status: done
- Owner: codex
- Agent Name: command_0
- Created: 2026-10-03T17:18:21.171206+00:00

- Completed: 2026-10-03T19:01:18Z
- Summary: Delivered 2026-10-03 (command_0): persistent_runtime_gauntlet_series_runner.py and
  test_persistent_runtime_gauntlet_series.py - the [60,180,300]-second x [3,5]-thread series, 36 cells per OS,
  each cell a fresh GIL-off process - plus a separate three-OS CI workflow required on dev-to-preprod
  promotion; 322 focused cases green including 24 real isolated cells; bundles regenerated with --check OK; no
  src change. The multi-hour hosted run remains for the owner. Closed by owner directive 2026-10-03.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-03T19:01:18Z) owner directive in chat, 2026-10-03: every active ticket in review
  is done; turned in by fable_1 under TASK-2026-10-03-turn-in-review-tickets.

## Authority and scope
Owner extends the Melder benchmark work: add a separate pytest series file and a separate
runner holding editable configuration and aggregation. Select durations [60,120,180,240,300]
seconds (300 maximum) and thread counts [3,5,7]. Reuse the existing persistent workloads,
warmup, lifetime checks and cleanup. Owner also requests a separate CI worker so this series
runs alongside the real-world gauntlet on dev-to-preprod promotion. Prior Melder onboarding
waiver continues for this benchmark task.

## Implementation contract
Each duration/thread/scenario/library combination runs in a fresh GIL-off Python process.
Preserve the existing two scenarios and three libraries, giving 90 cells and 4.5 hours of
measurement per OS plus warmup/setup. Keep scalar benchmark source files unchanged.
Write separate cell logs/results plus aggregate JSON, CSV and a readable summary. Keep
completed results if a later cell fails. Both CI benchmarks must succeed on dev-to-preprod;
other routes intentionally skip them. Use separate three-OS jobs with no dependency on one
another, and retain independent reports. No runtime Melder source edits or publication.

## Validation
Use contract tests plus short real subprocess cells, not the full multi-hour series.
Verify GIL-off, requested identity, all selected combinations, rejection above 300 seconds,
aggregation separation, failure propagation, independent workflow scheduling and merge gates.
Regenerate required repository bundles. The hosted run remains for after the changes land.

## Artifacts
- artifacts/2026-10-03_persistent_gauntlet_series/; retain_as_reference.
- CONTEXT_MANAGEMENT_REQUIRED: false.

## Owner size revision
Use [60,180,300] seconds and [3,5] threads instead. Both scenarios and three libraries
produce 36 cells, 108 minutes measured plus 6 minutes warmup per OS, before setup/cleanup.
Separate three-OS CI workflow is wired in parallel with the first gauntlet; both share the
validated promotion requirement. The first benchmark and its local defaults remain unchanged.

## Delivery
Implemented the owner's revised [60,180,300]-second and [3,5]-thread series.
Configuration and aggregation live in persistent_runtime_gauntlet_series_runner.py;
ordinary pytest entry is test_persistent_runtime_gauntlet_series.py. The new persistent
workflow uses independent runners and is scheduled alongside the real-world gauntlet
only on dev-to-preprod promotion PRs; the final gate requires both. Manual runs remain.

focused.xml: 322 passing cases, zero failures/errors/skips, including 24 real isolated
0.2/0.3-second cells across every library/scenario and 3/5 threads. Verified original
benchmark SHA hashes unchanged, source/test/other bundle proofs OK, and staged/unstaged
diff checks clean after correcting appended ignore-entry line endings. Four new files
staged only to include them in tracked-input bundles. No multi-hour run, hosted run, commit,
push or runtime Melder source change performed. delivery.json records final evidence and hashes.
Await owner review.
