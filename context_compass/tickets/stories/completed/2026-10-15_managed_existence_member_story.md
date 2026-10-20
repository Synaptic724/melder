# Story: managed_existence_member - the seventh Existence member, classified, routed and ranked

- Completed: 2026-10-15T10:11:15Z
- Summary: landed 0.2.8241 - `Existence.managed_spell_quantity` appended as the seventh member; the matrix
  classifies it for class spells only; route family `"managed"`; Phase 6 ranks it 0 with unique. Release-note
  section "`Existence.managed_spell_quantity`: objects leased from a root-owned pool and released back" opened.

## Metadata
- Story ID: STORY-2026-10-15-managed_existence_member
- Epic: EPIC-2026-10-14-managed_spell_quantity (tickets/epics/2026-10-14_managed_spell_quantity_epic.md); story 1 of 7
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T09:29:51Z
- Updated: 2026-10-15T10:11:15Z

## User Narrative
As an agent building in Melder, I want `Existence.managed_spell_quantity` recognized wherever Melder classifies
lifetimes, so that a managed binding is routed and ranked like the pooled lifetime it is.

## Value / MRP Alignment
Classification is what every later story builds on: the matrix, the route family and the Phase 6 rank decide which
binding families may use the member, which door a root gets and which dependencies a managed spell may have. The
member is appended last, so no existing member's value, name or rank moves.

## Ticket Contract
- ENTRY_GATE: the epic's Build Specification B6;
  system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md and
  system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_existence_classification.md written and
  linked; the mapping note recorded below.
- EXECUTION_BOUNDARY: src/melder/aether/spellbook/existence/existence.py,
  src/melder/aether/spellbook/resolution_style_matrix.py,
  src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py (`_build_model_shell`),
  src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py and their tests; any code
  that enumerates Existence and assumes six members (found by search, then read).
- DEPENDENCIES: none inside the lane; Milestone 1 of the epic (met).
- EXIT_GATE: its tests green under `-X gil=0` and `-X gil=1`; the touched modules' existing suites green; one notch
  taken from `__version__` at landing with the running release note's managed section extended; the epic's Build
  Specification updated with what this story settled; story closed (completed folder, board sync)
- FAILURE_ESCALATION: DECISION_REQUEST if a change would alter an existing member's behaviour, an existing spell id or
  record, or the frame -> conduit -> Book lock order; CONFLICT when the source contradicts the epic's Build
  Specification (fix the spec first); BLOCKER when a gate cannot be met

## Requirements (Functional)
- `Existence.managed_spell_quantity = auto()`, appended after the six members; `__str__` returns the bare name.
- ResolutionStyleMatrix: expected count 7; the member in the all-names and non-unique tuples; the class-based family
  supports it; the callable and existing-object families list it unsupported; `validate()` stays green.
- SpellArtifactProcessor `_build_model_shell`: existence managed -> route family `"managed"`.
- Phase 6 ScopeOrderingStrategy `scope_rank`: managed 0 (with unique). A managed holder may depend on unique, managed
  and many; it may not depend on cluster, lineage, unique_per_conduit or unique_per_spell_space; every holder may
  depend on a managed spell.

## Requirements (Non-Functional)
- The six members keep their values, names, ranks and every behaviour; no spell id moves.
- No module-level constants; docstrings carry AGENT_PURPOSE text in the house format.

