# Story: spell_id_hashes_the_object_code - the spell_id is the SHA256 of the registered object's code

## Metadata
- Story ID: STORY-2026-10-18-spell_id_hashes_the_object_code
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-18T15:01:53Z

## User Narrative
As an agent iterating on a class in Melder, I want its spell_id to change exactly when its code changes - a method
body, a parameter, a default, the constructor - and never for a docstring, a comment, a blank line or how it was
bound, so that every real edit is a new version I can stage and notch, and the same code is always the same spell.

## Value / MRP Alignment
Identity is structure. Today's hash misses method bodies (the epic's F1, F2, F5: an edited class is refused as a
collision) and folds in the bind call (the n-registrations bug). Hashing the object's code, and only that, fixes
both at the root.

## Ticket Contract
- ENTRY_GATE: the owner's calls on the epic's open edges (all five made 2026-10-18; renames count); the epic's
  architecture patch and this story's component patch approved; the board row.
- EXECUTION_BOUNDARY: `Bind.sha256_profile` and `Bind.spell_id_inspector` (their inputs), the binding profile
  strategy (a code digest per class or function, computed once per object), the hash domain (a new version tag);
  its tests and docs. Not the binding manifest or the caches (S2), revalidation (S3), the refusals (S4) or the
  migration (S5).
- DEPENDENCIES: the epic; the prototype probes; S2 lands with it.
- EXIT_GATE: the prototype's cases P1-P10 and I1-I9 are regression tests passing with the GIL off and on and
  across hash seeds; bind's cost measured against today's; the docs and the graph.
- FAILURE_ESCALATION: DECISION_REQUEST for an edge the owner has not called; RISK if bind's cost regresses
  materially; CONFLICT if a needed file is held.

## Requirements (Functional)
- The spell_id is the SHA256 of `v5-code`, the interpreter's cache tag and the target's encoding; the contract
  is the code-description patch, corrected here 2026-10-18T13:30:00Z:
  system_docs/patches/active/spell_identity_is_the_code_2026_10_18/code_description_patch_spell_code_digest.md.
- A class: its module, qualname, metaclass and bases, and the namespace of the class and of every class it
  inherits from outside the standard library (owner, 2026-10-18: a change in a base class is a change) - each
  function by its code (the instruction stream with each loaded constant by value, argument counts, flags, name
  tables, exception table), its defaults, its annotations' code, its closure values and type parameters, nested
  code the same way, and every value assigned in its body (class-level values; owner: "a change anywhere is a
  change").
- Line numbers, docstrings, comments and unused constants never enter it: constants are read by value in the order
  the instructions first load them, because in 3.14 a docstring takes or shifts slot 0 of the constant table.
- A function or lambda: its module, qualname and code as above. A decorated function is the wrapper itself, whose
  closure holds the function it wraps, so the decorator's code and the wrapped body both count (D2-D4).
- An existing object: its class's code plus its data - its slots and `__dict__`, each by value, recursively and
  cycle-safe (owner, 2026-10-18); an object with no Python-visible state keeps today's rule (type and
  address-free repr).
