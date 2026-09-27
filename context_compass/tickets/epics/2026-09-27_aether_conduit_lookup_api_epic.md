

# Epic: Aether conduit lookups say what they cover, and Aether can find any conduit

## Metadata
- Epic ID: EPIC-2026-09-27-aether-conduit-lookup-api
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T10:07:08Z
- Updated: 2026-09-27T10:41:49Z
- Target Window: 2026-Q4
- Related Program/Initiative: public API clarity for conduit discovery (owner ledger item MF7)

## Problem / Opportunity
Aether's eight conduit lookups (`list_conduit_ids`, `list_conduit_names`, `count_conduits`, `has_conduit_id`,
`has_conduit_name`, `find_conduit_id_by_name`, `get_conduit_by_name`, `get_conduit_by_id`) read only the frame's
root maps, but their names promise any conduit. A live named lesser therefore looks absent from Aether while
ConduitCloud and the Nexus commands find it (cause and repro:
tickets/tasks/2026-09-27_trace_get_conduit_by_name_named_lesser_lookup_task.md). Owner direction, 2026-09-27:
give the
root-only methods root-explicit names, add Aether lookups that find any conduit (by name, by id), let ConduitCloud
return all of its conduits, migrate every usage properly, and move the version up afterwards. Investigate before
migrating.

## MRP Alignment (Most Reasonable Product)
One coherent discovery surface at the runtime root: every name states its coverage, frame-wide discovery exists
where users look first, and no existing caller changes meaning silently. A rename done without a full usage map is
a trap; the survey comes first.

## Ticket Contract
- ENTRY_GATE: board row routes here; one story per method exists; the usage survey and design facts are recorded
  before any rename.
- EXECUTION_BOUNDARY: investigation only until the owner approves the API design (names, signatures, coverage,
  migration form, version step); then per-story implementation behind patch docs.
- DEPENDENCIES: tickets/tasks/2026-09-27_trace_get_conduit_by_name_named_lesser_lookup_task.md; named lesser
  scope contract (2026-09-23, src_architecture Operational Invariants).
- EXIT_GATE: every story accepted; every recorded usage migrated or deliberately kept (src, tests, docs, examples,
  system docs, generated bundles and assets); version moved per the owner's decision; board and closure sync done.
- FAILURE_ESCALATION: DECISION_REQUEST for names, migration form, cross-frame semantics and version step; CONFLICT
  when documents and source disagree.

## Goals (Outcomes)
- Root-only Aether lookups carry root-explicit names with unchanged behaviour.
- Aether can return any live conduit by name and by id; ConduitCloud can return all of its conduits.
- Every usage is migrated deliberately, and the version moves once the API change lands.

## Non-Goals (Explicit Exclusions)
- Changing named-lesser lifecycle, pooling or Cloud registration.
- Changing the Nexus command surfaces or FrameViewer methods that share these names, unless the owner adds them.

