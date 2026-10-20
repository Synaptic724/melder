"""Open EPIC-2026-10-18-spell_identity_is_the_code and its five stories (melder_0, 2026-10-18).

The owner's word (chat 2026-10-18): "if your going to implement anything please make an epic, document your stories
for it and lets hit that up next turn". Writes six new ticket files from the repository templates' sections; refuses
to overwrite an existing file. Usage (from context_compass/): open_epic.py <NOW>
"""
import pathlib
import sys

NOW = sys.argv[1]
EPIC_ID = "EPIC-2026-10-18-spell_identity_is_the_code"
EPIC_PATH = pathlib.Path("tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md")
S6_DONE = "tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"

ARTIFACT_NOTE = """Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket."""

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

STORY_NOTING = """## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.
"""

EPIC_NOTING = """## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.
"""

CLOSURE = """## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
"""

EPIC = f"""# Epic: spell_identity_is_the_code - a spell_id names the registered object's code; its binding is a manifest

## Metadata
- Epic ID: {EPIC_ID}
- Status: ready
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: {NOW}
- Updated: {NOW}
- Target Window: 2026-Q4
- Related Program/Initiative: Melder runtime correctness (the owner's direction, chat 2026-10-18); follows
  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool ({S6_DONE})

## Problem / Opportunity
A spell_id today is one SHA256 over two different things: a shallow outline of the registered object (for a class
its name, qualname, module, bases, MRO, field names, method names and constructor signature) and the bind call that
registered it (spellframe, binding name, existence, resolved disposal names, resolvable). The owner ruled this a
correctness bug (chat 2026-10-18): "the bind signature shouldn't impact the spells identity", "you could register the
same object n number of times for each existence this is a correctness bug big time", "the object's binding handle
shouldn't be part of its SHA256 hash", and the hash must read "the object registered its methods, its actual code not
its docstrings or comments", "the internal code inside the methods not just the superficial shit".

Proven on 0.2.8254 (probes, Artifact Links): a changed method body, a parameter added to a method and two lambdas
with different bodies get one spell_id today, and bind refuses an edited class as a collision; one class can be
registered once per binding name and staged once per existence, because each variant hashes differently.

The owner's design (chat 2026-10-18): the spell_id is the object's code; the bind signature gets its own hash in a
manifest associated with the object; when that binding hash changes, the object is revalidated.

## MRP Alignment (Most Reasonable Product)
Identity is structure, and structure is Melder's contract. One object must be one spell, a real code change must be a
new version an agent can stage and notch, and how a spell is kept - its address, lifetime, teardown, capability and
settings - must be a separate, recorded, revalidated binding rather than a hidden part of its name. Getting identity
right once removes duplicate registrations at the root, and the misrouting they caused, instead of patching each
consumer.

## Ticket Contract
- ENTRY_GATE: the owner's direction recorded (DECISION note); the stories filed; the active board row; per story,
  patch docs (an architecture patch for the epic, a component patch per story) linked and approved by the owner before
  any src/ edit; the owner's calls on the open edges (Open Questions) before STORY-2026-10-18-spell_id_hashes_the_object_code
  is implemented.
- EXECUTION_BOUNDARY: how a spell is identified and bound - bind's fingerprint and the binding profile, the binding
  manifest and its hash, the creation cache's keys, re-registration and revalidation, the staging refusals, and the
  migration (cache generation, record, research history, tests, docs). Excluded: the managed pool's release routing
  (set aside by the owner), melder_1's lanes and the other stories of EPIC-2026-10-17-correctness_defects.
- DEPENDENCIES: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (part A, 0.2.8254, done);
  melder_1 releasing the files it holds (spellbook.py, conduit.py, spell.py, restore_engine.py, graft_runner.py) for
  the stories that touch them; the owner's calls.
- EXIT_GATE: every story accepted; one notch per landed source change with its release-note entry; the system
  documents and the graph; the rebuild last with both checks OK; board and artifact sync; the owner's disposition.
- FAILURE_ESCALATION: DECISION_REQUEST for each edge the owner has not called; CONFLICT when a needed file is held by
  another lane; BLOCKER if a cache, record or restore path cannot keep its contract under the new identity.

## Goals (Outcomes)
- A spell_id is the SHA256 of the registered object's code - its methods and constructor: signatures, defaults,
  annotations and the instructions inside their bodies, nested code included - and nothing from the bind call.
- Docstrings, comments and formatting never change a spell_id; any real code change does.
- One object is one spell: registering it again, under any name or existence or as a staged version, is refused.
- The bind signature is a binding manifest on the spell with its own SHA256; a changed binding hash revalidates the
  spell and everything that depends on it.

## Non-Goals (Explicit Exclusions)
- The managed pool's release routing (the owner set it aside; one registration per object removes its duplicates).
- Changing how versions coexist, notch or are followed by borrowers (the 2026-10-14/15 rulings stand).
- melder_1's lanes and the other correctness stories.

## Scope Boundaries
- In scope: Bind and the binding profile, the Spell's binding manifest, the SpellCrystal record, the creation cache's
  structural and executor tiers, Creations' entries on re-registration, SpellSystemStates revalidation marks, the
  Spellbook/Conduit staging verbs and a binding-change verb, restore and graft, MutationResearch's spell_id
  references, docs and tests.
- Out of scope: everything under Non-Goals.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the owner's direction and his instruction (chat 2026-10-18) to make an epic with its stories and
  start next turn; the five stories are filed with their open questions.

## Success Metrics
- The prototype's cases (P1-P10, I1-I9) hold in src/: real code changes move the spell_id; docstrings, comments and
  blank lines do not; byte-identical across processes and GIL modes.
- No object can be registered twice in one scope.
- A binding change always revalidates: no plan, verdict, cache entry or stored object built for the old binding is
  used for the new one.

## Requirements (Functional + Non-Functional)
- Functional: the five stories' requirements.
- Non-functional: no source-file read at bind; the code hash computed once per class object; no new lock-order edge;
  warm meld paths unchanged; every spell_id moves once, documented as a Breaking change.

## Constraints / Assumptions
- melder_1 holds spellbook.py, conduit.py, spell.py, restore_engine.py and graft_runner.py; stories touching them wait
  for its release (mailbox, M0-193).
- Compiled instructions are specific to the Python version (and to -O); the creation cache is already admitted per
  release and interpreter.
- Device runs: `. ~/.melder_env`, TMPDIR under /tmp, the rebuild through a /tmp mirror.

## Dependencies / External References
- {S6_DONE}
- tickets/epics/2026-10-17_correctness_defects_epic.md
- src/melder/aether/spellbook/bind/bind.py (`Bind.sha256_profile`, `Bind.spell_id_inspector`)
- src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py
- src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py

## Milestones (Track Progress)
- [ ] Milestone 1: the owner's calls on the edges; the architecture patch and the first component patches approved.
- [ ] Milestone 2: the code hash and the binding manifest landed (S1, S2).
- [ ] Milestone 3: revalidation on binding change and one registration per object landed (S3, S4).
- [ ] Milestone 4: the migration, docs, notches and rebuild (S5); the owner's disposition.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-10-18-spell_id_hashes_the_object_code - the spell_id hashes the registered object's code
  (methods and constructor, bodies included; no docstrings or comments) and nothing from the bind call (S1).
- [ ] Story: STORY-2026-10-18-binding_manifest_hash - the bind signature becomes a binding manifest on the spell with
  its own SHA256, recorded, and part of the caches' keys beside the spell_id (S2).
- [ ] Story: STORY-2026-10-18-revalidate_on_binding_change - a changed binding hash revalidates the spell and its
  dependents; the store's entry follows the new binding; a verb changes a spell's binding in place (S3).
- [ ] Story: STORY-2026-10-18-one_registration_per_object - bind, bind_inactive and add_to_spell_index refuse an object
  already registered in scope, naming its registration (S4).
- [ ] Story: STORY-2026-10-18-spell_id_migration - every spell_id moves once: cache generation, record and restore,
  research history, tests, docs and the release note (S5).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: the owner's calls on the open edges (Open Questions).
- [ ] Task: the architecture patch for the epic; a component patch per story before its code.
- [ ] Task: complete each story above.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- All five stories accepted; the prototype's cases are regression tests in the suite; no object registers twice; a
  binding change revalidates; docs, notches and the rebuild; the owner's disposition.

## Risks / Mitigations
- Every spell_id moves once (records, caches, research history): one migration story, a cache generation, restore
  mapping and a Breaking release-note entry.
- Bind cost of hashing instructions: measured in S1; the digest is computed once per class object.
- A cache or store keyed by spell_id alone that misses a binding change: S2's patch inventories every spell_id-keyed
  cache and store before code.
- Overlap with melder_1's held files: the stories are sequenced; a mailbox NOTICE before each touch.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Each story: symptom-named regression tests, GIL off and on, the whole tree in a /tmp mirror before landing.
- The prototype probes re-run against src/ at each landing.

## Rollout / Adoption Plan
- Stories land S1 -> S2 -> S3 -> S4 -> S5 (S1 and S2 may land together, so the caches never see a spell_id without
  its binding hash); one notch per landed source change; the identity change is one Breaking entry in the running
  release note.

## Open Questions
- The owner's calls before S1's implementation: (1) inherited code - does a change in a base class's method move its
  subclasses' spell_ids (the prototype reads bases by name only)? (2) class-level values (e.g. `retries = 3` on the
  class) - part of the code? (3) an existing object bound as a spell - its class's code plus its data? (4) a renamed
  local variable - a code change (the prototype says yes)? (5) the scope of one registration - per process (today's
  default regime) or per frame?
- For S3: which binding fields revalidate and which only rebind (the managed settings rebind the pool without
  rebuilding plans since 0.2.8254).
- Left from S6, unproven: a spell disposed with managed objects out and registered again in another root leaves the
  old pool registered beside the new one; the pool following the spell is the proposed rule (pool routing is set aside
  by the owner).

## Decision Log
- {NOW}: opened on the owner's direction (DECISION note); five stories filed.

## Artifact Links (Optional)
{ARTIFACT_NOTE}

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_fingerprint_reads_code.py (F1-F5: what today's spell_id reads)
  - artifacts/correctness_defects_20261017/runs/probe_fingerprint_reads_code_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_fingerprint_reads_code_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_code_hash_prototype.py (P1-P10: the code-hash prototype)
  - artifacts/correctness_defects_20261017/runs/probe_code_hash_prototype_gil0_seed1.txt
  - artifacts/correctness_defects_20261017/runs/probe_code_hash_prototype_gil0_seed2.txt
  - artifacts/correctness_defects_20261017/runs/probe_code_hash_prototype_gil1_seed1.txt
  - artifacts/correctness_defects_20261017/runs/probe_code_hash_prototype_gil1_seed2.txt
  - artifacts/correctness_defects_20261017/probes/probe_code_hash_internals.py (I1-I9: changes inside a method body)
  - artifacts/correctness_defects_20261017/runs/probe_code_hash_internals_gil0_seed1.txt
  - artifacts/correctness_defects_20261017/runs/probe_code_hash_internals_gil0_seed2.txt
  - artifacts/correctness_defects_20261017/runs/probe_code_hash_internals_gil1_seed1.txt
  - artifacts/correctness_defects_20261017/runs/probe_code_hash_internals_gil1_seed2.txt
  - artifacts/spell_identity_20261018/ (the epic's scripts)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: at closure the probes stay as the design's evidence; each case becomes a regression test in its
  story

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a spell's identity (its code) versus its binding (how it is kept)
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probes); created {NOW}.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-18). Identity: "your blending 2 things the bind signature shouldn't
    impact the spells identity ... we should decouple these things"; "you could register the same object n number of
    times for each existence this is a correctness bug big time"; "the object's binding handle shouldn't be part of
    its SHA256 hash ... we only want to read the object registered its methods, its actual code not its docstrings or
    comments"; "the internal code inside the methods not just the superficial shit". Binding: "bind signature can get
    its own hash signature we could put into a manifest associated with an object and I think if that hash changes we
    should revalidate the object ... maybe it changes how we build things so we should also maintain this structure".
    Process: "please make an epic, document your stories for it and lets hit that up next turn". Recorded as five
    stories; S6 of EPIC-2026-10-17-correctness_defects is turned in with its part B superseded.
  EVIDENCE:
  - {S6_DONE}
  IMPACT: The spell_id formula, the binding record, the caches' keys, the registration rules and every recorded id
    change; one object becomes one spell.
  NEXT: The owner's calls on the open edges (Open Questions), then the architecture patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Where it starts, read and probed on 0.2.8254. `Bind.sha256_profile` hashes, for a class, its name, qualname,
    module, bases, MRO, field names, method names and constructor signature text, then the bind call's spellframe,
    binding name, existence and disposal names, in a hash domain chosen by resolvable; for a function its name,
    qualname, module, signature, parameter defaults, address-free repr and type. No method body is read, so F1 (a
    changed `run` body: one spell_id, bind refuses the edit as a collision), F2 (a parameter added to `run`) and F5
    (two lambdas with different bodies) collide today, while F3 (an `__init__` default) and F4 (a rename) do not.
    `bind_inactive` claims no address, so a class stages once per existence. The structural cache keys a payload by
    the spell_id because "the spell id already covers the spell's own signature, names, existence and
    resolvability". The prototype (outside src/) hashes the module, qualname, bases by name and, per function in the
    class body, the signature text and the `dis` instruction stream with resolved operands (no line numbers, no
    docstring constant, no unused constants): P1-P10 and I1-I9 behave as the owner wants, byte-identical across hash
    seeds and GIL modes.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:1011-1129
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:70-145
  - src/melder/aether/spellbook/spellbook.py:5423-5432
  - src/melder/aether/spellbook/spellbook.py:5754-5776
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:259-288
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_fingerprint_reads_code_gil0.txt:1-22
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_code_hash_prototype_gil0_seed1.txt:1-10
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_code_hash_internals_gil0_seed1.txt:1-22
  IMPACT: S1 has a working prototype to port; S2 must change the cache's key because the cache relies on the old
    spell_id covering the binding.
  NEXT: The owner's calls; then the architecture patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Order: (1) the owner's calls on the five edges; (2) the architecture patch (identity versus binding, the
    revalidation rule, the migration order, rollback) and the component patches of S1 and S2 for his approval; (3) S1
    and S2 together - the code hash, the binding manifest, the caches keyed by both - one notch; (4) S3 and S4 once
    melder_1 releases spellbook.py and conduit.py - revalidation on binding change, the binding verb, one registration
    per object; (5) S5 - the migration, docs, release note and the rebuild last. melder_1 told (M0-193).
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
  IMPACT: Nothing in src/ moves before the owner's calls and the approved patches.
  NEXT: Put the five calls to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

{CLOSURE}
{EPIC_NOTING}
## Context / Handoff Summary
- Scope: a spell_id becomes the SHA256 of the registered object's code (methods and constructor, bodies included; no
  docstrings, comments or line numbers); the bind signature becomes a binding manifest with its own SHA256 that
  revalidates the spell when it changes; one object is one spell; every spell_id moves once.
- State: ready (melder_0), discovery. Five stories filed (S1-S2 ready, S3-S5 draft); nothing in src/ yet. Evidence:
  the probes in Artifact Links. S6 of the correctness epic is turned in; its part B and open items live here.
- Next: (1) the owner's five calls (Open Questions); (2) the architecture patch and the S1/S2 component patches;
  (3) S1 and S2.

{TAIL}"""


