# Epic: Expose versioned registrations in Nexus without runtime resolution

## Metadata
- Epic ID: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Status: in_progress
- Owner: user
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T16:34:27Z
- Updated: 2026-09-19T21:38:40Z
- Target Window: owner-directed; no release version assigned
- Related Program/Initiative: Nexus graph discovery, Spellbook registration, Crystallizer, MutationResearch

## Problem / Opportunity
The application architecture includes abstract bases and internal helper definitions that agents
need to discover, inspect, revise, and version even when Melder must never resolve those entries.
The owner wants these definitions represented as connected nodes in the Nexus graph, with explicit
user/agent registration and a declared role. Exposing source text alone does not meet this need.

The current direction is to reuse registration with an explicit non-resolution mode. A required
consumer input targeting such a registration is supplied through an override when the consumer is
constructed. The selected planning direction is an explicit caller-supplied category in the resolved
socket model, preserving the original declaration and graph target. Ordinary PLAIN remains unchanged.
The visible/versioned architectural relationship must survive independently of construction edges.

## Owner Direction and Working Vocabulary
- Register definitions so the graph network manifests properly in Nexus and can be versioned.
- Keep application classes ordinary Python; no mandatory Melder inheritance or source annotations.
- Mark selected registrations unresolvable while retaining their discovery and versioning surfaces.
- Required consumer inputs targeting those registrations need supplied overrides at construction.
- Preserve the earlier ordinary-default precedence fix.
- Preserve existing version rules, as explicitly selected by the owner. Same-identity body-only edits
  do not automatically become new versions; use existing module/binding/version workflows.
- The public modifier is `resolvable: bool = True` on bind and bind_inactive, stored per Spell version.
- Required supplied dependencies use the owner-selected resolved category OVERRIDE_REQUIRED.
- Subsequent owner continuation authorized S2/S3 implementation. Actual runtime enforcement is S4;
  creating the epic itself did not implement or qualify it.

## MRP Alignment (Most Reasonable Product)
Graph membership must describe the actual architecture while execution membership states what
Melder may resolve. A coherent solution carries that distinction through registration, compilation,
Nexus access, research history, and restore. A meld-only guard or a source catalogue is insufficient.

## Ticket Contract
- ENTRY_GATE: This epic and the first discovery story/task are linked and routed; predecessor
  findings and relevant component slices are read before new source investigation.
- EXECUTION_BOUNDARY: Registration metadata, compiler admission/sockets, resolution entry points,
  Nexus graph publication/tools, research history, and persistence of the accepted mode/relationships.
- DEPENDENCIES: First discovery story settles semantics. System-impacting implementation requires
  the normal architecture/component/code-description patch contracts and scoped regression work.
- EXIT_GATE: Required stories are accepted; public behavior, graph visibility, persistence, docs,
  and generated assets agree; artifact and attention-board closure synchronization is complete.
- FAILURE_ESCALATION: Record unresolved identity, matching, ownership, or lifecycle decisions before
  implementation. Missing source evidence stays UNKNOWN; do not silently choose a new object model.

## Goals (Outcomes)
- Abstract bases/helpers become independently addressable graph participants through registration.
- Nexus exposes their role, current version, relationships, history, and permitted agent operations.
- Non-resolvable registrations never become automatic construction/reuse candidates.
- A consumer can be registered/compiled with a known required caller-supplied input.
- The executable dependency DAG and the descriptive/versioned graph preserve their distinct meanings.
- Existing bindings and explicit defaults retain their behavior when the new mode is unused.
- Crystallizer restore preserves the mode and graph relationships without silently enabling resolution.

## Non-Goals (Explicit Exclusions)
- Redesign of existing/user-created instance ownership, uniqueness, transfer, or disposal.
- The named lesser-conduit feature; it remains a separate epic.
- Automatic mutation of existing Python instances or replacement of every live subclass on source edit.
- Replacement of SpellContract's linked-provider model.
- Mandatory per-class mixins, decorators, or a repository-wide source rewrite.
- A new ad hoc cache-invalidation framework, a release, or a version bump during discovery.
- Automatic source-body version identity or a redesign of the existing research/custody version model.

