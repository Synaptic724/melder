# Approved 0.2.50 asset rebuild

The owner requested completed epic turn-in, cleanup and asset regeneration on 2026-09-23.
That instruction releases the prior generation hold. The named-lesser delivery tickets were
already closed; this pass also closed the accepted private-guard follow-up before building.

## Generated outputs

- Standard Melder runner: agent documentation (452 entries), bind guard (631 entries), and
  system documents (four records). Eight generated Python files changed: three primary manifests,
  document index, graph adjacency, and architecture/components/graph payloads.
- LLM source, tests and other bundles, their three indexes and shared manifest: seven outputs.
  Inputs include 587 source files, 851 test files and 366 other files.
- Version stays 0.2.50. No runtime edits, dependency changes, wheel or publication.

## Commands and results

```powershell
.venv_new/Scripts/python.exe src/melder/_build_assets/_build_asset_runner.py
.venv_new/Scripts/python.exe src/melder/_build_assets/_build_asset_runner.py --check
.venv_new/Scripts/python.exe llm_support/_builder.py --include-untracked
.venv_new/Scripts/python.exe llm_support/_builder.py --include-untracked --check
```

All three packaged checks and all three corpus checks pass. Use the local LLM flag until the
eleven new delivered files are tracked: two hierarchy source modules, seven named-feature tests
and two tutorials. It includes their actual working-tree contents without staging or committing.
Normal CI sees the same corpus once those files are added. ContextCompass state is excluded.

The existing asset/document/LLM selection passed 252 tests and skipped one import-isolation case
because Melder was already imported in that process. Running that single case in a fresh process
passed, giving 253 unique passing tests. No failing tests. Full-repository suite/coverage: not run.

Tests: tests/unit/melder/build_assets, tests/unit/melder/test_system_documents.py,
tests/unit/melder/test_system_document_view.py, and tests/unit/llm_support. XML and logs retain
the exact outcomes. Windows temp-file tests ran with approved sandbox escalation and fresh
workspace-contained basetemp paths; temporary test trees were removed after execution.

Source preservation compares 595 Python/stub files before and after. Only the eight expected
generated files changed, with no missing/new runtime file. See preservation.json.

The release draft replaces the historical hold with the completed build result. Its updated
content is included in the final LLM other bundle. Logs, hashes and test receipts are retained;
unrelated epics and other agents' active work remain unchanged.
