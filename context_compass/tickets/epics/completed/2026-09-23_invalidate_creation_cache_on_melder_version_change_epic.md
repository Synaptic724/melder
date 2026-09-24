# Epic: Automatically invalidate creation caches when the Melder release changes

## Metadata
- Epic ID: EPIC-2026-09-23-invalidate-creation-cache-on-melder-version-change
- Status: done
- Owner: user
- Agent Name: updater_0
- Authored by: updater_0
- Priority: p1
- Created: 2026-09-23T23:55:20Z
- Updated: 2026-09-24T09:52:40Z
- Completed: 2026-09-24T09:52:40Z
- Summary: Release-bound creation-cache admission shipped in source for 0.2.51; schema 9 and regressions qualified.
- Target Window: unscheduled
- Related Program/Initiative: persisted creation plans and release compatibility

## Problem / Opportunity
A Melder package-version bump does not currently invalidate the persisted conduit creation cache.
CachingSystem stores a separate compatibility version (currently 8), the Python interpreter cache
tag, frame/conduit names and spell-ID-keyed payloads. It does not store the installed Melder release.

A compiler or hydration change can therefore leave an old cached plan eligible when its spell ID
and cache compatibility version are unchanged. Maintainers must currently remember to advance the
separate cache version for such changes. The owner wants every package-version change to provide
an additional automatic safety boundary.

Source evidence:
- src/melder/__version__.py:1-12
- src/melder/utilities/caching_system/caching_system.py:120-131
- src/melder/utilities/caching_system/caching_system.py:456-576
- src/melder/aether/spellbook/spellbook_creation_system.py:412-517

## MRP Alignment
Make release upgrades predictable: a new installed release cannot execute a persisted plan from
a different release. Preserve the existing cold-cache rebuild path and warm-cache behavior.

## Ticket Contract
- ENTRY_GATE: Owner selects implementation; source and regression contracts are read and any
  required cache-policy patch documents exist before runtime changes.
- EXECUTION_BOUNDARY: Release stamp on persisted creation-cache envelopes, read/write validation,
  focused tests and associated documentation. This authoring pass does not implement the feature.
- DEPENDENCIES: Canonical package version, CachingSystem, conjure cache classification and emission.
- EXIT_GATE: Release mismatch and missing stamps reliably rebuild cold; same-release reuse remains;
  focused tests and public compatibility documentation are complete.
- FAILURE_ESCALATION: Record version-import cycles, legacy-reader compatibility or any need for
  per-meld checks. Do not solve cache invalidation by deleting unrelated persisted records.

## Goals
- Add the running Melder release to persisted creation-cache identity.
- Require an exact release match before accepting any spell payload from a bundle.
- Rebuild automatically through the existing cache-miss path when the release differs.
- Keep the independent cache-format/semantic version and interpreter checks.
- Keep ordinary meld execution free of additional version checks, locks or file access.

## Non-Goals
- Implementation during epic authoring.
- Changing spell IDs, binding fingerprints, lifetimes, ownership or resolution semantics.
- Live module reload or observing edits to __version__.py inside an already-running process.
- Automatic package-asset generation in installed user environments.
- Flushing application objects or deleting Crystallizer checkpoints, formations or research history.
- Moving compiler phases to Mojo, introducing an IR, or claiming the separate compiler epic.

## Scope Boundaries
| Surface | Intended work |
| --- | --- |
| Conduit creation .melc bundles | Add and enforce the canonical Melder release stamp |
| Cache schema/semantic version | Retain independently; advance once for the required envelope field |
| Conjure/cache emission | Reuse existing miss, compile, staging and atomic emission paths |
| Bind-guard/agent-documentation accelerator caches | Verify their existing manifest-change invalidation across a release; record any separate gap |
| In-memory contexts | Remain tied to the running installed code; no release polling during meld |
| Crystallizer durable records | Preserve their independent RecordVersion compatibility policy and contents |

The asset-accelerator verification is bounded: those caches already compare manifest size/mtime,
interpreter tag and their own format version. Shipped manifests remain an explicit build/CI duty.
Do not broaden this epic into a cache-system rewrite.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner-authorized cache implementation, qualification and release closeout are complete.

