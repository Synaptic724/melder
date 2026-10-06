

# Task: Retire a removed spell id's conduit verdicts and re-gate them on rebind (rebind after first meld)

## Metadata
- Task ID: TASK-2026-10-03-repair-rebind-after-first-meld
- Story: STORY-2026-10-03-rebind-after-first-meld-repair
- Status: done
- Owner: user
- Agent Name: fable_1
- Priority: p1
- Created: 2026-10-03T20:10:00Z
- Updated: 2026-10-03T21:08:00Z

- Completed: 2026-10-03T21:08:00Z
- Summary: Landed 2026-10-03 (fable_1) at Melder 0.2.8219 (notched from 0.2.8218): SpellSystemStates.unregister_index
  and register_index retire a spell id's per-conduit resolution verdicts (new ConduitResolutionState.forget_spell,
  SpellSystemStates.forget_spell_resolution_verdicts); 37 regressions (30 red before) across unit, component and
  integration; four tiers green; release-note section "Fixed: a definition removed after use can be bound again
  at the same address and melded"; src_architecture/src_components + indexes, graph, assets and bundles current.
  Owner ruling: a product built from a removed definition stays alive and keeps its slot. Work package C
  (consumer acceptance on the delivered build) stays with the owner under the epic.

## Objective
Land the DevOps control-plane repair proved in the reproduction task: `SpellSystemStates.unregister_index`
retires the removed spell id's per-conduit resolution verdicts in every `ConduitResolutionState`, and
`register_index` retires any verdict already held for the version id it publishes, so a definition bound
again under the same content-stable id is resolved (phases 5-11) by each conduit before it is built there.
Ship it with the regressions, the notch, the release note, the system docs and the rebuild.

## Ticket Contract
- ENTRY_GATE: patch lane `system_docs/patches/active/rebind_after_first_meld_2026_10_03/` exists with
  `architecture_patch.md`, `component_patch_devops_control_plane.md` and
  `code_description_patch_verdict_retirement.md`, linked here and on `artifact_board.md`; the owner has
  confirmed the exact edit (Propose -> Confirm -> Implement); the reproduction task's cause FACT and
  prototype MEASURE are on record.
- EXECUTION_BOUNDARY: src -
  `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py`
  (`ConduitResolutionState.forget_spell`),
  `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`
  (`SpellSystemStates.forget_spell_resolution_verdicts`, `_forget_resolution_verdicts_locked`,
  `register_index`, `unregister_index`, class docstring), `src/melder/__version__.py`. tests - new files under
  `tests/unit/melder/aether/dev_ops/spell_system_states/`, `tests/component/melder/aether/dev_ops/` and
  `tests/integration/melder/aether/conduit/`. docs - `release_docs/next_version_release.md`,
  `system_docs/src_architecture.md` + index, `system_docs/src_components.md` + index, the graph descriptors
  of the two files, then the asset and bundle rebuild. No other src file; fable_0's S8 set is untouched.
- DEPENDENCIES: TASK-2026-10-03-reproduce-rebind-after-first-meld (cause, prototype, probes);
  `special_instructions/agent_contribution_guide.md` (notch, note, rebuild-last); fable_0's rebuild window
  (the tree is at 0.2.8218 with assets current for it - coordinate before rebuilding).
- EXIT_GATE: regressions red on the unpatched tree and green after; the four tiers green on the patched tree;
  `__version__` notched by 0.0001 from the value read at landing; release-note section added; system docs
  and indexes updated and `--check` clean; assets and bundles rebuilt and both `--check` runs print only
  OK; work package C (consumer acceptance on the delivered build) handed to the owner.
- FAILURE_ESCALATION: DECISION_REQUEST on the M7 singleton-slot semantics (already filed); CONFLICT if
  another agent holds either source file; BLOCKER if the rebuild window cannot be obtained.

## Scope Boundaries
- In scope: the two registry verbs and their call sites, docstrings, regressions, notch, note, docs, rebuild.
- Out of scope: the M7 slotted-existence semantics (owner ruling, follow-up if (b)); MelderOps changes; the
  CreationContext guard; purge semantics; any S8 file.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-03T21:08:00Z) owner directive in chat, 2026-10-03 15:05 local ("turn in your stuff since your done"); all EXIT_GATE
  clauses but the owner-owed work package C are met, and C is tracked by the epic.
