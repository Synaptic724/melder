# Task: Inventory Aether Conduit Methods For Command Surface
- Completed: 2026-04-13T12:00:15Z
- Summary: Closed the source-backed Aether/Conduit ownership inventory after the conduit-discovery implementation lane landed on top of it.

## Metadata
- Task ID: TASK-2026-04-12-inventory-aether-conduit-methods-for-command-surface
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-12T15:00:15Z
- Updated: 2026-04-12T15:00:15Z

## Objective
Read `Aether` and inventory the existing conduit/root-conduit discovery and
creation methods so we can make one final proposal for which methods should be
owned by `Aether`, which should stay on `Conduit`, and which should be
facaded through the command systems.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a source-backed inventory of
  existing `Aether` methods before any more command-surface additions.
- EXECUTION_BOUNDARY: `Aether` source inspection, focused note capture, and a
  proposal only. No runtime code changes in this task.
- DEPENDENCIES:
  - src/melder/aether/aether.py
  - src/melder/aether/conduit/conduit.py
  - codex/context_compass/attention_board.md
- EXIT_GATE: one source-backed inventory of current `Aether` methods exists,
  along with a final proposal for what to add to `Aether` vs keep on
  `Conduit`.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current `Aether`
  topology/ownership is too inconsistent to propose a clean façade split
  without broader runtime refactoring.

## Scope Boundaries
- In scope:
  - current `Aether` conduit/root-conduit methods
  - current `Conduit` lesser-conduit methods
  - final proposal for ownership/facade split
- Out of scope:
  - code changes
  - command-system implementation
  - viewer/static/capability semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user redirected to a source-backed inventory/proposal
  pass before any more command-surface implementation.

## Steps / Checklist
- [ ] Read `aether.py` in bounded chunks and inventory current conduit/root-conduit methods.
- [ ] Cross-check the relevant existing `Conduit` methods for lesser-conduit operations.
- [ ] Propose the final ownership/facade split.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- source-backed `Aether` method inventory
- final command-surface ownership/facade proposal