- Local variable names are hashed, so a rename is a new version (owner, 2026-10-18, call 4: "yeah we count it
  of course").
- Nothing from the bind call enters it: spellframe, binding name, existence, disposal names, resolvable and the
  managed settings move to the binding manifest (S2).

## Requirements (Non-Functional)
- No source-file read at bind; code-object digests are memoized per Bind (code objects are immutable), class
  and object encodings are computed at each bind (classes and objects are mutable).
- Address-free and deterministic: byte-identical across processes, hash seeds and GIL modes.
- Bind's cost measured before and after on the gauntlet's bind-heavy worlds.

## Scope Boundaries
- In scope: Bind's fingerprint inputs, the binding profile's code digest, `spell_id_inspector`, tests and docs.
- Out of scope: the binding manifest and the caches (S2), revalidation (S3), the refusals (S4), the migration (S5).

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the owner made calls 1-3 and 5 (chat 2026-10-18; the epic's DECISION note), so the
  design docs start; call 4 (local names) is pending, counted by default.

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-binding_manifest_hash (lands with this story)
- STORY-2026-10-18-explicit_duplicate_binding (S6; parked in the backlog by the owner, 2026-10-18)
- STORY-2026-10-18-spell_id_migration

## Tasks (Implementation Checklist)
- [x] Task: the owner's calls (the epic's Open Questions; all five made 2026-10-18).
- [x] Task: the patches (architecture; Binding Pipeline and Spell Examination Profiles component;
  code-description) - written 2026-10-18; approved by the owner's word to land (2026-10-18T15:01:53Z),
  updated for decision B and strict uniqueness.
- [ ] Task: red regression tests from P1-P10 and I1-I9.
- [ ] Task: implement and measure bind's cost.
- [ ] Task: docs, graph, notch (with S2) and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- A changed method body, a parameter added to a method, a changed default, a renamed method and two lambdas with
  different bodies each give a different spell_id; a comment, a reworded or added docstring and blank lines give
  the same one.
- Binding the same class under two binding names gives one spell_id (S4 refuses the second registration).
- The ids are identical across processes and GIL modes.

## Validation / Test Plan
- Symptom-named tests such as `test_editing_a_method_body_changes_the_spell_id`,
  `test_a_docstring_or_comment_does_not_change_the_spell_id` and
  `test_two_lambdas_with_different_bodies_are_two_spells`; a subprocess test for stability across hash seeds; the
  epic's probes re-run on src/; the whole tree with the GIL off and on.

## UX / API / Data Notes
- **Breaking change** (with S5): every spell_id moves once; the same object always has the same spell_id.

## Risks / Mitigations
- Ids differ per Python version and under -O (compiled instructions): document it; the cache is already per
  interpreter.
- A closure's captured values count (derived from calls 2-3; stated for the owner in the architecture patch):
  two classes a factory makes with different captured values are two spells.
- Bind's cost: code digests memoized; a class over a large third-party base costs milliseconds (D9); measured on
  the gauntlet at landing.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None of the owner's calls is open (call 4 made 2026-10-18: renames count; the epic's DECISION note of
  2026-10-18T13:06:51Z).
- Stated in the architecture patch for the owner: two existing objects of one class with equal data are one
  spell (D10), so the second bind is refused as the same spell.
