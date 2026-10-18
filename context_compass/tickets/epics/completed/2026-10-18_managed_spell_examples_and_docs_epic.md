

# Epic: Managed spell pools taught end to end - runnable examples, their tests and a Sphinx page

## Metadata
- Epic ID: EPIC-2026-10-18-managed_spell_examples_and_docs
- Status: done
- Owner: user
- Agent Name: melder_2
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T21:13:40Z
- Updated: 2026-10-18T23:07:51Z
- Completed: 2026-10-18T23:07:51Z
- Summary: Managed spell pools taught end to end: a source-read lifecycle map (S1), intermediate lessons 42-48
  with 34 contract probes, green on 3.14t (S2), and the Sphinx chapter plus a release-note bullet (S3); no src/
  change; the closing rebuild waived by the owner.
- Target Window: 2026-Q4
- Related Program/Initiative: EPIC-2026-10-05-melder_services_and_pools (the program the pools shipped under);
  EPIC-2026-10-14-managed_spell_quantity (completed: the feature, 0.2.8241-0.2.8248)

## Problem / Opportunity
`Existence.managed_spell_quantity` landed at 0.2.8241-0.2.8248 (its four settings left the spell_id at 0.2.8254).
The system documents, the README, the glossary, `docs/intermediate/scopes.md` and a release-note section carry it,
but no runnable UX/AIX example teaches it, no example test proves it, and no Sphinx page walks a user through it:
the three pool modes (elastic, limited_quantity, queue), how an object is made and leased (meld, injection,
`Conduit.managed_spell_meld`), returned (`ReleaseManagedSpell`, `ManagedSpellLease`), reset
(`managed_spell_reset_methods`), refused (`ManagedSpellExhaustedError`), inspected and disposed. A search of
`UX_and_AIX_experiences/` found no managed name; in `docs/` the only source hits are `intermediate/scopes.md`,
`reference/glossary.md` and `api.toml` (grep, 2026-10-18T21:13:40Z).
Owner request (chat, 2026-10-18T20:51Z): investigate the new existence, make examples for the UX and AIX examples,
make tests for them, show every pool type and the full lifecycle (make, return, reset), add it to Sphinx after the
tests pass, and make an epic for it.

## MRP Alignment (Most Reasonable Product)
Documentation is part of the API. Examples written against `import melder as md` only and run by pytest on 3.14t
cannot drift from the code silently, and a Sphinx page whose every claim is verified in source gives users the
contract rather than an impression of it. Nothing ships that the code does not do.

## Ticket Contract
- ENTRY_GATE: melder_2 certified (2026-10-18T21:07Z); an attention_board.md row routes to the active story.
- EXECUTION_BOUNDARY: writes only to `UX_and_AIX_experiences/` (new examples and their pytest entries), `docs/`
  (the new page and its registrations), one entry in `release_docs/next_version_release.md`, this lane's tickets,
  boards and artifact folder, a tests_components entry if the suite map requires one, and the regenerated build
  assets and LLM bundles as the last step. No `src/` change and no notch. Tests and probes run on a VM copy under
  /tmp, never in the owner's tree.
- DEPENDENCIES: the managed-pool sources (`src/melder/aether/conduit/creations/managed_spell_quantity.py`,
  `release_managed_spell.py`, `managed_spell_lease.py` and their callers); melder_0's in-flight landing of
  EPIC-2026-10-18-spell_identity_is_the_code (S1/S2, 0.2.8257-0.2.8258: one object is one spell) and its rebuild;
  mailbox coordination before this lane's rebuild.
- EXIT_GATE: S1-S3 accepted; the examples and their tests green on 3.14t; the Sphinx build passes with the page in
  the navigation; the release-note entry; ticket closure and board sync; build assets and LLM bundles rebuilt with
  both `--check` runs printing only OK lines.