def story(slug: str, title: str, status: str, priority: str, narrative: str, value: str, contract: str,
          functional: str, nonfunctional: str, scope_in: str, scope_out: str, related: str, tasks: str,
          acceptance: str, validation: str, ux: str, risks: str, questions: str, handoff: str) -> str:
    """One story in the repository's story template."""
    return f"""# Story: {slug} - {title}

## Metadata
- Story ID: STORY-2026-10-18-{slug}
- Epic: {EPIC_ID}
- Status: {status}
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: {priority}
- Created: {NOW}
- Updated: {NOW}

## User Narrative
{narrative}

## Value / MRP Alignment
{value}

## Ticket Contract
{contract}

## Requirements (Functional)
{functional}

## Requirements (Non-Functional)
{nonfunctional}

## Scope Boundaries
- In scope: {scope_in}
- Out of scope: {scope_out}

## State Transition Event
- from_state: draft
- to_state: {status}
- transition_reason: filed under {EPIC_ID} on the owner's direction (chat 2026-10-18){'' if status == 'draft' else '; scope and owner set, the open questions named'}.

## Dependencies / Related Work
{related}

## Tasks (Implementation Checklist)
{tasks}
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
{acceptance}

## Validation / Test Plan
{validation}

## UX / API / Data Notes
{ux}

## Risks / Mitigations
{risks}

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
{questions}

## Decision Log
- {NOW}: filed under {EPIC_ID} (the epic's DECISION note).

## Artifact Links (Optional)
{ARTIFACT_NOTE}

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none yet (the design's probes are rowed under the epic)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: rows are added when this story produces its own artifacts

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a spell's identity (its code) versus its binding (how it is kept)
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed {NOW}.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Filed from the owner's direction (the epic's DECISION note of {NOW}); the evidence it starts from is the
    epic's FACT note and its probes. Nothing in src/ moves before this story's component patch is approved.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
  IMPACT: The scope, requirements and acceptance above are the plan the patch docs refine.
  NEXT: {handoff.splitlines()[-1].split(': ', 1)[-1] if handoff else 'the component patch'}
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

{CLOSURE}
{STORY_NOTING}
## Context / Handoff Summary
{handoff}

{TAIL}"""


