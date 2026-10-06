

# Task: Promote the host read surface into the system documents and remap the citations it shifted

## Metadata
- Task ID: TASK-2026-09-29-promote-host-read-surface-into-system-docs
- Story: none; follow-up of EPIC-2026-09-29-host-integration-read-surface (closed by owner turn-in)
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-29T22:27:07Z
- Updated: 2026-10-01T10:53:21Z

- Completed: 2026-10-01T10:53:21Z
- Summary: src_architecture, src_components, tests_components, docs/intermediate/scopes.md, the graph and the
  release note describe the 0.2.8208 frame lookups and read accessors; the 13 shifted citations and every
  aether.py citation remapped; assets and LLM bundles rebuilt (both checks OK). No source change, no notch.

## Objective
Parked at the owner's turn-in of the host read surface lane (chat, 2026-09-29: "add the details to the new release
and keep the version update then turn in your shit don't rebuild assets"). The source, tests, release note and the
0.2.8208 wheel landed; the canonical documents did not. This task brings them current when the owner schedules
it: describe `Aether.find_frame` / `get_frame` / `list_frame_names` and the read accessors in src_architecture,
src_components and tests_components; add the scopes.md paragraph; update the graph; and fix the 13 `path:line`
citations that the lane's insertions moved.

## Ticket Contract
- ENTRY_GATE: owner schedules it; board row; preservation baselines RE-CAPTURED at the start of the pass (the ones in
  artifacts/host_read_surface_20260929/docs/preservation/ describe the documents as of 2026-09-29T22:00Z).
- EXECUTION_BOUNDARY: context_compass/system_docs (the three documents, their indexes, the graph descriptors of the
  five touched nodes, the assembled graph), docs/intermediate/scopes.md, then assets and LLM bundles last.
- DEPENDENCIES: system_docs/patches/completed/host_read_surface_2026_09_29/ (the contracts to promote, archived
  without promotion); tickets/tasks/completed/2026-09-29_implement_frame_lookups_and_read_accessors_task.md.
- EXIT_GATE: the three documents describe the new calls; the 13 citations resolve to the same code as before the
  insertions; C1 entries of the five files remeasured; indexes current; both portability checks empty;
  preservation diff explained; graph assembled with the touched nodes read and accepted; assets and LLM bundles
  rebuilt with both checks OK.
- FAILURE_ESCALATION: CONFLICT if a document contradicts the landed source; BLOCKER if the graph tooling refuses.

## Scope Boundaries
- In scope: the objective above.
- Out of scope: source changes; the parked atomic-retirement story.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-01T10:53:21Z) the owner turned it in in chat, confirming the acceptance criteria.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-01T10:47:23Z) the exit gate is met short of the owner's acceptance: documents,
  indexes, graph, release note, assets and LLM bundles current, both checks OK (MEASURE notes 10:27Z-10:44Z);
  the five graph nodes stay unaccepted by DECISION (10:27:49Z); follow-ups parked in a backlog task.
- from_state: draft
- to_state: in_progress
- transition_reason: (2026-10-01T10:05:33Z) the owner scheduled it in chat (2026-10-01, "System docs catch-up");
  ticket out of the backlog and board row before any edit. Earlier: draft -> draft (parked) below.
- from_state: draft
- to_state: draft
- transition_reason: Created parked at the owner's turn-in; awaits scheduling.

## Steps / Checklist
- [x] Re-capture preservation baselines; read the three authoring instructions again.
- [x] Remap the 13 shifted citations (list below), each checked at its new line.
- [x] src_architecture: System Boundary list, Operational Invariants (noncreating, no lease, no lock), Failure
      Modes (get_frame ValueError, TypeError), a Frame Lookups diagram, C1 remeasure, Information Sources, handoff.
- [x] src_components: Aether Singleton responsibilities/invariants/failure modes, Subcomponent: Aether Frame
      Registry, AethericFrame Services (shared configuration, posture `frozen`), Spellbook Configuration (`frozen`,
      `aether_frame`), Conduit Runtime (`spellbook`), a lookup call flow, C1 entries, handoff.
