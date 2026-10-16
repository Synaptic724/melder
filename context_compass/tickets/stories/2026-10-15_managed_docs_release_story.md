# Story: managed_docs_release - system docs, graph, README, release note and benchmarks for the member

## Metadata
- Story ID: STORY-2026-10-15-managed_docs_release
- Epic: EPIC-2026-10-14-managed_spell_quantity (tickets/epics/2026-10-14_managed_spell_quantity_epic.md); story 7 of 7
- Status: blocked
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T09:29:51Z
- Updated: 2026-10-16T00:53:23Z

## User Narrative
As an agent arriving in a Melder world, I want the architecture, component and test maps, the graph, the README and
the release note to describe managed spells, so that I can use the member without reading its source first.

## Value / MRP Alignment
Documentation is part of the API in a public library; the patch docs promote into the canonical maps.

## Ticket Contract
- ENTRY_GATE: S1-S6 closed; the component maps sliced through their indexes for the sections to edit.
- EXECUTION_BOUNDARY: context_compass/system_docs (src_architecture, src_components, tests docs, their indexes, graph
  descriptors and reassembly), README.md, docs/ where the Existence members are listed,
  release_docs/next_version_release.md; the patch docs promoted and archived.
- DEPENDENCIES: S1-S6.
- EXIT_GATE: docs, indexes and graph current; release note final for the lane; benchmarks recorded; patch docs
  archived; both rebuild `--check` runs OK; the epic closed with the owner's acceptance
- FAILURE_ESCALATION: DECISION_REQUEST if a change would alter an existing member's behaviour, an existing spell id or
  record, or the frame -> conduit -> Book lock order; CONFLICT when the source contradicts the epic's Build
  Specification (fix the spec first); BLOCKER when a gate cannot be met

## Requirements (Functional)
- src_architecture: boundary list, meld sequence, operational invariants, failure modes, code map.
- src_components: Creations, Meld doors, binding pipeline, the lowering, Phase 6, ownership transfer.
- Tests docs; graph descriptors for the new modules; README Existence section; the release note.

## Requirements (Non-Functional)
- No path into context_compass in a produced document.
- Indexes regenerated in the same pass.

## Scope Boundaries
- In scope: documentation, benchmarks, patch promotion, rebuild.
- Out of scope: any `src/` change.

## State Transition Event
- from_state: in_progress
- to_state: blocked
- transition_reason: S7's work is done - benchmarks, the four system docs and the graph, the README and docs
  site, the release note, the archived patch lane, rubric scores - and the rebuild runs last; the EXIT_GATE's
  remaining item is the owner's acceptance of the epic, a reserved decision. Unblock: the owner accepts or
  redirects. The board row reads `review`.
- prior: ready -> in_progress (2026-10-15T21:07:15Z): S6 landed and closed (0.2.8246, rebuilt and checked).
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S6 lands.

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity EXIT_GATE.