## Files / Paths Impacted
- src/melder/aether/aether.py
- src/melder/aether/conduit/conduit.py
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content src/melder/aether/aether.py`

## Risks / Rollback Notes
- Risk: we misclassify existing ownership and propose more façade duplication.
  Rollback: keep the proposal source-backed and limited to current `Aether` and
  `Conduit` responsibilities.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T15:00:15Z
  TYPE: PLAN
  CLAIM: The user wants a source-backed final proposal before any more command
    surface additions: inventory the current `Aether` methods for conduit/root
    discovery and creation, compare them to current `Conduit` lower/runtime
    methods, and then decide what belongs in `Aether` and what should just be
    facaded through the command systems.
  EVIDENCE:
  - user_direction: "go read the aether and find all hte methods that exist there and then lets make a final propositoin to add things"
  IMPACT: This is an investigation/proposal-only slice, not another runtime
    implementation pass.
  NEXT: read `aether.py` in bounded chunks and inventory the existing
    conduit/root-related methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T15:08:00Z
  TYPE: FACT
  CLAIM: `Aether` already owns most of the root-conduit and frame-topology
    runtime seams we need for the next command surface, but they are private
    and inconsistent. Existing `Aether` conduit/root-related methods are:
    - cloud/lookup:
      `_register_conduit_cloud`, `_unregister_conduit_cloud`,
      `_get_conduit_cloud`, `_get_conduit_by_name`, `_get_conduit_by_id`
    - root conduit registry:
      `_add_conduit`, `_remove_conduit`
    - cluster topology:
      `_create_cluster`, `_remove_cluster`, `_get_cluster`,
      `_add_conduit_to_cluster`, `_remove_conduit_from_cluster`,
      `_get_conduits_in_cluster`, `_get_clusters_for_conduit`
    - spell ownership lookup:
      `_get_conduit_by_spell_id`, `_check_for_spell`
    What `Aether` does not currently expose is any coherent public/root-level
    list/find/create surface for command-facing use.
  EVIDENCE:
  - src/melder/aether/aether.py:603-822
  - src/melder/aether/aether.py:864-1148
  - src/melder/aether/aether.py:1160-1399
  IMPACT: The next command-surface additions should mostly be public/runtime
    facades over existing `Aether` ownership, not brand-new logic in command
    systems.
  NEXT: cross-check what should stay on `Conduit` so the final proposal does
    not move lesser-conduit or spell-owned operations up into `Aether`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T15:08:00Z
  TYPE: FACT
  CLAIM: `Conduit` should keep lineage-local and spell-local operations.
    Relevant existing lower/runtime methods are:
    - lesser/topology local to a conduit:
      `create_lesser_conduit(...)`
    - spell/local runtime:
      `find_spell_id(...)`, `find_contracted_spell(...)`,
      `get_spell_by_id(...)`, `get_spell_by_index_id(...)`,
      `meld(...)`, `meld_existing_spell(...)`,
      `has_live_creation(...)`, `describe_live_creation_status(...)`
    So the clean split is:
    - `Aether` owns frame/root-conduit discovery and root-conduit creation
    - `Conduit` owns lesser-conduit creation and spell operations
    - command systems facade those lower owners
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1548-1787
  - src/melder/aether/conduit/conduit.py:2440-2628
  IMPACT: We should not move lesser-conduit creation or spell retrieval/meld
    up into `Aether`; that would repeat the same layering mistake in a new
    place.
  NEXT: present the final ownership/facade proposal to the user before any
    new command-surface implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T15:16:00Z
  TYPE: FACT
  CLAIM: The user explicitly wants a full reread of `conduit.py` before the
    ownership proposal is trusted. The current partial `Aether` inventory is
    not enough; we need the full conduit surface in view so we can identify
    overlap, not just obvious root/spell seams.
  EVIDENCE:
  - user_direction: "so go read the conduit and the aether and make sure we're not overlapping shit"
  - user_direction: "so go read ALL of the conduit"
  IMPACT: The current task expands from selective source inventory to a full
    bounded reread of `conduit.py` plus the relevant `aether.py` surface before
    any final proposal.
  NEXT: reread `aether.py` and all of `conduit.py` in sequential bounded
    `Get-Content` chunks, then restate the ownership split from complete source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T15:28:40Z
  TYPE: FACT
  CLAIM: After rereading all of `conduit.py`, the real overlap is narrower than
    it first looked. `Conduit` already has Aether-backed convenience methods
    for:
    - `get_conduit_cloud`
    - `get_conduit_by_id`
    - `get_conduit_by_name`
    - `get_conduit_by_spell_id`
    - cluster actions (`create_cluster`, `delete_cluster`, `join_cluster`,
      `leave_cluster`, `list_clusters`, `refresh_cluster_shares`)
    while `Aether` owns the actual root/frame-wide state and cloud/cluster
    registries. The clean split is:
    - conduit discovery mesh lives on `ConduitCloud`
    - root/frame topology ownership stays in `Aether`
    - lesser lineage and spell/runtime actions stay on `Conduit`
    We should not add cloud-style discovery methods to `Conduit`, because that
    provides little value in automatic mode and duplicates the mesh surface.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:879-956
  - src/melder/aether/conduit/conduit.py:1548-1787
  - src/melder/aether/conduit/conduit.py:2292-2440
  - src/melder/aether/conduit/conduit.py:3070-3156
  - src/melder/aether/aether.py:603-822
  - src/melder/aether/aether.py:864-1148
  IMPACT: The next implementation should target `ConduitCloud` for discovery
    methods, backed by `Aether` ownership, and leave `Conduit` focused on
    lesser-conduit, spell, meld, and lifecycle/runtime behavior.
  NEXT: give the user the final method proposal: what to add to `ConduitCloud`,
    what stays in `Aether`, and what should not be added to `Conduit` or `Rift`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is a bounded inventory/proposal pass over `Aether` and `Conduit`
ownership for the next command-surface additions.
