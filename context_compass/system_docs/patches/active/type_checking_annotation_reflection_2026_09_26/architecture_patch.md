# architecture_patch

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:12:40Z
- Updated: 2026-09-26T09:12:40Z

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
    rendering typing's quoted generic arguments as `Any`; the 481 fully quoted hints in `src/`.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Utilities helpers (SignatureReflection, Package) | add/modify | one shared reader/renderer; Package stops raising | none |
| Spell Examination Profiles | modify | binding fingerprint text and detailed inspectors | SignatureReflection |
| SpellCompiler and Validation Pipeline | modify | occurrence contract fallbacks read FORWARDREF | none |
| ConduitWard and Contracts | modify | contract-key scan reads FORWARDREF | none |
| Packaged Hardcopy Documents And Public Helper Exports (ProtocolCrafter) | modify | reads FORWARDREF, renders unresolved names | none |
| Conduit Runtime | modify | one unreadable annotation (`"Conduit" \| None`) | none |

## Interface and Boundary Deltas
- Boundary delta: new internal module `src/melder/utilities/helpers/signature_reflection.py`
  (`SignatureReflection`, stateless static methods). Not exported from the package root.
- Interface delta: no public signature changes. Text outputs change only where they previously raised
  or embedded a ForwardRef owner: `Package.describe()`, detailed-profile `signature`/`annotation`
  strings, ProtocolCrafter output, and the bind `init_signature`/callable `signature` text.

## Cross-Component Invariants
- Invariant 1: where every annotation name resolves, rendered signature text is byte-identical to the
  default VALUE-format rendering (measured on 6,873 Melder callables).
- Invariant 2: rendered text never contains a ForwardRef owner or a memory address.
- Invariant 3: code that only reads parameters/defaults reads in `Format.FORWARDREF` (the Meld pattern).
- Invariant 4: the Signature object the requirements finder borrows stays the FORWARDREF signature.

## Migration and Rollout Order
1. Add SignatureReflection and its unit tests.
2. Switch the defaults-only readers (ConduitWard, both occurrence contract strategies, Package.signature).
3. Switch the renderers (Package.describe, ClassInspector, MethodInspector, BindingProfileStrategy,
   ProtocolCrafter) and fix the Conduit annotation.
4. Add the component regressions; run unit and component suites on 3.14t.
5. Promote to src_components/src_architecture, refresh the graph, rerun the asset builders.

## Rollback Strategy
- Rollback trigger: any regression in spell ids for classes whose annotations all resolve, or any
  suite failure attributable to these files.
- Rollback steps: restore the 9 modified modules from git, delete the new module and the two test
  files, rerun the asset builders.
- Post-rollback verification: `--check` on the asset runner; unit/component suites.

## Validation Expectations and Evidence Plan
- Regressions fail before and pass after; full unit and component suites show no new failures.
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
- What remains: promotion into canonical docs and the asset rebuild at closure.
- Next entrypoint: the task ticket's latest Notes NEXT.