## Scope Boundaries
- In scope: the accepted registration-to-graph-to-runtime contract and its required persistence/tests.
- Out of scope: unrelated Nexus features, generic code-editor tooling, and broad compiler refactors.
- Target-family expansion beyond abstract/concrete class definitions is an explicit discovery decision.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner started S1 discovery with a modifier on bind/bind_inactive and resolvable defaults.

## Established Evidence and Limits
- Phase 1 records annotation, default presence/value, and optionality separately. Ordinary defaults
  become PLAIN before annotation inference; explicit SpellMap/SpellContract descriptors run first.
- Phase 2 retains a PLAIN symbolic socket and its annotation. Phase 3 supplies no dependency key,
  concrete target IDs, or construction DAG edges for that shape.
- The inspected solo override helper forwards caller arguments; its no-override path calls the
  target without arguments. This is source evidence only, not a full public-meld behavior test.
- Existing Nexus research module/part reads reach source through SpellCrystal identity. Raw source
  preview exists, but it does not create independent durable custody.
- Registration and normal-conduit emission already feed Crystallizer; restore rebinds through
  runtime entry points and translates identities. Native policy/compiler metadata now exist, but
  the new mode/graph persistence schema is still unimplemented.
- S2 admission and S3 compiler propagation are implemented and tested. Direct/fast/nested/cached
  execution enforcement and full Nexus/persistence behavior remain unqualified.
- Detailed evidence: predecessor task, Notes at lines 273-478; reopen current ranges before citing.

## Requirements (Functional + Non-Functional)

### Registration and identity
- A user or authorized agent can explicitly register a definition with non-resolution intent.
- Keep role/classification distinct from the capability to resolve. A concrete helper can be
  non-resolvable even though Python could construct it.
- Retain target/source provenance, registration identity, and version information for graph access.
- Store mode on the Spell version, independently of SpellIndex selection. Decide the fingerprint
  schema and legacy-SHA behavior; prevent same-identity contradictory resolution policies.
- Preserve existing registration guards unless a specific new admissible category is approved.

### Compiler and runtime
- Direct meld of a selected non-resolvable registration fails with an explicit actionable error.
- Apply the restriction consistently to id/name/frame lookup, nested construction, and cached lanes.
- Conjure does not instantiate or demand a construction plan for a discovery-only root.
- A discovery-only definition's own constructor requirements may be described without becoming
  runnable prerequisites that invalidate the container.
- A required consumer parameter targeting such an entry can remain pending until construction;
  a missing supplied value reports the consumer, parameter, and target before avoidable side effects.
- Use the provided value through existing override semantics where supported. Do not manufacture None.
- Ordinary explicit defaults remain honored. Override presence must distinguish omission from an
  explicit falsey value; type/Optional validation policy is a separate decision.
- Preserve normal reuse: an already-created consumer need not supply construction inputs again
  unless existing override/reuse semantics explicitly require that behavior.
- Scope the restriction to the selected registration. A discoverable abstract definition must not
  automatically suppress separate resolvable implementations registered under its spellframe.

### Nexus graph and agent work
- Registering a definition produces a first-class discoverable node, not an invisible side record.
- Preserve meaningful relationships, including consumer-input references and applicable inheritance,
  implementation, containment, and internal-use relationships. Set the initial edge vocabulary in S1.
- Distinguish inferred structural facts from explicitly declared design relationships.
- Caller-supplied sockets retain target identity for graph navigation and impact without construction edges.
- Tools can inspect nodes, navigate relationships, compare versions, and stage permitted revisions
  without needing to meld the target or run arbitrary code just to discover it.
- Existing access controls must cover the new nodes/operations; visibility does not grant invocation.

