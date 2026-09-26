

# Task: Keep class binding-profile annotations when one names a TYPE_CHECKING-only type

## Metadata
- Task ID: TASK-2026-09-26-keep-class-binding-annotations-with-type-checking-names
- Story: none (follow-up recorded at closure of TASK-2026-09-26-fix-inspect-signature-nameerror-on-type-checking-annotations)
- Status: ready
- Owner: user
- Agent Name: melder_1
- Priority: p2
- Created: 2026-09-26T11:53:51Z
- Updated: 2026-09-26T11:56:25Z

## Objective
BindingProfileStrategy builds a class binding profile's `annotations` with `inspect.get_annotations` and
falls back to an empty dict when that raises, which a class-level annotation naming a TYPE_CHECKING-only type
does on Python 3.14. The class fingerprint hashes the sorted annotation keys, so those classes lose every
annotation name from their fingerprint and diagnostics. Establish from source exactly what is lost, who
consumes the annotations, and propose a fix.

## Ticket Contract
- ENTRY_GATE: Owner selected this lane 2026-09-26 (chat choice "Class annotation fallback").
- EXECUTION_BOUNDARY: Investigation reads src/ and runs probes on VM copies. src edits need owner
  confirmation of a DECISION_REQUEST (propose -> confirm -> implement); a fingerprint change moves the ids
  of affected classes once, which is a public-behaviour change.
- DEPENDENCIES: BindingProfileStrategy class profile, Bind.sha256_profile class branch, SignatureReflection.
- EXIT_GATE: Root cause and consumers evidenced; plan approved; implementation with regression tests;
  suites green; docs/graph updated.
- FAILURE_ESCALATION: DECISION_REQUEST for any fingerprint change; CONFLICT if stability and correctness
  cannot both hold.

## Scope Boundaries
- In scope: class-level annotation capture in binding profiles and every consumer of that field.
- Out of scope: ProtocolCrafter generic-argument rendering, graph semantics backlog, PEP 604 cleanup.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner chose this lane on 2026-09-26T11:53:51Z; investigation starts.
- from_state: in_progress
- to_state: ready
- transition_reason: Paused on owner redirect to the Phase-4 annotation-shape guard bug; prototype validated (2026-09-26T11:56:25Z).

## Steps / Checklist
- [x] Read the class-profile path and every consumer of ClassBindingProfile.annotations.
- [x] Reproduce: which classes fall back to {}, and what the fingerprint and diagnostics lose.
- [ ] Propose the fix and its id consequences (DECISION_REQUEST).
- [ ] Implement with regression tests after approval; validate; docs and graph.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence and probes under artifacts/class_binding_annotations_20260926/; a fix proposal; after approval, the
  fix, regression tests and docs.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py (expected)

## Validation
- Not run.

## Risks / Rollback Notes
- Restoring the missing annotation keys changes the fingerprint (spell id) of affected classes once.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/class_binding_annotations_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: ticket closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Class annotation capture under Python 3.14 lazy annotations.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.

## Notes
- DATETIME: 2026-09-26T11:55:07Z
  TYPE: FACT
  CLAIM: Source read in full for the class path. BindingProfileStrategy._build_class_profile reads
    inspect.get_annotations(cls, eval_str=True, globals=module dict) and on ANY exception sets annotations = {}
    (all-or-nothing: one unavailable name drops every class-level annotation). Consumers of
    ClassBindingProfile.annotations: Bind.sha256_profile (class branch hashes the sorted KEYS only) and the
    Nexus spell descriptor payload (publishes dict(annotations) as binding detail). FrameViewer's class view
    reads the inspector ClassProfile, not the binding profile. The detailed-profile path already has the fix
    shape: ClassInspector._class_annotations catches NameError and falls back to
    SignatureReflection.class_annotations(c) (FORWARDREF read; unavailable names as source text, quoted
    strings returned as written, no owner-bearing ForwardRef left). This strategy site is the only remaining
    get_annotations call in src/melder with a broad {} fallback.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:69-146
  - src/melder/aether/spellbook/bind/bind.py:944-954
  - src/melder/nexus/frame_descriptor/spell_descriptor_payload.py:14-52
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/class_inspector.py:150-173
  - src/melder/utilities/helpers/signature_reflection.py:153-186
  IMPACT: For affected classes the fingerprint ignores annotation names (adding or removing an annotated field
    does not change the id) and Nexus shows no annotations; ids are nevertheless process-stable ({} is
    deterministic), so this is a fidelity defect, not an id-stability one. Pending measurement.
  NEXT: Probe binding-profile annotations and spell ids for resolvable, TYPE_CHECKING-only, quoted and
    dataclass shapes on the device-tree source, then with the ClassInspector-style fallback in a VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T11:56:25Z
  TYPE: MEASURE
  CLAIM: Reproduced and prototyped (3.14.7t, two fresh processes each). Before: TypeCheckingField,
    QuotedUnavailable, NestedUnavailable and DataclassField all get annotations {} (every key dropped); ids are
    process-stable; adding "extra: Decimal" to TypeCheckingField leaves its id unchanged. ResolvedFields and
    NoAnnotations are correct. Prototype in a VM copy (one change in _build_class_profile: except NameError ->
    SignatureReflection.class_annotations(cls); other exceptions still {}): all keys kept, unavailable names
    as source text ('Decimal', 'list[Decimal]', 'Optional[Decimal]'), resolvable values unchanged, ids stable
    across processes, the extra field now changes the id. ResolvedFields and NoAnnotations ids unchanged; the
    four affected classes' ids change once.
  EVIDENCE:
  - context_compass/artifacts/class_binding_annotations_20260926/results/class_annotations_before.txt:1-41
  - context_compass/artifacts/class_binding_annotations_20260926/results/class_annotations_prototype.txt:1-78
  - context_compass/artifacts/class_binding_annotations_20260926/probes/probe_class_annotation_shapes.py:1-60
  IMPACT: Fix shape validated (one-line fallback mirroring ClassInspector). Lane paused on owner redirect to
    the Phase-4 AnnotationShapeGuard bug before the DECISION_REQUEST was raised.
  NEXT: On resume, raise the DECISION_REQUEST (fallback + one-time id change for affected classes).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
PAUSED 2026-09-26T11:56:25Z on owner redirect: fix validated in a VM copy (see MEASURE); next is the DECISION_REQUEST.
Opened 2026-09-26T11:53:51Z on owner selection. Investigation first; no src edits until the owner approves a plan.
Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
