# Epic: spell_identity_is_the_code - a spell_id names the registered object's code; its binding is a manifest

## Metadata
- Epic ID: EPIC-2026-10-18-spell_identity_is_the_code
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-18T23:43:33Z
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
  melder_0 writes the files these stories touch and announces each landing by mailbox (M0-193); melder_1
  held spellbook.py, spell.py and spell_index.py for
  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions until it landed as 0.2.8256 and
  handed them back (M1-37, M1-38); each lane claims a file from the other by message before editing it.
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
  melder_0 writes the files these stories touch and says so by mailbox before each landing (M0-193). S8 is
  on hold (M1-33); S9 of EPIC-2026-10-17-correctness_defects landed as 0.2.8256 and melder_1 handed
  spellbook.py, spell.py and spell_index.py back (M1-37, M1-38); conduit.py, spellbook_validation_error.py
  and change_control_manager.py are free. The next notches are above 0.2.8256: S1's, then S2's, each with
  its release-note entry. melder_1 holds mutation_research.py for S4 of
  EPIC-2026-10-17-correctness_defects and takes spellbook.py and spell.py once S1 and S2
  land, notching above them (M1-39, M1-40).
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
- [x] Milestone 1: the owner's calls on the edges; the architecture patch and the first component patches approved.
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
  patch and S1's and S2's patches approved by the owner's word to land, 2026-10-18; S3-S5 before their code).
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
- One object bound twice through a minted index, until melder_1's S4 lands: bind's collision
  guard misses a version alone in an index `remove_from_spell_index` minted (M4b, M5b); S4's
  edit A closes it, and this epic's S4 takes M4b and M5b as acceptance cases.

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
- 2026-10-18T15:45:30Z: Milestone 1 met - S1's patches updated, S2's written (FACT note).
- 2026-10-18T16:18:35Z: M1-37 consumed - S9 takes the refusal and lands first (FACT note); the owner's word - the
  binding hash goes into the SpellCrystal in this landing, the third-party reading is accepted, keep
  moving (DECISION note).
- 2026-10-18T17:23:22Z: M1-38 consumed - S9 landed as 0.2.8256 with the refusal; spellbook.py and spell.py are back
  (FACT note).

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

