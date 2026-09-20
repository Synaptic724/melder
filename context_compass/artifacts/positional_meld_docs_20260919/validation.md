# Positional meld documentation validation

Task: tickets/tasks/2026-09-19_document_positional_meld_calls_task.md.
Validation recorded: 2026-09-19T21:56:08Z.

## Change

- Audited 204 publication inputs through codemod.py.
- Replaced 150 occurrences across 65 published lesson/helper scripts and one package quickstart.
- README already used positional targets and needed no edit.
- Preserved explicit spell_id, spellframe, binding_name, override and bind(spell=...) usage.
- Python AST verification allows only the leading keyword-to-positional transformation and the
  same correction inside documentation/code strings. Original encoding and line endings are preserved.
- Second and final codemod checks report zero changes. The complete scoped diff was reviewed.

## Documentation checks

- Existing documentation tests: 39 passed.
- Strict Sphinx HTML build: 294 pages passed, with warnings treated as errors.
- Site check: 294 authored/generated pages, 35,501 local links and matching downloaded sources passed.
- Publication audit: 360 HTML files (including source/support pages), 557 code blocks, 137 Python
  downloads and four example archives containing 137 Python members have no old leading spell= calls.
- Source build assets and src/other LLM corpora regenerated with the repository builders.
- Asset checks pass against checkout version 0.2.43; src/other corpus fingerprints pass.
- Scoped git diff --check passed.
- Live Read the Docs publication was not performed; these are local source and build changes.

## Runtime example results and concurrent work

The four existing lesson harnesses ran on Python 3.14.7 free-threaded with PYTHON_GIL=0:
130 passed and three failed in 25.84 seconds.

- Expert 05 (unchanged): PermissionError removing a Windows temporary directory.
- Expert 09 (unchanged): checkpoint-cache membership assertion after flush.
- Expert 27 (one positional-call edit): checkpoint-cache membership assertion after flush; its
  earlier meld and subsequent world/codegen steps completed.

The owner confirmed another runtime change is in progress. The two cache failures remain
unattributed; this documentation task makes no runtime-green claim and changes no runtime behavior.
Their traces are retained in examples.log/examples.xml. No runtime repair was attempted here.

## Evidence

- changes.json and documentation.diff: complete changed-file inventory and reviewed diff.
- idempotence.json: no remaining edits on the same publication inputs.
- docs-tests.log, html-build.log, site-check.log: executed documentation checks.
- publication-audit.json: rendered code/download/archive sweep.
- source-assets-build.log, source-assets-check.log: builder and freshness results.
- corpora-build.log, corpora-check.log: derived corpus refresh and verification.
- examples.xml and examples.log: the complete example result, including the three failures.