## Scope Boundaries
- In scope: the eight Aether lookups, the three new lookups, their usages and documentation, the version step.
- Out of scope: other Aether surfaces; spell lookup (`_get_conduit_by_spell_id`) unless the survey ties it in.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner instruction in chat, 2026-09-27 ("make an epic and a story for each method and lets
  investigate before we migrate").

## Success Metrics
- Zero lookups whose name promises more than they cover; zero unmigrated usages at closure (by survey recount).

## Requirements (Functional + Non-Functional)
- Root-explicit methods behave exactly as today; new lookups state coverage, lease and error contracts.
- No hot-path cost; lookups take only leaf locks and invoke no callbacks.

## Constraints / Assumptions
- Public library: the migration form (hard rename or deprecated aliases) is the owner's call and must be documented.
- Names are unique per frame, not across frames (UNKNOWN until confirmed in source during the investigation).

## Dependencies / External References
- tickets/tasks/2026-09-27_trace_get_conduit_by_name_named_lesser_lookup_task.md
- docs/intermediate/scopes.md (current user guidance for named-scope discovery)

## Milestones (Track Progress)
- [x] Milestone 1: Usage survey and design facts recorded per story.
- [x] Milestone 2: Owner API decision (names, signatures, coverage, migration form, version step).
- [ ] Milestone 3: Patch docs written and linked.
- [ ] Milestone 4: Stories implemented and accepted.
- [ ] Milestone 5: Docs, system docs, bundles, release note and version moved.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-09-27-aether-list-conduit-ids-root-rename - Aether.list_conduit_ids: root-explicit
      name (`tickets/stories/2026-09-27_aether_list_conduit_ids_root_rename_story.md`)
- [ ] Story: STORY-2026-09-27-aether-list-conduit-names-root-rename - Aether.list_conduit_names: root-explicit
      name (`tickets/stories/2026-09-27_aether_list_conduit_names_root_rename_story.md`)
- [ ] Story: STORY-2026-09-27-aether-count-conduits-root-rename - Aether.count_conduits: root-explicit name
      (`tickets/stories/2026-09-27_aether_count_conduits_root_rename_story.md`)
- [ ] Story: STORY-2026-09-27-aether-has-conduit-id-root-rename - Aether.has_conduit_id: root-explicit name
      (`tickets/stories/2026-09-27_aether_has_conduit_id_root_rename_story.md`)
- [ ] Story: STORY-2026-09-27-aether-has-conduit-name-root-rename - Aether.has_conduit_name: root-explicit
      name (`tickets/stories/2026-09-27_aether_has_conduit_name_root_rename_story.md`)
- [ ] Story: STORY-2026-09-27-aether-find-conduit-id-by-name-root-rename - Aether.find_conduit_id_by_name:
      root-explicit name (`tickets/stories/2026-09-27_aether_find_conduit_id_by_name_root_rename_story.md`)
- [ ] Story: STORY-2026-09-27-aether-get-conduit-by-name-root-rename - Aether.get_conduit_by_name:
      root-explicit name (`tickets/stories/2026-09-27_aether_get_conduit_by_name_root_rename_story.md`)
- [ ] Story: STORY-2026-09-27-aether-get-conduit-by-id-root-rename - Aether.get_conduit_by_id: root-explicit
      name (`tickets/stories/2026-09-27_aether_get_conduit_by_id_root_rename_story.md`)
- [ ] Story: STORY-2026-09-27-aether-find-any-conduit-by-name - Aether finds any live named conduit in a
      frame, root or lesser, by name (`tickets/stories/2026-09-27_aether_find_any_conduit_by_name_story.md`)
- [ ] Story: STORY-2026-09-27-aether-find-any-conduit-by-id - Aether finds any live conduit in a frame by id,
      root or lesser (`tickets/stories/2026-09-27_aether_find_any_conduit_by_id_story.md`)
- [ ] Story: STORY-2026-09-27-conduit-cloud-list-all-conduits - ConduitCloud returns all of its conduits
      (`tickets/stories/2026-09-27_conduit_cloud_list_all_conduits_story.md`)

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Usage survey across src, tests, docs, examples, system docs and generated bundles (this investigation).
- [ ] Task: Version step and release note after the change lands.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- All stories accepted by the owner; survey recount shows no unmigrated usage; version moved; docs current.

## Risks / Mitigations
- Silent semantic change if an old name is reused with a wider meaning: decide explicitly, per method.
- Generated assets and LLM bundles embed method names: regenerate them in the same lane.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Per story: unit and integration tests on 3.14t and GIL; a survey recount before closure.

## Rollout / Adoption Plan
- Hard rename, no aliases (owner, 2026-09-27); release-note 'Breaking change' bullets list old -> new names.

## Open Questions
- Frame-string enforcement scope (DECISION_REQUEST note); everything else decided 2026-09-27.

## Decision Log
- 2026-09-27T10:31:58Z: option A, frame-scoped `aetheric_frame_name: str = "default"`, NAMED Cloud listing,
  hard rename, one 0.01 notch; TransferOfOwnership root-only by design (owner).
- 2026-09-27T10:07:08Z: owner direction recorded (Problem section); implementation waits for the API decision.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/aether_lookup_api_survey_20260927/survey_usages.py
  - artifacts/aether_lookup_api_survey_20260927/usage_survey_20260927.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: epic closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T10:07:08Z
  TYPE: DECISION
  CLAIM: Owner direction (chat, 2026-09-27) replaces the task's D1/D2 widening: rename Aether's root-only lookups to
    root-explicit names, add Aether lookups that find any conduit by name and by id, let ConduitCloud return all of
    its conduits, migrate every usage, move the version up afterwards; one story per method; investigate first.
  EVIDENCE:
  - tickets/tasks/2026-09-27_trace_get_conduit_by_name_named_lesser_lookup_task.md
  - src/melder/aether/aether.py:1643-1886
  IMPACT: Public API change across eight methods plus three additions; the survey gates every rename.
  NEXT: Survey every usage of the eight lookups and record it per story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-27T10:24:22Z
  TYPE: FACT
  CLAIM: Usage survey (AST, receivers resolved; script and output filed). Hand-written Aether callers: Aether
    itself (3), TransferOfOwnership (list_conduit_ids + get_conduit_by_id), CommandSystem and StaticFrameViewer
    (get_conduit_by_id), 6 root get_conduit_by_name calls in integration/component tests, 1 benchmark, and
    test_aether.py unit tests (11 public + 6 private-helper calls). No hand-written user doc calls an Aether
    lookup; docs teach the Cloud and Nexus methods of the same names. Generated copies (docs/_build,
    _readthedocs, llm_support, src_graph.md, _build_assets) are rebuilt, not edited. Per-method inventories are
    in each story.
  EVIDENCE:
  - context_compass/artifacts/aether_lookup_api_survey_20260927/usage_survey_20260927.txt:46-71
  - context_compass/artifacts/aether_lookup_api_survey_20260927/usage_survey_20260927.txt:72-73
  - context_compass/artifacts/aether_lookup_api_survey_20260927/usage_survey_20260927.txt:2-45
  - context_compass/artifacts/aether_lookup_api_survey_20260927/survey_usages.py:1-168
  IMPACT: The rename blast radius is small in src (4 external sites) and tests (~24 sites); most repo mentions
    are other classes' methods of the same names, which the migration must not touch.
  NEXT: Read the ConduitCloud public surface and past rename/version precedent, then write the design proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-27T10:24:22Z
  TYPE: UNKNOWN
  CLAIM: Side question, outside this epic: TransferOfOwnership._collect_impacted_conduit_ids sweeps only ROOT
    conduits for impacted lineages (via Aether's root id family); whether lessers holding contracted views
    should be swept is not established. A rename must keep today's root-only behaviour there.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:752-814
  IMPACT: None on the rename; raised to the owner as a possible separate item.
  NEXT: Mention to the owner; no investigation here.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-27T10:26:47Z
  TYPE: FACT
  CLAIM: Precedent and constraints: the last public rename (SpellMap/SpellContract `spell_override` ->
    `override`) shipped as a hard break with no alias and a 'Breaking change' bullet in the unreleased notes
    (release_docs/0.2.77.md, headed Melder 0.2.78); src has no deprecation machinery (no DeprecationWarning
    anywhere, search). The same method names already mean different coverage on different classes: Aether's
    eight answer over ROOTS, ConduitCloud's over NAMED SCOPES, and the Nexus getters over published, ACL-gated
    scopes including anonymous lessers by id.
  EVIDENCE:
  - release_docs/0.2.77.md:1-23
  - src/melder/aether/aether.py:1643-1886
  - src/melder/aether/aetheric_frame/conduit_cloud.py:525-686
  - src/melder/nexus/rift/command_system/command_system.py:194-291
  IMPACT: A hard rename matches precedent; reusing a generic name for a wider meaning cannot coexist with an
    alias.
  NEXT: Write the STRATEGY_DISCUSSION for the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-27T10:26:47Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: API design for the owner (from the survey and design facts in this epic and its stories).
    1 Objective: names state coverage; Aether can reach any conduit by name and by id; Cloud returns its conduits.
    2 Constraints: public library, hard-rename precedent (0.2.78 notes), no deprecation machinery, no hot-path cost,
      no silent change for callers that keep working.
    3 Known facts: three coverage levels exist - ROOT (frame root maps; Aether today), NAMED (Cloud directory:
      named roots + active named lessers; Cloud today), LIVE (roots + every attached lesser, named or anonymous;
      reachable only by root map + ward walk; duplicated twice in Nexus). Every root is named and in the Cloud.
      In-repo callers of the eight: 4 src sites (TransferOfOwnership, CommandSystem, StaticFrameViewer), ~24 tests,
      1 benchmark, 0 hand-written docs.
    4 Unknowns: whether "any frame" means one frame (as every Aether lookup today) or a search across frames
      (names are unique per frame only).
    5 Options:
      A (recommended) Rename the eight to *_root_* names (list_root_conduit_ids, list_root_conduit_names,
        count_root_conduits, has_root_conduit_id, has_root_conduit_name, find_root_conduit_id_by_name,
        get_root_conduit_by_name, get_root_conduit_by_id; private helpers follow). Reuse the generic
        get_conduit_by_name for NAMED (delegates to the frame Cloud) and get_conduit_by_id for LIVE (root map,
        then snapshot ward walk; both Nexus copies collapse into it). Retire the other six generic names rather
        than reuse them, since their "any" meaning splits between NAMED and LIVE. Add ConduitCloud.list_conduits()
        returning a NAMED snapshot. Hard rename, no aliases.
      B As A, but give the new lookups new names (for example find_conduit / find_conduit_by_id) and remove every
        generic name, so no call keeps compiling with a different meaning.
      C As A, but keep the six generic names as aliases of the Cloud's NAMED semantics (Aether and Cloud agree).
    6 Tradeoffs: A keeps the name users reach for (MF7) and every root lookup through it returns the same object as
      today, but code calling get_conduit_by_* keeps compiling; B is the most explicit and the loudest break; C
      maximises symmetry with the Cloud but keeps six names whose coverage differs from the root ones.
    7 Recommendation: A, frame-scoped (explicit frame, default "default"); version per the owner's decision below.
    8 Decision ask: option A/B/C; frame-scoped or cross-frame (and the ambiguity rule if cross-frame); Cloud
      list_conduits coverage NAMED or LIVE; hard rename or aliases; version step (0.01 notch rule, or 0.3.0 as a
      pre-1.0 breaking release).
  EVIDENCE:
  - context_compass/artifacts/aether_lookup_api_survey_20260927/usage_survey_20260927.txt
  - tickets/stories/2026-09-27_aether_find_any_conduit_by_id_story.md
  - tickets/stories/2026-09-27_aether_find_any_conduit_by_name_story.md
  - tickets/stories/2026-09-27_conduit_cloud_list_all_conduits_story.md
  IMPACT: Decides every story's name and migration form; implementation stays blocked until answered.
  NEXT: Owner answers the decision ask.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-27T10:31:58Z
  TYPE: DECISION
  CLAIM: Owner decisions (chat, 2026-09-27): option A accepted (eight *_root_* renames; get_conduit_by_name
    reused for NAMED, get_conduit_by_id for LIVE; the other six generic names retired;
    ConduitCloud.list_conduits() over NAMED scopes); hard rename, no aliases; lookups are frame-scoped only,
    with the frame optional and string-typed as `aetheric_frame_name: str = "default"` like the rest of Aether
    (no cross-frame search, no None sentinel); ONE 0.01 version notch when the epic lands, not 0.3.0.
    TransferOfOwnership stays root-only by design: lessers own only the lifecycle of what they create; the
    earlier UNKNOWN is resolved. Frame resolution follows _get_existing_frame: 'default' always resolves (lazily
    created, 2026-07-11 ruling), a custom frame must exist.
  EVIDENCE:
  - src/melder/aether/aether.py:385-403
  - src/melder/aether/aether.py:1611-1641
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:752-814
  IMPACT: Names, coverage, migration form and version are settled; only the frame-string enforcement scope is
    open (next note).
  NEXT: Owner answers the frame-string refinement; then patch docs and implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-27T10:31:58Z
  TYPE: DECISION_REQUEST
  CLAIM: Refinement to confirm: enforce 'frame must be a string' at runtime with a TypeError in one frame
    resolver shared by all ten lookups (today None yields ValueError "Aetheric frame 'None' does not exist." and
    a list yields a raw unhashable-type TypeError from the dict), and name the searched frame in not-found
    errors, since the most likely mistake with a defaulted frame is forgetting a custom one. For the eight root
    lookups this changes only the error raised for non-string input; the 'not found' wording tests match stays.
  EVIDENCE:
  - src/melder/aether/aether.py:1611-1641
  - src/melder/aether/aether.py:1914-1982
  IMPACT: Decides whether the root family keeps its current bad-input errors or shares the new resolver.
  NEXT: Owner answers; then write patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-27T10:41:49Z
  TYPE: DECISION
  CLAIM: Owner approved implementation (chat, 2026-09-27), including the shared frame resolver for all ten
    lookups and frame-naming not-found errors. One task implements all eleven stories as one change set.
  EVIDENCE: tickets/tasks/2026-09-27_implement_aether_conduit_lookup_api_task.md
  IMPACT: Stories move to in_progress; the task carries the tactical notes.
  NEXT: Patch docs under the task, then implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Survey done (artifact filed): the eight Aether lookups have 4 src callers, ~24 test sites and 1 benchmark; docs call
only the Cloud and Nexus methods of the same names. Design facts and a recommended API (option A) are in the
STRATEGY_DISCUSSION note. Waiting on the owner's decisions; no src, test or doc edits.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