S1 = story(
    "spell_id_hashes_the_object_code",
    "the spell_id is the SHA256 of the registered object's code",
    "ready", "p1",
    "As an agent iterating on a class in Melder, I want its spell_id to change exactly when its code changes - a method\n"
    "body, a parameter, a default, the constructor - and never for a docstring, a comment, a blank line or how it was\n"
    "bound, so that every real edit is a new version I can stage and notch, and the same code is always the same spell.",
    "Identity is structure. Today's hash misses method bodies (the epic's F1, F2, F5: an edited class is refused as a\n"
    "collision) and folds in the bind call (the n-registrations bug). Hashing the object's code, and only that, fixes\n"
    "both at the root.",
    "- ENTRY_GATE: the owner's calls on the epic's open edges (inherited code, class-level values, existing objects,\n"
    "  local renames, scope); the epic's architecture patch and this story's component patch approved; the board row.\n"
    "- EXECUTION_BOUNDARY: `Bind.sha256_profile` and `Bind.spell_id_inspector` (their inputs), the binding profile\n"
    "  strategy (a code digest per class or function, computed once per object), the hash domain (a new version tag);\n"
    "  its tests and docs. Not the binding manifest or the caches (S2), revalidation (S3), the refusals (S4) or the\n"
    "  migration (S5).\n"
    "- DEPENDENCIES: the epic; the prototype probes; S2 lands with it.\n"
    "- EXIT_GATE: the prototype's cases P1-P10 and I1-I9 are regression tests passing with the GIL off and on and\n"
    "  across hash seeds; bind's cost measured against today's; the docs and the graph.\n"
    "- FAILURE_ESCALATION: DECISION_REQUEST for an edge the owner has not called; RISK if bind's cost regresses\n"
    "  materially; CONFLICT if a needed file is held.",
    "- A class's spell_id hashes its module, qualname and bases (per the owner's inherited-code call) and, for every\n"
    "  function its body defines - methods, the constructor, static and class methods, property accessors - the\n"
    "  signature text (parameters, defaults, annotations; memory addresses removed) and the instruction stream with each\n"
    "  operand resolved to its value; nested code (functions, lambdas, comprehensions) is hashed the same way.\n"
    "- Line numbers, docstrings (the constant 3.14 flags with CO_HAS_DOCSTRING), comments and unused constants never\n"
    "  enter it; raw bytecode is not hashed, because a docstring shifts every constant index in it.\n"
    "- A function or lambda hashes its module, qualname, signature and instructions; a decorated function hashes the\n"
    "  function it wraps (`inspect.unwrap`).\n"
    "- An existing object hashes as the owner calls it (its class's code plus its data is the proposal).\n"
    "- Nothing from the bind call enters it: spellframe, binding name, existence, disposal names, resolvable and the\n"
    "  managed settings move to the binding manifest (S2).",
    "- No source-file read at bind; the digest is computed once per class object (a class object's code does not\n"
    "  change) and reused.\n"
    "- Address-free and deterministic: byte-identical across processes, hash seeds and GIL modes.\n"
    "- Bind's cost measured before and after on the gauntlet's bind-heavy worlds.",
    "Bind's fingerprint inputs, the binding profile's code digest, `spell_id_inspector`, tests and docs.",
    "the binding manifest and the caches (S2), revalidation (S3), the refusals (S4), the migration (S5).",
    f"- {EPIC_ID}\n- STORY-2026-10-18-binding_manifest_hash (lands with this story)\n- STORY-2026-10-18-spell_id_migration",
    "- [ ] Task: the owner's calls (the epic's Open Questions).\n"
    "- [ ] Task: the component patch (Binding Pipeline: the code digest; the hash domain).\n"
    "- [ ] Task: red regression tests from P1-P10 and I1-I9.\n"
    "- [ ] Task: implement and measure bind's cost.\n"
    "- [ ] Task: docs, graph, notch (with S2) and the rebuild last.",
    "- A changed method body, a parameter added to a method, a changed default, a renamed method and two lambdas with\n"
    "  different bodies each give a different spell_id; a comment, a reworded or added docstring and blank lines give\n"
    "  the same one.\n"
    "- Binding the same class under two binding names gives one spell_id (S4 refuses the second registration).\n"
    "- The ids are identical across processes and GIL modes.",
    "- Symptom-named tests such as `test_editing_a_method_body_changes_the_spell_id`,\n"
    "  `test_a_docstring_or_comment_does_not_change_the_spell_id` and\n"
    "  `test_two_lambdas_with_different_bodies_are_two_spells`; a subprocess test for stability across hash seeds; the\n"
    "  epic's probes re-run on src/; the whole tree with the GIL off and on.",
    "- **Breaking change** (with S5): every spell_id moves once; the same object always has the same spell_id.",
    "- Ids differ per Python version and under -O (compiled instructions): document it; the cache is already per\n"
    "  interpreter.\n- A closure's captured values are not code: decide with the owner if a factory-made class counts.\n"
    "- Bind's cost: memoize per class object; measure.",
    "- The epic's five calls, foremost inherited code and existing objects.",
    "- Scope: the spell_id hashes the registered object's code only.\n"
    "- State: ready (melder_0); waiting on the owner's calls and the patches.\n"
    "- Next: the component patch after the owner's calls.",
)

