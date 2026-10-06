

# Task: Investigate what MelderOps' Melder setup does when Melder's roots are already configured

## Metadata
- Task ID: TASK-2026-09-29-investigate-melderops-root-configuration-collisions
- Story: none; standalone investigation (advice for MelderOps, read-only there)
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-29T22:47:30Z
- Updated: 2026-09-30T15:40:12Z
- Completed: 2026-09-30T15:40:12Z
- Closure Basis: owner turn-in in chat (2026-09-30) of every finished lane: "yeah turn in the [lanes] you
  finished please, go ahead".
- Summary: A per-root answer, from source reads on both sides and three probe batches in fresh processes, to
  what MelderOps' Melder setup did when a host had already configured Melder's roots: an explicit MelderOps
  policy over an active host root crashed prepare() with an AttributeError; configured-but-inactive host roots
  were silently replaced or switched back on; a host's staged Aether policy was mutated; a late per-frame
  spell-id policy was reported but not in force; a refused dynamic conjure settled its frame. The owner picked
  every fix: F1-F6 (MelderOps) and M1-M4 (Melder), each in its own task. Read-only here; no source changed.

## Objective
Owner question (chat, 2026-09-29): MelderOps configures Melder through `spectrum/melder_setup` and
`configurations/melder_configuration.py`. When Melder already exists - Aether booted, a Crystallizer, MutationResearch
and Nexus configured or active, frames and Books present - and a MelderOps user asks for Crystallizer, MR or Nexus
to be a specific way, what happens: a collision, a silent keep, a replace, an error? Read both sides and answer
with evidence, per root.

