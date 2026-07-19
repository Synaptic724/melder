# Task: Design Frame Surface HLD
- Completed: 2026-04-09T21:59:36Z
- Summary: Retired the frameinfolink HLD task at user direction and left it as completed historical context.


## Metadata
- Task ID: TASK-2026-04-03-design-frame-surface-hld
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-03T09:17:21Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Define the high-level design for the frame-scoped surface objects, including
the canonical `FrameLink` layer, per-frame `FrameView`, the multi-view
`FrameViewer`, and the Nexus-owned link-update boundary, including how they
relate to profiles, commands, ACL application, binding, churn, and
conduit-based real object acquisition.

## Ticket Contract
- ENTRY_GATE: the new frame-surface epic is active and the user confirmed the
  corrected ownership model where Nexus owns and updates links.
- EXECUTION_BOUNDARY: HLD only; no runtime code changes.
- DEPENDENCIES:
  - tickets/epics/2026-04-03_frameinfolink_surface_query_and_binding_epic.md
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - tickets/artifacts/aethericrift_riftspace_interaction_architecture.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md
- EXIT_GATE: one concrete HLD exists for the canonical frame link layer, the
  per-frame view layer, the viewer layer that can consume multiple views, the
  Nexus-owned update boundary, and the query/display/bind boundary.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if multiple equally plausible
  object-responsibility splits remain unresolved.

## Scope Boundaries
- In scope:
  - canonical link responsibilities
  - `FrameView` responsibilities
  - `FrameViewer` responsibilities
  - Nexus-owned update responsibilities
  - multi-frame viewer consumption
  - churn/versioning tradeoff
  - command/query surface
  - bind boundary
- Out of scope:
  - eventstream implementation
  - ACL implementation details
  - runtime coding

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: this is the first concrete HLD slice under the new
  frame-surface epic.

