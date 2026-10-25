

# Task: Creations' `many` disposal docstrings state the contract the code has since 0.2.8257

- Completed: 2026-10-25T02:35:56Z
- Summary: The four creations.py docstrings that said a spell id hashes its disposal names - `ManyDisposalBucket`,
  `add_many_creations`, `register_many`, `_append_many_locked` - state the store as it is since 0.2.8257, as
  measured (no behaviour change; tests 423 passed, 1 skipped, the GIL off and on); src_components (the Creations
  entry, Unknowns, citations, code map, handoff), src_architecture (code map, handoff) and the graph (creations.py
  re-extracted, two nodes accepted) follow. Notched 0.2.8268; release-note section "Packaging and documentation".
  The two measured rebind outcomes are the owner's to rule on (S3, parked). Rebuild last, after this closure.

## Metadata
- Task ID: TASK-2026-10-25-creations_many_disposal_docstrings
- Story: none (standalone; the owner's go in chat, 2026-10-24 19:45 MDT)
- Status: done
- Owner: Mark (owner)
- Agent Name: melder_3
- Agent Role: synaptic_python_developer
- Priority: p3
- Created: 2026-10-25T01:50:10Z
- Updated: 2026-10-25T02:35:56Z

## Objective
Three docstrings in `src/melder/aether/conduit/creations/creations.py` - `ManyDisposalBucket`,
`Creations.add_many_creations` and `Creations.register_many` - say a spell id hashes its resolved disposal names, so
one `many` key cannot carry two disposal declarations. That has been untrue since 0.2.8257: the spell_id is the
object's code and the disposal names are a binding-manifest field. The docstrings are to state the contract the code
has today, measured where reading alone cannot settle it. No behaviour changes.

## Ticket Contract
- ENTRY_GATE: the owner's go (chat, 2026-10-24 19:45 MDT: "just keep moving fix the stale docstrings"); a board row
  routes here; no open lane holds creations.py.
- EXECUTION_BOUNDARY: docstrings and comments in creations.py; the documents' consequences - src_components'
  Creations entry, Unknowns entry, citations, code-map entry and handoff entry, src_architecture's code-map entry
  and handoff entry, both indexes, the graph's re-extraction (the DECISION of 2026-10-25T02:10:15Z); `__version__`
  (one notch) and the running release note; the rebuild last. No statement of code changes and no other source file;
  the probes run in scratch outside the repository.
- DEPENDENCIES: none blocking. melder_1's HYPOTHESIS of 2026-10-24T19:10:35Z in EPIC-2026-10-17-correctness_defects
  asks the same question of the code; its story, if any, stays melder_1's.
- EXIT_GATE: the three docstrings state the measured contract; creations.py compiles; the Creations tests pass with
  the GIL off and on; the src_components entry and index current (`--check` OK); notch, release-note line, closure;
  the rebuild last with both `--check`s OK.
- FAILURE_ESCALATION: DECISION_REQUEST when the contract the code has is a defect the owner must rule on (fix it, or
  document it); CONFLICT when another lane holds creations.py; BLOCKER when the tests cannot run.

## Scope Boundaries
- In scope: the three docstrings and any other comment in creations.py resting on the same premise; the
  src_components Unknowns entry, a handoff entry and its index; the notch, the release-note line and the rebuild.
- Out of scope: changing the store's behaviour (a fix, if the owner wants one, is its own ticket); the
  correctness-defects story melder_1 would file; the authoring instructions' heading pattern (not approved).

## State Transition Event
- from_state: in_progress (implementation)
- to_state: done
- transition_reason: the EXIT_GATE is met but for the rebuild, which the turn-in order runs after this closure: the
  docstrings state the measured contract, creations.py compiles, the Creations tests pass with the GIL off and on
  (the MEASURE of 2026-10-25T02:05:35Z), both indexes and the graph are current (the MEASURE of
  2026-10-25T02:31:46Z), and the notch, the release-note entry and the NOTICEs are done. Routine closure under the
  owner's go; the two rebind outcomes are reported for his ruling, not decided here.
- from_state (earlier): draft
- to_state (earlier): in_progress
- transition_reason (earlier): the owner's go in chat (2026-10-24 19:45 MDT) after the epic's closure report named
  these docstrings.

## Steps / Checklist
- [x] Read the `many` registration, disposal, purge and extract paths in creations.py and the emitter's call.
- [x] Probe the rebind case, the GIL off and on, so the docstrings state measured behaviour.
- [x] Rewrite the three docstrings (and `_append_many_locked`'s); compile; run the Creations tests with the
      GIL off and on.
- [x] src_components: the Unknowns entry, a handoff entry, the index `--check`; src_architecture's code
      map and handoff; the graph re-extracted, two nodes accepted, reassembled.
- [x] Notch, release-note line, NOTICE; closure and board sync.
- [x] The rebuild last with both `--check`s (after this closure; the MEASURE of 2026-10-25T02:39:05Z).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The four docstrings, corrected; the probes and their runs; the src_components, src_architecture and graph
  updates; the notch and the release-note entry.

## Files / Paths Impacted
- src/melder/aether/conduit/creations/creations.py (docstrings only)
- context_compass/system_docs/src_components.md and src_components_index.md
- context_compass/system_docs/src_architecture.md and src_architecture_index.md
- context_compass/system_docs/src_graph.md, src_graph_index.md and
  graph/melder/aether/conduit/creations/creations.json
- src/melder/__version__.py; release_docs/next_version_release.md
- the generated assets and bundles (the rebuild)

## Validation
- Ran: 423 passed, 1 skipped, with -X gil=0 and with -X gil=1 (the MEASURE of 2026-10-25T02:05:35Z).
- Ran: both index `--check`s, assemble_graph `--check`, the citation recipe and the portability greps (the
  MEASURE of 2026-10-25T02:31:46Z).
- Rebuild: ran after the closure; both `--check`s OK (the MEASURE of 2026-10-25T02:39:05Z).
- Recommended commands:
  - python -m py_compile src/melder/aether/conduit/creations/creations.py
  - pytest on the Creations tests with -X gil=0 and -X gil=1
  - index_document.py --check on src_components; the asset runner and the llm_support builder, each with `--check`

## Risks / Rollback Notes
- A docstring that promises what the code does not do is the defect being fixed; each new sentence is checked
  against the code or the probe. Rollback: the docstrings alone change, so a revert is the file's prior text.
- Concurrent writers to the boards and the release note: re-read before every write; NOTICE after the notch.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off (the rebuild ran after the closure, by the turn-in order)
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/creations_many_disposal_20261025/ (the probe and its runs)
- DISPOSITION: retain_as_reference - the probes reproduce the two rebind outcomes the owner has to rule on;
  rerun them at the fix (the DECISION of 2026-10-25T02:35:56Z)
- CLEANUP_TRIGGER: the owner's word, or the closure of the fix

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_3 (synaptic_python_developer); prose and implementation (docstrings); revision 1.
- Published By: UNKNOWN before publication (local files; the owner commits).
- Independent Review: none requested.

## Notes
- DATETIME: 2026-10-25T01:50:10Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Read the code first - `ManyDisposalBucket`, `Creations.add_many_creations`, `register_many`,
    `_append_many_locked` and the disposal, purge and extract paths, and the site-plan emitter that calls
    `register_many` - then probe the rebind case the src_components Unknowns entry describes (cleanup_spell, bind
    the class again with other disposal names, meld into a store still holding the old objects, tear down), the GIL
    off and on, so the three docstrings state what the code does rather than what it used to guarantee.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:23-30
  - src/melder/aether/conduit/creations/creations.py:727-760
  - src/melder/aether/conduit/creations/creations.py:791-820
  - context_compass/system_docs/src_components.md:160-170
  IMPACT: the docstrings are the contract the emitters rely on; rewritten from memory they would trade one wrong
    guarantee for another.
  NEXT: read creations.py in full, then the emitter's `register_many` call.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T01:58:21Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Read in full: creations.py writes a `many` key's disposal record once, at the key's first registration in a
    store, holding that registering Spell's list - `register_many` and `_append_many_locked` create the
    `ManyDisposalBucket` only when the key has none - and every later registration appends without comparing lists.
    `add_many_creations` refuses only a non-list slot and a mix of disposal-bearing and disposal-free registrations
    of one key, never a different list, so src_components' Unknown is wrong that it "would refuse the mismatch".
    `register_many` appends to whatever live slot the key holds, unchecked. `cleanup_spell` disposes no creation,
    and an emitted plan binds its own Spell's list as `dmN`. A fourth docstring rests on the dead premise:
    `_append_many_locked`'s Raises ("one many key carries one declaration (the spell id fixes it)").
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:791-862
  - src/melder/aether/conduit/creations/creations.py:864-921
  - src/melder/aether/spellbook/spellbook.py:4984-5153
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1579-1624
  - context_compass/system_docs/src_components.md:160-170
  IMPACT: four docstrings to correct, and the Unknown's `add_many_creations` clause with them.
  NEXT: probe the rebind cases (another disposal list; a slotted definition rebound as `many`), the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


- DATETIME: 2026-10-25T01:58:21Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Probed on 0.2.8267 (CPython 3.14.8 free-threaded, the GIL off and on; the same results). R1: a `many` spell
    bound with ["close"], melded, `cleanup_spell`, bound again with ["shutdown"] (the same spell_id) and melded: the
    second object joins the first one's bucket, the record keeps ["close"], and the root's teardown runs `close` on
    both objects and `shutdown` on neither. R3: the same in a lesser conduit's store at its pool return. R2 (the
    same list) and R4 (a first definition without disposal names) dispose each object with its own list; R5 (a
    second definition without names) records the second object nowhere, as any disposal-free `many`. R6: a
    `unique_per_conduit` or `unique` definition whose object is in the root's store, cleaned up and bound again as
    `many`: the next meld builds its object, then raises AttributeError "'Svc' object has no attribute 'append'"
    from `register_many` (creations.py:853), and that object is neither returned nor recorded. melder_1's HYPOTHESIS
    of 2026-10-24T19:10:35Z (EPIC-2026-10-17-correctness_defects) reproduces.
  EVIDENCE:
  - context_compass/artifacts/creations_many_disposal_20261025/probes/probe_rebind_many_disposal.py:1-95
  - context_compass/artifacts/creations_many_disposal_20261025/runs/probe_rebind_many_disposal_gil0.txt:1-21
  - context_compass/artifacts/creations_many_disposal_20261025/runs/probe_rebind_many_disposal_gil1.txt:1-25
  - context_compass/artifacts/creations_many_disposal_20261025/probes/probe_rebind_existence_to_many.py:1-74
  - context_compass/artifacts/creations_many_disposal_20261025/runs/probe_rebind_existence_to_many_gil0.txt:1-9
  - context_compass/artifacts/creations_many_disposal_20261025/runs/probe_rebind_existence_to_many_gil1.txt:1-13
  IMPACT: the docstrings can state today's contract as measured. Both behaviours are the gap
    STORY-2026-10-18-revalidate_on_binding_change (parked by the owner) closes - "a changed one retires the old
    entry" - so they stay out of this task and go to the owner and melder_1.
  NEXT: record the wording decision, then edit the four docstrings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-10-25T01:58:21Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Docstrings only, and they describe the measured behaviour without calling it intended: `ManyDisposalBucket`
    - the record keeps the list of the key's first registration in this store and every entry is disposed with it;
    since 0.2.8257 the spell id covers neither the disposal names nor the existence, so a rebound definition whose
    objects land beside the removed one's joins the record. `add_many_creations` and `_append_many_locked` - what
    they refuse (a non-list slot; disposal-bearing against disposal-free) and that they never compare lists.
    `register_many` - the emitters' guarantee is per Spell (one plan, one list), and a store still holding a removed
    definition's objects under the key breaks it: another list is appended under the first, a slotted object under
    the key fails the append. The patch-framework gate does not apply: no boundary, lifecycle, contract or behaviour
    changes. src_components: the Creations entry's many-registration paragraph states the same, and the Unknowns
    entry, now measured, leaves the Unknowns list for it.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:12-55
  - context_compass/system_docs/src_components.md:3641-3661
  - context_compass/agent_onboarding/default/engineer/skills/patch_framework_gating.md:11-18
  IMPACT: the docstrings stop promising one list per key, and say what the store does when that fails, so a reader
    of the emitters is not misled; the behaviour itself is the owner's to schedule.
  NEXT: edit the four docstrings in creations.py and compile it.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8


- DATETIME: 2026-10-25T02:05:35Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Implemented, docstrings only (creations.py 1,680 -> 1,711 lines; no statement changed; the module
    compiles): `ManyDisposalBucket` says the record holds the list of the Spell whose object first registered the
    key in the store, that later registrations leave it as it is, and that a definition rebound under other disposal
    names joins the removed one's record; `add_many_creations` names what it refuses (a non-list slot;
    disposal-bearing against disposal-free) and that it never compares lists, its Raises to match; `register_many`
    states its precondition (the emitters keep it within one definition), what a rebind does to it - another list
    appended under the first, a slotted object failing the append - and lists the AttributeError;
    `_append_many_locked`'s Raises loses the spell-id premise. No "hashes" claim is left in the file.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:12-45
  - src/melder/aether/conduit/creations/creations.py:736-805
  - src/melder/aether/conduit/creations/creations.py:807-892
  - src/melder/aether/conduit/creations/creations.py:894-952
  IMPACT: the store's contract now reads as the code behaves; the release note and src_components follow.
  NEXT: run the Creations tests with the GIL off and on.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7