## Ticket Contract
- ENTRY_GATE: owner question in chat; this board row.
- EXECUTION_BOUNDARY: read-only. priv_commandops: src/melder_ops/command_center/spectrum/melder_setup/*,
  configurations/melder_configuration.py and the Spectrum code that calls them. melder_private: the configure /
  activate / freeze paths of Aether, Crystallizer, MutationResearch and Nexus, and their configuration objects.
  Probes only in VM scratch against the 0.2.8208 VM env. No source edits in either repository.
- DEPENDENCIES: none.
- EXIT_GATE: per root (Aether, Crystallizer, MutationResearch, Nexus): what MelderOps requests, when, and what Melder
  does when that root is already configured, activated or in use - each with source evidence and, where
  behaviour is not obvious from reading, a probe; the answer delivered to the owner.
- FAILURE_ESCALATION: DECISION_REQUEST if a fix is warranted (it would be a separate ticket in the owning repo).

## Scope Boundaries
- In scope: the question above.
- Out of scope: fixing anything; MelderOps edits (priv_commandops agents own that code).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner question in chat (2026-09-29).
- from_state: in_progress
- to_state: review
- transition_reason: Per-root answer delivered with evidence (2026-09-29T23:13:17Z); awaiting owner acceptance
  and fix selection.
- from_state: review
- to_state: done
- transition_reason: (2026-09-30T15:40:12Z) owner turn-in in chat, after the fixes it picked (F1-F6, M1-M4)
  landed in their own tasks.

## Steps / Checklist
- [x] Read MelderConfiguration and the melder_setup package; record what MelderOps asks of each root and when.
- [x] Read each root's configure / activate / freeze path in Melder; record the already-configured behaviour.
- [x] Probe the non-obvious cases in VM scratch.
- [x] Answer the owner.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A per-root answer with evidence; probe scripts and results under artifacts/melderops_root_configuration_20260929/.

## Validation
- Not run.

## Risks / Rollback Notes
- Read-only; nothing to roll back.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No behaviour claim from a search hit or a document; read the code.
- [x] No closure without acceptance confirmation and board-sync completion.

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
  - artifacts/melderops_root_configuration_20260929/
- DISPOSITION: retain_as_reference
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
- DATETIME: 2026-09-29T22:48:47Z
  TYPE: FACT
  CLAIM: MelderOps side, read in full. MelderConfiguration holds one record per process root (aether, crystallizer,
    mutation_research, nexus): an optional supplied native configuration (`with_native_configuration`, adopted
    unless it is the one already installed) and a feature request (`with_feature`; ai_enabled=True requests all
    three optional roots, default False requests none; Aether is always requested). prepare() only builds and
    validates. Spectrum's runtime then re-assesses against the live host (`_preflight`) and, per requested root
    (`_activate_root`): if Melder reports the root ACTIVE it is reused untouched (Aether: only a resolver is set on
    its policy when that policy is still mutable); otherwise it calls `configure(policy)` on the root, releases
    custody, activates the policy object, then activates the root. The default assessment decides per root: not
    requested -> skip (host untouched, a supplied policy is kept but never installed); active with a supplied
    policy whose values differ from the installed one -> ValueError "Active <root> policy conflicts with the
    supplied configuration" (equal values -> reuse); installed but inactive and nothing supplied -> reuse the host's
    policy and activate it; otherwise build (the supplied policy, or fresh defaults). Values are compared with
    `get_configuration_dictionary()`. Frames: a settled frame must already be dynamic (+AI/Rift when requested),
    else ValueError; an unsettled one gets MelderOps' posture through `configure_aether_frame`.
  EVIDENCE:
  - priv_commandops:src/melder_ops/command_center/spectrum/configurations/melder_configuration.py:457-535
  - priv_commandops:src/melder_ops/command_center/spectrum/configurations/melder_configuration.py:860-1024
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/strategies.py:140-209
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/strategies.py:237-291
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/inspection.py:91-214
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/runtime.py:286-316
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/runtime.py:636-842
  IMPACT: What happens on a collision is decided by (a) MelderOps' active-or-not test and (b) what each Melder
    root does when `configure` is called while it is configured-but-inactive, or when frames already exist.
  NEXT: Read Aether.configure/activate and the first-frame collapse, then the three optional roots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T22:51:33Z
  TYPE: FACT
  CLAIM: Melder side, read. All four roots are process singletons with one installed policy each. Aether.configure
    replaces the installed policy outright, even after frames exist; the spell-id regime
    (`_process_wide_unique_spell_ids`) is read only when the FIRST frame is born, where a missing policy is filled
    with frozen defaults (not activated), and never again - so a policy installed after the first frame changes
    what `Aether.configuration` reports but not the regime; activate applies only its logger half (and first
    clears the utility system's resolver and default logger). Crystallizer.configure and MutationResearch.configure
    refuse while active ("Cannot reconfigure ... while it is active") and replace outright while inactive;
    deactivate keeps the policy. Crystallizer.activate records only its own policy twin and the Aether root twin -
    no world walk, so Books and conduits that already exist are not in the record. MutationResearch.activate
    hydrates an untouched registry from the crystallizer's recorded composition. Nexus.configure has NO active
    guard: it swaps the policy of a live Nexus, unfrozen, and Nexus reads policy live at each Rift validation.
    Nexus defaults allow Rift targets only in frame "default", one target frame.
  EVIDENCE:
  - src/melder/aether/aether.py:972-1054
  - src/melder/aether/aether.py:2474-2531
  - src/melder/aether/aether.py:2440-2472
  - src/melder/aether/aether_configuration.py:805-835
  - src/melder/crystallizer/crystallizer.py:568-695
  - src/melder/crystallizer/crystallizer.py:804-822
  - src/melder/mutation_research/mutation_research.py:607-706
  - src/melder/mutation_research/mutation_research.py:761-785
  - src/melder/nexus/nexus.py:803-910
  - src/melder/nexus/nexus.py:3208-3242
  - src/melder/nexus/configuration/nexus_configuration.py:307-352
  IMPACT: Combined with MelderOps' rule (reuse when active, conflict error when an active policy differs, otherwise
    configure-and-activate), the collisions are in the configured-but-inactive states and in Aether after the first
    frame; Nexus has a Melder-side gap of its own.
  NEXT: Probe each case in fresh VM processes (Melder calls, then MelderRuntime.initialize end to end).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T23:02:25Z
  TYPE: MEASURE
  CLAIM: Probes, one scenario per fresh VM process (PYTHON_GIL=0, 0.2.8208 VM env with an editable MelderOps copy).
    Melder level: Crystallizer and MutationResearch refuse configure while active and replace the installed policy
    silently while inactive; deactivate keeps the policy (its object still reports activated) and a bare re-activate
    turns recording back on. Nexus.configure on an ACTIVE Nexus is accepted: the live policy becomes the unfrozen
    replacement (allowed targets ('default',) -> ('melderops',)). Aether: a per-frame spell-id policy installed after
    the host's first frame is reported (process_wide_unique_spell_ids False) but not in force - after a conjure in
    frame tenant_a the same class bound in tenant_b is refused "Spell ID collision"; installed before the first frame
    it is accepted. MelderOps end to end: a host crystallizer configured but inactive is displaced by MelderOps' policy
    (max_persistence_crystals 7 -> 3, activated); one the host deactivated is switched back on by the AI preset with
    the host's policy. The designed conflict error is not reached: prepare() with a supplied crystallizer policy while
    the host's is active raises AttributeError 'CrystallizerConfiguration' object has no attribute
    'get_configuration_dictionary'. A host Book that bound under a mutable configuration cannot conjure dynamic once
    the crystallizer is active ("finalized BEFORE the first bind"); an automatic retry in the same process got the same
    refusal - UNKNOWN whether the failed dynamic attempt settled the frame first. Late activation records nothing
    already built (automatic: frame/book/conduit/spell counts 0; later binds are recorded); the dynamic early control
    records frame, book and conduit (1/1/1). Caveats: results4.txt was run before this session's re-onboarding
    (disclosed); bind-only probes do not discriminate - the same sealed regime accepted a bind-only second-frame bind
    (results2.txt:1-6) and refused it after a conjure (results3.txt:9-14) - so results2.txt:1-9 and the end-to-end
    Aether line results4.txt:20-22 prove nothing yet.
  EVIDENCE:
  - artifacts/melderops_root_configuration_20260929/results.txt:24-37
  - artifacts/melderops_root_configuration_20260929/results2.txt:1-16
  - artifacts/melderops_root_configuration_20260929/results3.txt:1-14
  - artifacts/melderops_root_configuration_20260929/results4.txt:1-23
  - artifacts/melderops_root_configuration_20260929/probe_roots.py:60-159
  - artifacts/melderops_root_configuration_20260929/probe_roots.py:162-239
  - artifacts/melderops_root_configuration_20260929/probe_roots.py:242-328
  IMPACT: The configured-but-inactive states collide silently (MelderOps' policy wins, or MelderOps re-arms what the
    host switched off); an active host crystallizer plus a supplied MelderOps policy crashes prepare() instead of
    raising the conflict error; a MelderOps Aether policy after the host's first frame is reported but not in force;
    turning recording on under a host that bound with a mutable configuration breaks the host's dynamic conjure.
  NEXT: Read the assessment's value comparison against the root configuration classes, then re-run the end-to-end
    Aether probe with a conjure and the automatic conjure on its own.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T23:07:47Z
  TYPE: FACT
  CLAIM: Root cause of the AttributeError, and the code moved under this investigation. DefaultAssessmentStrategy,
    for any of the four roots that the host has ACTIVATED, compares a supplied policy with the installed one through
    MelderHostInspector.values(), which calls get_configuration_dictionary() on every family except frame posture.
    That method belongs to MelderOps' own BaseConfiguration; no class in src/melder defines it (all six native
    configuration classes derive only from Cleanable). values(provided) is evaluated before any comparison, so a
    supplied Aether, Crystallizer, MutationResearch or Nexus policy for an active root raises AttributeError at
    prepare() whether or not its values match - the designed ValueError and the equal-values reuse are both
    unreachable. Frames compare through describe_posture() and Books by identity, so they are unaffected. Separately,
    priv_commandops carries uncommitted edits made at 22:59:32Z (inspection.py, runtime.py: the inspector moved to the
    0.2.8208 public read surface - find_frame, frozen, shared_spellbook_configuration, Conduit.spellbook). They do not
    change the decision logic (strategies.py untouched since 13:47:07Z; values() unchanged), but my earlier probes ran
    a VM copy taken before them, and the earlier FACT's inspection.py/runtime.py ranges refer to the pre-edit files.
  EVIDENCE:
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/strategies.py:140-182
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/inspection.py:162-183
  - priv_commandops:src/melder_ops/command_center/spectrum/configurations/base_configuration.py:341-351
  - artifacts/melderops_root_configuration_20260929/absence_get_configuration_dictionary.txt:1-24
  - artifacts/melderops_root_configuration_20260929/priv_commandops_worktree_capture.txt:1-18
  IMPACT: The "active host root plus explicit MelderOps policy" collision never produces a readable refusal; it
    crashes setup with an AttributeError naming a method the user never called. It is a MelderOps defect, fixable in
    values() by comparing through a native surface both families share (e.g. get_property over the policy's keys,
    or describe_*), which is a priv_commandops ticket, not this one.
  NEXT: Re-sync the VM MelderOps copy to the current tree, then probe the equal-values case, the end-to-end Aether
    regime with a conjure, and the automatic conjure on its own.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T23:11:12Z
  TYPE: MEASURE
  CLAIM: Second probe batch, VM MelderOps copy re-synced to the current tree (melder_setup identical by diff -rq).
    (1) An equal-valued supplied crystallizer policy over an active crystallizer and a supplied Nexus policy over an
    active Nexus both raise AttributeError at prepare() - equality never matters. (2) Discriminating end to end: with
    the host's first frame already born, MelderOps installs its per-frame Aether policy (reported
    process_wide_unique_spell_ids False) and the same class bound into a second frame after a conjure is still
    refused "Spell ID collision"; with no host frame first, MelderOps' own frame is born under the policy and the
    same bind is accepted. (3) The crystallizer guard is dynamic-only: an automatic conjure of a Book bound under a
    mutable configuration is accepted after recording is turned on. But a REFUSED dynamic conjure leaves the frame
    settled: frozen False/automatic before, frozen True/dynamic after - so every later conjure in that frame
    inherits dynamic and is refused too. (4) End to end: a host Book bound under a mutable configuration, then
    MelderOps' AI preset (crystallizer activated), then the host's dynamic conjure - refused.
  EVIDENCE:
  - artifacts/melderops_root_configuration_20260929/results5.txt:1-27
  - artifacts/melderops_root_configuration_20260929/probe_roots.py:331-460
  IMPACT: Aether: an explicit MelderOps Aether policy is only honoured for the spell-id regime when MelderOps boots
    before the host's first frame. Crystallizer: turning recording on under a host whose Books bound before their
    configuration was finalized breaks those Books' dynamic conjure, and the refusal itself flips the frame to
    dynamic (a Melder-side side effect independent of MelderOps).
  NEXT: Run the second half: logger policy injection and clearing, the default-frame posture cases, Nexus default
    targets under the AI preset, and late activation over a dynamic world.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T23:12:08Z
  TYPE: MEASURE
  CLAIM: Third probe batch. (1) A host that installed its own Aether policy without activating it: MelderOps (nothing
    supplied) reuses that same object, injects MelderOps' InitHelpers.resolve_channel_logger as its channel resolver,
    turns automatic channel-logger activation on (it was off), then freezes and activates it - the host's policy is
    mutated in place. The reused policy counts as not supplied, so the "generated default only" enablement in
    _configure_logging applies to a host policy. (2) A default logger the host registered on the hosted utility
    system (an Internal-labelled method) is cleared: Aether.activate clears resolver and default logger before
    applying MelderOps' policy (has_default_logger True -> False). (3) Pointing MelderOps at the host's frame: a
    settled automatic frame is refused cleanly ("Frame 'default' is not dynamic"); an unsettled one is switched to
    dynamic (automatic -> dynamic, still unfrozen) before the host conjures, and the host's plain conjure then runs
    in a dynamic frame. (4) The AI preset with no Nexus policy leaves Nexus active with allowed targets ('default',)
    while MelderOps' only frame is 'melderops'. (5) Recording turned on over an existing dynamic world records none
    of it (frame/book/conduit/spell counts 0); a later bind adds a spell index and crystal without frame, book or
    conduit twins.
  EVIDENCE:
  - artifacts/melderops_root_configuration_20260929/results6.txt:1-24
  - artifacts/melderops_root_configuration_20260929/probe_roots.py:461-579
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/runtime.py:693-769
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/models.py:155-181
  - priv_commandops:src/melder_ops/command_center/spectrum/melder_setup/builder.py:266-272
  - src/melder/aether/aether.py:1005-1073
  IMPACT: Aether's logging half is where MelderOps changes a host silently even with nothing supplied. The Nexus
    default is latent (MelderOps creates no Rift - no create_rift in its src) but would refuse any Rift aimed at
    MelderOps' frame. A MelderOps AI preset started after the host's world exists yields a record that cannot
    restore that world.
  NEXT: Deliver the per-root answer to the owner with the fix options; keep the lane open for acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T23:13:17Z
  TYPE: DECISION_REQUEST
  CLAIM: The per-root answer is delivered to the owner in chat (this ticket's notes carry the evidence). Fixes are
    warranted and belong to separate tickets; the owner picks which. MelderOps (priv_commandops, its agents): F1
    compare policies without get_configuration_dictionary (per-family native properties); F2 do not mutate a reused
    host Aether policy (resolver injection, activation flag); F3 treat a configured-but-inactive host root like an
    active one (conflict check instead of silent replacement) and never re-activate a root the host deactivated
    unless asked; F4 refuse a supplied Aether policy whose spell-id regime differs from the one a born frame
    already sealed; F5 give the AI preset a Nexus policy that admits MelderOps' own frames; F6 refuse or warn on the
    AI preset once host frames exist, since late recording cannot restore them. Melder (this repo, owner approval,
    one notch each): M1 Aether.configure/activate refuses, or reports honestly, a regime change after the first
    frame; M2 Nexus.configure refuses while active, like Crystallizer and MutationResearch; M3 a refused dynamic
    conjure must not leave its frame settled dynamic; M4 optional: a common native read of policy values for hosts.
  EVIDENCE: tickets/tasks/completed/2026-09-29_investigate_melderops_root_configuration_collisions_task.md:118-301
  IMPACT: Without F1 every explicit policy over an active host root crashes MelderOps setup; F2/F3 decide whether
    MelderOps may change a host's configuration without saying so.
  NEXT: Owner accepts the answer and chooses which fix tickets to open (and in which repository).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T15:40:12Z
  TYPE: DECISION
  CLAIM: The owner picked every fix (chat, 2026-09-29: "implement all the fixes") and turned this lane in
    (chat, 2026-09-30, every finished lane). M1-M4 landed in Melder at 0.2.8209-0.2.8212 under the guard task;
    F1-F6 landed in MelderOps under its honour-host-roots task, on Melder 0.2.8212 with the floor raised. Both
    close in the same pass. These notes stay the record of the collisions as they stood on Melder 0.2.8208.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-29_guard_melder_roots_for_host_collisions_task.md:28-41
  - priv_commandops:context_compass/tickets/tasks/completed/2026-09-29_honour_host_melder_roots_task_completed.md
  IMPACT: Nothing in this investigation stays open; the one gap it surfaced beyond F1-F6 and M1-M4 (the Aether
    record carries no spell-id regime) is recorded in the guard task.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Closed 2026-09-30T15:40:12Z on the owner's turn-in. Both sides were read and three probe batches recorded; the
per-root answer went to the owner in chat and the notes carry its evidence. The owner picked every fix: M1-M4
landed in Melder (0.2.8209-0.2.8212) under the guard task, F1-F6 in MelderOps under its honour-host-roots
task; both are closed with this one. Read-only in both repositories. Guard task:
tickets/tasks/completed/2026-09-29_guard_melder_roots_for_host_collisions_task.md

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
