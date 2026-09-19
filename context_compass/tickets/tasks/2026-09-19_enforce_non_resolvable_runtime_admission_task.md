# Task: Refuse non-resolvable registrations at runtime resolution doors

## Metadata
- Task ID: TASK-2026-09-19-enforce-non-resolvable-runtime-admission
- Story: STORY-2026-09-19-discoverable-resolution-runtime
- Status: review
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T21:45:00Z
- Updated: 2026-09-19T22:08:58Z

## Objective
Make direct resolution and reuse-only resolution refuse a selected Spell with resolvable=False
consistently through Conduit, SpellSpace, validation-skipping and memoized entry doors.

## Ticket Contract
- ENTRY_GATE: Owner explicitly approved continuing after S3; this task is routed from the board.
  Read S1 selector/runtime rules, S3's handoff, and component/graph/source call paths before patching.
- EXECUTION_BOUNDARY: Common target lookup/admission, ConduitMeld/SpellSpaceMeld dispatch, direct
  fast doors, existing error vocabulary, and focused public runtime regressions/docs/assets.
- DEPENDENCIES: Native Spell.resolvable and S3 compiler/root eligibility are implemented.
  A subsequent S4 task owns actual required-override execution across generated family lanes.
- EXIT_GATE: Selected False targets refuse with useful errors on all in-scope doors while ordinary
  resolvable targets, lookup/introspection and reuse retain their contracts; focused tests pass.
- FAILURE_ESCALATION: Trace each bypass before choosing placement. Do not weaken native contracts,
  redesign invalidation, or conflate direct refusal with required-input execution completion.

## Scope Boundaries
- In scope: real runtime resolution admission and its direct code/test/document owners.
- Out of scope: required-input value validation/emission, Nexus graph publication, crystal replay,
  supplied-object lifecycle redesign, named lesser conduits, releases or version changes.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Runtime admission, focused qualification and docs/assets are complete; input execution follows.

## Required Reading
- `tickets/stories/2026-09-19_discoverable_resolution_runtime_story.md`.
- S1 selector table and S3 implementation task handoff.
- Verified component slices: Meld Resolution Runtime; Creations and SpellSpace; compiler pipeline.
- Verified graph slices followed by complete relevant source call paths and direct callees.
- Tests architecture/components and the existing public meld/fast-door fixtures before adding tests.

## Steps / Checklist
- [x] Trace selected-target resolution, validation bypass, fast doors and scoped/reuse equivalents.
- [x] Record the exact admission/error contract in indexed patch documents and consume the mapping.
- [x] Add and run real public regression tests with False targets and True controls.
- [x] Implement the smallest shared refusal and any independently required fast-door enforcement.
- [x] Run focused runtime/compiler compatibility and preserve lookup behavior.
- [x] Update docs/assets and the remaining S4 required-input handoff.

