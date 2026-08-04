# Epic: Flatten lesser-conduit ownership to a root star (genealogy becomes data)

## CLOSED — WILL NOT DO (owner decision, 2026-07-02; agent optimizer_0)
- Completed: 2026-07-02T19:04:29Z (closed unimplemented; archived as a decision record)
- Summary: REJECTED by owner. The parent<->child lesser link's one load-bearing job is
  the teardown cascade (parent cleanup -> child cleanup; deterministic child-before-parent
  disposal of pooled/nested lessers). Flattening to a root star deletes the ~17% per-cycle
  ward link/detach cost but forces equivalent replacement bookkeeping to preserve that
  teardown determinism -> net-neutral-to-worse, not a real win. Not worth the structural
  churn.
- Census result (optimizer_0, evidence-backed; kept so this is not re-proposed): the
  parent<->child tree (`_parent_conduit` / `_lesser_conduits`) is read by ONLY three things:
  (1) teardown cascade (conduit_ward.py `_detach_for_pool` :336 / `cleanup_all_lesser_conduits`;
  conduit.py:435,4331), (2) `upgrade_to_normal` "no children" invariant (conduit_ward.py:512),
  (3) Nexus/Rift observability -- `parent_conduit_id` + `lineage_depth` in the conduit
  descriptor (frame_descriptor_manager.py:360-436) and `_get_lesser_conduit` walks used by the
  Rift command/viewer surfaces (command_system.py:203, static_frame_viewer.py:311). It carries
  NO resolution semantics (`unique_per_conduit_lineage` resolves off the ROOT:
  conduit.py:1628-1629, "lineage-root store") and NO contract semantics (peer contracts live in
  `_contracts` / `_initiated_index` / `_received_index` and explicitly exclude lessers,
  conduit_ward.py:1165). Both real consumers (cascade + visualizer) already work today, so
  flattening gains nothing structural.

## Metadata
- Epic ID: EPIC-2026-07-02-flatten-lesser-conduit-ownership-to-root-star
- Status: closed (will-not-do 2026-07-02)
- Owner: cowork
- Agent Name: unassigned (authored by melder_0 from user decision 2026-07-02)
- Priority: p1 (post-subsystems; pairs with the PGO/optimization pass)
- Created: 2026-07-02T02:10:00Z
- Updated: 2026-07-02T02:10:00Z

