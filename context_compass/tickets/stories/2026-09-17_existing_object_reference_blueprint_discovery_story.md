# Story: Discover the reference and blueprint model for externally supplied objects

## Metadata
- Story ID: STORY-2026-09-17-existing-object-reference-blueprint-discovery
- Epic: EPIC-2026-09-13-existing-object-lifecycle-ownership
- Status: in_progress
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-17T21:22:19Z
- Updated: 2026-09-17T23:14:23Z

## Owner Intent: The Basic End State

The user binds an ACTUAL EXISTING OBJECT. Melder studies that reference and its type, reuses normal
object registration/graph/runtime machinery where appropriate, and explicitly disables construction.
Resolution/injection returns the supplied reference. Ownership transfer must carry the existing object
and its applicable lifecycle responsibility, not merely move registration metadata.

Owner's wording: "it should basically be treated like a normal object, but creation is disabled".
The concrete marker, metadata representation and changes to individual paths remain design work.
Studying the definition must not reintroduce constructor injection into an already initialized object.

Dependency failure requirement: retain ordinary consumer -> provider edges. If the selected resolution
cannot use the supplied object, refuse the meld with a specific error naming the dependent object,
provider and relevant parameter/path. The owner accepts invalidation/refusal through the existing
resolution structures. Construction disabled and current resolvability must remain distinct.

Current work proceeds ONE STAGE AT A TIME. The earlier idea of registering a definition before supplying
a value remains a possible later extension. It is not the starting input case and must not drive Stage 1.
This clarification takes precedence over the broader candidate options in the initial discovery artifact.

## Current Checkpoint

- CURRENT_STAGE: 1 - bind representation.
- STAGE_STATUS: in_progress; error/validity distinction traced, bind metadata comparison still pending.
- CURRENT_DISCUSSION: owner asks whether the supplied object's application state is the user's chosen
  baseline. Proposed map-and-use boundary is recorded in the Stage-1 task; do not treat it as implemented.
- CURRENT_TASK: tickets/tasks/2026-09-17_existing_object_bind_representation_design_task.md.
- NEXT_SINGLE_STEP: settle the supplied-state boundary, then compare bind metadata and construction-policy
  placement while preserving the dependency-aware failure contract recorded in the Stage-1 task.
- ALREADY_DONE: initial cross-system source map and nine characterization probes. Their evidence lives
  in the original trace task/artifact. No production implementation of this model has started.
- DO_NOT_RESTART: the full discovery sweep, basic A-to-B injection proof, generic DI comparison or the
  definition-first supply discussion after a compaction.
- RESUME: after required re-onboarding, read Owner Intent and this checkpoint, then CURRENT_TASK's
  latest Notes and reread order. Resume its recorded NEXT rather than infer a fresh scope from chat.

## Staged Discovery Sequence

The story owns this sequence. Each stage will have one focused task; only Stage 1 is opened now.
Later-stage constraints may be recorded while working Stage 1, but do not become parallel work.

| Stage | Question and relevant component reading | Deliverable / exit condition | State |
| --- | --- | --- | --- |
| 1. Bind representation | Binding Pipeline; Spellbook Core. How do we study the supplied object, reuse normal metadata and represent construction disabled? | Field/profile/classification comparison, explicit distinction and bounded proposal with any decisions required. | in_progress; linked task below |
| 2. Storage and admission | Creations and SpellSpace; Conduit Runtime; active/parked binding. Where is the supplied reference retained and when does each existing scope take responsibility? | Reference authority and transition map for pre/post-conjure, staging, selection and agreed lifetimes. | queued |
| 3. Graph and execution | SpellCompiler; Meld Resolution Runtime; relevant codegen/cache nodes. How does normal graph participation retrieve this value without constructing it? | Direct/nested/collection/override/cache path map preserving incoming dependency edges and no-construction behavior. | queued |
| 4. Ownership transitions | ConduitWard and Contracts; Ownership Transfer; Creations Disposal. How does transfer move the actual object and its responsibility? | Move/removal/rollback/borrower/alias/disposal contracts, including the accepted configuration flag and provider-artifact authority. | queued |
| 5. Recording and source | Crystallizer; SpellCrystal; SyntheticModule; affected version/introspection consumers. What structure and restrictions survive recording/replay? | File-backed/synthetic/live-only representation and replay obligations, preserving the external object/state boundary. | queued |
| 6. Integrated implementation readiness | Revisit only the changed component boundaries and test owners. Do the stage decisions compose into one coherent behavior? | Accepted patch contracts, regression matrix, ordered implementation slices and required docs/build-asset checks. | queued |

For each stage:
- Read the relevant src_components sections through the verified index, then the needed graph/source.
- Reuse initial findings; add probes only for concrete unanswered behavior questions.
- Record findings, evidence, decisions, remaining questions and one NEXT action in the active task.
- Finish the bounded design proposal before advancing; resolve an owner-dependent choice explicitly.
- Update this checkpoint and attention-board route together when moving stages. Do not mark a later
  stage complete because the initial broad discovery mentioned it.
