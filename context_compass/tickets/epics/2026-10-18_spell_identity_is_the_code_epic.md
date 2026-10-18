# Epic: spell_identity_is_the_code - a spell_id names the registered object's code; its binding is a manifest

## Metadata
- Epic ID: EPIC-2026-10-18-spell_identity_is_the_code
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-18T15:01:53Z
- Target Window: 2026-Q4
- Related Program/Initiative: Melder runtime correctness (the owner's direction, chat 2026-10-18); follows
  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool
  (tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md)

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
  any src/ edit; the owner's calls on the open edges (Open Questions) before
  STORY-2026-10-18-spell_id_hashes_the_object_code is implemented.
- EXECUTION_BOUNDARY: how a spell is identified and bound - bind's fingerprint and the binding profile, the binding
  manifest and its hash, the creation cache's keys, re-registration and revalidation, the staging refusals, and the
  migration (cache generation, record, research history, tests, docs). Excluded: the managed pool's release routing
  (set aside by the owner), melder_1's lanes and the other stories of EPIC-2026-10-17-correctness_defects.
- DEPENDENCIES: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (part A, 0.2.8254, done); the
  owner's calls; one writer per file - melder_1 turned in its lane and released every file it held (M1-28), so
  melder_0 writes the files these stories touch and announces each landing by mailbox (M0-193); since M1-33
  melder_1 holds spellbook.py and spell.py for STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions
  until it lands (released, M0-195; S8 is on hold), and melder_0 claims a file back by message before editing it.
- EXIT_GATE: every story accepted; one notch per landed source change with its release-note entry; the system
  documents and the graph; the rebuild last with both checks OK; board and artifact sync; the owner's disposition.
- FAILURE_ESCALATION: DECISION_REQUEST for each edge the owner has not called; CONFLICT when a needed file is held by
  another lane; BLOCKER if a cache, record or restore path cannot keep its contract under the new identity.

## Goals (Outcomes)
- A spell_id is the SHA256 of the registered object's code - its methods and constructor: signatures, defaults,
  annotations and the instructions inside their bodies, nested code included - and nothing from the bind call.
- Docstrings, comments and formatting never change a spell_id; any real code change does.
- One object is one spell: registering it again, under any name or existence or as a staged version, is refused
  (strictly for now, the owner, 2026-10-18; an explicit duplicate bind, S6, is parked).
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
- from_state: ready
- to_state: in_progress
- transition_reason: the owner made calls 1-3 and 5 (chat 2026-10-18; DECISION note), so S1's design docs
  start; call 4 and the "conduit manifest" reading wait for his word.

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
- One writer per file: melder_1 turned in its lane at 2026-10-18T11:51:41Z and released every file it held (M1-28);
  melder_0 writes the files these stories touch and says so by mailbox before each landing (M0-193). Since M1-33
  S8 is on hold and melder_1 holds spellbook.py and spell.py for S9 of EPIC-2026-10-17-correctness_defects until
  it lands (M1-34, M0-195); conduit.py, spellbook_validation_error.py and change_control_manager.py are free. The
  next notch is above 0.2.8255, or above S9's if it lands first.
- Compiled instructions are specific to the Python version (and to -O); the creation cache is already admitted per
  release and interpreter.
- Device runs: `. ~/.melder_env`, TMPDIR under /tmp, the rebuild through a /tmp mirror.
- Three correctness stories wait for this epic on the owner's order (M1-32; melder_1's DECISION note in
  EPIC-2026-10-17-correctness_defects): STORY-2026-10-17-staged_version_releases_active_signature,
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only and
  STORY-2026-10-17-restore_drops_separated_parked_version.

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
- [ ] Story: STORY-2026-10-18-explicit_duplicate_binding - a bind that says so registers one object more than once,
  its scope recorded (S6; parked in the backlog by the owner, 2026-10-18).

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: the owner's calls on the open edges (Open Questions; all five made 2026-10-18).
- [x] Task: the parked configurables epic filed (EPIC-2026-10-18-identity_and_caching_configurables, backlog).
- [ ] Task: the architecture patch for the epic; a component patch per story before its code (the architecture
  patch and S1's patches written 2026-10-18; the owner's approval pending).
- [ ] Task: complete each story above.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- S1-S5 accepted (S6 parked by the owner); the prototype's cases are regression tests in the suite; no object
  registers twice; a binding change revalidates; docs, notches and the rebuild; the owner's
  disposition.

## Risks / Mitigations
- Every spell_id moves once (records, caches, research history): one migration story, a cache generation, restore
  mapping and a Breaking release-note entry.