## Requirements
- Read the canonical release from melder.__version__; do not copy a version constant into the cache.
- Stamp a named field such as melder_version on newly created and written cache envelopes.
- Accept only an exact matching release string, including patch/prerelease changes and downgrades.
  No SemVer compatibility inference or newest-version ordering is needed.
- Missing, malformed or differing release stamps produce a cold cache through the existing loader
  failure path. Never relabel old payloads with the current release to make them appear compatible.
- Advance the cache envelope compatibility generation when introducing the required stamp, so an
  older reader cannot ignore the new field and reuse a bundle written by the new implementation.
- Keep CACHE_VERSION_HISTORY/CURRENT_VERSION separate. They still document schema and semantic
  changes, including compiler changes made without changing the package release.
- Retain interpreter cache-tag, conduit identity and payload validation. Release equality is an
  additional condition, not a replacement for existing validation.
- Reject the entire mismatched bundle before payload selection or executor hydration.
- Reuse the existing cache path and atomic write behavior initially. No recursive cache-directory
  deletion, background cleaner or version polling is needed.
- A cold rebuild must respect disabled caching and existing error/write-failure behavior.
- Avoid importing the package root merely to read its version, and verify the normal import order.
- Read/check the release at initialization/load and emission boundaries, never on every meld.

## Constraints / Tradeoffs
Every package release deliberately causes a cold creation-plan build when an older bundle occupies
the same cache location, including releases whose changes are documentation-only. This is the
accepted safety tradeoff proposed here; subsequent same-release runs can reuse the refreshed cache.

A version change rejects reuse; it does not proactively rebuild every file on disk. A bundle is
recreated when that cache is next used and fresh payloads are successfully emitted. Reusing one path
across processes running different releases can cause repeated cold misses, but must never permit
cross-release reuse. Version-specific directories can be considered separately if this becomes a
measured operational problem.

## Required Reading Before Implementation
Start with src_architecture and indexed src_components sections for Spellbook Core, SpellCompiler
and Validation Pipeline, and the cache/asset owners; verify graph index ranges before using them.
Read the actual implementation units below. Existing source findings are leads, not a replacement
for checking the source at implementation time.

- src/melder/__version__.py
- src/melder/utilities/caching_system/caching_system.py
  Read initialization, _build_empty_cache_data, _load_or_initialize_from_disk,
  _normalize_loaded_cache_data and _write_current_cache_to_disk_locked in particular.
- src/melder/aether/spellbook/spellbook_creation_system.py
  Read conjure, _build_conjure_cache_state, _load_cached_creation_contexts_for_conjure,
  _stage_spell_payloads_at_conjure_end and _emit_conduit_cache_file_at_conjure_end.
- src/melder/aether/spellbook/spellbook.py
  Read _get_or_create_caching_system, _emit_spell_cache and _emit_cache_file_if_required.
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py
  Its PACKAGE_VERSION is an envelope format number, not the Melder package release.
- src/melder/utilities/caching_system/asset_cache.py
- src/melder/_build_assets/_build_asset_runner.py
- tests/unit/melder/utilities/test_caching_system.py
- Existing conjure/cache integration tests selected through the test-component map.

## Concrete Implementation Plan (source investigation complete)

The proposed runtime patch is confined to one file:
`src/melder/utilities/caching_system/caching_system.py`.

| Location | Proposed change |
| --- | --- |
| Imports | Import __version__ directly from melder.__version__, never from the public melder facade |
| CACHE_VERSION_HISTORY | Add generation 9 (unless another change advances it first), documenting the required release stamp |
| _build_empty_cache_data | Add melder_version with the canonical imported release |
| _normalize_loaded_cache_data | Require a matching release before adopting payloads; preserve the accepted stamp in the returned dictionary |
| _write_current_cache_to_disk_locked | Persist the stored envelope's melder_version alongside its existing metadata |
| Class/method contracts | Document release mismatch as a cold cache and the distinct schema/release checks |

Preserving the field in normalization AND emission is essential. Both methods construct new dictionaries
from explicitly named keys, so adding a stamp only to new-cache initialization would lose it on reload.
Use the existing _cache_data dictionary; no additional slot, version-provider object or public argument
is needed. Normal package initialization already imports the small version module before Aether.

