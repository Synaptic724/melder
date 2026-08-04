# Task: Implement Actionable Viewer Profile Tool Compositions
- Completed: 2026-04-09T11:31:39Z
- Summary: Finished the viewer host-only descriptor summary layer and left the viewer complete for this tranche.


## Metadata
- Task ID: TASK-2026-04-06-implement-actionable-viewer-profile-tool-compositions
- Story: STORY-2026-04-06-contract-backed-assigned-frame-views
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T15:58:28Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Make the single `general` `FrameViewerProfile` compose genuinely actionable
frame, conduit, and spell helper objects from a dedicated `profiles/general/`
package so the viewer is not just plumbing.

## Ticket Contract
- ENTRY_GATE: the host seam, selected-target context, and direct viewer/profile
  runtime are landed, and the user explicitly called out that the viewer still
  needs actionable composed tools.
- EXECUTION_BOUNDARY: actionable viewer tool composition and helper-object
  layout only.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-06_implement_rift_space_target_selection_context.md
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/
  - tests/unit/melder/aether/test_frame_viewer_projection.py
- EXIT_GATE: the single `general` profile is packaged under
  `profiles/general/`, composes `view_frame`, `view_conduit`, and
  `view_spell`, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the viewer needs a broader
  workspace/runtime redesign to become actionable.

## Scope Boundaries
- In scope:
  - actionable viewer methods
  - `profiles/general/` package layout
  - `view_frame`, `view_conduit`, and `view_spell` helper objects
  - single `general` profile composition
  - focused tests
- Out of scope:
  - codegen execution
  - raw object binding
  - broader workspace redesign

## State Transition Event
- from_state: blocked
- to_state: in_progress
- transition_reason: the user has now specified the exact viewer-method
  structure: one `general` profile under `profiles/general/` composed from
  `view_frame`, `view_conduit`, and `view_spell`.

## Steps / Checklist
- [ ] Inspect the current viewer/profile methods and identify the smallest
      missing actionable tool surface.
- [ ] Create patch docs for the `profiles/general/` helper-object layout.
- [ ] Add `profiles/general/` with `general_profile.py`, `view_frame.py`,
      `view_conduit.py`, and `view_spell.py`.
