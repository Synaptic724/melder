# Runtime admission qualification

Recorded: 2026-09-19T22:08:58Z. Owner: updater_0.
Ticket: `tickets/tasks/completed/2026-09-19_enforce_non_resolvable_runtime_admission_task.md`.

## Delivered behavior

Both concrete Meld doors refuse selected non-resolvable registrations before override normalization,
optional validity checks, hooks, construction/context acquisition or existing-object retrieval.
The shared MeldExecutionError identifies the selected version and explains consumer overrides and
resolvable registrations. Observational lookup remains available.

Four native checks and one shared cold helper implement this boundary. The warm guard ladder is
unchanged: a False registration cannot reach success-only warm-entry insertion, and capability is
immutable per version. No additional per-hit capability check or ownership/cache framework was added.

## Test evidence

- Red baseline: 58 failures. Runtime reached missing artifacts/validity errors or returned an existing
  supplied object; the requested refusal diagnostic was absent.
- New regression file: 58 passed in 0.64s, `admission_green.log` and `.xml`.
- Broader qualification: **665 passed, 1 skipped in 4.11s**, `compatibility_green.log` and `.xml`.
  This total includes the 58 new cases; do not add the two counts together.
- The one skipped shared-context rebuild test was already explicitly deferred by the project owner.
- Scope: both concrete doors; public selectors; automatic/dynamic and scoped paths; optional validity
  bypass; repeated input-cache lookups; existing-object reuse; overrides/hooks; True provider control;
  dynamic notch; existing fast-door tests; Meld unit/conduit component/compiler/default compatibility.
- Two legacy unit fixture constructors received the existing native `_resolvable=True` slot. All 34
  initial compatibility failures came from those incomplete stubs; no production fallback was added.

Environment: `.venv_new`, Python 3.14.7 free-threaded, uv `--no-sync --offline`, `-X gil=0`.
Pytest used `-p no:cacheprovider`; reports and uv cache are under this task's artifact directory.

## Documentation, assets and style

Runtime source prose, failure contract, diagrams and C1 extents were updated; indexes and graph rebuilt.
Three runtime descriptors and the other agent's package-root doc-only hash were refreshed. Authored
edges/stamps were preserved. The runtime class semantics stamps remain stale: scoped authored changes
are not a claim of whole-class semantic re-audit.

`doc_baseline.json` was captured before edits; `doc_line_changes.json` accounts for replaced feature
status and C1 values. Its apparent unrelated Claims-line loss is case-insensitive PowerShell grouping:
both original case variants remain at src_components lines 3425 and 3577. Nothing was deleted there.

Source assets rebuilt and all three check families pass against the current workspace version 0.2.43.
This task did not change the version. LLM source/tests bundles rebuilt with `--include-untracked`;
all src/tests/other fingerprint/output proofs pass. New-file/helper Ruff passes with only UP007/UP045
excluded to honor role-required Union/Optional; no lint policy or suppression comments changed.
Whitespace checks pass with existing CRLF tolerated. See build logs and `style_green.log`.

## Remaining boundary

Full repository suite and coverage: Not run. Required-input presence and nested branch/reuse preflight
inside emitted/hydrated executors remain the next S4 task. Nexus graph/history and crystal replay
remain later stories. These results establish direct runtime admission, not full feature completion.