Reject a missing/mismatching/malformed release with the existing load-validation failure mechanism.
_load_or_initialize_from_disk already catches load/validation failures and installs a fresh empty
cache. The normal conjure path then sees missing payloads, runs plan phases and stages/emits the new
bundle. No new invalidation branch is needed in Spellbook, compiler phases, Meld or CreationContext.

Keep the writer's stored, validated stamp. Do not rebuild a mismatched old payload dictionary and
stamp it with the new release. A library version is fixed for a running process; hot-swapping that
version or retaining a previous-version CachingSystem through a synthetic monkeypatch is not a
supported runtime upgrade model.

### Test changes

1. tests/unit/melder/utilities/test_caching_system.py
   - Assert the emitted release field and acceptance of a matching populated bundle.
   - Write marshal data to frame/conduit.melc and vary one field at a time for release mismatch,
     absent release, malformed release, Python tag, schema generation, conduit and payload failures.
   - Replace the stale JSON/wrong-path invalid-bundle fixtures; their current passing results do
     not demonstrate validation. Keep checks limited to contracts the loader actually enforces.
   - Verify that a cold reset followed by fresh payload emission produces a current reloadable bundle.
2. tests/integration/melder/spellbook/test_cache_schema_version_integration.py
   - Add the new documented generation and include the release stamp in the current-format fixture.
   - Continue proving older generations reset and the current generation accepts its populated payload.
3. tests/integration/melder/spellbook/test_cache_runtime_integration.py
   - Extend the existing automatic/dynamic first-run and second-run controls with a changed release.
   - Keep identical binding IDs and schema generation while changing the release, then observe the
     planner boundary and forbid stale payload publication during the mismatch run.
   - Verify emitted metadata, correct meld behavior and warm reuse on a subsequent matching run.
   - Cover upgrade/downgrade/prerelease mismatch and disabled caching without editing __version__.py.

Tests may patch the imported version binding at the loader module boundary while constructing a NEW
cache/runtime for the simulated release. No production version override parameter or provider framework.
Prefer public outcomes and counting a real planning boundary over only checking private attributes.

### Existing paths left intact

- Spellbook._get_or_create_caching_system selects one utility for the same frame/name cache path.
- _build_conjure_cache_state sees the empty store produced by rejection and follows its existing miss path.
- _stage_spell_payloads_at_conjure_end and _emit_cache_file_if_required write the refreshed envelope.
- Nested spell payload bytes and family-specific package/manifest versions are unchanged.
- Asset accelerator caches retain their existing manifest-change rules and release-stamped build checks.
- Durable Crystallizer records retain their existing independent compatibility and data.

### Qualification and documentation

Run the modified unit/schema/runtime tests, plus existing cache component/runtime-verification and
package-version metadata tests. A fresh-process import smoke check covers the additional leaf-module
import. This discovery pass did not execute tests or measure timing.

Update the scoped cache compatibility narrative/descriptors and public next-release notes after the
implementation qualifies. Regenerate documentation indexes/graph as appropriate. Finish source,
test and tracking edits before the final package/LLM build runners and checks; create no asset-only task.

Discovery evidence:
- src/melder/__init__.py:51-62
- src/melder/utilities/caching_system/caching_system.py:455-576
- src/melder/aether/spellbook/spellbook.py:908-1064
- src/melder/aether/spellbook/spellbook_creation_system.py:412-517
- src/melder/aether/spellbook/spellbook_creation_system.py:1021-1137
- tests/unit/melder/utilities/test_caching_system.py:238-387
- tests/integration/melder/spellbook/test_cache_schema_version_integration.py:1-75
- tests/integration/melder/spellbook/test_cache_runtime_integration.py:136-442

## Milestones
- [x] Confirm the envelope/import contract and capture failing release-mismatch regressions.
- [x] Add the release stamp and validate it at the existing load boundary.
- [x] Qualify same-release reuse, cross-release rebuilding and legacy compatibility.
- [x] Document the public upgrade behavior and regenerate assets after all final edits.

## Planned Stories
All three delivery slices were completed in TASK-2026-09-24-implement-release-version-cache-invalidation.

- [x] Cache compatibility contract and regressions: precise version source, legacy policy,
  initialization/emit consistency and failing tests before the implementation.