- FAILURE_ESCALATION: an example that needs a deep import is an init-surface gap - record it on the tier epic and
  raise DECISION_REQUEST; behaviour that contradicts the system documents - CONFLICT note, ask the owner; a Melder
  defect - file it, do not fix it (no `src/` in scope); a rebuild collision with melder_0 - coordinate through the
  mailbox before building.

## Goals (Outcomes)
- A user can run one example per pool mode and per lifecycle step and see what Melder does.
- Every example is executed by pytest on 3.14t and asserts only behaviour verified in source or by a probe.
- A Sphinx page explains managed spell pools end to end and points at the runnable examples.

## Non-Goals (Explicit Exclusions)
- No change to `src/`, no new API, no notch. Defects found are filed, not fixed.
- No benchmark and no rework of existing examples or pages beyond registering the new ones.
- No README rewrite.

## Scope Boundaries
- In scope: the lifecycle map (S1), the examples and their tests (S2), the Sphinx page, the release note and the
  rebuild (S3).
- Out of scope: changes to managed-pool semantics; the backlog defects of EPIC-2026-10-17-correctness_defects.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: S1-S3 done; closed on the owner's directive (chat, 2026-10-18T23:01Z), which also waived the
  closing rebuild of build assets and LLM bundles.

## Success Metrics
- Three pool modes and every lifecycle step each demonstrated by at least one runnable example.
- `pytest UX_and_AIX_experiences/pytest_examples` green on 3.14t with the new examples included.
- The Sphinx build passes and the page is reachable from the navigation.

## Requirements (Functional + Non-Functional)
- Functional: examples cover elastic, limited_quantity and queue; leasing by meld, by injection and through
  `managed_spell_meld`; release through `ReleaseManagedSpell` and a lease's `with`; reset methods; the exhaustion
  and queue-timeout refusals; inspection; disposal at teardown. Ownership transfer and a settings rebind if S1
  shows them teachable at the intermediate tier.
- Non-functional: `import melder as md` only; each file states TIER / GOAL / SURFACE EXERCISED; a `main()`; honest
  asserts; deterministic (no sleeps whose outcome depends on scheduling); the synaptic typing rules (Optional/Union,
  hints everywhere, no `from __future__ import annotations`).

## Constraints / Assumptions
- Examples run on Python 3.14t; the device VM's bare `python3` is 3.10, so a 3.14 interpreter is set up in scratch.
- Resolved (S2): `tests_components.md` lists `UX_and_AIX_experiences` only as a norecursedirs entry, so the
  example harness needs no entry there.

## Dependencies / External References
- `UX_and_AIX_experiences/AGENTS.md` (tier laws, verification harness, example law)
- `docs/maintaining.md` (Sphinx build and publication rules)
- `release_docs/next_version_release.md` (the managed section and `## Packaging and documentation`)
- `context_compass/system_docs/src_components.md` (Managed Spell Pools; Flow: Managed Lease -> Release)

## Milestones (Track Progress)
- [x] Milestone 1: lifecycle map - every step evidenced in source (S1)
- [x] Milestone 2: examples and tests green; walkthrough of pool types and lifecycle shown to the owner (S2)
- [x] Milestone 3: Sphinx page, release note (S3)
- [x] Milestone 4: closure, board sync, rebuild with both checks OK - closure and board sync done; the rebuild
  and its checks waived by the owner (2026-10-18T23:01Z), not performed

## Stories (Required to Complete)
- [x] Story: STORY-2026-10-18-managed_spell_lifecycle_map - read the managed sources whole; record the lifecycle map
- [x] Story: STORY-2026-10-18-managed_spell_ux_examples - runnable examples for every mode and step, with tests
- [x] Story: STORY-2026-10-18-managed_spell_sphinx_docs - the Sphinx page, the release note and the rebuild

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-10-18-managed_spell_lifecycle_map
- [x] Task: Complete story STORY-2026-10-18-managed_spell_ux_examples
- [x] Task: Complete story STORY-2026-10-18-managed_spell_sphinx_docs
- [x] Task: Coordinate the rebuild with melder_0 (mailbox NOTICE before building) - this lane's rebuild waived by
  the owner; M2-19 told melder_0 that its rebuild carries this lane's changes
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The three stories are accepted by the owner.
- The new examples and their tests pass on 3.14t; failures or unrun checks are recorded, never hidden.
- The Sphinx page builds, renders and is linked from the navigation.
- The release note carries the documentation entry; boards and artifact rows are synchronized.
- Build assets and LLM bundles are rebuilt last and both checks print only OK lines.

