# architecture_patch

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Status: completed (promoted 2026-09-26; archived at closure)
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:12:40Z
- Updated: 2026-09-26T09:57:44Z

## Patch Scope and Non-Goals
- Objective: Melder reads signatures and annotations of user code and of its own classes without
  raising when an annotation names a type that is unbound at runtime (a TYPE_CHECKING-only import
  under Python 3.14 lazy annotations), and any text it renders from them is deterministic.
- Non-goals:
  - No change to the typing policy (TYPE_CHECKING-only concrete imports, no quotes, no fallback
    aliases, no `from __future__ import annotations`).
  - No change to how Phase 1 classifies parameters (the requirements finder already reads FORWARDREF).
  - Not fixed here (recorded separately): function-spell fingerprints hash `repr()` addresses;
    binding-profile class annotations clear to `{}` on an unresolved name; external
    `typing.get_type_hints` / default `inspect.signature` on Melder's own API; ProtocolCrafter
    rendering typing's quoted generic arguments as `Any`; the 481 fully quoted hints in `src/`; the
    audit's policy counts (416 PEP 604 unions, 575 quoted annotations) - reported, not changed.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Utilities helpers (SignatureReflection, Package) | add/modify | one shared reader/renderer; Package stops raising | none |
| Spell Examination Profiles | modify | binding fingerprint text and detailed inspectors | SignatureReflection |
| SpellCompiler and Validation Pipeline | modify | occurrence contract fallbacks read FORWARDREF | none |
| ConduitWard and Contracts | modify | contract-key scan reads FORWARDREF | none |
| Packaged Hardcopy Documents And Public Helper Exports (ProtocolCrafter) | modify | reads FORWARDREF, renders unresolved names | none |
| Conduit Runtime | none in this lane | the one unreadable annotation was fixed by the owner directly | none |
| Nexus Descriptor And ACL Managers | modify (annotation-only) | four modules named types no scope bound | none |
| Meld Resolution Runtime | modify (annotation-only) | `"Meld"` was quoted and never imported | none |
| Utilities data structures (WeakConcurrentDict) | modify (annotation-only) | string operands in `\|` unions | none |
| Test suite (annotation integrity guard) | add | keep every src annotation evaluable | audit support module |

## Interface and Boundary Deltas
- Boundary delta: new internal module `src/melder/utilities/helpers/signature_reflection.py`
  (`SignatureReflection`, stateless static methods). Not exported from the package root.
- Boundary delta: new test-support module `tests/_annotation_audit_support.py` (static AST pass and
  dynamic evaluation pass; command-line entry point) and guard `tests/unit/melder/test_annotation_integrity.py`.
- Interface delta: no public signature changes. Text outputs change only where they previously raised
  or embedded a ForwardRef owner: `Package.describe()`, detailed-profile `signature`/`annotation`
  strings, ProtocolCrafter output, and the bind `init_signature`/callable `signature` text.

## Cross-Component Invariants
- Invariant 1: where every annotation name resolves, rendered signature text is byte-identical to the
  default VALUE-format rendering (measured on 6,873 Melder callables).
- Invariant 2: rendered text never contains a ForwardRef owner or a memory address.
- Invariant 3: code that only reads parameters/defaults reads in `Format.FORWARDREF` (the Meld pattern).
- Invariant 4: the Signature object the requirements finder borrows stays the FORWARDREF signature.
- Invariant 5: every annotation owner in `src/melder` evaluates in VALUE format once its module's
  TYPE_CHECKING imports are bound, and no annotation uses a string literal as a `|` operand. Guarded by
  `tests/unit/melder/test_annotation_integrity.py` (zero static and dynamic findings).

## Migration and Rollout Order
1. Add SignatureReflection and its unit tests.
2. Switch the defaults-only readers (ConduitWard, both occurrence contract strategies, Package.signature).
3. Switch the renderers (Package.describe, ClassInspector, MethodInspector, BindingProfileStrategy,
   ProtocolCrafter) and fix the Conduit annotation.
4. Add the component regressions; run unit and component suites on 3.14t.
5. Annotation-only fixes from the audit (Nexus ACL modules, creation_context, WeakConcurrentDict) and
   the repository guard (owner-approved 2026-09-26).
6. Promote to src_components/src_architecture, refresh the graph, rerun the asset builders.

## Rollback Strategy
- Rollback trigger: any regression in spell ids for classes whose annotations all resolve, or any
  suite failure attributable to these files.
- Rollback steps: restore the 14 modified modules from git (list: the task's commit manifest), delete
  the new module and the four new test files, rerun the asset builders.
- Post-rollback verification: `--check` on the asset runner; unit/component suites.

## Validation Expectations and Evidence Plan
- Regressions fail before and pass after; full unit and component suites show no new failures.
- Recorded (device tree, 3.14.7t): unit 8540 passed, component 2097 passed, integration 1924 passed,
  no failures; the guard reports zero findings.
- Evidence: `artifacts/inspect_signature_nameerror_20260926/` (probes, before/after results).
- Spell ids: identical across processes for a TYPE_CHECKING-annotated class; unchanged for classes
  whose annotations resolve.

## Ticket Coverage Map
- Epic: none
- Story: none
- Tasks: tickets/tasks/2026-09-26_fix_inspect_signature_nameerror_on_type_checking_annotations_task.md

## Unknowns and Decision Requests
- UNKNOWN: whether any user dataclass reads differently in FORWARDREF than in VALUE (one Melder
  dataclass, ChangeControlStagedMutation, does); such text is deterministic after this patch.
- DECISION_REQUEST: none open (owner approved the set 2026-09-26).

## Context / Handoff Summary
- What changed: see the component patches.
- What changed since authoring: audit fixes and the guard joined the lane; the owner fixed the Conduit
  annotation directly, so this lane leaves conduit.py untouched.
- What remains: promotion into canonical docs, graph refresh, and the asset rebuild at closure.
- Next entrypoint: the task ticket's latest Notes NEXT.
