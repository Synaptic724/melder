# Provider artifact ownership repair

Task: TASK-2026-09-13-repair-provider-artifact-ownership
Status: implemented; owner review pending.

## Owner decision
Retain Melder's current unique-only supplied-object model. Retire the broader reference/lifetime
redesign and fix the concrete artifact bug. The retired epic, discovery story and two discovery tasks
are archived under completed with disposition retired_by_owner, preserving findings and unimplemented
proposals as history. Existing Protocol repair records remain linked to the concrete repair program.

## Mechanism and repair
Phase 5 previously attached artifacts to all visible Spells. Attachment clears later executable
artifacts and creation contexts. A borrower could therefore erase its provider's plan, while its own
planning queue rebuilt only owned Spells. Target-local compilation had the same mismatch for dependencies
in the same book: it rebuilt only the target after invalidating the entire dependency closure.

CompilerPhase5 now receives explicit publication_spell_ids in its attachment helper:
- Conduit-wide passes publish to the book's owned _spells_by_id keys.
- Local passes publish only to their selected target.
- The complete visible/scoped graph and index remain available for consumer analysis and validation.
- Unselected dependency Spells retain their executable artifacts and contexts.
- Selected Spells still invalidate their old outputs and rebuild through the established pipeline.

Only compiler_phase_5.py changes production behavior. No external-object registration, lifetime,
disposal, ownership-transfer API, cache-version or validation-bypass changes. No new xfail markers.

## Evidence
| Run | Result | Files |
| --- | --- | --- |
| Original native baseline | 7 failed, 6 passed | repair_20260919_red.log/xml |
| Added same-book local baseline | 1 failed, 13 deselected | local_single_20260919_red.log/xml |
| Focused patched native/unit selection | 29 passed | repair_20260919_green.log/xml |
| Extended compiler/contract/spellbook selection | 935 passed, 2 skipped, 3 pre-existing xfailed, 1 non-strict xpassed; 8 tmp fixture errors | repair_20260919_extended.log/xml |
| Eight cache cases rerun outside Windows sandbox | 8 passed | cache_20260919.log/xml |
| Original unchanged CommandOps provider acceptance | 9 passed | commandops_20260919.log/xml |

The extended selection has zero assertion failures. Its eight fixture errors were Windows temporary
directory access failures, also seen with a new workspace basetemp. The isolated unsandboxed rerun
resolved that environment issue. Combined ordinary native passes: 943. The existing expected-failure
markers are in test_spellbook_integration_di_validation_faults.py and were not changed here.

The original CommandOps test includes real GraphCache/PolicyEngine injection, all eight independent
prefixes, retained graph data and provider use before and after borrower cleanup. It ran on CommandOps'
existing .venv314 (Python 3.14.7 free-threading) with process-local PYTHONPATH selecting this Melder source.
No package installation or environment replacement occurred.

The preliminary three-identical-consumer same-book variant hit the existing duplicate-name rule;
local_20260919_red.log preserves that setup observation. The permanent minimal single-consumer case
reproduced the artifact bug and passes after repair.

## Reproduction commands
From melder_private:

```powershell
.venv_new/Scripts/python.exe -m pytest tests/integration/melder/spellbook/test_provider_artifact_ownership.py tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5_local.py -q -p no:cacheprovider
.venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/spell_compiler tests/component/melder/spellbook/spell_crafter/phases/test_spellbook_component_spell_crafter_phase5.py tests/component/melder/spellbook/test_spell_compiler_component_system.py tests/integration/melder/spellbook tests/component/melder/aether/conduit/test_conduit_component_spell_contracts.py -q -p no:cacheprovider --tb=short
```

For downstream acceptance, use its existing interpreter, disable bytecode writes, prepend this checkout's
src and CommandOps src to process-local PYTHONPATH, and select its unchanged
tests/component/spectrum/test_linked_commandops_providers.py. Store reports in this task's artifact folder.

## Documentation and assets
Architecture/components describe publication authority; their indexes are rebuilt. The canonical
extractor/merge refreshed only the Phase-5 descriptor; the class semantics were re-read and accepted.
Source extent is measured at 709 lines. Graph/index, source assets and repository bundles are regenerated.
All baseline nonblank normalized architecture/component lines remain present; additions are scoped to
this compiler boundary. Pre-existing whole-document quality/portability issues remain outside this repair.

Source and touched tests pass E9/F63/F7/F82 correctness checks. git diff --check passes.
Full repository suite, coverage and broad concurrent ownership-transfer qualification: Not run.

## Review boundary
Repair delivered locally at version 0.2.40. No release, replacement wheel or publication is included.
The original regression assertions stay intact. Formal repair-ticket closure awaits owner acceptance.

## Component follow-up (2026-09-19T13:30:00Z)
Owner's full run exposed an old expectation in test_spellbook_component_spell_crafter.py: it required
local consumer compilation to publish a blueprint onto its dependency. That expectation contradicts the
repaired publication boundary. The earlier selected suite omitted this component file.

Updated the test/docstring and parameterized absent versus real precompiled dependency artifacts.
Both cases require the provider node in the consumer index and preserve the provider's existing
blueprint, system index and codegen references. The uncompiled case preserves None. No runtime edit.

- Exact old case reproduced: component_followup_red.log/xml.
- Entire reported file plus native ownership tests: 31 passed; component_followup_focused.log/xml.
- Entire Spellbook component tree: 491 passed; component_followup_full.log/xml.
- Test corpus regenerated; all three corpus checks pass; component_followup_bundle_check.log.
- Source asset check and scoped correctness lint pass. Diff check passes with cr-at-eol enabled
  for this existing CRLF file; default Git whitespace checking otherwise reports CR characters as trailing
  whitespace. No repository Git configuration was changed; the file's existing CRLF convention is preserved.