- DATETIME: 2026-10-25T02:05:35Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Tests on CPython 3.14.8 free-threaded, PYTHONPATH=src, from the repository root: the Creations unit tests
    (tests/unit/melder/aether/conduit/creations, test_cluster_creations.py), the component and integration Creations
    tests, the rebind-after-first-meld integration tests and the build-asset unit tests - 423 passed and 1 skipped
    with -X gil=0 and the same with -X gil=1. The skip is test_running_the_runner_never_imports_melder, which skips
    when another test of the session has imported melder.
  EVIDENCE:
  - tests/unit/melder/build_assets/test_build_asset_runner.py:443-463
  - tests/integration/melder/aether/conduit/test_rebind_after_first_meld_integration.py:297-311
  IMPACT: the docstring change leaves every behaviour these tests pin unchanged, as it must.
  NEXT: src_components: the Creations entry's many-registration paragraph, the Unknowns entry, a handoff entry, the
    index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7


- DATETIME: 2026-10-25T02:10:15Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The documents follow the source in the same change: src_components' Creations entry states the measured
    rebind behaviour (its many-registration paragraph and two Failure Modes) and its Unknowns entry, now answered,
    leaves the list; its numeric citations into creations.py move 9 lines (the ManyDisposalBucket edit; 264-337 ->
    273-346 and so on) and both code maps remeasure creations.py (1,680 -> 1,711 lines); each document gets a dated
    handoff entry; the graph re-extracts (creations.py's descriptor and the eight generated-asset descriptors the
    last rebuild moved), its two class nodes are accepted after the re-read - their authored prose holds - and the
    graph reassembles. No architecture prose changes.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:3641-3661
  - context_compass/system_docs/src_components.md:3829-3840
  - context_compass/system_docs/src_graph.md:5183-5261
  - context_compass/agent_onboarding/default/engineer/skills/staleness_protocol.md:22-35
  IMPACT: a measured fact replaces an UNKNOWN where the reading hierarchy sends a reader, and no measured range or
    source hash is left describing the old file.
  NEXT: edit src_components and src_architecture, regenerate both indexes, then the graph.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T02:22:29Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Two refinements of the 02:10:15Z decision, taken before the document edits: the answered Unknowns entry is
    replaced, not just removed - the one rebind nobody measured, a `many` definition cleaned up and bound again
    under a slotted existence while a store holds its bucket, stays UNKNOWN with its investigation target (slotted
    stores are keyed by spell_id, and that key holds the removed definition's `many` bucket), because dropping the
    entry would read as if every rebind direction were settled; and neither document's handoff entry names a
    version, because the notch is read at landing and melder_0 is landing D-10 (a source change) in the same window
    - the release note and the closure name the notch.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:807-892
  - context_compass/system_docs/src_architecture.md:1846-1858
  - context_compass/attention_board.md:114-114
  - context_compass/special_instructions/agent_contribution_guide.md:28-31
  IMPACT: the Unknowns list keeps exactly the rebind question nobody has measured, and no system document names a
    version this landing might not get.
  NEXT: apply the src_components edit (Metadata, Unknowns, the Creations entry, the code map, the handoff) and
    regenerate its index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T02:31:46Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The documents follow the source. src_components (11,874 -> 11,909 lines): the Creations entry's many
    registration trim says what `add_many_creations` checks (a non-list slot; disposal-bearing against
    disposal-free) and that neither verb compares method lists, with what a rebind meets; its Failure Modes gain the
    two measured rebind outcomes; the answered Unknowns entry gives way to the direction nobody measured (a `many`
    bound again under a slotted existence); the four creations.py citations moved 9 lines (273-346, 348-396,
    399-427, 429-523); the code map remeasures creations.py (1,711 lines); a dated handoff entry; Metadata
    2026-10-25. src_architecture (4,784 -> 4,793): the creations.py code-map entry and a handoff entry. The graph: a
    full extraction into a scratch copy, of which only creations.py's descriptor was taken - melder_0's seven
    in-flight codegen files and the eight generated-asset descriptors stay as they were; the two class nodes' prose
    is sharpened where it read as one declaration per key (ManyDisposalBucket: later registrations append under the
    first list, every entry disposal-bearing or none; Creations: `add_many_creations` refuses disposal-bearing
    against disposal-free, neither verb compares lists), re-read against the source, accepted, and the graph
    reassembled.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:159-172
  - context_compass/system_docs/src_components.md:3643-3667
  - context_compass/system_docs/src_components.md:3824-3862
  - context_compass/system_docs/src_components.md:8956-8960
  - context_compass/system_docs/src_components.md:11618-11629
  - context_compass/system_docs/src_architecture.md:3821-3826
  - context_compass/system_docs/src_architecture.md:4473-4480
  - context_compass/system_docs/graph/melder/aether/conduit/creations/creations.json:1-259
  - context_compass/system_docs/src_graph.md:5183-5261
  IMPACT: a reader descending architecture -> components -> graph meets the contract the docstrings now state, and
    no measured range or source hash in the three documents describes the old file.
  NEXT: take the notch (read `__version__` first), add the release-note entry and send the NOTICEs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:31:46Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Gates on this pass: both indexes regenerated, `--check` OK (src_components 155 sections over 11,909 lines,
    src_architecture 61 over 4,793); assemble_graph `--check` OK (593 sections, 28,193 lines); the citation recipe
    over the three documents: 1,416 citations, none missing or out of bounds; the portability and absolute-path
    greps return nothing on either document and no heading is wrapped. Content preservation (baselines captured at
    02:18:54Z, before the first edit): src_components lost 22 lines, each accounted - 11 of the answered Unknowns
    entry (its Related and status lines survive in the new entry), 3 of the many registration trim (rewritten), one
    evidence line (now naming `add_many_creations`), the 4 citations (+9), the code map's two counts and stamp, and
    the date; src_architecture lost 4 - the code map's counts and stamp, and the date. Rubric: not re-scored whole;
    this pass changed one C3 entry, one C1 entry and a handoff entry in src_components and the C1 entry and a
    handoff entry in src_architecture, so the totals recorded at their stories' closures stand (src_components 84.5,
    src_architecture 81, both B), with the touched citations remeasured on this pass. The graph census after:
    creations.py's two class nodes accepted; 15 descriptors still lag their source - the eight generated assets,
    which lag every rebuild, and melder_0's seven in-flight codegen files.
  EVIDENCE:
  - context_compass/system_docs/src_components_index.md:9-19
  - context_compass/system_docs/src_architecture_index.md:9-19
  - context_compass/system_docs/src_graph_index.md:9-18
  - context_compass/system_docs/src_components.md:48-84
  IMPACT: the documents can be sliced and trusted as of this pass; nothing the gates check is left red.
  NEXT: notch `__version__` to the next number, then the release-note entry.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T02:35:56Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Notched 0.2.8268 (`__version__` read at 0.2.8267 at 02:32:23Z; the running note's header with it) and added
    one bullet to the running note's "Packaging and documentation" section, before its rebuild line, which names
    0.2.8268: the internal store's docstrings no longer say a spell_id covers a `many` spell's disposal names, what
    the store does after a rebind (the two outcomes, known and not fixed), and that the packaged documents and graph
    say the same. NOTICEs: M3-9 to melder_1 (the hypothesis reproduces; the probes; a story is theirs; the notch),
    M3-10 to melder_0 and M3-11 to melder_2 (the notch), each with its alert line; melder_2 consumed M3-11 and the
    older M3-8. Consumed M2-43 (melder_2's lane open: python-publish.yml, .github/scripts,
    tests/unit/github_workflows, .github/ci_cd, BRANCH_WORKFLOW.md, README.md's install lines,
    docs/beginner/install.md, one Packaging bullet before the running note's rebuild line, the tests documents; no
    src, no notch, a rebuild at their turn-in): I hold none of those files, said so in M3-12, and said my rebuild
    runs next.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  - release_docs/next_version_release.md:127-136
  - context_compass/mailbox_board.md:98-155
  IMPACT: the version and the running note carry this landing, and the other lanes know the number is taken and
    which files are whose.
  NEXT: close: completed/, board sync, the artifact row; then the rebuild.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T02:35:56Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Closed under the owner's go of 2026-10-24 19:45 MDT: every EXIT_GATE item holds but the rebuild, which the
    turn-in order runs after the closure; no reserved decision is taken here - whether to fix the two rebind
    outcomes, through S3 of EPIC-2026-10-18-spell_identity_is_the_code (parked) or a narrower change, is the
    owner's. The artifact folder is retained as reference rather than deleted on close: its probes are the
    reproducers of those two outcomes and are rerun at the fix (precedent:
    TASK-2026-10-24-cache_file_write_failure_fails_meld); the owner can order it deleted.
  EVIDENCE:
  - context_compass/special_instructions/agent_contribution_guide.md:88-97
  - context_compass/artifact_board.md:92-92
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:1-8
  IMPACT: the lane leaves nothing open but the rebuild, and the reproducers survive for whoever fixes the behaviour.
  NEXT: move the ticket to completed/, sync both boards, then rebuild and check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T02:39:05Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The rebuild, last, after the closure, from the repository root on CPython 3.14.8 (TMPDIR=/tmp,
    PYTHONDONTWRITEBYTECODE=1, GIT_OPTIONAL_LOCKS=0): the asset runner wrote the three asset families at v0.2.8268
    (agent documentation 469 entries, bind guard 629, system documents 4) and its `--check` printed OK for all three
    (key match); llm_support/_builder.py --include-untracked wrote src (585 files), tests (1,147) and other (417)
    and the manifest, and its `--check --include-untracked` printed OK for all three. No .git lock was left.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:136-136
  IMPACT: the generated assets and bundles carry 0.2.8268 and this landing's documents; the turn-in is complete.
  NEXT: report to the owner: the landing, and the two rebind outcomes for his ruling.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Scope: the creations.py docstrings that said a spell id hashes its disposal names, corrected to the contract the
code has (no behaviour change), and the documents that follow them. State: done (2026-10-25T02:35:56Z), melder_3;
notched 0.2.8268, release-note section "Packaging and documentation". Evidence: tests 423 passed, 1 skipped, the GIL
off and on (the MEASURE of 2026-10-25T02:05:35Z); documents and graph gates green (the MEASURE of
2026-10-25T02:31:46Z). Open for the owner: the two measured rebind outcomes (the MEASURE of 2026-10-25T01:58:21Z) -
fix them through S3 of EPIC-2026-10-18-spell_identity_is_the_code (parked) or a narrower change; the probes are
retained for the rerun. Next: none in this lane - the rebuild ran with both `--check`s OK (the MEASURE of
2026-10-25T02:39:05Z).

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