### History, custody, and restore
- Persist registration mode, role metadata, and the accepted graph relationships.
- Versioned graph selections identify the relevant node revisions and relationship targets rather
  than silently following a changing latest version.
- Keep source/module context sufficient for the accepted physical/synthetic reconstruction contract.
- Saving a candidate and adopting it into a running graph remain separate operations.
- Restore and graft preserve non-resolution intent and continue identity translation correctly.
- Decide legacy-record handling and cache-key/version changes using existing version/mismatch machinery.
- Registration/graph cleanup and index transfer/notch must preserve or remove metadata consistently;
  this does not expand lifecycle ownership of supplied application instances.

## Constraints / Assumptions
- Category spelling is OVERRIDE_REQUIRED and existing version rules are retained. Admission/selection
  recommendations are recorded in S1; exact graph payload and replay details remain S5/S6 work.
- The resolved caller-supplied category supersedes ordinary PLAIN coercion as the planning direction.
- No separate source registry is preselected over the owner's registration-flag direction.
- First trace the existing model; propose the smallest complete change that preserves its invariants.
- Python 3.14+ is the repository baseline. Follow current role typing/cleanup/documentation policy.

## Dependencies / External References
- Predecessor discovery and owner discussion:
  `tickets/tasks/2026-09-19_understand_nexus_crystallizer_spellbook_task.md`
- Separate related feature, not a prerequisite:
  `tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md`
- Historical adjacent proposal, not the implementation contract:
  `tickets/epics/archive/2026-04-07_agent_exposable_class_surface_contract_discovery_epic.md`
  That draft concerns class-surface introspection and explicitly excludes mutation integration.
- Existing-object redesign remains parked:
  `tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md`

## Milestones (Track Progress)
- [ ] M1: Accepted registration/socket/graph semantic table and source-grounded change map.
- [ ] M2: Minimal failing behavior regressions and accepted implementation patch contracts.
- [ ] M3: Registration and compiler/runtime paths honor the new mode end to end.
- [ ] M4: Nexus navigation/history and Crystallizer round trips preserve the complete graph contract.
- [ ] M5: Integration qualification, public guidance, generated assets, and owner acceptance.

## Stories (Required to Complete)
- [ ] S1: `STORY-2026-09-19-discoverable-registration-contract-discovery` — source discovery in review.
  `tickets/stories/2026-09-19_discoverable_registration_contract_discovery_story.md`
- [ ] S2: `STORY-2026-09-19-discoverable-registration-modifier` — implemented; focused validation passes; review pending.
  `tickets/stories/2026-09-19_discoverable_registration_modifier_story.md`
- [ ] S3: `STORY-2026-09-19-caller-supplied-socket-compiler` — implemented; 2098 focused tests pass; in review.
  `tickets/stories/2026-09-19_caller_supplied_socket_compiler_story.md`
- [ ] S4: `STORY-2026-09-19-discoverable-resolution-runtime` — ready; consumes the delivered S2/S3 contract.
  `tickets/stories/2026-09-19_discoverable_resolution_runtime_story.md`
- [ ] S5: `STORY-2026-09-19-discoverable-nexus-graph-and-history` — draft; depends on S1-S4.
  `tickets/stories/2026-09-19_discoverable_nexus_graph_and_history_story.md`
- [ ] S6: `STORY-2026-09-19-discoverable-registration-persistence` — draft; depends on S1-S5.
  `tickets/stories/2026-09-19_discoverable_registration_persistence_story.md`
- [ ] S7: `STORY-2026-09-19-discoverable-registration-qualification` — draft; depends on S1-S6.
  `tickets/stories/2026-09-19_discoverable_registration_qualification_story.md`

All seven story files exist. S1 results are recorded; S2 registration and S3 compiler implementation
are review-ready. S4 runtime enforcement is next, followed by graph/history, persistence and full
qualification. The compiler layer does not establish runtime safety or feature completion.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Complete the first S1 discovery task:
  `tickets/tasks/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md`
