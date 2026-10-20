# Epic: identity_and_caching_configurables - how deeply Melder reads objects, how it caches, and what we advise

## Metadata
- Epic ID: EPIC-2026-10-18-identity_and_caching_configurables
- Status: draft
- Owner: user
- Agent Name: unassigned (parked; filed by melder_0)
- Agent Role: UNKNOWN (no executor while parked)
- Priority: p3
- Created: 2026-10-18T14:33:32Z
- Updated: 2026-10-18T14:33:32Z
- Target Window: UNKNOWN (parked: "we can think about it after", the owner, chat 2026-10-18)
- Related Program/Initiative: EPIC-2026-10-18-spell_identity_is_the_code (its decisions are the defaults here)

## Problem / Opportunity
The owner (chat 2026-10-18), deciding how S1 treats installed third-party code: "B I think this is reasonable but
this should maybe become a configurable on a spellbook that we can remember add this as an epic to explore how
caching configuration and bind configuration could do stuff we can think about it after ( think this could become
a caching configurable)"; and in the same message: "add an epic with configurable ideas for the user in terms of
caching and complexity of how deeply we understand objects and whats advised".

The identity epic fixes one rule for everyone: the application's code is digested, installed packages are named by
qualified name and distribution version (B), an existing object's data is read whole. Users will want other points
on that scale - deeper for a package they edit, shallower for objects that carry per-process state - and a say in
how the creation cache keys and keeps what it builds. This epic collects those ideas, their costs and what we
would advise, for the owner to pick from later.

## MRP Alignment (Most Reasonable Product)
A setting that changes identity changes structure, so each one needs a contract: who may set it, where it lives,
how it is recorded so a restore computes the same ids, and what goes wrong at each value. Fewer settings with clear
advice beat many knobs that let one object have two ids in one process.

## Ticket Contract
- ENTRY_GATE: the owner takes this epic out of the backlog and picks the ideas to build;
  EPIC-2026-10-18-spell_identity_is_the_code has landed (its rules are the defaults these settings vary).
- EXECUTION_BOUNDARY: design only until then - the configuration surfaces (AetherConfiguration, the frame posture,
  SpellbookConfiguration, bind options), the identity digest's depth, the creation cache's policy, and advice
  (presets, warnings). No src/ edit from this epic while it is parked.
