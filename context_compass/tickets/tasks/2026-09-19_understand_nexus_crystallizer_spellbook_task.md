# Task: Understand Nexus, Crystallizer, and Spellbook ownership and interaction

## Metadata
- Task ID: TASK-2026-09-19-understand-nexus-crystallizer-spellbook
- Story: none (standalone discovery)
- Successor Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Status: review
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-19T15:07:35Z
- Updated: 2026-09-19T16:25:38Z

## Objective
Build a high-level but source-grounded understanding of Nexus, Crystallizer, and Spellbook,
starting with the relevant src_components sections and tracing their principal connections.

## Problem / Context
The owner requests deeper orientation in these three systems after onboarding. Architecture and
the component index are already read; this task narrows into component contracts and live source.
MRP alignment: establish accurate boundaries and ownership before discussing further changes.

## Ticket Contract
- ENTRY_GATE: Completed re-onboarding, existing certification, and this ticket routed on the board.
- EXECUTION_BOUNDARY: Read the named systems and their immediate boot, frame, recording, restore,
  and MutationResearch source/versioning collaborators; edit only this record and coordination boards.
- DEPENDENCIES: Current architecture and component indexes; source remains behavior authority.
- EXIT_GATE: Explain responsibilities, lifecycles, cross-system flows, and unresolved limits with
  source references; leave discovery in review for owner acceptance.
- FAILURE_ESCALATION: Record contradictions or inaccessible evidence; do not infer missing behavior.

## Scope Boundaries
- In scope: Nexus/Rift and frame access, Spellbook bind/conjure and configuration, Crystallizer
  emission/persistence/restore, ownership and cleanup relationships between these systems.
  Owner follow-up: investigate agent visibility/versioning of unbound abstract bases and internal
  code without admitting them to runtime resolution; discuss architectural options only.
  Latest follow-up: reuse registration with an unresolvable/discoverable flag; inspect compiler
  parameter classification, graph/socket preservation, and required override behavior.
- Out of scope: Runtime changes, new features, benchmarks, full-suite testing, or resuming backlog work.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: PLAIN signature/topology behavior and the solo invocation helpers are traced;
  proposed discoverable-registration semantics are ready for discussion, not implementation.

## Steps / Checklist
- [x] Reuse completed onboarding orientation and verify both document indexes are current.
- [x] Read indexed component contracts for the three systems and their principal connecting seams.
- [x] Trace relevant source methods and callers to verify the main interactions and ownership.
- [x] Record each completed investigation unit before continuing into the next.
- [x] Prepare a concise explanation with clear evidence boundaries.
- [x] Investigate the owner's unbound-source question and compare architectural directions.

## Deliverables
- This ticket's durable findings and reread pointers.
- A high-level explanation grounded in the actual ownership and execution paths.

## Files / Paths Impacted
- context_compass/tickets/tasks/2026-09-19_understand_nexus_crystallizer_spellbook_task.md
- context_compass/attention_board.md
- context_compass/mailbox_board.md

## Validation
- Both authored-document index checks passed before taking component slices.
- Tests: Not run. This is discovery with no runtime changes.
- Source tracing is inspection, not an execution or test claim.

## Risks / Rollback Notes
- Some component prose may lag source. Record meaningful disagreements rather than normalizing them.
- Keep the readset centered on the named systems; source depth should answer concrete questions.

## Applicable Anti-Patterns
- [x] No behavior claims supported only by component prose or search hits.
- [x] No reactivation of parked ownership proposals.
- [x] No runtime edits or manufactured validation claims.
- [ ] No closure without owner acceptance and board synchronization.

## Done Checklist
- [x] Component and source investigation complete.
- [x] Findings and caveats recorded with evidence ranges.
- [x] Explanation prepared and validation limitations stated.
- [ ] Acceptance criteria reviewed with the owner.
- [x] Board synchronized to review or accepted closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Nexus, Crystallizer, Spellbook, frame ownership, recording and restore.
- IF_UNKNOWN: none

## Noting Behavior
- Record completed read units with evidence, impact, and one next action.
- Keep notes append-only and preserve UNKNOWN for behavior not traced in source.

