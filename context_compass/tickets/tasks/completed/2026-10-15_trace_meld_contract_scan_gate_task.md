# Task: Trace why Meld._ensure_lineage_resolvable scans SpellContract defaults on every gated meld

## Metadata
- Task ID: TASK-2026-10-15-trace_meld_contract_scan_gate
- Story: none - standalone; owner-directed (chat 2026-10-15); the same scan was measured on 2026-10-05 in
  EPIC-2026-10-05-melder_services_and_pools
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T15:31:31Z
- Updated: 2026-10-15T18:46:58Z

- Completed: 2026-10-15T18:46:58Z
- Summary: Investigation only. The meld gate's SpellContract scan is unconditional since 438efc387
  (2026-01-28); the Book-wide validation flag clears once every visible spell resolves, but a resolvable=False
  definition pins it for good and a late bind until its first meld, and then every meld scans (~21 us of 23).
  The owner directed the fix: successor TASK-2026-10-15-make_meld_state_checks_follow_spell_state.

## Objective
A MelderOps agent reported that every meld of its Task runs `inspect.signature` through
`Meld._ensure_lineage_resolvable` -> `_check_contracts_and_force_revalidation` -> `_iter_spell_contract_defaults`.
The owner read the code (chat 2026-10-15): the check is too strict - a spell's state should decide when it runs, it
should skip fast, and it should not do a deep lookup on every meld or for every spell. Trace the method through the
git history and the tickets: when the contract check and its placement arrived, and why. Investigation only: no
`src/` change until the owner picks the fix.

## Ticket Contract
- ENTRY_GATE: the board row routes this task; findings are recorded in Notes before the answer.
- EXECUTION_BOUNDARY: read-only on `src/`, git history (read-only commands with GIT_OPTIONAL_LOCKS=0) and tickets;
  logs under artifacts/meld_contract_scan_20261015/; this ticket and the boards.
- DEPENDENCIES: EPIC-2026-10-05-melder_services_and_pools (the 2026-10-05 measurement and its memo plan).
- EXIT_GATE: the claim answered point by point from the code; the history of the gate and the contract check traced
  to commits and tickets; the owner picks the fix or redirects.
- FAILURE_ESCALATION: DECISION_REQUEST for the fix approach; BLOCKER if the history cannot be read safely.

## Scope Boundaries
- In scope: `Meld._ensure_lineage_resolvable`, `_check_contracts_and_force_revalidation`,
  `_iter_spell_contract_defaults`, `_force_resolution_revalidation`, the Spellbook validation flag (RiskManager),
  the ConduitMeld and SpellSpaceMeld gate calls, their git history and the related tickets.
- Out of scope: any fix; MelderOps code; melder_0's managed_spell_quantity lane.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the investigation (chat 2026-10-15: "go look this up in dynamic mode", then
  "trace this method ... look up the git history and look up the tickets related to it").

- from_state: in_progress
- to_state: done
- transition_reason: the claim is answered from the code, the history and two probes, and the owner picked the
  fix (chat 2026-10-15); the successor task carries it.

