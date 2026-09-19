# Non-resolvable registration feature qualification

Owner: updater_0. Recorded: 2026-09-19T23:21:53Z.
Owning task: `tickets/tasks/2026-09-19_publish_and_replay_non_resolvable_definitions_task.md`.

## Delivered contract

- `bind` and `bind_inactive` retain per-version `resolvable: bool = True`. False definitions keep
  registration/source/version identity while direct resolution and reuse refuse them.
- The compiler preserves selected descriptive references without construction edges or False-root
  execution plans. Ordinary defaults and real resolvable providers retain their existing behavior.
- Supplied values use the existing solo/many-only/generalized override paths, including manifest
  hydration. Python handles missing ordinary required arguments. No runtime argument preflight added.
- Nexus publishes capability, dependency/reference and registered direct-base links in the existing
  binding payload. `describe_spell_relationships` exposes visible incoming/outgoing links through
  ViewSpell and FrameViewer. Hidden binding sections/targets are filtered; no instance is resolved.
- Late structural compilation republishes current reference metadata. Existing explicit Rift
  projection refresh and active/parked publication rules remain. Research history/source reads work.
- SpellCrystal captures the bool; active/staged restore and selected/parked/merge graft forward it.
  New records use the existing major-version gate at 2.0.0. Older records without the field use True.
  Restored bindings/selected members reconstruct references through normal compilation.
- Existing source/version identity rules are retained. No package version, release, ownership model,
  automatic method-body versioning or named lesser-conduit feature was introduced.

## Runtime validation

`qualification_summary.json` deduplicates `(classname, name)` across the five final reports in its
recorded order, taking the latest result when a corrected fixture was rerun:

**8055 passed, 1 pre-existing skipped, 4 pre-existing expected failures; 0 unresolved failures.**

- `combined.xml`: 499 passed across targeted Nexus/compiler/crystal/loader/component tests, new
  graph/history/legacy/staged tests and supplied-value compatibility.
- `broad.xml`: 7595 passed initially; ten old cache/dump fixture failures were corrected.
- `remaining.xml`: all 91 cases in those two corrected files passed, resolving the ten failures.
- `replay.xml`: 49 passed and three existing graft-uniqueness xfails; one old literal version assertion
  failed and was corrected to the current record version.
- `replay_final.xml`: four passed and one existing graft xfail, resolving that assertion and proving
  real source/history access plus graph visibility filtering after the final test additions.
- `version_graph.xml`: the strengthened existing graph case passes with parked version history,
  explicit notch and updated base links while old history remains readable (no additional case count).

The counts overlap and must not be summed. The summary records 8060 distinct cases in total.
Earlier red/failed reports remain as diagnostic history, not current failures.

Environment: Python 3.14.7 free-threaded in `.venv_new`, uv `--no-sync --offline`, `-X gil=0`,
pytest `-p no:cacheprovider`. Windows sandbox temp-folder ACLs required running the affected suites
outside the sandbox; their explicit basetemps and reports stayed inside this task directory.

## Documentation and generated assets

- Public registration/override guides document usage, ordinary constructor errors, graph navigation,
  record compatibility and unchanged version/lifecycle semantics.
- Source architecture/components and measured affected C1 ranges were refreshed. Their indexes and
  the assembled graph were regenerated using the existing tools. Scoped descriptor semantics were
  updated without inventing a whole-class audit or accepting stale semantic stamps.
- `doc_baseline.json` was captured before edits; `doc_line_changes.json` accounts for replaced stale
  feature-status/version text and remeasured C1 values. No unrelated material was discarded.
- Source assets rebuilt for the current workspace package version 0.2.43.
- Final source and src/tests/other bundle freshness checks pass; see `check_source_final.log` and
  `check_llm_final.log`. The public guide example executes successfully (`documented_example.py`).
- 39 documentation tests pass and the strict 294-page HTML build succeeds using the existing pinned
  docs environment from the positional-example task. The primary dev environment lacks Sphinx/Jinja;
  it was not modified to install them. Site-check result is retained in `site_check.log`.
  Final site/source parity also passes in `check_site_final.log` (35,513 local links).
- New test/helper Ruff checks pass with only UP007/UP045 excluded for the role's required Union/Optional
  spelling. No lint policy or suppression comments changed. Whitespace checks tolerate existing CRLF.

## Scope limits retained deliberately

- Existing whole-child overrides eagerly construct registered children before replacement. A plain
  required-int control reproduces this without the new feature. Tests preserve that existing behavior;
  branch pruning was not added under the guise of required-input validation.
- Existing process-wide uniqueness still rejects grafting a second live copy of the same identity.
  The successful graft test imports detached custody after releasing source claims. The three older
  live-copy conflict tests remain expected failures under their existing owner records.
- This is selected-scope qualification, not a full repository-suite or coverage measurement.
  No measured performance improvement is claimed. No deployment, publication or package version bump.