- [ ] Review the source-grounded S1 socket-contract proposal:
  `tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md`
- [ ] Settle selection of definitions versus executable providers:
  `tickets/tasks/2026-09-19_define_discoverable_registration_selection_task.md`
- [ ] Define non-resolvable target admission and fingerprint/source identity:
  `tickets/tasks/2026-09-19_define_non_resolvable_admission_identity_task.md`
- [x] Implement S2 registration foundation:
  `tickets/tasks/2026-09-19_implement_resolvable_registration_modifier_task.md`
- [x] Implement S3 compiler policy and downstream input/reference handoff:
  `tickets/tasks/2026-09-19_implement_override_required_compiler_task.md`
- [ ] Maintain source-backed decisions and a compact resume route across story transitions.
- [ ] Before code changes, create/read required patch contracts and map them to implementation/tests.
- [ ] Keep authored architecture/components and indexes current; regenerate graph/build assets normally.

## Acceptance Criteria (Epic Done)
- A registered abstract base and helper can be found, traversed, and versioned in Nexus without resolution.
- Direct resolution refuses; registration/conjure remains usable without constructing those definitions.
- A required consumer input accepts the supplied object and reports a useful missing-input error otherwise.
- Descriptive target relationships survive caller-supplied execution, revision, and graph history queries.
- Defaults, ordinary provider matching, and normal bindings pass compatibility regressions.
- Restored/grafted registrations retain the same mode and selected relationship semantics.
- Applicable lookup/override/compiler/cache paths are verified, with honest limits recorded.
- Required stories are accepted and documentation/build records match the final implementation.

## Risks / Mitigations
- A top-level meld guard misses nested or cached construction: qualify all execution doors.
- Ordinary PLAIN has no concrete target link: preserve one in the explicit supplied-input model.
- An abstract spellframe flag poisons concrete providers: classify the selected registration precisely.
- Discovery-only roots fail eager validation: separate descriptive requirements from construction admission.
- A new mode changes identity or restores as resolvable: define schema/fingerprint behavior before patching.
- Source revisions silently retarget consumers: preserve version selections and explicit adoption.
- Broad introspection redesign consumes the task: settle one registration/socket boundary first.

## Applicable Anti-Patterns
- [ ] No implementation derived only from enum names or component prose.
- [ ] No caller-supplied category that loses the registered graph target or rewrites declaration facts.
- [ ] No fake default or nullable annotation to suppress required-input enforcement.
- [ ] No blanket type-wide suppression of resolvable spellframe implementations.
- [ ] No alternate cache framework or speculative global compiler rewrite.
- [ ] No closure while required stories remain unaccepted.

## Validation / Test Approach
S2 registration tests pass (42 new cases within 1845 focused tests). S3 passes 2098 distinct focused
tests, including 42 new compiler component cases; source/LLM asset checks pass. These runs overlap
across stories and must not be added together as a distinct-test total. Later-layer tests remain
planned. Read tests_architecture/tests_components before creating test files and use existing fixtures.

| Area | Required behavioral evidence |
| --- | --- |
| Admission | Abstract/helper registration, default mode compatibility, duplicate identity/mode policy |
| Resolution | Direct id/name/frame refusal; no constructor/disposal side effects on the definition |
| Required input | Missing override fails clearly; supplied object reaches consumer by identity |
| Default precedence | None, falsey and chosen-instance defaults retain their established behavior |
| Matching | Discovery-only target distinguished from a resolvable implementation of the same frame |
| Graph | Node visibility, typed relationships, target navigation, revision/diff and impact behavior |
| Execution lanes | Root/nested, solo/generalized/many-only, positional/named/deep overrides as supported |
| Revalidation/cache | Pre/post-conjure registration, invalidation, cache cold/warm parity, restored executors |
| Persistence | Capture/checkpoint/flush/load/graft preserves mode, edges, selected versions, translations |
| Lifecycle | Registration removal, index selection/transfer, retained history, no accidental instance ownership |

