# Epic: spell_identity_is_the_code - a spell_id names the registered object's code; its binding is a manifest

## Metadata
- Epic ID: EPIC-2026-10-18-spell_identity_is_the_code
- Status: ready
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-18T11:45:58Z
- Target Window: 2026-Q4
- Related Program/Initiative: Melder runtime correctness (the owner's direction, chat 2026-10-18); follows
  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md)

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
- tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md
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
- 2026-10-18T11:45:58Z: opened on the owner's direction (DECISION note); five stories filed.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probes); created 2026-10-18T11:45:58Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-18T11:45:58Z
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
  - tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md
  IMPACT: The spell_id formula, the binding record, the caches' keys, the registration rules and every recorded id
    change; one object becomes one spell.
  NEXT: The owner's calls on the open edges (Open Questions), then the architecture patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T11:45:58Z
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

- DATETIME: 2026-10-18T11:45:58Z
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
- Scope: a spell_id becomes the SHA256 of the registered object's code (methods and constructor, bodies included; no
  docstrings, comments or line numbers); the bind signature becomes a binding manifest with its own SHA256 that
  revalidates the spell when it changes; one object is one spell; every spell_id moves once.
- State: ready (melder_0), discovery. Five stories filed (S1-S2 ready, S3-S5 draft); nothing in src/ yet. Evidence:
  the probes in Artifact Links. S6 of the correctness epic is turned in; its part B and open items live here.
- Next: (1) the owner's five calls (Open Questions); (2) the architecture patch and the S1/S2 component patches;
  (3) S1 and S2.

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
