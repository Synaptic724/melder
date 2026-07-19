# Task: investigate conduit cluster registry decoupling
- Completed: 2026-05-20T09:32:43Z
- Summary: Closed after proving the current `ConduitCluster` dependency on `ConduitCloud` was only method-time conduit-id lookup plus frame-name forwarding, which defined the later narrow implementation cut.

## Metadata
- Task ID: TASK-2026-05-20-investigate-conduit-cluster-registry-decoupling
- Story: none
- Epic: EPIC-2026-05-18-recompose-conduit-aether-spellbook-runtime-ownership
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-20T08:59:54Z
- Updated: 2026-05-20T09:32:43Z

## Objective
Investigate whether `ConduitCluster` can stop depending on `ConduitCloud` by
accepting narrower registry-backed lookup surfaces instead, and identify the
exact cloud methods or data it currently relies on.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for investigation only and wants the
  old completed refactor lanes turned in first.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit_cluster.py`
  - `src/melder/aether/aetheric_frame/conduit_cloud.py`
  - directly implicated frame or caller seams only if needed to explain the
    current contract
- DEPENDENCIES:
  - no production edits in this lane
  - no speculative redesign beyond the current lookup/registry boundary
- EXIT_GATE:
  - the exact current `ConduitCloud` dependency surface inside
    `ConduitCluster` is explicit
  - the minimal registry-backed method set needed to remove the back-reference
    is explicit
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current cluster behavior
  depends on broader cloud-owned semantics than simple conduit lookup.

## Scope Boundaries
- In scope:
  - constructor dependency surface
  - current method calls from `ConduitCluster` into `ConduitCloud`
  - whether passing `_conduits` or a narrower lookup surface is sufficient
- Out of scope:
  - implementing the decoupling
  - broader cluster ownership redesign
  - unrelated conduit/cloud cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a bounded investigation of
  `ConduitCluster` decoupling and wants the old refactor hopper cleaned up.

## Steps / Checklist
- [ ] read `conduit_cluster.py` in bounded chunks
- [ ] read the adjacent `conduit_cloud.py` lookup surface it depends on
- [ ] map the exact current dependency calls and data assumptions
- [ ] state the minimal duplicate/lookup surface needed to remove the cloud
      back-reference
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- evidence-backed dependency map for `ConduitCluster -> ConduitCloud`
- recommendation for the minimal lookup/registry surface needed to decouple it

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-20_investigate_conduit_cluster_registry_decoupling_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "conduit_cloud|_registry|get_conduit|find_conduit|cluster" src/melder/aether/conduit/conduit_cluster.py src/melder/aether/aetheric_frame/conduit_cloud.py`

## Risks / Rollback Notes
- Low risk because this lane is investigation only.

## Applicable Anti-Patterns
- [ ] No implementation disguised as investigation.
- [ ] No speculative ownership claims without file evidence.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-20T08:59:54Z
  TYPE: PLAN
  CLAIM: The user hypothesis is narrow and testable: `ConduitCluster` may only
    need a registry-backed lookup surface from `ConduitCloud`, not the full
    cloud object. This lane exists to prove the exact current call surface
    before any refactor is proposed.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next read pass should stay on `conduit_cluster.py` and
    `conduit_cloud.py` until the exact dependency surface is explicit.
  NEXT: read `conduit_cluster.py`, then map every `ConduitCloud` method or
    data dependency it currently uses.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T09:06:12Z
  TYPE: FACT
  CLAIM: `ConduitCluster` does not currently store a `ConduitCloud`
    back-reference at all. The cloud only constructs clusters with
    `ConduitCluster(cluster_name)`, then passes itself into five cluster
    methods as a live lookup helper. Inside those methods, the actual cloud
    dependency surface is tiny: repeated `get_conduit_by_id(...)` calls plus
    reads of `frame_name`. The cluster does not call any cloud name-lookup,
    cluster-registry, or registration helpers.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:300-317
  - src/melder/aether/conduit/conduit_cluster.py:172-250
  - src/melder/aether/conduit/conduit_cluster.py:271-350
  - src/melder/aether/conduit/conduit_cluster.py:353-410
  - src/melder/aether/aetheric_frame/conduit_cloud.py:129-205
  IMPACT: The decoupling question is not "remove a stored backref"; it is
    whether the five method-time `cloud` parameters can be replaced by a
    narrower lookup/frame surface.
  NEXT: isolate those five methods and decide whether `_conduits` plus a frame
    name string is sufficient, or whether any hidden behavior still requires
    cloud-owned logic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:09:31Z
  TYPE: FACT
  CLAIM: The remaining cloud dependency is even narrower than it first looked.
    The cluster only needs conduit lookup by id. The current `cloud.frame_name`
    reads are not a separate cloud-only behavior; one cluster path
    (`share_to_borrower`) already uses `owner._aetheric_frame_name` directly,
    and the other `cloud.frame_name` call sites are forwarding that same frame
    name into borrower contract methods. So the minimal semantic surface is:
    1) resolve peer conduits by id from the frame-owned root registry, and
    2) preserve the current missing-id skip behavior. A raw `_conduits` dict is
    close, but it is not identical to the current contract by itself because
    `ConduitCloud` also serializes borrowed-store reads with its own `RLock`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_cluster.py:198-208
  - src/melder/aether/conduit/conduit_cluster.py:240-250
  - src/melder/aether/conduit/conduit_cluster.py:290-345
  - src/melder/aether/conduit/conduit_cluster.py:378-404
  - src/melder/aether/conduit/conduit_cluster.py:444-455
  - src/melder/aether/aetheric_frame/conduit_cloud.py:26-32
  - src/melder/aether/aetheric_frame/conduit_cloud.py:62-65
  - src/melder/aether/aetheric_frame/conduit_cloud.py:179-205
  IMPACT: If we decouple `ConduitCluster`, the truthful narrow replacement is
    not "duplicate all of ConduitCloud." It is one id-lookup helper over the
    frame-owned conduit registry plus an explicit decision about how to retain
    the current lock/skip semantics.
  NEXT: summarize the exact candidate replacement shapes and call out the
    smallest clean one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T09:11:46Z
  TYPE: FACT
  CLAIM: The interface blast radius is small. `IConduitCluster` only hardcodes
    `IConduitCloud` on three public methods: `handle_join(...)`,
    `handle_leave(...)`, and `refresh_member_shares(...)`. The more explicit
    share-management helpers (`share_to_borrower(...)`,
    `remove_shared_from_borrower(...)`) are already cloud-free and operate on
    real conduit objects.
  EVIDENCE:
  - src/melder\utilities\interfaces\iconduitcluster.py:60-87
  - src/melder\aether\conduit\conduit_cluster.py:172-294
  - src/melder\aether\conduit\conduit_cluster.py:412-458
  IMPACT: The eventual decoupling cut is localized: constructor/init plus a few
    method signatures and their cloud-driven call sites, not a broad interface
    redesign.
  NEXT: give the user the minimal truthful replacement surface and the one real
    caution about lock semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Fresh investigation-only lane for the `ConduitCluster` dependency on
`ConduitCloud`.