Prefer a small public regression per contract, then broaden only for unresolved branches. Do not
mark expected new-feature failures as permanently acceptable xfails. No coverage result is claimed.

## Rollout / Adoption Plan
- Discovery and semantic decisions first; public API spelling remains provisional until then.
- Add the mode without changing the behavior of callers that omit it.
- Use the existing cache/record versioning mechanisms for incompatible artifacts.
- Deliver runtime, graph, and persistence compatibility together before claiming feature completion.
- Public examples, generated hardcopies, and build-runner outputs accompany the accepted implementation.

## Open Questions
S1-S3 settled native mode/identity, initial admission, Phase-3 resolved classification and the selector/
default/Optional/collection/descriptor policy. Read the discovery and implementation tasks for those
decisions. Existing version rules remain; body-only edits do not automatically mint new versions.

- Which additional notch/transfer, nested and receiving-policy matrices are required for final qualification?
- How is supplied-value type compatibility checked for ABCs and non-runtime-checkable Protocols?
- Which graph edges are inferred, declared, version-pinned, and relevant to invalidation versus impact only?
- Which Nexus tool and access-control surfaces expose independent registration discovery and revisions?
- How are older crystal/cache records interpreted, and how does restore rebuild graph-only registrations?
- How are externally supplied live references represented in graph observations without claiming ownership?

## Decision Log
- 2026-09-19: Owner selected modifier placement on bind and bind_inactive, defaulting to resolvable.
  Working spelling is resolvable: bool = True; no separate registration framework is the default plan.
- 2026-09-19: Owner requested this epic after approving the direction for deeper discussion.
- Reuse registration with an explicit non-resolution mode; no mandatory application inheritance.
- Keep graph relationships and versionability even when no executable dependency edge is produced.
- Required supplied inputs retain real defaults and are checked at construction.
- 2026-09-19: Plan an explicit resolved caller-supplied category; preserve original Phase-1 declarations.
  This supersedes earlier PLAIN lowering. User requested real stories and reading requirements for all steps.
- Direct target resolution should refuse. Resolvable implementations under a shared spellframe remain distinct.
- Subsequent owner continuation authorized S2 implementation; no release/version bump or owned-object redesign.

## Source Read Map and Re-Entry Order
Read documents through current indexes, then source methods. These are scoped routes, not a request
to preload entire subsystems. Recheck line positions/hashes after source or generated-doc changes.

Every story has its own Required Reading Before Work section. That section is required when entering
that story; do not preload all seven readsets. Reuse source already read in the same uninterrupted
session when it is unchanged. After compaction, complete ContextCompass REONBOARD, then read this epic,
the active story and task, and their required source context. Read implementation in full before edits;
test paths are starting points, not a claim that existing tests cover this new feature.

1. Orientation: `system_docs/src_architecture.md`, `src_architecture_index.md`, `src_components_index.md`.
   Component topics: Binding Pipeline; DI Descriptors and Contract Sockets; SpellCompiler and Validation;
   AR Runtime Surface; Nexus Descriptor And ACL Managers; Crystallizer Root; MutationResearch Root/ResearchSet.
2. Registration and target policy:
   `src/melder/aether/spellbook/spellbook.py` — bind, bind_inactive, conjure, registry/index transitions.
   `src/melder/aether/spellbook/bind/bind.py` — admission, profiles, fingerprints, Spell construction.
   `src/melder/aether/spellbook/spell.py` — immutable metadata, owner references, compiler lifecycle.
   `src/melder/aether/spellbook/bind/spell_index.py` — membership and selected identity.
   `src/melder/aether/spellbook/resolution_style_matrix.py` — binding-family restrictions.
