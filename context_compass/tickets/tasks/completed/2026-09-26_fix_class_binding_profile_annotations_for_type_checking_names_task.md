

# Task: Keep class binding-profile annotations when a field names a TYPE_CHECKING-only type

- Completed: 2026-09-26T16:32:21Z
- Summary: Class binding profiles keep class-level annotations that name TYPE_CHECKING-only types (source text,
  the ClassInspector read), so those fields count in the spell id and appear in Nexus; affected classes get a
  new id once. Tests, docs, graph and release note done; owner accepted. Ships in 0.2.59+ (owner notches).

## Metadata
- Task ID: TASK-2026-09-26-fix-class-binding-profile-annotations-for-type-checking-names
- Story: none (fix for the defect left open by TASK-2026-09-26-keep-class-binding-annotations-with-type-checking-names)
- Status: done
- Owner: user
- Agent Name: melder_1
- Priority: p2
- Created: 2026-09-26T16:12:32Z
- Updated: 2026-09-26T16:32:21Z

## Objective
A class whose field annotations name a type imported only under `TYPE_CHECKING` loses every annotation from its
class binding profile (`BindingProfileStrategy._build_class_profile` falls back to `{}` on any exception). Keep
the annotations - unavailable names rendered as source text, as `ClassInspector` already does - so the spell id
reflects the class's annotated fields and Nexus publishes them. Affected classes get a new id once.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("ok keep working on stuff then please go ahead"), answering the
  recommendation to fix this defect with its one-time id change for affected classes.
- EXECUTION_BOUNDARY: `binding_profile_strategy.py` (the class-annotation read) and its tests; docs
  (src_components, src_architecture if the invariant text changes), the graph descriptor, the release note. Other
  agents' files untouched; no cache-generation bump unless investigation shows one is required.
- DEPENDENCIES: tickets/tasks/completed/2026-09-26_keep_class_binding_annotations_with_type_checking_names_task.md
  (investigation and prototype), SignatureReflection.class_annotations, Bind.sha256_profile.
- EXIT_GATE: Fix applied with tests; before/after probes; suites green on a worktree sync; docs, graph and release
  note current; owner reviews.
- FAILURE_ESCALATION: DECISION_REQUEST if the fix needs a cache-generation bump, touches another agent's file, or
  changes ids beyond the affected classes; CONFLICT if another lane is editing the same file.

## Scope Boundaries
- In scope: class binding-profile annotations for names unbound at runtime; the id consequence; Nexus binding detail.
- Out of scope: callable profiles, ClassInspector, the detailed profile, other exceptions than NameError.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved the fix and the one-time id change (2026-09-26T16:12:32Z).
- from_state: in_progress
- to_state: review
- transition_reason: Applied to the worktree; suites green on a worktree sync; docs, graph and release note
  current (2026-09-26T16:28:45Z).
- from_state: review
- to_state: done
- transition_reason: Owner accepted ("ok cool whats next?"); closure sync done (2026-09-26T16:32:21Z).

## Steps / Checklist
- [x] Re-read the class path, the fallback helper and every consumer in full on current source.
- [x] Patch lane (architecture + component) and implementation-to-validation mapping.
- [x] Implement on a VM copy with tests; before/after probes; unit, component and integration suites.
- [x] Apply to the worktree by anchored edit; docs, graph descriptor, release note.
- [x] Owner review.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Fixed `BindingProfileStrategy._build_class_profile` with tests; docs, graph and release note.

## Files / Paths Impacted
- src: spell_examiner/strategies/binding_profile_strategy.py.
- tests: test_binding_profile_strategy.py (+6 tests), test_binding_profile_strategy_future_annotations.py (one
  test moved to the new contract).
- docs: src_components, src_architecture (+indexes), graph descriptor, src_graph (+index), release note.
- Exact list: artifacts/class_binding_annotations_fix_20260926/results/commit_files.txt.

## Validation
- VM copy synced from the worktree plus the fix (3.14.7t, -X gil=0): unit melder 8202 passed, 4 failed (same on
  base); unit other dirs 44 failed + 388 errors (same on base; files absent from the copy); component 2135;
  integration spellbook 581, crystallizer 258, conduit 268, mutation_research + live_sim 67, aether 716,
  multithreading 42 passed. 4 new tests fail on unpatched source. Owner machine: Not run.