- Production implementation remains separately authorized and must follow the accepted design scope.

## User Narrative
As Melder's owner, I want a source-backed design for registered external references and their
blueprints, so supplied objects can participate coherently in the DGR without Melder constructing them.

## Value / MRP Alignment
Preserve Melder's uniqueness, graph and ownership contracts. Determine how references, definition
records and actual supplied values interact before extending lifetime or version support. The result
must address compiler, runtime, transfer and persistence together rather than promise a local flag fix.

## Ticket Contract
- ENTRY_GATE: owner explicitly requests this discovery story and investigation; epic and task are linked.
- EXECUTION_BOUNDARY: source/document reads, isolated diagnostic probes and design artifacts only.
  Production changes, new public APIs, package installation and release work are not part of discovery.
- DEPENDENCIES: parent epic's primary proposal, accepted prior annotation/injection fixes, and retained
  Protocol/provider-artifact/identity evidence. Discovery is not dependent on an unresolved repair passing.
- EXIT_GATE: each required stage has its bounded deliverable and decisions recorded; the integrated
  design is reviewable before implementation. The initial broad report alone does not complete later stages.
- FAILURE_ESCALATION: separate unavailable source/material from undecided policy. Raise conflicting
  invariants explicitly; do not invent object reconstruction from a live reference alone.

## Requirements (Functional)
- Start with the value supplied at registration; retain definition-first supply as a later extension.
- Identify how binding classification, value presence and construction permission affect the normal pipeline.
- Preserve exact-reference dependency injection and a hard prohibition on creating the supplied target.
- Preserve a specific consumer/provider/parameter diagnostic when the active resolution cannot use the
  supplied value; publish failure in the appropriate existing resolution context rather than erase the edge.
- Define how the current uniqueness rules relate to definition/version, registration, value and scope.
- Investigate existing Conduit/SpellSpace storage and lifetime routing; do not invent request scopes.
- Identify how existing scope stores admit and release the bound reference, and how invalid missing state is reported.
- Determine what broader lifetime/version labels can mean without creating a new physical object.
- Trace active/parked admission, transfer, discard, rollback, shared visibility and cleanup ownership.
- Trace SpellCrystal capture, SyntheticModule custody and replay for file-backed, synthetic and live-only inputs.
- Establish where the provider-artifact failure intersects the ownership model and preserve its regression contract.
- Include Protocol admission and the accepted configured-disposal option in the complete design boundary.

## Requirements (Non-Functional)
- Separate source facts, measured results, hypotheses and owner decisions.
- No runtime identity/custody assumptions based solely on graph/docs or conventional DI behavior.
- Keep no-new-creation enforcement explicit across direct, compiled, overridden and restored paths.
- Consider concurrent scope use and lifetime release, with no unmeasured performance claims.
- Record exact reread pointers, probe inputs, output and limits so another session can resume.

## Scope Boundaries
- In scope: Bind/Spell/profile/requirements, compiler/executors, Creations and existing scopes, transfer,
  uniqueness/selection and crystallizer source/record/replay mechanisms needed by this model.
- Out of scope: shipping the redesign, named-conduit implementation, generic DI tutorials, unrelated
  framework comparisons, stateful application recovery beyond the external-value boundary.

## State Transition Event
- from_state: review
- to_state: in_progress
- transition_reason: owner clarified the supplied-instance end state and requests a durable sequential approach.

## Dependencies / Related Work
- tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md
- tickets/tasks/2026-09-13_repair_existing_instance_planning_task.md
- tickets/tasks/2026-09-13_repair_provider_artifact_ownership_task.md
- tickets/tasks/2026-09-13_compare_existing_object_ownership_di_task.md
- tickets/epics/2026-08-02_agent_authored_synthetic_modules_epic.md (context requiring fresh verification).

## Tasks
- [x] TASK-2026-09-17-trace-existing-object-reference-model (discovery delivered; review pending):
  tickets/tasks/2026-09-17_trace_existing_object_reference_model_task.md
- [x] Synthesize findings into a coherent decision document.
- [ ] Stage 1: tickets/tasks/2026-09-17_existing_object_bind_representation_design_task.md.
- [ ] Open subsequent stage tasks in the sequence above as the preceding stage resolves.

## Acceptance Criteria
- Each supported/proposed input case maps to definition, reference storage, compiler action and lifecycle owner.
- Source-backed evidence distinguishes what already works from missing mechanisms and policy changes.
- No-new-creation constraints and incoming dependency edges are explicit in the proposed compiler treatment.
- A lifetime/version matrix explains the supplied reference, admissible reuse and scope release.
  Definition-first supply remains separately identified when discussed.
- Transfer/rollback and provider-artifact obligations have explicit source owners and qualification cases.
- Fileless/synthetic/live-only capture and replay limits are stated without conflating structure and instance state.
- Remaining design decisions are concrete and accompanied by viable choices/tradeoffs.