- [x] Envelope implementation: stamp, read validation and compatibility-generation update, with
  existing interpreter/identity/format checks and no hot-path work.
- [x] Runtime qualification and release guidance: normal conjure cold/warm paths, supported cache
  families, bounded accelerator verification and public release notes.

## Acceptance Criteria
- A bundle stamped with the current release can be reused when other existing checks pass.
- Changing only the release while retaining identical spell IDs and cache-format generation makes
  the bundle cold. Cover an upgrade, downgrade and prerelease difference.
- A legacy bundle without the release field is rejected safely, with no old executor invocation.
- New writes always carry the running release and current cache compatibility version.
- Readers from before the required-field change reject newly generated envelopes by schema version.
- Existing Python-tag, malformed-bundle and disabled-cache behavior remains correct.
- A rebuilt cache is reused on the next same-release conjure; no continuing rebuild loop is introduced.
- Existing runtime/hook/scope behavior remains unchanged and no per-meld version lookup is added.
- Durable Crystallizer data is neither deleted nor re-versioned by creation-cache invalidation.

## Validation / Test Approach
- Unit tests for matching/mismatching/missing/malformed release stamps, retained format checks,
  interpreter mismatch and emitted metadata.
- Behavioral integration: create a cache, change the simulated installed release at a controlled
  version-provider boundary, reconstruct the same definitions, and prove fresh planning occurs.
- Same-release control: prove the existing cache-hit path still avoids the normal plan rebuild.
- Exercise normal named-conduit cache paths and supported manifest families without requiring a
  literal pip upgrade or changing the repository's package version inside tests.
- Inspect the ordinary meld path for unchanged work; run the appropriate existing cache tests.
- Validation for this planning pass: source reading only. No tests or runtime changes are claimed.

## Risks / Mitigations
- Added version import creates a bootstrap cycle: use the small canonical version module and test import.
- Older readers ignore the new field: advance the envelope compatibility generation when it is added.
- Newly stamped old payloads appear current: reject before adoption, then build a fresh empty envelope.
- Unexpected extra startup cost: measure cache-load/conjure impact; no per-meld checks.
- Broad cleanup destroys user data: never delete persistence records or unrelated cache directories.

## Applicable Anti-Patterns
- [x] No compatibility inferred from release ordering.
- [x] No automatic rewriting of old payload metadata to bypass incompatibility.
- [x] No package version duplicated into another manually maintained constant.
- [x] No per-meld filesystem/version check.
- [x] No runtime implementation before the owner selects it.