- Recommended commands:
  - `pytest tests/unit tests/component tests/integration` on 3.14t.

## Risks / Rollback Notes
- Ids of affected classes change once: their creation-cache plans rebuild on first conjure; crystallizer restore
  maps old ids to new; MutationResearch records a new version.
- Rollback: restore the file from git.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/class_binding_annotations_fix_20260926/
  - artifacts/class_binding_annotations_20260926/ (earlier probes and prototype, read-only)
  - system_docs/patches/completed/class_binding_annotations_2026_09_26/
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: ticket closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Class binding-profile annotations with names unbound at runtime.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T16:12:32Z
  TYPE: DECISION
  CLAIM: Owner approved the fix ("ok keep working on stuff then please go ahead", answering the recommendation:
    one-line NameError fallback to SignatureReflection.class_annotations, one-time id change for affected
    classes). The defect is still in current source: the class read in _build_class_profile ends in
    "except Exception: annotations = {}" and the file differs from HEAD only by line endings.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:69-146
  - context_compass/artifacts/class_binding_annotations_20260926/results/class_annotations_prototype.txt:1-78
  IMPACT: Scope approved; the earlier prototype is the starting point, re-verified against current source.
  NEXT: Re-read binding_profile_strategy.py, SignatureReflection.class_annotations, ClassInspector's fallback and
    Bind.sha256_profile in full; check active tickets and the mailbox for anyone writing these files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T16:14:02Z
  TYPE: FACT
  CLAIM: Re-read on current source. BindingProfileStrategy._build_class_profile reads
    inspect.get_annotations(cls, eval_str=True, globals=module dict) inside "except Exception: annotations = {}"
    (undocumented broad catch). ClassInspector._class_annotations already has the target shape: except NameError ->
    SignatureReflection.class_annotations(c), which reads the class's own annotations in FORWARDREF and renders
    unavailable names as source text (STRING format), never eval'ing quoted strings. Consumers of
    ClassBindingProfile.annotations: Bind.sha256_profile hashes the sorted KEYS only, and the Nexus descriptor payload
    publishes dict(annotations); no other reader. The fallback returns the same keys the eval read would, so only
    classes currently dropped to {} change id; all other ids are byte-identical. Tests: the only class-annotation
    failure test forces RuntimeError and asserts {} (still true under a NameError-only fallback); no test pins
    {} for a TYPE_CHECKING name. Earlier prototype (same change) kept all keys with unavailable names as text,
    left resolved values and unaffected ids unchanged, and stayed process-stable.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:68-146
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/class_inspector.py:150-173
  - src/melder/utilities/helpers/signature_reflection.py:152-188
  - src/melder/aether/spellbook/bind/bind.py:892-990
  - src/melder/nexus/frame_descriptor/spell_descriptor_payload.py:14-60
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy.py:255-288
  - context_compass/artifacts/class_binding_annotations_20260926/results/class_annotations_prototype.txt:1-78
  IMPACT: One-method change; no cache-generation bump (a changed id is a cache miss and the non-full-hit conjure
    rewrites the bundle, generation 12). The broad catch stays for non-NameError failures but gets documented
    as best-effort (banned-pattern rule).
  NEXT: Check active tickets and the mailbox for writers of this file, then write the patch lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T16:15:29Z
  TYPE: PLAN
  CLAIM: Patch lane class_binding_annotations_2026_09_26 written and read in order (architecture ->
    component_patch_binding_profile; no code-description patch: no new control flow). Mapping, patch section ->
    implementation -> validation: NameError fallback -> new staticmethod BindingProfileStrategy.
    _read_class_annotations(cls, module) called from _build_class_profile (evaluated read; NameError ->
    SignatureReflection.class_annotations; other failures and a failing fallback -> {}, documented best-effort) ->
    strategy unit tests for TYPE_CHECKING, quoted, nested-generic and dataclass shapes plus the failing-fallback
    case; unaffected classes -> existing RuntimeError test and a resolvable-values test; fingerprint -> unit test
    that a TYPE_CHECKING-typed field changes Bind.sha256_profile; probes -> the six-shape module before/after.
    Work on VM copies (~/cba_fix patched, ~/cba_base unpatched) by an anchored apply script, then suites, then the
    worktree.
  EVIDENCE:
  - system_docs/patches/active/class_binding_annotations_2026_09_26/architecture_patch.md:1-50
  - system_docs/patches/active/class_binding_annotations_2026_09_26/component_patch_binding_profile.md:1-23
  IMPACT: Patch-framework entry gate satisfied.
  NEXT: Build the VM copies and write the apply script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T16:19:42Z
  TYPE: MEASURE
  CLAIM: Implemented on ~/cba_fix by scripts/apply_fix.py (new staticmethod _read_class_annotations; ModuleType and
    Dict imports; docstring) plus six unit tests. Strategy tests: 18 passed patched; on unpatched source 4 of the 6
    new tests fail (TYPE_CHECKING, quoted/nested, dataclass, fingerprint) and the 2 behaviour-preserving ones pass.
    Probe (six shapes, 3.14.7t, two fresh processes each, identical per tree): the four affected shapes gain their
    keys (unavailable names as 'Decimal', 'list[Decimal]', 'Optional[Decimal]') and get new ids; ResolvedFields and
    NoAnnotations keep identical ids; adding a TYPE_CHECKING-typed field changes the id only after the fix. Unit
    chunks patched: spellbook 2163 passed + 1 failed, aether 4145 passed, rest 1893 passed + 4 failed. The 4 "rest"
    failures fail identically on base in the same chunk (two build-asset builder tests and the version stamp:
    assets stale; test_bind_rejects_internal_class: order-dependent, passes alone on both). The spellbook failure
    is mine to fix: my earlier search of test_binding_profile_strategy_future_annotations.py was cut at 20 lines and
    missed test_binding_profile_future_annotations_missing_names_clear_annotations, which pins the old {} for a
    missing name - the behaviour the owner approved changing.
  EVIDENCE:
  - context_compass/artifacts/class_binding_annotations_fix_20260926/scripts/apply_fix.py:1-274
  - context_compass/artifacts/class_binding_annotations_fix_20260926/results/probe_cba_fix_1.json:1-63
  - context_compass/artifacts/class_binding_annotations_fix_20260926/results/probe_cba_base_1.json:1-37
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy_future_annotations.py:241-261
  IMPACT: One existing test must move to the new contract (keep the name as source text; no error; methods still
    collected). Its SyntaxError sibling still expects {} and passes.
  NEXT: Add that test update to apply_fix.py, re-sync ~/cba_fix from base, re-apply, rerun unit chunks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T16:24:27Z
  TYPE: MEASURE
  CLAIM: apply_fix.py now also moves the pinning test to the new contract (renamed
    test_binding_profile_future_annotations_missing_names_keep_source_text; asserts {"missing": "MissingType"} and
    method collection). Re-synced ~/cba_fix from base and re-applied. Suites (3.14.7t, -X gil=0): strategy tests 34
    passed; unit melder spellbook 2164, aether 4145, rest 1893 passed with 4 failures identical to base in the same
    chunk; unit architecture_and_design/github_workflows/llm_support 44 failed + 388 errors identical to base (files
    absent from the VM copy); component 2135 passed; integration spellbook 581, crystallizer 258, conduit 268,
    mutation_research + live_sim 67, aether 716, multithreading 42 passed.
  EVIDENCE:
  - context_compass/artifacts/class_binding_annotations_fix_20260926/results/suite_results.txt:1-18
  - context_compass/artifacts/class_binding_annotations_fix_20260926/scripts/apply_fix.py:1-310
  IMPACT: Validated on the copy; ready for the worktree after a fresh target check.
  NEXT: Confirm the three target files in the worktree still equal ~/cba_base, then apply and hash-compare.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T16:24:48Z
  TYPE: MEASURE
  CLAIM: Applied to the worktree (all three targets were byte-identical to the synced base first; every anchor
    matched). The three files are byte-identical to the validated copy. Ignoring line endings: source +49/-14,
    test_binding_profile_strategy.py +174, the future-annotations test +9/-2.
  EVIDENCE:
  - context_compass/artifacts/class_binding_annotations_fix_20260926/results/source_diff.patch:1-90
  - context_compass/artifacts/class_binding_annotations_fix_20260926/results/test_diff.patch:1-223
  IMPACT: Code done; docs, graph and release note remain.
  NEXT: Verify the src_components/src_architecture indexes, slice the binding-profile sections, update them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T16:26:38Z
  TYPE: FACT
  CLAIM: Docs promoted by scripts/promote_docs.py (indexes verified current first, regenerated after, --check OK:
    src_components 9553 lines, src_architecture 2905). src_components Spell Examination Profiles: new invariant for
    the class binding profile read; the prior bullet's evidence range remeasured (106-114 -> 105-113). Found stale:
    its Failure Modes still listed function spell ids changing per process as an unfixed limit (fixed by the
    stable-ids lane earlier today); that line now records both limits fixed. src_architecture: the Annotation
    reflection invariant extended; handoff entries in both. The citation recipe reports no missing or
    out-of-bounds range for the touched files, and each cited range was opened on its symbol.
  EVIDENCE:
  - system_docs/src_components.md:4398-4421
  - system_docs/src_architecture.md:895-907
  - context_compass/artifacts/class_binding_annotations_fix_20260926/scripts/promote_docs.py:1-84
  IMPACT: Canonical docs current; packaged documents follow the owner's asset rebuild.
  NEXT: Re-extract the graph descriptor for binding_profile_strategy.py, update its prose, accept, assemble.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T16:28:45Z
  TYPE: FACT
  CLAIM: Graph: descriptors re-extracted into a scratch tree (3.14.7t, --strict, no skips); this file's changes
    were only its source hash, the class span and method count, and the two new imports. One responsibility
    added to BindingProfileStrategy (scripts/author_graph.py); the class node accepted after reading its source
    (was SEMANTICS_STALE); only this descriptor copied back; assemble and --check: 603 sections, 28434 lines
    (+1, the new responsibility). Release note: one bullet in "TYPE_CHECKING-only annotations no longer break
    Melder" (fields now count in the id; one-time id change and plan rebuild; resolvable classes keep their ids).
    Commit list written.
  EVIDENCE:
  - context_compass/artifacts/class_binding_annotations_fix_20260926/scripts/author_graph.py:1-23
  - release_docs/next_version_release.md:250-277
  - context_compass/artifacts/class_binding_annotations_fix_20260926/results/commit_files.txt:1-23
  IMPACT: Exit gate met apart from owner review and the deferred asset rebuild.
  NEXT: Owner reviews.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T16:29:22Z
  TYPE: FACT
  CLAIM: Consumed melder_0 M0-33 (NOTICE, no ACK): the owner notched __version__ to 0.2.59 for the override work and
    melder_0 moved the release header and added two sections ("Overrides build only what you did not supply",
    "Faster warm melds"), retiring the obsolete override-path bullet. Both writers' edits to the release note are
    present (0.2.59 header and LLM line, melder_0's sections, this lane's class-fields bullet and the validation-report
    details); no line over 110. Nothing for this lane to change.
  EVIDENCE:
  - release_docs/next_version_release.md:1-2
  - release_docs/next_version_release.md:250-277
  - src/melder/__version__.py:12-12
  IMPACT: The version this fix ships in is 0.2.59; the closed 0.2.58 notch ticket is superseded, not wrong.
  NEXT: Owner reviews.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T16:32:21Z
  TYPE: DECISION
  CLAIM: Owner accepted ("ok cool whats next? btw each change we make is a notch of 0.01 so its fine").
    Closure: ticket to tickets/tasks/completed/, patch lane to system_docs/patches/completed/ (deltas already
    in src_components and src_architecture), artifacts retained, boards synced, commit list names the moved
    paths. Version: owner convention is one notch per change; __version__ is left to the owner's commit-time
    notch. Owner-machine suites: Not run.
  EVIDENCE:
  - context_compass/system_docs/patches/completed/class_binding_annotations_2026_09_26/architecture_patch.md:1-50
  - context_compass/artifacts/class_binding_annotations_fix_20260926/scripts/close_lane.py:1-140
  IMPACT: melder_1 moves to the next lane (self-referencing constructor message).
  NEXT: none (closed).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
CLOSED 2026-09-26T16:32:21Z: owner accepted; ticket, patch lane, boards and commit list synced.
IN REVIEW 2026-09-26T16:28:45Z: class binding profiles keep TYPE_CHECKING-named annotations as source text
(NameError fallback to SignatureReflection.class_annotations, the ClassInspector read); affected classes get a new
id once. Tests, docs, graph and release note done; suites green on a worktree sync (failures identical to base).
Nothing committed; packaged documents and LLM bundles follow the owner's asset rebuild.
Opened 2026-09-26T16:12:32Z on owner direction. Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