- DATETIME: 2026-10-18T15:38:29Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-36 from melder_1 (2026-10-18T15:27:07Z, ACK), consumed; it answers M0-196 and M0-197. The owner
    reopened S9's rule - refusal on all three doors, or the hole rule (S9's TRADEOFF note) - and melder_1 sends
    his pick as M1-37. Under the refusal S9 is a check in `cleanup_and_remove_spell` (spellbook.py) and a
    Raises entry on `Spell.cleanup` (spell.py): it lands first, both files come back by message right after,
    and S1 and S2 notch above it. Under the hole rule both files come here at once and S9 follows S1, then also
    needing conduit.py and details.py, maybe meld.py, each claimed by message first. melder_1 edits neither
    file before M1-37; spell_index.py stays with melder_1 (M0-197).
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:424-459
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:461-480
  IMPACT: S1 and S2's edits in spell.py and spellbook.py wait for M1-37 either way; the patch updates, S2's
    component patch and the blast-radius run do not need them. Under the hole rule S9 would edit details.py
    and maybe meld.py, which S1's statement sweep also touches (their "fingerprint" docstrings): those files
    are taken in turn.
  NEXT: Apply S1's patch updates and S2's component patch; the blast-radius run; read the mailbox for M1-37.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T15:45:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Milestone 1 is met: the architecture patch and S1's patches are approved by the owner's word to land
    and updated for his decisions (decision B, strict uniqueness, S6 parked); S2's patches are written - the
    binding manifest (Binding Pipeline, S2 section) and the creation cache's keys (generation 23) - with S2's
    inventory, decisions and mapping in its story. Nothing in src/ yet. The binding hash joins the record in
    S5, not this landing (S2's DECISION note).
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:1-218
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md:281-307
  - context_compass/tickets/stories/2026-10-18_binding_manifest_hash_story.md:148-184
  - context_compass/tickets/stories/2026-10-18_binding_manifest_hash_story.md:186-204
  IMPACT: S1 and S2 move to the blast-radius run; their spell.py and spellbook.py edits wait for M1-37.
  NEXT: The blast-radius run in a /tmp mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T16:18:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-37 from melder_1 (2026-10-18T15:41:09Z, NOTICE), consumed; it answers M0-196 (M1-36). The owner chose
    the refusal for S9 of EPIC-2026-10-17-correctness_defects: all three cleanup doors refuse the active
    member of an index that holds parked versions, the messages naming the remedies; Book teardown is
    unaffected. S9 lands first: its edits are `cleanup_and_remove_spell`'s check and docstring,
    `_dispose_spell`'s refusal text and `cleanup_spell`'s docstring in spellbook.py, and `Spell.cleanup`'s
    Raises entry in spell.py, nothing else. melder_1 hands both files back by message right after its
    landing, rebuild included, and S1 notches above it; spell_index.py and conduit.py are melder_0's again
    now. Since then the owner gave his word on those edits (E1-E7) and named the notch 0.2.8256 (melder_1's
    DECISION note of 2026-10-18T16:02:48Z).
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:517-542
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:584-598
  IMPACT: S1 and S2 edit spell.py and spellbook.py only after melder_1's hand-back; until then they are built
    and tested in a /tmp working mirror. The next notches are above 0.2.8256.
  NEXT: The owner's crystallizer call (DECISION note below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T16:18:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-18, mid-turn): "ok cool make sure you land the binding hash going into
    crystallizer too please, those 3 things for library version are fine, and lets keep moving on this, to
    finish it off, M1 is working on refusal yeah". So: (1) the binding hash goes into the SpellCrystal record in
    this landing, with S2, not in S5: S2's DECISION note of 2026-10-18T15:45:30Z, point (1), is superseded,
    S2's Requirements, Acceptance Criteria and EXIT_GATE say so again, and a record patch (the field, its
    RecordVersion, what restore and graft do with a recorded hash) is written and linked before any
    crystallizer code. (2) The third-party reading stated for him in the architecture patch - an object of an
    installed package hashed as its type, its distribution version and its address-free repr, an installed
    class, metaclass or function named with its distribution version - is accepted as written. (3) S9 takes
    the refusal and lands first (M1-37). (4) Keep moving to finish: S1 and S2 are built and run in a /tmp
    working mirror while S9 lands, and copied into the repository once spellbook.py and spell.py are back.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-18_binding_manifest_hash_story.md:194-212
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:196-202
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:113-118
  IMPACT: S2 gains the crystal's record (spell_crystal.py, the record version, and the replays in restore_engine.py
    and graft_runner.py where they read it); the architecture patch's matrix and S2's mapping gain the
    record row; the third-party reading is final, not for him to narrow.
  NEXT: Record the blast-radius run; read the crystal, the record version and both replays whole; write the
    record patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T16:24:12Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Migration step 2 is done: the blast radius of S1 and S2 is 101 new failures with the GIL off and on and
    none a Melder defect (S1's MEASURE note); S1 alone replays the creation cache across bindings and S2's
    keys repair it (S2's MEASURE note); a class's spell_id must not depend on whether its annotations were
    read, so the digest skips `__annotate_func__` while it is None (S1's FACT note); and until S3 lands a
    rebind under another slotted existence meets the object the removed definition left in its slot (S3's
    FACT note) - a RISK carried to the release note unless S3 lands in the same release.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md:309-336
  - context_compass/tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md:338-361
  - context_compass/tickets/stories/2026-10-18_binding_manifest_hash_story.md:262-282
  - context_compass/tickets/stories/2026-10-18_revalidate_on_binding_change_story.md:135-158
  IMPACT: Nothing found blocks S1 and S2; the landing rewrites the 101 tests from triage.md.
  NEXT: The crystallizer record patch for S2; M0-198 to melder_1; S1 and S2 built in a /tmp working mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:23:22Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-38 from melder_1 (2026-10-18T17:07:19Z, NOTICE), consumed. S9 of EPIC-2026-10-17-correctness_defects
    landed at 0.2.8256 and is turned in, rebuilt last with both checks OK; spellbook.py and spell.py are
    melder_0's again, as spell_index.py and conduit.py already were (M1-37). S9's src edits were its E1-E7 in
    those two files and the notch: `cleanup_and_remove_spell`'s refusal and docstring, `_dispose_spell`'s
    refusal text and `cleanup_spell`'s docstring, and `Spell.cleanup`'s Raises entry - none of S1's or S2's
    edit sites; the mirror's spell.py and spellbook.py are byte-identical to the repository's (diff -rq), so
    edits_spell.py's check run holds for the repository. Outside src the landing re-reads what S9 changed: the
    four system documents and their indexes, the spellbook.json and spell.json graph descriptors (accepted)
    and the graph, and the running release note (header 0.2.8256, a new section, the packaging lines). The
    next notches are above 0.2.8256.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:1-9
  - src/melder/__version__.py:12-12
  - src/melder/aether/spellbook/spellbook.py:602-781
  - release_docs/next_version_release.md:1-3
  IMPACT: S1 and S2's spell.py and spellbook.py edits go into the repository at the landing; the mirror moves to
    0.2.8256 (its __version__, build assets and release note) before the apply.
  NEXT: Sync the mirror to 0.2.8256; then edits_profiles.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T18:08:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-39 from melder_1 (2026-10-18T18:04:38Z, NOTICE, ACK requested), consumed after the re-onboarding;
    ACKed as M0-199. S4 of EPIC-2026-10-17-correctness_defects has the owner's word (chat 2026-10-18):
    `remove_from_spell_index` registers the index it mints as a post-conjure `bind` registers its new
    index, the root's teardown unregisters it with the rest, and `residency_view` reads its version parked;
    no new index state. melder_1 claims mutation_research.py, which S1 and S2 do not edit, and asks for
    spellbook.py once S1 and S2 land, notching above them. A gap for strict uniqueness, read in
    `Aether._check_for_spell` and proven by melder_1's probe on 0.2.8256: the guard asks the frame's
    `has_spell` and then returns `find_index_for_spell`, None for a version alone in a minted index, so a
    second bind of that version's spell_id - by another Book of the frame (M4b), or of another frame under
    process-wide ids (M5b) - is accepted, and an unconjured Book's later conjure is refused. Under S1 the
    spell_id is the object's code, so until S4's edit A lands one object can be registered twice this way.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md:304-327
  - context_compass/artifacts/minted_index_registry_20261018/runs/probe_minted_index_fix_cases_0_2_8256_gil0.txt:1-31
  - src/melder/aether/aether.py:2550-2622
  IMPACT: S1 and S2 keep their edit list; spellbook.py is handed to melder_1 at their landing. The gap is a
    Risk of this epic and an acceptance case of its S4 (one_registration_per_object) once melder_1's S4
    has landed; the release note names it if S1 and S2 land first.
  NEXT: The S1+S2 component test in the /tmp mirror (GIL off and on), red against the repository.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T18:40:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-40 from melder_1 (2026-10-18T18:16:51Z, NOTICE, ACK requested), consumed after the re-onboarding;
    ACKed as M0-200. S4's edit D is a docstring in spell.py (`Spell._spell_index_unless_cleaned` names the
    root's teardown among its readers), so melder_1 asks spell.py back with spellbook.py when S1 and S2
    land, edits neither before that message, and re-checks S4's anchors in both against the landed tree;
    mutation_research.py stays with melder_1 until S4 lands. S1 and S2's 19 spell.py edits do not touch
    that docstring.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/scripts/edits_spell.py:1-118
  - src/melder/aether/spellbook/spell.py:911-948
  IMPACT: The landing NOTICE hands back spellbook.py and spell.py together; nothing else in S1 and S2's edit
    list changes.
  NEXT: The test tranche in the mirror: category (b), the tests of the retired `Bind.sha256_profile`.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T21:53:02Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-15 from melder_2 (2026-10-18T21:32:20Z, NOTICE, ACK requested), consumed after the re-onboarding;
    ACKed as M0-201. melder_2 runs EPIC-2026-10-18-managed_spell_examples_and_docs (owner request): new
    example files only (lessons 42-47 in UX_and_AIX_experiences/02_intermediate and
    pytest_examples/test_managed_spell_probes.py), a new docs/ page and a release-note entry under
    Packaging and documentation; no src and no notch; its asset and LLM rebuild waits for this landing's.
    It asks three things of this landing: (1) to be told before it edits UX_and_AIX_experiences/ or
    docs/, because some UX examples bind one class twice, which S1 and S2 refuse - which ones is UNKNOWN
    until swept, and the whole-tree runs (unit, component, integration, experimentation) never ran the
    examples; (2) a correction: src_architecture's failure mode and src_components' managed-pool failure
    modes say a release after the pool's root was torn down raises RuntimeError, while its probe (P08,
    P19) shows `ReleaseManagedSpell().release` raising the not-managed ValueError through the registry and
    only a `ManagedSpellLease` getting the RuntimeError - UNKNOWN until the release paths are read;
    (3) a NOTICE when this landing's rebuild is done. melder_0 holds the running release note until then.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_lifecycle_map_story.md:1-352
  - context_compass/system_docs/src_architecture.md:2525-2535
  - context_compass/system_docs/src_components.md:3951-3952
  IMPACT: (1) widens the landing: an example that binds one class twice fails the way the 88 tests did, so
    the examples are swept and run in the mirror before the rebuild, melder_2 told before any edit;
    (2) is a documentation correction in two documents this pass holds, made only if the code confirms
    it; (3) orders the two rebuilds and keeps one writer on the release note.
  NEXT: Sweep UX_and_AIX_experiences/ and docs/ for one object bound twice; read the release paths for (2).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:18:15Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-16 and M2-17 from melder_2 (2026-10-18T22:03:37Z and 22:10:43Z, NOTICEs), consumed after the
    re-onboarding; M0-202 answers. M2-16: at 5e3800c7a (S1 and S2 committed on 0.2.8256) `pytest_examples`
    fails 17 rows with the GIL off and on, the same without melder_2's files - 12 one-object refusals, 4
    rows on premises in the identity area and expert 37's missing VERIFY header. This landing's mirror
    agrees with clean caches: 17 failed with S1 and S2, 7 at 0.2.8256 (the 4 premise rows, the VERIFY
    header and two contract probes that rebind one class), so 10 rows are new. melder_2's lane added,
    each binding an object once, 02_intermediate/42-48_managed_spell_*.py,
    pytest_examples/test_managed_spell_probes.py and a MANAGED SPELL POOLS section in
    02_intermediate/_concept_map.txt. M2-17: its S3 edits six docs/ files - catalog.toml, curriculum.toml,
    a new intermediate/managed-spells.md, one bullet of intermediate/index.md, one cross-link line of
    intermediate/scopes.md and seo.toml. A read-only grep of docs/ (no .venv, no _build) for the old
    identity rule finds candidates in other files only: reference/glossary.md, reference/troubleshooting.md
    (and the advanced/worlds.md it links), advanced/inspection-walkthrough.md and
    intermediate/configuration.md; intermediate/scopes.md names `spell_id=` once, for purge.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_ux_examples_story.md:171-196
  - context_compass/artifacts/spell_identity_20261018/runs/ux_examples/ux_s1s2_gil0_clean.txt:1-27
  - context_compass/artifacts/spell_identity_20261018/runs/ux_examples/ux_base8256_gil0_clean.txt:1-17
  - docs/reference/glossary.md:14-14
  - docs/reference/troubleshooting.md:12-12
  - docs/advanced/inspection-walkthrough.md:16-16
  - docs/intermediate/configuration.md:82-82
  - docs/intermediate/scopes.md:104-104
  IMPACT: S3's six files and this sweep's candidates are disjoint, so melder_2's S3 proceeds; the examples sweep
    owns the 10 new rows and decides the 7 older ones by reading them; melder_2's new files need nothing.
  NEXT: Finish reading the failing rows' sources (37_the_frame_conduit_cloud.py, test_intermediate_probes.py
    near 492 and 864), then record the sweep on S1 and write the rewrite script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:28:21Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-15's point (2) holds, read whole: `Creations.cleanup` unregisters its managed pools from
    `ReleaseManagedSpell` (`_unregister_managed_quantities`) before it cleans them, and `unregister` drops
    a class whose last pool goes (`_drop_pool`). So after a root's teardown `ReleaseManagedSpell().release`
    finds no pool for the object's class and `_resolve_pool` raises ValueError "<Class> is not a managed
    spell class in any live root: bind it with existence=Existence.managed_spell_quantity, or its root was
    torn down." - unless another live root pools the class, whose pool then takes the object (one pool and
    no filter is that pool's `put_back`, which trusts the object). The torn-down RuntimeError ("The pool of
    managed spell '<name>' was torn down with its root conduit; the object is yours to dispose.") is
    `put_back` on a cleaned pool: a `ManagedSpellLease` released after the teardown (it holds its pool), or
    a registry release that read the pool before the store unregistered it. src_architecture's failure mode
    and src_components' Managed Spell Pools failure modes give the RuntimeError for any release after
    teardown; this docs pass corrects both. No code changes: routing by class through live roots is the
    0.2.8244 design.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:326-399
  - src/melder/aether/conduit/creations/creations.py:1261-1282
  - src/melder/aether/conduit/creations/release_managed_spell.py:319-355
  - src/melder/aether/conduit/creations/release_managed_spell.py:357-399
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - src/melder/aether/conduit/creations/release_managed_spell.py:666-686
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:553-611
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:916-928
  - src/melder/aether/conduit/creations/managed_spell_lease.py:103-127
  - context_compass/system_docs/src_architecture.md:2525-2535
  - context_compass/system_docs/src_components.md:3951-3952
  - context_compass/tickets/stories/completed/2026-10-18_managed_spell_lifecycle_map_story.md:1-352
  IMPACT: Two documentation corrections in the source follow-ups of this pass; melder_2 hears it with the
    rebuild NOTICE.
  NEXT: The examples' rewrite (S1's PLAN note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T22:55:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-18 consumed (melder_2, 2026-10-18T22:38:41Z): S3's six docs/ files are on the tree - the managed
    spells chapter, lessons 42-48 in the catalog, the chapter in the curriculum, a bullet in the intermediate
    index, a cross-link in scopes.md and the page in seo.toml - with the docs checks green on melder_2's
    mirror; this landing's rebuild carries them, and melder_2's release-note entry and rebuild wait for its
    rebuild-done NOTICE. M0-203 answers: the docs sweep edits five pages, none of the six (glossary,
    troubleshooting, the inspection walkthrough, configuration and the README's Frame Boundaries section),
    and the examples' rewrite changed lesson text the site renders.
  EVIDENCE: context_compass/tickets/stories/2026-10-18_managed_spell_sphinx_docs_story.md:172-199
  IMPACT: The rebuild order holds: this landing's rebuild first, then melder_2's entry and rebuild; the docs
    checks run over both lanes' docs before this landing's rebuild.
  NEXT: The docs sweep applied, then the docs checks.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:06:32Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-19 consumed (melder_2, 2026-10-18T23:04:33Z): on the owner's directive in melder_2's chat (23:01Z: finish
    now, no rebuild in that lane) melder_2 added its one release-note bullet - the managed spells chapter,
    docs/intermediate/managed-spells.md - directly above the closing rebuild line of `## Packaging and
    documentation`, runs no rebuild and closes S3 and its epic; its writes to docs/ and release_docs/ end there.
    So this landing's release-note pass re-reads the file and keeps that bullet above the rebuild line, and this
    landing's rebuild is the one that carries melder_2's docs and release-note changes.
  EVIDENCE:
  - release_docs/next_version_release.md:1063-1070
  - context_compass/tickets/stories/2026-10-18_managed_spell_sphinx_docs_story.md
  IMPACT: No ordering wait remains on melder_2's side; the docs checks before the rebuild still cover both lanes'
    docs, and the rebuild line names this landing's version.
  NEXT: The tests system documents and the source follow-ups.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T23:31:15Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1 and S2 turned in: S1 notched 0.2.8257, S2 0.2.8258; both moved to completed/, their board rows and
    details out, two closed anchors in; the patch folder archived; staged/ moved into _to_delete/. S3 (a
    changed binding revalidates), S4 (the refusal names the existing registration) and S5 (records holding
    one object twice) stay draft, each after its own patch; S6 stays parked.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-10-18_spell_id_hashes_the_object_code_story.md
  - context_compass/tickets/stories/completed/2026-10-18_binding_manifest_hash_story.md
  IMPACT: The epic's first milestone - identity is the code, the binding a manifest - is landed but for the rebuild.
  NEXT: The rebuild for 0.2.8258, then the NOTICEs to melder_1 (M1-40) and melder_2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T23:43:33Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Rebuilt last for 0.2.8258, in a /tmp mirror and copied back byte for byte (writes in place; the mount
    refuses the builders' atomic replace, and a first in-repo asset run stopped there after writing three
    manifests identical to the mirror's): assets - agent documentation 470 entries, bind guard 630, system
    documents 4, all v0.2.8258; LLM bundles with --include-untracked - src 585 files, tests 1139, other 409
    (the mirror first missed the tracked `src/melder/__melder_cache__/__melder_cache__.py`; rebuilt with it).
    Repo-side --check: assets OK x3, bundles OK x3; no .git/index.lock. In the mirror after the rebuild:
    build_assets, llm_support, github_workflows and the identity tests - 731 passed, 1 skipped.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/runs/rebuild/assets_check_repo.txt:1-7
  - context_compass/artifacts/spell_identity_20261018/runs/rebuild/llm_check_repo.txt:1-7
  - context_compass/artifacts/spell_identity_20261018/runs/rebuild/llm_build_mirror_2.txt:1-4
  IMPACT: S1 and S2's landing is complete; melder_1 and melder_2 are told.
  NEXT: Report to the owner; then S3-S5, each after its own patch.
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
- State: in_progress (melder_0), implementation. The owner's word (DECISION note of 2026-10-18T15:01:53Z): land S1
  with S2's cache keys now, duplicates strictly refused (S6 parked in the backlog), binding and caching
  patterns later (EPIC-2026-10-18-identity_and_caching_configurables); and (DECISION note of
  2026-10-18T16:18:35Z) the binding hash goes into the SpellCrystal in this landing and the third-party reading
  is accepted as written. His earlier calls and decisions stand (DECISION notes of 2026-10-18T12:15:14Z,
  13:06:51Z, 14:14:10Z). S1 and S2 in_progress; S3-S5 draft, each after its own patch; nothing in src/ yet.
  S9 of EPIC-2026-10-17-correctness_defects took the refusal and landed first as 0.2.8256 (M1-37, M1-38);
  spellbook.py, spell.py, spell_index.py and conduit.py are melder_0's, and S1 and S2 notch above 0.2.8256.
- Done since: M1-37 consumed and the owner's crystallizer call recorded (FACT and DECISION notes of
  2026-10-18T16:18:35Z).
- Done since: the blast radius recorded (MEASURE note of 2026-10-18T16:24:12Z).
- Done since: the crystallizer record patch written and the `__annotate_func__` rule added to the
  code-description patch (S2's PLAN note of 2026-10-18T16:32:46Z).
- Done since: S1's SpellCodeDigest and S2's BindingManifest written and probed in the mirror (the
  stories' notes of 2026-10-18T17:05:55Z).
- Done since: M1-38 consumed - S9 landed as 0.2.8256; spellbook.py and spell.py are back (FACT note of
  2026-10-18T17:23:22Z).
- Done since: S1 and S2 applied to the /tmp working mirror and smoke-checked, the GIL off and on (the
  stories' FACT notes of 2026-10-18T17:51:07Z).
- Done since: M1-39 consumed and ACKed (M0-199) - melder_1's S4, its file claims and the
  minted-index guard gap (FACT note of 2026-10-18T18:08:26Z).
- Done since: M1-40 consumed and ACKed (M0-200) - spell.py goes back with spellbook.py at
  the landing (FACT note of 2026-10-18T18:40:11Z).
- Done since: the whole tree run with S1 and S2 in the mirror - 406 new failures in five categories,
  the 213 doubles fixed (S1's MEASURE note of 2026-10-18T18:44:20Z).
- Done since: the test tranche finished in the mirror and the whole tree green but melder_1's 18 S8
  tests, the GIL off and on; bind's cost measured, +37 to +55 us a bind (S1's MEASURE and RISK notes
  of 2026-10-18T19:59:24Z).
- Done since: S1 and S2 applied to the repository and committed by the owner (5e3800c7a); the
  source system documents carry them (S1's FACT note of 2026-10-18T21:51:31Z).
- Done since: M2-15 consumed and ACKed (M0-201) - melder_2's examples lane, the UX examples
  that bind one class twice, a release-after-teardown correction to verify, the rebuild order
  (FACT note of 2026-10-18T21:53:02Z).
- Done since: M2-16 and M2-17 consumed (M0-202 answers) - melder_2's count of the examples (17
  rows, as this landing's mirror counts), its new files, and S3's six docs/ files, none of them
  this sweep's (FACT note of 2026-10-18T22:18:15Z).
- Done since: the examples rewritten and run (S1's MEASURE note of 2026-10-18T22:52:11Z).
- Done since: M2-18 consumed and M0-203 sent (FACT note of 2026-10-18T22:55:41Z).
- Done since: the docs sweep (S1's FACT notes of 2026-10-18T22:57:08Z).
- Done since: M2-19 consumed - melder_2's release-note bullet is on the tree, above the rebuild line,
  and its lane runs no rebuild (FACT note of 2026-10-18T23:06:32Z).
- Done since: the tests system documents and the source follow-ups (S1's MEASURE note of 2026-10-18T23:18:31Z).
- Done since: the graph, the notches (0.2.8257, 0.2.8258) and the release note (S1's FACT note of 2026-10-18T23:26:28Z).
- Done since: S1 and S2 turned in (FACT note of 2026-10-18T23:31:15Z).
- Done since: rebuilt for 0.2.8258 (FACT note of 2026-10-18T23:43:33Z); M0-204 hands spellbook.py
  and spell.py back to melder_1 and M0-205 tells melder_2 the rebuild carried its lane.
- Next: S3 (a changed binding revalidates), S4 (the refusal names the existing
  registration) and S5 (records holding one object twice), each after its own patch, on
  the owner's word.

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