## Deliverables
- Consistent runtime refusal, meaningful regressions and retained validation results.
- A precise handoff to S4 generated required-input enforcement.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/` entry/lookup owners and direct exception/door collaborators.
- Conduit/SpellSpace public entry methods only if their source requires an independent gate.
- Focused unit/component tests, matching source docs/graph/build assets and ContextCompass records.

## Validation
- 665 passed, one pre-existing owner-deferred test skipped, including all 58 new admission cases.
- Source/LLM asset freshness, new-file/helper Ruff and whitespace checks pass. Current build version
  is 0.2.43; this task did not modify the version. Full repository suite/coverage: Not run.
- Exact scope and limits: `artifacts/non_resolvable_runtime_admission_20260919/validation.md`.

## Risks / Rollback Notes
- A fast door may bypass common lookup/validation; admission must survive that route.
- Existing False construction-plan absence must not result in an accidental missing-artifact error.
- Other agents are changing documentation; preserve their board/source/build work.
- Keep S2/S3 and earlier owner-approved changes intact.

## Applicable Anti-Patterns
- [x] No policy inside an optional validation gate only.
- [x] No fallback provider when the explicitly selected registration is False.
- [x] No new ownership/invalidation model or introspection restriction.
- [x] No claim that direct refusal completes S4 supplied-value enforcement.

## Done Checklist
- [x] Runtime admission implemented and verified.
- [x] Required docs/generated assets updated.
- [x] Validation and successor handoff recorded; boards synchronized.
- [ ] Owner acceptance before closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- PATCH_ID: non_resolvable_runtime_admission_2026_09_19
- ARTIFACT_PATHS:
  - artifacts/non_resolvable_runtime_admission_20260919/
  - artifacts/non_resolvable_runtime_admission_20260919/validation.md
  - system_docs/patches/active/non_resolvable_runtime_admission_2026_09_19/architecture_patch.md
  - system_docs/patches/active/non_resolvable_runtime_admission_2026_09_19/component_patch_meld.md
  - system_docs/patches/active/non_resolvable_runtime_admission_2026_09_19/code_description_patch_admission.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted task closure; promote/archive temporary patch contracts normally.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: selected target, capability refusal, fast doors, scoped/reuse dispatch.
- IF_UNKNOWN: none

## Noting Behavior
Record complete call-path findings before the next tranche, with evidence and one concrete NEXT.

## Notes
- DATETIME: 2026-09-19T21:45:00Z
  TYPE: PLAN
  CLAIM: Owner approved S4 continuation. Start with one bounded runtime admission task; actual
    required-input enforcement remains a subsequent S4 unit so the distinct proof obligations stay clear.
  EVIDENCE:
  - tickets/stories/2026-09-19_discoverable_resolution_runtime_story.md:19-54
  - tickets/tasks/2026-09-19_implement_override_required_compiler_task.md:825-856
  IMPACT: Runtime work has a concrete entry scope; no source implementation or tests have begun.
  NEXT: Read selector decisions and relevant component/graph slices, then trace the direct runtime doors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:48:41Z
  TYPE: FACT
  CLAIM: Read the Meld base and both concrete runtime doors. Normal meld and reuse-only each resolve
    their target independently; lookup helpers also serve observational probes and must remain usable
    for False registrations. Both warm ID doors are success-only memoization after normal execution.
    An admission check before normalization, optional validity, hooks or reuse can prevent a False
    entry from ever reaching construction or fast-door insertion. Public facades delegate and preserve
    errors, so they do not need duplicate behavioral gates.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:143-613
  - src/melder/aether/conduit/meld/spellspace_meld.py:168-620
  - src/melder/aether/conduit/meld/meld.py:1262-1515
  - src/melder/aether/conduit/conduit.py:3967-4198
  - src/melder/aether/conduit/spell_space/spell_space.py:443-497
  IMPACT: Use one shared cold error helper and four selected-target checks. Verify immutable capability
    and version/epoch transitions before deciding whether warm guards require any additional read.
    MeldExecutionError already carries the exact target id/name; no new exception family is needed.
  NEXT: Read capability/epoch setters and actual fast-door tests, then record the patch and regression matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:54:14Z
  TYPE: DECISION
  CLAIM: Capability has no live setter and is a different False version identity; both fast doors
    are success-only. Enforce four selected-target checks using the native slot and one shared cold
    MeldExecutionError helper. False cannot mint a fast entry, so retain the existing warm guards.
    The public SpellSpace has meld only; its reuse-only door is internal SpellSpaceMeld and must be
    identified honestly in tests. Test-book caching will be disabled for the first refusal matrix.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:619-636
  - src/melder/aether/spellbook/spell.py:686-713
  - src/melder/aether/conduit/meld/conduit_meld.py:241-414
  - src/melder/aether/conduit/meld/spellspace_meld.py:261-422
  - src/melder/utilities/custom_exceptions/meld_execution_error.py:4-179
  IMPACT: A direct admission change can remain independent of input execution and preserve the warm path.
  NEXT: Consume the new indexed patch contracts and establish real runtime refusal regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:56:44Z
  TYPE: DECISION
  CLAIM: Patch contracts were read in architecture/component/control-flow order and indexed. Mapping:
    selected-target refusal -> four concrete-door checks and Meld's shared error -> real ID/name/frame,
    scoped/reuse and override/hook refusal tests; warm-entry invariant -> unchanged guard ladder ->
    existing fast-door regressions and True controls. Test component/bootstrap/fixture reads are complete.
  EVIDENCE:
  - system_docs/patches/active/non_resolvable_runtime_admission_2026_09_19/architecture_patch.md:7-37
  - system_docs/patches/active/non_resolvable_runtime_admission_2026_09_19/component_patch_meld.md:3-27
  - system_docs/patches/active/non_resolvable_runtime_admission_2026_09_19/code_description_patch_admission.md:3-19
  IMPACT: Admission implementation has a source-backed test/patch contract; supplied-input execution stays separate.
  NEXT: Add the real runtime admission component tests and capture their red baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:58:12Z
  TYPE: MEASURE
  CLAIM: All 58 new component cases fail on the current runtime. Failures are 20 missing-codegen
    errors, 34 structural/resolution validation errors, two missing-live ValueErrors, and two reuse
    calls returning the supplied existing object without refusal. The requested admission diagnostic
    is absent across both concrete doors. No constructor-side workaround is warranted.
  EVIDENCE:
  - artifacts/non_resolvable_runtime_admission_20260919/admission_red.xml:1-1
  - artifacts/non_resolvable_runtime_admission_20260919/admission_red.log:1-80
  IMPACT: The matrix reproduces actual missing runtime policy, including existing-object reuse.
  NEXT: Implement the shared error and four early selected-target checks, then rerun these cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:58:53Z
  TYPE: MEASURE
  CLAIM: The shared cold error and four selected-target checks are implemented. All 58 new public/
    real-door cases pass in 0.64s: exact selectors, both postures/scopes, optional validation bypass,
    supplied existing-object reuse, overrides/hooks, True provider controls and dynamic notch. Lookup
    probes remain usable; warm guard ladders are unchanged. No required-input executor work was added.
  EVIDENCE:
  - artifacts/non_resolvable_runtime_admission_20260919/admission_green.log:1-2
  - src/melder/aether/conduit/meld/meld.py:599-626
  - src/melder/aether/conduit/meld/conduit_meld.py:350-365
  - src/melder/aether/conduit/meld/spellspace_meld.py:366-379
  IMPACT: Direct admission now has the intended diagnostic before other runtime paths. Broader native
    fixture and fast-door compatibility still need qualification before this task enters review.
  NEXT: Run existing Meld/fast-door and conduit/compiler compatibility plus scoped style checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:00:07Z
  TYPE: MEASURE
  CLAIM: Broader admission/Meld/conduit/compiler/default qualification reports 631 passed, 34 failed
    and one existing owner-deferred shared-context test skipped. All 34 failures are two old _SpellStub
    factories lacking native _resolvable; their complete constructors were read. New tests and real
    fast-door cases pass. Ruff requests two import wraps and PEP604; preserve role-required Optional/
    Union by excluding UP045 and UP007 in the scoped command, without changing configuration.
  EVIDENCE:
  - artifacts/non_resolvable_runtime_admission_20260919/compatibility.xml:1-1
  - tests/unit/melder/aether/conduit/meld/test_meld.py:220-357
  - tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py:154-217
  IMPACT: Align fixture producers with the native Spell contract; do not add production fallback probes.
  NEXT: Add default True to the two stub constructors, wrap the new imports, and rerun this focused suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:02:11Z
  TYPE: MEASURE
  CLAIM: Focused compatibility is green after two native fixture updates: 665 passed, one existing
    owner-deferred shared-context test skipped, 4.11s. Scoped new-file Ruff passes with UP007/UP045
    excluded solely for role-required Union/Optional. Direct admission is ready for docs/assets.
    Mailbox notice from workflows_1 reports 65 positional-example docs and a doc-only __init__.py
    change; preserve it and include that module's mechanical descriptor hash in the graph refresh.
  EVIDENCE:
  - artifacts/non_resolvable_runtime_admission_20260919/compatibility_green.log:1-11
  - tickets/tasks/2026-09-19_document_positional_meld_calls_task.md
  IMPACT: No known failures remain in the tested groups. Other agent publication/build work must
    survive; required supplied-value execution is still the next S4 task, not completed by these tests.
  NEXT: Refresh scoped runtime docs/graph and generated assets, then route the required-input task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:08:27Z
  TYPE: FACT
  CLAIM: Scoped runtime prose/diagrams and C1 extents are updated; both indexes and graph were rebuilt.
    Three runtime descriptors plus workflows_1's doc-only root module were mechanically refreshed,
    preserving authored edges/stamps. The three runtime class stamps remain SEMANTICS_STALE; scoped
    additions are not a whole-class semantic re-audit. The source build passes against the current
    workspace version 0.2.43; this task did not change the version. Content comparison accounts for
    obsolete feature-status/C1 lines. Its one apparent unrelated Claims-line loss is a baseline
    PowerShell case-insensitive grouping collision: both case variants remain in the document.
  EVIDENCE:
  - artifacts/non_resolvable_runtime_admission_20260919/doc_line_changes.json
  - artifacts/non_resolvable_runtime_admission_20260919/build_source.log:1-3
  - system_docs/src_components.md:3425-3425
  - system_docs/src_components.md:3577-3577
  IMPACT: Runtime admission documentation matches its limited scope and preserves other agents' work.
    No whole-document quality audit, full-suite coverage or full S4 safety claim is made.
  NEXT: Refresh LLM outputs, verify assets/style, then record admission review and route required-input execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:08:58Z
  TYPE: MEASURE
  CLAIM: Admission delivery is in review with 665 passing cases and one existing deferred skip.
    Final source/LLM freshness checks pass; new-file/helper Ruff passes after an import wrap.
    Authored docs/indexes and scoped graph deltas are current for this boundary. Validation artifact
    records exact test scope, preservation proof and the unresolved required-input execution boundary.
  EVIDENCE:
  - artifacts/non_resolvable_runtime_admission_20260919/validation.md:1-55
  - artifacts/non_resolvable_runtime_admission_20260919/style_green.log:1-1
  IMPACT: Continue S4 without reopening direct admission or claiming full runtime/feature completion.
  NEXT: Execute tickets/tasks/2026-09-19_enforce_required_override_execution_task.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Admission is implemented and in review: one common error helper plus four native capability checks.
665 tests pass, one pre-existing owner-deferred test skips; all 58 new admission cases pass. Docs,
indexes, graph/build/LLM outputs and scoped style are synchronized. Read the validation artifact for
exact evidence and limits. Current workspace build version is 0.2.43; this task did not change it.

NEXT: the required-override execution task under S4. Consume required_override_params in live Phase11
export/emission/hydration, preserving omitted versus falsey values, reuse and whole-branch replacement.
Direct admission and compiler metadata do not prove those execution semantics. No full-suite/coverage,
Nexus/history or crystal-replay claim. Existing guard ladders and observation remain unchanged.

No agents; preserve S2/S3, earlier owner work and workflows_1's positional-example changes. The root
module's doc-only descriptor hash is refreshed; no whole-class semantic re-audit is claimed. Authoring
skills/examples were read; content-preservation baseline and replacement ledger are retained.