S2 = story(
    "binding_manifest_hash",
    "the bind signature becomes a binding manifest with its own SHA256",
    "ready", "p1",
    "As an agent, I want how a spell is kept - its address, lifetime, teardown, capability and settings - recorded as a\n"
    "binding manifest with its own SHA256 beside the spell_id, so that Melder knows exactly when a spell's binding\n"
    "changed and never reuses what it built for the old binding.",
    "Once the spell_id is the code (S1), the binding needs its own identity: the creation cache and the record rely on\n"
    "the spell_id covering the binding today (`StructuralSnapshot.structural_key`: \"the spell id already covers the\n"
    "spell's own signature, names, existence and resolvability\"). The owner's design keeps that structure as a manifest.",
    "- ENTRY_GATE: S1's component patch approved; this story's component patch approved; melder_1's release of spell.py\n"
    "  (the Spell carries the manifest); the board row.\n"
    "- EXECUTION_BOUNDARY: the binding manifest and its hash (Bind builds it, the Spell carries it, `describe` shows\n"
    "  it), the SpellCrystal record, the creation cache's structural key and world stamp, the cache generation; tests\n"
    "  and docs. Not revalidation (S3).\n"
    "- DEPENDENCIES: S1 (lands with it); melder_1's release of spell.py.\n"
    "- EXIT_GATE: a binding change without a code change misses both cache tiers; the record round-trips the manifest;\n"
    "  byte-identical across processes; docs.\n"
    "- FAILURE_ESCALATION: CONFLICT while spell.py is held; DECISION_REQUEST on which fields the binding hash covers.",
    "- The manifest holds the spellframe (with its kind and contract), the binding name, the existence, the resolved\n"
    "  disposal names in order, resolvable and the managed settings; its binding hash is a SHA256 over it, address-free\n"
    "  and deterministic.\n"
    "- The Spell carries the manifest and its hash; `Spell.describe` and the record (the SpellCrystal) show both.\n"
    "- The structural cache keys a payload by spell_id and binding hash, and the world stamp carries every spell's\n"
    "  binding hash, so the executor tier's full hit needs them too; a cache generation retires the old bundles.\n"
    "- Nothing else identifies a spell by its binding.",
    "- No new lock; the hash is computed once at bind.\n- Byte-identical across processes and GIL modes.",
    "the manifest, its hash, the record and the caches' keys.",
    "revalidation and the store (S3), the refusals (S4), the migration (S5).",
    f"- {EPIC_ID}\n- STORY-2026-10-18-spell_id_hashes_the_object_code\n- STORY-2026-10-18-revalidate_on_binding_change",
    "- [ ] Task: the component patch (Binding Pipeline: the manifest; the creation cache's keys; the record).\n"
    "- [ ] Task: inventory every spell_id-keyed cache and store (it feeds S3).\n"
    "- [ ] Task: red tests; implement; docs; notch with S1; the rebuild last.",
    "- Changing only a spell's existence, disposal list, address or resolvable changes its binding hash and not its\n"
    "  spell_id, and the next conjure misses both cache tiers for it.\n"
    "- The record carries the manifest and a restore replays it.",
    "- `test_changing_only_the_binding_changes_the_binding_hash_not_the_spell_id`,\n"
    "  `test_a_binding_change_misses_the_creation_cache`; the record round-trip; GIL off and on.",
    "- `Spell` gains the manifest and its binding hash (read-only).",
    "- A cache or store keyed by spell_id alone is missed: the inventory task lists them before code.",
    "- Which managed settings belong to the binding hash, or to a pool-only setting (S3's question).",
    "- Scope: the binding becomes a manifest with its own SHA256, recorded and part of the caches' keys.\n"
    "- State: ready (melder_0); waiting on S1's patch and melder_1's release of spell.py.\n"
    "- Next: the component patch with S1's.",
)