3. Socket and compiler boundary:
   `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py`
   `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py`
   `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py`
   `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
   `src/melder/aether/spellbook/spellbook_creation_system.py` — compilation scheduling/admission.
   Phase 4/5/6 validation, artifact processing and codegen planning: follow verified graph/source callers.
4. Execution and override doors:
   `src/melder/aether/conduit/conduit.py` and `src/melder/aether/conduit/meld/meld.py`.
   `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/`
   Generalized and many-only strategy peers, cache hydration, and override-targeting maps.
5. Nexus and research:
   `src/melder/nexus/frame_descriptor_manager.py` and `src/melder/nexus/nexus.py`.
   `src/melder/nexus/rift/command_system/codegen_command_system.py` — research and materialization verbs.
   `src/melder/mutation_research/mutation_research.py` — custody reads, parts/diffs, synthesis, world entry.
   `src/melder/mutation_research/research_set/research_set.py` — identity, ancestry and graph organization.
6. Persistence and regeneration:
   `src/melder/crystallizer/crystals/spell_crystal.py` and `spell_index_crystal.py` in the same directory.
   `src/melder/crystallizer/crystal_loader_system/restore_engine.py` and `graft_runner.py`.
   `src/melder/crystallizer/persistence/persistence_system.py` and `persistence_profile.py`.
   Existing cache metadata/version checks and the source/build asset runners; do not invent replacements.
7. Existing tests to consult, not claimed as feature coverage:
   `tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py`
   `tests/component/melder/spellbook/test_spellbook_component_spell.py`
   `tests/component/melder/spellbook/spell_crafter/topology/test_spellbook_component_spell_local_topology.py`
   `tests/component/melder/aether/conduit/test_conduit_component_meld_overrides_deep.py`
   `tests/integration/melder/mutation_research/test_research_room_commands_integration.py`
   `tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: story closure according to each future artifact's declared disposition.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: registration mode, Nexus graph, supplied inputs, history and persistence.
- IF_UNKNOWN: none; scoped reread routes and evidence are in this epic and its child tickets.