## Risks / Mitigations
- melder_0's landing moves spell_id rules mid-lane (one object is one spell): examples bind each class once; the
  tests run again on the tree after that landing.
- Queue waits involve threads and timeouts: hand objects across threads with events, use short fixed timeouts, and
  assert contract outcomes only.
- The device VM's /sessions disk is full (attention_board.md notes): TMPDIR and scratch under /tmp.
- A rebuild racing melder_0's: a mailbox NOTICE first, one rebuild after their landing.
- Sphinx not installed in the VM: install from `docs/requirements.lock` into the scratch environment.

## Applicable Anti-Patterns
- [x] No epic-state transition without story-level evidence.
- [x] No closure while required stories are incomplete or unaccepted.
- [x] No program claims without source evidence from story/task notes.
- [x] No example or page asserting behaviour not verified in source or by a probe.

## Validation / Test Approach
- `pytest UX_and_AIX_experiences/pytest_examples -v` on 3.14t (GIL off, and on where the harness allows).
- The Sphinx build documented in `docs/maintaining.md`.
- `python src/melder/_build_assets/_build_asset_runner.py --check` and
  `python llm_support/_builder.py --check --include-untracked` after the rebuild.

## Rollout / Adoption Plan
- The examples land in the intermediate tier's concept order; the page joins the docs navigation; the release
  note's `## Packaging and documentation` names both.

## Open Questions
- Resolved (S2): tier placement - the lessons are 02_intermediate 42-48 (beginner allows only unique, many and
  unique_per_conduit).