- Decided (the owner, the epic's DECISION note of 2026-10-18T14:14:10Z): installed third-party code and objects are
  named by qualified name and distribution version (B); the patches move to B. A configurable for it is parked
  in EPIC-2026-10-18-identity_and_caching_configurables.
- The explicit duplicate bind (S6) is parked by the owner (the epic's DECISION note of 2026-10-18T15:01:53Z):
  one object is strictly one spell for now, and the corrected refusal names no duplicate option.

## Decision Log
- 2026-10-18T11:45:58Z: filed under EPIC-2026-10-18-spell_identity_is_the_code (the epic's DECISION note).
- 2026-10-18T12:15:14Z: the owner made calls 1-3 and 5 (the epic's DECISION note); in_progress for the design docs.
- 2026-10-18T13:06:51Z: the owner's call 4 - a renamed local variable counts (the epic's DECISION note).
- 2026-10-18T13:30:00Z: the design docs written for the owner's approval; Requirements corrected to them (MEASURE and
  PLAN notes).
- 2026-10-18T14:14:10Z: the owner's decisions - installed third-party code by version (B); the explicit
  duplicate bind lands with this story as S6 (the epic's DECISION note).
- 2026-10-18T15:01:53Z: the owner's word to land this story now, with S2's cache keys; duplicates strictly refused, S6
  parked (the epic's DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/spell_identity_20261018/probes/code_digest_v2.py (the code digest v2 prototype)
  - artifacts/spell_identity_20261018/probes/probe_code_digest_cases.py (E01-E34)
  - artifacts/spell_identity_20261018/probes/probe_code_digest_corpus.py (src/melder corpus, cost)
  - artifacts/spell_identity_20261018/runs/ (four runs of each: hash seeds 1 and 2, GIL 0 and 1)
  - artifacts/spell_identity_20261018/probes/probe_code_digest_design_edges.py (D1-D10, two runs)
  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md
  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_binding_pipeline.md
  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_spell_examination_profiles.md
  - system_docs/patches/active/spell_identity_is_the_code_2026_10_18/code_description_patch_spell_code_digest.md
- DISPOSITION: retain_as_reference (the probes); promote_to_documentation (the patch docs, at landing)
- CLEANUP_TRIGGER: at closure the probes stay as the design's evidence; each case becomes a regression test

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a spell's identity (its code) versus its binding (how it is kept)
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-10-18T11:45:58Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-18T11:45:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Filed from the owner's direction (the epic's DECISION note of 2026-10-18T11:45:58Z); the evidence it
    starts from is the epic's FACT note and its probes. Nothing in src/ moves before this story's component patch is
    approved.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:220-270
  IMPACT: The scope, requirements and acceptance above are the plan the patch docs refine.
  NEXT: the component patch after the owner's calls.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T12:45:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The code digest v2 prototype (outside src/) holds the owner's calls 1-3 on 3.14.7t. Rules: a function is
    its deoptimized instruction stream (co_code, EXTENDED_ARG folded) with each LOAD_CONST replaced by its order of
    first use and the used constants hashed by value, plus its argument counts, flags without CO_HAS_DOCSTRING, name
    tables and exception table, its defaults, the code of its __annotate__, its closure values (a __classdict__ cell
    is a marker), its type parameters and its __dict__ minus __wrapped__; a class is its module, qualname,
    metaclass, direct bases and, per MRO entry, the namespace digest of code outside the standard library (standard
    library and builtins by qualified name), a namespace being every __dict__ entry except interpreter bookkeeping
    (_abc_impl opaque); values go by value (scalars, containers, enum members with their values), classes by name
    unless nested (then digested), functions by code, typing objects by text, standard-library and Melder objects by
    type, user objects by type and data (slots, then __dict__, cached_property values skipped), cycles marked. All
    42 cases (E01-E34) behave as designed. The id moves for a base-class method body, a class-level value, a tuple's
    order, a nested class, a decorator argument, property, static and class method bodies, a dataclass default, an
    enum value, a field or parameter annotation, a user metaclass body, an except clause, a local rename (counted),
    a type parameter bound, another module, a factory's captured value, object data, nested object data, a mangled
    slot, a bound method's self data, partial arguments, a lambda default and two standard-library loggers (today's
    id moves for four of these). It stays for docstrings, comments and blank lines (a try/except method too), the
    same source executed twice, equal object data, a held lock or logger, self-reference, a cached_property read,
    20000 calls (specialization), annotations read, a runtime-checkable isinstance, ABC.register, sys.monitoring
    LINE and INSTRUCTION events and sys.settrace; a class-level dict mutated at runtime moves it (an object is
    hashed as it is at bind). Byte-identical across hash seeds 1 and 2 and GIL 0 and 1. Corpus: all 782 classes and
    functions of src/melder digest without error into 782 distinct digests, identical across the four runs; per
    target, cold (fresh memo) median 0.29 ms, p95 1.5 ms, max 7.5-10.7 ms over the four runs; warm (code digests
    memoized) median 0.11 ms, p95 0.45 ms; today's fingerprint median 0.064 ms, p95 0.16 ms. The first prototype's
    dis walk cost 1172 ms over Melder's 5952 code objects, the co_code walk 46 ms. Found on the way: in 3.14
    co_consts[0] holds the docstring or else the first constant, which the optimizer may leave unused, so constants
    must be read by value, never by index.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/probes/code_digest_v2.py:1-349
  - context_compass/artifacts/spell_identity_20261018/probes/probe_code_digest_cases.py:1-234
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_cases_gil0_seed1.txt:1-42
  - context_compass/artifacts/spell_identity_20261018/probes/probe_code_digest_corpus.py:1-90
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_corpus_gil0_seed1.txt:1-6
  - context_compass/artifacts/spell_identity_20261018/runs/corpus_digests_gil0_seed1.tsv:1-782
  IMPACT: S1's design docs can state the digest as a contract with a measured cost: about 0.1 to 0.3 ms more per
    bind, paid at bind and never at meld. Only code objects may be memoized; classes and functions are mutable.
  NEXT: Write the architecture patch, the Binding Pipeline component patch and the code-description patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T13:30:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The design-edge probe (D1-D10; 3.14.7t, hash seed 1, GIL 0 and 1, the same verdicts): a dataclass
    default_factory change moves the id (D1, through the generated __init__'s closure); a decorator's wrapper body
    and the decorated body each move it, the same decorated source twice does not (D2-D4); two packaging Version
    objects differ (D5); two C objects without Python-visible state (yaml's Mark) collide under the prototype and
    under today's repr rule alike (D6: their repr is the address-stripped default), so the design keeps today's repr
    rule for such a target; a class-level reference to another class and a module-level helper a method calls are
    named, not hashed (D7, D8); a class over pygments' PythonLexer costs 2.6-3.2 ms cold and 1.9 ms warm against
    0.03 ms for a plain class (D9: class namespaces are encoded at every bind); equal-data objects are one spell (D10).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/probes/probe_code_digest_design_edges.py:1-111
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_design_edges_gil0_seed1.txt:1-13
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_design_edges_gil1_seed1.txt:1-17
  IMPACT: The code-description patch states rule 2e (today's repr rule for an object without Python-visible
    state), the decorator rule (the wrapper with its closure, not `inspect.unwrap`) and the third-party decision
    with its measured cost; the Requirements are corrected in place.
  NEXT: The owner's approval of the patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T13:30:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch section -> implementation -> validation, for after the owner's approval. (1) Code-description
    patch, steps 1-8 and the value table -> spell_code_digest.py (class SpellCodeDigest, its tables as class
    attributes) -> test_spell_code_digest.py, one test per rule (its Validation Focus Points), red first.
    (2) Binding Pipeline patch, Target boundary and State deltas -> bind.py (the `_spell_code_digest` slot,
    `__init__`, `cleanup`, `_bind_logic`'s id, `spell_id_inspector(spell)`, the three removals) -> test_bind.py,
    test_bind_managed_spell_options.py and the other files that name the fingerprint (14) moved to the new rule.
    (3) Spell Examination Profiles patch -> binding_profile.py and binding_profile_strategy.py ->
    test_binding_profile_strategy.py. (4) Architecture patch, the S1 rows of its statements table -> spell.py,
    lookup_container.py, aether.py, aether_configuration.py, the three meld docstrings, and spellbook.py's
    inspect_spell and remedy texts once melder_1 releases spellbook.py -> a docstring audit. (5) Interface
    deltas -> the F1 loop, the refusal and inspect_spell stage 3 as integration tests. (6) Architecture step 2 ->
    the blast-radius run before any of this. (7) S2's patches land in the same pass, with their own mapping.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:1-187
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_binding_pipeline.md:1-107
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_spell_examination_profiles.md:1-61
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/code_description_patch_spell_code_digest.md:1-164
  IMPACT: The consumption mapping the patch gate requires is in place before any code.
  NEXT: The owner's approval; then the blast-radius run.
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
- Scope: the spell_id hashes the registered object's code only.
- State: in_progress (melder_0), implementation: the owner's word to land it now with S2 (the epic's DECISION
  note of 2026-10-18T15:01:53Z); the patches are updated for B and strict uniqueness before the code. spellbook.py
  and spell.py are melder_1's for S9 and asked for (M0-196).
- Done: Bind's fingerprint and the binding profile read whole; the prototype extended to bases, class-level
  values, object data and closures, and measured (MEASURE note).
- Done since: the four patch docs in system_docs/patches/active/spell_identity_is_the_code_2026_10_18/, the D
  probe (MEASURE note) and the mapping (PLAN note).
- Next: the patches updated for B and strict uniqueness; the blast-radius run in a /tmp mirror; the landing
  pass with S2.

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