## Decision Log
- Owner requests release-version changes to automatically invalidate cached plans for safety.
- Recommendation: exact release equality plus the existing independent cache compatibility version.
- Owner authorized runtime implementation, epic completion, version 0.2.51 and public release notes.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- Promoted contracts and qualification evidence are retained by tickets/tasks/completed/2026-09-24_implement_release_version_cache_invalidation_task.md.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes
- DATETIME: 2026-09-24T09:52:40Z
  TYPE: DECISION
  CLAIM: The authorized feature and release closeout are complete. Generation 9 stores and enforces
    the canonical Melder release; legacy/malformed/mismatched bundles rebuild through existing paths.
    Final package version is 0.2.51. Three test files, canonical cache documentation/descriptors and
    the focused public next-release draft are updated. The old 0.2.50 release is preserved.
  EVIDENCE:
  - artifacts/cache_release_guard_20260924/validation.md:1-51
  - artifacts/cache_release_guard_20260924/final_version.log:1-3
  - artifacts/cache_release_guard_20260924/final_metadata.log:1-2
  - artifacts/cache_release_guard_20260924/documentation_and_scope.json
  IMPACT: 138 unique final-version tests qualify across the 137-case run and deferred asset stamp
    check. All package/LLM checks passed. Source comparison isolates the cache owner and version
    metadata; only the reread cache class was semantically accepted. Turn in the epic/task and
    archive promoted patch contracts. All feature inputs are tracked; the final LLM build uses
    its normal tracked-input mode, leaving the unrelated untracked performance experiment outside it.
  NEXT: Rerun both builders and their checks after this final tracking update, with no subsequent edits.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T00:59:25Z
  TYPE: FACT
  CLAIM: The complete cache owner, version module/import order, Book/conjure load/write paths and
    existing unit/schema/runtime controls support a one-runtime-file change. Initialization,
    normalization and emission all need the new field; the latter two otherwise drop it. The
    existing mismatch-to-empty path already drives cold compilation and ordinary cache emission.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:455-576
  - src/melder/__init__.py:51-62
  - src/melder/aether/spellbook/spellbook.py:908-1064
  - src/melder/aether/spellbook/spellbook_creation_system.py:1021-1137
  IMPACT: No new hot-path work, public API or compiler orchestration is needed. Three existing test
    files provide the main repair/regression surfaces; the stale invalid-file fixture must be corrected.
    Asset and durable-record caches retain their distinct policies. No runtime or test edits yet.
  NEXT: Owner reviews the concrete implementation plan before the runtime patch begins.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T00:55:46Z
  TYPE: FACT
  CLAIM: The existing invalid-bundle unit matrix writes frame-a/root/bundle.json, while the real
    CachingSystem reads frame-a/root.melc using marshal. Those cases currently exercise a missing
    file rather than their named rejection branches. New release-version tests must write the real
    envelope/path and include a populated accepted control before mutating individual fields.
  EVIDENCE:
  - tests/unit/melder/utilities/test_caching_system.py:300-389
  - src/melder/utilities/caching_system/caching_system.py:176-186
  - src/melder/utilities/caching_system/caching_system.py:471-547
  IMPACT: Include a bounded repair of these loader tests in the feature test work. Assert existing
    supported rejection contracts; do not introduce unrelated key-validation policy from stale labels.
  NEXT: Read the existing schema/runtime integration controls and package import order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T00:55:10Z
  TYPE: DECISION
  CLAIM: Owner requests reading the epic and determining how to implement it. Investigate the
    cache envelope, version import, current tests and the minimum source/test/documentation scope.
    This is discovery and planning only; no runtime or test implementation is authorized yet.
  EVIDENCE:
  - Owner's current investigation instruction.
  - src/melder/utilities/caching_system/caching_system.py:456-576
  IMPACT: Assign this discovery to updater_0. Reuse the already-read source trace, then close the
    remaining import/test-fixture questions. The separate compiler IR epic remains unclaimed.
  NEXT: Read existing cache tests and package initialization, then record the exact change map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T23:55:20Z
  TYPE: FACT
  CLAIM: The persisted creation-cache header has version/python/frame/conduit fields but no Melder
    release field. CURRENT_VERSION is 8. Load validation rejects incompatible versions and the
    existing load exception path resets the in-memory cache for recompilation.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:120-131
  - src/melder/utilities/caching_system/caching_system.py:456-576
  - src/melder/aether/spellbook/spellbook_creation_system.py:412-517
  IMPACT: Package-version changes alone do not currently fence previously emitted creation plans.
  NEXT: On implementation selection, write the release-stamp regression and required patch contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T23:55:20Z
  TYPE: DECISION
  CLAIM: Owner requests an epic for release-triggered cache invalidation. Record a fail-closed,
    exact-release envelope check while preserving separate format/interpreter checks and all
    durable records. No runtime implementation or package version change is authorized by this epic pass.
  EVIDENCE:
  - Owner's current safety-policy and epic request.
  - src/melder/__version__.py:1-12
  - src/melder/utilities/caching_system/asset_cache.py:151-247
  IMPACT: A one-time cold build on any changed release trades startup reuse for predictable safety.
  NEXT: Owner selects the implementation slice; no work is claimed automatically.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Implementation evidence reviewed.
- [x] Acceptance criteria confirmed.
- [x] Documentation and tracking synchronized.

## Noting Behavior
Keep cross-story decisions and tradeoffs here; record detailed implementation evidence in child tasks.

## Context / Handoff Summary
Completed under the owner implementation/release instruction. CachingSystem admits only the exact
Melder release, current format generation 9 and existing interpreter/conduit/payload requirements.
Normal cache miss/rebuild paths remain authoritative. Release 0.2.51 and public next-release notes
are ready. See the completed implementation task and artifacts/cache_release_guard_20260924/.
Final asset generation/checks follow this turn-in with no later edits. The compiler IR epic is unchanged.
