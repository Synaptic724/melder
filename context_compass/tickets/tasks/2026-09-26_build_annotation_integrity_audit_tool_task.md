

# Task: Build a tool that finds every annotation in the library that can never evaluate

## Metadata
- Task ID: TASK-2026-09-26-build-annotation-integrity-audit-tool
- Story: none (sibling of TASK-2026-09-26-fix-inspect-signature-nameerror-on-type-checking-annotations)
- Status: review
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T09:17:15Z
- Updated: 2026-09-26T09:23:31Z

## Objective
Owner direction 2026-09-26: "building a tool that can find all these kinds of bugs in the entire library
and lets locate them ... all forms of "Type" | None, because it fails". Build an audit that locates every
annotation in src/melder that raises when evaluated even with every TYPE_CHECKING import available (the
"Conduit" | None class of defect), run it, and report each finding with file:line.

## Ticket Contract
- ENTRY_GATE: Owner direction in chat; board row inspect_annotation_audit routes here.
- EXECUTION_BOUNDARY: The tool and its results live in this task's artifact folder and run on copies;
  no repository file outside context_compass/ is edited. Fixing findings, or adding the tool to the
  repository as a test or CI guard, needs owner confirmation first.
- DEPENDENCIES: Sibling fix task (resumes with the findings folded in).
- EXIT_GATE: Tool run over all of src/melder with findings recorded; owner review.
- FAILURE_ESCALATION: BLOCKER if modules cannot be imported for the dynamic pass; DECISION_REQUEST for
  repository placement of the tool.

## Scope Boundaries
- In scope: every annotation site in src/melder (parameters, returns, class and module variables, nested
  functions and classes, type aliases); defects that raise on evaluation (TypeError from a string in a |
  union, names undefined even under TYPE_CHECKING, other evaluation errors); a policy count of PEP 604
  unions and quoted annotations.
- Out of scope: fixing findings (sibling task / owner decision); third-party code.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed the audit on 2026-09-26.
- from_state: in_progress
- to_state: review
- transition_reason: Tool built, controls pass, findings recorded (MEASURE notes); owner review.

## Steps / Checklist
- [x] Static pass (AST, no import): union-with-string-literal and undefined-name detection.
- [x] Dynamic pass: import every module, bind its TYPE_CHECKING imports, evaluate every annotation owner.
- [x] Run over src/melder; record findings with file:line.
- [x] Negative controls: seeded defects are caught; clean code is not flagged.
- [ ] Owner review; decide repository placement and fixes.
- [ ] Run Ticket Microcycle; document each meaningful finding before continuing.

## Deliverables
- artifacts/annotation_integrity_audit_20260926/: the tool, results, controls.

## Files / Paths Impacted
- context_compass/artifacts/annotation_integrity_audit_20260926/ only.

## Validation
- Negative control and full src/melder run recorded (sandbox 3.14.0rc2t; device VM 3.14.7t).
  Owner machine: Not run.

