# Task: Keep resolvable=False spells out of the meld gate and run the contract check only when a spell's state calls for it

## Metadata
- Task ID: TASK-2026-10-15-make_meld_state_checks_follow_spell_state
- Story: none - standalone; follows TASK-2026-10-15-trace_meld_contract_scan_gate (done); supersedes the memo plan
  (STORY-TBD-meld_contract_scan_memo) of EPIC-2026-10-05-melder_services_and_pools
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T18:46:58Z
- Updated: 2026-10-16T09:36:46Z

- Completed: 2026-10-16T09:36:46Z
- Summary: Rule 1 landed, notched 0.2.8247: a lineage whose selected version was bound resolvable=False carries
  `SpellState.non_resolvable`, and RiskManager's Book validation flag leaves it out, so one Protocol or abstract
  definition no longer sends every meld of its Book through the validation gate (15-16 us -> 0.3-0.7 us a warm
  meld). Release-note section: "A non-resolvable definition no longer sends every meld of its Book through
  validation". The owner accepted it; rule 2 (check a contract only when the consumer's state calls for it, and
  recheck consumers on a notch) moved to TASK-2026-10-16-recheck_contract_consumers_when_provider_changes.

## Objective
Two rules from the owner (chat 2026-10-15). Spells bound resolvable=False are deliberate - meant to stay
unresolvable and only observable by Nexus - so they must be excluded from the meld state checks; today RiskManager
counts them, and one such spell keeps the Book-wide validation flag up for the Book's life. And a spell's own state
must decide when the SpellContract check runs: skip fast, no `inspect.signature` on every meld or for every spell.
Design first, with the owner ("lets figure this out"); no `src/` edit before he approves the design.

## Ticket Contract
- ENTRY_GATE: the board row routes this task; the code paths are read whole and recorded; the owner approves the
  design; before any `src/` edit, the patch docs under system_docs/patches/active/meld_state_gate_2026_10_15/
  exist and are linked.
- EXECUTION_BOUNDARY: design phase: read-only on `src/`; probes under artifacts/meld_contract_scan_20261015/;
  the patch docs. After approval: the files the approved design names (expected: RiskManager and Meld), their
  tests, system docs, the release note, the notch and the rebuild.
- DEPENDENCIES: TASK-2026-10-15-trace_meld_contract_scan_gate (findings and probes); melder_0's managed_spell_quantity
  lane (no shared file is edited without a handoff).
- EXIT_GATE: no resolvable=False spell holds the flag; a meld of a spell whose state needs no contract check makes no
  signature scan; contract-bearing spells still validate and revalidate when their state calls for it; the suites
  pass with the GIL off and on; the cost is measured; docs, notch, rebuild; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for each design choice; CONFLICT if the state machinery cannot express "contract
  validation needed" without a new state.

## Scope Boundaries
- In scope: RiskManager's spell registration and risk sets; the meld gate and its contract check; the state that
  marks contract validation as needed; Nexus visibility of resolvable=False spells (must not change).
- Out of scope: managed_spell_quantity work; the compiler's own contract scans; MelderOps code.

