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
- Updated: 2026-10-18T20:03:20Z

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
- [x] Task: red regression tests from P1-P10 and I1-I9 (staged/tests; green on the mirror, GIL off and on).
- [ ] Task: implement and measure bind's cost (measured, MEASURE note of 2026-10-18T19:59:24Z; lands with S2).
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
- Bind's cost: code digests memoized; a class over a large third-party base costs milliseconds when digested
  (D9), and decision B names installed bases instead (a version lookup); measured on the gauntlet at landing.

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
- 2026-10-18T15:45:30Z: the patches updated for decision B and strict uniqueness (FACT note).

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

- DATETIME: 2026-10-18T15:45:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1's patches are updated for the owner's word and decisions (the epic's DECISION notes of
    2026-10-18T14:14:10Z and 15:01:53Z), nothing in src/: the architecture patch is approved and records his
    decisions as DECIDED (the third-party-object reading - type, version and address-free repr - stated for
    him to narrow), invariant 4 counts repr() of an installed third-party object, invariant 7 names the key and
    the stamp, the new invariant 8 states decision B, the matrix gains the binding manifest and the creation
    cache (bind-guard 628 -> 630), and the statements table gains the creation system's and the caching
    system's stamp text and five "fingerprint" statements (meld.py, contract/details.py, inspector_utility.py).
    The Binding Pipeline patch carries the corrected refusal texts with no duplicate option, the S2 section
    and the file order (M1-36). The code-description patch states B: a third-party class, metaclass or
    function named `<qualified> <dist>==<version>`, a third-party object `ext:` with its repr, site-packages
    detection and the version lookup. The Spell Examination Profiles patch is approved with its
    recommendation (the fields go).
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:1-218
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_binding_pipeline.md:1-155
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/code_description_patch_spell_code_digest.md:1-181
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/component_patch_spell_examination_profiles.md:1-63
  IMPACT: S1's patches match what lands; the PLAN note's mapping stands, with SpellCodeDigest gaining the
    site-packages check and the version lookup (measured on the device: importlib.metadata.version about
    0.2 ms, packages_distributions 14.7 ms once).
  NEXT: The blast-radius run in a /tmp mirror with S2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T16:24:12Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The blast radius (the architecture patch's Migration step 2), measured in a /tmp mirror of 0.2.8255
    with nothing in the repository edited: the prototype code digest with decision B as the spell_id (in
    `Bind._bind_logic` and `spell_id_inspector`) and S2's binding hash in the creation cache's structural
    key and world stamp. The whole tree ran with the GIL off and on: 14542 tests each, 126 failed, 25 of them
    in the unpatched baseline (melder_1's S8 and S9 red tests), so 101 new failures - the same set in both
    modes - and none is a Melder defect: 88 register one object twice and meet strict uniqueness at bind
    ("Spell ID collision detected"); 1 binds one class in two frames' Books under process-wide ids and
    meets conjure's integrity check; 5 pin S2's cache format and stamp; 2 use `Bind.sha256_profile` as their
    oracle; 3 assert that a binding change moves the spell_id; 1 asserts the opposite of the owner's call 1
    (a base-class change); 1 expects the frame claim's message before the collision. triage.md lists each
    test and its rewrite. The landing's own whole-tree run gives the final count (the FACT note below).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/blast_radius/triage.md:1-148
  - context_compass/artifacts/spell_identity_20261018/blast_radius/tally_output.txt:1-18
  - context_compass/artifacts/spell_identity_20261018/blast_radius/mirror/_br_digest.py:1-158
  - context_compass/artifacts/spell_identity_20261018/blast_radius/mirror/mirror_bind.diff:1-38
  - context_compass/artifacts/spell_identity_20261018/blast_radius/mirror/mirror_structural_snapshot.diff:1-31
  IMPACT: The landing rewrites 101 tests by category - distinct classes or subclasses where a test wants two
    registrations, a refusal test where one object twice is the point, the new oracle, the reversed premises
    - and no src finding blocks S1.
  NEXT: The crystallizer record patch (S2); then S1 built in a /tmp working mirror from the code-description
    patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T16:24:12Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Python 3.14 adds keys to a class's `__dict__` when its annotations are read: a class with no annotations
    gains `__annotate_func__` = None and `__annotations_cache__` (A1); a class with annotations holds
    `__annotate_func__` from creation and gains `__annotations_cache__` (A2). The prototype excluded only
    `__annotations_cache__`, so one class's spell_id differed before and after anything read its annotations
    (A3: False), and Melder reads them itself (the binding profile's `_read_class_annotations`). Skipping
    `__annotate_func__` while it is None keeps the id stable (A3: True), with the GIL off and on. The
    code-description patch's excluded keys and validation list gain that rule before SpellCodeDigest is
    written; a class with annotations keeps its annotate function in the encoding (its annotations' code).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/blast_radius/probes/probe_annotate_func_in_class_dict.py:1-76
  - context_compass/artifacts/spell_identity_20261018/blast_radius/runs/probe_annotate_func_in_class_dict_gil0.txt:1-7
  - context_compass/artifacts/spell_identity_20261018/blast_radius/runs/probe_annotate_func_in_class_dict_gil1.txt:1-7
  - context_compass/artifacts/spell_identity_20261018/probes/code_digest_v2.py:54-57
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/code_description_patch_spell_code_digest.md:103-109
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:147-191
  IMPACT: Without the rule a spell_id would depend on whether a class's annotations had been read before bind:
    unstable across processes and call orders, the opposite of S1's contract.
  NEXT: The rule into the code-description patch, with the crystallizer record patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T17:05:55Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: SpellCodeDigest is written from the code-description patch - src/melder/aether/spellbook/bind/
    spell_code_digest.py, staged under the epic's artifacts and copied into the /tmp working mirror (0.2.8255
    with S9's E1-E7); nothing in the repository's src. The prototype's probes, re-run against it through a
    two-line adapter: the 42 cases E01-E34 give the designed verdicts and D1-D10 too, D6 keeping its recorded
    limit (two C objects without Python-visible state collide, as under today's repr rule); every id is
    byte-identical across hash seeds 1 and 2 and GIL 0 and 1. The corpus: 783 targets of src/melder digest
    without error; per target cold (a fresh digest, site roots found each time) median 0.46 ms, p95 1.7 ms;
    warm median 0.12 ms, p95 0.47 ms; today's fingerprint median 0.066 ms. A class over pygments'
    PythonLexer, named by version under decision B, costs 0.53 ms cold and 0.013 ms warm (2.6-3.2 ms when it
    was digested).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/staged/src/melder/aether/spellbook/bind/spell_code_digest.py:1-1316
  - context_compass/artifacts/spell_identity_20261018/staged/runs/src_digest_cases_gil0_seed1.txt:1-42
  - context_compass/artifacts/spell_identity_20261018/staged/runs/src_digest_cases_gil1_seed2.txt:1-46
  - context_compass/artifacts/spell_identity_20261018/staged/runs/src_digest_design_edges_gil0_seed1.txt:1-13
  - context_compass/artifacts/spell_identity_20261018/staged/runs/src_digest_corpus_gil0_seed1.txt:1-6
  - context_compass/artifacts/spell_identity_20261018/staged/runs/src_digest_stability_md5.txt:1-8
  IMPACT: S1's digest is ready for Bind; the probes' cases become its unit tests (red first, against src).
  NEXT: BindingManifest and the Spell's manifest (S2), then Bind wired to the digest in the mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T17:05:55Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Four refinements of the code-description contract, made while writing SpellCodeDigest and written into
    the patch in this pass; every probe verdict is unchanged. (1) A code constant that is a number, string
    or bytes literal, None, Ellipsis or a bool is its exact repr: stripping " at 0x..." from every constant
    made a literal such as "listening at 0x1F" equal "listening". (2) An int past the interpreter's decimal
    conversion limit is written in hex: `int.__repr__` raises ValueError there, and the digest never raises.
    (3) A type-parameter or alias part given eagerly (`TypeVar("T", bound=int)`) is `const:` and its stored
    value: its evaluator is a `_typing._ConstEvaluator`, which the `ref:` row reduced to its type, so a bound
    change did not move the id; a part given lazily (PEP 695 syntax) stays its evaluate function's code,
    never called. (4) Containers are read through their builtin base type in one call (`tuple.__iter__`,
    `dict.items`), so a subclass's `__iter__` never runs and a concurrent writer never makes a walk raise.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/staged/src/melder/aether/spellbook/bind/spell_code_digest.py:573-598
  - context_compass/artifacts/spell_identity_20261018/staged/src/melder/aether/spellbook/bind/spell_code_digest.py:687-700
  - context_compass/artifacts/spell_identity_20261018/staged/src/melder/aether/spellbook/bind/spell_code_digest.py:702-738
  - context_compass/artifacts/spell_identity_20261018/staged/src/melder/aether/spellbook/bind/spell_code_digest.py:866-889
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/code_description_patch_spell_code_digest.md:151-155
  IMPACT: The patch stays the exact contract of the code that lands; (1) and (3) close two ways a real change
    kept its id, (2) a way the digest could raise at bind.
  NEXT: Unit tests for the four, beside the probes' cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:51:07Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1 is applied to the /tmp working mirror (0.2.8256 plus the two new modules; nothing in the repository's
    src): one applier over every edit list, all anchors matched in check mode, then written. edits_bind:
    26 edits, one of them the 246-line cut of the old inspector and `sha256_profile`; edits_spell: 19;
    edits_profiles: binding_profile.py 22 and binding_profile_strategy.py 13 (the fingerprint-only fields
    and the `stable_repr` calls that filled them removed, the docstrings corrected); edits_statements: 21 -
    spellbook.py 7 (`inspect_spell`'s stage 3 and its two comments, the conjure refusal, both collision
    refusals, which now name the colliding spell_id, and the research entry's Args), lookup_container.py,
    aether.py, aether_configuration.py (2), the three meld doors, meld.py's two resolvers, details.py (2),
    inspector_utility.py, spell_system_states.py and spell_index.py. The sweep of src/ for "fingerprint"
    found three statements the architecture patch's table did not list (the research entry's
    "Binding-signature SHA256", spell_system_states.py's "the same class at the same address mints the same
    id", spell_index.py's "hottest fingerprint read"); what still says fingerprint is the crystallizer's
    module and seal fingerprints, the codegen's row constants, generation 22's history comment and the new
    modules' mentions of the retired fingerprint. binding_profile_strategy.py mixes CRLF (244 lines) and LF
    (77) in the working tree while git holds it LF; the applier writes it all CRLF, as binding_profile.py is.
    Smoke on the mirror, the GIL off and on, identical: a bound class's spell_id is SpellCodeDigest's, its
    Spell carries its binding manifest, a second registration under another binding name and existence is
    refused with the new text naming the spell_id, and `inspect_spell` finds the class after conjure (an
    unbound class: None).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/scripts/apply_s1_s2.py:1-39
  - context_compass/artifacts/spell_identity_20261018/scripts/edits_statements.py:1-215
  - context_compass/artifacts/spell_identity_20261018/scripts/edits_profiles.py:1-136
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_s1s2_src.diff:1-2018
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_smoke_s1s2_gil0.txt:1-6
  - context_compass/artifacts/spell_identity_20261018/staged/runs/mirror_smoke_s1s2_gil1.txt:1-6
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:165-182
  - src/melder/aether/spellbook/spellbook.py:2544-2675
  IMPACT: S1's source edits are complete in the mirror; before the landing come its tests - the digest's cases
    as unit tests, red against the repository's src and green on the mirror - the blast radius's 101
    rewrites and the whole tree with the GIL off and on; then docs, the notch and the rebuild.
  NEXT: test_spell_code_digest.py from the probes' cases (E01-E34, D1-D10, A1-A3, P1-P10, I1-I9) and the four
    refinements.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T18:44:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The whole tree on the /tmp mirror with S1 and S2 (0.2.8256, the two new modules and the new tests; GIL
    off; 14,697 tests: unit 9,759, component 2,428, integration 2,256, experimentation 254) fails 424. 18
    are melder_1's S8 tests, red on the 0.2.8255 baseline too and on hold with the owner (M1-33); 406 are
    new. By category (whole_tree_triage.py over the failed ids and their first errors): (a) 213 test
    doubles and pins of what S2 changed - the fake Spells of the crystal harness and the snapshot tests have
    no `binding_hash`, and PAYLOAD_FORMAT 2, generation 23 and RecordVersion 4.3.0 moved the pins; (b) 96
    tests of the retired API - `Bind.sha256_profile` (47 of test_bind.py's 48), the profiles'
    `fingerprint_repr` and `spell_id_inspector`'s old keywords; (c) 88 tests that register one object
    twice, now refused (24 files, test_ordered_disposal_replay.py 22); (d) 2 reversed premises (a resolved
    disposal order or a managed binding no longer changes the spell_id); (e) 4 others (the cross-process
    stability test, two resolvable regexes, a two-frame conjure); 3 failed only because the mirror lacked
    repository files, copied in since. The blast radius counted 101 (triage.md) because it ran the identity
    change with the old API and pins in place; categories (a) and (b) are what it could not see. The
    doubles are rewritten (tests_edits_doubles.py: the harness and seven test files): those files and the
    new binding-hash test pass, 350 tests.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2/whole_tree_triage_gil0.txt:1-80
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2/failed_gil0.txt:1-424
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2/base_8255_failed.txt:1-25
  - context_compass/artifacts/spell_identity_20261018/scripts/whole_tree_triage.py:1-93
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_edits_doubles.py:1-234
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_doubles_gil0.txt:1-6
  IMPACT: The tranche is four times the blast radius; (b) to (e) remain: (b) retires the tests of the removed
    API onto their successors or converts them, (c) gives each test one registration per object or makes
    it a refusal test, (d) asserts the binding hash moves where the spell_id used to, (e) one at a time.
  NEXT: Category (b): read test_bind.py's `sha256_profile` tests and map each to its successor before
    retiring it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T18:48:19Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: test_bind.py's 44 test functions of `Bind.sha256_profile` (47 cases), read whole, test a function S1
    removes. 43 are retired onto the successors that carry their property now (the map names one per
    test); the non-bool `resolvable` check (4 cases) moves to public `Bind.bind`, refused before the
    target is examined; the inspector test is rewritten - `Bind.spell_id_inspector` equals
    `SpellCodeDigest().spell_id`, the same on every call, with no binding profile built. Three successor
    cases are added to test_spell_code_digest.py where none existed: methods defined in another order
    keep the spell_id, a parameter's kind moves it, and non-ASCII identifiers digest stably. Five of the
    retired tests pinned what the owner's design reverses (annotation values and parameter annotations,
    the dataclass and decorated flags, the origin file); their successors assert the opposite. Section
    comments left without tests are kept and say where their tests went. The owner was told (chat).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2/retired_sha256_profile_tests.md:1-65
  - tests/unit/melder/spellbook/bind/test_bind.py:365-399
  - tests/unit/melder/spellbook/bind/test_bind.py:638-734
  - tests/unit/melder/spellbook/bind/test_bind.py:936-966
  - tests/unit/melder/spellbook/bind/test_bind.py:1004-1017
  - tests/unit/melder/spellbook/bind/test_bind.py:1193-1204
  - tests/unit/melder/spellbook/bind/test_bind.py:1269-1282
  - tests/unit/melder/spellbook/bind/test_bind.py:1425-1456
  - tests/unit/melder/spellbook/bind/test_bind.py:1605-1660
  - tests/unit/melder/spellbook/bind/test_bind.py:1715-1728
  - tests/unit/melder/spellbook/bind/test_bind.py:1764-1826
  IMPACT: test_bind.py's 48 failures close and every property they pinned stays under test, on the digest or
    the manifest; the edit list is the batch `bind` of tests_apply_s1_s2.py.
  NEXT: tests_edits_bind.py: check, apply to the mirror, run test_bind.py and the digest's tests (GIL off).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T19:11:29Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Category (b), the retired API's tests, is done in nine of its ten files, and with it the rewrites
    those files held of the other categories: nine batches of tests_apply_s1_s2.py (bind, managed,
    fingerprint, profile_strategy, component_bind, lifecycle_hooks, inherited, ordered_disposal,
    resolvable_registration), applied to the /tmp mirror, close 116 of the 424 failed ids - (b) 95 of
    96, (c) one object registered twice 18 of 88, (d) the ordered-disposal reversed premise 1 of 2,
    (e) the two resolvable-registration regexes 2 of 4. The nine files and the digest's test pass, 503
    tests, with the GIL off and on. A staged second member is a second version of its class - a subclass
    with the same name, qualname and module and one class-level value more (`second_version_of`) -
    because staging the class itself again is refused. Left: test_ordered_disposal_replay.py (1 of (b),
    22 of (c)), 48 of (c) in 20 other files, 1 of (d), 2 of (e); beside them melder_1's 18 S8 baselines.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_category_b_gil0.txt:1-4
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_category_b_gil1.txt:1-2
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2/whole_tree_triage_gil0.txt:1-80
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_apply_s1_s2.py:1-73
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_edits_ordered_disposal.py:1-133
  IMPACT: 74 failed ids of S1 and S2 remain before the whole tree reruns; every batch lands in the
    repository through the same applier, so the mirror's green is the landing's.
  NEXT: test_ordered_disposal_replay.py: the staged member becomes a second version of the service, the
    restore-policy tests assert the kept spell_ids and the reported binding changes; batch ordered_replay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T19:59:24Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The test tranche is done in the mirror: batches ordered_replay, one_object_a and one_object_b of
    tests_apply_s1_s2.py close the last 74 failed ids - (b) 1; (c) 70, one object registered twice, by a
    class of its own where a test only needs a second spell, `version_of` (a subclass with the same name,
    qualname and module and one class-level value more) where the name matters, a module-level class where
    a restore or graft imports the version, and per-frame spell ids where one class lives in two roots; (d)
    1, a managed binding keeps its spell_id and moves its binding hash; (e) 2, the process-stability child
    and the two-frame conjure. Batch A's files pass 114 tests and batch B's 113, the GIL off and on. The
    whole tree on the mirror (14,645 tests: unit 9,707, component 2,427, integration 2,257,
    experimentation 254) then fails the same 18 ids with the GIL off and on, all melder_1's S8 tests - red
    on the 0.2.8255 baseline and on hold with the owner (M1-33); S9's 7 from that baseline pass at
    0.2.8256. Run 2 counts 52 ids fewer than run 1: 89 gone (the retired API's tests and renamed ones), 37
    new (successors, renames and the binding-hash tests).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2_run2/summary.txt:1-14
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2_run2/failed_gil0.txt:1-18
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2_run2/failed_gil1.txt:1-18
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2_run2/id_diff_run1_run2.txt:1-133
  - context_compass/artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2/base_8255_failed.txt:1-25
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_one_object_a_gil0.txt:1-1
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_one_object_a_gil1.txt:1-1
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_one_object_b_gil0.txt:1-1
  - context_compass/artifacts/spell_identity_20261018/staged/runs/tests_one_object_b_gil1.txt:1-1
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_edits_one_object_a.py:1-302
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_edits_one_object_b.py:1-472
  - context_compass/artifacts/spell_identity_20261018/staged/tests/_spell_identity_test_support.py:1-46
  IMPACT: S1 and S2 are green in the mirror end to end, and every batch lands through the same applier, so the
    landing's tree is the mirror's; the exit gate's last item, bind's cost, is the next note.
  NEXT: The landing pass: apply_s1_s2.py and tests_apply_s1_s2.py on the repository (--check, then the run),
    with a copy batch for the two new tests no batch copies; then the notches, the docs and the rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T19:59:24Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Bind's cost before (0.2.8256) and after (S1 and S2), through the benchmark's own cycle
    (profile_bind_conjure_cycle.run_cycle, caching disabled, no meld sweep - its sweep fails at 0.2.8256,
    before and after alike), 20 cycles a run: the gauntlet's 29 classes bind in 5.9-6.2 ms before and
    7.8-8.0 ms after with the GIL off (6.3 and 7.9 ms with it on), one bind's median 194-200 us before and
    249-253 us after, +55 us; 200 generated classes bind in 38.6-39.4 ms before and 46.5-48.0 ms after,
    187-189 us a bind before and 225 us after, +37 us. Conjure is unchanged (12.3-12.7 ms; 60.8-61.8 ms),
    so setup grows about 10% (18.6 to 20.4 ms) and 9% (100 to 109 ms); a meld reads none of it. The
    profile puts the difference in `SpellCodeDigest.spell_id`: `Bind._bind_logic` takes 0.150 s before
    and 0.225 s after over 580 profiled binds, spell_id 0.077 s of it; the binding profile costs the same
    before and after. The code memo is per Bind, so each new Spellbook digests every class's code again.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/probes/probe_bind_cost.py:1-74
  - context_compass/artifacts/spell_identity_20261018/probes/probe_bind_cost_profile.py:1-54
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/gauntlet_before_gil0_r1.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/gauntlet_before_gil0_r2.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/gauntlet_before_gil1_r1.txt:1-9
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/gauntlet_after_gil0_r1.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/gauntlet_after_gil0_r2.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/gauntlet_after_gil1_r1.txt:1-9
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/synth200_before_gil0_r1.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/synth200_before_gil0_r2.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/synth200_after_gil0_r1.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/synth200_after_gil0_r2.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/profile_bind_before_gil0.txt:1-52
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/profile_bind_after_gil0.txt:1-52
  IMPACT: The exit gate's measurement is made: +37 to +55 us a bind, once per registration; melds unchanged.
  NEXT: The landing pass (the tranche note's NEXT); the cost is the owner's to weigh (RISK note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T19:59:24Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: RISK
  CLAIM: Bind costs 20-31% more after S1 (+37 to +55 us a class, setup +9-10%) because the spell_id now reads
    every function's code. Two remedies, unmeasured and not in this landing: a code memo shared by every
    Spellbook (owned by Aether, weakly keyed by code object), so a class bound again in a new Book
    digests nothing; and hashing incrementally instead of joining text. How much each recovers is UNKNOWN.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/profile_bind_after_gil0.txt:1-52
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/gauntlet_after_gil0_r1.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/runs/bind_cost/synth200_after_gil0_r1.txt:1-5
  IMPACT: A world binding a few hundred classes pays a few milliseconds more at setup; a process that builds
    Books often pays it for every Book.
  NEXT: Land as measured unless the owner says otherwise; told in chat with the numbers.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T20:03:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S1 and S2 are applied to the repository: apply_s1_s2.py (26 files edited, the two new modules copied)
    and tests_apply_s1_s2.py (every batch, then a new batch `new_tests`), each --check first, wrote
    nothing until every anchor matched, and the repository's src/ then equals the mirror's byte for byte.
    tests/ equals it too but for two files melder_1 committed at 0.2.8256 after the mirror was built - its
    S4 red tests (test_separated_version_is_known_to_its_frame_integration.py and the residency test in
    test_mutation_research_root.py), red by design until S4 lands. One new test module existed only in the
    mirror, test_spell_code_digest_libraries.py (decision B's nine tests, in both whole-tree runs): it is
    staged now and copied by `new_tests` with the binding manifest's tests and the component test.
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/scripts/apply_s1_s2.py:1-39
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_apply_s1_s2.py:1-105
  - context_compass/artifacts/spell_identity_20261018/scripts/tests_edits_new_tests.py:1-23
  - context_compass/artifacts/spell_identity_20261018/staged/tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py:1-119
  IMPACT: The code and tests of the landing are in place; nothing is committed (the owner commits). The landed
    tree's whole run, with melder_1's S4 tests, comes with the rebuild mirror.
  NEXT: The docs: the patch docs promoted into the system documents, their indexes, the graph; then the
    notches, the release note, the closure and the rebuild.
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
  note of 2026-10-18T15:01:53Z); the patches are updated for B and strict uniqueness before the code. S9
  landed as 0.2.8256 and spellbook.py and spell.py are back (M1-38; the epic's FACT note of
  2026-10-18T17:23:22Z).
- Done: Bind's fingerprint and the binding profile read whole; the prototype extended to bases, class-level
  values, object data and closures, and measured (MEASURE note).
- Done since: the four patch docs in system_docs/patches/active/spell_identity_is_the_code_2026_10_18/, the D
  probe (MEASURE note) and the mapping (PLAN note).
- Done since: the patches updated for B and strict uniqueness (FACT note).
- Done since: the blast radius measured and the `__annotate_func__` rule found (MEASURE and FACT notes of
  2026-10-18T16:24:12Z).
- Done since: the `__annotate_func__` rule written into the code-description patch (2026-10-18T16:32:46Z).
- Done since: SpellCodeDigest written and probed in the mirror; four contract refinements in the
  code-description patch (MEASURE and DECISION notes of 2026-10-18T17:05:55Z).
- Done since: S1 applied to the /tmp working mirror with S2 - the profiles and the statements sweep -
  and smoke-checked (FACT note of 2026-10-18T17:51:07Z).
- Done since: the whole tree run on the mirror and triaged - 424 failures, 18 of them melder_1's S8
  baseline; the doubles rewritten and green (MEASURE note of 2026-10-18T18:44:20Z).
- Done since: category (b) in nine of its ten files with the rewrites they held - 116 failed ids
  closed, 503 tests green with the GIL off and on (MEASURE note of 2026-10-18T19:11:29Z).
- Done since: the tranche finished - the ordered-disposal replay (S2's MEASURE note of
  2026-10-18T19:17:19Z), then (c), (d) and (e) in 20 files - and the whole tree green but melder_1's 18
  S8 tests, the GIL off and on (MEASURE note of 2026-10-18T19:59:24Z).
- Done since: bind's cost measured - +37 to +55 us a bind, setup +9-10%, conjure and melds unchanged
  (MEASURE and RISK notes of 2026-10-18T19:59:24Z).
- Next: the landing pass with S2 - src and tests into the repository, docs, the notches (read at
  landing, above 0.2.8256), the release note, the rebuild last.

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