S3 = story(
    "revalidate_on_binding_change",
    "a changed binding hash revalidates the spell and its dependents",
    "draft", "p1",
    "As an agent changing how a spell is kept - its lifetime, teardown, address or capability - I want Melder to\n"
    "revalidate that spell and everything that depends on it, so that no plan, verdict, cache entry or stored object\n"
    "built for the old binding is used for the new one.",
    "The owner's rule: \"if that hash changes we should revalidate the object\". A binding change can change what a\n"
    "spell is built as (existence), how it is torn down (disposal names), who resolves it (address: Phase 3 matches\n"
    "categories by spellframe) and whether it is built at all (resolvable).",
    "- ENTRY_GATE: S1 and S2 landed; this story's component patch approved; melder_1's release of spellbook.py and\n"
    "  conduit.py; the board row.\n"
    "- EXECUTION_BOUNDARY: re-registration of a spell_id with another binding hash, the revalidation marks, Creations'\n"
    "  entry for the spell_id, a binding-change verb; tests and docs.\n"
    "- DEPENDENCIES: S1, S2; melder_1's release; the notch's revalidation marks (0.2.8250).\n"
    "- EXIT_GATE: every binding change revalidates the spell and its dependents; the store never hands the new binding\n"
    "  an object built for the old one; the verb works on an active spell whose index holds parked versions.\n"
    "- FAILURE_ESCALATION: DECISION_REQUEST on the verb's shape and on what happens to the old objects; CONFLICT while\n"
    "  a needed file is held.",
    "- Re-registering a spell_id with a different binding hash retires its verdicts (as `register_index` does), resets\n"
    "  its compiled plan and gates its lineage, and marks what depends on it downstream, as a notch marks them.\n"
    "- The store's entry under the spell_id follows the binding: an unchanged existence and disposal list keep it; a\n"
    "  changed one retires the old entry - its objects stay alive and are torn down with their own disposal list - before\n"
    "  the new binding builds.\n"
    "- A verb changes a spell's binding in place and keeps its spell_id (cleanup_spell refuses an active member whose\n"
    "  index holds parked versions today).\n"
    "- The managed settings: a settings-only change keeps part A's pool rebind, unless the owner rules otherwise.",
    "- No new lock-order edge; warm meld paths unchanged; the marks run with the Book lock free, as the notch's do.",
    "re-registration, revalidation, the store's entry, the binding verb.",
    "the hashes (S1, S2), the refusals (S4), the migration (S5), pool routing (set aside by the owner).",
    f"- {EPIC_ID}\n- STORY-2026-10-18-binding_manifest_hash\n- STORY-2026-10-18-one_registration_per_object",
    "- [ ] Task: the component patch (Spellbook, Creations, SpellSystemStates, Conduit's verb).\n"
    "- [ ] Task: red tests per binding field; implement; docs; notch; the rebuild last.",
    "- Changing a spell's existence from many to unique (or back) through the verb builds the new existence at the next\n"
    "  meld and never returns the old entry; its dependents rebuild.\n"
    "- Changing its spellframe makes the consumers that matched the old category re-resolve.\n"
    "- Changing only its managed settings rebinds the pool and rebuilds nothing.",
    "- `test_changing_a_spells_existence_revalidates_it_and_its_dependents`,\n"
    "  `test_a_binding_change_never_serves_the_old_entry`; GIL off and on.",
    "- A new binding verb on Conduit (name and shape in the patch).",
    "- Objects of the old binding: kept alive with their own teardown (Melder does not police userland objects).",
    "- The verb's name and shape; which fields revalidate; the old entry's objects; a disposed spell's pool beside a new\n"
    "  root's pool after a re-registration elsewhere (unproven; from S6).",
    "- Scope: a binding change revalidates the spell and its dependents; the store and a verb follow it.\n"
    "- State: draft (melder_0); after S1 and S2.\n"
    "- Next: the component patch once S1 and S2 land.",
)

