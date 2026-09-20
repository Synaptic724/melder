# S3 compiler validation

Owner: updater_0. Recorded: 2026-09-19T21:38:00Z.
Ticket: `tickets/tasks/completed/2026-09-19_implement_override_required_compiler_task.md`.

## Delivered boundary

OVERRIDE_REQUIRED is a resolved socket policy. Declaration/default facts remain unchanged;
descriptive reference IDs are separate from executable target IDs. Non-resolvable definitions
retain descriptive topology without executable roots or Phase8-11 construction plans.

Injection/model/planner data carries immutable `required_override_params` rows in both variants:
`(parameter_name, position, parameter_kind_name, referenced_spell_ids_tuple)`.
Injection IR/signature export preserves the new metadata. Existing frame-key watching and the
structural-to-resolution validity handoff rebuild changed consumer plans through normal machinery.

This is compiler qualification. Direct/reuse/fast/cached refusal and supplied-value enforcement
remain S4 work. Nexus graph/history is S5; crystal capture/restore/graft and durable compatibility
are S6. The feature is not ready for release.

## Executed tests

Environment: `.venv_new`, Python 3.14.7 free-threaded, `uv run --no-sync --offline`, `-X gil=0`.
Pytest cacheprovider was disabled; uv cache and reports are task-owned.

| Report | Passed | Failed/errors | Pytest elapsed |
| --- | --- | --- | --- |
| `expanded_compatibility.log` / `.xml` | 1961 | 0 / 0 | 4.11s |
| `remaining_compatibility_green.log` / `.xml` | 137 | 0 / 0 | 0.64s |

The two XML case sets have zero overlapping `(classname, name)` keys: **2098 distinct cases**.
The expanded set contains all 42 cases in the new compiler component file.
The remaining set covers eight additional files for creation-system fast paths/chunking, state
objects, multithreaded state behavior, and the resolution-style matrix.

Earlier red reports are retained as reproduction evidence, not current failures. The task notes
identify fixture-only failures separately from actual missing feature behavior.

## Generated assets and style

- Source build wrote 452 agent-documentation entries, 629 guard entries, and four system documents
  for version 0.2.40. `check_source.log` confirms all three asset families are current (exit 0).
- LLM build recorded 585 source files and 826 test files. `check_llm.log` confirms src/tests/other
  fingerprints and output proofs match (exit 0). Build/check used `--include-untracked` so the new
  component test is included without staging unrelated work.
- `check_style.log`: new component file plus the three retained Python tools pass Ruff (exit 0).
  The command excludes UP045 because the selected role requires Optional/Union. No lint config
  or suppression comments changed; this is not a repository-wide lint result.
- Whitespace check exits 0 using `core.safecrlf=false` and the existing-CRLF allowance
  `core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol`.
- Architecture and component indexes pass check mode. Graph assembly check verifies all 591
  section ranges against their headers. The S3 mechanical refresh touched 22 source descriptors;
  authored deltas were scoped to this change. No whole-class semantic re-audit is claimed for
  larger source owners. `doc_line_changes.json` records replaced documentation lines.

## Exact check commands

```powershell
uv run --no-sync --offline python -X gil=0 src/melder/_build_assets/_build_asset_runner.py --check
uv run --no-sync --offline python -X gil=0 llm_support/_builder.py --include-untracked --check
uv run --no-sync --offline ruff check --no-cache --ignore UP045 tests/component/melder/spellbook/test_spellbook_component_override_required.py context_compass/artifacts/override_required_compiler_20260919/probe_revalidation.py context_compass/artifacts/override_required_compiler_20260919/refresh_graph.py context_compass/artifacts/override_required_compiler_20260919/update_semantics.py
```

Set `UV_PROJECT_ENVIRONMENT` to the repository's `.venv_new` and `UV_CACHE_DIR` to this artifact
directory's `uv_cache` before reproducing. The XML reports enumerate the exact tested case sets.

## Limits and next consumer

Full repository suite, repository-wide coverage and full feature qualification: **Not run**.
No runtime supplied-value safety, complete nested transition matrix, persistence round trip,
performance improvement, or release-readiness claim follows from the compiler tests.

S4 must consume the plan metadata in live Phase11 `CodegenCreationSchemaHelpers`, emitted
executor families and cache hydration. It must independently cover every resolution door,
missing versus falsey supplied values, reuse, nested replacements and hook/side-effect order.
Read the S3 task and S4 story for the concrete source map before editing.