## Decision Log
- 2026-10-18: the examples go in the existing `UX_and_AIX_experiences/` (the request named
  `UI_AND_AIX_Examples`, which does not exist); stated to the owner before certification, no objection.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/managed_spell_examples_20261018/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: epic closure (probes, runs and scripts stay as the lane's evidence)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - UNKNOWN
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_2; synaptic_python_developer; prose; this epic; 2026-10-18T21:13:40Z
- Published By: UNKNOWN (local backend; no hosting service)
- Independent Review: none requested yet

## Notes
- DATETIME: 2026-10-18T21:13:40Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Three stories in order. S1 reads the managed sources whole (pool, release registry, lease, mode, errors,
    the bind options, the meld door, Creations' pool map) after slicing the component map, and records the
    lifecycle map with evidence. S2 writes intermediate examples for every mode and step plus their pytest
    coverage, runs them on 3.14t, and reports the pool types and lifecycle to the owner. S3 writes the Sphinx
    page, the release-note entry, closes the tickets and rebuilds last after a mailbox NOTICE to melder_0.
  EVIDENCE:
  - context_compass/system_docs/src_components_index.md:53-53
  - UX_and_AIX_experiences/AGENTS.md:1-44
  - context_compass/special_instructions/agent_contribution_guide.md:75-87
  IMPACT: The order puts source evidence before every example and every page; no `src/` change, so no notch.
  NEXT: Slice src_components.md "Component: Managed Spell Pools" (3860-3973) and read the pool sources whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T21:33:11Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1 closed. The probe runs on CPython 3.14.6t in the cloud workspace (the device VM has no 3.14 and no
    route to fetch one); the tree crosses as tarballs in the gitignored build/melder_2_mirror/. Two findings
    travel with the epic: stale failure-mode text in src_architecture/src_components (melder_0 holds them; told in
    M2-15) and the root-held consumer RISK (owner walkthrough). S2 started.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-18_managed_spell_lifecycle_map_story.md
  IMPACT: Tranche order holds: S2 examples, then S3 page and rebuild after melder_0's rebuild.
  NEXT: S2 lesson 42.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T22:03:37Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-201 (melder_0's ACK of M2-15, 21:53:02Z) consumed: (1) melder_0 sweeps UX_and_AIX_experiences/ and
    docs/ for one object bound twice and tells this lane before it edits either; (2) it corrects the stale
    release-after-teardown text in src_architecture and src_components in its docs pass if the P08/P19 reading
    holds; (3) it holds release_docs/next_version_release.md until its rebuild - this lane adds its entry after
    melder_0's rebuild-done NOTICE, which also starts this lane's rebuild. Sent M2-16: the 17 pre-existing
    example-harness failures (S2 MEASURE note), this lane's new files in UX_and_AIX_experiences/, and a promise
    to name the exact docs/ files before S3 edits them.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_ux_examples_story.md:171-196
  IMPACT: S3's page may be written now, after a NOTICE naming its docs/ files; its release-note entry and the
    rebuild wait for melder_0's rebuild-done NOTICE (tranche order unchanged, one rebuild per lane).
  NEXT: The owner walkthrough of the pool types and the lifecycle; S2 closure; then S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T23:07:51Z
  AUTHOR: melder_2
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Epic closed on the owner's directive (chat, 2026-10-18T23:01Z: "ok please finish all those things off and
    skip build assets and llm bundles its not required since other agents are working"). S1 mapped the managed
    pool lifecycle from source with a 19-case probe; S2 added intermediate lessons 42-48 and 34 contract probes,
    green on 3.14t with the GIL off and on (rerun green on the current tree at closure); S3 added the Sphinx chapter
    docs/intermediate/managed-spells.md (docs checks green, 313 pages) and one release-note bullet. No src/ change,
    no notch. The exit gate's rebuild of build assets and LLM bundles is waived by the owner and was not run;
    melder_0's rebuild carries this lane's docs and release-note changes (M0-203, M2-19). Open after closure: (1)
    the owner's answer on the root-held consumer teardown order (S1 RISK) - the chapter and lesson 47 document
    today's behaviour and the way around it; (2) the stale failure-mode text in src_architecture.md:2529-2531 and
    src_components.md:3951-3952 - a registry release after root teardown raises the not-managed ValueError, not the
    RuntimeError - which melder_0 holds and corrects in its docs pass (M0-201); (3) the 17 pre-existing
    example-harness failures, which belong to melder_0's one-object rewrite (M2-16, M0-202, M0-203).
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_lifecycle_map_story.md:305-318
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_ux_examples_story.md:198-217
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_sphinx_docs_story.md:352-372
  - context_compass/system_docs/src_architecture.md:2529-2531
  - context_compass/system_docs/src_components.md:3951-3952
  IMPACT: Managed spell pools are taught end to end - runnable lessons, contract probes and a page in the site's
    navigation; the generated assets stay stale until melder_0's rebuild, as the owner accepted.
  NEXT: None for this lane; the open items sit with the owner and melder_0.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
Scope: examples, tests and a Sphinx page for `Existence.managed_spell_quantity`; no `src/` change. State: done -
S1 (lifecycle map), S2 (lessons 42-48, 34 probes, green on 3.14t GIL off and on, rerun green at closure) and S3
(chapter docs/intermediate/managed-spells.md, docs checks green, release-note bullet) are closed; the closing
rebuild was waived by the owner and melder_0's rebuild carries the changes. Open: the owner's answer on the
root-held consumer teardown order; the stale failure-mode text in src_architecture and src_components
(melder_0, M0-201); the 17 pre-existing harness failures (melder_0's one-object rewrite).
Update this view in place. Preserve historical Notes/comments and link unchanged context/full evidence.

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