## Steps / Checklist
- [x] Read the gate path in the code (ConduitMeld.meld step 3, Meld._ensure_lineage_resolvable,
      _check_contracts_and_force_revalidation, _iter_spell_contract_defaults, RiskManager's flag).
- [x] Trace the git history of the method and the contract check.
- [x] Find the related tickets and what they decided.
- [x] Answer the owner; record his pick.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- A point-by-point answer with code, commit and ticket evidence.

## Files / Paths Impacted
- context_compass/tickets/tasks/2026-10-15_trace_meld_contract_scan_gate_task.md
- context_compass/artifacts/meld_contract_scan_20261015/ (git and grep logs)
- context_compass/attention_board.md, context_compass/artifact_board.md

## Validation
- Git history read with GIT_OPTIONAL_LOCKS=0; no index lock appeared (artifacts/meld_contract_scan_20261015/git_*.txt).
- Probes on the live repo, Python 3.14.7t, GIL off and on, in artifacts/meld_contract_scan_20261015/runs/:
  probe_gil0.txt, probe_gil1.txt and probe_flag_recovery_gil0.txt. No test suite run: nothing in src/ changed.
- Recommended commands:
  - GIT_OPTIONAL_LOCKS=0 git log -L (read-only), with .git/index.lock checked before and after

## Risks / Rollback Notes
- Read-only investigation; nothing in `src/` changes.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
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
  - artifacts/meld_contract_scan_20261015/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none - the folder stays rowed under the successor task

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - when a meld runs the SpellContract scan, and how it came to run unconditionally
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; the whole ticket;
  initial revision 2026-10-15T15:31:31Z; the direction is the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: 2026-10-15T15:31:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The gate path as the code stands. `ConduitMeld.meld` and `SpellSpaceMeld.meld` call
    `_ensure_lineage_resolvable` only while the Spellbook's `_spellbook_validation_required` flag is set, not on
    every meld. That flag is Book-wide: RiskManager sets it whenever any lineage the conduit sees is not `valid`,
    structurally or in that conduit, and clears it only when none is. Inside the method the structural rerun is
    guarded by the spell's own state, but `_check_contracts_and_force_revalidation` runs unconditionally after it,
    and it starts with `_iter_spell_contract_defaults`, which calls `inspect.signature(..., FORWARDREF)` with no
    cache and no state check; a spell without SpellContract defaults gets [] every time. For a spell whose contracts
    resolve, it then gates the spell's resolution validity, so `_ensure_resolution_resolvable` reruns its resolution
    phases. Dynamic spells never mint a fast-door entry (they run `_execute_admitted`), so every dynamic meld
    reaches the flag check. So the scan runs on every meld of every spell in a Book while any one lineage there is
    risky, for spells whose own state is valid. The compiler scans the same defaults at compile time (Phase 8
    analyzer, Phase 9 contract processor).
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:576-580
  - src/melder/aether/conduit/meld/conduit_meld.py:589-640
  - src/melder/aether/conduit/meld/spellspace_meld.py:524-526
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:624-655
  - src/melder/aether/conduit/meld/meld.py:933-987
  - src/melder/aether/conduit/meld/meld.py:1311-1380
  - src/melder/aether/conduit/meld/meld.py:1382-1427
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1054-1083
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:185-300
  IMPACT: The MelderOps claim is right about the scan and its missing cache, but the trigger is the Book-wide flag
    rather than every meld; the cost lands on every spell whenever any spell in the Book is risky. The owner calls
    this too strict: a spell's state should decide when the check runs.
  NEXT: Trace the git history of the method and the contract check, then the related tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T15:38:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: History (git, read-only) and tickets. 2026-01-25 4dd6efdd5 made `_ensure_lineage_resolvable` the gate in
    front of every meld; the same day c21be881c added RiskManager and put that gate behind the Book-wide
    `_spellbook_validation_required` flag. 2026-01-28 438efc387 added `_check_contracts_and_force_revalidation`
    to the method, unconditionally after the structural branch, with an uncached `inspect.signature(call_target)`
    scan; its message names only unit tests ("Update MeldEngine kwargs unit tests ... after phase migration") and
    its two new tests are "missing contract raises" and "contract forces revalidation". No ticket records why;
    the docstring is the only stated intent (validate SpellContract providers at meld, rerun phases 5-11 when
    contracts exist). Later commits kept the call where it was: d8b643f37 (2026-02-15, resolution_required
    lane), 1102bfab9 (2026-05-30, Meld split), d241361c0 and 22c07323e (2026-07-11, lineage admission added and
    removed), 63ef620e3 (2026-09-19, structure_changed revalidation), 9eb100389 (2026-09-26, rebuild window).
    Tickets that met it described or patched it without gating it: the 2026-06-04 mutation-contract epic (runtime
    step 5, after Phase 4 already marks a lineage `gated` + `contract_unvalidated` and link changes dirty the
    affected consumers), the 2026-06-06 and 2026-06-22 mapping tasks, the 2026-09-13 repair (annotation format
    only) and the 2026-10-05 services epic (measured; memo plan never started). So the state the owner describes
    exists - Phase 1 classifies contract sockets, Phase 4 sets `contract_unvalidated`, contract-link changes dirty
    consumers - and the meld check has never read it.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/git_show_4dd6efdd5_c21be881c_meld.txt:1-12
  - context_compass/artifacts/meld_contract_scan_20261015/git_show_4dd6efdd5_c21be881c_meld.txt:53-110
  - context_compass/artifacts/meld_contract_scan_20261015/git_show_438efc387.txt:1-200
  - context_compass/artifacts/meld_contract_scan_20261015/git_pickaxe_call_site.txt:1-3
  - context_compass/artifacts/meld_contract_scan_20261015/git_commit_list_ensure_lineage_resolvable.txt:1-106
  - context_compass/tickets/epics/completed/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md:387-411
  - context_compass/tickets/tasks/completed/2026-06-06_map_mutation_planner_phase11_convergence_task.md:313-325
  - context_compass/tickets/tasks/completed/2026-06-22_deep_map_phase8_11_meld_creations_existence_task.md:169-182
  - context_compass/tickets/tasks/completed/2026-09-25_survey_compiler_phases_1_to_4_task.md:468-482
  - context_compass/tickets/tasks/completed/2026-09-13_repair_existing_instance_planning_task.md:614-624
  - context_compass/tickets/epics/2026-10-05_melder_services_and_pools_epic.md:22-25
  IMPACT: The over-strict check is original to 2026-01-28 and was never revisited; the owner's direction (the
    spell's state decides, a fast skip, no deep lookup per meld or per spell) replaces the services epic's memo
    plan.
  NEXT: Answer the owner and record his pick of the fix lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T15:49:26Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Correction raised by the owner (chat 2026-10-15: "by default its set to True"): `Spellbook.__init__` sets
    `_spellbook_validation_required = True`, and only RiskManager ever lowers it - `register_conduit`, called once at
    the end of a conjure, seeds the root's bucket from every visible spell (owned and contracted) and refreshes the
    flag; later validity events refresh it again. So the gate is open by default and closes only if, at that moment
    and after, every lineage the root sees is valid structurally and in that conduit. My earlier reply ("only while
    any spell is unknown or gated") stated the code's rule without checking whether the flag ever actually drops in a
    real world; that is UNKNOWN until measured. Plan: a dynamic-mode probe that reads the flag and the risky sets
    after conjure, counts `_ensure_lineage_resolvable` entries and contract scans per meld, and times them.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:352-355
  - src/melder/aether/spellbook/spellbook.py:6031-6057
  - src/melder/aether/spellbook/spellbook_creation_system.py:1040-1072
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:251-283
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:624-655
  IMPACT: Whether the scan runs on every meld in practice depends on the flag ever clearing; the probe settles it.
  NEXT: Write and run the dynamic-mode probe on the live repo, GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T15:51:47Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Probe on the live repo (source 0.2.8244, Python 3.14.7t, GIL off and on, 2000 melds per case). When every
    spell resolves (automatic or dynamic, root or lesser), conjure drops the flag to False and it stays there: no
    gate entry, no scan, 0.3 us per meld automatic (fast door) and 0.7 us dynamic. Two ordinary things pin it True:
    a Protocol definition bound resolvable=False (risky_resolution=['IThing'] from conjure on; it can never resolve)
    and a spell bound on the root after conjure that has not been melded (risky_resolution=['Other']). Then every
    meld of every spell - here a valid `many` Task with no contracts - enters the gate and runs one
    inspect.signature: 20.8-23.0 us per meld GIL off (18.7-20.9 GIL on) against 1.9-2.1 us with the scan stubbed;
    inspect.signature(Task, FORWARDREF) alone costs 10.5 us (14.1 GIL on).
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_gil0.txt:1-25
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_gil1.txt:1-25
  - context_compass/artifacts/meld_contract_scan_20261015/probe_meld_contract_scan.py:1-179
  IMPACT: The default True only clears when every lineage the root sees is resolved, and one non-resolvable
    definition or unmelded late bind - both normal in a dynamic world - pins the Book-wide flag for good, so the
    scan runs on every meld of every spell. Two strictness problems: the Book-wide flag counts lineages that never
    or need not resolve, and inside the gate the scan ignores the spell's own state.
  NEXT: Answer the owner with the measurement and record his pick of the fix lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T16:13:20Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Recovery of the flag, same setup (GIL off). A late bind on the root raises the flag (risky_resolution=
    ['Other']) and melding that spell once drops it back to False; later melds stay off the gate. A Protocol
    definition bound resolvable=False keeps it True after every resolvable spell has been melded (risky_resolution=
    ['IThing']): it never drops. So the MelderOps agent's "every meld" is overstated as a rule - the flag clears
    once every spell the root sees has resolved - but it holds in any Book carrying a non-resolvable definition,
    and between a late bind and that spell's first meld.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_flag_recovery_gil0.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/probe_flag_recovery.py:1-40
  IMPACT: The scan on every meld is a pinned-flag condition, not the default steady state; a non-resolvable
    definition pins it permanently, which is the likeliest cause in the MelderOps world (UNKNOWN until checked there).
  NEXT: Answer the owner; record his pick of the fix lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T18:32:29Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner ruling (chat 2026-10-15): spells bound resolvable=False are often deliberate and must be excluded
    from state checks. Today they are not. RiskManager seeds every visible spell with no `resolvable` test, reads its
    conduit resolution verdict, and counts anything but `valid` as risk; a spell with no verdict reads the state's
    initial `unknown`. A resolvable=False spell never gets a verdict (it is left out of resolution planning, and a
    direct meld refuses it), so it pins the Book-wide flag for the Book's life - measured: risky_resolution=['IThing']
    after conjure and after every resolvable spell was melded. Every meld of every other spell then pays the gate
    and the contract scan. The fix lane, when opened, takes both rules: the flag ignores resolvable=False spells, and
    the meld-side check follows the melded spell's own state.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:320-366
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:476-493
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:546-571
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:643-655
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:230-247
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_flag_recovery_gil0.txt:4-4
  IMPACT: A deliberate registration silently costs every meld in its Book about 20 us; excluding it is part of the
    fix, not an option.
  NEXT: Wait for the owner's go on the fix lane; no `src/` change before it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T18:46:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner's pick (chat 2026-10-15): "thats an issue we need to address ... those spells are meant to be
    unresolvable and are meant to just be observable by nexus so lets figure this out". The question is answered and
    the trace is complete; the fix and its design move to TASK-2026-10-15-make_meld_state_checks_follow_spell_state,
    which takes this task's findings, its probes and its evidence folder. Closed by its assigned agent; no review asked.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:1-20
  IMPACT: The board routes the successor; this task's Notes are the reference for the fix's design.
  NEXT: None here; the successor reads the code paths the fix touches and proposes the design.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done (2026-10-15T18:46:58Z). The scan, the Book-wide flag that admits it and its history are recorded in Notes, with two
probes. Next: TASK-2026-10-15-make_meld_state_checks_follow_spell_state (the fix and its design).

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