- from_state: draft
- to_state: in_progress
- transition_reason: cause recorded as FACT and the repair prototyped green in the VM mirror
  (reproduction task notes 2026-10-03T19:32:35Z and 20:06:00Z); owner directed the fix ("this is
  important to fix").
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-03T21:00:00Z) EXIT_GATE met except the owner's acceptance: source, 37 regressions
  (30 red before), four tiers green, notch 0.2.8219, release note, system docs + indexes, graph, assets and
  bundles rebuilt with both checks OK; work package C (consumer acceptance) is the owner's.

## Steps / Checklist
- [x] Author the patch lane (architecture, component, code description) and link it (ticket + artifact board).
- [x] Propose the exact edit to the owner; wait for confirmation. (confirmed 2026-10-03 14:31 local)
- [x] Apply `fix/apply_forget_verdicts.py` to the tree (CRLF-preserving); read back both files.
- [x] Regressions: unit (forget_spell; registry forget on unregister/register; no risk callback), component
      (RiskManager flag follows the rebind), integration (four-case probe + revalidation matrix M1-M5 as
      regressions, M2/M2b as guards, M7 per the owner's ruling (a)).
- [x] Red on the unpatched tree, green on the patched tree; four tiers green.
- [x] Notch `__version__` (read at landing), release-note section, system docs + indexes, graph descriptors.
- [x] Rebuild assets and bundles last; both `--check` runs OK.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The two-file source change, its regressions, the notch and release-note section, updated system docs.
- `artifacts/rebind_after_first_meld_20261003/fix/` with the apply script, diff, run logs.

## Files / Paths Impacted
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py
- src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py
- src/melder/__version__.py
- tests/unit/melder/aether/dev_ops/spell_system_states/ (new test modules)
- tests/component/melder/aether/dev_ops/spell_system_states/ (new test module)
- tests/integration/melder/aether/conduit/ (new test module)
- release_docs/next_version_release.md
- context_compass/system_docs/src_architecture.md, src_architecture_index.md
- context_compass/system_docs/src_components.md, src_components_index.md
- context_compass/system_docs/graph/ (descriptors of the two files), src_graph.md + index (reassembled)

## Validation
- RUN 2026-10-03T21:00:00Z on the landed content (VM mirror synced from the tree, 3.14.7t, -n 2): unit 8853 passed /
  3 skipped / 7 xfailed; component 2286 / 23 / 1 xfailed; integration 2021 / 2 / 4 xfailed / 2 xpassed;
  tests/tests + experimentation + experiments 250 / 4. Regressions 37 green (30 red on the unpatched files).
  Asset and bundle checks OK (artifacts/rebind_after_first_meld_20261003/fix/landing_results.txt).
- Recommended commands (VM, 3.14.7t):
  - `. ~/.fable_1_env && cd $MELDER_MIRROR && $PY -m pytest tests/unit -q -p no:cacheprovider -n 2`
  - the same for tests/component, tests/integration, and `tests/tests tests/experimentation tests/experiments`

## Risks / Rollback Notes
- Forgetting on `register_index` also fires on notch and transfer re-registrations: those spells are
  resolved again per conduit at their next meld (one target pass), which is the documented lazy intent of
  notch; no warm-path cost.
- Rollback: revert the two files together; no record, cache or API shape changes.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src edit before the patch lane exists and the owner confirmed the exact edit.
- [ ] No "tests ran" claim without the run; "Not run." otherwise.

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
  - artifacts/rebind_after_first_meld_20261003/
  - system_docs/patches/active/rebind_after_first_meld_2026_10_03/architecture_patch.md
  - system_docs/patches/active/rebind_after_first_meld_2026_10_03/component_patch_devops_control_plane.md
  - system_docs/patches/active/rebind_after_first_meld_2026_10_03/code_description_patch_verdict_retirement.md
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: patch docs promoted into src_architecture/src_components at landing and archived under
  system_docs/patches/completed/ at turn-in; artifacts kept with the epic's evidence.

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
- DATETIME: 2026-10-03T20:10:00Z
  TYPE: PLAN
  CLAIM: Patch-section -> implementation -> validation mapping. (1) architecture_patch "Cross-Component
  Invariants" -> `ConduitResolutionState.forget_spell` + `SpellSystemStates._forget_resolution_verdicts_locked`
  -> unit tests on both classes (verdict gone, dirty + reason, miss is a no-op, no risk callback, cleaned
  state raises). (2) component_patch "unregister_index" -> the call in both branches of `unregister_index`
  -> unit test: a verdict set for the id in two conduit states is gone after unregister, other ids kept;
  integration M1/M3/M4. (3) component_patch "register_index" -> the call before the structural gate ->
  unit test: a verdict present for the id is gone after register_index, first-time id untouched;
  integration: the four-case probe. (4) code_description "risk model" -> no callback -> component test on
  `_spellbook_validation_required` (M5). Owner ruling pending on M7.
  EVIDENCE:
  - tickets/tasks/2026-10-03_reproduce_rebind_after_first_meld_task.md:146-262
  - artifacts/rebind_after_first_meld_20261003/fix/apply_forget_verdicts.py:1-347
  IMPACT: satisfies patch_framework_gating's mapping requirement before any src edit.
  NEXT: author the three patch docs, link them, then propose the edit to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-03T20:32:00Z
  TYPE: DECISION
  CLAIM: Owner confirmed the proposal in chat (2026-10-03 14:31 local): "I agree with everything your doing yes".
  Implementation of the exact edit (fix/apply_forget_verdicts.py) is authorised; M7 is still an open ruling
  (owner asked what "reallocate under the same kind" means; answered: for slotted existences the replacement's
  first meld returns the surviving old object in the id-keyed slot; (a) document it, (b) evict the slot on
  removal with a disposal home for the evicted object - a follow-up either way; the landing does not depend
  on it). Landing order: regressions red on the unpatched state -> green on the patched mirror -> tree edit ->
  tiers -> notch -> note -> docs -> rebuild.
  EVIDENCE:
  - tickets/tasks/2026-10-03_repair_rebind_after_first_meld_task.md:17-24
  - artifacts/rebind_after_first_meld_20261003/fix/prototype_results.txt:1-22
  IMPACT: the Propose -> Confirm gate is passed for the declared files/symbols; no other file is authorised.
  NEXT: write the unit/component/integration regressions and run them red against the unpatched files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T20:44:00Z
  TYPE: DECISION
  CLAIM: Owner ruled M7 = (a) in chat (14:42 local: "it should be deliberately left alive thats perfect"): for a
  slotted existence the object built from the removed definition keeps its id-keyed slot, the replacement's
  first meld in that scope returns it, and an override against it is refused ("already exists", the stored
  shared-instance rule). Pinned by
  `test_slotted_replacement_meets_the_surviving_singleton_in_its_slot`; stated in the patch docs and the
  release note. No follow-up task.
  EVIDENCE:
  - tests/integration/melder/aether/conduit/test_rebind_after_first_meld_integration.py:289-311
  - release_docs/next_version_release.md:308-343
  IMPACT: the repair ships complete; nothing remains open on semantics.
  NEXT: system docs (architecture, components, indexes, graph), then the rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-03T20:44:00Z
  TYPE: MEASURE
  CLAIM: LANDED IN THE TREE. `fix/apply_forget_verdicts.py` applied (two files, byte-identical to the validated
  mirror copies); four test modules added (37 tests: 30 red on the unpatched files - the two first-meld probe
  cases, M1, M3, M4, the two flag tests, M7 and the 22 unit tests of the new verbs - and 7 guards green before
  and after). Tiers on the landed content (mirror synced from the tree, 3.14.7t, -n 2): unit 8853 passed /
  3 skipped / 7 xfailed; component 2286 / 23 / 1; integration 2021 / 2 / 4 xfailed / 2 xpassed; tests/tests +
  experimentation + experiments 250 / 4; 0 failures. `__version__` notched 0.2.8218 -> 0.2.8219 (read at
  landing); release note header and a "Fixed: a definition removed after use can be bound again at the same
  address and melded" section added, its example executed (first.value 1, second.value 2, distinct objects);
  Packaging bullet added and the rebuild line moved to 0.2.8219 (rebuild not yet run).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:548-618
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:307-375
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:765-872
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:929-1017
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-1
  - artifacts/rebind_after_first_meld_20261003/fix/regressions_unpatched.txt:1-40
  IMPACT: source, tests, notch and note are in; docs and rebuild remain before hand-off.
  NEXT: update src_architecture.md and src_components.md (+ indexes), graph descriptors, then rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T21:00:00Z
  TYPE: MEASURE
  CLAIM: DOCS AND REBUILD DONE. src_architecture.md: meld-time validation gate step 6, a first Operational
  Invariant ("Per-conduit verdicts retire with their definition"), a first Failure Mode (the fixed RuntimeError),
  the code-map extent of spell_system_states.py (1651) and a handoff paragraph; src_components.md: the
  SpellSystemStates Registry entry (verbs corrected from the never-existing `register_lineage` /
  `unregister_lineage` / `consume_dirty_lineages` to `register_index` / `unregister_index` /
  `consume_dirty_indexes`; retirement in both verbs; the public verb; lock order), the Conduit Resolution State
  entry (`forget_spell`), the bind flow, the meld-time gate flow, both code-map extents and a handoff paragraph;
  both indexes regenerated, `--check` OK. Graph: extractor --strict (584 descriptors, skipped=0), the two class
  nodes re-authored (retirement responsibility; `owns_state` corrected from `_dirty_lineages` to the real slots)
  and --accept'ed, graph reassembled (27592 lines, 584 ranges verified). Rebuild last: assets WROTE x3 and
  --check OK x3 at v0.2.8219; LLM bundles WROTE and --check OK x3 with --include-untracked (the plain check
  flags `tests` until the four new test files are tracked). The asset builder unlinks payload files, which the
  connected folder refused; the owner granted delete permission for the rebuild.
  EVIDENCE:
  - artifacts/rebind_after_first_meld_20261003/fix/landing_results.txt:1-25
  - system_docs/src_architecture.md:917-936
  - system_docs/src_components.md:6335-6396
  - release_docs/next_version_release.md:308-343
  IMPACT: the change set is complete and self-consistent; the ticket is in review for the owner's acceptance.
  NEXT: owner accepts (turn-in: patch docs promoted and archived, boards synced) and runs work package C -
  install the 0.2.8219 build in priv_commandops and rerun the unchanged five-case selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T21:05:00Z
  TYPE: FACT
  CLAIM: Notch NOTICE delivered to command_0 over the codex_bridge (special_instructions/codex_mcp.md): Codex chat
  "agent: command_0", threadId 01a0711f-ca9e-7b43-88de-a5cdab379ba2 (hostId local), bridgeMessageId
  a880d430-b48a-4ead-a344-f6d892cb3fb9 - 0.2.8219 taken, the repair landed, work package C stays with the owner,
  the ruled slotted-existence behaviour. No ACK requested; delivery confirmed, not read. fable_0, muse_0 and
  melder_2 are not reachable over the bridge (Claude / opencode runtimes); the owner relays the notch to them.
  EVIDENCE:
  - special_instructions/codex_mcp.md:41-57
  - special_instructions/agent_contribution_guide.md:31-32
  IMPACT: the one live agent whose epic this repairs, and whose consumer tests form work package C, knows the
  build to test against.
  NEXT: owner's acceptance (turn-in) and work package C.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
STATE 2026-10-03T21:00:00Z: REVIEW. Landed at 0.2.8219 with 37 regressions, four tiers green, release note, system docs,
graph, assets and bundles current. M7 ruled (a): the surviving product is deliberately left alive and keeps
its slot. Waiting on the owner's acceptance (turn-in) and work package C (consumer acceptance in
priv_commandops on the delivered build).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