## Risks / Rollback Notes
- Importing every module runs import-time code (Melder boots Aether on import); run in a throwaway process.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
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
  - artifacts/annotation_integrity_audit_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: ticket closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Annotations that cannot evaluate on Python 3.14 (string operands in | unions, undefined names).
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Keep notes append-only; promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T09:17:15Z
  TYPE: MEASURE
  CLAIM: Truth table on 3.14.0rc2t: a string literal in a | union raises TypeError against None, a str,
    a class, int, list[int], Optional[...], Union[...], Any and an existing X | None; only
    typing.List[int] and a TypeVar accept it. So any string literal operand of | in an annotation is a
    defect (crash in nearly every pairing, a policy violation in the rest). The sibling task's dynamic
    probe found one instance (Conduit._resolve_peer_conduit_for_contract_hooks) but only covered
    module-level functions and direct class members, not nested functions/classes or variable
    annotations.
  EVIDENCE:
  - context_compass/artifacts/inspect_signature_nameerror_20260926/results/invalid_annotations_before.txt:1-2
  - context_compass/artifacts/inspect_signature_nameerror_20260926/probes/probe_invalid_annotations.py:1-59
  IMPACT: A static AST rule is sound for the string-union class; a dynamic pass is needed for anything
    only evaluation can reveal (undefined names, non-generic subscripts).
  NEXT: Build the static pass and the dynamic pass; seed negative controls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T09:19:41Z
  TYPE: MEASURE
  CLAIM: Tool built (annotation_audit.py). Static pass (AST, no import) checks every annotation site:
    STRING_IN_UNION (string literal operand of |, also inside string annotations and Literal[...]),
    UNDEFINED_NAME (no enclosing module/class/function scope, TYPE_CHECKING import, type parameter or
    builtin binds it), UNPARSEABLE_STRING. Dynamic pass imports every module, binds its own
    TYPE_CHECKING imports, and evaluates every owner (module, classes incl. nested, functions,
    methods, static/class methods, property accessors) in VALUE format -> EVAL_ERROR. Negative
    control (sandbox 3.14.0rc2t): all 9 seeded defects reported (param, return, class var, module var,
    nested class, nested function, Literal["a" | "b"], string inside a string annotation, undefined
    name); the clean file (self reference, class-scope name, TYPE_CHECKING-only name, forward
    reference, PEP 695 param, closure name, quoted generic arg, function-local annotation) produced
    zero findings.
  EVIDENCE:
  - context_compass/artifacts/annotation_integrity_audit_20260926/annotation_audit.py:1-523
  - context_compass/artifacts/annotation_integrity_audit_20260926/controls/control_result.txt:1-33
  IMPACT: Tool is trustworthy enough to run over src/melder.
  NEXT: Run it over a VM copy of the current device src/melder on 3.14.7t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T09:22:22Z
  TYPE: MEASURE
  CLAIM: Audit of current device src/melder (VM copy, 3.14.7t): 596 files, 596 modules imported, 692
    TYPE_CHECKING names bound, 8,303 annotation owners evaluated. Findings:
    (1) STRING_IN_UNION x3, weak_concurrent_dict.py:1621/1657/1685 (__or__/__ior__/__ror__ other:
    "WeakConcurrentDict[_K, _V]" | Mapping[_K, _V] | ...). Not an EVAL_ERROR today only because Mapping
    is typing.Mapping (its __ror__ accepts a str); the module also imports collections.abc Mapping as
    MappingABC, and switching to it would make all three raise. (2) Names undefined even under
    TYPE_CHECKING, 21 owners that raise NameError on any VALUE read: frame_acl_compiler.py (13 owners;
    FrameACLRuleSet, FrameACLViewProfile, IFrameACLProfileBuilder never imported),
    frame_acl_set_compatibility_validator.py (6; FrameACLRuleSet, IFrameACLProfileBuilder),
    frame_acl_profile_builder.py (1; FrameACLRuleSet), frame_acl_configuration_chain.py (1; Any never
    imported); plus creation_context.py:239/276 quoted "Meld" with no import at all. (3) The Conduit
    "Conduit" | None is no longer present: device conduit.py changed after 08:57 (owner edit) to
    conduit: Optional["Conduit"]; the tool reports it on the 08:33 snapshot, so the rule catches it.
    Policy counts: 416 PEP 604 unions, 575 quoted annotations.
  EVIDENCE:
  - context_compass/artifacts/annotation_integrity_audit_20260926/results/report_src_melder.txt:1-78
  - context_compass/artifacts/annotation_integrity_audit_20260926/results/snapshot_0833_static.txt:1-57
  - src/melder/aether/conduit/conduit.py:6735-6740
  - src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_dict.py:1618-1625
  - src/melder/nexus/acl/frame_acl_compiler.py:1-20
  IMPACT: 3 latent string unions and 5 modules with missing imports (every annotation read of those 21
    owners fails; get_type_hints and mypy would too). None is a runtime crash in normal Melder use.
  NEXT: Report to the owner; propose fixes and whether to keep the tool as a repository guard.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T09:25:17Z
  TYPE: DECISION
  CLAIM: Owner approved ("yeah ok go fix this shit please"): fix the audit findings (TYPE_CHECKING imports
    for FrameACLRuleSet/FrameACLViewProfile/FrameACLProfileBuilder replacing the nonexistent
    IFrameACLProfileBuilder, Any in frame_acl_configuration_chain, Meld in creation_context, the three
    WeakConcurrentDict unions as Union[...]), add the audit as a repository test guard, and resume the
    approved SignatureReflection fix minus conduit.py (already fixed by the owner).
  EVIDENCE: context_compass/artifacts/annotation_integrity_audit_20260926/results/report_src_melder.txt:1-78
  IMPACT: Both lanes move to implementation; writer melder_1 (melder_0 confirmed no overlap, M0-15).
  NEXT: Re-hash planned files on the device and apply edits to current bytes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Tool built and run: 3 latent string unions (weak_concurrent_dict), 21 owners in 5 modules whose
annotations name never-imported types, conduit fixed by the owner. Awaiting owner review of fixes and
tool placement. Opened 2026-09-26T09:17:15Z on owner direction. Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
