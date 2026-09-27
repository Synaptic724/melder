

# Task: Build a tool that finds every annotation in the library that can never evaluate

## Metadata
- Completed: 2026-09-26T10:12:17Z
- Closure Basis: owner acceptance in chat ("you fixed the issues so lets move onto the next thing").
- Summary: Annotation audit built and run over src/melder; its findings fixed; kept as the repository guard
  tests/unit/melder/test_annotation_integrity.py (green on the device tree).
- Task ID: TASK-2026-09-26-build-annotation-integrity-audit-tool
- Story: none (sibling of TASK-2026-09-26-fix-inspect-signature-nameerror-on-type-checking-annotations)
- Status: done
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T09:17:15Z
- Updated: 2026-09-26T09:57:24Z

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
- from_state: review
- to_state: in_progress
- transition_reason: Owner approved fixing the findings and keeping the audit as a repository test
  guard (DECISION 09:25:17Z); both landed in the sibling commit_v1; device validation follows.
- from_state: in_progress
- to_state: review
- transition_reason: Guard corrected and green on the device tree (MEASURE 09:57:20Z); owner review.
- from_state: review
- to_state: done
- transition_reason: Owner accepted (DECISION 2026-09-26T10:12:17Z).

## Steps / Checklist
- [x] Static pass (AST, no import): union-with-string-literal and undefined-name detection.
- [x] Dynamic pass: import every module, bind its TYPE_CHECKING imports, evaluate every annotation owner.
- [x] Run over src/melder; record findings with file:line.
- [x] Negative controls: seeded defects are caught; clean code is not flagged.
- [x] Owner decided placement (repository test guard) and fixes (DECISION 09:25:17Z); both landed.
- [x] Owner acceptance review.
- [ ] Run Ticket Microcycle; document each meaningful finding before continuing.

## Deliverables
- artifacts/annotation_integrity_audit_20260926/: the tool, results, controls.

## Files / Paths Impacted
- context_compass/artifacts/annotation_integrity_audit_20260926/ (tool, controls, results).
- tests/_annotation_audit_support.py and tests/unit/melder/test_annotation_integrity.py (owner-approved guard).

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
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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
- DATETIME: 2026-09-26T09:48:30Z
  TYPE: FACT
  CLAIM: The approved fixes and the repository guard landed with the sibling task's commit_v1: the three
    WeakConcurrentDict unions, the TYPE_CHECKING imports in the four frame_acl modules
    (IFrameACLProfileBuilder -> FrameACLProfileBuilder), Any in frame_acl_configuration_chain, Meld in
    creation_context; the audit as tests/_annotation_audit_support.py plus
    tests/unit/melder/test_annotation_integrity.py (library static and dynamic zero-finding guards, seeded
    static and dynamic controls, six string-union shapes). Hash-verified on the device; not yet run there.
  EVIDENCE:
  - context_compass/artifacts/inspect_signature_nameerror_20260926/results/commit_v1_manifest.txt:1-19
  - tests/unit/melder/test_annotation_integrity.py:1-221
  IMPACT: The audit is now a repository guard; this task closes once the guard passes on the device tree.
  NEXT: Run test_annotation_integrity.py on a VM copy of the device tree (3.14.7t) and record MEASURE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T09:53:00Z
  TYPE: MEASURE
  CLAIM: Device-tree run (VM copy, 3.14.7t, hash-verified identical to commit_v1): the three new test files
    give 31 passed, 1 failed. The failure is test_string_union_shapes_raise_when_evaluated[Optional[int] |
    "C"]: on 3.14.7t a typing.Union operand (Optional[...], Union[...], or an existing X | None) ACCEPTS a
    string on either side and wraps it as ForwardRef, so that shape evaluates. CORRECTS the 09:17:15Z truth
    table, which was measured on 3.14.0rc2t only: bare str/None/Any/classes/builtin generics still raise, but
    union operands raise on rc2 and not on 3.14.7. Every other guard passed on the device tree: library
    static and dynamic audits at zero findings, both seeded controls.
  EVIDENCE:
  - context_compass/artifacts/annotation_integrity_audit_20260926/results/union_truth_table_3_14_7t.txt:1-14
  - tests/unit/melder/test_annotation_integrity.py:200-221
  - tests/_annotation_audit_support.py:9-11
  IMPACT: STRING_IN_UNION stays correct as a static rule (the "C" | None form still raises on every build,
    and the others break the repo's no-| and no-quotes typing rules), but the guard test and the module
    docstring overstate it. As committed, one guard test fails on 3.14.7.
  NEXT: Within the approved guard files, drop the union-operand case from the must-raise list and pin it as
    policy-only; correct the docstring. Then run the full unit and component suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T09:56:30Z
  TYPE: FACT
  CLAIM: Guard corrected in place (approved guard files only, CRLF kept): the must-raise parametrization
    drops Optional[int] | "C" and adds list[int] | "C" (raises on every build seen); its docstring states
    why a typing.Union operand is excluded and that the static pass still reports it (seeded outer.inner).
    The now-unused Optional import is removed. The support-module docstring states the per-operand outcome
    and the 3.14.0rc2 / 3.14.7 difference. Device and VM copy hashes match (support d678887c, test 795e70cd);
    the three new files give 32 passed on the VM copy (3.14.7t).
  EVIDENCE:
  - tests/unit/melder/test_annotation_integrity.py:200-224
  - tests/_annotation_audit_support.py:1-30
  IMPACT: The guard now asserts only what holds on every observed 3.14 build.
  NEXT: Run the full unit and component suites on the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T09:57:20Z
  TYPE: MEASURE
  CLAIM: The repository guard passes on the device tree (3.14.7t): tests/unit/melder/test_annotation_integrity.py
    is green inside the full unit run (8540 passed), including the library static and dynamic zero-finding
    guards over the committed src and both seeded controls. The exit gate is met; owner review remains.
  EVIDENCE: context_compass/artifacts/inspect_signature_nameerror_20260926/results/device_suites_commit_v1.txt:1-5
  IMPACT: Task ready for review; closure waits for owner acceptance with the sibling fix task.
  NEXT: Move to review; owner confirms acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T10:12:17Z
  TYPE: DECISION
  CLAIM: Owner accepted both tasks in chat ("yeah its fine lets keep moving bro you fixed the issues so lets
    move onto the next thing"): acceptance criteria met. Closure: completion summary, move to
    tickets/tasks/completed/, attention-board closure sync, artifact dispositions (evidence and audit
    folders retained as reference; patch lane archived to system_docs/patches/completed/ after promotion).
  EVIDENCE: attention_board.md:114-115
  IMPACT: Both lanes close; open follow-ups stay listed in the fix task's DECISION_REQUEST note.
  NEXT: Owner picks the next lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Tool built and run: 3 latent string unions (weak_concurrent_dict), 21 owners in 5 modules whose
annotations name never-imported types, conduit fixed by the owner. Owner approved the fixes and the
repository guard; both landed in the sibling commit_v1; the guard (one union-operand case corrected) is
green on the device tree. Closed 2026-09-26T10:12:17Z on owner acceptance. Opened 2026-09-26T09:17:15Z on owner direction. Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