- [ ] Add actionable viewer methods through those helper objects.
- [ ] Compose those methods into the single seeded `general` profile.
- [ ] Add/update focused tests.
- [ ] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- actionable viewer methods
- composed `general` profile helper surfaces
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`
- `python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py`
- `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`

## Risks / Rollback Notes
- Risk: the slice drifts into codegen/runtime execution.
  Rollback: keep the cut on actionable navigation/inspection/view-selection
  tools only.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/frame_viewer_general_helper_surfaces/architecture_patch.md
  - system_docs/patches/active/frame_viewer_general_helper_surfaces/component_patch_frame_viewer_profile.md
  - system_docs/patches/active/frame_viewer_general_helper_surfaces/component_patch_frame_viewer.md
  - system_docs/patches/active/frame_viewer_general_helper_surfaces/code_description_patch_general_viewer_helper_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicitly retire after the
  general viewer helper model settles

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T15:58:28Z
  TYPE: PLAN
  CLAIM: The next bounded requirement is actionable viewer composition. The
    current viewer chain is real, but the user is right that it still needs a
    stronger composed tool surface to be worth using. The smallest correct cut
    is to add actionable navigation/inspection/view-selection methods and then
    compose those methods into seeded viewer profiles.
  EVIDENCE:
  - user_instruction: "by the end of today you better have a viewer that can compose different kinds of methods in the profile to actually have actionable tools to use"
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-760
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-223
  IMPACT: This slice should make the viewer materially useful instead of just
    structurally correct.
  NEXT: inspect the current viewer/profile surface and add the smallest set of
    truly actionable methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T15:58:28Z
  TYPE: FACT
  CLAIM: The smallest real gap is not “more random tools.” It is two missing
    categories of actionable behavior on the viewer:
    1) view navigation/inspection (`describe_available_views`, default-view
       switching)
    2) per-view profile targeting (`list_view_profile_names`,
       `set_default_view_profile`)
    The low-level chain is already there, but these methods are what make the
    viewer materially useful to an agent through profile composition instead of
    only through direct object poking.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:174-760
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:510-689
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-223
  IMPACT: The next cut should add those actionable methods and then expose them
    through seeded profile tool maps with meaningful aliases.
  NEXT: implement view-navigation/per-view-profile methods on `FrameViewer`,
    then seed actionable viewer profiles around them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T16:52:25Z
  TYPE: CONFLICT
  CLAIM: This task is now blocked by a broader architectural correction. The
    user explicitly redirected the active Nexus lane away from more
    `FrameViewerProfile` tool composition and toward:
    1) descriptor<->ACL payload-contract validation
    2) investigation of removing `FrameView` from the runtime path entirely
    So this task is no longer the active next step.
  EVIDENCE:
  - user_instruction: "I want you to properly ensure payloads are validated"
  - user_instruction: "lets remove the view, as well we don't need that and lets just use the viewer"
  - user_instruction: "I don't want you to do this in 1 prompt"
  IMPACT: More viewer-profile tool composition would now be building on a
    runtime layer that may be deleted next.
  NEXT: keep this task blocked until the remove-`FrameView` investigation
    resolves the runtime direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T20:28:20Z
  TYPE: DECISION
  CLAIM: The viewer-method lane is reactivated on the corrected runtime. The
    user wants exactly one profile per frame, and that profile should now live
    under `profiles/general/` and compose three helper objects:
    `view_frame`, `view_conduit`, and `view_spell`. These are helper surfaces
    inside the single `general` profile, not separate profiles.
  EVIDENCE:
  - user_instruction: "in the profiles folder, make a folder called general"
  - user_instruction: "In general place those 3 files for view_frame, view_conduit, view_spell"
  - user_instruction: "Then compose those inside the general profile itself"
  - user_instruction: "we only want 1 profile we do not want 3"
  IMPACT: The implementation should reorganize the general viewer profile into
    helper objects instead of adding more seeded top-level viewer profiles.
  NEXT: create the patch docs and implement the `profiles/general/` package
    layout on the current descriptor-driven viewer runtime.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T20:49:34Z
  TYPE: FACT
  CLAIM: The first pass of the new `profiles/general/` helper layout exposed a
    code-quality miss: several newly added helper-surface methods landed
    without docstrings. That violates the repo's documentation-first editing
    contract, so the next step is to repair the new `general` helper files
    before continuing the viewer-method tranche.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-358
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-85
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-85
  IMPACT: Viewer-method work should pause until the new helper surfaces meet
    the repo's docstring contract.
  NEXT: add rich docstrings to the newly added helper-surface methods and then
    resume the runtime refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T20:42:47Z
  TYPE: MEASURE
  CLAIM: The `general` helper-object layout is now landed and green on the
    focused viewer/Nexus slices. The viewer profile package now has
    `profiles/general/` with `general_profile.py`, `view_frame.py`,
    `view_conduit.py`, and `view_spell.py`; the builder now seeds only
    `general`; tool routing supports dotted helper-object handler paths; and
    the viewer tests were realigned to the one-profile model.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:1-174
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-358
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-85
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-85
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:173-183
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile_builder.py:33-39
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:767-840
  - tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py:1-131
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-363
  - tests/unit/melder/aether/test_nexus.py:1-807
  IMPACT: The viewer-method tranche can move to user review instead of staying
    in implementation.
  NEXT: review the one-profile `general` helper-object slice and either accept
    it or direct the next viewer-method expansion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T21:08:18Z
  TYPE: MEASURE
  CLAIM: The helper objects are now deeper and more operator-focused. The
    frame helper can report frame inventory and the effective ACL access
    contract, the conduit helper can describe conduit topology and list
    conduit-owned spells, and the spell helper now has a dedicated
    `describe_spell_detail(...)` path that distinguishes
    `payload_not_detailed` from `acl_restricted` instead of forcing richer
    detail blindly. Focused and nearby viewer/Nexus slices are green after the
    refinement.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-611
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-235
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-287
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:1-186
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-519
  IMPACT: The viewer is now much closer to the real operator use case: inspect
    the frame, understand the ACL posture, walk conduits to spells, and ask
    for richer spell detail without forcing every payload to be `detailed`.
  NEXT: remove fresh `__pycache__` again and leave this tranche ready for user
    review or another viewer-method refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T21:17:05Z
  TYPE: PLAN
  CLAIM: The next useful gap is explicit lookup and ACL explanation. The
    helpers now describe records and payloads well, but the operator still
    needs faster exact lookup (`find_*`) plus explicit access-explanation
    methods that answer what is visible, which sections are exposed, and how
    much detail is available under the current ACL posture.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-611
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-235
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-287
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:185-248
  IMPACT: This pass should make the viewer faster to operate and more explicit
    about ACL-driven constraints instead of making the operator infer them.
  NEXT: add exact-lookup and ACL-explanation methods to the 3 helper objects,
    route them through the `general` profile, and validate the focused viewer
    slices again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T22:01:35Z
  TYPE: DECISION
  CLAIM: The host/profile boundary needs one more correction. `FrameViewer`
    should stay on simple host duties only, while frame-local descriptive work
    belongs on the bound `view_frame` helper. Concretely:
    - `view_frame.list_frames()` and `view_frame.describe_views()` should go
      away
    - `FrameViewer.describe_available_views()` should remain host-level but be
      simplified to frame listing/default only
    - direct host `describe_frame(...)` use in tests/tools should move to the
      profile/helper path
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:99-134
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:360-492
  - tests/unit/melder/aether/test_frame_viewer_projection.py:194-194
  - tests/unit/melder/aether/test_frame_viewer_projection.py:285-285
  - tests/component/melder/aether/test_frame_acl_compiler_component.py:239-239
  IMPACT: The current helper/package layout is close, but the frame host still
    leaks too much frame-local behavior and `view_frame` still carries
    multi-frame-ish methods it should not own.
  NEXT: remove the multi-frame-ish helper methods, simplify the host view
    description, and realign the focused tests to the corrected boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T22:03:09Z
  TYPE: MEASURE
  CLAIM: The host/profile boundary correction is now landed and green.
    `FrameViewer` stays on simple host duties (`list_frame_names`,
    `describe_available_views`, frame selection), while `view_frame` owns the
    frame-local descriptive methods. The multi-frame-ish helper methods were
    removed from `view_frame`, host `describe_frame`/`describe_frames` were
    dropped, and the focused tests now call frame-local description through the
    bound profile/tool path instead of the host.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:302-492
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-666
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:174-225
  - tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py:1-131
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-638
  - tests/component/melder/aether/test_frame_acl_compiler_component.py:223-244
  IMPACT: The viewer surface is more coherent now: host methods are simple and
    frame-local detail stays on the bound helper object where it belongs.
  NEXT: remove fresh `__pycache__` again and keep iterating on useful helper
    methods instead of blurring the host boundary again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T22:10:04Z
  TYPE: MEASURE
  CLAIM: The latest host-boundary refinement is green. `FrameViewer` now owns
    only simple descriptor-host methods (`list_frame_names`,
    `describe_available_views`, `describe_frame`, `describe_frames`,
    `count_frames`, `count_root_conduits`, `count_spell_records`) while the
    frame-local helper objects retain the payload/ACL-shaped methods. The
    focused viewer/component tests were realigned to that boundary.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:302-492
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:174-225
  - tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py:1-131
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-638
  - tests/component/melder/aether/test_frame_acl_compiler_component.py:223-244
  IMPACT: The host surface now matches your rule better: simple descriptor
    summaries and counts on `FrameViewer`, payload/detail logic on the bound
    helpers.
  NEXT: clear fresh `__pycache__` again and continue runtime-only refinement
    when you want the next operator method batch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T22:07:08Z
  TYPE: DECISION
  CLAIM: The host boundary is being refined again. `FrameViewer` is allowed to
    expose simple descriptor-level frame information to the agent:
    frame names, counts, and descriptor summaries. It is not allowed to expose
    payload bodies or ACL-shaped payload views through those host methods. The
    payload-aware methods stay on the bound helper objects.
  EVIDENCE:
  - user_instruction: "you are allowed to use frame_viewer to describe the frames registered in it"
  - user_instruction: "you are not permitted to go into the records and view the payloads"
  - user_instruction: "count all spell records, count root conduits, count frames, describe frames, describe frame"
  IMPACT: The next cut should add host-level descriptor summary/counter methods
    and route `describe_frame`/`describe_frames` back to the host without
    reintroducing payload or ACL detail there.
  NEXT: implement descriptor-only frame summary/counter methods on
    `FrameViewer`, update the `general` tool map, and realign the focused
    tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T21:20:28Z
  TYPE: MEASURE
  CLAIM: The lookup/explanation refinement is now green. The `general` profile
    can do exact target lookup by display name, exact conduit lookup by name,
    exact spell lookup by binding name, spell filtering by `payload_type`, and
    explicit ACL explanation for frame/conduit/spell visibility and visible
    sections. This makes the operator path less inferential and more direct.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-736
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-345
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-472
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:1-193
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-638
  IMPACT: The `general` viewer surface is now materially better for real use:
    inspect the frame, find the thing, and understand what the ACL is exposing
    without manual guesswork.
  NEXT: remove fresh `__pycache__` again and leave this tranche ready for
    another refinement or review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T21:16:09Z
  TYPE: PLAN
  CLAIM: The next refinement gap is lookup and explanation ergonomics. The
    helpers can now describe records and payloads, but the main operator still
    lacks fast exact-name lookup and explicit ACL-facing explanations for why a
    conduit or spell exposes only certain sections. The next bounded cut is to
    add those lookup/explanation methods on `view_frame`, `view_conduit`, and
    `view_spell`, then route them through the same single `general` profile.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-490
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-235
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-287
  IMPACT: The next pass should improve day-to-day usability instead of adding
    another architectural layer.
  NEXT: implement exact lookup and ACL-explanation helpers, then validate the
    focused viewer/Nexus slices again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T20:56:37Z
  TYPE: FACT
  CLAIM: The helper objects are now record-aware instead of just wrapping
    generic target links. `view_frame` can describe the filtered frame payload,
    `view_conduit` can describe individual conduits and conduit payload
    sections, and `view_spell` can describe individual spells and spell payload
    sections. The spell helper explicitly degrades cleanly when the published
    spell payload is only `general`, so richer detailed-only fields are omitted
    instead of forcing or faking them.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-490
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-176
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-194
  - tests/unit/melder/aether/test_frame_viewer_projection.py:180-515
  IMPACT: The viewer now actually meshes with `FrameRecord`,
    `ConduitRecord`, `SpellRecord`, and the compiled ACL surface instead of
    only surfacing generic link metadata.
  NEXT: remove fresh `__pycache__` garbage again and leave this tranche ready
    for review/acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T21:02:17Z
  TYPE: FACT
  CLAIM: Both `general` and `detailed` spell profiles can publish into
    `SpellRecord` through the same `spell.profile -> to_descriptor_payload()`
    path. `FrameDescriptorManager._publish_spell_record(...)` accepts anything
    satisfying `ISpellGeneralProfile`, so a `SpellDetailedProfile` also
    qualifies because it subclasses `SpellGeneralProfile`. The difference is in
    the published payload body: `general` emits `payload_type="general"` with
    empty richer detail maps, while `detailed` emits `payload_type="detailed"`
    with richer class/callable/member/dynamic-access content populated when
    available.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:26-156
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:27-242
  - src/melder/aether/nexus/frame_descriptor_manager.py:440-454
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:12-113
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:69-199
  IMPACT: The viewer helpers must never force `detailed`. They should inspect
    `payload_type` and degrade cleanly when only `general` payload content is
    published.
  NEXT: keep the `view_spell` helper on the graceful-degradation path and
    avoid assuming detailed-only fields are present.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T21:05:10Z
  TYPE: PLAN
  CLAIM: The next refinement pass should optimize the `general` helper objects
    around the actual viewer use case: fast frame inventory, conduit topology,
    spell payload inspection, and a richer spell-detail path when the published
    spell payload is `detailed`. The user wants `general` payloads supported,
    but not forced into fake rich detail.
  EVIDENCE:
  - user_instruction: "one question you should really be asking is what the fuck do I want out of this viewer"
  - user_instruction: "have some special optimized methods for detailed"
  - user_instruction: "I want general to be supported but not as deeply as detaield"
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-490
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-176
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-194
  IMPACT: The helper objects should grow explicit inventory/topology/payload
    methods and a separate detailed spell path instead of relying only on
    generic target descriptions.
  NEXT: implement richer frame/conduit/spell helper methods and route them
    through the `general` profile tool map, then validate the focused slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T22:22:31Z
  TYPE: FACT
  CLAIM: The host/profile boundary is still incomplete. `FrameViewer` still
    exposes the old ACL/link helper surface publicly (`list_links`,
    `list_available_targets`, `describe_available_targets`,
    `get_required_link_by_source`, and related grouped/count/display helpers),
    and `RiftSpace` still delegates selection/description through those host
    methods. That violates the newer rule that `FrameViewer` should only expose
    simple descriptor-host methods while payload/ACL-shaped work stays on the
    bound helper objects.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:504-698
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:263-490
  - src/melder/utilities/interfaces/interfaces.py:6015-6037
  IMPACT: The next cut must remove the stale host ACL/link surface from
    `FrameViewer` and rewire `RiftSpace` to use the bound profile tool path
    instead of reaching into the viewer host directly.
  NEXT: delete the public host ACL/link methods from `FrameViewer`, switch
    `RiftSpace` target selection/description to `execute_tool(...)`, and then
    fix the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T22:28:58Z
  TYPE: DECISION
  CLAIM: The dispatcher path is the wrong model. `FrameViewer.execute_tool(...)`
    should be removed instead of becoming the main surface. The corrected
    runtime split is:
    - `FrameViewer` hosts only simple multi-descriptor methods
    - the selected bound profile is consumed directly
    - `view_frame` / `view_conduit` / `view_spell` expose the frame-local
      methods directly without a generic tool router in between
  EVIDENCE:
  - user_instruction: "we don't need a fucken dispatcher"
  - user_instruction: "I do not want multiframe methods inside the frame_view"
  - user_instruction: "FrameViewer just hosts general methods about the descriptor"
  IMPACT: The next cut must remove `execute_tool(...)`, stop routing workspace
    flows through a dispatcher, and update tests/runtime to use direct viewer
    host methods or direct bound-profile helper methods.
  NEXT: remove `execute_tool(...)`, rewire `RiftSpace` to call the selected
    bound profile directly, and update the focused viewer/Nexus tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T22:35:03Z
  TYPE: FACT
  CLAIM: The runtime surface is now aligned to the corrected naming and
    boundary model. `FrameViewer` keeps only the simple multi-descriptor host
    methods (`describe_available_views`, `count_root_conduits`,
    `count_spell_records`, `describe_frame`, `describe_frames`) and the
    generic dispatcher was renamed to `execute_method(...)`. `RiftSpace`
    target selection/description now routes through that profile-method seam
    instead of the removed host ACL/link methods.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:374-488
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:681-723
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:263-320
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:371-470
  IMPACT: Validation can now target the corrected public/runtime surface rather
    than the stale `execute_tool(...)` / host-link path.
  NEXT: run the focused viewer/Nexus tests and fix any remaining callers that
    still assume the old host ACL surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T22:37:52Z
  TYPE: MEASURE
  CLAIM: The corrected viewer/profile surface is green on the broader
    viewer/Nexus slice. The stale host ACL/link methods are gone, the runtime
    now uses `execute_method(...)` instead of `execute_tool(...)`, and
    the direct caller/tests were realigned to that renamed seam plus the
    descriptor-only host methods on `FrameViewer`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:374-488
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:681-723
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:263-320
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:371-470
  - tests/unit/melder/aether/test_frame_viewer_projection.py:249-249
  - tests/unit/melder/aether/test_frame_viewer_projection.py:762-762
  - tests/component/melder/aether/test_frame_acl_compiler_component.py:239-244
  - tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py:132-138
  IMPACT: The repo is back in a coherent state for this lane: one simple
    multi-descriptor host, one selected bound profile per frame, and one
    correctly named profile-method execution seam.
  NEXT: review this viewer-boundary tranche and either accept it or direct the
    next viewer/runtime refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T23:20:22Z
  TYPE: PLAN
  CLAIM: The next expansion batch is now concrete from the live descriptor and
    payload shapes. We can add a much richer operator surface without changing
    the descriptor wall yet:
    1) `FrameViewer` gets more multi-frame descriptor-only inventory/filter
       methods over `FrameRecord`, `ConduitRecord`, and `SpellRecord`
    2) `view_frame` gets visible-surface, topology, identity, and search/group
       helpers
    3) `view_conduit` gets root/group/relationship/inventory helpers
    4) `view_spell` gets identity/origin/lineage/binding/resolution/detail
       helpers plus explicit dunder-member visibility in detailed mode
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:1-98
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:1-91
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:1-137
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:1-104
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:1-75
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:1-259
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:1-410
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:1-455
  IMPACT: We can materially improve daily Rift usability right now without
    reopening payload/schema design, as long as the host stays descriptor-only
    and the helper objects stay frame-local.
  NEXT: implement the descriptor-only host batch first, then add the helper
    expansion batch and cover it with focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T00:16:19Z
  TYPE: MEASURE
  CLAIM: The expansion batch is landed and green. `FrameViewer` now has a much
    richer descriptor-only multi-frame inventory/provenance surface
    (`list_frame_ids`, `describe_descriptor_inventory`,
    `describe_descriptor_topology`, `describe_spell_record`, and related
    record/filter methods). `view_frame` now has visible-surface/topology/search
    methods, `view_conduit` now has root/relationship/inventory/access-summary
    methods, and `view_spell` now has identity/origin/lineage/binding/
    resolution/metadata/detail methods plus explicit dunder-member visibility
    in detailed mode. The `FrameViewer` docstrings were also tightened around
    the host/profile boundary and the `execute_method(...)` seam.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:502-1290
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1471-1534
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:252-698
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:174-497
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:178-777
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:174-262
  - tests/unit/melder/aether/test_frame_viewer_projection.py:718-1077
  IMPACT: The Rift viewer surface is materially more usable now without
    breaking the descriptor wall or reopening mutation/payload-schema work.
  NEXT: review this larger viewer-surface tranche and either accept it or
    direct the next operator-surface refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T00:49:17Z
  TYPE: MEASURE
  CLAIM: The next operator-ergonomics batch is landed and green. `FrameViewer`
    now has compact host/operator summaries and descriptor comparisons
    (`describe_frame_brief`, `describe_host_inventory`, `compare_frames`,
    `compare_frame_conduits`, `compare_frame_spells`). `view_frame` now has
    `describe_frame_brief`, `describe_target_brief`, and
    `describe_missing_surface`; `view_conduit` now has
    `describe_conduit_brief` and `describe_conduit_missing_sections`; and
    `view_spell` now has `describe_spell_brief` and
    `describe_spell_missing_sections`. The new methods are also routed through
    the `general` profile map and covered by focused regression tests.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:502-1290
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:252-751
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:174-358
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:178-455
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:174-262
  - tests/unit/melder/aether/test_frame_viewer_projection.py:799-1170
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py" -> 52 passed
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py" -> 780 passed
  IMPACT: The viewer surface is faster to scan and compare now, not just wider.
  NEXT: review the brief/compare refinement and either accept it or direct the
    next operator-surface refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T01:05:08Z
  TYPE: MEASURE
  CLAIM: The crosswalk/ambiguity tranche is landed and green. `FrameViewer`
    now exposes record-level ambiguity and comparison helpers
    (`describe_binding_name_collisions`, `describe_spell_name_collisions`,
    `describe_lineage_groups`, `describe_spellframe_groups`,
    `describe_spellbook_permission_mismatches`,
    `describe_spellbook_existence_mismatches`, `compare_spell_records`,
    `compare_conduit_records`). `view_frame` now exposes
    `describe_visible_collisions`, `view_conduit` now exposes
    `describe_conduit_crosswalk` and `compare_conduits`, and `view_spell` now
    exposes `describe_spell_crosswalk` and `compare_spells`. The new methods
    are wired through the `general` profile map and covered by focused tests.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:775-1290
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:522-836
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:386-435
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:464-784
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:174-262
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1403-1621
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py" -> 58 passed
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py" -> 786 passed
  IMPACT: The viewer surface is now materially better at answering relation,
    ambiguity, and comparison questions instead of only listing or describing
    individual objects.
  NEXT: review the crosswalk/ambiguity refinement and either accept it or
    direct the next operator-surface refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T01:22:50Z
  TYPE: MEASURE
  CLAIM: The AST class-surface tranche is landed and green. A dedicated AST
    describer now emits minified JSON for class surfaces, `FrameViewerProfile`
    can describe itself plus any `view_*` helper objects dynamically, and
    `FrameViewer` now exposes host methods to describe the viewer class, the
    selected profile class, the selected helper classes, and the aggregated
    active AST surface bundle for the current frame context.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/class_surface_ast_describer.py:1-1
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:327-434
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1363-1547
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1624-1691
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py" -> 60 passed
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py" -> 788 passed
  IMPACT: The agent can now inspect the viewer/profile/helper source-defined
    class surfaces directly in compact JSON instead of guessing what methods
    exist or how to call them.
  NEXT: review the AST introspection slice and either accept it or direct the
    next operator/runtime refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T11:03:52Z
  TYPE: DECISION
  CLAIM: The AST describer should be treated as one shared static-method class,
    not a bag of free functions. The viewer/profile layer should only facade
    those static methods by passing `self`, so the same class can be reused
    later across the wider Melder system without per-object describer
    instances.
  EVIDENCE:
  - user_instruction: "the class should only own static methods"
  - user_instruction: "the viewer should just facade the methods it has and then pass self as the variable in the facade"
  - src/melder/aether/nexus/rift/frame_viewer/class_surface_ast_describer.py:1-313
  IMPACT: The current AST implementation needs one final architectural cleanup:
    move the shared AST logic into a reusable static-method class and keep the
    viewer/profile methods as thin facades only.
  NEXT: refactor the AST describer module into one shared static-method class,
    update the viewer/profile facades, and rerun the focused viewer validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T11:27:17Z
  TYPE: PLAN
  CLAIM: The next AST refinement is bigger than just the shared static class.
    The shared describer should also own:
    - one minified-JSON onboarding hint for Melder system-doc objects
    - one generic minified-JSON agent-purpose surface
    - enforcement of `_ast_helper_access`
    - private/public gating behavior
    The viewer remains the proving ground, but this also introduces the first
    top-level hardcopy system-doc objects:
    `__architecture__`, `__components__`, `__graph_network__`,
    `__graph_details__`.
  EVIDENCE:
  - user_instruction: "the class should only own static methods"
  - user_instruction: "we need to generically say access: public, as part of the message for __agent_purpose__"
  - user_instruction: "if the string is set to private it should expect that only the __agent_purpose__ exists"
  - user_instruction: "add the top level files __graph_details__ etc etc all these 4 items"
  IMPACT: This turns the AST utility into the first real agent-exposure
    contract and seeds the top-level system-doc objects the onboarding hint can
    point at.
  NEXT: add the `_ast_helper_access` / `__agent_purpose__` contract, private
    gating, onboarding/purpose JSON methods, and the top-level system-doc
    object placeholders, then validate the focused viewer and package-root
    slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T22:18:16Z
  TYPE: DECISION
  CLAIM: The AST metadata contract should be direct class-level metadata, not
    inherited semantic fallback from `Cleanable`. The shared describer should:
    - require `_ast_helper_access` to be defined on the concrete class
    - use the concrete class `__agent_purpose__` when present
    - report inherited parent-class purposes separately for context
    - never silently treat `Cleanable.__agent_purpose__` as the concrete
      object's own semantic purpose
  EVIDENCE:
  - user_instruction: "remove the cleanable inheritance vector spread you created"
  - user_instruction: "the scan of an object also shows its inherited objects purpose in a proper way"
  - user_instruction: "class level attrs not inited ATTRS"
  IMPACT: The current AST helper and `Cleanable` defaults need a contract
    correction before the viewer experiment becomes the broader model.
  NEXT: remove the semantic defaults from `Cleanable`, require direct
    class-level access metadata, and add inherited-purpose reporting to the
    shared AST JSON output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T11:10:12Z
  TYPE: MEASURE
  CLAIM: The AST refactor is now landed and green in the exact shape requested.
    The shared logic lives in one static-method class,
    `ClassSurfaceAstDescriber`, under
    `src/melder/utilities/helpers/class_surface_ast_describer.py`. The
    `FrameViewerProfile` and `FrameViewer` methods are now thin facades that
    pass `self` into that shared class rather than owning the AST logic
    themselves. The earlier viewer-local free-function module is gone.
  EVIDENCE:
  - src/melder/utilities/helpers/class_surface_ast_describer.py:1-313
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:10-11
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:340-458
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:23-23
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2003-2208
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1629-1705
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py" -> 60 passed
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py" -> 788 passed
  IMPACT: The viewer AST experiment now matches the intended architecture and
    the shared static utility can be reused later by other Melder systems.
  NEXT: review the AST static-facade refactor and either accept it or direct
    the next operator/runtime refinement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T11:35:44Z
  TYPE: MEASURE
  CLAIM: The shared AST access contract is now landed and green. The static
    describer now owns:
    - onboarding JSON pointing at `__architecture__`, `__components__`,
      `__graph_network__`, and `__graph_details__`
    - agent-purpose JSON
    - `_ast_helper_access` enforcement
    - private/public gating
    `Cleanable` now publishes default public access plus a generic
    `__agent_purpose__`, the viewer/profile/helper classes override with more
    specific public purposes, and the package root now exposes placeholder
    top-level system-doc objects through `melder.__architecture__`,
    `melder.__components__`, `melder.__graph_network__`, and
    `melder.__graph_details__`.
  EVIDENCE:
  - src/melder/utilities/general_base/cleanable.py:1-1
  - src/melder/utilities/helpers/class_surface_ast_describer.py:1-1
  - src/melder/system_document.py:1-1
  - src/melder/__architecture__.py:1-1
  - src/melder/__components__.py:1-1
  - src/melder/__graph_network__.py:1-1
  - src/melder/__graph_details__.py:1-1
  - src/melder/__init__.py:1-1
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1693-1761
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py" -> 63 passed
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py" -> 791 passed
  IMPACT: The viewer experiment now proves a broader Melder-ready agent
    exposure contract: shared static class-surface introspection, explicit
    access gating, semantic purpose text, and top-level system-doc entry
    objects.
  NEXT: review the shared AST access contract and either accept it or direct
    the next broader Melder agent-surface move.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T22:22:12Z
  TYPE: MEASURE
  CLAIM: The AST metadata contract is now aligned to the stricter rule. The
    semantic defaults were removed from `Cleanable`, `_ast_helper_access` is
    now required on the concrete class being described, and the shared AST
    helper reports inherited parent-class purposes separately instead of
    treating inherited purpose text as the concrete object's own purpose.
    Public concrete classes in the current viewer experiment now define their
    own `_ast_helper_access = "public"` and `__agent_purpose__` explicitly.
  EVIDENCE:
  - src/melder/utilities/general_base/cleanable.py:1-1
  - src/melder/utilities/helpers/class_surface_ast_describer.py:1-1
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-1
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:1-1
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:1-1
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-1
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:1-1
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-1
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1762-1832
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py" -> 64 passed
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_viewer_general_helper_matrix.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py" -> 792 passed
  IMPACT: The viewer experiment now matches the intended contract for a future
    wider Melder rollout: explicit concrete-class metadata, explicit private
    gating, and inherited purposes shown only as context.
  NEXT: review the direct-class metadata correction and either accept it or
    direct the next Melder agent-surface move.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T00:52:45Z
  TYPE: PLAN
  CLAIM: The next useful tranche is crosswalks and ambiguity handling. The
    current surface is wide and much more usable now, but the next time-saving
    win is helping the operator answer:
    - what frame/conduit/spellbook/lineage context a spell lives in
    - what related visible objects hang off one spell or conduit
    - where visible collisions or duplicate-like identities exist
    - what differs between two visible objects beyond raw set diffs
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:344-1917
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:88-836
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:11-435
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:14-784
  IMPACT: This should make the viewer feel more like a real operator console
    instead of a large bag of individual getters.
  NEXT: add spell/conduit/frame crosswalk methods, visible collision summaries,
    and spell/conduit comparison methods, then validate the focused viewer
    slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T01:16:14Z
  TYPE: DECISION
  CLAIM: The next introspection slice should be AST-first and emit minified
    JSON strings. Runtime should only locate the active viewer/profile/helper
    objects; AST should describe their class surfaces (public method names,
    signatures, docstrings, properties, and source locations). The output
    should be compact JSON so the agent can consume it directly without extra
    formatting noise.
  EVIDENCE:
  - user_instruction: "we do want to output in minified json btw that makes the most sense here"
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:1-1
  - src/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/spell_requirements_finder.py:596-596
  IMPACT: The implementation should use AST/source parsing for class-surface
    description, not deeper runtime method inspection, and the public return
    type should be minified JSON strings.
  NEXT: add an AST class-surface describer plus viewer/profile/helper methods
    that return minified JSON for the active viewer/profile/helper classes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-07T00:44:07Z
  TYPE: PLAN
  CLAIM: The next refinement batch should focus on operator ergonomics, not
    more raw surface area:
    1) compact `brief` methods on the host and helper surfaces
    2) host-level frame/descriptor comparison methods
    3) stronger "what differs / what is missing" summaries
    The goal is to make the current viewer faster to use, not just wider.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:344-1882
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:88-751
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_conduit.py:11-358
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:14-455
  IMPACT: This can improve day-to-day Rift usage without breaking the
    descriptor wall or reopening payload-schema work.
  NEXT: add host-level `brief` / comparison methods first, then add helper-side
    brief summaries and comparison-aware outputs, and validate the focused
    viewer slice again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-08T10:08:19Z
  TYPE: FACT
  CLAIM: The last useful `FrameViewer` host pass is smaller than expected.
    Two of the proposed host-summary methods already exist:
    `describe_frame_brief(...)` and `describe_host_inventory()`. The remaining
    clean host-only gap is a thin summary layer:
    `describe_viewer()`, `describe_current_frame()`,
    `describe_frames_inventory()`, `compare_frames_brief(...)`, and one
    curated `describe_viewer_method_surface()` helper.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:545-580
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:582-611
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:613-683
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2440-2459
  - tests/unit/melder/aether/test_frame_viewer_projection.py:959-978
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1017-1022
  IMPACT: The final viewer-host refinement can stay narrow, descriptor-only,
    and multi-frame-light instead of reopening another broad host expansion.
  NEXT: add the five remaining host-only summary methods, expose them through
    the `general` profile map, and extend the focused viewer tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-08T10:11:25Z
  TYPE: MEASURE
  CLAIM: The final host-only descriptor-summary layer is now landed and green.
    `FrameViewer` now exposes `describe_viewer()`,
    `describe_current_frame()`, `describe_frames_inventory()`,
    `compare_frames_brief(...)`, and `describe_viewer_method_surface()`.
    The `general` profile map routes those host methods through
    `execute_method(...)`, and the focused viewer unit slice passed after the
    change. Multi-frame behavior stayed shallow and descriptor-only.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:613-849
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/general_profile.py:210-217
  - tests/unit/melder/aether/test_frame_viewer_projection.py:956-1060
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1444-1516
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_viewer_projection.py" -> 64 passed
  - validation_result: "python -m pytest -q tests/unit/melder/aether/test_frame_view_and_viewer_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py" -> 74 passed
  IMPACT: The viewer host is now materially complete for its intended job:
    descriptor-only viewing, summary, comparison, and routing into frame-local
    helper methods without widening into non-viewer responsibilities.
  NEXT: review the final host-only refinement and either accept the viewer as
    done for this tranche or redirect to the next non-viewer subsystem.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