- [x] tests_components: the two new test files (component list, C1 entries, sources, handoff).
- [x] scopes.md paragraph; graph extract (--strict), author, accept, assemble
      (accept deliberately not done: DECISION 2026-10-01T10:27:49Z).
- [x] Indexes, portability checks, preservation report; assets and LLM bundles last.

## Citations shifted by the 0.2.8208 insertions (old -> new; each checked 2026-09-29T22:08Z)
- src_architecture.md:425-427 conduit.py 5280->5309, 5352->5381, 5370->5399, 5425->5454, 5448->5477, 5496->5525
- src_architecture.md:864 and src_components.md:2543 conduit.py 5229-5231 -> 5258-5260 (link isinstance check)
- src_architecture.md:1271 aetheric_frame.py 691-752 -> 726-787 (bind_frame_configuration unfrozen branch)
- src_components.md:469 conduit.py 5329, 5405, 5485 -> 5358, 5434, 5514 (transaction mediator reads)
- src_components.md:984 spellbook_configuration.py 277-343 -> 329-395 (freeze)
- src_components.md:1227 aetheric_frame_configuration.py 1984 -> 2008 (SafeGuard pair)
- src_components.md:1267 aetheric_frame.py 759-770 -> 794-805 (conflicting posture warning)
- src_components.md:5185, 5188, 5191 conduit.py 5352, 5425, 5496 -> 5381, 5454, 5525
- src_components.md:5204 conduit.py 5280, 5370, 5448 -> 5309, 5399, 5477
- src_components.md:9478 aetheric_frame.py 867 -> 902 (find_index_for_spell)
- Offsets: aether.py +149 from 1687; aetheric_frame.py +35 from 591; aetheric_frame_configuration.py +24 from 1500;
  spellbook_configuration.py +52 from 219; conduit.py +29 from 1910. File lengths now 2839, 1180, 2074, 1479, 7131.
  Document line numbers above are as of 2026-09-29T22:00Z and move with any edit.

## Deliverables
- The three documents, their indexes, scopes.md and the graph current for 0.2.8208; assets and bundles rebuilt.

## Validation
- Asset --check OK (VM mirror and device) and LLM --check --include-untracked OK (device), 2026-10-01T10:44Z.
- VM mirror, GIL off: package-root unit files, build_assets, agent-text reader and multithreaded
  document-view tests: 299 passed, 24 skipped. Full suite: Not run (no src or test change). Coverage: Not run.

## Risks / Rollback Notes
- Until this runs, the packaged system documents do not mention the new calls, and the 13 citations above point
  24 to 52 lines away from the code they name.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No graph acceptance without reading the node's source against its prose.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/host_read_surface_2026_09_29/
  - artifacts/host_read_surface_docs_20261001/
- DISPOSITION: promote_to_documentation (the patch contracts, promoted by this pass); retain_as_reference (the
  edit evidence). Input only, not this ticket's artifact: artifacts/host_read_surface_20260929/ (cleared under the
  implementation task).
