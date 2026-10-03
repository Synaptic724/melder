

# Task: Reproduce rebind-after-first-meld on current source and locate the transition that drops creation codegen

## Metadata
- Task ID: TASK-2026-10-03-reproduce-rebind-after-first-meld
- Story: STORY-2026-10-03-rebind-after-first-meld-repair
- Status: done
- Owner: user
- Agent Name: fable_1
- Priority: p1
- Created: 2026-10-03T19:13:22Z
- Updated: 2026-10-03T21:08:00Z

- Completed: 2026-10-03T21:08:00Z
- Summary: Delivered 2026-10-03 (fable_1): the four-case probe ported to Melder's own reset fixture reproduced the defect
  on current source (2 failed / 2 passed, identical to the 0.2.8215 receipt); the cause was traced and recorded as
  FACT (per-conduit verdicts keyed by the content-stable spell id survive unregister_index; the same-id rebind is
  born structurally valid, so the meld-time structural gate never re-gates them); the repair was prototyped and
  measured in the VM mirror (probe 4/4, revalidation matrix 7/7, four tiers green) and handed to the repair task,
  which landed it at 0.2.8219. No src change in this task. Evidence retained under
  artifacts/rebind_after_first_meld_20261003/.

## Objective
Run the epic's four-case probe against current Melder source with a Melder-only fixture, classify the
present behaviour (still failing / already fixed), and if it fails, trace from
`CreationContextBuilder.build` back to the transition that leaves the replacement spell without
`spell_codegen_creation`, recorded as FACT with source evidence.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; epic evidence read.
- EXECUTION_BOUNDARY: reads anywhere under src/ and tests/; writes only to this ticket, the story,
  the boards and `artifacts/rebind_after_first_meld_20261003/` (probe copies, run logs, JUnit). No
  src/ edit in this task.
- DEPENDENCIES: the epic's artifacts; the VM env (/tmp/fable_1, CPython 3.14.7t) and its mirror.
- EXIT_GATE: a MEASURE note with the probe's 4-case result on the working tree and on HEAD, and either
  a FACT naming the responsible transition with `path:start-end` or an UNKNOWN with the next evidence
  target; artifacts saved; handoff to the repair task.
- FAILURE_ESCALATION: CONFLICT if the trace lands in fable_0's open S8 files; RISK if the working-tree
  and HEAD results differ.

## Scope Boundaries
- In scope: reproduction, tracing, evidence.
- Out of scope: any fix, any test added to tests/, any doc edit.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-03T21:08:00Z) owner directive in chat, 2026-10-03 15:05 local; EXIT_GATE met (MEASURE, cause FACT, artifacts, handoff to the
  repair task, which is closed in the same pass).
- from_state: draft
- to_state: in_progress
- transition_reason: owner directed the investigation (2026-10-03); story routed; VM env ready.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-03T20:14:00Z) EXIT_GATE met - MEASURE (2/4 on current source), cause FACT with source
  evidence, repair prototyped and measured, artifacts saved, handed off to
  tickets/tasks/2026-10-03_repair_rebind_after_first_meld_task.md; closure waits on the owner.

## Steps / Checklist
- [x] Port the probe to a Melder-only fixture in the VM scratch (not in tests/).
- [x] Run the four cases on the working-tree mirror and on a HEAD export; save JUnit + logs. (src/ of the working tree is content-identical to HEAD, so one run covers both.)
- [x] Trace the failing path and name the transition (FACT) or the next evidence target (UNKNOWN).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/rebind_after_first_meld_20261003/ with the ported probe, runs and a findings note.
- Notes here with the classification and the cause or the next target.

## Files / Paths Impacted
- context_compass/artifacts/rebind_after_first_meld_20261003/
- this ticket, the story, attention_board.md, artifact_board.md

## Validation
- RUN 2026-10-03T19:17:48Z (VM, mirror, 3.14.7t): 2 failed / 2 passed - see Notes. Command:
  - `. ~/.fable_1_env && cd $MELDER_MIRROR && $PY -m pytest /tmp/fable_1/rebind/test_rebind_probe_melder_only.py -q -p no:cacheprovider`