## Steps / Checklist
- [ ] Define the Nexus-side canonical holding zone and what objects it owns.
- [ ] Define what canonical `FrameLink` owns.
- [ ] Define what `FrameView` owns.
- [ ] Define what `FrameViewer` owns.
- [ ] Define what Nexus-owned link-update machinery owns.
- [ ] Define how one viewer consumes multiple frame views.
- [ ] Define the weakref versus deterministic-update tradeoff.
- [ ] Define the command/query surface and the bind boundary.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- HLD for the frame-scoped surface objects
- recommended implementation sequence

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md`

## Risks / Rollback Notes
- Risk: object names are chosen before responsibilities are stable.
  Rollback: keep the HLD focused on responsibilities first and treat names as
  provisional if needed.

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
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-03T09:17:21Z
  TYPE: PLAN
  CLAIM: The immediate design target is the frame-scoped surface model, not the
    whole Rift runtime. The first draft assumed:
    `FrameInfoLink` as the node/entry object,
    `FrameView` as the frame-scoped collection,
    `FrameViewer` as the query interface,
    and `FrameInfoLinkSystem` as the strategy host/projection system.
  EVIDENCE:
  - user_instruction: "FrameLink hosts all the objects under a specific frame"
  - user_instruction: "FrameView owns the FrameLink objects"
  - user_instruction: "the FrameViewer gives you the ability to find information on things"
  - user_instruction: "FrameLinkSystem will host the strategies we use to view them"
  IMPACT: The next step is to lock responsibilities and the bind boundary
    before implementation thinking goes any further.
  NEXT: propose the responsibility split and the query/display/bind contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T09:29:18Z
  TYPE: FACT
  CLAIM: Two important corrections emerged immediately. First, `FrameLink` may
    be the wrong name because in the broader system vocabulary a "link"
    already implies a connection/relationship rather than a projected node or
    view-entry. Second, the canonical live surface probably belongs on `Nexus`,
    not `Rift`: Nexus already owns the authoritative registry/policy layer for
    frames and Rifts, so if frames/spells/conduits change underneath, Nexus is
    the right place to maintain and refresh the current view while Rifts merely
    consume that view under session-specific access rules.
  EVIDENCE:
  - user_instruction: "a link in my system is a connection that represents something so maybe FrameLink doesn't make sense"
  - user_instruction: "I think the Nexus should own access to all the Frames and all the objects we're referring to"
  - user_instruction: "and then the Rift just gets access to it"
  IMPACT: The HLD should move away from a Rift-owned canonical surface store and
    instead treat Nexus as the authoritative live view host, with Rift consuming
    a session-scoped projection on top. Naming should also avoid overloading
    "link" if it already has a strong relationship meaning elsewhere.
  NEXT: propose better object names and a Nexus-owned canonical surface model
    with Rift as a consumer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T09:35:02Z
  TYPE: DECISION
  CLAIM: The corrected HLD should now be read like this:
    Nexus owns and updates canonical `FrameLink` representations,
    `FrameView` owns references to those links for one perspective,
    `FrameViewer` owns the methods that query/interact with that view,
    and ACLs are represented in the links after policy application rather than
    being executed by the viewer. Real object acquisition still stays outside
    the viewer surface through the conduit/Rift bind path.
  EVIDENCE:
  - user_instruction: "the FrameView should own the objects and the Viewer should have the methods to interact with them right?"
  - user_instruction: "the Nexus updates links if something changes"
  - user_instruction: "ACLs don't live in the FrameLink they are just represented there"
  IMPACT: The design problem is now well-posed enough to move into exact
    responsibility tables for the surface objects.
  NEXT: define the exact responsibilities and forbidden responsibilities for
    `FrameLink`, `FrameView`, `FrameViewer`, and the Nexus update boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T11:26:49Z
  TYPE: FACT
  CLAIM: The user clarified the next-order implications of the corrected model.
    `FrameViewer` is the final consumer and may need to hold multiple
    `FrameView` objects at once so it can build multiple interactive areas
    across contracts that span more than one frame. At the same time, lower
    truth may churn quickly, including repeated spell mutation, so the HLD must
    think seriously about update cost. Weak references may eventually help, but
    starting there would likely trade determinism for complexity too early. A
    related unresolved issue is that spells do not currently live in a shell
    that represents multiple versions simultaneously.
  EVIDENCE:
  - user_instruction: "the Viewer can build multiple interactive areas because its the final output consumer"
  - user_instruction: "things will change quickly and sometimes a spell might mutate a few times in a few minutes"
  - user_instruction: "spells don't live in a shell that can represent multiple versions"
  IMPACT: The HLD should explicitly include multi-frame viewer consumption and
    the weakref/versioning tradeoff instead of treating them as implementation
    details.
  NEXT: define the exact responsibilities and fields for `FrameLink`,
    `FrameView`, `FrameViewer`, and the Nexus update boundary with those
    pressures in mind.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T20:49:16Z
  TYPE: DECISION
  CLAIM: The next concrete step is now clearer than before. The viewer-side
    objects that were scaffolded under `rift/` are intentionally only shells.
    The next design target is the Nexus-side canonical holding zone for the
    representations those shells will consume. In other words: before finalizing
    `FrameLink` / `FrameView` / `FrameViewer` semantics, we need to define what
    canonical frame/conduit/spell representation objects Nexus will host and
    how lower runtime changes update them.
  EVIDENCE:
  - user_instruction: "we haven't built the nexus holding zone for all the objects we want to actually consume here"
  - user_instruction: "I think we go there first"
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-170
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-141
  IMPACT: The HLD task should now prioritize the Nexus-side canonical store
    format and update flow before spending more effort on viewer/query
    semantics.
  NEXT: define the Nexus-side holding zone object and the canonical
    frame/conduit/spell representation objects it should host.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T20:59:41Z
  TYPE: FACT
  CLAIM: The current record-model direction is now clear enough to preserve.
    The missing next layer is a Nexus-side canonical representation store that
    holds live mutable records rather than snapshots. The canonical ownership
    split discussed so far is:
    1) `Nexus` owns the canonical representation store and update ingress;
    2) viewer-side objects under `rift/` stay as consumers, not truth owners.
    The record families we identified are:
    - `SpellRecord`: updated at bind/examination time and again when
      ownership/version changes after conjure or MutationResearch. It should
      carry spell identity (`spell_id`, `lineage_id`, `spell_name`,
      `spellframe`, `binding_key`), policy (`existence`, `permissions`),
      ownership (`owner_conduit_id`, and likely `spellbook_id`), plus the
      semantic side from `SpellAIProfile` and the resolution/structural side
      needed for the viewer.
    - `ConduitRecord`: live mutable conduit representation. The current
      preferred shape is thin but complete enough to target a conduit by id:
      `conduit_id`, `conduit_name`, `frame_name`, `conduit_state`,
      `dynamic_environment`, `policy`, and explicit peer-link information.
      Every conduit already has a stable id, so canonical per-conduit records
      are likely better than storing roots only. Full lesser-conduit trees may
      still be derived on demand from the real root conduit instead of being
      mirrored eagerly in the record.
    - `FrameRecord`: frame-level living representation. This should hold the
      frame posture and frame-owned services, not just conduit counts. We
      explicitly called out that a frame is more than a conduit holder and may
      expose things like change-control and other frame-owned services.
    We also clarified that `NexusFrameRecord` is already a different object:
    it is the runtime management record for actual Nexus-managed internal
    frames and should not be reused as the viewer-facing canonical
    representation layer.
  EVIDENCE:
  - user_instruction: "record all your ideas about SpellRecord, ConduitRecord and Spellbook and Spellframe all that jazz in the ticket"
  - user_instruction: "for conduit I think its mainly links that impact it"
  - user_instruction: "the frame itself isn't just a conduit holder"
  - src/melder/spellbook/spellbook.py:152-200
  - src/melder/aether/conduit/conduit.py:107-176
  - src/melder/spellbook/spell.py:41-118
  - src/melder/aether/nexus/nexus_frame_record.py:11-30
  IMPACT: Future work should stop debating whether the viewer layer needs truth
    and instead focus on formalizing the Nexus-owned canonical record store and
    update ingress for these record families.
  NEXT: define the actual Nexus-side store object and its update semantics
    before finalizing the viewer/query objects any further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T20:59:41Z
  TYPE: DECISION
  CLAIM: The `Nexus` chicken-and-egg problem is now better framed. We do not
    want to auto-enable full interactive Rift behavior just because spell
    examination or AI profiles exist, because `Nexus.enable(...)` today
    represents a process-wide interactive policy boundary. But we do need a way
    for lower runtime layers to keep the Nexus-side canonical records current.
    The emerging direction is to separate "Nexus exists and may ingest
    canonical record updates" from "Nexus is enabled for interactive Rift
    operations." In other words, Nexus likely needs a passive/canonical ingest
    posture distinct from full interactive AR enablement.
  EVIDENCE:
  - user_instruction: "we have a chicken and the egg problem now"
  - user_instruction: "we can't update nexus unless its active, and enabled"
  - user_instruction: "what if we just enable it by default"
  - src/melder/aether/nexus/nexus.py:323-351
  IMPACT: The next design slice should formalize the Nexus-side holding zone
    and ingress lifecycle before deciding whether any automatic enablement or
    publication path is acceptable.
  NEXT: decide what object owns the canonical store and whether Nexus needs a
    passive ingest mode distinct from interactive enablement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T21:19:37Z
  TYPE: FACT
  CLAIM: A dedicated follow-up backlog task now exists for the Nexus-side
    implementation work implied by the HLD: passive ingest semantics plus the
    canonical record store. This captures the implementation direction without
    prematurely activating it before the design lane is done.
  EVIDENCE:
  - tickets/tasks/backlog/2026-04-03_implement_nexus_passive_ingest_and_canonical_store_task.md:1-119
  IMPACT: The HLD lane now has a concrete downstream implementation target,
    which should make the current design work easier to sequence and less
    likely to get lost after compaction.
  NEXT: continue refining the canonical store shape in design, then activate
    the backlog task when the HLD is stable enough.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T22:42:00Z
  TYPE: FACT
  CLAIM: The frame-level configuration story is now clearer and it sharpens the
    Nexus holding-zone design. `AethericFrame` already has exactly one
    `_configuration` slot, so the long-lived runtime posture is inherently
    frame-scoped, not spellbook-scoped. But `Spellbook` can still temporarily
    carry its own local `Configuration` object before conjure binds it into
    Aether. That means same-frame Spellbooks can momentarily diverge in their
    candidate config objects until one of them validates/freezes and binds the
    frame config. The three values that matter most for AR/Nexus posture are
    now clear: `system_state`, `ai_native_enabled`, and
    `rift_enabled`. Other values like full-AOT/JIT behavior remain more
    spellbook/runtime specific and do not need to be the first frame-posture
    payload surfaced into Nexus.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:86-87
  - src/melder/aether/aether.py:372-423
  - src/melder/spellbook/spellbook.py:2645-2689
  - src/melder/spellbook/spellbook.py:2833-2893
  - src/melder/spellbook/spellbook_creation_system.py:201-222
  - src/melder/spellbook/configuration/configuration.py:71-80
  - src/melder/spellbook/configuration/configuration.py:383-391
  IMPACT: The Nexus-side canonical store should likely treat frame posture as
    one explicit frame-level record/facet sourced from the bound
    `AethericFrame` configuration, while also recognizing there is a pre-bind
    same-frame conflict hole if multiple Spellbooks try to carry different
    candidate configs before the first bind.
  NEXT: decide whether same-frame config divergence should be rejected before
    conjure and whether the first frame-level canonical payload for Nexus
    should be only `system_state`, `ai_native_enabled`, and
    `rift_enabled`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to define the HLD for the frame-scoped query/display/bind
surface with Nexus owning and updating canonical links before implementation
starts.