- DEPENDENCIES: EPIC-2026-10-18-spell_identity_is_the_code (S1's digest, S2's binding manifest, S3's revalidation,
  S6's explicit duplicates).
- EXIT_GATE: the owner's selection; a story per selected idea, each landed with tests, docs, notch and rebuild.
- FAILURE_ESCALATION: DECISION_REQUEST for where an identity setting lives (process, frame or Book); RISK for any
  setting that can give one object two ids in one process.

## Goals (Outcomes)
- A user can choose how deeply Melder reads an object for its identity, within limits that keep one object one
  spell in a process.
- A user can choose how the creation cache keys, keeps and drops what it builds.
- Melder advises: named presets with measured costs, and warnings for settings that cost correctness or speed.

## Non-Goals (Explicit Exclusions)
- Changing the identity epic's defaults (they stand until the owner picks otherwise here).
- Anything on the warm meld path.
- The managed pool's release routing.

## Scope Boundaries
- In scope: the ideas in the PLAN note, their contracts and costs, where each setting lives and how it is recorded.
- Out of scope: everything under Non-Goals.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: filed and parked on the owner's word ("we can think about it after").

## Success Metrics
- Each setting states its default, its cost (measured: bind time and cache hit rate) and its risk.
- No setting makes one object two spells in one process unless the user binds it twice on purpose (S6).

## Requirements (Functional + Non-Functional)
- Identity settings are recorded with the world (the Crystallizer record), so a restore under other settings
  reports the difference instead of silently minting other ids.
- Settings are read at bind or conjure, never at meld.

## Constraints / Assumptions
- Under the default process-wide spell-id regime two Books that bind one object must compute one id, so an
  identity setting held per Book could give one object two ids; identity settings belong to the process
  (AetherConfiguration) or to the frame (under per-frame ids). The owner suggested a Spellbook setting: open is
  whether a Book setting may only tighten, must agree with the process, or covers caching only.

## Dependencies / External References
- tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
- system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md
- artifacts/spell_identity_20261018/runs/ (the digest's measured costs)

## Milestones (Track Progress)
- [ ] Milestone 1: the owner picks the ideas to build.
- [ ] Milestone 2: a story per picked idea, designed with patch docs.
- [ ] Milestone 3: landed with tests, docs, notches and the rebuild.

## Stories (Required to Complete)
- None filed while parked. Candidates, one per idea in the PLAN note:
- [ ] Candidate C1: identity depth - outline, code (the default) or deep.
- [ ] Candidate C2: installed packages - named by version (the default, B), digested (A), or digested for a
  listed set of packages.
- [ ] Candidate C3: object data depth - whole (the default), shallow or type only; size and depth limits; fields
  left out per class.
- [ ] Candidate C4: creation cache policy - on or off, its keys, when it is dropped, how much it keeps.
- [ ] Candidate C5: binding changes - which manifest fields rebuild plans and which only rebind (S3's rule as a
  setting).
- [ ] Candidate C6: explicit duplicates - the scoped block and a strict switch (S6's follow-ups).
- [ ] Candidate C7: presets and the advisor.
- [ ] Candidate C8: the settings recorded with the world, and a mismatch reported at restore.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: the owner's selection when he takes the epic out of the backlog.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Every picked idea landed with its default, cost and advice documented; the rest recorded as declined.

## Risks / Mitigations
- One object, two ids: identity settings at process or frame level only (Constraints); mismatches reported at
  restore (C8).
- Settings nobody understands: presets first, each with its measured cost (C7).
- Cache misses from identity that reads per-process state (a lock, a logger, a pid in an object's data): the
  advisor warns at bind (C7); per-class exclusions (C3).

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Per picked idea: the identity epic's probes run under each value; the gauntlet's bind-heavy worlds for cost.

## Rollout / Adoption Plan
- Parked. When taken out: presets and the advisor first (C7), then the settings the owner picks.

## Open Questions
- Where an identity setting lives: process, frame or Book (Constraints).
- Whether "remember" means the settings recorded with the world (C8) or a saved per-Book profile.
- Which presets: for example strict (deep identity, duplicates refused), balanced (the identity epic's defaults)
  and fast (outline identity, the cache kept longest).

## Decision Log
- 2026-10-18T14:33:32Z: filed and parked on the owner's direction (chat 2026-10-18; the identity epic's
  DECISION note of 2026-10-18T14:14:10Z).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none (the costs cited are the identity epic's runs, rowed under its story)
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none while parked

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - identity depth, caching policy and the advice that goes with them
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-10-18T14:33:32Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-18T14:33:32Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-18), quoted under Problem / Opportunity: installed third-party code
    is named by version (B) for now; a configurable for it - and for caching, for how deeply Melder reads objects,
    and for what we advise - goes into this parked epic, to think about after.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:436-461
  IMPACT: Nothing here is built until the owner takes it out of the backlog; the identity epic's rules are the
    defaults every idea varies.
  NEXT: The owner takes the epic out of the backlog and picks the ideas.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T14:33:32Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The ideas, with costs measured for the identity epic (3.14.7t) and what we would advise.
    C1 identity depth: outline - today's rule (names, bases, method names, constructor signature), median 0.064 ms
    a bind, but an edited method body keeps the id and the edit is refused as a collision; code - S1's default,
    median 0.29 ms cold and 0.11 ms warm, p95 1.5 ms cold; deep - installed packages digested too, 2.6-3.2 ms cold
    for a class over a large third-party base (pygments' PythonLexer), and a package upgrade moves the ids. Advice:
    code; deep only where agents edit the package; outline only for worlds nobody edits.
    C2 installed packages: by name and version (B, the default), digested (A), or digested for listed packages -
    for a company package installed in site-packages that agents change (under B as proposed, an editable
    install counts as application code). Advice: B, plus the list where needed.
    C3 object data: whole (the default: slots and __dict__ by value, nested, cycle-safe), shallow, or type only
    (today's repr rule); size and depth limits; fields left out per class (a cache, a timestamp). Advice: whole,
    with exclusions for fields that hold per-process state - they make an id differ per process, so the cache
    misses and a restore mints other ids.
    C4 creation cache: on or off, keys (spell_id and binding hash after S2), what turns it cold (a release, an
    interpreter, a package version under B), how much it keeps and where. Advice: on.
    C5 binding changes: which manifest fields rebuild plans and which only rebind (S3's rule), or rebuild on any
    change (strict).
    C6 explicit duplicates: the scoped block `with spellbook.duplicate_scope(...)` and a strict switch refusing
    duplicates (S6's follow-ups).
    C7 presets and the advisor: strict, balanced (the identity epic's defaults) and fast, each with its measured
    cost; warnings at bind for a risky setting or object, shown like conjure(validation_warnings=True).
    C8 the settings recorded with the world (the Crystallizer record), a restore under other settings reported.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md:185-226
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md:228-249
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:463-523
  IMPACT: The owner has the menu, the costs and the advice in one place when he takes the epic up.
  NEXT: The owner's selection.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: configurables for identity depth, installed packages, object data, caching, binding changes and
  duplicates, with presets and advice (PLAN note).
- State: draft, parked in the backlog on the owner's word; no story filed, nothing built.
- Next: (1) the owner takes it out of the backlog and picks the ideas; (2) where identity settings live (Open
  Questions); (3) a story per picked idea, presets and the advisor first.

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