## Notes
- DATETIME: 2026-09-19T15:07:35Z
  TYPE: PLAN
  CLAIM: Follow the owner's requested document-first orientation through the three systems.
    Source architecture has been read during re-onboarding; both authored indexes now pass checks.
  EVIDENCE:
  - context_compass/system_docs/src_architecture_index.md:10-19
  - context_compass/system_docs/src_components_index.md:10-19
  IMPACT: Component ranges can be used directly without searching or loading the entire document.
  NEXT: Read Spellbook, Nexus, and Crystallizer component entries and identify source seams to trace.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

Read-unit note (component contracts):
- DATETIME: 2026-09-19T15:09:13Z
  TYPE: FACT
  CLAIM: The component map assigns runtime registration/conjure to Spellbook, AR access and
    descriptor/ACL policy to Nexus, and recording/assets/replay to three Crystallizer children.
    These are documented responsibilities; source verification is the next unit. The crystallizer
    entry claims a live-world catch-up, while architecture states only Aether root catch-up.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:339-629
  - context_compass/system_docs/src_components.md:731-831
  - context_compass/system_docs/src_components.md:1064-1317
  - context_compass/system_docs/src_components.md:1318-1766
  - context_compass/system_docs/src_components.md:1847-2070
  - context_compass/system_docs/src_architecture.md:987-1001
  IMPACT: Keep graph ownership, permitted views/actions, and structural replay distinct.
    Activation catch-up remains UNKNOWN until source settles the conflicting prose.
  NEXT: Trace Nexus lifecycle, frame creation, descriptor publication, and Rift attachment in source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T15:10:27Z
  TYPE: FACT
  CLAIM: Nexus constructs descriptor/ACL/frame managers and Rift gates, while each Rift owns one
    configured room and its projection/link state. Bare Rift creation attaches no frames. Explicit
    managed-frame creation first reserves an Aether frame, binds its posture, then constructs a
    Spellbook and conjures the rooted Conduit. Frame-link attachment is a separate operation with
    runtime eligibility, topology, descriptor, same-name ACL, and budget checks before projections.
  EVIDENCE:
  - src/melder/nexus/nexus.py:156-379
  - src/melder/nexus/nexus.py:803-1161
  - src/melder/nexus/nexus_frame_manager.py:278-409
  - src/melder/nexus/nexus_frame_manager.py:446-697
  - src/melder/nexus/nexus_frame_manager.py:699-821
  - src/melder/nexus/nexus_frame_manager.py:958-1076
  - src/melder/nexus/rift/rift.py:144-313
  - src/melder/nexus/rift/rift.py:447-681
  - src/melder/nexus/rift/rift.py:970-1089
  IMPACT: A Rift workspace and a runtime frame are separate lifecycles. Nexus's creation path
    reuses Spellbook/conjure but also explicitly creates and postures the underlying frame first.
  NEXT: Trace descriptor publication/projection construction and the Spellbook lifecycle seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T15:11:40Z
  TYPE: FACT
  CLAIM: Spellbook publishes frame/root-conduit/spell records after conjure and incremental spell
    records after later binds, gated by the frame's rift_enabled posture. Descriptor publication
    accepts normal, lesser, and pooled_lesser conduits without a name requirement. Nexus builds
    separate view/command/codegen projections from descriptors plus selected ACL configurations.
    ACL refresh optionally disables impacted Rift gates, drains activity, replaces projections,
    and reopens gates. Codegen attachment additionally requires dynamic and AI-native posture.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5883-5974
  - src/melder/nexus/frame_descriptor_manager.py:177-414
  - src/melder/nexus/nexus.py:2236-2396
  - src/melder/nexus/nexus.py:2445-2506
  - src/melder/nexus/nexus.py:2628-2727
  - src/melder/nexus/nexus.py:3060-3123
  IMPACT: Nexus descriptors are a live access surface, separate from ConduitCloud naming and
    Crystallizer's persistent structural record. Visibility and permission are separate decisions.
  NEXT: Trace Spellbook construction, bind, configuration freeze, conjure, and structural emission.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T15:12:55Z
  TYPE: FACT
  CLAIM: Spellbook holds active/inactive owned and borrowed maps, references frame-owned posture
    and control state, and borrows the hosted Nexus/Crystallizer/MR roots. Bind registers the spell,
    stages structural work, emits spell custody/index membership when recording in a dynamic frame,
    and publishes incrementally to Nexus after conjure. Conjure runs inside a transaction, settles
    or inherits frame mode, freezes book config, compiles/resolves (or loads eligible cached lanes),
    constructs one Conduit, wires it, and publishes Nexus state. Recorded dynamic worlds require
    finalized book configuration before their first bind. Book twins emit with conjure identity;
    normal dynamic conduits emit their own twins, while lesser conduits currently skip emission.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:217-353
  - src/melder/aether/spellbook/spellbook.py:5026-5290
  - src/melder/aether/spellbook/spellbook.py:5418-5567
  - src/melder/aether/spellbook/spellbook.py:5709-5881
  - src/melder/aether/spellbook/spellbook.py:6333-6570
  - src/melder/aether/spellbook/spellbook_creation_system.py:202-349
  - src/melder/aether/spellbook/spellbook_creation_system.py:955-1018
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:265-403
  - src/melder/aether/conduit/conduit.py:421-466
  - src/melder/aether/aether.py:136-344
  IMPACT: Nexus descriptor publication and Crystallizer emission share runtime events but have
    different admission rules. Aether constructs and ultimately tears down the hosted roots;
    Spellbook does not own those global services. Compiler cache replay is separate from world replay.
  NEXT: Read Crystallizer activation and its persistence/asset/loader boundaries, then verify replay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T15:13:51Z
  TYPE: FACT
  CLAIM: Crystallizer owns three distinct children: the in-memory persistence record, asset storage,
    and the loader. Activation requires an already-activated CrystallizerConfiguration, installs
    checkpoint/restore policy, emits its own policy, and catches up only the configured Aether root.
    There is no live-world walk in activation. Runtime emissions feed the active named profile;
    checkpoints seal journal windows into the in-memory ledger, and flush ships those values to
    local cache plus an optional external manager. Automatic checkpointing is emission-driven.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:175-332
  - src/melder/crystallizer/crystallizer.py:568-826
  - src/melder/crystallizer/crystallizer.py:1082-1141
  - src/melder/crystallizer/crystallizer.py:1522-1620
  - src/melder/crystallizer/crystallizer.py:1842-1886
  - src/melder/crystallizer/persistence/persistence_system.py:92-297
  - src/melder/crystallizer/persistence/persistence_system.py:939-1010
  - src/melder/crystallizer/asset_management/asset_management_system.py:110-283
  IMPACT: Recording, checkpoint sealing, durability, and replay are separate operations. The
    src_components live-world catch-up bullet is stale; activation order matters for capture.
  NEXT: Trace loader admission and replay of Nexus, frames, Spellbooks, bindings, and Conduits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T15:15:14Z
  TYPE: FACT
  CLAIM: World replay claims Aether load authority, detaches/folds the checkpoint chain, refuses
    preflight blockers, and drives ordered runtime reconstruction. Per-book replay reloads/finalizes
    config, binds hydratable targets, conjures the recorded root, then parks/selects index members;
    recorded identities map to new live IDs. Nexus replay restores root configuration/lifecycle.
    NexusCrystal explicitly excludes live Rifts, rooms, workstations, and projections. SpellCrystal
    retains bind metadata and module analysis, not the live Spell or application object reference;
    instance/method/lambda/callable-object targets are replay_required and yield reported shortfalls.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py:271-411
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:165-196
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:335-431
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:649-871
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1490-1712
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1739-2014
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2456-2514
  - src/melder/crystallizer/crystals/nexus_crystal.py:1-188
  - src/melder/crystallizer/crystals/spell_crystal.py:143-342
  IMPACT: Restore rebuilds the recorded structure through normal runtime entry points. It does
    not restore arbitrary live object memory or Nexus session state. This is orientation only;
    no deferred existing-object redesign is being reopened.
  NEXT: Verify the Nexus room command/codegen path, then summarize the three-system model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T15:16:51Z
  TYPE: FACT
  CLAIM: A RiftSpace owns its viewer, workstation, command, memory, and event systems; codegen rooms
    additionally own CodegenSystem. Commands enter/release RiftGate tickets, and codegen validates
    before namespace construction and compile/execute. materialize_codegen is an explicit separate
    operation: validate, create SyntheticModule, materialize with import support, and report exports.
    It does not bind that target; subsequent Spellbook.bind owns the recorded custody transition.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:1767-1846
  - src/melder/nexus/rift/rift_space/rift_space.py:155-323
  - src/melder/nexus/rift/rift_space/codegen_rift_space.py:81-175
  - src/melder/nexus/rift/command_system/command_system.py:1010-1154
  - src/melder/nexus/rift/command_system/codegen_command_system.py:601-889
  - src/melder/nexus/rift/codegen_system/codegen_system.py:115-176
  - src/melder/nexus/rift/codegen_system/codegen_system.py:260-402
  - src/melder/aether/spellbook/spellbook.py:5245-5268
  IMPACT: The three systems meet through ordinary runtime entry points and structural emissions.
    Running generated code, materializing an importable module, binding it, and recording it are
    distinct acts. No claim of sandbox completeness or exhaustive command-policy audit is made.
  NEXT: Discuss the requested three-system explanation with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T15:19:33Z
  TYPE: PLAN
  CLAIM: Owner extends the discussion to source definitions that should never be resolvable spells.
    Check existing module/part custody and MutationResearch/Nexus access before defining the gap.
    Potential directions remain proposals, not implementation decisions or a revived object epic.
  EVIDENCE:
  - context_compass/system_docs/src_components_index.md:88-92
  - src/melder/crystallizer/crystals/spell_crystal.py:143-342
  IMPACT: Distinguish visibility of unbound code inside an existing spell's module world from an
    independently addressable and versioned source artifact.
  NEXT: Read MutationResearch component slices and its module/part/research registration methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T15:22:10Z
  TYPE: FACT
  CLAIM: Existing Nexus research_module/research_part/research_parts commands delegate to MR reads
    taking a spell_id. Those reads fetch a SpellCrystal, then inspect module text and class/function
    parts across that crystal's module_targets; groups fan out to member spell IDs. Source resolves
    retained synthetic/user text first, then live disk with a drift marker. The referenced class
    itself need not be separately selected as a spell for part_view to search its containing source.
    ResearchSet.register_spell records identity/ancestry but does not create source custody; a
    declaration alone cannot satisfy the reads' get_spell_crystal lookup.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:4447-4708
  - src/melder/nexus/rift/command_system/codegen_command_system.py:1352-1472
  - src/melder/mutation_research/mutation_research.py:1819-2050
  - src/melder/mutation_research/mutation_research.py:2295-2601
  - src/melder/mutation_research/research_set/research_set.py:1090-1224
  IMPACT: The gap is not total invisibility of every unbound definition. The source tools have a
    spell-custody anchor; independent unbound-source intake/addressing/versioning is the design issue.
  NEXT: Check part extraction, recorded diffs, and candidate synthesis limits before recommending options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T15:24:14Z
  TYPE: FACT
  CLAIM: Part extraction enumerates top-level AST ClassDef/function definitions without requiring
    abstract or helper classes to be separately bound. Historical part diffs resolve retained
    crystal source only, while present-tense reads may fall back to live disk. Raw candidate
    preview can analyze source with no spell ID and produces no record. Existing synthesis is
    anchored to two spell IDs and composes their root-module texts. These are reusable facilities,
    but none of these paths supplies independent durable source custody on registration alone.
  EVIDENCE:
  - src/melder/mutation_research/synthesis/structural_synthesizer.py:242-436
  - src/melder/mutation_research/mutation_research.py:1683-1746
  - src/melder/mutation_research/mutation_research.py:2603-2784
  - src/melder/mutation_research/mutation_research.py:2800-2965
  - src/melder/mutation_research/mutation_research.py:2967-3091
  IMPACT: The practical gap is independent source intake, discovery, history, and revision/promotion
    for code outside spell-root custody. It is broader than an abstract-class constructor restriction.
  NEXT: Present bounded architectural options with module context and explicit runtime adoption.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T15:24:14Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Proposed direction, not approved implementation: expose selected modules/packages as
    source artifacts through Nexus without admitting their definitions into bind/meld resolution.
    Objective: agents can discover, inspect, revise, compare, and version abstract bases/helpers.
    Constraints: no automatic construction/resolution; preserve Python module/import context;
    separate saving a candidate from applying it to the live graph.
    Known facts: module/part source analysis, retained diffs, candidate preview, synthetic modules,
    and research ancestry already exist, but the durable reads traced here require SpellCrystal IDs.
    Unknowns: exact intake owner/API, source identity/migration schema, ACL integration, dependency
    pinning, and physical/synthetic publication policy require a dedicated design if selected.
    Options: (1) extend spell-anchored module browsing, smallest reach but keeps standalone source
    dependent on a bound anchor; (2) first-class source/module artifacts with class/function selectors,
    reusing analysis/storage/research facilities while runtime binding remains explicit; (3) introduce
    non-resolvable Spell variants, sharing identity machinery but broadening compiler/lookup contracts.
    Recommendation: option 2, with module revisions as reconstructible context and addressable class
    parts for agent work. Preserve source dependency/inheritance relationships so one changed base
    can identify affected concrete consumers. New source versions should not silently mutate existing
    class identities/instances; affected consumers need a deliberate validation/adoption step.
    Decision pending: whether independent source artifacts are the desired direction at all.
  EVIDENCE:
  - src/melder/mutation_research/mutation_research.py:2295-2601
  - src/melder/mutation_research/mutation_research.py:2800-3091
  - src/melder/nexus/rift/command_system/codegen_command_system.py:740-889
  - src/melder/crystallizer/crystals/spell_crystal.py:143-342
  IMPACT: Makes agent-addressable code a broader set than resolvable runtime providers, while
    keeping abstract/helper definitions out of object lifetime and creation semantics.
  NEXT: Discuss these proposals with the owner; do not implement or open a redesign epic yet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T15:54:37Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner corrected the proposal: source-artifact exposure alone is insufficient. The graph
    network must manifest properly in Nexus, be versionable, and allow a user or agent to register
    an item and define its role without intruding on application architecture or requiring resolution.
    The previous module-catalogue recommendation underspecified this requirement and is superseded.
  EVIDENCE: Owner directive recorded verbatim: "I want the graph network to properly manifest in
    nexus, and be versionable, but not be intrusive in the architecture, so the user or agent can
    register it and define it as something".
  IMPACT: The design target is first-class typed graph membership with relationships and history.
    Source custody supports that graph; it is not the entire proposed product surface.
  NEXT: Discuss additive graph registration and the distinction between node role and runtime binding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T15:54:37Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Revised proposal for discussion: Nexus exposes an integrated graph containing existing
    spell-backed runtime nodes and explicitly registered definition nodes. Register a real target
    or source reference with a declared role, identity, revision, and typed relationships. A
    definition can be an abstract base, protocol, helper, function, or module without entering DI
    lookup or receiving existence/creation/disposal semantics. Existing bindings keep their runtime
    identity and behavior; integration is additive rather than a new compulsory application model.
    Relationships such as inherits, implements, uses, contains, and injects retain distinct meanings;
    only runtime-resolution edges participate in the executable dependency graph. Nexus tools operate
    on graph node/revision identities for navigation, inspection, candidate revision and comparison.
    Versioned graph selections preserve both node revisions and their relationships. Registering or
    saving a definition revision does not execute it or silently replace a live dependency.
    Exact role vocabulary, identity owner, persistence schema, inferred-versus-declared edge policy,
    access rules, and runtime adoption protocol remain open. No implementation is approved.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor_manager.py:259-414
  - src/melder/mutation_research/mutation_research.py:2295-2601
  - src/melder/mutation_research/research_set/research_set.py:1090-1224
  IMPACT: Registration into the agent-visible architectural graph is broader than registration for
    runtime resolution. Application classes can remain ordinary Python while gaining graph identity.
  NEXT: Confirm the conceptual boundary in discussion before designing concrete registration APIs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:20:53Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner now proposes reusing registration with an unresolvable/discoverable flag. Consumer
    inputs involving those definitions would require overrides, using PLAIN-like sockets with
    deferred satisfaction analogous in intent to SpellContract. This is discussion, not permission
    to implement. Verify whether ordinary PLAIN preserves the desired graph information and whether
    missing required inputs are currently distinguished from defaults.
  EVIDENCE: Owner proposal in the current turn: "flag that they are unresolvable" and "use PLAIN
    in the socket" so consumers "require that they are overriden into it".
  IMPACT: Reuse of bind/Spell machinery is back on the table; the earlier independent-registration
    recommendation must not override this direction. Graph visibility must survive execution policy.
  NEXT: Read DI descriptor/compiler component entries and trace PLAIN/default/override handling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:23:57Z
  TYPE: FACT
  CLAIM: PLAIN is defined as caller/default-supplied with no DI contract. Phase 1 separately records
    annotation, default presence/value and optionality. Ordinary explicit defaults become PLAIN;
    a missing default is not equivalent to None. Phase 2 includes PLAIN as a real symbolic socket
    and retains its annotation. SpellContract is a different shape with a contract key and its own
    provider/link semantics. Reusing the PLAIN execution path does not require erasing the signature.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:630-730
  - context_compass/system_docs/src_components.md:2709-2871
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py:3-70
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:975-1226
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:49-184
  IMPACT: The proposed required supplied input is compatible in concept with PLAIN, but we must
    verify downstream target-edge and missing-value behavior before claiming implementation reuse.
  NEXT: Inspect Phase 3 target mapping and one complete plain/override construction lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T16:25:38Z
  TYPE: FACT
  CLAIM: Phase 3 keeps PLAIN in local topology but gives it no dependency key, concrete target IDs,
    or construction DAG edges. The solo no-overrides executor calls the target with no arguments;
    its override helper forwards supplied positional/keyword arguments and otherwise does the same.
    That helper has no dedicated missing-required-input diagnostic. These source observations do
    not establish public meld or nested generalized/cached-path behavior; no runtime test was run.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:545-898
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:7-240
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:7-309
  IMPACT: PLAIN already supports the argument-supply mechanism, but its ordinary topology does
    not express a link to a discoverable definition. Required-supply errors and descriptive graph
    relationships must be intentional parts of the new contract, not inferred from PLAIN alone.
  NEXT: Discuss the precise registration, consumer-supply, and graph-preservation rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:25:38Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Refined owner proposal for discussion: a registration may be discoverable/unresolvable,
    remaining visible and versioned while direct meld refuses and compilation does not treat it
    as a construction root. A consumer socket targeting that registration uses caller-supplied
    execution, potentially reusing PLAIN. With no default it requires an override when constructing
    the consumer; absence should report the consumer, parameter, and unresolvable target clearly.
    Ordinary explicit defaults keep their established precedence. Graph metadata must retain the
    consumer-to-definition relationship independently of the executable DAG. SpellContract is a
    useful analogy for deferred satisfaction, but its cross-conduit-provider gates are a different
    supply mechanism. Apply the flag to the selected registration; an abstract type used as a
    spellframe must not automatically disable separate resolvable implementations. The flag and
    its meaning must survive versioning and restore. All of this remains a proposal, not a patch.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1100-1226
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:49-184
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:545-898
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:279-309
  IMPACT: Reuses familiar registration/override concepts while maintaining the owner's versioned
    Nexus graph and preventing discovery-only entries from entering creation semantics.
  NEXT: Discuss this model with the owner; implementation and full-path regressions remain unapproved.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T16:41:59Z
  TYPE: DECISION
  CLAIM: Owner requested the dedicated epic. Its canonical program record now contains the accepted
    direction, unresolved semantics, source read map, validation matrix, and staged story sequence.
    S1 has one ready discovery task; later implementation stories are planned, not created or started.
    This task remains the evidence/history predecessor and has not been moved to completed.
  EVIDENCE:
  - tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md:1-35
  - tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md:1-29
  - tickets/tasks/completed/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md:1-27
  IMPACT: Active continuation moves to the dedicated discovery task through the epic/story hierarchy.
    No runtime behavior or new regression tests changed as part of epic creation.
  NEXT: Continue through the successor task's registration ownership and target-selection trace.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
