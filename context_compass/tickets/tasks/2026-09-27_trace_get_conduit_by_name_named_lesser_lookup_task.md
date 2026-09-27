

# Task: Find why Aether.get_conduit_by_name reports existing named lesser scopes as not found

## Metadata
- Task ID: TASK-2026-09-27-trace-get-conduit-by-name-named-lesser-lookup
- Story: none
- Status: review
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T09:45:42Z
- Updated: 2026-09-27T10:07:50Z

## Objective
Owner report (ledger item MF7, logged outside this repository): `Aether.get_conduit_by_name` finds only root
conduits and reports "not found" for a named lesser (group) scope that exists. Owner intent: the lookup finds
any named conduit. Establish from source where a named lesser's name is registered, what the lookup reads and
why the two miss each other; reproduce it; put fix options to the owner. No src edits in this task until the
owner approves a plan.

## Ticket Contract
- ENTRY_GATE: active board row routes here; M2-12 consumed into Notes; every finding noted before the next
  tranche.
- EXECUTION_BOUNDARY: read-only across `Aether.get_conduit_by_name`, the `ConduitCloud` named directory, the
  `AethericFrame` conduit registries, the `Conduit` named-lesser publication and retirement paths, and their
  tests; a repro probe under `artifacts/`. No src or test edits.
- DEPENDENCIES: named lesser scope contract (2026-09-23; src_architecture, Operational Invariants). None open.
- EXIT_GATE: cause stated from source that was read (not a search hit); repro result recorded, or "Not run"
  with the reason; fix options with public-API impact; owner decision recorded.
- FAILURE_ESCALATION: DECISION_REQUEST if the intended lookup semantics are ambiguous (pooled or idle names,
  cross-frame names, what an Aether-level lookup may return); CONFLICT if documents and source disagree.

## Scope Boundaries
- In scope: every by-name conduit lookup the public API offers and the registries behind them; where and when a
  lesser's name is published and retired.
