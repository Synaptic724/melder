"""File S6 (explicit duplicate binding) and the parked configurables epic (melder_0, 2026-10-18).

Run from context_compass/ after record_duplicate_options.py, which leaves its timestamp in /tmp/m0_mq/T.txt.
Refuses to overwrite either ticket.
"""
import pathlib
import sys

T = pathlib.Path("/tmp/m0_mq/T.txt").read_text(encoding="utf-8").strip()
EPIC = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
S1 = "tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md"
STORY = pathlib.Path("tickets/stories/2026-10-18_explicit_duplicate_binding_story.md")
BACKLOG = pathlib.Path("tickets/epics/backlog/2026-10-18_identity_and_caching_configurables_epic.md")


def note_range(path, datetime_line, nth=1):
    """Lines of the nth Note opened by `datetime_line`, through its SCORE line (1-based, inclusive)."""
    lines = pathlib.Path(path).read_text(encoding="utf-8").split("\n")
    starts = [i for i, line in enumerate(lines) if line == datetime_line]
    if len(starts) < nth:
        sys.exit(f"note {datetime_line!r} #{nth} not found in {path}")
    start = starts[nth - 1]
    end = next(i for i in range(start, len(lines)) if lines[i].startswith("  SCORE_0_TO_10:"))
    return f"{start + 1}-{end + 1}"


STRATEGY = note_range(EPIC, f"- DATETIME: {T}")
DECISION = note_range(EPIC, "- DATETIME: 2026-10-18T14:14:10Z")
CORPUS = note_range(S1, "- DATETIME: 2026-10-18T12:45:46Z")
EDGES = note_range(S1, "- DATETIME: 2026-10-18T13:30:00Z", 1)

TAIL = """## Project-Specific Additions
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
"""

STORY_TEXT = """# Story: explicit_duplicate_binding - a bind that says so registers one object more than once

## Metadata
- Story ID: STORY-2026-10-18-explicit_duplicate_binding
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: draft
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: {T}
- Updated: {T}

## User Narrative
As an agent working in Melder, I want to register one object more than once when I say so - for example a
`Worker` class kept as a shared `unique` named `shared` and as a `many` named `fresh`, or three bindings of one
settings class - and call each by its name, so that I can keep several bindings of the same code while an
accidental second registration is still refused.

## Value / MRP Alignment
S1 makes the spell_id the object's code, so a second registration of the same object is refused. Today one class
binds once per binding name, because the binding name is hashed. Without an explicit path S1 would take that
away; with it, duplication is a choice the bind writes down and Melder records, not a side effect of a name.

## Ticket Contract
- ENTRY_GATE: the owner's choice of the form and the option's name (Open Questions); the epic's architecture patch
  and S1's patches updated for it and approved; the board row.
- EXECUTION_BOUNDARY: the duplicate option on `Spellbook.bind`, `Spellbook.bind_inactive`, the Conduit facades,
  `scan_bind` and `SpellBinder`; its place in the spell_id (S1's digest); the Spell's record of it; the
  SpellCrystal field and the restore and graft replay; the refusal text that names it. Not the binding manifest
  (S2), revalidation (S3), the one-registration refusals themselves (S4) or the migration (S5).
- DEPENDENCIES: S1 (lands with it); S2 (the binding manifest stays apart from the scope); S5 (the record version).
- EXIT_GATE: the acceptance criteria as regression tests with the GIL off and on; docs; S1's notch and rebuild.
- FAILURE_ESCALATION: DECISION_REQUEST for the form, the name and the binding-name default; CONFLICT if a needed
  file is held by another lane.

## Requirements (Functional)
- Pending the owner's choice. The recommended form (the epic's STRATEGY_DISCUSSION note of {T}):
- `duplicate_scope=<str>` on bind and bind_inactive, the Conduit facades, `scan_bind` and `SpellBinder`: the scope
  joins the spell_id - the SHA256 of the code and the scope - so each scope of one object is its own spell; no
  scope keeps the plain code id.
- The Spell keeps its scope and its plain code id, so the copies of one object can be listed together.
- The same object with the same scope twice is refused like any duplicate; an unscoped second registration is
  refused with a message that names the existing registration and the option.
- When no binding name is given, the binding name is the scope, so each copy has its own address and is melded
  by it.
- The record keeps the scope; restore and graft replay it through the bind verbs.

## Requirements (Non-Functional)
- Nothing at meld; one string more in the hash at bind.
- The scope is identity, not binding: it is not part of S2's binding manifest, and a binding change (S3) never
  moves it.

## Scope Boundaries
- In scope: the option on the bind verbs and their facades, the spell_id input, the Spell field, the record field
  and replay, the refusal text, tests and docs.
- Out of scope: a scoped block (`with spellbook.duplicate_scope(...)`), a strict switch refusing duplicates and
  stacked scan declarations - parked in EPIC-2026-10-18-identity_and_caching_configurables; old records holding
  one object twice (S5 restores the first, the owner's decision).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: filed from the owner's direction (the epic's DECISION note of 2026-10-18T14:14:10Z); the form
  is with him.

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-spell_id_hashes_the_object_code (S1; lands with this story)
- STORY-2026-10-18-binding_manifest_hash (S2)
- STORY-2026-10-18-one_registration_per_object (S4; its refusal names this option)
- STORY-2026-10-18-spell_id_migration (S5; the record version)
- EPIC-2026-10-18-identity_and_caching_configurables (backlog; the scoped block and the strict switch)

## Tasks (Implementation Checklist)
- [ ] Task: the owner's choice of the form and the name.
- [ ] Task: the design in the epic's patch folder - the architecture patch's formula and one-object invariant, the
  Binding Pipeline component patch, the code-description patch's spell_id rule.
- [ ] Task: red regression tests, then the implementation with S1.
- [ ] Task: docs and the release-note entry with S1.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- `bind(spell=Worker, existence="unique", binding_name="shared")`, then `bind(spell=Worker, existence="many",
  duplicate_scope="fresh")`, give two spells: `meld(spell=Worker, binding_name="fresh")` builds a new Worker each
  time and `meld(spell=Worker, binding_name="shared")` returns the shared one.
- A second `bind(spell=Worker, ...)` with no scope is refused, naming the first registration and the option.
- The same scope twice is refused; a scoped copy's spell_id is the same across processes and GIL modes.
- A recorded world with scoped copies restores and grafts with each copy and its scope.

## Validation / Test Plan
- Symptom-named tests such as `test_a_second_bind_of_one_class_is_refused_without_a_scope`,
  `test_two_scopes_of_one_class_are_two_spells_called_by_name` and `test_a_scoped_copy_restores_with_its_scope`;
  the GIL off and on; the whole tree in a /tmp mirror before landing.

## UX / API / Data Notes
- A new keyword on the bind verbs (name pending), additive. With S1 it replaces the implicit way to bind one class
  twice - another binding name - which S1 removes; part of S1's Breaking entry.

## Risks / Mitigations
- A parameter typed with the class sees every copy: AMBIGUOUS_PROVIDER at conjure unless a SpellMap default picks
  one, as two binding names of one class do today; the message names the remedy.
- An unfiltered managed release of a class with two managed copies asks for `spell_id=`, as today.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- DECISION_REQUEST (owner): the form - (1) an option whose scope joins the spell_id (recommended), (2)
  `duplicate=True` with the address in the spell_id, (3) a scoped block, (4) a Book setting (the epic's
  STRATEGY_DISCUSSION note of {T}); the option's name (`duplicate_scope`, from his words, or another); the
  binding name defaulting to the scope (recommended).

## Decision Log
- {T}: filed as S6 from the owner's direction (the epic's DECISION note of 2026-10-18T14:14:10Z); four forms
  with him (the epic's STRATEGY_DISCUSSION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none yet (the design goes into system_docs/patches/active/spell_identity_is_the_code_2026_10_18/)
- DISPOSITION: promote_to_documentation (the patch docs, at landing)
- CLEANUP_TRIGGER: at landing the design is promoted with S1's

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - one object bound more than once, on purpose
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed {T}.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: {T}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Filed from the owner's direction: "we do want the option for users to bind multiple objects twice like 3
    different versions of the configuration so a user can just call it ... by adding a configurable bind action
    such that we can capture that scope and still allow duplication but it has to be explicit" (chat 2026-10-18).
    The four forms, the code read for them and the recommendation are in the epic's STRATEGY_DISCUSSION note;
    the design joins S1's patches once the owner picks the form and the name.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:{DECISION}
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:{STRATEGY}
  IMPACT: This story lands with S1, or S1 removes today's way to bind one class twice with nothing in its place.
  NEXT: The owner's choice of the form and the name.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: an explicit bind option that registers one object more than once, its scope recorded; lands with S1.
- State: draft (melder_0). Four forms are with the owner, (1) recommended (the epic's STRATEGY_DISCUSSION note of
  {T}); nothing designed in the patches or written in src/ yet.
- Next: (1) the owner's choice of the form and the name; (2) the design in S1's patch folder; (3) red tests and
  the implementation with S1.

"""