- CLEANUP_TRIGGER: task closure

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
- DATETIME: 2026-09-29T22:27:07Z
  TYPE: DECISION
  CLAIM: Parked at the owner's turn-in (chat, 2026-09-29) of the host read surface lane: release note written,
    version kept at 0.2.8208, asset rebuild waived, canonical documents not yet promoted. The shifted-citation
    list above was verified line by line on 2026-09-29.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-29_implement_frame_lookups_and_read_accessors_task.md
  - context_compass/system_docs/patches/completed/host_read_surface_2026_09_29/architecture_patch.md:1-75
  IMPACT: The documentation gap stays visible instead of living only in chat.
  NEXT: Wait for the owner to schedule it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:15:27Z
  TYPE: MEASURE
  CLAIM: Entry gate met. Preservation baselines re-captured (the three documents and their indexes, the graph and
    its index, scopes.md; sha256 and line counts in the manifest). The three authoring instructions, the four
    examples, the patch-contract skills and the five archived patch contracts were read. The eight landed calls
    were read in source: `Aether.find_frame` / `get_frame` / `list_frame_names` over `_find_registered_frame`
    (noncreating, "default" included; one `dict.get` or one `dict.copy()`, no Aether lock; a frame that reads
    `cleaned` is absent; TypeError for a non-string name, `get_frame` ValueError when absent),
    `AethericFrame.shared_spellbook_configuration` (gated by the posture's sharing flag, None before a Book binds
    one), `AethericFrameConfiguration.frozen` and `SpellbookConfiguration.frozen` (read under the object's lock),
    `SpellbookConfiguration.aether_frame` (fixed at construction) and `Conduit.spellbook` (borrowed). The 13
    shifted citations still point 24-52 lines off; conduit.py, aetheric_frame.py, aetheric_frame_configuration.py
    and spellbook_configuration.py are unchanged since 0.2.8208, and each 2026-09-29 target was re-read at its
    current line.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_docs_20261001/baseline_manifest.txt:1-19
  - src/melder/aether/aether.py:1799-1946
  - src/melder/aether/aetheric_frame/aetheric_frame.py:591-624
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1500-1522
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:219-269
  - src/melder/aether/conduit/conduit.py:1910-1937
  - context_compass/artifacts/host_read_surface_docs_20261001/citation_remap.txt:1-85
  IMPACT: The documents can describe the calls from source, and the 13 remaps are verified, not copied forward.
  NEXT: Record the aether.py citation finding, then the PLAN note.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:15:27Z
  TYPE: CONFLICT
  CLAIM: The documents' other numeric citations into aether.py were read against source too: of 16, six still hold
    (17-19, 209-222 twice, 222, 320-332, 334-337) and ten do not. My own 0.2.8213 insertion
    (`process_wide_unique_spell_ids`, 43 lines at 762) moved three of them and I did not remap them then: the
    `aetheric_mediator` property (762-795 -> 805-838) and `_frame_creation_transaction` (1288-1333 -> 1331-1376,
    cited twice). The rest were already stale: `_instance` 100 -> 116, double-checked `__new__` 114-118 ->
    130-134, the `__init__` body 174-250 -> 175-251, `_ensure_frame` 893 -> 1187, `_ensure_default_frame` 323 ->
    385, the plane-admission block 1243-1264 -> 1225-1249. And the src_architecture invariant the first ones back
    is wrong about the mechanism: it says teardown is IDENTITY-CHECKED ("only cleared when `Aether._instance is
    self`"), but `cleanup()` resets `_instance` and `_initialized` unconditionally in its `finally` (BUG-149,
    2026-07-17); only the construction-failure rollback in `__init__` checks identity. A stale instance still
    cannot unseat a live one, because its `cleanup()` returns at the `_cleaned` check first. A heuristic pass
    over all 177 numeric citations in the three documents flags 26 suspects: the 13, the aether.py ones above,
    and 16 into other files (mutation_research.py 6, bind.py 4, spellbook.py 2, spellbook_creation_system.py 2,
    crystallizer.py 1, an analyzer strategy 1), not verified by reading.
  EVIDENCE:
  - src/melder/aether/aether.py:120-134
  - src/melder/aether/aether.py:175-251
  - src/melder/aether/aether.py:253-337
  - context_compass/artifacts/host_read_surface_docs_20261001/citation_remap.txt:1-85
  - context_compass/artifacts/host_read_surface_docs_20261001/citation_heuristic_audit.txt:1-27
  IMPACT: Evidence for the subsystem this pass documents would mislead a reader, and one invariant describes a
    mechanism the code no longer has. The source wins; the documents are corrected in this pass.
  NEXT: PLAN note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T10:15:27Z
  TYPE: PLAN
  CLAIM: One apply script per document (artifacts/host_read_surface_docs_20261001/apply/); every anchor must
    match once, nothing is written otherwise, and added lines stay within 120 characters. (1) src_architecture:
    the boundary list gains the frame lookups and the five accessors; Operational Invariants gains "Frame
    lookups never create a frame" with evidence; Failure Modes gains the lookup errors; Diagrams gains Frame
    Lookups (ASCII and Mermaid); the three citations of the 13 and the four aether.py ones are remapped and the
    teardown sentence follows the source; C1 entries remeasured (aether.py, aetheric_frame.py, conduit.py,
    spellbook_configuration.py) plus aetheric_frame_configuration.py; Information Sources; handoff.
    (2) src_components: Aether Singleton (responsibility, invariant, failure mode, Observability's error-site
    count 19 -> 21), Subcomponent: Aether Frame Registry, AethericFrame Services (shared configuration; the
    posture's `frozen`; aetheric_frame_configuration.py into Key Files), Spellbook Configuration (`aether_frame`,
    `frozen`), Conduit Runtime (`spellbook`), a new Flow: Aether Frame Lookup, the other ten of the 13 and the six
    stale aether.py citations, C1 entries, Information Sources, handoff. (3) tests_components: the two test files
    in their clusters and the C1 core set. (4) docs/intermediate/scopes.md: one paragraph. (5) Graph: walker
    report for the five nodes, author and accept after reading, extract --strict, assemble. (6) Release note: one
    Packaging and documentation bullet. (7) Indexes, the documents' citation recipe, portability checks,
    preservation diffs, rubric scores. (8) Assets and LLM bundles last, both --check OK. No src change, so no
    notch. Out of scope and filed as a backlog task: the 16 heuristic suspects into other files. melder_0 is the
    only writer of these files until the lane closes; NOTICE to fable_0, melder_2 and muse_0 (muse_0's
    defect_hunting_fixes_1 lane edits src_components, last updated 2026-09-27).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-29_promote_host_read_surface_into_system_docs_task.md:49-75
  - context_compass/system_docs/patches/completed/host_read_surface_2026_09_29/architecture_patch.md:1-75
  - context_compass/artifacts/host_read_surface_docs_20261001/citation_remap.txt:1-85
  IMPACT: The pass is bounded: the 0.2.8208 calls, the 13 citations and aether.py's citations; nothing else moves.
  NEXT: Send the NOTICEs, then apply src_architecture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T10:19:02Z
  TYPE: MEASURE
  CLAIM: src_architecture applied (apply_docs_architecture.py, every anchor matched once): the boundary list names
    the three lookups and five accessors; Operational Invariants carries "Frame lookups never create a frame";
    Failure Modes carries the get_frame ValueError and the TypeError/RuntimeError cases; Diagrams carries Frame
    Lookups (ASCII and Mermaid, separating Spellbook creation from the lookups that create "default"); the
    singleton invariant states the identity-checked construction rollback and the unconditional teardown reset
    with remapped evidence; six citations remapped; C1 remeasured for the four files and the posture module
    added; Information Sources and handoff updated. The index is regenerated and --check reports it current
    (58 sections, 3487 lines). Checks still to run with the other documents: citation recipe, portability,
    preservation diff.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:455-459
  - context_compass/system_docs/src_architecture.md:971-987
  - context_compass/system_docs/src_architecture.md:1301-1316
  - context_compass/system_docs/src_architecture.md:1476-1480
  - context_compass/system_docs/src_architecture.md:2880-2902
  - context_compass/system_docs/src_architecture.md:3177-3183
  IMPACT: The architecture map describes the 0.2.8208 calls and its Aether evidence points at the code.
  NEXT: Apply src_components.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:22:28Z
  TYPE: MEASURE
  CLAIM: src_components applied (apply_docs_components.py, every anchor matched once): the Aether Singleton entry
    (responsibility, the noncreating-lookup invariant, the lookup failure modes, error-site count 21), the Aether
    Frame Registry subcomponent (creators versus lookups, lock-free reads), AethericFrame Services
    (`shared_spellbook_configuration`, the posture's `frozen`, aetheric_frame_configuration.py into Key Files),
    Spellbook Configuration (`aether_frame`, `frozen` and its lock), Conduit Runtime (`spellbook`), a new Flow:
    Aether Frame Lookup; the ten citations of the 13 and six stale aether.py citations remapped; C1 remeasured
    (four files) and the posture module added; Information Sources; handoff. Index regenerated, --check current
    (148 sections, 10457 lines). Found while checking the C1 join: the core set already differs from the C3
    Key Files union (12 key files have no entry, 19 entries are named by no Key Files list); recorded in the
    handoff, not changed here.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:1136-1145
  - context_compass/system_docs/src_components.md:5565-5580
  - context_compass/system_docs/src_components.md:1222-1225
  - context_compass/system_docs/src_components.md:1301-1306
  - context_compass/system_docs/src_components.md:974-976
  - context_compass/system_docs/src_components.md:2588-2591
  - context_compass/system_docs/src_components.md:6724-6733
  - context_compass/system_docs/src_components.md:10088-10095
  IMPACT: The component map carries each new call where its component lives, and its evidence points at code.
  NEXT: Read the two test files and tests_architecture_instructions, then apply tests_components.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:24:35Z
  TYPE: MEASURE
  CLAIM: tests_components applied (apply_docs_tests.py): test_configuration_read_accessors.py joins the
    Aether/Nexus/Rift unit cluster and test_aether_frame_lookups.py the Aether integration cluster, each with what
    it protects, read from the two files; both enter the C1 code map measured (80 and 275 lines) and Information
    Sources; the core set is 206 and still equals the Key Files union; the tier counts were re-counted (unit
    468/471, component 149/151, integration 149/156, 766) and match, so none changed. Index current (66
    sections, 2790 lines). docs/intermediate/scopes.md gains one paragraph on the frame lookups and the reads
    (apply_user_docs.py; the file's mixed line endings kept, the new lines LF like their neighbours).
  EVIDENCE:
  - context_compass/system_docs/tests_components.md:890-892
  - context_compass/system_docs/tests_components.md:1260-1265
  - tests/integration/melder/aether/test_aether_frame_lookups.py:1-275
  - tests/unit/melder/aether/test_configuration_read_accessors.py:1-80
  - docs/intermediate/scopes.md:61-73
  IMPACT: The test map and the user guide carry the 0.2.8208 surface.
  NEXT: Graph: walker report for the five nodes, then author, accept and assemble.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:27:49Z
  TYPE: MEASURE
  CLAIM: Graph: the mechanical tier of the five descriptors was already current (each lists the new methods and
    its source_sha256 matches the file), so the extractor was not re-run in write mode; its --check reports
    new=0, orphaned=0, skipped=0 and the standing census (204 stale, 9 unsemantic), and the only descriptors whose
    source moved are eight generated build-asset modules the rebuild rewrites every pass. Aether's node already
    named the three lookups; one responsibility each was authored on AethericFrame, AethericFrameConfiguration,
    SpellbookConfiguration and Conduit (apply_graph_semantics.py, extractor format checked first), and
    src_graph.md was reassembled (27573 lines, 584 ranges verified, index line count and hash recomputed and
    equal, no tooling path). Release note: one Packaging and documentation bullet; header and rebuild line stay
    0.2.8215 (no notch); CRLF kept.
  EVIDENCE:
  - context_compass/system_docs/src_graph.md:886-886
  - context_compass/system_docs/src_graph.md:955-955
  - context_compass/system_docs/src_graph.md:4458-4458
  - context_compass/system_docs/src_graph.md:6060-6060
  - release_docs/next_version_release.md:335-339
  IMPACT: The generated graph names the four reads; the release note records the documentation catch-up.
  NEXT: Run the checks: indexes, citation recipe, portability, preservation diffs.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:27:49Z
  TYPE: DECISION
  CLAIM: The five touched nodes are NOT accepted, against this ticket's own exit-gate wording ("touched nodes read
    and accepted"). Accepting stamps that every authored line of the node matches its source; for Aether (2954
    lines), Conduit (7131) and the other three that means auditing all of their existing prose, which this pass
    did not do - it read only the members it documents. So they stay SEMANTICS_STALE with the pre-existing
    204-node census, as in the earlier lanes; the four new responsibilities were each checked against the member
    they describe.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/src_graph_generation.md:118-131
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/apply/note_graph.txt:1-19
  IMPACT: No stamp claims a verification that was not done; the stale census is unchanged.
  NEXT: Run the checks.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:29:19Z
  TYPE: MEASURE
  CLAIM: Checks on the files as written. Indexes: src_architecture (58 sections, 3487 lines), src_components (148,
    10457), tests_components (66, 2790) and the graph (584 ranges) are current. Content preservation: every
    baseline line is still present except the ones this pass replaced on purpose - 27 in src_architecture, 30 in
    src_components, 2 in tests_components, 0 in scopes.md, each a remapped citation, a remeasured C1 field, an
    Updated date, a count, or the singleton and frame-registry text the notes record. Portability: no tooling path
    or absolute path in the three documents. Citation recipe: nothing missing or out of bounds. Joins: 149 and 227
    cited source paths resolve into the graph index; 206 test paths exist. Rubric, src_architecture (read whole
    this session; scored from the file on disk): Fidelity 4 (two numeric citations the heuristic flags remain
    unread), Contract 5, Depth 4 (one-clause invariants, e.g. the frozen-configuration line), Addressability 3
    (container H2s such as Diagrams wrap H3 units), Join 3 (most C1 ranges carried forward), Mirror 3
    (tests_architecture not re-checked) = 75, band B. src_components and tests_components are not re-scored: the
    rubric needs a whole-document re-read with per-entry depth, which this pass did not do; their joins are above.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_docs_20261001/checks.log:1-71
  - context_compass/system_docs/src_architecture.md:2725-2727
  - context_compass/system_docs/src_architecture.md:1327-1327
  IMPACT: The documents are structurally sound and their new evidence resolves; the scores say where they are weak.
  NEXT: Rebuild assets and LLM bundles, then both checks.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:37:57Z
  TYPE: MEASURE
  CLAIM: The asset rebuild cannot run on the device tree: `write_payloads` deletes every existing payload before it
    writes (stale-payload clearing) and the connected folder refuses deletes, so the run raised PermissionError on
    the first payload. By then it had written three files at v0.2.8215 - the agent documentation manifest (460
    entries), the bind guard manifest (619 entries) and `system_documents_index.py`, because `write_manifest`
    writes the index before the payloads. The payloads, the graph adjacency and the system documents manifest are
    still the 2026-09-30 copies, so the device's assets disagree with each other until the rebuild finishes. No
    temporary file and no .git/index.lock was left. The previous lane met the same refusal: it rebuilt in the VM
    mirror, copied the changed manifest and payload files back with copy_back_assets.py, and ran the LLM builder
    on the device.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_docs_20261001/rebuild_assets.log:1-24
  - src/melder/_build_assets/_system_documents/_builder.py:542-626
  - src/melder/_build_assets/_system_documents/_builder.py:974-1001
  - context_compass/tickets/tasks/completed/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md:429-450
  IMPACT: The device's build assets are half-written; turn-in waits on finishing the rebuild.
  NEXT: Compare the asset inputs between the device and the VM mirror, bring the mirror to the device's versions,
    run the asset runner there and copy the results back.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:40:47Z
  TYPE: MEASURE
  CLAIM: The asset inputs of the device tree and the VM mirror differ only in this lane's six system documents and
    indexes: all 583 Python files under src/melder hash equal in the newline-canonical form both code builders
    hash (compare_asset_inputs.py), so once those six are copied in, the mirror rebuild sees the device's inputs.
    The two manifests the failed device run wrote equal the mirror's apart from line endings. They and
    system_documents_index.py are LF now, while the device's other generated assets are CRLF, the checkout's
    convention (HEAD stores them LF; .gitattributes pins LF only for system_docs Markdown and llm_support, and
    fingerprints fold CRLF). The copy-back helper is adapted to write CRLF for generated .py files, so those three
    return to the checkout's form; it still never deletes.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/compare_asset_inputs_before.log:1-9
  - context_compass/artifacts/host_read_surface_docs_20261001/apply/compare_asset_inputs.py:1-186
  - .gitattributes:23-50
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/copy_back_assets.log:1-8
  IMPACT: The rebuild can run in the mirror with no other input to reconcile, and the copy-back leaves the device
    tree in the form it had before the failed run.
  NEXT: Copy the six documents into the mirror, run the asset runner there, copy back, --check on the device.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:44:56Z
  TYPE: MEASURE
  CLAIM: Rebuild, last. The six system documents were copied into the VM mirror (its asset inputs then equal the
    device's) and the asset runner wrote the three manifests there at v0.2.8215 (agent documentation 460 entries,
    bind guard 619, four system documents, no refusal); its --check is OK. copy_back_assets.py wrote 7 of the 8
    generated files to the device, CRLF: the three payloads and the system documents manifest changed content;
    the agent documentation and bind guard manifests (back to their 2026-09-30 bytes) and the system documents
    index changed line endings only; the graph adjacency manifest was already current (no edge changed). The
    device's asset --check is OK for all three, and each device payload, executed alone, embeds its document byte
    for byte with the index's sha256 and line count. The LLM builder on the device (--include-untracked,
    GIT_OPTIONAL_LOCKS=0) rewrote the other bundle (scopes.md, the release note) and left src and tests unchanged
    (build-asset outputs are outside its corpora); its --check is OK for all three. No .git/index.lock. In the
    mirror the package-root unit files, build_assets, the agent-text reader and the multithreaded document-view
    tests pass with the GIL off: 299 passed, 24 skipped. Coverage: Not run.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/compare_asset_inputs_sync.log:1-15
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/rebuild_assets_vm.log:1-3
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/check_assets_vm.log:1-3
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/copy_back_assets.log:1-9
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/check_assets_device_final.log:1-3
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/device_payload_roundtrip.log:1-3
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/rebuild_llm_device.log:1-4
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/check_llm_device.log:1-3
  - context_compass/artifacts/host_read_surface_docs_20261001/runs/post_rebuild_package_root_vm.log:1-6
  - context_compass/artifacts/host_read_surface_docs_20261001/apply/copy_back_assets.py:1-149
  IMPACT: The exit gate is met short of the owner's acceptance: documents, indexes, graph, assets and LLM bundles
    are current and both checks print only OK.
  NEXT: File the follow-up backlog task, then move this task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T10:47:23Z
  TYPE: DECISION
  CLAIM: The follow-ups this pass found but did not work are parked in one backlog task: the 16 heuristic suspect
    citations into other files (unread), the src_components core-set drift, and a stale count found while
    verifying the rebuild - both documents say the bind guard holds 582 entries, the manifest holds 619. The task
    is linked to the audit list on the artifact board. Nothing else is open in this lane.
  EVIDENCE:
  - context_compass/tickets/tasks/backlog/2026-10-01_audit_remaining_system_document_citations_task.md:1-145
  - context_compass/system_docs/src_architecture.md:534-535
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:16-19
  - context_compass/artifact_board.md:90-90
  IMPACT: The lane closes on its own scope; the known defects stay visible.
  NEXT: Move to review, NOTICE fable_0, melder_2 and muse_0, report to the owner for turn-in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T10:53:21Z
  TYPE: DECISION
  CLAIM: The owner turned the task in (chat: "ok cool continue doing work and finish turning in your shit"),
    confirming the acceptance criteria. Closure: the ticket moves to completed, its board row becomes a closed
    anchor, both artifact rows move to cleared (the patch contracts promoted, the edit evidence retained), and
    melder_0 releases the M0-160..162 claims except src_architecture, src_components and their indexes, which the
    backlog audit task takes next on the same direction ("continue doing work").
  EVIDENCE:
  - context_compass/tickets/tasks/backlog/2026-10-01_audit_remaining_system_document_citations_task.md:1-145
  - context_compass/artifact_board.md:88-90
  IMPACT: This lane is closed; the follow-up starts from its own ticket.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Turned in 2026-10-01T10:53:21Z (owner). src_architecture, src_components, tests_components, scopes.md, the graph
and the release note describe the 0.2.8208 frame lookups and read accessors; the 13 shifted citations and every
aether.py citation point at their code; the singleton invariant states what teardown does. Indexes current,
assets rebuilt in the VM mirror and copied back (CRLF), LLM bundles rebuilt; both checks OK. No src change, no
notch. The five graph nodes stay SEMANTICS_STALE (DECISION 10:27:49Z). Open elsewhere: the backlog audit task.
Next: the owner's turn-in. Scheduled by the owner 2026-10-01T10:05:33Z.
Parked 2026-09-29T22:27:07Z. Start with the Entry Gate (fresh baselines), then the citation list, then the
three documents.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