- Out of scope: changing named-lesser lifecycle, pooling, Nexus publication or crystallizer replay, unless the
  cause sits there (then raise it).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner instruction in chat, 2026-09-27 ("Look into this please ... get conduit by name should
  actually allow the user to find any named conduit").
- from_state: in_progress
- to_state: review
- transition_reason: Cause evidenced from source and reproduced in both modes; fix plan and owner decisions D1/D2
  recorded in Notes (2026-09-27T09:58:06Z).

## Steps / Checklist
- [x] Consume M2-12 into Notes; open the board row.
- [x] Descend: src_architecture named-lesser invariant -> components index -> ConduitCloud / Aether / Conduit
      slices -> graph index -> graph slices -> the code.
- [x] Read `Aether.get_conduit_by_name` and every registry it consults; read where
      `create_lesser_conduit(name=...)` publishes and retires the name.
- [x] Reproduce with a probe, or record "Not run" with the reason.
- [x] Fix options with a recommendation; owner decision.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidenced cause, repro result and a fix plan (files, symbols, tests, docs) for owner approval.

## Files / Paths Impacted
- None in src or tests during this task. Candidate files after approval (PLAN note):
  - src/melder/aether/aether.py
  - tests/unit/melder/aether/test_aether.py
  - tests/integration/melder/aether/test_aether_named_lesser_lookup.py (new)
  - system_docs patch lane, src_components, src_architecture, indexes, release note, `__version__`

## Validation
- Probe only (MEASURE note, 3.14.7t and 3.14.7). Suites: Not run.
- Recommended commands (3.14.7t venv; repeat with the GIL build):
  - `python -m pytest tests/unit/melder/aether/test_aether.py -q`
  - `python -m pytest tests/integration/melder/aether -q`

## Risks / Rollback Notes
- An Aether-level lookup that returns lessers must not hand out idle pooled shells or grant a lease ("borrowed
  discovery grants no lease"), and must keep names frame-wide unique.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behaviour claim cited to a search hit; every range covers the logic that was read.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/conduit_name_lookup_20260927/probe_named_lesser_lookup.py
  - artifacts/conduit_name_lookup_20260927/results_20260927.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: ticket closure

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
- DATETIME: 2026-09-27T09:45:42Z
  TYPE: FACT
  CLAIM: Consumed M2-12 (melder_2 -> melder_0, NOTICE, 2026-09-26T22:41:56Z, no ACK requested): assets and LLM
    bundles were rebuilt at 0.2.74, and an empty .git/index.lock sat on the device at 22:21:52Z. Re-checked at
    09:44:37Z: `__version__` is 0.2.78 (other lanes notched overnight) and the lock is gone (ls). A fix from this
    lane notches above the version current when it lands; git on the device stays read-only, GIT_OPTIONAL_LOCKS=0.
  EVIDENCE: src/melder/__version__.py:12-12
  IMPACT: Version baseline for any fix; git hazard for history reads during the investigation.
  NEXT: Slice the named-lesser invariant, then descend to Aether.get_conduit_by_name and ConduitCloud.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T09:46:53Z
  TYPE: HYPOTHESIS
  CLAIM: The documents put a named lesser's name in ConduitCloud's own named directory (`_named_conduits`,
    `_conduit_names_by_id`), separate from the frame-owned normal-root `_conduits` map the Cloud only borrows.
    If `Aether.get_conduit_by_name` reads the root map (or a root-only frame getter), a live named lesser is
    invisible to it, which matches the owner's report. Evidence of intent only; the lookup body is not read yet.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:991-998
  - context_compass/system_docs/src_components.md:5347-5364
  - context_compass/system_docs/src_components.md:6245-6256
  IMPACT: If confirmed, the defect is in the lookup, not in lesser registration; the fix would consult the Cloud
    directory rather than change how lessers are published.
  NEXT: Read Aether.get_conduit_by_name, ConduitCloud's named-directory methods and the Cloud registration in
    Conduit._link_new_lesser_under_lock, in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T09:48:32Z
  TYPE: FACT
  CLAIM: Cause, from source. `Aether.get_conduit_by_name` delegates to `Aether._get_conduit_by_name`, which resolves
    only through the frame's root maps (`_conduit_ids_by_name` -> `_conduits`) and never reads the frame's
    ConduitCloud. `AethericFrame.register_root_conduit` publishes a named root into BOTH the Cloud directory and the
    root maps; `Conduit._link_new_lesser_under_lock` publishes a named lesser into the Cloud directory ONLY (lessers
    never enter root ownership, by design). So Aether raises "Conduit with name X not found." for a live named
    lesser, while `ConduitCloud.get_conduit_by_name` (reachable today via `Aether.get_conduit_cloud(frame)`)
    returns it. The HYPOTHESIS above is confirmed; the owner's guess (lessers missing from ConduitCloud) is not the
    cause. Aether's `find_conduit_id_by_name`, `list_conduit_names` and `has_conduit_name` read the same root-only
    map; their docstrings say "root", so the family was never widened when named lessers landed (2026-09-23).
  EVIDENCE:
  - src/melder/aether/aether.py:1842-1863
  - src/melder/aether/aether.py:1914-1948
  - src/melder/aether/aether.py:1677-1709
  - src/melder/aether/aether.py:1772-1840
  - src/melder/aether/aether.py:1888-1912
  - src/melder/aether/aetheric_frame/aetheric_frame.py:339-378
  - src/melder/aether/conduit/conduit.py:2723-2792
  - src/melder/aether/aetheric_frame/conduit_cloud.py:268-291
  - src/melder/aether/aetheric_frame/conduit_cloud.py:481-501
  IMPACT: The fix belongs in Aether's name-lookup family (read the Cloud directory), not in lesser registration. How
    far it goes (get_conduit_by_name only, or the whole name family) is an owner decision.
  NEXT: Reproduce with a probe (named lesser: Aether lookup raises, Cloud lookup returns) and locate the existing
    tests for these methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T09:51:28Z
  TYPE: MEASURE
  CLAIM: Reproduced on 0.2.78 (snapshot copy of src in VM scratch; 3.14.7t and 3.14.7 GIL; both exit 0). In an
    automatic frame and in a dynamic frame, for root -> named lesser -> named nested lesser: the root is found by
    every Aether name read; both lessers make `Aether.get_conduit_by_name` raise "Conduit with name X not found.",
    `find_conduit_id_by_name` return None and `has_conduit_name` return False, while
    `ConduitCloud.get_conduit_by_name` returns the exact object. `Aether.list_conduit_names` lists the root only;
    the Cloud lists all three. After the nested lesser's cleanup the Cloud retires its name (lookup raises, not
    listed), so reading the Cloud would not surface returned or idle shells.
  EVIDENCE:
  - context_compass/artifacts/conduit_name_lookup_20260927/results_20260927.txt:1-45
  - context_compass/artifacts/conduit_name_lookup_20260927/results_20260927.txt:46-90
  - context_compass/artifacts/conduit_name_lookup_20260927/probe_named_lesser_lookup.py:1-70
  IMPACT: Confirms the FACT above at runtime in both modes; a fix that reads the Cloud directory returns the right
    live object and inherits the Cloud's retirement on return.
  NEXT: Survey src callers and tests of Aether's name-lookup family and the docs that describe it, then draft fix
    options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T09:51:28Z
  TYPE: UNKNOWN
  CLAIM: Side observation, outside this task: binding the SAME class into a Spellbook of a SECOND frame raised
    "Spell ID collision detected ... already registered in the Spellbook or Aether for this frame" (first probe
    run); whether spell ids are meant to be Aether-wide across frames is not established here. The probe now
    binds one class per frame.
  EVIDENCE: src/melder/aether/spellbook/spellbook.py:5332-5332
  IMPACT: None on this task; raised to the owner as a possible separate item.
  NEXT: Mention to the owner in the findings report; no investigation in this task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T09:54:12Z
  TYPE: FACT
  CLAIM: Tooling interpreter corrected on owner instruction (2026-09-27): every script and repo tool in this lane
    now runs on CPython 3.14.7 free-threaded from a VM venv (~/.venv314t, pytest 9.1.1), loaded per call from
    ~/.melder_env with PYTHONDONTWRITEBYTECODE=1. Before this, the board and ticket edit scripts and the two index
    --check runs used the VM's system python3 3.10.12, below the repository's floor; the probe already ran on
    3.14.7t and 3.14.7. Re-verified on 3.14.7t: both document indexes and the graph index are current. No 3.10
    bytecode was left in the repository and no .git/index.lock exists; one read-only `git check-ignore` ran without
    GIT_OPTIONAL_LOCKS=0, and later git calls set it.
  EVIDENCE: pyproject.toml:10-10
  IMPACT: Repo tooling evidence in this lane comes from the interpreter the repository targets, avoiding the
    older-interpreter silent-skip hazard in graph extraction.
  NEXT: Resume the survey of root-map writers, tests and user docs for Aether's name-lookup family.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T09:58:06Z
  TYPE: FACT
  CLAIM: Change-surface survey. (1) The frame root maps have one writer, `AethericFrame.register_root_conduit`, which
    publishes the root into the Cloud directory first, and every root must be named; reading the Cloud therefore
    returns the same object for every root name and adds live named lessers. (2) No src code calls Aether's name
    family except Aether itself (search, absence proof); the crystallizer probes the Cloud's own `has_conduit_name`.
    (3) Nexus command getters already resolve named lessers and drop them on cleanup, and the user docs send readers
    to the Cloud for named scopes; Aether's facade is the only surface that lags. (4) Unit tests pin the root-map
    implementation: the fixture's `_FrameConduitCloudStub` has no name directory and three tests seed only root maps,
    so a Cloud-reading fix must seed the stub (test-setup drift, not a behaviour change). Integration tests that look
    up roots through Aether are expected to keep passing by (1); that is Not run.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:339-378
  - tests/unit/melder/aether/test_aether.py:23-93
  - tests/unit/melder/aether/test_aether.py:123-143
  - tests/unit/melder/aether/test_aether.py:692-718
  - tests/unit/melder/aether/test_aether.py:766-794
  - tests/integration/melder/aether/test_named_lesser_nexus_commands.py:35-68
  - docs/intermediate/scopes.md:24-52
  IMPACT: The fix is safe for roots and for internal callers; its test cost is the stub, three unit tests and one new
    regression test.
  NEXT: Record the fix plan and the owner decisions it needs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T09:58:06Z
  TYPE: PLAN
  CLAIM: Fix plan, pending owner approval; no src, test or doc edits have been made.
    1) Patch docs first (public contract and canonical docs change): `system_docs/patches/active/
       aether_named_lookup_2026_09_27/` with architecture_patch.md and component_patch_aether_singleton.md, linked here.
    2) `src/melder/aether/aether.py`: `_get_conduit_by_name` keeps its frame resolution and error logging but resolves
       the name through `frame._conduit_cloud.get_conduit_by_name(name)`, re-raising the same ValueError ("Conduit with
       name X not found."); `find_conduit_id_by_name` and `list_conduit_names` read the same directory
       (`has_conduit_name` follows through `list_conduit_names`). Docstrings state the contract: exact names of named
       roots and active named lessers at any depth, in both modes; a borrowed reference with no lease; retired, pooled
       and anonymous scopes never resolve. The id family is unchanged unless D2 says otherwise.
    3) Tests: seed a name directory in `_FrameConduitCloudStub` and update the three unit tests; add unit tests for the
       delegation (a lesser-only name resolves; a missing name raises); add an integration regression test named for
       the symptom (automatic and dynamic frames: root, named lesser and nested named lesser resolve by identity
       through Aether; has, find and list agree; after cleanup the name is gone; an anonymous lesser never resolves).
       Red on 0.2.78, green after, on 3.14t and GIL.
    4) Promote into src_components (Aether component) and src_architecture (named-lesser invariant); regenerate their
       indexes; re-author the aether.py graph descriptor if its prose says root-only; release-note bullet; notch
       `__version__` above the value current at landing; NOTICEs to the active agents.
  EVIDENCE:
  - src/melder/aether/aether.py:1677-1709
  - src/melder/aether/aether.py:1805-1863
  - src/melder/aether/aether.py:1914-1948
  - src/melder/aether/aetheric_frame/conduit_cloud.py:481-501
  - src/melder/aether/aetheric_frame/conduit_cloud.py:552-576
  - src/melder/aether/aetheric_frame/conduit_cloud.py:709-738
  IMPACT: A contained change: one src file, one unit test file, one new integration test file, plus docs.
  NEXT: Owner answers D1 and D2 (next note) and approves this plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T09:58:06Z
  TYPE: DECISION_REQUEST
  CLAIM: Two owner decisions before implementation.
    D1 scope: (a, recommended) the whole Aether NAME family (`get_conduit_by_name`, `find_conduit_id_by_name`,
    `has_conduit_name`, `list_conduit_names`) reads the frame's Cloud directory, so the four agree with each other,
    with the Cloud and with Nexus; (b) `get_conduit_by_name` only, which leaves has, find and list reporting a name
    absent that get_conduit_by_name returns.
    D2 id family (`get_conduit_by_id`, `list_conduit_ids`, `has_conduit_id`, `count_conduits`): (a, recommended) stays
    root-only, with docstrings saying so and pointing to the name family for scopes; (b) widened as well, which can
    only ever cover NAMED lessers, because anonymous lessers sit in no frame-wide directory.
  EVIDENCE:
  - src/melder/aether/aether.py:1643-1840
  - src/melder/aether/aetheric_frame/conduit_cloud.py:503-576
  - docs/intermediate/scopes.md:42-52
  IMPACT: D1 decides API consistency; D2 decides whether the id family changes meaning.
  NEXT: Ask the owner for D1, D2 and plan approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T10:07:50Z
  TYPE: DECISION
  CLAIM: Owner redirect (chat, 2026-09-27) supersedes D1/D2: Aether's root-only lookups get root-explicit names,
    Aether gains lookups for any conduit (by name, by id), ConduitCloud returns all of its conduits, every usage is
    migrated and the version moves afterwards. Tracked by EPIC-2026-09-27-aether-conduit-lookup-api with one story
    per method; this task's cause and repro are the epic's evidence and no fix lands under this task.
  EVIDENCE: tickets/epics/2026-09-27_aether_conduit_lookup_api_epic.md:154-165
  IMPACT: This task's deliverable (cause, repro, options) is complete; it can be turned in on owner confirmation.
  NEXT: Owner turn-in; the usage survey continues under the epic.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Cause (source and runtime): Aether's name lookups read only the frame's root maps, while named lessers are published
only into the frame's ConduitCloud directory; the Cloud, Nexus and the user docs already treat names frame-wide.
Repro filed under artifacts/conduit_name_lookup_20260927/. Fix plan and decisions D1/D2 are in Notes; nothing is
edited. Next: the owner's D1/D2 answers and plan approval, then patch docs before any src change.

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
