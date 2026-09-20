# Feature turn-in failure repairs

Owning task: `tickets/tasks/completed/2026-09-19_fix_feature_turn_in_failures_task.md`.

## Repairs

- The crystallizer root test's `_DummySpell` omitted native `resolvable`. It now supplies True,
  matching the ordinary Spell contract. Production crystal capture remains strict.
- Local foundational compiler registration captured the previous scheduler run's cancellation event
  in positional arguments. The scheduler creates a new signal only when `run_all_phases` begins.
  Local Phase-5/6 factories now forward that current event at unit creation. Prior failed runs no
  longer poison later revalidation, and cancellation during the current phase remains effective.
- No retries, cancellation suppression, new locks, ownership changes or steady-state meld checks.
  The owner-supplied churn test is unchanged.

## Evidence

- `baseline.xml`: owner crystallizer failure reproduced; the other ten selected tests passed.
- `crystallizer_green.xml`: all seven crystallizer root tests pass after fixture correction.
- `cancellation_red_ready.xml`: all six deterministic new cases fail before the runtime repair.
  Two prove recovery after a real failed scheduler run; four prove current-run cancellation reaches
  local Phase-5/6 bodies. Cases use one and four real scheduler workers.
- `focused_green.xml`: 358 passed across both owner files, the new regression, creation-system
  tests and synchronization unit/component tests.
- `churn_summary.log`: 25 fresh-process runs of the unchanged live churn case pass.
- `final_green.xml`: 53 passed and one existing asset-runner skip after final import/style changes.
- `qualification_summary.json`: the two final green selections contain 394 distinct passing tests,
  one skipped asset-runner case and no failures. These overlap; do not add their counts.
- `final_validation.xml` records an earlier sandbox-only fixture setup failure: Windows denied
  access to pytest's default temporary directory. The exact selection subsequently passed outside
  the sandbox with its basetemp and reports under this artifact directory.
- `cancellation_red.xml` is the initial test-harness setup failure before binding fresh Aether
  class handles, retained as diagnostic history rather than the production regression evidence.

## Documentation and builds

- `src_components` now documents local event binding and the existing persistent pool/per-run
  cancellation lifecycle. `components_before.md` and `doc_line_changes.json` account for the five
  replaced lines; remaining document content is preserved. This is a scoped update, not a full audit.
- The creation-system descriptor was refreshed through canonical extraction/merge. Existing authored
  edges and semantic stamps were retained; the graph and component index were regenerated.
- Source assets and all repository bundles were regenerated/checked for the existing version 0.2.43.
  `check_source_final.log` and `check_llm_final.log` both pass. No package version was changed.
- `style_green.log`: new regression Ruff passes, excluding UP045 for the required Optional spelling.
- Full repository suite and coverage: Not run. The prior feature qualification remains separately
  documented in `artifacts/non_resolvable_graph_replay_20260919/validation.md`.

## Execution

Tests used `.venv_new` Python 3.14.7 free-threaded, uv `--no-sync --offline`, `-X gil=0`, and
pytest `-p no:cacheprovider`. Reports and the fresh-process churn logs are retained here.
The owner requested feature turn-in, then required these two repairs first; closure follows their
successful qualification. No git commit, push, release or publication is part of this pass.