## Validation / Test Plan
Use existing verified A-to-B injection as a baseline, not the central discovery question again.
Run isolated probes only to resolve identified unknowns. Capture current behavior without monkeypatching
it into acceptance. Any simulated correction must be labeled diagnostic and kept separate from baseline.

## UX / API / Data Notes
No API name or representation is selected yet. Candidate interfaces belong in the decision artifact
and must preserve existing scope vocabulary, uniqueness and externally supplied-object semantics.

## Risks / Mitigations
- Presence of a live value is conflated with source policy: locate every such branch before choosing fields.
- Compiled plans can retain a global value: trace captures before claiming per-scope external resolution.
- Metadata and cleanup stores can diverge: trace admission/release/transfer as one lifecycle.
- Synthetic modules can be mistaken for state reconstruction: identify exactly what material they carry.
- Prior partial fixes can be regressed: retain their specific proof cases in the migration requirements.

## Open Questions
- Which normal bind metadata can the supplied instance reuse, and where should construction-disabled intent live?
- Which owner/scope admits a value, and what do replacement/version selection and cleanup mean?
- What module/code material can be preserved for an object available only through a live reference?
- Which parts of the provider-artifact failure need architectural changes versus contract-preserving correction?

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/existing_object_discovery_20260917/discovery.md (owned by the linked trace task).
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain the accepted design and source evidence for implementation.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record the exact source or owner decision needed.

## Notes
- DATETIME: 2026-09-17T21:22:19Z
  TYPE: DECISION
  CLAIM: Owner authorizes discovery of how the reference/blueprint/no-new-creation model should work.
    Created this story and a tactical trace task; runtime implementation remains outside this phase.
  EVIDENCE:
  - Owner request to make a discovery story and figure out the model.
  - tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md:14-95
  IMPACT: The earlier no-discovery discussion boundary is lifted for this story; it is not approval to implement.
  NEXT: Trace the current registration/compiler/value-store boundaries and record the first meaningful finding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T21:46:58Z
  TYPE: FACT
  CLAIM: The task delivered a source-backed reference/blueprint candidate model and nine native
    characterization cases. Existing stores support reference transfer, but current shortcuts permit
    resolvable values outside those stores; staged admission and crystal replay have explicit gaps.
  EVIDENCE:
  - artifacts/existing_object_discovery_20260917/discovery.md:1-370
  - tickets/tasks/2026-09-17_trace_existing_object_reference_model_task.md
  IMPACT: The initial discovery is reviewable. Recommended direction separates external-only source
    policy, scope value admission, cleanup custody and executable artifact authority; no runtime change.
  NEXT: Discuss the external-only definition plus scoped-admission direction first, then its custody rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T22:21:43Z
  TYPE: DECISION
  CLAIM: Owner clarifies the basic target as a user-bound existing object treated like a normal object
    with construction disabled; ownership transfer must carry the existing object. Owner requires
    stepwise work that survives repeated compaction. Added the authoritative six-stage sequence and
    current checkpoint; opened only the bind-representation task.
  EVIDENCE:
  - Owner's clarification and request for a compaction-safe approach, preserved in Owner Intent above.
  - tickets/tasks/2026-09-17_existing_object_bind_representation_design_task.md
  IMPACT: Stage 1 is the sole next design scope. The initial broad map and nine observations remain
    reference evidence; earlier definition-first supply proposals do not displace supplied-instance binding.
  NEXT: Follow the Stage-1 task to compare class/instance bind metadata and draft its reuse table.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-17T23:08:39Z
  TYPE: DECISION
  CLAIM: Owner explicitly requires a special dependency-aware error when a supplied object cannot
    satisfy another object's resolution, and accepts invalidation/refusal through existing structures.
    Stage 1 now records construction policy separately from resolution validity and carries the
    diagnostic attribution obligation forward to Stage 3.
  EVIDENCE:
  - Owner's current dependency-resolution question and error requirement.
  - tickets/tasks/2026-09-17_existing_object_bind_representation_design_task.md
  IMPACT: Keep normal graph edges and eligible-reference injection. Refuse unsatisfied active paths
    without constructor fallback. Error schema and exact validity publication are not implemented.
  NEXT: Complete the Stage-1 metadata comparison with this distinction in the representation contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Findings and remaining decisions reviewed with owner.
- [ ] Acceptance confirmed and task/board state synchronized.

## Noting Behavior
Keep tactical evidence in the task; record cross-boundary implications and decisions here.

## Context / Handoff Summary
CURRENT STAGE: 1 - bind representation, in progress. Read Owner Intent and Current Checkpoint first.
The user supplies an existing object; treat it through normal object machinery with creation disabled.
Transfer must carry that object and applicable responsibility. Failed dependency resolution must identify
the consumer/provider/path and use the appropriate validity/error structure; construction policy remains
separate. Complete the Stage-1 bind metadata comparison next; reuse the earlier broad discovery as evidence.
Stage state, source pointers, decisions and NEXT live in ContextCompass. No production implementation.