S4 = story(
    "one_registration_per_object",
    "an object already registered is refused, whatever the bind signature",
    "draft", "p1",
    "As an agent, I want Melder to refuse registering an object it already holds - under any name, existence or as a\n"
    "staged version - so that one object is one spell and nothing is built twice for it.",
    "The owner: \"you could register the same object n number of times for each existence this is a correctness bug big\n"
    "time\". With S1 the same object has one spell_id, so the existing collision check refuses it; this story makes the\n"
    "refusal complete across every registration path and makes its message say what happened.",
    "- ENTRY_GATE: S1 landed; this story's component patch approved; melder_1's release of spellbook.py; the board row.\n"
    "- EXECUTION_BOUNDARY: the registration paths (bind, bind_inactive, add_to_spell_index, scan_bind, restore and graft\n"
    "  through them) and the refusal message; tests and docs.\n"
    "- DEPENDENCIES: S1; melder_1's release; the owner's scope call (per process or per frame).\n"
    "- EXIT_GATE: a second registration of one object is refused on every path with nothing registered; one active\n"
    "  object per address still holds; moving a registration between indexes still works.\n"
    "- FAILURE_ESCALATION: DECISION_REQUEST on the scope; CONFLICT while spellbook.py is held.",
    "- bind, bind_inactive and add_to_spell_index (and scan_bind, restore and graft through them) refuse a spell_id\n"
    "  already registered in scope - per process by default, per frame under per-frame ids - with nothing registered.\n"
    "- The message names the existing registration (its frame, Book, address, index, active or parked) and the remedy:\n"
    "  change its binding with S3's verb, or move it with add_to_spell_index / remove_from_spell_index.\n"
    "- One active object per address stays (the frame's signature claim).",
    "- The refusal adds no lock and no meld-path work.",
    "the registration paths and the refusal message.",
    "the hashes (S1, S2), revalidation (S3), the migration (S5).",
    f"- {EPIC_ID}\n- STORY-2026-10-18-spell_id_hashes_the_object_code\n- STORY-2026-10-18-revalidate_on_binding_change",
    "- [ ] Task: the component patch (Spellbook's registration paths, the message).\n"
    "- [ ] Task: red tests per path; implement; docs; notch; the rebuild last.",
    "- Binding a class under a second name, binding it with another existence and staging it as a version are each\n"
    "  refused with the new message, and nothing is registered.\n"
    "- A class bound in a second frame is refused under process-wide ids and accepted under per-frame ids.",
    "- `test_registering_the_same_class_twice_is_refused_whatever_the_binding`; per path; GIL off and on.",
    "- **Breaking change** (with S5): one class can no longer be registered twice to get two objects; use subclasses.",
    "- Tests and users that bind one object twice: counted and moved in S5.",
    "- The scope (per process or per frame) - the epic's call 5.",
    "- Scope: one object, one registration, on every path, with a clear refusal.\n"
    "- State: draft (melder_0); after S1.\n"
    "- Next: the component patch once S1 lands.",
)