## Notes
- DATETIME: 2026-09-19T16:34:27Z
  TYPE: DECISION
  CLAIM: Owner requested a dedicated epic for the accepted discussion direction. Registration remains
    the proposed entry; discoverable/unresolvable behavior must preserve the connected Nexus graph,
    required supplied inputs, default precedence, history and restore. First proceed with S1 discovery.
  EVIDENCE:
  - tickets/tasks/2026-09-19_understand_nexus_crystallizer_spellbook_task.md:273-478
  IMPACT: Later sessions have one program record instead of reconstructing the design from chat.
  NEXT: Trace registration-mode ownership and Phase-3 selected-target handling in the first S1 task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:43:07Z
  TYPE: FACT
  CLAIM: The epic, S1 story, and first discovery task are created and cross-linked. Referenced full
    file paths resolve, the active board routes to the S1 task, and the predecessor links to this
    program. New ticket contents were reread; tracked documentation passes diff whitespace checks.
  EVIDENCE:
  - tickets/stories/2026-09-19_discoverable_registration_contract_discovery_story.md:1-60
  - tickets/tasks/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md:1-50
  - attention_board.md:80-90
  IMPACT: Planning is durable and ready for the next source-discovery pass. No production code,
    feature test, generated package asset, release, or existing-object redesign changed.
  NEXT: Start the first S1 task at Bind._bind_logic and Spell/SpellIndex mode ownership.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-19T17:01:48Z
  TYPE: FACT
  CLAIM: S1's first task traced the default-True modifier through both entry points, Bind identity,
    Spell/SpellIndex, Phase-3 candidates, structural scheduling, Phase-4 cycles, and concrete meld doors.
    The recommendation is per-Spell bind-time policy with no extra public lifecycle enum or registry.
    Resolved socket metadata and full downstream compatibility remain design/qualification work.
  EVIDENCE:
  - tickets/tasks/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md:74-162
  IMPACT: Public simplicity is preserved while the actual compiler and persistence work stays visible.
  NEXT: Settle caller-supplied socket policy before starting implementation stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T17:25:45Z
  TYPE: PLAN
  CLAIM: Owner requested all implementation stories and per-story reading requirements before
    compaction. Split the former combined socket/runtime work so registration, compiler semantics,
    runtime execution, Nexus/history, persistence, and qualification each have one bounded story.
    Preserve the selected caller-supplied category direction and a ready S1 continuation task.
  EVIDENCE:
  - tickets/tasks/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md:355-392
  IMPACT: A new agent can resume from the epic/story/task hierarchy without reconstructing chat.
  NEXT: Create S2-S7 story files with dependencies, source/test read maps, and acceptance contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T17:45:45Z
  TYPE: FACT
  CLAIM: All seven story records now exist. Each has required reading, dependencies, bounded tasks,
    validation, acceptance and handoff sections. Full referenced file paths were checked (129 resolve),
    and the new story/task contents were reread. S1 now routes to the ready resolved-socket contract task.
    The explicit caller-supplied category replaces the earlier PLAIN preference throughout active plans.
  EVIDENCE:
  - tickets/stories/2026-09-19_discoverable_registration_contract_discovery_story.md:62-114
  - tickets/stories/2026-09-19_discoverable_registration_modifier_story.md:61-105
  - tickets/stories/2026-09-19_caller_supplied_socket_compiler_story.md:65-119
  - tickets/stories/2026-09-19_discoverable_resolution_runtime_story.md:64-115
  - tickets/stories/2026-09-19_discoverable_nexus_graph_and_history_story.md:66-120
  - tickets/stories/2026-09-19_discoverable_registration_persistence_story.md:68-125
  - tickets/stories/2026-09-19_discoverable_registration_qualification_story.md:63-120
  - tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md:13-85
  IMPACT: The complete plan and a precise re-entry route are durable in ContextCompass. This pass
    changed planning/coordination files only; no runtime tests, feature code, assets or release were run.
  NEXT: After required re-entry, read the ready S1 task and begin with required-hole validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:36:34Z
  TYPE: FACT
  CLAIM: S1's second task is review-ready with a concrete caller-supplied schema, propagation map
    and regression design. The source supports reusing existing socket addressing and injection/plan
    ownership, but declaration-based validation, executable target expansion and solo code generation
    need explicit adaptation. S3/S4 reading requirements link this evidence. Remaining S1 matching,
    descriptor/collection and version identity choices stay visible; no feature code was changed.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md:89-215
  IMPACT: The program can review a specific contract instead of revisiting PLAIN versus DI abstractions.
  NEXT: Discuss the proposed socket schema and settle provider-versus-definition selection in S1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:45:34Z
  TYPE: DECISION
  CLAIM: Owner named the internal required-input category OVERRIDE_REQUIRED and approved continuing.
    Preserve ordinary defaults and the connected graph; proceed with provider-versus-definition
    selection in the new focused S1 task. Existing notes with CALLER_SUPPLIED are historical.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md:89-116
  IMPACT: The category name/core meaning is settled; S1 selection and identity work remains explicit.
  NEXT: Trace existing root lookup versus Phase-3 candidate selection in the new S1 task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:05:38Z
  TYPE: FACT
  CLAIM: Selection recommendations are now source-backed and separately recorded. Root meld remains
    exact lookup; implicit annotation selection can prefer resolvable providers; explicit selectors
    retain their intended target/cardinality. False definitions remain active graph registrations
    under normal uniqueness. Admission/fingerprint/custody identity is the next independent S1 unit.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_discoverable_registration_selection_task.md:84-210
  IMPACT: The remaining discovery is explicit rather than conflated with the selected OVERRIDE_REQUIRED name.
  NEXT: Complete the admission/identity task before creating implementation patch contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T19:25:38Z
  TYPE: DECISION
  CLAIM: Owner explicitly retained existing version rules. No automatic body-only source-version
    identity is added. S1 admission/fingerprint/custody/research trace is complete for this boundary;
    recommend unchanged v4-binding identities for omitted/True and a distinct False prefix.
    S2 is now staged as a concrete registration task; patch contracts and regressions come first.
  EVIDENCE:
  - tickets/tasks/2026-09-19_define_non_resolvable_admission_identity_task.md:77-174
  IMPACT: The feature extends resolution capability and graph access without redesigning version identity.
  NEXT: Execute tickets/tasks/2026-09-19_implement_resolvable_registration_modifier_task.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-19T20:05:28Z
  TYPE: FACT
  CLAIM: S2 registration foundation is implemented and review-ready: immutable native capability,
    compatible True identities, distinct False domain, conditional Protocol admission and both
    binding facades. All 42 new cases and 1845 focused compatibility cases pass. Source/LLM assets
    regenerated and checks pass. This advances registration only; no runtime/graph/replay completion.
  EVIDENCE:
  - tickets/tasks/2026-09-19_implement_resolvable_registration_modifier_task.md
  IMPACT: S3 now has a concrete per-Spell bool to consume. S4 still must block all resolution doors;
    S5 must expose connected graph semantics; S6 must explicitly persist/replay False safely.
  NEXT: Begin S3 compiler implementation from the existing source-read map and OVERRIDE_REQUIRED contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:38:40Z
  TYPE: FACT
  CLAIM: S3 compiler delivery is review-ready: OVERRIDE_REQUIRED and descriptive target IDs survive
    compilation without construction edges; False roots are excluded from executable plans; both
    planner variants carry required-input rows. Existing revalidation machinery handles the tested
    direct-consumer selector changes. 2098 distinct focused tests and source/LLM asset checks pass.
  EVIDENCE:
  - tickets/tasks/2026-09-19_implement_override_required_compiler_task.md
  - artifacts/override_required_compiler_20260919/validation.md:1-72
  IMPACT: S4 can implement concrete runtime enforcement. S5/S6 still need connected Nexus graph
    and safe durable replay; S7 qualifies the complete feature. No release is authorized by this result.
  NEXT: Open S4's runtime task using the delivered schema and existing version/ownership decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user.
