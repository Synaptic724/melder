# Task: Design Profile Contracts And Access Boundaries

## Metadata
- Task ID: TASK-2026-04-02-design-profile-contracts-and-access-boundaries
- Story: STORY-2026-04-02-profile-contracts-and-access-boundaries
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-04-02T22:25:55Z
- Updated: 2026-04-26T20:06:02Z

## Objective
Define the field-level ownership split between semantic profiles, structure
profiles, and ACL/access decisions, identify which object should later
consume them on the Rift side, and define the layered ACL spec plus
intersection-merge rule that should feed that later consumer.

## Ticket Contract
- ENTRY_GATE: the new epic is routed and the user approved starting with the
  data model before building the Rift aggregation layer.
- EXECUTION_BOUNDARY: design and documentation of profile/access contracts only.
- DEPENDENCIES:
  - tickets/epics/2026-04-02_rift_profile_surface_and_access_model_epic.md
  - src/melder/spellbook/spell_crafter/spell_examiner/*
  - src/melder/aether/structure_profiles/*
  - src/melder/aether/nexus/*
- EXIT_GATE: we have a concrete proposed split for
  `SpellAIProfile`, structure profiles, and ACL/access policy, with clear
  ownership rules and next implementation targets.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the design requires merging
  concerns in a way the user does not want.

## Scope Boundaries
- In scope:
  - semantic profile responsibilities
  - structural profile responsibilities
  - ACL/access responsibility split
  - Rift-side consuming responsibility at a high level
  - layered ACL spec ownership
  - ACL merge/precedence rule
- Out of scope:
  - code implementation
  - final eventstream design
  - UI rendering contracts

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: this is the first concrete design slice under the new
  profile/access epic.

## Steps / Checklist
- [ ] Capture current profile capabilities and gaps.
- [ ] Define what belongs in `SpellAIProfile`.
- [ ] Define what belongs in structure profiles.
- [ ] Define what belongs in ACL/access decisions.
- [ ] Define the raw ACL spec shape for Spell, Spellbook, Conduit, and Frame.
- [ ] Define the narrowing/intersection merge rule for those ACL specs.
- [ ] Define which Rift-side object should consume/aggregate them later.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- design notes for semantic/structural/access split
- ACL spec and merge-rule definition
- proposed next implementation targets

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content src/melder/spellbook/spell_crafter/spell_examiner/profiles/ai_profile.py`
  - `Get-Content src/melder/aether/structure_profiles/structure_profile_models.py`

## Risks / Rollback Notes
- Risk: we define a blurry model that still mixes semantic, structural, and
  access concerns.
  Rollback: keep the split explicit and reject mixed-field proposals.

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
- CLEANUP_TRIGGER: stale artifact reference removed because the linked file no longer exists

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T19:36:33Z
  TYPE: FACT
  CLAIM: The SpellExaminer/profile substrate lane is now closed and stable
    enough that ACL design can resume on top of it. The spell-facing profile
    model now has:
    - `general` and `detailed` only
    - two-step lifecycle completion
    - profile propagation through bind/scan paths
    - resolution data living under the spell-owned profile instead of a mirror
      field on `Spell`
    That means the next ACL work no longer needs to pause on spell profile
    storage uncertainty and can go back to the authored ACL configuration and
    view-side composition problem.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-05_implement_spell_examiner_registry_rebuild_task.md:1-166
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:1-130
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:1-384
  IMPACT: The active next ACL/design step can focus on `FrameACLConfiguration`
    and the view-side object composition instead of reopening spell profile
    lifecycle mechanics.
  NEXT: define the concrete view-side ACL configuration object graph on top of
    the now-stable spell profile and descriptor surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T13:12:00Z
  TYPE: FACT
  CLAIM: The current descriptor and AI-profile surfaces sharpen the view-ACL
    design space. The descriptor already gives us three concrete record
    families to target:
    `FrameRecord`, `ConduitRecord`, and `SpellRecord`.
    Those records already cover most of the stable view-facing truth we need:
    frame posture and topology summaries, conduit identity/policy/linkage
    state, and spell identity plus visibility-relevant policy/profile fields.
    `SpellRecord` is especially important because it already carries
    `binding_profile`, `resolution_profile`, and `ai_profile`.
    The current `SpellAIProfile` is a live object graph that bundles the
    binding profile, resolution profile, optional class/callable profiles,
    free-form metadata, instance-member inventory, and dynamic-access flags.
    So the first real view configuration should not invent another substrate
    model. It should author visibility/filter rules over these existing
    descriptor records, and then use the attached `ai_profile` to validate and
    enrich spell/member view rules later.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:1-124
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:1-91
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:1-131
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/ai_profile.py:1-101
  IMPACT: The view-side ACL object should be designed as policy over
    descriptor-owned truth, not as a second duplicate representation layer.
    The descriptor records should be the stable targeting surface, and the AI
    profile should be treated as member inventory/enrichment support rather
    than as the ACL truth owner.
  NEXT: propose the full object composition for `FrameACLViewConfiguration`
    using `FrameRecord`, `ConduitRecord`, `SpellRecord`, and `SpellAIProfile`
    as the grounding surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T19:42:03Z
  TYPE: FACT
  CLAIM: The current ACL design state is now preserved in one dedicated artifact
    instead of being split only across task notes. The artifact records the
    current direction for:
    - builder-first authoring
    - persisted selector-first ACL documents with optional resolved-id caches
    - descriptor-owned management/validation/compiled-access split
    - stable selector identities (frame name, conduit name, spell lookup/signature)
    - validated path-gating merge semantics
    - the relationship to `FrameLinkContract` / viewer surfaces
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/nexus_acl_builder_and_persistence_model.md:1-267
  IMPACT: The next thread can resume ACL implementation/design from one durable
    file instead of reconstructing the model from scattered note history.
  NEXT: use the artifact as the canonical ACL design reference for the next
    builder/document/schema pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T17:48:26Z
  TYPE: DECISION
  CLAIM: The ACL persistence model should be dual-identity, not names-only and
    not ids-only. Persisted ACL documents may carry both selector identity and
    resolved runtime identity, but the selector side is authoritative across
    runs. For frames and conduits, the stable cross-run selector is the name
    (`frame_name`, `conduit_name`) because ULID-style runtime ids are not
    stable between runs. For spells, the stable selector is the existing meld
    signature / spell lookup identity, and the current `spell_id` may also be
    persisted as a resolved deterministic value. On JSON load, ACL management
    should resolve names/signatures back to the current runtime ids and refresh
    the stored resolved-id side rather than treating old runtime ids as the
    sole authority.
  EVIDENCE:
  - user_instruction: "we need the names and the ID because we use both"
  - user_instruction: "if they provide a JSON to parse instead of fluent we look for the names and find the IDs for the objects between runs"
  - user_instruction: "spellIDs stay the same because they are SHA256 keys but the ULIDs change for everything else"
  IMPACT: The ACL system now has a clearer storage contract: persisted docs
    should include stable selectors plus optional cached resolved ids, while
    validation/compile refreshes the resolved-id side on every load.
  NEXT: define the exact persisted JSON shape with selector fields and
    optional resolved-id cache fields, plus the reload/refresh rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T17:22:47Z
  TYPE: DECISION
  CLAIM: JSON/id-keyed ACL authoring is the wrong primary interface because
    users do not know runtime ids (`conduit_id`, `spellbook_id`, `spell_id`).
    Those ids are fine for compiled/internal storage, but the authored ACL
    surface should be a fluent selector API that reuses Melder's existing
    semantic lookup conventions. Spell selectors should ride the same logical
    key path the runtime already uses for bind/meld
    (`spellframe + binding_name`, with `spell_name + binding_name` fallback).
    Conduit and spellbook selection should also be context-driven rather than
    raw-id driven, likely through frame-scoped and conduit-scoped fluent
    builders.
  EVIDENCE:
  - user_instruction: "you can't use IDs because the user does not know IDs"
  - user_instruction: "we cannot use a json format due to that context"
  - user_instruction: "spells you can use keys"
  - user_instruction: "we need an actual fluent api for the entire registration process for ACLS"
  - src/melder/utilities/helpers/general_helpers.py:32-215
  - src/melder/spellbook/spellbook.py:1119-1147
  - src/melder/aether/conduit/meld/meld.py:1028-1058
  IMPACT: ACL design now needs two explicit representations:
    1) user-facing fluent authoring/selectors,
    2) compiled descriptor-owned set structures keyed by resolved ids.
    The fluent API is the real authoring contract; JSON/id maps are only an
    internal compiled/storage format if we keep them at all.
  NEXT: define the fluent ACL authoring API and how it resolves selectors into
    descriptor-owned compiled ACL sets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T17:08:51Z
  TYPE: FACT
  CLAIM: Spell ACL authoring should reuse Melder's existing logical spell
    identity path rather than inventing a second selector model. Bound spells
    already carry a normalized lookup key built through
    `SpellInputUtils.make_spell_key_from_parts(...)` /
    `normalize_spell_key(...)`, where the canonical logical identity is
    `(frame_key, binding_key)`. `Spellbook.bind(...)` registers that key in
    `_lookup_spells` against the lineage (`SpellIndex`), and meld resolution
    uses the exact same `(frame_key, binding_key)` path when the caller does
    not provide a raw `spell_id`. So spell ACL authoring should target the same
    logical identity system:
    - primary: `spellframe + binding_name`
    - fallback: `spell_name + binding_name` when no spellframe exists
    - optional advanced override: exact current `spell_id`
    Then ACL compilation can resolve that logical key to the current runtime
    `spell_id` through the existing lookup/index path instead of creating a new
    parallel name-to-spell mapping.
  EVIDENCE:
  - src/melder/spellbook/bind/bind.py:153-248
  - src/melder/utilities/helpers/general_helpers.py:32-215
  - src/melder/spellbook/spellbook.py:1119-1147
  - src/melder/spellbook/spellbook.py:1149-1195
  - src/melder/spellbook/spellbook.py:2478-2574
  - src/melder/aether/conduit/meld/meld.py:1028-1058
  - src/melder/aether/conduit/meld/meld.py:1060-1138
  - src/melder/aether/conduit/meld/contracts/spell_map.py:1-219
  IMPACT: Spell ACLs can be user-authored with the same semantic selectors the
    runtime already understands for meld/bind resolution, while the compiled
    ACL layer still resolves those selectors to current `spell_id`s for fast
    lookup.
  NEXT: define spell ACL selectors around canonical logical keys
    (`spellframe/binding_name` first, `spell_name/binding_name` fallback) and
    treat raw `spell_id` as an advanced direct selector rather than the primary
    user-facing path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T16:44:30Z
  TYPE: PLAN
  CLAIM: The ACL design now needs an explicit subsystem split instead of one
    monolithic "ACL object." The user wants fast overlapping set logic and also
    a real validation layer, which points to three separate concerns:
    raw ACL storage/management, ACL validation, and compiled access output. The
    likely shape is a descriptor-owned `ACLManagementSystem` that stores raw
    frame/conduit/spellbook/spell ACL specs and compiled caches, a sibling
    `ACLValidationSystem` that validates schema/reference/hierarchy
    contradictions, and a thin Nexus facade that delegates to those systems
    through `FrameDescriptor`.
  EVIDENCE:
  - user_instruction: "we might still be able to use set operations just to keep it simple"
  - user_instruction: "we need to build a proper ACLManagementSystem, ACLValidationSystem"
  - user_instruction: "we put the ACLs in the ACL management system but then we facade this to the nexus"
  IMPACT: The next design pass should focus on the exact subsystem boundaries
    and shared normalized set schema rather than arguing only about layer
    precedence.
  NEXT: define the internal structures of `ACLManagementSystem`,
    `ACLValidationSystem`, and the compiled access surface they should produce.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T16:38:12Z
  TYPE: DECISION
  CLAIM: The ACL merge rule is no longer "lowest/more specific layer wins."
    That override model is too loose because it allows lower layers to reopen
    surfaces a higher owner intended to close. The better direction is
    validated path-gating: effective access exists only when every relevant
    owner in the path permits it. Lower layers may narrow/filter access inside
    their scope, but they may not widen access above a higher-level deny. If a
    lower ACL explicitly re-allows something a higher layer denied, ACL
    validation should flag that as an invalid configuration rather than silently
    picking a winner.
  EVIDENCE:
  - user_instruction: "I take back what I said about lower levels having more power"
  - user_instruction: "if the frame has a conduit denied, but we try and enable it in lower leveles we should throw an error and flag whats wrong"
  IMPACT: The compiler design should shift from precedence semantics to
    consistency validation plus intersection/set-subtraction semantics. This
    keeps ACLs fast and predictable while avoiding hidden override behavior.
  NEXT: define raw ACL shapes with explicit allow/deny selectors per ownership
    layer and add a compile-time validation pass that rejects lower-level
    contradictions against higher-level denies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T16:30:24Z
  TYPE: PLAN
  CLAIM: The cleanest v1 ACL shape now looks like a Nexus/descriptor-owned
    three-layer raw ACL registry plus a separate compiled access surface.
    `FrameDescriptor` is already the correct frame aggregate, so raw
    ACL specs should live under it rather than on the giant runtime objects.
    The recommended first slice is:
    1) one frame-level ACL container,
    2) spellbook ACLs keyed by spellbook id,
    3) conduit ACLs keyed by conduit id,
    while deferring a separate spell-level ACL container unless we truly need
    it. Spell-specific visibility can still be expressed inside spellbook ACLs
    keyed by stable lineage ids. The compiler should normalize those raw specs
    against the current `FrameRecord`, `ConduitRecord`, and `SpellRecord`
    state and emit one derived access surface containing fast set-based
    answers for the future frame/view/codegen layer. `FrameLinkContract`
    should then become a view-safe representation over that compiled access,
    not the place where ACL merging happens.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor.py:1-430
  - src/melder/aether/nexus/canonical_store/frame_record.py:1-115
  - src/melder/aether/nexus/canonical_store/conduit_record.py:1-88
  - src/melder/aether/nexus/canonical_store/spell_record.py:1-112
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-145
  - user_instruction: "ACLs live under descriptor but not yet"
  - user_instruction: "spellbook/conduit/aether"
  - user_instruction: "and what if the nexus owns it instead and we use IDs to target the element"
  - codex/context_compass/tickets/artifacts/ai_profile_and_policy_middleware_design.md:11-163
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:33-240
  IMPACT: This avoids two bad outcomes at once: bloating runtime objects with
    another mirrored subsystem, and flattening ACL logic into viewer or
    contract placeholders. It also gives us a stable place to compile and cache
    access answers later.
  NEXT: define the exact raw ACL fields and the compiled operation buckets
    (`visible`, `methods`, `attrs`, `bindable`, `linkable`, `creatable`) for
    this descriptor-owned model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T16:30:24Z
  TYPE: FACT
  CLAIM: The retained Rift artifacts reinforce a cleaner three-layer split for
    the ACL lane. The lower substrate already has spell permissions, conduit
    policies, and link contracts; the middle layer should be a derived
    target/access surface; and the top layer is the room/view/workspace model
    (`RiftSpace`, `RiftAttribute`, `RiftMethod`, validator/codegen flow). The
    artifacts consistently treat the workspace as policy-agnostic and consume a
    compiled behavioral surface rather than raw contracts. They also preserve a
    hard separation between ordinary local room work and canonical
    MutationResearch/promotion.
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:10-285
  - codex/context_compass/tickets/artifacts/ai_profile_and_policy_middleware_design.md:11-163
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:12-298
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md:11-185
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md:1-43
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md:1-35
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md:1-50
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_validation_system.md:1-41
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/code_description_patch_rift_validation_and_execution.md:1-49
  IMPACT: The ACL model should not be designed as one flat middleware blob and
    should not be buried inside raw `SpellContract` or runtime policy enums.
    The correct direction is: raw ACL specs under real ownership layers,
    Nexus-side compilation into a derived access surface, then room/view/codegen
    consumption of that compiled surface.
  NEXT: define the exact raw ACL containers that should live under
    `FrameDescriptor`, plus the compiled access object that later
    frame/view/codegen layers consume.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T12:05:48Z
  TYPE: DECISION
  CLAIM: The ACL model is now materially more concrete than the older artifacts.
    The intended layering is not one flat policy middleware object invented in
    isolation; it is a multi-level access-spec stack attached to real Melder
    ownership layers. The user-defined levels are:
    1) Spell ACLs: per-spell method/attribute visibility plus full-spell deny;
    2) Spellbook ACLs: spell/spell-index allow/deny lists and broader
       spellbook-scoped restrictions;
    3) Conduit ACLs: conduit/root/link access restrictions;
    4) Frame ACLs: coarse conduit and spell deny/allow shaping at frame scope.
    The intended precedence is bottom/specific over top/general, but in a
    narrowing way: lower layers should specialize or further restrict higher
    ones rather than silently widening access above a broader deny. The user
    also wants these ACL specs configured on the real objects (`Spell`,
    `Spellbook`, `Conduit`, `AethericFrame`), collected through Nexus, and then
    compiled into the derived access surface used by view, contracts, and
    codegen.
  EVIDENCE:
  - user_instruction: "ACLs were meant to be Spell Level like what methods and attributes we want to show or even if we want to decline a specific spell"
  - user_instruction: "SPellbook level, what spells and spellindexes we want to eliminate"
  - user_instruction: "Conduit Level, we could outright deny access to conduits based on specific roots and linking access"
  - user_instruction: "final Frame level, is access to specific conduits, denylist for spells etc etc"
  - user_instruction: "The general theme here is the bottom variant would outrank the higher varients"
  - user_instruction: "These would be configured in Spell, Spellbook, Conduit, and Frame as additional configurables that is collected via the Nexus and utilized in the view and for contracts and then also for codegen"
  IMPACT: This gives the ACL lane a real ownership model. The next design step
    is to define the normalized ACL spec shape per layer plus the merge rules
    that compile those raw specs into the derived access contract consumed by
    frame/view/contract/codegen layers.
  NEXT: define the per-layer ACL spec schema and the merge/precedence rules,
    with explicit operation categories (visibility, attribute read, method
    invoke, bind, create/link, etc.).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T11:52:00Z
  TYPE: FACT
  CLAIM: The current runtime already separates three different concerns that we
    should not blur when we design the viewer/contract ACL layer. First, spell-
    level permissions already exist as a tiny enum on the spell itself
    (`read`, `create`, `block`). Second, conduit-level relationship policy
    already exists separately as `Policies` on `ConduitWard`
    (`default`, `whitelist_all`, `block_all`, `inbound_only`,
    `outbound_only`). Third, `SpellContract` itself is not an ACL object at
    all; it is only a late-binding contract socket that carries contract
    identity (`spell`, `spellframe`, `binding_name`) plus optional override
    payload. So if we want ACLs that can be utilized in the future contract/view
    layer, they should not be shoved into `SpellContract` directly and they
    should not just mirror the existing spell permission enum. We likely need a
    distinct derived access view over the current spell permission + conduit
    policy + contract/link state.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/permissions/permissions.py:1-10
  - src/melder/aether/conduit/conduit_ward/policies/policies.py:1-15
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:6-57
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:74-155
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:29-55
  IMPACT: We are ready to design the contract/view ACL layer, but only if we
    treat it as its own derived contract/output model rather than pretending
    the current `Permissions`, `Policies`, or `SpellContract` types already are
    that full ACL model.
  NEXT: define the derived ACL/access object shape and decide which layer owns
    computing it for frame/view/contract consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T11:58:00Z
  TYPE: FACT
  CLAIM: The retained original AR artifacts still carry a useful contract
    direction for this lane. They already separate the room target model from
    deeper substrate/link mechanics: `RiftAttribute` / `RiftMethod` are the
    declared target universe, `RiftValidationSystem` validates against that
    target universe, `RiftSpace` is the room/execution surface, and the AR
    profile stack is explicitly described as exposure/capability shaping rather
    than runtime config or fake sandboxing. That means our future
    frame/view/ACL work should likely treat link contracts as lower substrate
    mechanics, while the viewer/room layer consumes a derived target/access
    model over them instead of exposing raw contract/socket objects directly.
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:18-58
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md:1-31
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md:1-27
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md:1-38
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_validation_system.md:1-31
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/code_description_patch_rift_validation_and_execution.md:1-44
  IMPACT: We do not need to invent the top-side contract model from scratch.
    The existing artifacts already support a layered answer: substrate
    contracts/links below, derived room targets plus derived access/exposure
    above.
  NEXT: use those artifacts as precedent when defining the future
    FrameLink/FrameView/FrameViewer contract surface and its derived ACL model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T22:25:55Z
  TYPE: PLAN
  CLAIM: The first slice should avoid designing the full Rift exposure/event
    model immediately. The correct order is to define the data families first:
    semantic profile data, structural profile data, and access-policy data,
    then decide later how Rift aggregates them.
  EVIDENCE:
  - user_instruction: "lets target the data first"
  - user_instruction: "I think we focus on the profiles to give the most potential then go to ACLs, and then build the next stuff for the rift right?"
  IMPACT: This task should stay at the contract-definition layer instead of
    jumping into premature implementation.
  NEXT: propose the ownership split and field families to the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T22:33:42Z
  TYPE: FACT
  CLAIM: The user clarified the higher-level operating split that should govern
    this design. `Rift` should be treated as the execution/API surface into
    Melder, while CommandOps should own the threadpool/actor execution and task
    scheduling side. That means the Rift-side model should stay synchronous and
    queryable as an API boundary, not absorb CommandOps threading concerns. The
    missing question is therefore what query/display object sits on top of the
    profile families and how requests/responses should be structured for
    codegen or method-call usage.
  EVIDENCE:
  - user_instruction: "Rift (Execution Surface), CommandOps WorkPlace(thread interacts with objects and interacts with workstation object from rift...)"
  - user_instruction: "the thread tasks should be in the commandops side so we don't need any threads in the Rift"
  IMPACT: The design should target an API-style Rift surface with structured
    query/request/response objects, not a threaded runtime inside Rift.
  NEXT: propose the API boundary objects and request/response contract with
    CommandOps owning orchestration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T22:40:31Z
  TYPE: FACT
  CLAIM: The user clarified a second critical split inside the API model.
    The Rift-side API is needed to discover, inspect, and resolve objects/spells,
    but once a target is deliberately bound into the workspace as `self`,
    codegen should be able to operate on that object first-class instead of
    continuing to route every interaction through the query surface. That means
    the design needs two explicit modes: a discovery/query mode and a bound
    execution mode.
  EVIDENCE:
  - user_instruction: "you can use this api to understand the spells and things in it"
  - user_instruction: "you can also call the objects you want and they get bound to the workspace as self"
  - user_instruction: "from here you can use codegen to interact with it first class"
  - user_instruction: "at this level you no longer need that interface"
  IMPACT: The Rift-side design should not assume one uniform interaction model.
    It needs a query/resolve surface for discovery and selection, plus a bound
    object workspace mode where codegen interacts with real objects directly.
  NEXT: define the boundary between discovery/query APIs and bound-object
    execution semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T22:47:52Z
  TYPE: FACT
  CLAIM: The original AR artifacts already captured most of the semantic split
    we are rediscovering. The strongest recovered points are:
    1) `RiftSpace` was intended to be the primary semantic execution room,
    not just a registry wrapper;
    2) the room should expose a queryable current-state surface distinct from
    interaction history;
    3) codegen was intended to move through a declared target model
    (`RiftAttribute` / `RiftMethod`) and then operate in a bound workspace
    context where `RiftSpace` is the semantic execution root;
    4) profiles were already meant to stay separate from runtime config and to
    shape exposure/capability rather than become fake sandbox mechanics;
    5) local workspace actions were always meant to remain distinct from
    canonical mutation/promotion.
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:24-31
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:64-76
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:122-137
  - codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md:245-285
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md:4-31
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md:4-27
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md:4-38
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_validation_system.md:4-26
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/code_description_patch_rift_validation_and_execution.md:21-43
  IMPACT: We should not invent a brand-new model. The correct move is to
    reconcile the recovered original AR semantics with the current live
    Nexus/Rift/runtime code and then implement the missing pieces in that
    direction.
  NEXT: summarize the recovered artifact model for the user and propose how it
    maps onto the current Nexus/Rift/profile split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T22:56:14Z
  TYPE: DECISION
  CLAIM: The user confirmed the intended API model. Static AR should not
    require dynamic system state. In static mode the agent may query declared
    targets, inspect them, resolve already-registered Melder objects, bind the
    real returned objects into the workspace, and then operate on those bound
    objects first-class through codegen. What static mode must not expose is
    open conduit-backed local construction. Dynamic mode adds that construction
    surface on top of the same declared target/query/bind model. CommandOps
    owns the threadpool and may execute multiple query/codegen tasks in
    parallel against the Rift API surface.
  EVIDENCE:
  - user_instruction: "in Static, you don't need to be in Dynamic(Conduit State) mode right?"
  - user_instruction: "you can basically query these objects spawn them still using codegen and then work with them right?"
  - user_instruction: "once you find your objects you bind them to the workspace, and you just use codegen"
  - user_instruction: "You can also use codegen to query multiple things at once because its available you just create multiple tasks and it executes them via the threadpool"
  IMPACT: The design should enforce a two-mode AR contract:
    discovery/query/resolve/bind exists in both static and dynamic,
    while conduit-backed local construction is dynamic-only. CommandOps remains
    the parallel execution owner.
  NEXT: define the concrete API boundary objects for query, bind, workspace
    bindings, and action execution under that split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:36:28Z
  TYPE: FACT
  CLAIM: The ACL design task is now partially stale against the live
    descriptor contract. Its current notes still talk about `SpellRecord`
    carrying `binding_profile`, `resolution_profile`, and `ai_profile`, and
    they still use the older `SpellAIProfile` naming as if that were the
    current spell-facing floor. But the live runtime has moved further:
    `SpellRecord`, `ConduitRecord`, and `FrameRecord` are all payload-backed
    now, and the spell-facing profile family is `general` / `detailed`.
    That means the next ACL design step should target payload-backed descriptor
    records and the current rich spell descriptor payload floor instead of the
    old split-field `SpellRecord` model.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:145-169
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:43-104
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:34-71
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:34-68
  - src/melder/utilities/interfaces/interfaces.py:2161-2299
  IMPACT: The ACL/view lane should stop targeting the old split record model
    and should define `FrameACLViewConfiguration` over the payload-backed
    descriptor records that actually exist now.
  NEXT: inspect the current ACL runtime objects (`FrameACLConfiguration`,
    `FrameACLProfile`, `FrameACLContainer`, `FrameACLManager`) and propose the
    concrete view-side configuration object graph on top of the payload-backed
    record contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:36:28Z
  TYPE: FACT
  CLAIM: The current ACL runtime objects are still a generic serialized-holder
    model, not a typed view/codegen configuration model. `FrameACLConfiguration`
    stores one normalized JSON payload string and its default payload shape is
    just `{frame_name, view_acl, codegen_acl}`. `FrameACLProfile` is a named
    strategy registry over `ViewACLDetails` and `CodegenACLDetails`, and those
    detail objects are also just normalized JSON string holders. `FrameACLContainer`
    and `FrameACLManager` are already the right lifecycle/history shells around
    that state: the container owns one chain, validator, and unique builder,
    while the manager owns frame-name -> container plus named profile storage.
    So the next concrete ACL design step is not "invent the subsystem." The
    subsystem exists. The next step is to replace or refine the generic JSON
    payload layer with typed `FrameACLViewConfiguration` and sibling typed
    config objects that sit inside the existing shell objects.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:10-444
  - src/melder/aether/nexus/acl/frame_acl_profile.py:10-543
  - src/melder/aether/nexus/acl/frame_acl_container.py:14-259
  - src/melder/aether/nexus/frame_acl_manager.py:14-535
  IMPACT: The ACL design lane should preserve the current manager/container/
    chain skeleton and focus its next design pass on typed configuration
    composition rather than subsystem ownership.
  NEXT: inspect the current builder and validator behavior, then define the
    exact typed object graph for `FrameACLConfiguration`, with
    `FrameACLViewConfiguration` as the first concrete payload to replace the
    generic JSON holder model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:36:28Z
  TYPE: DECISION
  CLAIM: The next concrete ACL design slice should preserve the existing shell
    objects and replace the generic payload layer inside them. `FrameACLManager`
    and `FrameACLContainer` are already the right ownership/history shell.
    `FrameACLConfiguration` should evolve from "one normalized JSON string with
    `view_acl` and `codegen_acl` keys" into a typed root object that owns:
    1) `FrameACLViewConfiguration`
    2) `FrameACLCodegenConfiguration`
    plus the existing chain metadata (`frame_name`, source/previous ids,
    created_at, reason, locked). `FrameACLBuilder` should edit those typed
    child objects instead of a raw JSON string, and `FrameACLValidator` should
    graduate from frame-name-only validation into descriptor-backed validation
    against the payload-backed `FrameRecord` / `ConduitRecord` /
    `SpellRecord` surface. `FrameACLProfile` should remain the reusable
    profile library, but its detail holders should eventually become typed
    view/codegen profile objects instead of generic JSON strings too.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:10-444
  - src/melder/aether/nexus/acl/frame_acl_builder.py:10-192
  - src/melder/aether/nexus/acl/frame_acl_validator.py:10-116
  - src/melder/aether/nexus/acl/frame_acl_profile.py:10-543
  - src/melder/aether/nexus/acl/frame_acl_container.py:14-259
  - src/melder/aether/nexus/frame_acl_manager.py:14-535
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:43-104
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:34-71
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:34-68
  IMPACT: The ACL lane now has one concrete design direction that fits both the
    existing ACL shell objects and the new payload-backed descriptor contract.
  NEXT: update the retained ACL artifact to reflect this typed configuration
    direction, then define the concrete field composition for
    `FrameACLViewConfiguration`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:36:28Z
  TYPE: CONFLICT
  CLAIM: The old four-layer ACL model included a first-class spellbook ACL
    layer, but the live descriptor substrate still has no `SpellbookRecord` and
    no stable spellbook selector beyond runtime ids. Current descriptor truth
    only gives us:
    - `FrameRecord`
    - `ConduitRecord`
    - `SpellRecord`
    plus `origin_spellbook_id` / `config_origin_spellbook_id` references.
    That is enough for internal grouping, but not enough for a selector-first
    persisted spellbook ACL surface that matches the rest of the design.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:33-68
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:33-71
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:33-115
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:274-289
  - codex/context_compass/tickets/artifacts/nexus_acl_builder_and_persistence_model.md:134-171
  IMPACT: A clean v1 `FrameACLViewConfiguration` can target frame, conduit, and
    spell selectors directly, but spellbook-level authored selectors are still
    blocked on missing stable selector substrate.
  NEXT: recommend one of two paths:
    1) defer first-class spellbook ACL authoring in v1 and let frame/conduit/
       spell layers cover the initial design, or
    2) add a new stable spellbook selector contract/record before finalizing
       the ACL schema.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:36:28Z
  TYPE: PLAN
  CLAIM: The first typed `FrameACLViewConfiguration` draft should map directly
    onto the payload-backed descriptor records instead of inventing a second
    representation layer. The clean v1 object graph is:
    1) `FrameACLConfiguration`
       - existing chain metadata
       - `view_configuration: FrameACLViewConfiguration`
       - `codegen_configuration: FrameACLCodegenConfiguration`
    2) `FrameACLViewConfiguration`
       - `minimum_spell_payload_profile_name`
       - `frame_rule: FrameViewRule`
       - `conduit_rules_by_name: Dict[str, ConduitViewRule]`
       - `spell_rules_by_selector: Dict[SpellSelector, SpellViewRule]`
    3) `FrameViewRule`
       - frame-wide ceilings over payload visibility
       - conduit/spell allow/deny selectors at frame scope
    4) `ConduitViewRule`
       - `visible`
       - `show_payload`
       - `show_policy`
       - `show_peer_links`
       - conduit-scoped spell allow/deny selectors
    5) `SpellViewRule`
       - `visible`
       - section toggles that map directly to spell payload fields:
         `show_binding_payload`, `show_resolution_payload`,
         `show_class_profile`, `show_callable_profile`,
         `show_metadata`, `show_instance_members`,
         `show_dynamic_access`
       - `allow_method_names` / `deny_method_names`
       - `allow_attribute_names` / `deny_attribute_names`
    This keeps the ACL config extendable, keeps it aligned with the current
    descriptor payloads, and gives the validator one direct mapping target.
    Spellbook-level authored selectors should stay deferred in v1 until a stable
    selector surface exists.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:77-203
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:9-66
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:8-101
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:112-166
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:170-210
  IMPACT: The ACL lane now has one concrete typed view-configuration draft that
    matches the live descriptor record contract and is specific enough to turn
    into an implementation plan later.
  NEXT: update the retained ACL artifact with this typed
    `FrameACLViewConfiguration` draft and use it as the current design floor for
    the next implementation-planning slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T20:06:02Z
  TYPE: FACT
  CLAIM: The task is still live on the attention board, but its ticket header
    had drifted. `Agent Name` was missing and the `Updated` timestamp still
    reflected the older design pass even though the lane is still routed.
  EVIDENCE:
  - codex/context_compass/attention_board.md:26-26
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:1-12
  IMPACT: The ticket header needs normalization so the active design lane keeps
    explicit assignment metadata.
  NEXT: keep the task routed as an in-progress design lane until the user
    either retires it or requests the next ACL slice explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-26T20:10:59Z
  TYPE: FACT
  CLAIM: The ticket's active artifact declaration was stale. It still claimed
    `tickets/artifacts/nexus_acl_builder_and_persistence_model.md` as an active
    linked artifact, but that file is gone on disk, so the live artifact link
    has been removed from the task header.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:103-108
  - missing_artifact_path: codex/context_compass/tickets/artifacts/nexus_acl_builder_and_persistence_model.md
  IMPACT: The task no longer advertises a dead active artifact reference in its
    metadata, even though older historical notes still mention the past design
    artifact.
  NEXT: use current ticket notes and live runtime docs as the active ACL design
    context unless a replacement retained artifact is created later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is the first design slice under the profile/access epic and should
produce the field/responsibility split before implementation begins.
