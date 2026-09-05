# Task: Implement Intermediate composition chapters and all 37 lessons

## Metadata
- Task ID: TASK-2026-09-04-rtd-intermediate-content
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-intermediate-curriculum
- Story Path: ../stories/2026-09-04_rtd_intermediate_curriculum_story.md
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-04T23:46:20Z

## Objective
Deliver configuration, DI, hooks, scopes, linking, permissions, late binding, and a connected-system walkthrough with all Intermediate examples.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: docs/intermediate/, Intermediate lesson presentation metadata, helper-aware instructions, related links, and source-backed lesson corrections.
- DEPENDENCIES: S1/S2 and agreed Beginner vocabulary.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Foundation/catalog and Beginner chapters are built; composition content now proceeds.

## Steps / Checklist
- [ ] Read the exact inputs and record one bounded implementation decision.
- [ ] Complete required patch contracts when the change is system-impacting.
- [ ] Implement the scoped deliverable with notes before the next tranche.
- [ ] Validate meaningful behavior/content and record actual outcomes.
- [ ] Synchronize parent story and hand off or close after acceptance.

## Acceptance Criteria
- [ ] All required chapters and all 37 lessons are present.
- [ ] Provider/consumer/link/pull/meld ordering is accurately explained.
- [ ] Helper requirements and public md.* usage are preserved.
- [ ] Cross-level topic links preserve original source placement.
- [ ] Applicable example/probe and link/render checks have recorded outcomes.

## Validation
- Existing Intermediate harness: 37 passed on Python 3.14t, including the cluster identity assertion.
- Strict integrated rendering and API links follow as later-level/reference destinations are added.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/rtd_validation_20260904/intermediate.xml
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement Intermediate composition chapters and all 37 lessons
- IF_UNKNOWN: none

## Noting Behavior
- Finish a coherent read/work unit and append evidence, impact, and one next action.
- Keep notes append-only; label unverified claims explicitly.

## Notes
- DATETIME: 2026-09-04T22:07:46Z
  TYPE: PLAN
  CLAIM: Implement this bounded part of the accepted documentation program under its existing story.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:293-344
  - Owner implementation instruction on 2026-09-04.
  IMPACT: The complete program now has explicit execution tasks and dependency boundaries.
  NEXT: Activate this task when its dependency milestone is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:46:20Z
  TYPE: DECISION
  CLAIM: Extend docs/curriculum.toml and docs/intermediate/ using the README's exact relevant sections
    plus authored bridges for configuration, hooks, scopes, overrides, permissions, and ownership.
    Keep all 37 saved lessons under their existing IDs and include helpers in the collection downloads.
    Patch boundary/validation ordering maps to Curriculum._chapter and DocumentationBuilder.load;
    validate with the existing example harness and strict Sphinx, without runtime API changes.
  EVIDENCE:
  - docs/tools/curriculum.py:65-152
  - docs/tools/build_docs.py:77-142
  - system_docs/patches/active/rtd_site_2026_09_04/architecture_patch.md:15-38
  - README.md:478-597
  IMPACT: Canonical README prose remains authoritative while missing depth becomes addressable chapters.
  NEXT: Read the saved composition lessons before writing their chapter explanations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:52:30Z
  TYPE: DECISION
  CLAIM: The complete composition examples explicitly build provider and consumer before linking,
    then have the consumer pull and meld per edge. Cluster lesson 25 already compares the two returned
    buses but only prints the comparison; add that same identity condition as an assertion. New guides
    will explain permission choices without treating a caught exception as proof of a successful meld.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/26_conduit_categories_as_factories.py:90-136
  - UX_and_AIX_experiences/02_intermediate/36_late_binding_with_spellcontract.py:64-130
  - UX_and_AIX_experiences/02_intermediate/25_clusters_unique_per_cluster.py:25-62
  IMPACT: The connected walkthrough can use the canonical main function and its asserted shared service.
  NEXT: Write chapter mappings and authored bridges, then execute the Intermediate harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:49:00Z
  TYPE: FACT
  CLAIM: Read the complete registration/configuration/scope lessons. SpellBinder finalizes each
    registration; with_kwargs carries bind parameters, while constructor configuration uses override.
    Configuration lessons explicitly set disposal before conjure and tune worker/barrier settings.
    Hook examples key callbacks by book ID; scope examples demonstrate lineage sharing, child cleanup,
    and preserved creations on promotion. The shared-config lesson's historical surface-gap prose
    must not be promoted into a new guide without current verification.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/02_spellbinder_full_chain.py:1-60
  - UX_and_AIX_experiences/02_intermediate/30_config_disposal_and_the_frozen_law.py:1-75
  - UX_and_AIX_experiences/02_intermediate/32_config_meld_hooks.py:1-46
  - UX_and_AIX_experiences/02_intermediate/28_upgrade_to_normal.py:1-62
  IMPACT: Author guides around demonstrated public calls and keep unverified historical claims out.
  NEXT: Read the linked-subsystem examples and existing verification harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:49:46Z
  TYPE: MEASURE
  CLAIM: Twelve Intermediate chapter mappings and eight authored bridge pages are implemented.
    The existing harness passed all 37 examples, including the new cluster shared-identity assertion.
    Canonical README sections supply module registration, DI, dynamic linking, and SpellContract prose.
  EVIDENCE:
  - docs/curriculum.toml:107-209
  - artifacts/rtd_validation_20260904/intermediate.xml:1-1
  - UX_and_AIX_experiences/02_intermediate/25_clusters_unique_per_cluster.py:25-65
  IMPACT: Composition content is ready for integrated rendering after its Advanced destinations exist.
  NEXT: Implement Advanced chapters, then validate the combined site and curriculum cross-links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [x] No silently omitted content or invented validation.
- [x] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Twelve Intermediate chapters and all 37 saved lesson routes are implemented; all 37 scripts pass.
Current task is in review pending integrated HTML/API/navigation quality checks. Cluster lesson 25
now asserts shared identity. Source code is included canonically. Owner handles commits and pushes.