BACKLOG_TEXT = """# Epic: identity_and_caching_configurables - what a user sets about how deeply Melder reads objects and how it caches, and what we advise

## Metadata
- Epic ID: EPIC-2026-10-18-identity_and_caching_configurables
- Status: draft
- Owner: user
- Agent Name: unassigned (parked; filed by melder_0)
- Agent Role: UNKNOWN (no executor while parked)
- Priority: p3
- Created: {T}
- Updated: {T}
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
- {T}: filed and parked on the owner's direction (chat 2026-10-18; the identity epic's DECISION note of
  2026-10-18T14:14:10Z).

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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed {T}.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: {T}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-18), quoted under Problem / Opportunity: installed third-party code
    is named by version (B) for now; a configurable for it - and for caching, for how deeply Melder reads objects,
    and for what we advise - goes into this parked epic, to think about after.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:{DECISION}
  IMPACT: Nothing here is built until the owner takes it out of the backlog; the identity epic's rules are the
    defaults every idea varies.
  NEXT: The owner takes the epic out of the backlog and picks the ideas.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: {T}
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
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md:{CORPUS}
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md:{EDGES}
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:{STRATEGY}
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

"""


def fill(text):
    return (text.replace("{T}", T).replace("{STRATEGY}", STRATEGY).replace("{DECISION}", DECISION)
            .replace("{CORPUS}", CORPUS).replace("{EDGES}", EDGES))


for path, text in ((STORY, STORY_TEXT), (BACKLOG, BACKLOG_TEXT)):
    if path.exists():
        sys.exit(f"refusing to overwrite {path}")
    path.write_bytes((fill(text) + TAIL).encode("utf-8"))
    print("filed", path)
print("ranges: strategy", STRATEGY, "decision", DECISION, "corpus", CORPUS, "edges", EDGES)