## Risks / Rollback Notes
- The working tree carries fable_0's unlanded S8 edits; a HEAD export (git archive, read-only) is the
  control. Nothing to roll back: no tree edit.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] A search hit is not a read: the transition is named only from source read in full.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: kept with the epic's evidence at closure.

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
- DATETIME: 2026-10-03T19:13:22Z
  TYPE: FACT
  CLAIM: The saved evidence fixes the operation prefix: bind -> meld -> (withdraw peer grant) ->
  cleanup_spell -> bind same class/spellframe/name (existence many) -> meld fails with "Cannot build
  CreationContext before spell_codegen_creation exists" at CreationContextBuilder.build; the two cases
  that skip the first meld pass, linking is irrelevant. Recorded on Melder 0.2.8215 (installed wheel),
  3.14.7t, 2026-10-03T13:55:44Z; current source behaviour is UNKNOWN.
  EVIDENCE:
  - artifacts/2026-10-03_rebind_after_first_meld/rebind_retest_2026-10-03.json:19-60
  - artifacts/2026-10-03_rebind_after_first_meld/test_native_rebind_probe.py:26-63
  - artifacts/2026-10-03_rebind_after_first_meld/native_rebind_finding.md:1-48
  IMPACT: the first meld is the differentiator, so the state the first meld leaves on the OLD spell or
  on shared per-address state is where to look.
  NEXT: port the probe to the Melder-only reset fixture and run it on the working-tree mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T19:17:48Z
  TYPE: MEASURE
  CLAIM: REPRODUCED ON CURRENT SOURCE. The probe ported to Melder's own reset fixture (no MelderOps import)
  gives 2 failed / 2 passed in 0.87s on the working-tree mirror (src/ content-identical to HEAD 4ddf7530f,
  __version__ 0.2.8216; CPython 3.14.7t, GIL off): [True-False] and [True-True] raise RuntimeError
  "Cannot build CreationContext before spell_codegen_creation exists" from CreationContextBuilder.build via
  Conduit.meld -> ConduitMeld.meld -> Meld._execute_admitted -> Spell._get_or_build_creation_context ->
  CreationContextFactory.get_or_build_for_spell; [False-False] and [False-True] pass. Identical to the
  0.2.8215 receipt, so the defect is not fixed and not an environment artefact. Probe and JUnit saved.
  EVIDENCE:
  - artifacts/rebind_after_first_meld_20261003/test_rebind_probe_melder_only.py:1-84
  - artifacts/rebind_after_first_meld_20261003/probe_working_tree.xml:1-1
  - src/melder/aether/conduit/meld/meld.py:882-882
  - src/melder/aether/spellbook/spell.py:847-847
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:361-361
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:121-121
  IMPACT: work package A's first half is done (still failing); the trace can start from a live repro.
  NEXT: read Meld._execute_admitted and its readiness gates, Spellbook.cleanup_spell and bind, and the
  SpellSystemStates validity path for a spell id that is removed and re-registered.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T19:32:35Z
  TYPE: FACT
  CLAIM: CAUSE. Per-conduit resolution verdicts are keyed by spell id and survive the spell's removal. The
  first meld's target pass writes root_validity=valid and spell_validity=valid for the id into the root
  conduit's ConduitResolutionState (`_resolution_by_conduit_id`). `cleanup_spell` -> `invalidate_spell` +
  `cleanup_and_remove_spell` -> `SpellSystemStates.unregister_index` removes the lineage state, the spell-id
  index, the topology and the dependency edges, but never touches `_resolution_by_conduit_id`, and
  `register_index` on the rebind only gates the NEW SpellSystemState (structural). The rebind of the same
  class at the same address mints the same content-stable spell id with a fresh Spell object and no compiler
  artifact; at meld #2 the structural state is already valid (late binds compile 1-4 eagerly), so
  `_gated_validation_required` is False and `_force_resolution_revalidation` never runs;
  `_get_resolution_validity` (not a phase-5 root yet, so `get_spell_validity`) returns the dead spell's
  `valid`; `_ensure_resolution_resolvable` returns without phases 5-11; `_execute_admitted` reaches
  `CreationContextBuilder.build` with `artifact._spell_codegen_creation is None`. Instrumented run printed
  every state above (diag_rebind_output.txt). The controls pass because no verdict exists for an unmelded id.
  EVIDENCE:
  - artifacts/rebind_after_first_meld_20261003/diag_rebind_output.txt:1-45
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:743-832
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:299-353
  - src/melder/aether/spellbook/spellbook.py:4138-4245
  - src/melder/aether/spellbook/spell.py:1353-1425
  - src/melder/aether/conduit/meld/meld.py:1134-1270
  - src/melder/aether/conduit/meld/meld.py:1436-1460
  - src/melder/aether/conduit/meld/meld.py:826-891
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:106-125
  IMPACT: a definition removed after use leaves a stale valid verdict under its content-stable id in every
  conduit that resolved it; the replacement inherits it and skips compilation. Both halves of the owner's
  hypothesis hold: DevOps verdicts are not retired on destroy, and a rebind does not re-gate them.
  NEXT: design the repair in the DevOps control plane (retire the id's conduit verdicts on unregister; gate
  them on register_index) under a patch lane, then propose the exact edit to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-03T19:47:00Z
  TYPE: RISK
  CLAIM: Owner (chat, 2026-10-03 13:44 local): retiring/re-gating the DevOps verdicts may not by itself
  make the REVALIDATION correct; that has to be investigated as part of the repair, not assumed. What is
  evidenced today: the two control cases prove unknown -> `_ensure_resolution_resolvable` ->
  `_run_resolution_phases_for_target_spell` -> context build works for a fresh late-bound spell on this
  tree, so a retired verdict puts the failing cases onto that path. What is NOT evidenced: (a) that the
  target pass republishes a correct plan for the replacement (override honoured, many lifetime, disposal
  list); (b) dependents of the removed definition - `unregister_index` computes the structural impact
  closure, but whether a consumer's phase-11 plan is rebuilt against the replacement is unproven; (c) the
  peer root that resolved the old id through its contract keeps its own verdict - retirement must cover
  every conduit, not the melding one; (d) RiskManager coherence - the structural callback gets
  `SpellValidity.cleaned`, the resolution callback gets nothing today; (e) whether an eagerly-valid
  structural state over an absent conduit verdict is the intended shape, versus gating the new state so
  `_force_resolution_revalidation` runs the normal structure-changed route.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:743-832
  - src/melder/aether/conduit/meld/meld.py:1208-1270
  - src/melder/aether/conduit/meld/meld.py:1388-1435
  - artifacts/rebind_after_first_meld_20261003/probe_working_tree.xml:1-1
  IMPACT: the repair's acceptance bar is a revalidation matrix (self, dependents, peer conduit, override,
  disposal, risk view), red-to-green, not the exception disappearing; the patch docs must state it.
  NEXT: read `Spellbook._run_resolution_phases_for_target_spell` and the creation system's target pass in
  full to name what a rerun republishes and for whom, then write the matrix into the repair task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-03T20:06:00Z
  TYPE: MEASURE
  CLAIM: PROTOTYPE OF THE REPAIR, in the VM mirror only (the tree is untouched). Two registry verbs:
  `ConduitResolutionState.forget_spell(spell_id, *, change_reason)` pops the spell-level and root-level
  verdict for one id (dirty-marked, no RiskManager callback - lineage membership in the risk model is
  owner-scoped and recomputed by `register_spell`, so a callback would leave a sticky risky key in peer
  conduits); `SpellSystemStates._forget_resolution_verdicts_locked(spell_id, *, change_reason)` applies it to
  every live conduit state under the registry lock (registry -> state is the only lock order; no callback
  runs), called from `unregister_index` (reason cleaned_up_spell, both branches) and from `register_index`
  (reason register_or_rebind, before the structural gate), plus the public `forget_spell_resolution_verdicts`.
  Results on CPython 3.14.7t: the four-case probe 4/4 (was 2/4); the revalidation matrix 7/7, of which M1
  (replacement re-resolved: own phase 5-11 artifacts, root verdict valid, old product alive), M3 (a peer
  conduit that melded the old definition through its contract melds the replacement with its override),
  M4 (old and new product both disposed by the scope's cleanup) and M5 (`_spellbook_validation_required`
  True after the rebind, False after the revalidating meld) were red on the unpatched 0.2.8218 tree, and
  M2/M2b (a dependent consumer rebuilds against the rebound address - a different class under the same
  spellframe, and the same class) were already green (the structural impact closure in `unregister_index`
  covers dependents). Full tiers on the prototype: unit 8829 passed, component 2283, integration 2011,
  tests/tests+experimentation+experiments 250; 0 failures. Unpatched baseline on 0.2.8218: 7 failed / 4
  passed over the same 11 cases.
  EVIDENCE:
  - artifacts/rebind_after_first_meld_20261003/fix/apply_forget_verdicts.py:1-347
  - artifacts/rebind_after_first_meld_20261003/fix/prototype.diff:1-265
  - artifacts/rebind_after_first_meld_20261003/fix/prototype_results.txt:1-22
  - artifacts/rebind_after_first_meld_20261003/fix/baseline_unpatched_0_2_8218.txt:1-4
  - artifacts/rebind_after_first_meld_20261003/test_rebind_revalidation_matrix.py:1-278
  IMPACT: the exception half and the revalidation half (self, peer conduit, dependents, disposal, risk flag)
  are both measured green; the repair is a two-file DevOps control-plane change with no public API change
  and no meld hot-path cost (bind and removal paths only, O(#conduits) dict pops).
  NEXT: write the DECISION (design + one open semantic question), open the repair task with the patch lane,
  and propose the exact edit to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-03T20:06:00Z
  TYPE: DECISION_REQUEST
  CLAIM: M7 (informational, unique_per_conduit): after `cleanup_spell` the surviving old product stays in
  the root store under the content-stable spell id, so the replacement definition's first meld returns THAT
  object (same instance, value 1, override ignored) instead of building a new singleton - the replacement
  inherits the old product's slot. On the unpatched tree the same case raises the RuntimeError. The MelderOps
  Actions case is `many`, where each meld builds, so this does not block the repair; it is a semantic ruling
  for the owner: (a) accept and document ("a surviving singleton is the replacement's instance until its
  scope disposes it"), or (b) a follow-up that retires the old product's slot on definition removal for the
  slotted existences. Not evidenced: what the owner intends here.
  EVIDENCE:
  - artifacts/rebind_after_first_meld_20261003/test_rebind_revalidation_matrix.py:261-278
  - artifacts/rebind_after_first_meld_20261003/fix/prototype_results.txt:2-2
  IMPACT: decides whether the repair ships with a documented singleton rule or opens a follow-up task.
  NEXT: owner rules (a) or (b); the repair lands either way.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-10-03T20:06:00Z: cause is a FACT, repair prototyped and measured green in the VM mirror (fix/ under the artifact folder); the tree is untouched. Handing off to the repair task (patch lane rebind_after_first_meld_2026_10_03). Open: the M7 singleton-slot ruling.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