- Bind cost of hashing instructions: measured in S1; the digest is computed once per class object.
- A cache or store keyed by spell_id alone that misses a binding change: S2's patch inventories every spell_id-keyed
  cache and store before code.
- Overlap with another lane's files: one writer per file; a mailbox NOTICE before each landing (M0-193).

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Each story: symptom-named regression tests, GIL off and on, the whole tree in a /tmp mirror before landing.
- The prototype probes re-run against src/ at each landing.

## Rollout / Adoption Plan
- Stories land S1 -> S2 -> S3 -> S4 -> S5 (S1 and S2 land together, so the caches never see a spell_id without
  its binding hash; S6 is parked, so a second registration of one object is strictly refused); one notch
  per landed source change; the identity change is one Breaking entry in the running release note.

## Open Questions
- The owner's calls before S1's implementation, made 2026-10-18 (DECISION note): (1) inherited code - yes, a change
  in a base class moves its subclasses' spell_ids; (2) class-level values - code ("a change anywhere is a change");
  (3) an existing object - its class's code plus its data; (5) the scope of a registration - not part of this
  change, the existing spell-id regime stands; (4) a renamed local variable - counted ("yeah we count it of
  course", DECISION note of 2026-10-18T13:06:51Z). All five are made.
- The owner's "conduit manifest" (chat 2026-10-18), read as: each spell's binding hash is recorded in what the
  conduit builds and caches the spell from (its plan, its creation cache), and a changed hash revalidates and
  rebuilds that spell; confirmed (DECISION note of 2026-10-18T14:14:10Z).
- Third-party code and objects (S1): B, named by qualified name and distribution version (the owner, DECISION
  note of 2026-10-18T14:14:10Z); a configurable for it belongs to the parked configurables epic.
- A record made before the change that holds one object twice (S5): restore the first and file a shortfall per
  dropped duplicate (the owner, DECISION note of 2026-10-18T14:14:10Z).
- The explicit duplicate bind (S6, STORY-2026-10-18-explicit_duplicate_binding): parked by the owner (DECISION
  note of 2026-10-18T15:01:53Z); one object is strictly one spell for now; the four forms stay in the
  STRATEGY_DISCUSSION note of 2026-10-18T14:33:32Z.
- Configurables (how deeply Melder reads objects, installed packages, caching, the duplicates policy, presets
  and advice): parked in EPIC-2026-10-18-identity_and_caching_configurables (backlog), on the owner's word.
- For S3: which binding fields revalidate and which only rebind (the managed settings rebind the pool without
  rebuilding plans since 0.2.8254).
- Left from S6, unproven: a spell disposed with managed objects out and registered again in another root leaves the
  old pool registered beside the new one; the pool following the spell is the proposed rule (pool routing is set aside
  by the owner).

## Decision Log
- 2026-10-18T11:45:58Z: opened on the owner's direction (DECISION note); five stories filed.
- 2026-10-18T12:01:17Z: M1-28 consumed - melder_1's files are free; the entry gates no longer wait on a release
  (FACT note).
- 2026-10-18T12:15:14Z: the owner made calls 1-3 and 5; in_progress for S1's design docs (DECISION note).
- 2026-10-18T13:06:51Z: the owner's call 4 - a renamed local variable counts (DECISION note).
- 2026-10-18T13:06:51Z: M1-30 and M1-31 consumed - the owner's order is parallel; melder_1 holds four files for
  S8 until it lands (FACT note).
- 2026-10-18T13:42:22Z: S1's design docs written; three decisions with the owner (DECISION_REQUEST note).
- 2026-10-18T14:14:10Z: the owner's decisions - the conduit-manifest reading confirmed, third-party code named
  by version (B), old duplicates restore the first; explore an explicit duplicate bind; file a configurables epic
  (DECISION note).
- 2026-10-18T14:33:32Z: the explicit duplicate bind explored - four forms with the owner, (1) recommended; S6 filed;
  the configurables epic filed in the backlog (STRATEGY_DISCUSSION note).
- 2026-10-18T15:01:53Z: the owner's word - land S1 with S2's cache keys now, duplicates strictly refused, S6 parked;
  binding and caching patterns later (DECISION note).

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
  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/ (the epic's and S1's patch docs)
- DISPOSITION: retain_as_reference (the probes and scripts); promote_to_documentation (the patch docs, at landing)
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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probes); created
  2026-10-18T11:45:58Z.
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
  - context_compass/tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md:977-996
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
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:116-126
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:160-173
  IMPACT: Nothing in src/ moves before the owner's calls and the approved patches.
  NEXT: Put the five calls to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T12:01:17Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-28 from melder_1 (2026-10-18T11:51:41Z), consumed: melder_1 landed and rebuilt 0.2.8255 (docstrings and
    comments call a SpellIndex a SpellIndex; nothing renamed), turned in
    TASK-2026-10-16-recheck_contract_consumers_when_provider_changes on the owner's word, and handed back every file
    its lane held - spellbook.py, conduit.py, the lookup fix's files, the wording sweep's src files, S6's files,
    `__version__`, the release note, the system documents and the graph (not committed). No story here waits on a
    release any more: the PLAN note's step (4) loses its melder_1 condition, and the Ticket Contract, Constraints,
    Risks and the stories' entry gates are corrected in place. One writer per file still holds; melder_0 announces
    each landing by mailbox (M0-193). The next notch is above 0.2.8255.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:15-21
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  IMPACT: S2-S5 can start once their patches are approved; S1 and S2 notch 0.2.8256 at the earliest.
  NEXT: The owner's calls on the five edges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T12:15:14Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's calls on the open edges (chat 2026-10-18). (1) "yes": a change in a base class's code moves its
    subclasses' spell_ids, so a class's code digest includes the code of the classes it inherits from. (2) "class
    level values are code yeah, so a change anywhere is a change": values assigned in a class body enter the digest.
    (3) "yes": an existing object bound as a spell is identified by its class's code plus its data. (5) "this isn't
    related to our change your focus is bind and bindhashing for the conduit manifest": the scope of a registration
    stays the existing spell-id regime and no story decides it; the focus is bind and its hashing (S1) and the
    binding manifest the conduit builds from (S2, with S3's revalidation). (4) Open: he asked what a local variable
    is - the example and the recommendation (count a rename, as answer 2 implies) are sent, with the reading of
    "conduit manifest" for him to confirm. melder_1 ACKed M0-193 (M1-29): it holds no file and claims from melder_0
    by message before it edits one.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:160-173
  IMPACT: S1 can be designed: a class's bases, its class-level values and an existing object's data are inputs of
    the code hash. S4 loses its scope question.
  NEXT: Read Bind's fingerprint and the binding profile whole, extend the prototype to bases, class-level values and
    object data, then write S1's design docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T13:06:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's call 4 (chat 2026-10-18): "yeah we count it of course" - a renamed local variable is a code
    change and moves the spell_id. A function's local names (co_varnames), cell names and free names enter its code
    digest beside its instructions, as the code digest v2 prototype already does: case E27 (`total` renamed
    `amount`) moves the id, today's id does not. All five of the owner's calls on the epic's edges are made; what
    stays with him is the "conduit manifest" reading (S2).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/probes/code_digest_v2.py:167-205
  - context_compass/artifacts/spell_identity_20261018/probes/probe_code_digest_cases.py:110-112
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_cases_gil0_seed1.txt:18-18
  IMPACT: S1's code-description patch states local names as part of a function's digest, with no alternative;
    S1's Requirements, Open Questions and entry gate are corrected in place.
  NEXT: Write S1's architecture, component and code-description patches for the owner's approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T13:06:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-30 and M1-31 from melder_1, consumed. M1-30 (12:30:17Z): the owner's order (chat 2026-10-18) is
    parallel - melder_0 keeps this epic; melder_1 takes the correctness stories the owner fully confirmed, one at a
    time, each re-verified on the current tree, starting with
    STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (S8). M1-31 (12:48:25Z): the owner approved S8's
    patch (failed_notch_refusal_2026_10_18), and melder_1 claims for S8 until it lands spellbook.py (`_notch_spell`,
    `_apply_notch`, a new `_revert_refused_notch`, one docstring), conduit.py (`notch_spell`'s docstring),
    spellbook_validation_error.py (an optional `preface`) and change_control_manager.py (one docstring). Released
    (M0-194): this epic edits no src/ file before the owner approves its patches; then S1 needs spellbook.py only
    for `inspect_spell`'s stage-3 docstring and comment, and S3 and S4 need it and conduit.py later. melder_0
    claims a file back by message before editing it and waits for S8's landing if S8 is still open; whoever lands
    second notches above the first.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:1-12
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-62
  - src/melder/aether/spellbook/spellbook.py:2517-2643
  IMPACT: One writer per file holds: the four files are melder_1's until S8 lands. The Ticket Contract's
    DEPENDENCIES and the Constraints are corrected in place.
  NEXT: Write S1's patch docs; claim spellbook.py back once the owner approves them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T13:42:22Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: S1's design docs are written for the owner's approval (the architecture patch, the Binding Pipeline and
    Spell Examination Profiles component patches and the code-description patch, in
    system_docs/patches/active/spell_identity_is_the_code_2026_10_18/), with three decisions for him: (1) the
    "conduit manifest" reading (S2; asked 2026-10-18); (2) third-party code and objects - A (recommended):
    digested like the application's, so a package upgrade moves the ids and a third-party object with per-process
    state makes its holder's id differ per process; B: named by qualified name and distribution version, bounded
    but blind to settings kept inside library objects; (3) a record made before the change that holds one object
    twice: restore the first and file a shortfall per dropped duplicate (recommended), or refuse the restore whole.
    Stated for him rather than asked: one object binds once per process by default (call 5), so a second Book that
    binds the same class is refused and shares it instead; a closure's captured values count; equal-data objects
    are one spell; code a spell only names is not hashed.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:51-75
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:159-180
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_design_edges_gil0_seed1.txt:1-13
  IMPACT: No src/ edit before his approval; S2's patches follow his answer on (1); (2) decides whether S1 digests
    installed packages; (3) decides how S5 restores old records.
  NEXT: Report the docs to the owner plainly, with the Greeter example; on approval, the blast-radius run in a
    /tmp mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T14:14:10Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's three decisions (chat 2026-10-18), answering the DECISION_REQUEST note: (1) "Yes you are
    correct" - the "conduit manifest" reading stands: each spell's binding hash is kept with what the conduit builds
    and caches that spell from, and a changed hash revalidates and rebuilds that spell (S2, S3). (2) "B I think
    this is reasonable but this should maybe become a configurable on a spellbook that we can remember add this as
    an epic to explore how caching configuration and bind configuration could do stuff we can think about it after
    ( think this could become a caching configurable)" - installed third-party code and objects are named by
    qualified name and distribution version (S1); a configurable comes later, in a parked epic. (3) "yes this is
    intended as the original goal was to always have 1 class anyways just restore the first, sure" - a record
    holding one object twice restores the first and files a shortfall per dropped duplicate (S5). New direction,
    same message: "we do want the option for users to bind multiple objects twice like 3 different versions of the
    configuration so a user can just call it ... by adding a configurable bind action such that we can capture that
    scope and still allow duplication but it has to be explicit" - to explore now; and "add an epic with
    configurable ideas for the user in terms of caching and complexity of how deeply we understand objects and
    whats advised".
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:395-419
  IMPACT: S1's patches move to decision B; the conduit-manifest reading is S2's design; S5 restores the first
    registration. The explicit duplicate path must land with S1: from S1's landing the existing collision refusals
    refuse a second registration of one object, which today succeeds under another binding name.
  NEXT: Explore the explicit duplicate bind on the code (Bind, the bind verbs and their options, SpellBinder,
    scan_bind, the record and restore's replay); file the configurables epic in the backlog.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T14:33:32Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Registering one object more than once on purpose (the owner, DECISION note of
    2026-10-18T14:14:10Z), for his choice.
    Objective: keep several bindings of the same code - for example `Worker` as a shared `unique` named
    `shared` and as a `many` named `fresh` - each called by name, while an accidental second registration
    stays refused.
    Constraints: identity stays the object's code (S1); the duplication is written in the bind and recorded;
    nothing changes at meld; it lands with S1.
    Known, read on 0.2.8255: the spell_id hashes the binding name today (`Bind._bind_logic` passes it to
    `sha256_profile`), so a class binds once per binding name. bind and bind_inactive refuse an id the Book
    or the process already holds. An active spell also claims its address frame-wide: the spellframe or the
    class name, with the binding name or "__default__". A meld names a spell by spell_id or by that
    address. The record keeps the binding name and restore replays it through `bind`. A parameter typed
    with a class that several spells provide is refused at conjure (AMBIGUOUS_PROVIDER) unless a SpellMap
    default picks one. So from S1 on, the second registration of a class under another name - accepted
    today - meets the collision refusal. Different data needs nothing new: two existing objects of one
    class with different data are two spells under S1 (call 3); the option is for bindings of one class,
    or of equal-data objects.
    Unknowns: none that block; the form, the name and the binding-name default are the owner's.
    Options: (1) an option on the bind verbs, `duplicate_scope="fresh"`: the scope joins the spell_id (the
    SHA256 of the code and the scope; no scope keeps the plain code id); the Spell keeps the scope and the
    plain code id, so the copies of one object list together; the record keeps the scope and restore and
    graft replay it; an unscoped second registration is refused with a message naming the first and the
    option. (2) `duplicate=True`: the address enters the spell_id of an explicit duplicate. (3) a block,
    `with spellbook.duplicate_scope("tenant_a"):`, giving every bind inside it the scope - (1) for a batch,
    held per thread. (4) a Book setting that allows duplicates.
    Tradeoffs: (1) keeps identity and binding apart - the scope is identity, the binding name stays a
    binding field S3 can change; (2) is one flag but puts a binding field back into identity, so renaming a
    duplicate's binding (S3) would make it another spell; (3) suits tenants and can follow (1); (4) is
    explicit per Book, not per bind, against "it has to be explicit". Under every form each active copy
    needs its own address (the frame claim), a class annotation sees every copy (AMBIGUOUS_PROVIDER unless
    a SpellMap default picks one, as two binding names do today) and an unfiltered managed release of two
    managed copies asks for `spell_id=` (as today).
    Recommendation: (1), with the binding name defaulting to the scope when none is given, so
    `bind(spell=Worker, existence="many", duplicate_scope="fresh")` is melded as `meld(spell=Worker,
    binding_name="fresh")`; (3) and a strict switch wait in the parked configurables epic.
    Decision ask: the form, and the name (`duplicate_scope`, from his words, or another). Filed as S6,
    STORY-2026-10-18-explicit_duplicate_binding; the configurables epic is filed in the backlog as
    EPIC-2026-10-18-identity_and_caching_configurables.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:795-804
  - src/melder/aether/spellbook/spellbook.py:5405-5419
  - src/melder/aether/spellbook/spellbook.py:5754-5776
  - src/melder/aether/aether.py:2550-2624
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1064-1083
  - src/melder/utilities/helpers/general_helpers.py:365-401
  - src/melder/aether/conduit/meld/meld.py:2067-2149
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2142-2199
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:628-704
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py:71-118
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:51-94
  IMPACT: Without S6 at S1's landing, S1 removes today's way to bind one class twice and puts nothing in
    its place. Once the form is chosen, the architecture patch's formula (invariant 1) and its one-object
    rule (invariant 5) gain the explicit exception, and S4's refusal names the option.
  NEXT: The owner's choice of the form and the name; then S1's patches updated for decision B and S6.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T15:01:53Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-18), answering the STRATEGY_DISCUSSION note: "I'm not sure right now for
    now just land the first thing we agreed on and then we'll talk about the rest later with duplication if a
    user changes how an object is initialized maybe we're fine with things being strictly unique lets try it
    for now but allow different kinds of binding patterns and caching patterns later so users can change how
    it behaves". So S1 lands now - the spell_id is the object's code - in the one landing the architecture
    patch plans for it (Migration step 5): S1 with S2, whose binding hash keys the creation cache beside the
    spell_id, so a cache built for one binding is never replayed for another under one spell_id (invariant
    7); each with its notch. Duplicates are strictly refused for now: S6 is parked in the backlog unbuilt, and
    the corrected refusal names no duplicate option. Binding and caching patterns users can choose come later
    (EPIC-2026-10-18-identity_and_caching_configurables). His word to land is the approval of S1's patches,
    which are updated for decision B (installed packages named by version) and strict uniqueness; S2's
    component patch is written before its code. S3, S4 and S5 follow, each after its own patch (Migration
    step 6).
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:77-111
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:464-524
  IMPACT: S1 and S2 move to implementation; S6 leaves the landing; spell.py and spellbook.py are claimed from
    melder_1 by message (M0-196) before either is edited.
  NEXT: Update S1's patches for B and strict uniqueness; write S2's component patch; the blast-radius run in a /tmp
    mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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
- State: in_progress (melder_0), implementation. The owner's word (DECISION note of 2026-10-18T15:01:53Z): land S1
  with S2's cache keys now, duplicates strictly refused (S6 parked in the backlog), binding and caching
  patterns later (EPIC-2026-10-18-identity_and_caching_configurables). His earlier calls and decisions
  stand (DECISION notes of 2026-10-18T12:15:14Z, 13:06:51Z, 14:14:10Z). S1 and S2 in_progress; S3-S5
  draft, each after its own patch; nothing in src/ yet. melder_1 holds spellbook.py and spell.py for S9 of
  EPIC-2026-10-17-correctness_defects (M1-33); both are asked for by M0-196. The next notch is above
  0.2.8255, or above S9's.
- Next: (1) S1's patches updated for B and strict uniqueness, S2's component patch; (2) the blast-radius run
  in a /tmp mirror; (3) the landing pass - red tests, src, green, the moved tests, the whole tree with the
  GIL off and on, docs, notches, the rebuild last.

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
