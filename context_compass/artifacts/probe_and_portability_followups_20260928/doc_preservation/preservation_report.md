# Content preservation report - portability pass on src_architecture and src_components (2026-09-28)

Baselines captured before the first edit (`*_before.txt`, `*_before.md`); after-captures span each document
alone. Comparisons: `src_architecture_compare.md` (22 lost, 18 added) and `src_components_compare.md` (31 lost,
28 added). Every lost line is accounted for:

- Index tool commands, 12 lines per document (three `python .../index_document.py` invocations with their
  `--doc` lines and code fences) and the lead-in lines "Consume it by slicing ...:" / "Verify before trusting
  any range:" / "companion is `..._index.md`, rebuilt ...:": RELOCATED, not lost - the same three commands
  (regenerate, slice, check) are in each document's authoring instructions ("Indexing Contract"), which is
  where the portability rule sends them. The prose that stays says the index exists, what it records and
  that it must be verified before slicing.
- "Spec: `agent_onboarding/...`" (one per document): removed by the rule ("the document does not cite its
  own tooling"); the new closing paragraph of each `## Indexing` says the commands belong to the tooling.
- Patch-lane paths (1 in src_architecture, 3 in src_components) and the companion-list entry
  `system_docs/patches/active/`: reworded to the patch id plus the migration file's name, or to "the
  documentation tooling's open patch lanes"; the wrapped lines around them were reflowed.
- Skill-file names (`src_architecture_instructions.md` x2, `src_components_instructions.md` x3,
  `agent_onboarding/.../src_graph_generation.md`): reworded to "authoring instructions" / "graph generation
  tooling"; the neighbouring words on those lines are unchanged.
- src_components C1 fields of conduit_meld.py (end_line, loc 1039 -> 1087; verified_at): remeasured.

src_architecture's index rules ("Format rules ..." and "An index records ...") moved from inside the citation
subsection to the `## Indexing` body; the line multiset shows them retained. Added lines: the rewritten
Indexing prose, the reworded pointer lines, one handoff paragraph per document, and the C1 fields.