- [ ] Acceptance criteria confirmed by user.
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Keep program decisions and cross-story dependencies here; tactical findings stay in child tasks.
- Preserve append-only decisions and explicit UNKNOWNs; every pass ends with one next source question.

## Context / Handoff Summary
S1 source discovery is in review; S2 registration and S3 compiler are implemented and review-ready.
S4 runtime enforcement is ready to begin; S5-S7 remain required. Read the S3 child task and validation
artifact for exact code, 2098 distinct passing cases, build checks and remaining limits.

Current native contract: bind/bind_inactive default resolvable=True; each Spell stores its own immutable
capability. True retains existing version fingerprints; False uses v4-binding-non-resolvable. Application
Protocol definitions are admitted only with False. Existing naming, uniqueness, ownership and lifetime
rules remain. Source assets and LLM source/tests corpora are regenerated and verified.

S3 delivers SocketKind.OVERRIDE_REQUIRED, descriptive references separate from executable targets,
construction-root exclusion, required-input rows across both planners and injection exports, plus
existing selector/structural/resolution revalidation integration. The remaining runtime must consume
required_override_params via live CodegenCreationSchemaHelpers, emitted executors and hydration.

Next: S4 direct/reuse/nested/fast/scoped/cached refusal and actual required-input enforcement. S5
exposes connected Nexus graph/history; S6 persists/replays policy; S7 qualifies the complete feature.
Compiler metadata does not establish runtime safety and False is not yet preserved by crystal replay.
Do not ship this partial feature. No owned-object redesign, named-lesser work or version bump occurred.

After compaction: REONBOARD, then the S3 handoff and S4 story required-reading routes. User selected
OVERRIDE_REQUIRED and existing version rules; do not reopen source-body versioning.