## Scope Boundaries
- In scope: the member and the three classification seams; code that assumes six members.
- Out of scope: bind options and validation (S2), pools (S3), codegen (S5); a managed binding cannot be melded until
  S5 lands.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes and the touched suites green;
  notched 0.2.8241 (delegated routine closure under the owner's go-ahead).

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity Build Specification B6; S2 depends on this member.
- tests/unit/melder/spellbook/test_resolution_style_matrix.py;
  tests/unit/melder/spellbook/spell_crafter/system/validation/test_scope_ordering_strategy.py

## Tasks (Implementation Checklist)
- [x] Read existence.py, resolution_style_matrix.py, `_build_model_shell` and ScopeOrderingStrategy whole; search for
      code enumerating Existence (six-member assumptions) and read each hit.
- [x] Write the component patch and the mapping note.
- [x] Red tests: matrix with seven members and the family policy, route family, Phase 6 ranks.
- [x] Implement; green under both GIL modes; run the touched modules' existing suites.
- [x] Notch, the release note's managed section, the epic spec update, close and sync the board.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- `ResolutionStyleMatrix.validate()` passes with seven members; the policy tests above pass.
- A managed spell maps to route family `"managed"`; an unknown member still raises.
- Phase 6 accepts managed -> unique / managed / many and refuses managed -> narrower lifetimes; every existing rank
  test passes unchanged.

## Validation / Test Plan
- `python -X gil=0 -m pytest tests/unit/melder/spellbook/test_resolution_style_matrix.py
  tests/unit/melder/spellbook/spell_crafter/system/validation/test_scope_ordering_strategy.py` and the new tests; the
  same with `-X gil=1`; the existence and scope-ordering integration suites.

## UX / API / Data Notes
- Public: `Existence.managed_spell_quantity` (usable at bind once S2 lands; meldable once S5 lands).

## Risks / Mitigations
- Code or tests that pin the six-member list fail -> update a pin only when it pins the list itself, with the reason
  recorded; a behaviour assertion that breaks is a finding.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No `src/` edit before the component patch and the mapping note exist.

## Open Questions
- None open.

## Decision Log
- 2026-10-15 (melder_0): append the member last so existing `auto()` values and orders stay put.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_existence_classification.md
  - artifacts/managed_spell_quantity_20261015/ (this story's runs and scripts)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (artifacts)
- CLEANUP_TRIGGER: patch docs promoted and archived at S7; artifacts retained

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - classification of Existence.managed_spell_quantity
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, design, implementation and tests of this story;
  created 2026-10-15T09:29:51Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-15T09:29:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened as S1 of the lane: the member and the three classification seams (matrix, route family, Phase 6 rank),
    red tests first. Seams located on 0.2.8240: Existence 3-138, ResolutionStyleMatrix 44-491, `_build_model_shell`
    107-182, ScopeOrderingStrategy 31-145.
  EVIDENCE:
  - src/melder/aether/spellbook/existence/existence.py:3-138
  - src/melder/aether/spellbook/resolution_style_matrix.py:44-491
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:107-182
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:31-145
  IMPACT: Defines the story's tranche order.
  NEXT: Read the four seams whole and search for six-member assumptions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T09:32:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1's seams, read whole on 0.2.8240. (1) `Existence` has six `auto()` members and `__str__` returns the
    bare name; its class docstring says "The six modes" and its AGENT_PURPOSE lists them. (2) ResolutionStyleMatrix
    is a policy artifact read only by its tests: `validate()` checks the enum count against
    `EXPECTED_EXISTENCE_COUNT` (6) and that every family row classifies exactly `ALL_EXISTENCE_NAMES`; the
    callable and existing-object families take `NON_UNIQUE_EXISTENCE_NAMES` as unsupported, so adding the member to
    both tuples classifies it everywhere. (3) `_build_model_shell` maps each existence to a route family and raises
    RuntimeError for any other member, so a managed spell cannot compile today. (4) Phase 6 builds `scope_rank` per
    run (no class constant) and SKIPS any node or dependency whose existence has no rank, so a managed spell is
    unchecked in both directions until it gets rank 0. (5) The search for six-member assumptions found only the
    matrix count; the Nexus static rooms (`static_command_system.py` 207-210, 232-233, 626-628;
    `static_frame_viewer.py` 291-294) treat many and unique_per_spell_space as having no stored object - a managed
    spell belongs in those sets, which belongs with `meld_existing_spell`'s managed branch in S3.
  EVIDENCE:
  - src/melder/aether/spellbook/existence/existence.py:3-138
  - src/melder/aether/spellbook/resolution_style_matrix.py:44-491
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:107-182
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:31-145
  - src/melder/nexus/rift/command_system/static_command_system.py:195-240
  - src/melder/nexus/rift/frame_viewer/static_frame_viewer.py:280-300
  IMPACT: S1 is four small additive edits plus the Existence docstrings; the Nexus static sets move to S3's
    store-reader work, recorded in S3.
  NEXT: Write component_patch_existence_classification.md and the mapping note, then the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T09:33:02Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch-section -> implementation -> validation mapping (patch_artifact_consumption). Read order done:
    architecture_patch.md (invariants 1 and 2 apply here), component_patch_existence_classification.md. (a)
    Existence before/after -> append the member and its docstring, update the class docstring and AGENT_PURPOSE ->
    unit: the member exists, is last, `str()` is the bare name, the six values are unchanged. (b) Matrix -> count 7,
    the two tuples, LAST_UPDATED_ISO -> unit: `validate() == ()`, family policy for the member. (c) Route family ->
    one elif -> unit: `_build_model_shell` returns "managed". (d) Phase 6 -> one `scope_rank` entry -> unit:
    managed->unique/managed/many accepted, managed->cluster/lineage/upc/spellspace refused, unique/upc/many->managed
    accepted. No code-description patch: no control-flow, concurrency or error-semantics change.
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md:1-106
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_existence_classification.md:1-38
  IMPACT: S1's entry gate is met; the red tests come next.
  NEXT: Write the red tests and run them against 0.2.8240 (expected to fail).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T10:10:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S1 implemented and validated. Source: the member and its docstrings (existence.py), the matrix count and
    both tuples with LAST_UPDATED_ISO 2026-10-15 (resolution_style_matrix.py), the "managed" route family
    (spell_artifact_processor.py), `scope_rank` 0 with a comment (scope_ordering_strategy.py). Red first: 6 failures
    plus a collection error on 0.2.8240; green: the 41 tests of the four files pass under `-X gil=0` and `-X gil=1`;
    the existence and scope-ordering integration suites (45), the spellbook unit tree (929 + 1446) and the top-level
    unit tests (145) pass under `-X gil=0`. Notched 0.2.8241 with the release note's managed section; the asset
    rebuild needed delete permission on melder_private (granted by the owner for this session) and both asset
    checks print OK. Not run: the whole tree (S5 and S7 run it).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s1_red_gil0.txt:1-12
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s1_green_gil0.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s1_green_gil1.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s1_unit_spell_crafter_gil0.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s1_unit_spellbook_rest_gil0.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s1_rebuild_assets_check.txt:1-4
  - src/melder/aether/spellbook/existence/existence.py:3-165
  IMPACT: S1's acceptance criteria hold; the member is classified, routed and ranked; S2 can bind it.
  NEXT: Close S1, route the board to S2, then the llm_support rebuild last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user (in the lane's report to the owner)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S1 - the member, matrix, route family, Phase 6 rank. Done: landed 0.2.8241.
- Evidence: Notes (FACT, PLAN mapping, MEASURE); runs in artifacts/managed_spell_quantity_20261015/runs/.
- Not run: the whole tree (S5 and S7 run it).
- Next: S2 (tickets/stories/2026-10-15_managed_bind_options_story.md).

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