S5 = story(
    "spell_id_migration",
    "every spell_id moves once, and nothing breaks silently",
    "draft", "p2",
    "As a user upgrading Melder, I want the one-time move of every spell_id handled - caches, records, research history,\n"
    "tests and docs - so that nothing silently breaks and every change is documented.",
    "Every spell_id changes once with S1. The creation cache, the Crystallizer record, MutationResearch's history and the\n"
    "suite all hold spell_ids; each needs a defined path, and the change is one Breaking release-note entry.",
    "- ENTRY_GATE: S1-S4's patches approved; this story's component patch; melder_1's release of restore_engine.py and\n"
    "  graft_runner.py; the board row.\n"
    "- EXECUTION_BOUNDARY: the cache generation, the record version and restore/graft mapping, research history, the\n"
    "  tests that bind one object twice, the system documents, the graph, README and the release note.\n"
    "- DEPENDENCIES: S1-S4; melder_1's release; the owner's call on records holding one object twice.\n"
    "- EXIT_GATE: an old cache is cold once; an old record restores with mapped ids or reports what it cannot rebuild;\n"
    "  the suite is green with the GIL off and on; docs, notch and the rebuild with both checks OK.\n"
    "- FAILURE_ESCALATION: DECISION_REQUEST on the record policy; CONFLICT while a needed file is held.",
    "- A cache generation retires every bundle written under the old ids.\n"
    "- The record's version moves; restore and graft map recorded ids to the new ones; a record that registered one\n"
    "  object twice rebuilds the first and reports the rest as a shortfall, or refuses (the owner's call).\n"
    "- MutationResearch history recorded under old spell_ids is mapped or marked, as the patch decides.\n"
    "- Tests that bind one object twice move to two objects; every managed and fingerprint test moves to the new rule.\n"
    "- Docs: the system documents, the graph, README and the release note (Breaking: every spell_id moves; one object,\n"
    "  one spell; a binding change revalidates).",
    "- The migration adds no runtime cost after the first cold conjure.",
    "caches, records, research history, tests and docs.",
    "the hashes (S1, S2), revalidation (S3), the refusals (S4).",
    f"- {EPIC_ID}\n- STORY-2026-10-18-spell_id_hashes_the_object_code\n- STORY-2026-10-18-one_registration_per_object",
    "- [ ] Task: the component patch (CachingSystem, RecordVersion, RestoreEngine, GraftRunner, MutationResearch).\n"
    "- [ ] Task: count the tests that bind one object twice (a prototype run).\n"
    "- [ ] Task: implement; docs; release note; notch; the rebuild last.",
    "- A world recorded before the change restores (mapped ids) or reports exactly what it could not rebuild.\n"
    "- A cache written before the change is cold once and rewritten.",
    "- `test_a_record_from_before_the_identity_change_restores_with_mapped_ids`; the whole tree with the GIL off and on.",
    "- **Breaking change**: every spell_id moves once.",
    "- Research lanes keyed by old ids lose their residency join: the patch decides mapping or marking.",
    "- The record policy for one object registered twice (rebuild the first and report, or refuse).",
    "- Scope: the one-time move of every spell_id.\n"
    "- State: draft (melder_0); after S1-S4's patches.\n"
    "- Next: the component patch with the others'.",
)


def write(path: pathlib.Path, text: str) -> None:
    """Write a new file; refuse to overwrite one."""
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path}")
    path.write_text(text, encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    write(EPIC_PATH, EPIC)
    for slug, text in (("spell_id_hashes_the_object_code", S1), ("binding_manifest_hash", S2),
                       ("revalidate_on_binding_change", S3), ("one_registration_per_object", S4),
                       ("spell_id_migration", S5)):
        write(pathlib.Path(f"tickets/stories/2026-10-18_{slug}_story.md"), text)