## Tasks (Implementation Checklist)
- [x] Benchmarks: the spike probes and the existing meld shapes, before and after.
- [x] Edit the system docs and regenerate indexes; descriptors and graph reassembly.
- [x] README and the release note.
- [ ] Archive the patch docs (done); rebuild assets and bundles last (done, both checks OK); close the epic (the
  owner's acceptance).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Every check in the EXIT_GATE recorded.

## Validation / Test Plan
- Index and graph checks; both rebuild checks.

## UX / API / Data Notes
- None.

## Risks / Mitigations
- Stale citations -> the src_architecture citation check recipe.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No `src/` edit before the component patch and the mapping note exist (S7 changed no `src/` file).

## Open Questions
- None open.

## Decision Log
- None yet.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/managed_spell_quantity_2026_10_15/architecture_patch.md (archived with the lane)
  - artifacts/managed_spell_quantity_20261015/ (this story's runs and scripts)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (artifacts)
- CLEANUP_TRIGGER: patch docs promoted and archived at S7; artifacts retained

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - documentation of managed spells
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, design, implementation and tests of this story;
  created 2026-10-15T09:29:51Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-15T09:29:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened ready behind S6: documentation, benchmarks, patch promotion and the rebuild.
  EVIDENCE: context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:36-56
  IMPACT: Holds the lane's closing work.
  NEXT: Start after S6 closes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-15T21:07:15Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: S7 started on 0.2.8246 (S1-S6 landed; the S6 rebuild checks printed only OK). Order: (1) benchmarks - the
    existing meld shapes and scope cycles A/B, HEAD's 0.2.8240 tree (exported read-only with `git archive` into the VM's
    /tmp) against the working copy, processes interleaved, both GIL modes; the managed warm cycle again at 0.2.8246;
    (2) align the patch lane with the source as built (architecture patch, then each story's component and
    code-description patches), then promote it: src_architecture (boundary list, boot and cleanup sequences, meld and
    transfer sequences, invariants, failure modes, code map, sources, a diagram, handoff) and its index; src_components
    (the components and flows the member touches, sliced through the index, the code map) and its index; the tests
    docs; graph descriptors for the new modules, authored semantics and reassembly; (3) README and docs/ where the
    Existence members are listed; the release note's packaging lines; (4) archive the patch lane, sync the artifact
    board, rebuild last, close the story and hand the epic to the owner for acceptance. No `src/` change, no notch.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:21-45
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:36-56
  - context_compass/special_instructions/agent_contribution_guide.md:18-27
  IMPACT: The epic's EXIT_GATE items that remain (benchmarks, docs, graph, README, release note, rebuild) map onto
    this order; the owner's acceptance closes the epic.
  NEXT: Export HEAD's src into /tmp and write the existing-shapes A/B probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T21:10:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: No regression on the existing meld shapes or scope cycles from 0.2.8240 (HEAD, before S1) to 0.2.8246. A/B
    on the VM (CPython 3.14.7t), three process pairs alternating the trees, 100,000 cycles x 7 rounds per process (a
    twentieth of that for the scope arms), median of the per-process medians, after/before: gil=1 - unique 0.960,
    many 0.996, unique_per_conduit 1.033, many of many 1.007, many of unique 1.024, override 0.990, by name 1.021,
    dynamic many 0.992, dynamic unique 1.009, lesser cycle 1.013, spellspace cycle 1.021; gil=0 - 0.984, 0.990,
    0.999, 0.980, 0.991, 1.005, 1.013, 1.000, 1.017, 0.969, 1.027. Every ratio sits inside the per-process spread
    (about 5%). The managed warm cycle at 0.2.8246 (200,000 x 7): a direct meld plus its release 306 ns (gil=0) /
    319 ns (gil=1) on an automatic root and 739 / 734 ns on a dynamic one; a `many` holder leasing one object plus
    the release 365 / 385 ns - S5's numbers. Every run left one object in each pool (count 1, idle 1).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_bench_ab_gil1.txt:85-98
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_bench_ab_gil0.txt:85-98
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_warm_lease_cycle_gil0.txt:1-9
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_warm_lease_cycle_gil1.txt:1-9
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s7_existing_shapes.py:1-212
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_bench_ab.py:1-41
  IMPACT: The epic's benchmark gate is met: existing meld paths within noise; the managed cycle well under 1 us.
  NEXT: Align the patch lane with the source as built, architecture patch first.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T21:18:13Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The patch lane matches the source as built, read whole (architecture patch, six component and four
    code-description patches) against the S1-S6 code: the pool, the registry, the lease, the dispense, the stamps,
    the error texts and the as-built notes (U3-U11) agree. Two drifts, corrected in the lane before promotion: the
    architecture patch said three package-root exports where S4 shipped four (`ManagedSpellLease` joined
    `ManagedSpellMode`, `ReleaseManagedSpell` and `ManagedSpellExhaustedError`), and the S5 component patch named
    the lowering test file
    test_site_plan_lowering.py (it is test_site_plan_lowering_managed.py). Promotion targets: src_architecture
    (glossary, boundary list, guardrails, boot, meld, transfer and cleanup sequences, four invariants, five failure
    modes, code map, sources, a diagram, handoff), src_components (a new C3 component for the pools, registry and
    lease; dated entries in Public API, Spellbook Core, Binding Pipeline, Aether, Crystallizer, Conduit, Creations,
    Meld and SpellCompiler; the ownership-transfer subcomponent; two flows; the code map and inventory; sources;
    handoff), tests_components and tests_architecture (28 new test files, 9 changed).
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md:1-112
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_dispense_codegen.md:75-89
  - src/melder/__init__.py:226-252
  - src/melder/aether/conduit/creations/creations.py:326-399
  - src/melder/aether/aether.py:186-266
  IMPACT: The canonical docs can be written from the patches plus the cited source; nothing in the lane contradicts
    the epic's Build Specification.
  NEXT: Edit src_architecture and regenerate its index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T21:23:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: src_architecture carries the managed member (scripts/s7_docs_architecture.py): the glossary, the boundary
    list, the guardrails (628 bind-guard entries), the boot sequence (seven eager hosted roots, `ReleaseManagedSpell`
    last), the meld, transfer and cleanup sequences, four operational invariants (pools, registry, leases in plans,
    owner stamps through a transfer), five failure modes (refusals, release errors, bind refusals, the 0.2.8246 fix,
    the open pre-conjure staging gap), the code map (five new modules; 21 extents remeasured - the lane's 20 files and
    `spell_system_states.py`, three lines stale since 2026-10-04), the sources, a Managed Lease and Release diagram
    and a handoff entry. Found while checking: 23 numeric citations into conduit.py, spellbook.py, aether.py and
    bind.py no longer pointed at their symbols - most had already drifted before this lane (since 0.2.8235); they
    are re-pointed at the code they name (scripts/s7_docs_architecture_citations.py). The index is regenerated (62
    sections, 4473 lines) and the document's citation recipe reports 0 problems.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1-4473
  - context_compass/system_docs/src_architecture_index.md:1-91
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_architecture.py:1-419
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_architecture_citations.py:1-61
  IMPACT: The architecture document describes 0.2.8246; the component map is next.
  NEXT: Promote the lane into src_components (the new component, the dated entries, flows, code map).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T21:43:02Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: src_components carries the managed member (scripts/s7_docs_components.py; s7_docs_components_fix.py applied
    before its first run, s7_docs_components_counts.py after it): a new C3 component "Managed Spell Pools
    (ManagedSpellQuantity, ReleaseManagedSpell, ManagedSpellLease)" with the full entry contract, written after
    re-reading on 0.2.8246 the five new modules whole, the bind normalizers, `Spell._add_owned_conduit`, the lease
    emission and the Creations pool verbs; dated entries in Public API, Spellbook Core, Binding Pipeline, Aether,
    Crystallizer, Conduit Runtime, Creations (with Owned State and the Existence list), Meld Resolution Runtime and
    SpellCompiler; the owner stamps in the Ownership Transfer subcomponent and the transfer flow; a new Managed Lease
    -> Release flow and a Managed Pools diagram; the code map adds the five modules and remeasures 26 extents (four
    stale since earlier lanes); the inventory adds five entries by its own rule and its group counts follow (aether
    285, utilities 46); the source list re-resolves (177 files); a handoff entry. The re-read corrected three draft
    claims before the run: limited_quantity also serves an object released since the plan's pop; `describe(cls)`
    rows are the pool snapshot plus `holding_conduit_id` and `active_version`; `count` never exceeds the limit,
    while a released fresh override object is pooled uncounted. The index is regenerated (152 sections, 11472
    lines). The citation recipe finds nothing in src_components or src_architecture and one stale graph section
    (`spellframe_kind/__init__.py`, absent from disk), left for the graph pass.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:1-11472
  - context_compass/system_docs/src_components_index.md:1-181
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_components.py:1-462
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_components_fix.py:1-94
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_components_counts.py:1-54
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:14-938
  - src/melder/aether/conduit/creations/release_managed_spell.py:13-686
  IMPACT: The component map describes 0.2.8246; the tests docs are next, then the graph.
  NEXT: Promote the lane's 28 new and 9 changed test files into tests_components and tests_architecture.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T22:02:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Three test files the lane edited had their line endings flipped, so the diff the owner commits showed whole
    files instead of the lane's lines: test_conduit_facade.py was CRLF at HEAD and all LF on disk (+1015/-1010
    against +6/-1 ignoring CR); test_codegen_plan_discovery_core.py and test_generalized_specializer_wrapper.py were
    LF at HEAD and mixed on disk (the HEAD lines CRLF, the lane's 46 and 20 added lines LF). Each is restored to its
    HEAD convention, content unchanged: the plain diff now equals the CR-insensitive one (+6/-1, +46/-0, +20/-0),
    and the three files pass in both GIL modes (61 tests each run). No other file in the working tree differs only
    by line endings. The repository pins no eol for Python on purpose (.gitattributes), so a file keeps the endings
    it was committed with.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/test_conduit_facade.py:1-1015
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py:1-328
  - tests/unit/melder/spellbook/spell_compiler/test_generalized_specializer_wrapper.py:1-394
  - .gitattributes:25-30
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_line_endings_restored_gil0.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_line_endings_restored_gil1.txt:1-10
  IMPACT: The owner reviews the lane's real test changes, not three rewritten files.
  NEXT: Write the tests docs from the lane's 28 new files (their 312 test contracts) and the 9 changed ones.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-15T22:23:27Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The tests docs' facts, measured on disk before the first edit. tests_components' Key Files union is 219 paths
    and equals its 219 C1 records (the join script dropped `pyproject.toml`, a root file with no slash, until its
    filter was fixed). The three CI tiers hold 833 `test_*.py` modules (unit 502 of 505 `.py`, component 165 of 167,
    integration 166 of 173); mocks 44 `.py`; experimentation 204 `.py`, 33 of them tests. The lane's 28 new files hold
    397 test functions (unit 331, component 23, integration 43) - the 22:02:20Z note's "312" was wrong. 22 C1
    records are stale (20 in tests_components, 2 in tests_architecture), 17 of them from earlier lanes; the suites'
    subtree counts lag earlier lanes too (unit aether +2, unit spellbook +2, component spellbook +3). The nine
    changed files are read through their CR-insensitive diffs. Found: tests_architecture's C1 header says its map is
    the union of tests_components' key files, but the map holds the 36 harness and entrypoint surfaces the document
    names; the header is corrected in this pass. Plan: a new "Managed Spell Pools Unit Cluster" (the nine
    aether/conduit files), dated Protects bullets and key files in ten clusters and the three suites, a stress flow,
    28 measured code-map records, the 22 stale ones remeasured, the counts and the 247-path core set, sources and
    handoff in both documents.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_tests_facts.txt:1-114
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_tests_names.txt:1-511
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_tests_join_before.txt:1-23
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_tests_join.py:1-113
  - context_compass/system_docs/tests_architecture.md:587-779
  - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:77-124
  IMPACT: The tests docs are written from counts and ranges measured now, not carried forward.
  NEXT: Write and run scripts/s7_docs_tests.py over tests_components and tests_architecture, then the gates.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T22:35:37Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: tests_components and tests_architecture carry the managed lane (scripts/s7_docs_tests.py, then
    s7_docs_tests_fix.py: the meld door's method is `meld_existing_spell`). tests_components: a new Managed Spell
    Pools Unit Cluster (the pool and its stress file, the Creations map and discard, the registry and its stress
    file, the lease, the meld doors, the transfer stamps), dated Protects lines in ten existing clusters with key
    files in nine, a line in each suite, the flow "Managed Pool Stress Under Eight Threads", 28 measured C1
    records and the 20 stale ones remeasured, the counts (833 modules) and the core set: 247 paths, equal to the
    247 records, with no MISSING, OUT OF BOUNDS or STALE RANGE left. tests_architecture: the inventory recounted,
    its two stale records remeasured, its C1 header corrected (a 36-path subset of that core set, not the union),
    a WORKER HANG failure mode, sources and handoff. Gates: both indexes regenerated (68 and 32 sections) and
    `--check` OK; the portability search finds nothing; one H1 each; no unclosed bracket in a heading; the
    absolute-path search matches only the recipe's `end_line:\s` code line in each document (pre-existing, not a
    path); preservation: 75 and 15 baseline lines changed, each an edited count, a remeasured C1 field, an Updated
    line or a rewritten line whose content is kept. Correction of the 22:23:27Z note: 21 of the 22 stale records
    were already stale at the 0.2.8240 commit (only test_scan_bind_option_parity.py is this lane's), and the
    subtree lags there were unit aether +3, unit spellbook +2, component spellbook +3, integration conduit +2.
  EVIDENCE:
  - context_compass/system_docs/tests_components.md:928-984
  - context_compass/system_docs/tests_components.md:1731-1748
  - context_compass/system_docs/tests_components_index.md:1-97
  - context_compass/system_docs/tests_architecture.md:587-600
  - context_compass/system_docs/tests_architecture_index.md:1-61
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_tests.py:1-618
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_docs_tests_run.txt:1-25
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_tests_join_after.txt:1-1
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_tests_preservation.txt:1-81
  IMPACT: The four system documents describe 0.2.8246; the graph is next.
  NEXT: Extract the graph with --strict and author the five new modules' semantics.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T22:58:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The graph after `extract_graph.py --strict` on 0.2.8246 (591 descriptors written, 1227 nodes, nothing
    skipped): the walker, the report of record, counts 1233 nodes in 592 descriptors - AUTHORED 1042,
    SEMANTICS_STALE 166, UNSEMANTIC 20, RETIRED 5 - the extra descriptor being the stranded
    `spellframe_kind/__init__.py` (its source is gone; no authored content). Measured against the same descriptors
    extracted from the 0.2.8240 export (scripts/s7_graph_census.py): the 10 new unsemantic nodes are the five new
    modules (a module and a class node each); 22 stale nodes were AUTHORED against 0.2.8240 and moved only by this
    lane's diff; 8 more in files this lane changed (Conduit, TransferOfOwnership, Creations, ConduitMeld, Meld,
    SpellSpaceMeld, SitePlanEmission, SpellBinder) were already stale at 0.2.8240 - prose earlier lanes wrote and
    never re-stamped; 84 moved and 60 never-stamped stale nodes, 9 unsemantic ones and the 5 retired ones
    (dag_index, ManyOnlyCodegenPlanTargetKind) sit in files this lane did not change. The extractor's census line
    (238 stale, 132 unverified) overstates: it tests the stamp's truthiness, so the 72 module nodes accepted with
    an empty stamp count as unverified there, while the walker tests the key and counts them AUTHORED, as its own
    comment says it should.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_extract.txt:1-46
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_walker_after_extract.txt:1-123
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_census_before.txt:1-201
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_graph_census.py:1-72
  - context_compass/tools/system_documents/python/graph_walker.py:91-117
  - context_compass/tools/system_documents/python/extract_graph.py:490-517
  IMPACT: The plan for the graph: author the 10 new nodes from the five modules read whole; extend the 22
    lane-moved nodes' prose with the lane's facts after reading every changed hunk of their spans
    (runs/s7_graph_prose_by_lane.txt) and accept them - their prose was verified against 0.2.8240 and the hunks are
    the only change; add the lane's facts to the 8 nodes already stale before the lane
    (runs/s7_graph_prose_pre_lane.txt) without accepting them, because their older claims were never verified;
    leave the other 144 stale, 9 unsemantic and 5 retired nodes as the backlog they were; delete the stranded
    descriptor (nothing to keep).
  NEXT: Write and run scripts/s7_graph_semantics.py, accept the 32 nodes, re-extract and assemble.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T23:04:59Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The graph describes 0.2.8246 (scripts/s7_graph_semantics.py: 76 edits in 32 descriptors). Authored from the
    modules read whole: the five new modules' 10 nodes - ManagedSpellQuantity (sizes per mode; reserve, put_back,
    abandon, adopt, destroy_object, cleanup; no reference to an object that is out), ReleaseManagedSpell (the
    hosted-root singleton shape, the copy-on-write maps, register/unregister by the stores, the release fast path
    and the cold resolver, managed, release_all, describe), ManagedSpellLease, ManagedSpellMode and
    ManagedSpellExhaustedError - and eight edges among them. The 22 nodes the lane's diff moved got the lane's facts
    and were accepted with the 10 new ones (graph_walker --accept --apply, 32 nodes in 25 descriptors); two claims
    were corrected rather than appended (SoloCodegenPlanDiscoveryStrategy declines a managed model, RecordVersion
    stamps 4.2.0) and SitePlanRuntimeHelpers' role names the lease returns; nine lane edges join them (Aether owns
    the registry, Creations owns its pools and uses the registry, Conduit creates leases, Bind uses the mode, ...).
    The 8 nodes stale since before the lane got the lane's facts and stay unaccepted. The stranded descriptor
    `spellframe_kind/__init__.py` (an untracked empty `__init__.py` extracted at 0.2.8222, gone since; no prose) is
    deleted. Re-extracted with --strict (591 descriptors, nothing skipped, new or orphaned) and assembled:
    src_graph.md 28058 lines, 591 sections all verified against their headers, 1227 nodes, 1415 edges. Walker:
    AUTHORED 1074, SEMANTICS_STALE 144, UNSEMANTIC 9, RETIRED 5, no stranded descriptor - the backlog as it was
    before the lane (census: none lane-moved, none new). Checks: src_components' Key Files join resolves all 370
    citations (218 paths) against the graph's 591 sections; the citation recipe finds nothing missing or out of
    bounds among 1407 citations in the src documents; the graph names no path into the documentation package.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_graph_semantics.py:1-490
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_accept_apply.txt:1-34
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_extract_after.txt:1-46
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_walker_after.txt:1-110
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_census_after.txt:1-169
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_assemble.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_join.txt:1-1
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_citation_recipe.txt:1-1
  - context_compass/system_docs/src_graph_index.md:1-617
  IMPACT: Docs and graph are current for 0.2.8246; the owner gets the stale backlog (144 nodes, 8 of them in this
    lane's classes; 9 unsemantic; 5 retired) as a figure for a separate verification task.
  NEXT: The README lifetimes section, docs/intermediate/scopes.md, the glossary and the release note's packaging lines.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T23:31:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The user-facing docs describe managed spells (scripts/s7_docs_user.py, s7_docs_api.py,
    s7_docs_release_api_line.py). README: "Seven Lifetimes, Not Three" adds the `managed_spell_quantity` row and a
    lease-and-release example with the three modes and the teardown rule; the teardown section's stale sentence ("A
    failing method stops that object's remaining method calls", wrong since 0.2.80) now says every declared method
    runs, newest first within a store, the failures chained and raised together once the scope has ended, and a
    managed object disposed only when its pool destroys it. probes/probe_s7_readme_examples.py runs both in both GIL
    modes: the lease, the reset on release, the same object leased again, a ninth lease of a limit-8 pool refused,
    teardown closing the 3 idle objects and none of the 5 out; `close` raising while `shutdown` still runs, the
    worker disposed before its connection. docs/curriculum.toml's selector and description follow the heading (all
    14 README selectors resolve); the scopes guide's purge table gains the managed row and a paragraph; the glossary
    defines "Managed spell". Found: docs/api.toml never got S4's four root exports, so the docs site build has
    refused the export list since 0.2.8244 ("Public API selection drift: missing=['ManagedSpellExhaustedError',
    'ManagedSpellLease', 'ManagedSpellMode', 'ReleaseManagedSpell']"); the three managed surfaces now join the
    "resolution" group (its guide is the lifetimes chapter) and the error joins "errors". docs/tests: 60 passed with
    Sphinx 9.1.0 from docs/requirements.lock in a scratch venv under the VM's /tmp (the melder venv has no Sphinx).
    The release note gains the packaging lines. The CRLF files stay CRLF: their HEAD blobs are LF and the owner's
    Windows checkout converts, so the VM's plain diff shows whole files while the CR-insensitive diff is +55/-11.
    Left out, beyond S7's boundary: architecture_and_design/02_architecture/ownership_and_lifetimes.md and
    05_engineering_drawings/README.md (with their diagrams) list six members, but that set is stamped as verified
    against Melder 0.1.2 as a whole; adding two lines would leave the stamp claiming a check nobody ran, so it is a
    follow-up for the owner.
  EVIDENCE:
  - README.md:476-527
  - README.md:568-573
  - docs/curriculum.toml:55-61
  - docs/intermediate/scopes.md:124-139
  - docs/reference/glossary.md:52-58
  - docs/api.toml:10-14
  - docs/api.toml:53-56
  - release_docs/next_version_release.md:525-539
  - src/melder/aether/conduit/creations/creations.py:401-449
  - src/melder/aether/conduit/creations/creations.py:525-578
  - src/melder/aether/conduit/meld/conduit_meld.py:211-262
  - src/melder/aether/conduit/meld/spellspace_meld.py:229-234
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s7_readme_examples.py:1-138
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_readme_examples_gil0.txt:1-5
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_readme_examples_gil1.txt:1-9
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_docs_user_selectors.txt:1-2
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_docs_tests_sphinx.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_user.py:1-186
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_api.py:1-39
  IMPACT: A reader of the README, the site or the glossary meets the seventh member with an example that runs; the
    site build accepts the root's export list again. Remaining for S7: the patch lane's archive, rubric scores,
    the review handoff and the rebuild.
  NEXT: D6 - move the patch lane to patches/completed/ and replace its 11 artifact-board rows with one cleared row.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T23:32:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The patch lane is archived: `mv -n` moved system_docs/patches/active/managed_spell_quantity_2026_10_15/
    (its eleven docs - the architecture patch, six component and four code-description patches) to
    system_docs/patches/completed/, after their content was promoted into src_architecture, src_components, the
    tests docs and the graph (the MEASURE notes above). scripts/s7_archive_patch_lane.py replaced the lane's 11 active
    artifact-board rows with one cleared promote_to_documentation row and repointed the live references (the epic's
    Dependencies and Artifact Links, this story's Artifact Links); historical Notes keep the paths they cited. The
    three evidence folders (melder_object_pools_20261011, managed_shell_spike_20261014, managed_spell_quantity_20261015)
    stay active, retained as reference under the epic.
  EVIDENCE:
  - context_compass/artifact_board.md:92-108
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:474-474
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:672-672
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:93-93
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_archive_patch_lane.py:1-53
  IMPACT: The patch-framework closure gate holds: no temporary patch doc of the lane is left under patches/active,
    and both boards agree with the tickets.
  NEXT: Score the four system documents against the quality rubric, from disk.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-15T23:39:29Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rubric scores of the four system documents, from disk after their index rebuilds (self-scored; no
    independent reviewer): src_architecture 83 (B) - fidelity 4, contract 5, depth 4, addressability 4, join 4,
    mirror 4; src_components 83 (B) - 4, 5, 4, 4, 4, 4; tests_architecture 83 (B) - 4, 5, 4, 4, 4, 4;
    tests_components 77 (B) - 4, 4, 3, 4, 4, 4. Measured by scripts/s7_rubric_checks.py: one H1 each, no duplicate
    indexed name, no unclosed heading, every contract section present and in order, no portability or absolute-path
    hit, every C1 record complete with its file present and its extent equal to the file's line count today (160,
    36, 232 and 247 records), every Key Files path resolving (218 source paths in the graph index, 244 test paths on
    disk), all 26 source and 7 test C3 entries carrying the twelve fields. Scoring found two stale claims and fixed
    them: the guardrails called the bind-guard manifest "619-entry" (628 at 0.2.8246), and the cleanup sequence and
    the Aether entry put the LoadGate and the mediator plane after the frames, while `Aether.cleanup` cleans them
    first, then the frames, ReleaseManagedSpell, the other hosted roots, a `finally` reset and the logger
    (scripts/s7_docs_architecture_guard_count.py, s7_docs_aether_cleanup_order.py; both indexes regenerated and
    checked). Why not 5: fidelity - older claims carry no citation (the Rift and Nexus failure bullets) and fifteen
    "Architecture narrative (folded in ... 2026-08-01)" blocks in src_components were not re-verified on this pass;
    depth - one-clause fields remain (examples below), and the test suite-level C3 entries describe tiers without
    naming what they protect (the clusters under them do); addressability - contract H2s that hold only
    sub-headings (Data Flows and Sequences, Diagrams, C3 Components Catalog), flagged by the slicer but selectable;
    join - every extent holds today, but 134 of 160, 34 of 36, 201 of 232 and 199 of 247 verified_at stamps were
    carried forward, and in-prose numeric citations were bounds-checked and sampled, not all opened; mirror - each
    pair shares its contract but adds different non-contract sections.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_rubric_checks.txt:1-53
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_rubric_checks.py:1-171
  - context_compass/system_docs/src_architecture.md:628-632
  - context_compass/system_docs/src_architecture.md:969-972
  - context_compass/system_docs/src_components.md:1270-1274
  - src/melder/aether/aether.py:268-361
  - tests/unit/melder/spellbook/bind/test_bind.py:114-127
  - src/melder/aether/spellbook/bind/bind.py:713-713
  - context_compass/system_docs/src_architecture.md:2205-2221
  - context_compass/system_docs/src_architecture.md:1890-1890
  - context_compass/system_docs/src_components.md:699-699
  - context_compass/system_docs/src_components.md:3329-3329
  - context_compass/system_docs/src_components.md:5686-5686
  - context_compass/system_docs/tests_components.md:379-379
  - context_compass/system_docs/tests_components.md:552-552
  - context_compass/system_docs/src_architecture_index.md:45-45
  - context_compass/system_docs/src_architecture_index.md:70-70
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:43-54
  IMPACT: All four documents are band B and usable as inputs; the weakest is tests_components (depth 3). The next
    refresh should restamp verified_at where extents were checked, cite the Rift and Nexus failure modes, and re-verify
    the folded August narratives in src_components.
  NEXT: S7 to review - this story's handoff, the epic's Milestone 4 and synthesis note, the board row; rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T00:01:08Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The rebuild ran last, after every S7 edit of the README, docs, release note, the four system docs with their
    indexes and the graph: the asset runner wrote the agent-documentation (468 entries), bind-guard (628 entries) and
    system-documents (4 entries) manifests for 0.2.8246, and its `--check` printed three OK lines. The LLM builder
    (`--include-untracked`, the lane's new files being untracked) rewrote the "other" corpus (404 files: the README,
    docs and release note moved) and left src and tests unchanged - its classifier excludes the generated
    `_build_assets` manifests and payloads and everything under context_compass/ - and its `--check` printed three
    OK lines, so the ticket and board edits after the rebuild leave both checks valid. The packaged architecture
    payload carries the scoring fix (the 628-entry sentence). The graph descriptor of a regenerated payload module
    lags the rebuild by one pass (src_architecture_payload: descriptor sha256 8a526db44e5d..., file f6a2281bd2e4...;
    mechanical tier only): re-extracting would change the graph the payloads embed, so it waits for the next lane's
    rebuild. Not run: hosted CI and coverage (the owner's).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_rebuild_assets.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_rebuild_assets_check.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_llm_support.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_llm_support_check.txt:1-3
  - llm_support/_builder.py:62-100
  - src/melder/_build_assets/_system_documents/payloads/src_architecture_payload.py:649-649
  IMPACT: S7's EXIT_GATE holds except the owner's acceptance of the epic; Milestone 4 is met.
  NEXT: The owner accepts the epic (S1-S7) or redirects, and rules on stamping parked versions.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user (2026-10-16T00:03:22Z, the owner report)
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S7 - benchmarks, docs, graph, README, release note, patch promotion, rebuild; no `src/` change, no notch.
- State: blocked on the owner's acceptance (board: review), 0.2.8246. Done: the benchmarks (no regression;
  MEASURE), the patch lane aligned (FACT), src_architecture, src_components, tests_components and
  tests_architecture promoted with their indexes, the graph re-extracted, authored and assembled (144 stale and 9
  unsemantic nodes remain from before the lane, 8 of the stale ones in its classes), and the user docs written -
  README lifetimes and teardown sections, the docs curriculum, scopes guide, glossary, the site's API selection
  (S4's four exports were missing) and the release note's packaging lines (MEASURE notes). Then: the patch lane
  archived and both boards synced (FACT), the rubric scores (MEASURE: 83, 83, 83, 77; two stale claims fixed while
  scoring), and the rebuild, last: both checks print only OK (MEASURE).
- Next: S8 (tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md, the owner's 2026-10-16 follow-ups)
  lands after melder_1's fix and updates these docs; then the owner accepts the epic and S7 closes with it. The
  architecture_and_design lifetimes are a backlog task now
  (tickets/tasks/backlog/2026-10-16_refresh_architecture_and_design_lifetimes_task.md).
- Docs custody: the system docs, their indexes and the graph are free for melder_1's landing (the epic's DECISION
  note of 2026-10-16T00:21:04Z); S7 edits them again only after that landing.
- Limits: codex_bridge `list_threads` fails ("Codex app tool request failed", again at re-onboarding); hosted CI
  and coverage are the owner's (Not run).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