PROGRAM ROUTE: continue through the discoverable-non-resolvable registrations epic and its S1 task:
`tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
`tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md`
`tickets/tasks/completed/2026-09-19_trace_discoverable_registration_compiler_boundary_task.md`
This predecessor retains the original source evidence and discussion. No feature code has been written.

Current proposal: reuse registration with a discoverable/unresolvable flag and required caller-supplied
consumer inputs, using PLAIN execution where appropriate. Existing PLAIN retains an annotated socket
but Phase 3 gives it no target link/construction edge. Preserve the Nexus descriptive relationship
separately, require overrides for required inputs at construction, honor explicit defaults, and keep
the selected-registration flag distinct from abstract spellframe matching. Direct meld should refuse;
conjure/restore/versioning must honor the same mode. These are discussion rules, not implemented code.
Only the solo helper was inspected for override invocation; nested/generalized/cache behavior is untested.

Latest owner direction supersedes the earlier source-catalogue framing: expose a properly connected,
versioned graph in Nexus whose nodes users/agents explicitly register and classify. Abstract bases
and helpers must be graph participants without being resolvable spells. Keep application architecture
nonintrusive and preserve ordinary Python definitions. The proposed additive graph-registration model
and typed-edge/runtime-participation distinction are discussion material, not an approved API/design.
See the final ALIGNMENT_CHECK and STRATEGY_DISCUSSION notes before continuing.

Orientation is complete and in review. No runtime code changed and no tests ran. The source reads
were scoped methods/call paths, not complete audits of every module or feature.

- Aether is the common host and frame owner. Nexus and Crystallizer are hosted roots that a
  Spellbook references; they are not independent runtime worlds.
- Spellbook owns registration, lookup/active membership, configuration, and compilation/conjure
  orchestration. Its frame owns posture/control state; one book conjures one root conduit.
- Nexus owns Rift access policy, descriptor and ACL managers, and managed-frame coordination.
  Each Rift owns one room, links to selected frames, and the current projections. Creating a Rift,
  creating a managed frame, and linking a frame are separate operations.
- Descriptor records advertise runtime structure. ACL-derived projections control views/commands/
  codegen. Runtime publication is not the same registry or admission rule as persisted recording.
- Crystallizer is the passive structural sink, split into record, asset storage, and loader.
  Bind/configuration/conduit lifecycle seams emit; checkpointing and flushing are separate.
- Restore rebuilds configurations, frames, books, bindings, conduits, and relationships through
  runtime verbs, translating identities and reporting unreplayable inputs. Nexus root configuration
  is recorded; live Rift sessions and arbitrary application-instance memory are outside these twins.
- Codegen's materialization path creates an importable synthetic module; a subsequent bind mints
  spell custody. Executing code alone does not perform that registration path.

Verified caveats for future discussion:
- The component map's live-world catch-up claim is stale: Crystallizer activation only catches up
  the configured Aether root. Recording must be active for subsequent structural emissions.
- Nexus descriptors accept lesser and pooled_lesser conduit states, while
  Conduit's crystallizer emission currently accepts only normal dynamic conduits.
- Instance/method/lambda/callable-object custody is marked replay_required; no ownership redesign
  was resumed. Further behavior claims must trace their own source paths rather than extrapolate.

Resume through the Notes evidence pointers for the specific question raised next. The owner has
not requested feature implementation or accepted closure of this discovery ticket.
