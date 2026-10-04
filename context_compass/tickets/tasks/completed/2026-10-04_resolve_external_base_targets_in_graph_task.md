

# Task: Resolve stdlib and builtin base classes in the source graph so no shipped edge target is unresolved

## Metadata
- Task ID: TASK-2026-10-04-resolve-external-base-targets-in-graph
- Story: none (standalone tooling/asset repair)
- Status: done
- Owner: user
- Agent Name: fable_1
- Priority: p1
- Created: 2026-10-04T18:20:00Z
- Updated: 2026-10-04T18:35:00Z

- Completed: 2026-10-04T18:35:00Z
- Summary: The graph extractor now resolves bases written through `import X` modules and builtins, so the four
  `(unresolved)` targets that shipped in the adjacency (`local`, `Loader`, `MetaPathFinder`, `ReferenceError`) read
  `threading.local`, `importlib.abc.Loader`, `importlib.abc.MetaPathFinder`, `builtins.ReferenceError`; graph,
  assets and bundles regenerated; the owner's failing `test_edge_candidates_are_not_in_the_shipped_adjacency`
  passes (84/84 in its file). No Melder source change, no notch. Closed under the owner's standing turn-in directive.

## Objective
The owner's 0.2.8224 unit run fails `test_system_document_view.py::test_edge_candidates_are_not_in_the_shipped_adjacency`:
the sampled node `DeadReferenceError` carries a derived `specializes` edge whose target is `ReferenceError (unresolved)`.
Four such edges ship (pre-existing, all external bases): `local`, `Loader`, `MetaPathFinder`, `ReferenceError`. The
extractor resolves bases only through `from X import Y` and same-module definitions, so a dotted base rooted in an
`import X` module and a builtin stay unresolved and the assembler prints `<label> (unresolved)`. Resolve them:
`import X` modules feed the import map, a dotted base resolves to `<module id>.<rest>`, a bare builtin to
`builtins.<Name>`. The node count grew with the 0.2.8222/0.2.8224 nodes, which moved the test's every-25th sample
onto the first of the four; the data was wrong before.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; the extractor's base handling and PASS-1 resolution read.
- EXECUTION_BOUNDARY: `tools/system_documents/python/extract_graph.py` (a PACKAGE-class file of the Context Compass
  install - the edit is deliberate and the upgrade tool will report it as a local change), the four descriptors it
  re-resolves, `system_docs/src_graph.md` + index (reassembled), the Melder build assets (adjacency), bundles.
- DEPENDENCIES: none.
- EXIT_GATE: zero `(unresolved)` targets in `src_graph.md`; the failing test passes with the whole
  `test_system_document_view.py`; assets and bundles rebuilt with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST if a resolved external id would collide with a package node id.

## Scope Boundaries
- In scope: edge-target resolution of external bases.
- Out of scope: edge candidates (guesses stay bare names by design); any Melder source change.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: graph regenerated with every target resolved; the test is green; assets and bundles current.

## Steps / Checklist
- [x] Extractor: `import X` in the import map; dotted-base resolution; builtins.
- [x] Re-extract (--strict), reassemble, rebuild assets; run the test file; rebuild bundles; both checks.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A graph with no unresolved base target; the test green.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY.

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/test_system_document_view.py -q -p no:cacheprovider`

## Risks / Rollback Notes
- None to runtime: the change touches generated documentation data and no Melder source. No notch (no `src/`
  code change; the regenerated assets are the normal rebuild).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: delete_on_close

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-04T18:20:00Z
  TYPE: FACT
  CLAIM: `base_name` reduces an attribute base (`threading.local`, `importlib.abc.Loader`) to its last attribute and
  `import_map` records only `from X import Y` names, so PASS 1 (`imports.get(label) or local_defs.get(...)`) leaves
  dotted-module bases and builtins without `to`; `assemble_graph.py` then prints `<label> (unresolved)`. Exactly four
  descriptors carry such an edge (synthetic_module x2, dead_reference_error, spell_space_thread_state); none is new.
  EVIDENCE:
  - tools/system_documents/python/extract_graph.py:113-121
  - tools/system_documents/python/extract_graph.py:180-203
  - tools/system_documents/python/extract_graph.py:555-571
  - tools/system_documents/python/assemble_graph.py:173-173
  IMPACT: a resolution fix in the extractor removes the class of defect; no test or Melder source changes.
  NEXT: implement the three resolution rules and regenerate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T18:35:00Z
  TYPE: MEASURE
  CLAIM: DONE. `extract_graph.py`: `import X` names enter the import map as module ids; `base_dotted` keeps the dotted
  text of an attribute base (in-memory `_to_dotted`, popped before write) so PASS 1 resolves `<module>.<rest>` when the
  head is an imported module; a bare builtin resolves to `builtins.<Name>`. Re-extract: 448/448 edge targets resolved
  (100%), zero `(unresolved)` in `src_graph.md` (the four read `threading.local`, `importlib.abc.Loader`,
  `importlib.abc.MetaPathFinder`, `builtins.ReferenceError`); assembled (587 sections); assets rebuilt and checked;
  `tests/unit/melder/test_system_document_view.py` 84 passed (the owner's failing test included). No `src/` change,
  no notch; bundles rebuilt at turn-in. The extractor is a PACKAGE-class install file; the upgrade tool will report
  this local change rather than overwrite it.
  EVIDENCE:
  - tools/system_documents/python/extract_graph.py:113-137
  - tools/system_documents/python/extract_graph.py:197-212
  - tools/system_documents/python/extract_graph.py:332-340
  - tools/system_documents/python/extract_graph.py:586-605
  - system_docs/src_graph.md:5850-5850
  - system_docs/src_graph.md:25751-25751
  IMPACT: the shipped adjacency carries only qualified targets; the test's sampling can land anywhere.
  NEXT: none (closure).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-10-04T18:35:00Z: DONE. Graph targets fully resolved; test green; assets and bundles current.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