## Problem / Opportunity
The lesser-conduit tree is structural theater: lessers already reuse the ROOT's pool, the
root Creations, and the root-lineage resolution id, so lineage semantics were always
root-anchored. Intermediate parent<->child links carry no semantic payload but create
reference cycles that tax conduit resets (~17% measured improvement expected from the cycle
drop) and feed the gauntlet churn/GC tail (see refactor_0's GC probe lane). The tree still
EMERGES semantically at consumption time (nested scope usage forms it for free); enforcing
it structurally pays twice for one truth.

## Decision (user, 2026-07-02)
- Ownership goes FLAT: root -> all lesser conduits (star), no intermediate structural links.
- Genealogy becomes DATA: retain `parent_id` as a recorded diagnostic fact / semantic view
  only; nothing structural or lifecycle-bearing hangs off it.
- Linking is reserved for roots.
- Rename: `unique_per_conduit_lineage` -> `unique_per_root` (the name catching up to what
  the semantics always were). Lineage->root vocabulary sweep across code/docs/tests
  (pattern: general_0's terminology-rename lane).
- AMENDMENT (user, 2026-07-02): add a SpellbookConfiguration item that allows the tree to
  FORM as an opt-in (e.g. `conduit_genealogy_tree_enabled`, default False = flat star).
  Purpose: observability tooling - graph maps showing where objects are going. When enabled,
  tree formation exists for the diagnostic/visualization surface; it must remain
  non-load-bearing (ownership, cleanup, and existence semantics stay root-star in BOTH
  modes). Design note for Story 2: since genealogy is retained as parent_id data anyway,
  evaluate whether graph maps can be served from the data alone and the flag only needs to
  materialize richer tree indexes/structures where data-derived views fall short - the flag
  buys visualization, never semantics.

## Ticket Contract
- ENTRY_GATE (the two checks, impact-engine style - MUST come back clean before any edit):
  1. Enumerate every reader of `_parent_conduit` / ward lineage maps beyond cleanup and
     `upgrade_to_normal` (contract visibility, hooks, spellspace nesting walking the chain =
     blast radius; upgrade itself simplifies: "no children" becomes trivially true flat).
  2. Teardown ordering: the tree gave child-before-parent disposal for free; the star must
     preserve equivalent determinism via reverse-registration order.
- EXECUTION_BOUNDARY: conduit.py, conduit_ward.py (lineage maps/conversion), creations
  root wiring, existence enum + resolution_style_matrix, terminology sweep surfaces.
- DEPENDENCIES: after crystallizer/MR subsystem build-out; coordinate with refactor_0's
  GC-tail lane (shared motivation) and mediator lanes (transaction scope keys name conduits).
- EXIT_GATE: flat ownership landed; rename sweep 0 old tokens; full 3.14t tree green
  (user-run); reset benchmark confirms the cycle-drop win; docs synced
  (src_architecture/src_components lineage sections).
- FAILURE_ESCALATION: CONFLICT note if check 1 finds a load-bearing parent-chain reader.

## Goals / Non-goals
- Goals: cheaper conduit resets (target ~17%), fewer GC cycles (churn-tail relief), simpler
  upgrade_to_normal, honest naming (unique_per_root).
- Non-goals: changing root linking/contract semantics; changing consumption-side scope
  nesting behavior (the semantic tree must still emerge identically for callers).

## Stories (suggested breakdown)
- [ ] Story 1: Entry-gate investigation (parent-chain reader census + teardown-order design).
- [ ] Story 2: Flatten ownership structure + genealogy-as-data (`parent_id` fact retention).
- [ ] Story 3: `unique_per_conduit_lineage` -> `unique_per_root` rename sweep (code/docs/tests).
- [ ] Story 4: Validation: user-run 3.14t tree + reset/gauntlet benchmark comparison
      (before/after cycle counts and churn tails).

## Applicable Anti-Patterns
- [ ] No implementation before the entry-gate census is evidence-complete.
- [ ] No rename outside the declared sweep boundary.
- [ ] No closure without user-run 3.14t green + benchmark MEASURE note.

## Noting Behavior
- Epic notes: program direction, cross-story tradeoffs, tranche order.

## Notes
- DATETIME: 2026-07-02T02:10:00Z
  TYPE: DECISION
  CLAIM: User decision captured at end of 2026-07-01 session (with melder_0): the DI tree
    pattern between lesser conduits is a semantic illusion - conduits use pools and
    root-anchored state, consumption forms the tree naturally, so structural tree links are
    deleted in favor of a root star with genealogy retained as data. Expected ~17% reset
    improvement from cycle drop (user estimate, to be verified by Story 4); connects to the
    gauntlet churn/GC tail evidence (melder max 24.4ms, 2026-07-01 gauntlet run).
  EVIDENCE:
  - codex/context_compass/system_docs/src_architecture.md:791-799
  - codex/context_compass/tickets/tasks/2026-06-20_gauntlet_gc_tail_probe_task.md:1-1
  IMPACT: Cheaper resets, GC-tail relief, simpler upgrade path, honest existence naming.
  NEXT: Story 1 entry-gate census when a lane picks this up post-subsystems.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
User-decided flattening of lesser-conduit ownership: root star + genealogy-as-data +
unique_per_root rename. Entry gate = parent-chain reader census + teardown-order design.
Scheduled after the crystallizer/MR subsystem build-out; pairs with the PGO pass.