## State Transition Event
- from_state: blocked
- to_state: done
- transition_reason: the owner accepted rule 1 as landed in 0.2.8247 (chat 2026-10-16: asked "shall I mark rule 1
  accepted and close its ticket, then open rule 2 as its own ticket on this story?", he answered "yees sure thats
  good"). The EXIT_GATE's rule-2 conditions move by his direction (Note 2026-10-16T09:30:40Z) to the successor
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes; board and artifact rows are synced.
- prior: in_progress -> blocked (2026-10-16T01:50:42Z), the text below:
- from_state: in_progress
- to_state: blocked
- transition_reason: rule 1 is landed as 0.2.8247 - code, tests (green with the GIL off and on), the four system
  docs and their indexes, the graph, the release note, the notch notice, the archived patch lane, rubric scores -
  and the rebuild runs last. The EXIT_GATE's remaining conditions are the owner's: accepting rule 1 (reserved) and
  answering items (2)-(3), on which rule 2's "no signature scan" condition waits. Unblock: the owner accepts and
  answers, or redirects. The board row reads `review`.
- prior: draft -> in_progress (2026-10-15T18:46:58Z): the owner directed the fix (chat 2026-10-15: "thats an issue
  we need to address ... lets figure this out").

## Steps / Checklist
- [x] Read whole: RiskManager and its callers; SpellSystemStates' contract flags and contract-dirty marking; Phase 1's
      SpellContract classification and what survives conjure; the meld gate methods; Spell.resolvable.
- [x] Propose the design to the owner; record his picks (rule 1: Option A; items (2)-(3) open).
- [x] Write the patch docs; get the owner's go.
- [x] Red tests, the change, green suites (GIL off and on), measurement - on the scratch tree; the real tree waits
      for the call-site handoff.
- [x] Docs, release note, notch, rebuild last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- An approved design and patch docs; then the change with tests, docs, notch and rebuild.

## Files / Paths Impacted
- context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md
- context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/ (patch docs)
- context_compass/artifacts/meld_contract_scan_20261015/ (probes and runs)
- after approval: the `src/` files the design names, their tests, system docs, release_docs/next_version_release.md

## Validation
- Run: every chunk of the test tree (23) with the GIL off and on, on the scratch tree and on a copy of the landed
  tree; the unit, component and mutation checks of each part; the probes before and after; the release-note
  example (Notes 2026-10-15T21:32:39Z to 2026-10-16T01:05:44Z and the Notes of 2026-10-16 below).
- Not run: coverage (pytest --cov); hosted CI.
- Recommended commands:
  - the probes in artifacts/meld_contract_scan_20261015/ (gate entries, scans and microseconds per meld)
  - the meld, conduit, spellbook and dev-ops suites with the GIL off and on

## Risks / Rollback Notes
- The gate guards correctness: a skipped check must be one the spell's state proves unnecessary, never a guess.

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
  - system_docs/patches/completed/meld_state_gate_2026_10_15/
- DISPOSITION: retain_as_reference for the artifact folder; promote_to_documentation for the five patch docs
  (promoted at 0.2.8247 to src_architecture, src_components, tests_components, tests_architecture and the graph,
  then archived under system_docs/patches/completed/)
- CLEANUP_TRIGGER: none left - the patch docs are archived; the artifact folder stays as evidence, rowed under
  the successor TASK-2026-10-16-recheck_contract_consumers_when_provider_changes

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - which spells the meld state checks count, and which state decides the contract check
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; the whole ticket;
  initial revision 2026-10-15T18:46:58Z; the direction is the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: 2026-10-15T18:46:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Starting point, from the predecessor's Notes: the meld enters `Meld._ensure_lineage_resolvable` only while
    the Book-wide `_spellbook_validation_required` flag is up; RiskManager keeps it up while any spell the root sees
    lacks a `valid` resolution verdict, and counts resolvable=False spells, which never get one. Inside the gate,
    `_check_contracts_and_force_revalidation` scans the signature on every call and, for spells with contracts,
    forces a resolution rerun every time. Measured: about 21 us of a 23 us meld while the flag is pinned, 0.7 us
    when it is down.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-15_trace_meld_contract_scan_gate_task.md:133-304
  IMPACT: The two rules address the two causes: the flag's membership and the check's trigger.
  NEXT: Read RiskManager's callers and the contract state machinery whole, then propose the design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T19:01:10Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: RiskManager, read whole. Spells enter a conduit's bucket only through `register_spell` (conjure end via
    `register_conduit`, bind, notch, contract add, transfer), always with the actual Spell object, so the active
    version's `resolvable` is at hand; later changes arrive as structural and resolution validity events keyed by
    lineage. Nothing reads `resolvable`, and `_is_risky` counts anything but `valid`. A resolvable=False version gets
    no verdict (left out of planning, refused at meld), so it reads `unknown` for good; a dependency or bind change can
    also gate it structurally, and nothing ever revalidates it. The same flag guards the fast doors: ConduitMeld,
    SpellSpaceMeld, SpellSpace and Conduit only serve a warm meld from the door while the flag is down, so one such
    definition also takes every automatic meld off the fast door.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:251-283
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:320-366
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:410-471
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:574-655
  - src/melder/aether/spellbook/spell.py:767-784
  - src/melder/aether/conduit/meld/conduit_meld.py:436-500
  - src/melder/aether/spellbook/spellbook.py:3906-3919
  IMPACT: Rule 1 fits RiskManager alone: track the lineages whose active version is resolvable=False and let them hold
    no risk on either axis; no other surface changes, and Nexus reads none of this.
  NEXT: Measure the cost the rule removes, with the exclusion emulated in a probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T19:01:10Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The contract state already exists, and one path bypasses it. Phase 3 records each SpellContract socket in a
    per-Book reverse index (key -> consumer lineages); Phase 4 marks a consumer `gated` + `contract_unvalidated` when
    its provider is missing and clears the flag when present; `mark_contract_dependents_dirty` gates the consumers of a
    key, and it runs on link (change-control commit hook), grant, uncontract, sever and remove-all (ward invalidation).
    Phase 9 bakes the provider's spell id into the consumer's plan, so a provider change needs a rebuild. When a lender
    notches an index-linked spell, or parks a version-anchored copy, the owner's fan-out ends in the borrower Book's
    contracted-map mutators (park, reactivate, add), and none of them marks the key's consumers. Today the meld's
    unconditional scan papers over that: it forces a 5-11 rebuild of every contract consumer on every gated meld.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1309-1389
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1391-1447
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1532-1556
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:147-177
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:840-873
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2740
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2380
  - src/melder/aether/conduit/conduit.py:5907-5936
  - src/melder/aether/spellbook/spellbook.py:1623-1751
  - src/melder/aether/spellbook/spellbook.py:1809-1842
  - src/melder/aether/spellbook/spellbook.py:3155-3214
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:185-298
  - src/melder/aether/conduit/meld/meld.py:933-988
  - src/melder/aether/conduit/meld/meld.py:1311-1474
  IMPACT: Rule 2 is safe only if the borrower marks the key's consumers wherever its active contracted copy changes;
    then the structural branch (Phase 4 presence, structure_changed rebuild) does everything the scan did.
  NEXT: Measure today's consumer cost and whether a consumer follows a lender notch without the scan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T19:01:10Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Design probe (live repo, Python 3.14.7t, GIL off / on; monkeypatches only). A Protocol definition bound
    resolvable=False pins the flag in automatic worlds too: 22.8 / 19.1 us per meld, 0.3 us with the exclusion
    emulated (the fast door comes back); dynamic 27.9 / 20.7 -> 0.9 / 0.8 us. A SpellContract consumer in a borrower
    Book costs 2663 / 2354 us per meld today: the borrowed provider's lineage stays `unknown` in the borrower and pins
    its flag, and every meld forces the consumer's 5-11 rebuild; with the scan removed it is 2.0 / 1.9 us. But with the
    scan removed the consumer keeps getting version A after the lender notches to B (and its lineage reads `valid`):
    today the consumer follows a notch only through the per-meld rebuild.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_design_baseline_gil0.txt:1-21
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_design_baseline_gil1.txt:5-25
  - context_compass/artifacts/meld_contract_scan_20261015/probe_design_baseline.py:1-269
  IMPACT: Both rules are large wins (60x for automatic worlds with a definition, ~1300x for contract consumers); rule 2
    needs the borrower-side marking or consumers stop following a notch.
  NEXT: Propose the design to the owner with the decisions it needs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T19:01:10Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Proposed design, for the owner. (1) RiskManager keeps a per-conduit set of lineages whose active version is
    resolvable=False; `register_spell` puts a lineage there (or takes it out when a resolvable version becomes active)
    and clears its risk, and both validity updates ignore lineages in it. (2) The meld drops the unconditional scan and
    the forced rebuild; a contract change reaches the meld through the consumer's state, and the scan runs only on the
    failure path, to raise today's MeldExecutionError ("SpellContract could not be resolved ... param ... key") when a
    rerun leaves the lineage `contract_unvalidated`. (3) The borrower Book marks the key's consumers `gated` +
    `contract_unvalidated` wherever its active contracted copy changes (add, park, reactivate, remove), which covers
    notch, notch back, park and destroy; gate only, so stored consumer objects keep their provider, as today. Asks:
    approve (1)-(3); gate-only on a notch rather than also dropping stored consumers as grant and sever do; and the
    handoff of spellbook.py (melder_0's file; (3) is about ten lines there). Borrowed spells still hold a borrower's
    flag until melded there; that is correct and costs about 2 us per meld after the fix; no change proposed.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_design_baseline_gil0.txt:1-21
  - src/melder/aether/conduit/meld/meld.py:933-988
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:320-366
  - src/melder/aether/spellbook/spellbook.py:1623-1751
  IMPACT: Rules 1 and 2 hold without new states; files: RiskManager, Meld, the Book's contracted maps, their tests,
    system docs, release note, notch, rebuild.
  NEXT: The owner's answers; then the patch docs under system_docs/patches/active/meld_state_gate_2026_10_15/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T19:43:37Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner ruling (chat 2026-10-15): "discuss a way to introduce a new systemspellstate that can exclude objects
    that have no intention of being resolved, and thus must be overriden thats the point of resolvable, you don't need
    to invent a new solution please explore these options first". Item (1) of the design request (a RiskManager-private
    set) is withdrawn: the exclusion belongs in the spell-state model, chosen after reading its existing options and
    the intent of `resolvable`. Items (2) and (3) (the contract check) are unchanged and still await his answer.
  EVIDENCE: context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:222-246
  IMPACT: Discussion only; no patch docs or `src/` edits until the owner picks the option.
  NEXT: Read the intent of `resolvable` and the state model, record them, bring the options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T19:43:37Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The intent of `resolvable` (EPIC-2026-09-19-discoverable-non-resolvable-registrations, owner-directed):
    abstract bases, Protocols and internal helpers are registered so agents can discover, inspect, version and
    navigate them in Nexus, while Melder never resolves them - "graph membership must describe the actual
    architecture while execution membership states what Melder may resolve". The capability is per Spell version
    (default True; a notch can flip it; a Protocol target must be False). A consumer parameter whose only match is a
    False definition compiles as an OVERRIDE_REQUIRED socket that keeps the reference for the graph; the value is
    supplied by override at construction. Direct meld and reuse refuse a False version at the door, before the
    validation gate and independently of the Book flag; planning (Phase 5 snapshot, phases 8-11, cache ids) leaves
    it out; Nexus publishes it; the Crystallizer replays the bool. That lane changed registration, compiler,
    runtime, Nexus and records, but not the state model: SpellSystemState and RiskManager have no notion of it.
  EVIDENCE:
  - context_compass/tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md:19-42
  - context_compass/tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md:105-153
  - context_compass/tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md:289-300
  - context_compass/tickets/stories/completed/2026-09-19_discoverable_resolution_runtime_story.md:37-37
  - src/melder/aether/spellbook/spellbook.py:5477-5479
  - src/melder/aether/conduit/meld/conduit_meld.py:559-561
  - src/melder/aether/conduit/meld/meld.py:812-838
  - src/melder/aether/spellbook/spellbook_creation_system.py:2855-2895
  - context_compass/system_docs/src_components.md:4020-4040
  - context_compass/system_docs/src_components.md:864-864
  IMPACT: A False lineage is a declared absence of resolution, not pending work; any state check that waits for its
    verdict waits forever.
  NEXT: Read the state model for where that declaration belongs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T19:43:37Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The state model has three axes: `SpellValidity`, the coarse gate meld reads, one enum for the structural
    verdict (SpellSystemState) and the per-conduit resolution verdict (ConduitResolutionState); `SpellState` flags, the
    accumulating explanation of why a lineage is in its state, each owned by the subsystem that sets it (validation
    clears only the topology flags); and `SpellStateChangeReason`, the last event. `unknown` means never validated -
    work still owed. A False definition never receives a resolution verdict, so each conduit answers its initial
    `unknown` forever and RiskManager, which counts anything but `valid`, reads that as risk; nothing in the model can
    say that no verdict is owed. The flag axis already carries this pattern twice: transfer sets `disabled` +
    `transfer_in_progress` and clears it; Phase 4 and contract marking set `gated` + `contract_unvalidated`.
    `register_index` is where a lineage's selected version is (re)registered (bind and notch change it; transfer
    re-registers the same one). Flags are not persisted: no Crystallizer, Nexus or MutationResearch reader, and the
    structural snapshot reads only `contract_unvalidated`.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_state.py:1-75
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_validity.py:1-85
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_state_change_reason.py:1-99
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:349-417
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:613-666
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:307-374
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:230-247
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:643-655
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:855-891
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:147-177
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:424-424
  IMPACT: The missing state is an explanation ("excluded by declaration"), so it belongs on the flag axis; the gate
    axis stays truthful.
  NEXT: Weigh a new flag, a new validity value and reuse of an existing state; bring them to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T19:43:37Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: STRATEGY_DISCUSSION
  CLAIM: (A, recommended) A new `SpellState` flag, `non_resolvable` (or `override_required`): the selected version is a
    resolvable=False definition, kept for discovery and versioning and supplied to its consumers by override; it owes
    no resolution verdict. Producer: `register_index` takes the selected version's capability and sets or clears the
    flag before its own `mark_structural_change`, so every bucket already sees it when that gated event publishes; bind
    and notch pass it, transfer keeps it; validation never clears it (existing rule). Consumer: RiskManager reads the
    flag from the lineage's state in `register_spell` and in both validity events and gives a flagged lineage no risk;
    validity stays truthful and RiskManager keeps no set of its own. Meld, Nexus and records are unchanged; the meld
    hot path does not read it. (B) A new `SpellValidity` value: every validity writer (Phase 4, dependency and contract
    marking, transfer) would have to respect it, per-conduit states are created lazily and cannot know the
    capability, and the meld raises on an unrecognised value. (C) Reuse `disabled` or `anchored_component`: `disabled`
    is the transfer window's refusal and must stay risky; `anchored_component` means a non-mutable infrastructure
    component. Emulated effect of the exclusion: 22.8 -> 0.3 us per meld (automatic), 27.9 -> 0.9 us (dynamic).
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_design_baseline_gil0.txt:2-9
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:320-471
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:307-374
  - src/melder/aether/spellbook/spellbook.py:3906-3919
  - src/melder/aether/spellbook/spellbook.py:5686-5694
  - src/melder/aether/conduit/meld/meld.py:1174-1244
  IMPACT: Files for (A): spell_state.py, spell_system_states.py, risk_manager.py, two call sites in spellbook.py
    (melder_0's file), tests, docs, release note, notch, rebuild.
  NEXT: The owner picks the option and the flag's name.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T20:29:45Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner ruling (chat 2026-10-15): "well do the recommended, it makes sense to add a new spellstate just map
    that out to ensure we don't break anything please fully understand the implications of the state system but I
    agree with A sounds reasonable", then "make regression tests for this please so we can properly ensure it
    works". Option A is approved: a new `SpellState.non_resolvable` flag (the recommended name) for a lineage whose
    selected version is a resolvable=False definition, produced where that version is registered and read by
    RiskManager, with the validity axis left truthful. Before any `src/` edit: map every reader and writer of the
    state model from source, write the patch docs, and settle the producer's call sites (spellbook.py and
    transfer_of_ownership.py are melder_0's). Regression tests are part of the deliverable. Items (2)-(3) of the
    design request (the contract check) are not answered and stay out of this change.
  EVIDENCE: context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:323-350
  IMPACT: Rule 1 moves to implementation after the map and the patch docs; rule 2 waits for the owner.
  NEXT: Map the state system's readers and writers from source and record the map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T20:49:27Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: State-system map, producer side (read whole). `SpellSystemStates.register_index` is the only call that
    (re)registers a lineage's selected version: it reuses an existing state (its flags survive) and creates one only
    for a new index, retires the verdicts held for the selected id, then gates the index; the gate publishes to
    RiskManager outside the state lock but inside the registry lock. Callers: bind and notch, each followed by
    `register_spell` for the owner conduit, and three transfer sites - the flip unregisters the lineage and registers
    it again on the same frame registry, so a transferred lineage gets a fresh state and loses every flag; the
    rollback re-registers (a fresh state only when the two Books use different registries); the disable step
    registers a missing state. SpellIndex holds ids only, so the capability must come from the caller, and all five
    call sites are in melder_0's files. Flag writers today: the state's topology helpers and `clear_dirty` (topology
    flags only), contract marking, Phase 4 and the structural-snapshot replay (`contract_unvalidated`), transfer
    (`transfer_in_progress`). Readers: the meld gate (`transfer_in_progress`) and the snapshot capture
    (`contract_unvalidated`). No Crystallizer, Nexus or MutationResearch reader; snapshot rows carry no other flag
    and replay touches no other flag; no test enumerates the members; the graph descriptor lists them (with a stale
    `new_lineage`).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:307-374
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:349-417
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:517-549
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:613-666
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:765-871
  - src/melder/aether/spellbook/spellbook.py:5686-5694
  - src/melder/aether/spellbook/spellbook.py:3904-3919
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:855-891
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:958-1002
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1443-1491
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:153-177
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:388-426
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:672-702
  - src/melder/aether/conduit/meld/meld.py:1174-1244
  - src/melder/_build_assets/_system_documents/payloads/src_graph_payload.py:3115-3125
  IMPACT: register_index can set the flag before it gates, so every risk bucket sees it when the gated event
    publishes; the transfer flip must pass the capability or a transferred definition pins the flag again.
  NEXT: Map the consumer side (RiskManager, the meld doors, borrowers).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T20:49:27Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: State-system map, consumer side (read whole). RiskManager mirrors validity per (conduit, lineage) in two
    sets and computes resolution risk for the lineage's selected version id, so a lineage flag that describes the
    selected version matches how risk is already computed. It never holds its lock while calling the registry; the
    registry calls it under the registry lock; ConduitResolutionState publishes outside its lock. The Book flag is
    read only by the meld doors and the gate. Exclusion is safe: every meld door refuses a resolvable=False target
    before the flag-guarded gate (ConduitMeld, SpellSpaceMeld and both reuse paths), and warm doors are minted only
    after admission; a borrower's active copy is the owner's active member when contracted, and after a lender
    notch the conduit parks or moves borrowers' copies once the transaction ends - in that window a borrower can
    meld its old copy, whose plan survives (`_cleanup_creation_context` clears only the context). Today a False
    lineage stays in the resolution-risk set for good, and a reactivated borrowed copy is never re-registered with
    RiskManager: if the exclusion emptied the sets, a notch from a False to a True version would leave reactivated
    borrowers with no resolution risk for the new version. While the flag is up every meld runs
    `_ensure_lineage_resolvable`, whose contract scan rebuilds each SpellContract consumer per meld: a Book held up
    only by False definitions loses that per-meld rebuild and behaves like the same Book without them.
    `register_conduit` refreshes once per seeded spell. Pre-existing: refreshes set the Book flag outside the manager
    lock, so two can land out of order; a removed lineage is risky until `unregister_spell` drops it.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:251-283
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:320-366
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:410-471
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:527-571
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:624-655
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:271-325
  - src/melder/aether/conduit/meld/conduit_meld.py:436-443
  - src/melder/aether/conduit/meld/conduit_meld.py:559-580
  - src/melder/aether/conduit/meld/conduit_meld.py:821-822
  - src/melder/aether/conduit/meld/spellspace_meld.py:514-526
  - src/melder/aether/conduit/meld/spellspace_meld.py:766-767
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1986-1995
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2475-2482
  - src/melder/aether/conduit/conduit.py:5693-5710
  - src/melder/aether/spellbook/spell.py:942-969
  - src/melder/aether/spellbook/spellbook.py:1623-1751
  - src/melder/aether/spellbook/spellbook.py:3155-3214
  - src/melder/aether/conduit/meld/meld.py:933-988
  - src/melder/aether/spellbook/spellbook.py:684-712
  IMPACT: The exclusion belongs where the Book flag is distilled: the risk sets keep tracking exactly as today and
    only the flag ignores flagged lineages, so a notch back to a resolvable version counts again at once.
  NEXT: Record the refined design and the call-site handoff, then write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T20:49:27Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Option A as mapped (refinements inside the approved design; no new concept). (a) `SpellState.non_resolvable`
    is appended and owned by `register_index`; validation never clears it; its only effect is that RiskManager's
    Book flag ignores a flagged lineage's risk - validity, the other flags and every other reader are unchanged.
    (b) `register_index(..., *, resolvable: Optional[bool] = None)`: False sets the flag, True clears it, None keeps
    it only while the selected version is unchanged (a new state, or a changed selection without a capability,
    clears it, so a stale exclusion can never cover a resolvable version); a non-bool raises TypeError; the flag is
    written before `mark_structural_change`, through a new flag-only `SpellSystemState.update_flags` (no publish), and
    read through a new `has_flag`. (c) RiskManager: `_refresh_spellbook_flag` raises the flag only for a risky key
    that is not a lineage whose state has the flag ("spell:" keys and missing states count, as today); the reads run
    outside the manager lock, as its validity reads already do; `register_conduit` seeds and then refreshes once, so
    conjure pays no spells-times-definitions cost. (d) Call sites: bind and notch pass `resolvable=<spell>.resolvable`;
    the transfer flip and its rollback pass `spell_obj.resolvable`; the disable step stays (a missing state is
    conservative). Those are four one-keyword edits in melder_0's files (spellbook.py x2, transfer_of_ownership.py
    x2): the handoff goes through the owner. (e) Until it is granted, the whole change - those four edits included -
    is built and validated on a scratch copy of the tree (suites with the GIL off and on, the probe), and nothing
    lands in the real tree, so no inert half can reach a commit without its notch.
  EVIDENCE: context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:369-452
  IMPACT: Patch docs and a validated prototype next; landing (tests, docs, notch, release note, rebuild) follows the
    handoff.
  NEXT: Write the patch docs under system_docs/patches/active/meld_state_gate_2026_10_15/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T21:01:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written and linked (Artifact Links); read order architecture -> the three component patches -> the
    code description; no conflict with each other or with the canonical docs (src_architecture's meld-time gate and
    RiskManager text describe today's flag, which the landing amends). Mapping, patch section -> implementation ->
    validation: (1) arch invariants 1-2 and component_patch_spell_state_model -> spell_state.py (the member and its
    docstring), spell_system_state.py (`update_flags`, `has_flag`), spell_system_states.py (`register_index`'s
    keyword and its capability write, `index_has_flag`, docstrings) -> unit tests for the state and the registry.
    (2) Invariants 3, 5 and 7, component_patch_risk_manager and the code description -> risk_manager.py
    (`_register_spell_risk`, one refresh in `register_conduit`, the snapshot and `_has_unexcluded_risk` in
    `_refresh_spellbook_flag`, docstrings) -> unit tests on a real registry; the old stub gains `index_has_flag`.
    (3) Invariant 4 and component_patch_registration_call_sites -> the four keywords (scratch tree until the
    handoff) -> component tests: automatic and dynamic worlds, notch both ways, transfer and rollback, an override
    consumer, a borrower, and melds racing notches. (4) Invariant 6 -> review and that race test. (5) Invariant 7 ->
    the probe before and after. (6) Landing -> src_architecture and src_components, the SpellState graph descriptor
    (its stale `new_lineage` too), the release note, the notch, the rebuild.
  EVIDENCE:
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/architecture_patch.md:1-103
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_spell_state_model.md:1-81
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_risk_manager.md:1-70
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_registration_call_sites.md:1-65
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/code_description_patch_risk_distillation.md:1-72
  IMPACT: The entry gate for the melder_1 files is met; the call sites wait for the owner's handoff.
  NEXT: Red tests and the change on the scratch tree (/tmp/cc_res/nonres/tree), then the suites with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T21:20:19Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Gap in the mapped design, found while writing the risk tests: `set_validity` publishes only a changed
    validity, so `register_index` on a lineage already `gated` publishes no event and the other conduits holding the
    lineage keep their Book flags. That is the normal notch-back case: v1 (True) -> v2 (False) gates the lineage and
    nothing revalidates it (a False version is refused before the gate, and a notch recompiles lazily), so the notch
    back to v1 finds it `gated`. The owner's bucket is refreshed by the `register_spell` that follows the notch, but
    an index-linked borrower gets v1 back through `_reactivate_contracted_spell`, which never calls RiskManager: its
    flag, down while the lineage was flagged, would stay down, and its first meld of v1 would skip the gate although
    `register_index` retired v1's verdicts there. Today that flag stays up and the gate runs.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:349-417
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:517-549
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:307-374
  - src/melder/aether/spellbook/spellbook.py:3826-3920
  - src/melder/aether/spellbook/spellbook.py:1690-1757
  - src/melder/aether/spellbook/spellbook.py:3155-3214
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:410-437
  IMPACT: Unfixed, the exclusion would let a borrower skip the gate after a notch back; invariant 5 must not depend
    on the validity changing.
  NEXT: Amend the patch docs with the re-publication, then the tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T21:20:19Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Refinement inside Option A (same flag, same reader): `register_index` notes whether its capability write
    changed the flag (`update_flags` returns that) and whether the lineage was already `gated`; when both hold it
    calls a new `SpellSystemState._republish_validity()` after the gate, still under the registry lock, which
    publishes the current validity to RiskManager the way `set_validity` does (read under the state lock, published
    outside it, contained). `on_structural_validity_change` then refreshes every conduit holding the lineage, the
    reactivated borrower included. No extra event when the flag did not change or when the gate event fired. Patch
    docs amended (architecture invariant 5 and interface deltas, the state-model and RiskManager component patches,
    the code description); tests gain a unit case for the re-publication and a component notch-back with an
    index-linked borrower.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:511-535
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/architecture_patch.md:1-109
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_spell_state_model.md:1-89
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_risk_manager.md:1-70
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/code_description_patch_risk_distillation.md:1-79
  IMPACT: A notch back to a resolvable version counts the lineage again in every conduit, whether or not its gate
    was already closed.
  NEXT: Test B (RiskManager on a real registry) and the stub update, then the four melder_1 files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T21:32:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The four call-site keywords reach five test doubles in melder_0's lanes that mirror the old signature or lack
    `Spell.resolvable`: two `register_index` lambdas in test_spellbook.py, the fake registry and `build_spell` of both
    transfer unit files, and the fake registries of two component spellbook files. With only the keywords applied, 45
    unit tests failed (AttributeError 'resolvable' on a SimpleNamespace spell, TypeError on the lambdas). A real Spell
    always carries `resolvable` (default True) and the real registry takes the keyword, so the doubles are corrected
    to mirror that (keyword accepted, `resolvable=True` on the built spell; the bind lambda records the value and
    the test asserts bind passes it). No production fallback is added. These five test files join the handoff.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook.py:2435-2435
  - tests/unit/melder/spellbook/test_spellbook.py:2503-2503
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:122-135
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1069-1108
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:120-133
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:1020-1059
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:555-566
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:110-121
  - context_compass/artifacts/meld_contract_scan_20261015/runs/callsites_gil0.txt:1-2
  IMPACT: The handoff covers the four keyword lines plus the doubles in these five test files; apply_call_sites.py
    applies both.
  NEXT: Component tests D on the scratch tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T21:32:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Scratch tree (synced to the real tree at 0.2.8246 first; Python 3.14.7t), red then green. Unit test A (28:
    flags, `register_index`, the re-publication, `index_has_flag`) and B (11: the distillation on a real registry)
    were red - A 28 failed; B 11 failed, then 8 failed and 3 passed after the state-model change (the 3 are the
    unchanged-behaviour guards). The stub C gained `index_has_flag`. The four melder_1 files are written by
    apply_state_model.py and apply_risk_manager.py, the call sites and doubles by apply_call_sites.py (exact-text
    edits that refuse a missing anchor, to be re-run on the real tree). Green: A 28, risk_manager 32, dev_ops unit
    742 with the GIL off and on; with the call sites, GIL off: unit_aether 4460 (4421 + 39 new), unit_sb 2560,
    comp_sb 819, comp_aether 1377 + 1 xfailed, int_aether 785 + 5 xfailed, int_conduit 335 - the baseline counts.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/red_gil0.txt:1-5
  - context_compass/artifacts/meld_contract_scan_20261015/runs/green_gil0.txt:1-3
  - context_compass/artifacts/meld_contract_scan_20261015/runs/green_gil1.txt:1-1
  - context_compass/artifacts/meld_contract_scan_20261015/runs/callsites_gil0.txt:3-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/baseline_gil0.txt:1-6
  - context_compass/artifacts/meld_contract_scan_20261015/apply_state_model.py:1-460
  - context_compass/artifacts/meld_contract_scan_20261015/apply_risk_manager.py:1-252
  IMPACT: The change holds on the unit, component and integration chunks run so far; the rest of the tree and GIL on
    are still to run.
  NEXT: Component tests D (worlds, notch both ways, transfer, borrower notch-back, races), then every chunk GIL 0 and 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T21:41:50Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Correction to the FACT at lines 511-535: the first notch back does not find the lineage gated. The notch
    commit runs phases 1-4 for a member never compiled, and Phase 4 clears the gate, so after v1 -> def the lineage
    is `valid` and the notch back publishes its gate event. The `gated` registration comes with a repeat notch: the
    commit skips a member compiled before, so v1 -> def -> v1 -> (melds) -> def leaves the lineage `gated` and the
    next notch back publishes nothing. Traced on the scratch tree: with `_republish_validity` disabled, after that
    sequence the index-linked borrower's flag stays down and its meld of v1 skips the gate (v1's verdict stays
    `unknown`); with it, the flag rises and the meld revalidates (`valid`). The re-publication stands, the patch docs
    now say "repeat notch", and the component test runs that sequence (it fails with the re-publication disabled).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_borrower_notch_back_gil0.txt:1-24
  - context_compass/artifacts/meld_contract_scan_20261015/probe_borrower_notch_back.py:1-114
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:511-535
  IMPACT: The gap is real for agents notching back and forth between versions, which is the intended use; the
    earlier note named the wrong trigger.
  NEXT: Record the component results and the mutation checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T21:41:50Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Component tests D (9, real wiring): automatic and dynamic worlds with a Protocol definition (flag down, no
    gate entry on the next melds, the definition still refused), an override consumer of a definition, a notch to a
    definition and back, a borrower after a repeat notch, a transfer and a rolled-back transfer, a contract
    consumer that follows its lender's notch beside a definition, and four melder threads racing 40 notches. Green
    with the GIL off and on. Mutation checks: re-publication disabled -> 3 unit and 1 component fail; exclusion
    disabled -> 7 unit and 7 component fail; call-site keywords removed -> 7 component fail. In the race, a binding
    lookup that lands inside a notch's swap raises KeyError "No spell found" (meld's lookups take no Book lock, and
    `_apply_notch` takes the outgoing version off the maps before it puts the incoming one on) - pre-existing and
    unrelated to this change; the test accepts it and the refused definition, and fails on anything else.
  EVIDENCE:
  - tests/component/melder/aether/dev_ops/spell_system_states/test_non_resolvable_validation_flag_component.py:1-453
  - context_compass/artifacts/meld_contract_scan_20261015/runs/component_gil0.txt:1-3
  - context_compass/artifacts/meld_contract_scan_20261015/runs/component_gil1.txt:1-2
  - context_compass/artifacts/meld_contract_scan_20261015/runs/mutation_gil0.txt:1-7
  - src/melder/aether/conduit/meld/meld.py:1960-2009
  - src/melder/aether/spellbook/spellbook.py:3826-3920
  IMPACT: Each part of the change has a test that fails without it; the race shows no definition build and no
    error class the change could cause.
  NEXT: Every chunk with the GIL off and on on the scratch tree, then the probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T22:12:54Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Every chunk of the test tree passes on the scratch tree with the GIL off and on (23 chunks, the same counts
    in both modes): unit_aether 4460, unit_sb 2560, unit_cryst 607, unit_mr 277, unit_util 826 + 2 skipped + 7
    xfailed, unit_build 116, unit_top 146, unit_llm 28, unit_arch 18, unit_gh 491; comp_aether 1386 + 1 xfailed,
    comp_sb 819, comp_cryst 110, comp_mr 40, comp_util 41 + 23 skipped; int_aether 785 + 5 xfailed, int_conduit 335,
    int_sb 619 + 2 skipped + 2 xpassed, int_mt 54, int_cryst 276 + 3 xfailed, int_mr 67, int_live 1 + 1 xfailed;
    experimentation 250 + 4 skipped. Against the six chunks run on the pristine copy the only change is the new
    tests (unit_aether 4421 -> 4460, comp_aether 1377 -> 1386). unit_gh's first GIL-off run failed 2 tests because
    the scratch copy lacked `.readthedocs.yaml` and `codecov.yml` (a copy omission); with both copied in it passed.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/full_gil0.txt:1-24
  - context_compass/artifacts/meld_contract_scan_20261015/runs/full_gil1.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/baseline_gil0.txt:1-6
  - context_compass/artifacts/meld_contract_scan_20261015/run_chunks.sh:1-36
  IMPACT: The change, its four call sites and the corrected doubles break nothing in the tree in either mode.
  NEXT: The before/after probe.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-15T22:12:54Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Before/after probe, GIL off (before: a copy of the real tree's src at 0.2.8246; after: the scratch tree;
    caching off, nothing written to either tree). Warm meld: an automatic Book with one Protocol definition 15.09 ->
    0.24 us, dynamic 16.38 -> 0.71 us, a consumer fed a class definition by override 15.48 -> 0.53 us (gate entries
    1 -> 0 per meld, Book flag up -> down); without a definition unchanged (0.26 -> 0.26, 0.84 -> 0.70 us); the
    borrower SpellContract consumer unchanged (2154 -> 2158 us: its flag is held by the borrowed provider, a
    resolvable lineage - items (2)-(3)). Conjure of 200 spells with 0, 20 and 100 definitions: medians within 2 ms
    either way over 2 x 9 runs a side, register_conduit unchanged, one refresh instead of one per visible spell (401
    instead of 601-701). The regression: with only definitions risky, `_has_unexcluded_risk` probes every key
    through `index_has_flag` (two locks, about 0.5 us a key), so a refresh costs 1.4 -> 2.6 us with no definition,
    1.7 -> 11.2 us with 20, 1.8 -> 43.8 us with 100 and 1.8 -> 521 us (max 1.6 ms) with 1000; in a dynamic Book with
    1000 definitions a late bind plus its first meld (4 refreshes) goes 6.9 -> 9.2 ms, while warm melds go 12.5 ->
    0.70 us.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/probe_before_after.py:1-374
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_before_gil0.txt:1-13
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_after_gil0.txt:1-13
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_conjure_gil0.txt:1-12
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_d1000_gil0.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/apply_risk_manager.py:134-206
  IMPACT: The meld path improves as designed and nothing else moves except the flag refresh, whose cost now grows
    with the number of definitions - an event-path regression for bind- and notch-heavy Books with many of them.
  NEXT: Make the exclusion check independent of per-key Python work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T22:12:54Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Refinement inside Option A (the same flag and reader; RiskManager keeps no state of its own): the registry
    publishes the ids of the lineages whose state carries `SpellState.non_resolvable` as a frozenset
    (`SpellSystemStates.non_resolvable_index_ids`), replaced whole under the registry lock wherever that membership
    can change - `register_index` reconciles the lineage with its flag right after `_record_selected_capability`,
    before the gate publishes; `unregister_index` drops it; cleanup leaves an empty set as a tombstone for readers
    racing it - and read without a lock. `RiskManager._has_unexcluded_risk` becomes one subset test of the risky
    keys against it (a `spell:` key or a removed lineage is never in it, as before), so a refresh takes no registry
    lock and does no Python work per key. `index_has_flag` stays as the per-lineage read. Tests: A gains the set
    (each registration path, unregister, cleanup, replacement rather than mutation, agreement with the flag); the
    stub C answers it; the component helper asserts the set agrees with the flag at every check; patch docs and the
    apply scripts follow, and the four melder_1 files on the scratch tree are regenerated from pristine copies.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_d1000_gil0.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/apply_risk_manager.py:134-206
  - context_compass/artifacts/meld_contract_scan_20261015/apply_state_model.py:319-363
  - context_compass/artifacts/meld_contract_scan_20261015/apply_state_model.py:366-456
  IMPACT: A refresh's cost no longer grows with Python work per definition; the meld path, the flag's meaning and
    every existing test expectation stay as they are.
  NEXT: Apply it on the scratch tree, rerun A-D and every chunk with the GIL off and on, then the probe both modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T22:34:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The published set, built and validated on the scratch tree. The old apply scripts were first shown to
    reproduce the four scratch files byte for byte from pristine copies; the amended scripts then regenerated them,
    and all three scripts' --check find every anchor in the real tree. Tests: A 34 (6 new: every registration path,
    unregister, replacement rather than mutation, agreement with the flag, the cleanup tombstone), B 11, C 21 (the
    stub answers the set), D 9 (each flag check asserts the set agrees) - green with the GIL off and on. Mutations:
    register_index not publishing the membership fails 6 A, 7 B and 7 D; unregister_index keeping it fails 2 A and
    1 B. Every chunk is green in both modes with the earlier counts plus the 6 new tests (unit_aether 4466). Probe
    after the refinement: a warm meld with a definition 14.4-16.4 -> 0.24-0.77 us in both modes, plain worlds and
    conjure unchanged within noise; a refresh costs 2.3 / 3.8 / 6-8 / 36 us with 0 / 20 / 100 / 1000 definitions
    (1.3-2.7 us before the change; 521 us at 1000 with the per-key probe); a late bind plus its first meld at 1000
    definitions 7437 -> 7360 us (GIL off) and 7613 -> 6951 us (GIL on); interleaved, 5 x 60 late binds a side:
    medians 2499 -> 2313 us with no definition and 3590 -> 2886 us with 100.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/refine_gil0.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/runs/refine_gil1.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/runs/mutation_published_set_gil0.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/full_refined_gil0.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/full_refined_gil1.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_after_refined_gil0.txt:1-13
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_after_refined_gil1.txt:1-13
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_before_gil1.txt:1-13
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_d1000_refined.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_late_bind_interleaved_gil0.txt:1-20
  - context_compass/artifacts/meld_contract_scan_20261015/refine_published_set_2026_10_15.py:1-343
  - context_compass/artifacts/meld_contract_scan_20261015/patch_docs_published_set_2026_10_15.py:1-201
  IMPACT: Rule 1 is built, tested and measured; the event path no longer pays per definition, and the meld path
    keeps the win. What remains is the landing.
  NEXT: Make the apply scripts keep each file's line endings (next Note), then ask the owner for the handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T22:34:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The apply helper rewrites every file it touches with LF line endings (`read_text` translates CRLF and
    `write_bytes` writes LF). Of the ten files the landing edits, git stores three test files with CRLF in the
    index - test_spellbook_component_spell_crafter.py, test_transfer_of_ownership.py and
    test_transfer_of_ownership_contracts.py (i/crlf w/crlf) - so an LF rewrite would commit as a whole-file change;
    the others are stored LF (risk_manager.py, spell_state.py, spell_system_state.py and test_risk_manager.py are
    CRLF only in the owner's working copy, three files are mixed, spellbook.py and transfer_of_ownership.py are LF).
    The scratch tree's copies are LF; Python reads both alike, so no run is affected.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/eol_listing_2026_10_15.txt:1-12
  - context_compass/artifacts/meld_contract_scan_20261015/apply_lib.py:1-42
  IMPACT: Landed as is, the three CRLF test files (melder_0's lanes) would carry a whole-file diff. The helper
    must write CRLF back to a file that was CRLF throughout; mixed and LF files stay LF (their index form).
  NEXT: Fix apply_lib.apply, regenerate the scratch files with it, confirm the content is unchanged.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-15T23:17:16Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner direction (chat 2026-10-15): "just talk to melder_0 in the mailbox". For this exchange the owner
    overrides the codex_mcp transport rule (mailbox messaging retired since 2026-10-02): melder_1 sends M1-18 to
    melder_0 in mailbox_board.md `## Messages` with one alert line (melder_1's last ID was M1-17, 2026-09-26). It
    asks melder_0 (1) to release the four call-site lines and the five test doubles to melder_1 for one landing
    window, or to apply apply_call_sites.py itself; (2) whether melder_1 may add its release-note section, take the
    next notch and rebuild last; (3) when src_architecture, src_components, their indexes and the graph are free
    after S7. melder_0 also works under codex_mcp and skips the mailbox, so the owner points it at M1-18.
  EVIDENCE:
  - context_compass/special_instructions/codex_mcp.md:13-24
  - context_compass/system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_registration_call_sites.md:1-84
  IMPACT: The landing waits on melder_0's answer (or the owner's).
  NEXT: When the owner says melder_0 replied, read its M0 message, copy it into these Notes and consume it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-16T00:47:20Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: melder_0 answered M1-18 yes to all three (relayed by the owner in chat 2026-10-16 and recorded in its
    epic's DECISION note; no M0-175 was posted in the mailbox). (1) melder_1 makes the four `register_index` keyword
    edits (spellbook.py bind and notch, transfer_of_ownership.py flip and rollback) and the five test doubles itself,
    as one landing; melder_0 leaves those files untouched until melder_1 reports that it has landed. (2) melder_1
    adds its own `##` section to release_docs/next_version_release.md, takes the next notch from `__version__` at
    landing (0.2.8246 at 00:46Z) and runs the rebuild last. (3) src_architecture, src_components, the tests docs,
    their indexes and the graph are free now (S7's edits are finished). The owner confirmed this reply is the one to
    act on. The handoff hold is cleared; items (2)-(3) of the design request (the contract check) stay with the owner.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:1387-1407
  - context_compass/mailbox_board.md:1028-1038
  IMPACT: melder_1 holds the landing window on the four src files and five test files until its M1-19 notice; the
    landing is one change set with one notch.
  NEXT: Re-run the three apply scripts' --check against the real tree, then apply them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T01:05:44Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rule 1 is landed in the real tree and validated there. Before the edit the real tree's src matched the
    pristine 0.2.8246 copy except six generated system-document assets from melder_0's S7 rebuild; the three apply
    scripts' --check found every anchor and the scripts applied the eleven edits (the four melder_1 src files, the
    four keywords in spellbook.py and transfer_of_ownership.py, the doubles in five test files; CRLF kept for the six
    files whose working copy is CRLF throughout); tests A, B and D were copied in as new files and the stub C
    written CRLF. After it, src and tests equal the validated scratch tree file for file (CR ignored), except those
    six assets and test-written .meldercache files. A fresh copy of the landed tree (context_compass and docs linked
    read-only, nothing run in the real tree) passes all 23 chunks with the GIL off and on at the scratch counts
    (unit_aether 4466, comp_aether 1386 + 1 xfailed, int_aether 785 + 5 xfailed, int_cryst 276 + 3 xfailed, ...).
    Probe on that copy, GIL off: a warm meld with a definition 15.09 -> 0.26 us (automatic), 16.38 -> 0.73 us
    (dynamic), 15.48 -> 0.41 us (override consumer); plain worlds 0.25 / 0.79 us; the borrower contract consumer
    2206 us (unchanged; items (2)-(3)); conjure of 200 spells 32.5-36.0 ms with 401 refreshes; a late bind plus its
    first meld 2269-2934 us.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/landed_gil0.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/landed_gil1.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_landed_gil0.txt:1-13
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_before_after_before_gil0.txt:1-13
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:324-466
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:500-620
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:703-738
  IMPACT: The code and its tests are in place and green in both modes; docs, the release note, the notch, closure
    and the rebuild remain.
  NEXT: Amend src_architecture and src_components (and their indexes), the tests docs and the graph descriptors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T01:50:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The four system documents carry rule 1, read back from disk after their index rebuilds. src_architecture:
    step 7 of the meld-time gate, the first operational invariant (the flag and its writer, the published set, the
    subset test, the repeat-notch re-publication, the lock order, the measurements), the first failure mode, six
    code-map extents remeasured (spellbook.py 7615, transfer_of_ownership.py 2155, spell_system_states.py 1886,
    spell_system_state.py 806, spell_state.py 93, risk_manager.py 751) and the notch-seam and settle citations into
    spellbook.py remeasured. src_components: the DevOps Control Plane, the SpellSystemStates Registry, Meld Runtime
    Gating, flow step 6, two new code-map entries and the touched blocks' seam and Conduit citations remeasured; its
    handoff names spellbook.py:7233-7244, :286, :5713-5719, :5273-5285, :6546 and transfer_of_ownership.py:953,
    :1444 as stale from earlier lanes and not re-audited. tests_components: the DevOps Control Plane Unit Cluster
    (A, B), D in the Aether Component Cluster, five C1 entries, 250 core paths; tests_architecture: the recount (836
    test modules). Every line that left the four documents is an edit (a remeasured number, extent, stamp, date or
    count), the four indexes are current, and there is no portability or absolute-path hit.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:839-845
  - context_compass/system_docs/src_architecture.md:1034-1062
  - context_compass/system_docs/src_architecture.md:1938-1947
  - context_compass/system_docs/src_architecture.md:4052-4061
  - context_compass/system_docs/src_components.md:4719-4829
  - context_compass/system_docs/src_components.md:6986-7039
  - context_compass/system_docs/src_components.md:11033-11043
  - context_compass/system_docs/tests_components.md:931-952
  - context_compass/system_docs/tests_architecture.md:884-887
  - context_compass/artifacts/meld_contract_scan_20261015/runs/docs_preservation_2026_10_16.txt:1-76
  - context_compass/artifacts/meld_contract_scan_20261015/runs/docs_index_check_2026_10_16.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/land_docs_src_architecture_2026_10_16.py:1-237
  - context_compass/artifacts/meld_contract_scan_20261015/land_docs_src_components_2026_10_16.py:1-214
  - context_compass/artifacts/meld_contract_scan_20261015/land_docs_tests_2026_10_16.py:1-171
  - context_compass/artifacts/meld_contract_scan_20261015/remap_citations_2026_10_16.py:1-72
  IMPACT: The packaged documents describe the landed behaviour; the stale citations named above are earlier lanes'
    drift, recorded here and left for a citation pass (outside this change).
  NEXT: The graph descriptors and the assembled graph.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-16T01:50:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The graph carries rule 1. Authored fields were written, then tightened after re-reading each node's source
    against them: SpellState (owns_state `new_index` for the stale `new_lineage`, plus `non_resolvable`; the
    capability flag), SpellSystemState (`update_flags`; `_republish_validity` on the registry's request),
    SpellSystemStates (the capability write, the re-publication, the published set; owns
    `_non_resolvable_index_ids`), RiskManager (the subset test; `register_conduit` refreshes once) and Spellbook (bind
    and notch pass the capability). Those five nodes were stamped against the pristine 0.2.8246 source, so each was
    re-read against the diff from that copy and accepted (`graph_walker --accept --apply`). TransferOfOwnership stays
    SEMANTICS_STALE: its stamp predates melder_0's 0.2.8246 change, so verifying it is not this lane's. Re-extracted
    with --strict (591 descriptors, nothing skipped; it also restores the extractor's indent=1, which the walker's
    accept writes as indent=2): census 9 unsemantic, 221 stale, 0 orphaned; walker 1074 AUTHORED (+5), 144 stale.
    Assembled 591 sections, 1227 nodes, 1415 edges, 28063 lines; --check and the index proof pass; no portability
    hit. The sections that changed are the six source files, `__version__.py` and six generated system-document
    assets whose bytes moved since the previous assembly.
  EVIDENCE:
  - context_compass/system_docs/src_graph_index.md:101-106
  - context_compass/system_docs/src_graph_index.md:144-144
  - context_compass/system_docs/src_graph_index.md:362-362
  - context_compass/artifacts/meld_contract_scan_20261015/graph_semantics_2026_10_16.py:1-76
  - context_compass/artifacts/meld_contract_scan_20261015/graph_semantics_refine_2026_10_16.py:1-56
  - context_compass/artifacts/meld_contract_scan_20261015/runs/graph_accept_2026_10_16.txt:1-7
  - context_compass/artifacts/meld_contract_scan_20261015/runs/extract_graph_2026_10_16.txt:1-46
  - context_compass/artifacts/meld_contract_scan_20261015/runs/graph_walker_report_2026_10_16.txt:1-110
  - context_compass/artifacts/meld_contract_scan_20261015/runs/assemble_graph_2026_10_16.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/runs/assemble_graph_check_2026_10_16.txt:1-4
  IMPACT: The wiring slices for the six files describe the landed code, and the five nodes read as verified against it;
    the graph's stale count fell by the five this lane had made stale.
  NEXT: The release note, the notch notice and the patch lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-16T01:50:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Release note, notch notice and records. release_docs/next_version_release.md reads "# Melder 0.2.8247" and
    gains "A non-resolvable definition no longer sends every meld of its Book through validation" (the symptom, a
    Protocol example, the measurements, the notch-back behaviour, what stays the same), a packaging bullet and the
    rebuild line for 0.2.8247. Its example was run as written on the pristine 0.2.8246 code and on the landed code: a
    warm override meld 12.9 -> 0.39 us with the GIL off and 13.2 -> 0.40 us with it on, and a meld of the definition
    is refused with the same MeldExecutionError on both (the landed copy's version file predates the notch). The
    attention board carries "Notch notice (melder_1, 2026-10-16)". The five patch docs moved (mv -n) to
    system_docs/patches/completed/meld_state_gate_2026_10_15/; the artifact board clears them as one
    promote_to_documentation row, and the folder row names the landing's evidence.
  EVIDENCE:
  - release_docs/next_version_release.md:1-3
  - release_docs/next_version_release.md:487-527
  - release_docs/next_version_release.md:585-589
  - context_compass/artifacts/meld_contract_scan_20261015/release_note_2026_10_16.py:1-83
  - context_compass/artifacts/meld_contract_scan_20261015/release_example_2026_10_16.py:1-56
  - context_compass/artifacts/meld_contract_scan_20261015/runs/release_example_2026_10_16.txt:1-12
  - context_compass/attention_board.md:302-305
  - context_compass/artifact_board.md:96-96
  - context_compass/artifact_board.md:103-103
  IMPACT: Users read the change, with a checked example; other lanes see the notch to build above; the patch lane is
    closed out as promoted.
  NEXT: Score the four system documents with the quality rubric, from disk.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-16T01:50:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rubric scores, from disk after the index rebuilds (self-scored; no independent reviewer): src_architecture 83
    (B) - fidelity 4, contract 5, depth 4, addressability 4, join 4, mirror 4; src_components 83 (B) - 4, 5, 4, 4,
    4, 4; tests_architecture 83 (B) - 4, 5, 4, 4, 4, 4; tests_components 77 (B) - 4, 4, 3, 4, 4, 4. Basis:
    src_architecture was re-read whole in this session; for the other three the sections this landing edited were
    re-read from disk and the measurable half rerun (one H1 each, no duplicate indexed name, no unclosed heading,
    contracts complete and in order, no portability or absolute-path hit, 160 / 36 / 234 / 250 C1 records complete
    with every extent equal to its file today, every Key Files path resolving), while their unchanged remainder
    keeps melder_0's S7 judgment of 2026-10-15T23:39:29Z. Why not 5: fidelity - uncited older bullets
    (src_architecture.md:2229, :2241, :2250) and a meld-flow diagram that still names "Phase12 Compiled
    Executors" in both src documents; depth - one-clause lines remain (src_architecture.md:2229) and four
    src_components entries have thin fields (PhaseScheduler at :5641); addressability - container H2s that hold only
    sub-headings (src_architecture.md:724, :3556; src_components.md:193); join - 154 of 160, all 36, 228 of 234 and
    245 of 250 verified_at stamps are carried forward although every extent measured equal today; mirror - each
    pair shares its contract and adds different non-contract sections. tests_components depth 3: its Mock Fixture
    Corpus entry has five thin fields.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rubric_checks_2026_10_16.txt:1-52
  - context_compass/artifacts/meld_contract_scan_20261015/rubric_checks_2026_10_16.py:1-173
  - context_compass/system_docs/src_architecture.md:2229-2229
  - context_compass/system_docs/src_architecture.md:2241-2241
  - context_compass/system_docs/src_architecture.md:2250-2251
  - context_compass/system_docs/src_architecture.md:3831-3848
  - context_compass/system_docs/src_components.md:5641-5714
  - context_compass/system_docs/src_components.md:10767-10784
  - context_compass/system_docs/tests_components.md:629-718
  - context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:498-545
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:43-54
  IMPACT: All four documents are band B and usable as inputs; their weak points predate this landing, which
    changed none of the scores melder_0 recorded at S7.
  NEXT: Move the ticket to review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-16T01:50:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The ticket moves from in_progress to blocked (board row `review`, mode handoff). Rule 1 is landed as 0.2.8247
    with its tests green in both GIL modes, the four system documents and their indexes, the graph, the release
    note, the notch notice, the archived patch lane and the rubric scores, and the rebuild runs last. The EXIT_GATE's
    remaining conditions are the owner's: accepting rule 1 (reserved), and answering items (2)-(3) of the design
    request - rule 2's "no signature scan when the spell's state needs no contract check", which waits on him (a
    borrower SpellContract consumer still costs about 2 ms a meld). After the rebuild, M1-19 tells melder_0 that
    the landing is done and its files are released. Recorded and left alone (outside this change): the notch-swap
    KeyError race (Note 2026-10-15T21:41:50Z), the stale citations named in src_components' handoff, and
    TransferOfOwnership's unverified graph node.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:860-993
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:31-33
  - context_compass/attention_board.md:198-198
  IMPACT: Rule 1 is done from melder_1's side; what remains is the owner's.
  NEXT: Rebuild the assets and the LLM bundles with both checks, then send M1-19.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T01:58:17Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last, from the repository root on Python 3.14.7t. The first asset run wrote the agent-documentation
    and bind-guard manifests and the system-documents index, then stopped with PermissionError: the
    system-documents builder deletes its three payload modules before writing them again, and the connected folder
    refused deletes. The owner granted delete permission on melder_private for this session (used for those three
    files only), and the full run wrote all three assets at v0.2.8247 (468 agent-documentation entries, 628
    bind-guard entries, 4 system documents); --check printed only OK lines. The LLM bundles, built with
    --include-untracked because the three new test files are untracked, rewrote src (583 files), tests (1117) and
    other (404) and the manifest; --check printed only OK lines.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rebuild_assets_2026_10_16_first_attempt.txt:1-29
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rebuild_assets_2026_10_16.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rebuild_assets_check_2026_10_16.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/llm_support_2026_10_16.txt:1-9
  - context_compass/artifacts/meld_contract_scan_20261015/runs/llm_support_check_2026_10_16.txt:1-8
  IMPACT: The change set is complete and consistent: code, tests, docs, graph, release note, notch and generated
    assets agree at 0.2.8247.
  NEXT: Send M1-19 to melder_0 (the landing is done; its files are released); then the owner's acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T09:30:40Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner direction on rule 2 (chat 2026-10-16), settling items (2)-(3) of the design request in principle:
    "so question if spellcontract exists and its satisfied we're good but if notch happens it should be rechecked
    isn't that the story we should land on?", then, asked mark-only or also dropping stored consumer objects:
    "marking makes sense thats the point we want to make sure we can still resolve it because the init might change
    for a notched spell". The story: a satisfied SpellContract needs no per-meld check; a notch (and any other change
    of the borrower's active contracted copy: notch back, park, reactivate, add, remove) marks the key's consumers
    `gated` + `contract_unvalidated`, so their next meld re-validates the contract and rebuilds their plan against the
    version now active - its new `__init__` and dependencies included - and fails with the error a first meld would
    give when that version cannot be resolved for them. Mark only: objects already built keep their provider. Not yet
    confirmed by the owner: rule 1's acceptance and closure, and rule 2 as its own successor ticket.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:181-212
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:213-232
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:233-257
  IMPACT: Rule 2's design is settled in principle; building it needs patch docs, the owner's approval of them and a
    handoff of spellbook.py from melder_0 for the borrower-side marking (its contracted-map mutators).
  NEXT: The owner confirms rule 1's acceptance and closure and a successor ticket for rule 2 on this story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T09:36:46Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner acceptance (chat 2026-10-16): asked "shall I mark rule 1 accepted and close its ticket, then open rule
    2 as its own ticket on this story? It would start with the design docs for your approval, with no source changes
    until you approve them", he answered "yees sure thats good". Rule 1 is accepted as landed in 0.2.8247 and this
    ticket closes. Rule 2 - the EXIT_GATE's contract-check conditions, settled in principle in the Note of
    2026-10-16T09:30:40Z - moves to the successor
    TASK-2026-10-16-recheck_contract_consumers_when_provider_changes, which starts with patch docs for his approval and
    changes no source before it. The artifact folder is rowed under the successor as its evidence; the patch lane
    stays archived.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:1054-1076
  - context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:39-41
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md
  IMPACT: Rule 1 is done and accepted; nothing of it remains open.
  NEXT: None here; rule 2 continues in the successor.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Closed (done, 2026-10-16T09:36:46Z): the owner accepted rule 1 as landed in 0.2.8247. `register_index` writes
`SpellState.non_resolvable` from the selected version's `Spell.resolvable` (bind, notch, the transfer flip and its
rollback pass it) and mirrors it in the registry's published `non_resolvable_index_ids`; RiskManager's Book flag
leaves flagged lineages out with one subset test, and `register_index` re-publishes the validity when the flag
changes on a lineage already gated. Tests A (34), B (11), C (the stub) and D (9) are in the tree; all 23 chunks
passed with the GIL off and on; a warm meld in a Book with a definition 15.1 -> 0.26 us (automatic), 16.4 -> 0.73
us (dynamic). The four system docs and their indexes, the graph, the release note, the notch notice, the archived
patch lane (system_docs/patches/completed/meld_state_gate_2026_10_15/), rubric 83 / 83 / 83 / 77 (B), and the
assets and LLM bundles rebuilt for 0.2.8247 with both checks OK. melder_0 has its files back (M1-19).
Rule 2 continues in TASK-2026-10-16-recheck_contract_consumers_when_provider_changes: a satisfied contract needs no
per-meld check, a notch marks the key's consumers for a recheck (mark only) so a notched version's new `__init__`
is re-resolved; patch docs first, for the owner's approval; spellbook.py (melder_0's) needs a handoff for the build.
Recorded, not fixed (outside this change): the notch-swap KeyError race, the stale spellbook.py and
transfer_of_ownership.py citations named in src_components' handoff, TransferOfOwnership's unverified graph node.
Not run: coverage.

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
