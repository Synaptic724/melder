# Task: name_stdlib_functions_and_namespace_packages_in_spell_id - the spell_id follows the object's own code

## Metadata
- Task ID: TASK-2026-10-19-name_stdlib_functions_and_namespace_packages_in_spell_id
- Story: none (standalone backlog task; from S1's RISK note, EPIC-2026-10-18-spell_identity_is_the_code)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-19T01:14:00Z
- Updated: 2026-10-19T01:14:00Z

## Objective
A spell_id is the SHA256 of what a registered object is (`SpellCodeDigest`, 0.2.8257). Two of its inputs
are not the object's own code; this task names them instead of reading them:
- a standard-library function a target holds is named (`fn:<module>.<qualname>`), as a standard-library
  class is named today (`class:` and `mro` lines); the interpreter's minor is already in the hash, through
  the cache tag;
- installed third-party code is named with the distribution that ships its module, not with the first
  distribution in sorted order under its top-level name.

Why (the owner asked for the reason with the task, chat 2026-10-19; source and measurements in the FACT note):
- `SpellCodeDigest._encode` digests every plain function but an installed third-party one, so a class that
  holds a standard-library function - every `typing.NamedTuple` and `typing.TypedDict` class does, through
  `__orig_bases__` - has a spell_id that reads that function's compiled code. The id then moves with no change
  to the class: under -O (measured on 3.14.7: the seven NamedTuple classes among 788 targets, through the
  `assert` in `typing._namedtuple_mro_entries`), and with any 3.14 patch release that changes that code
  (UNKNOWN whether one does; the cache tag names the minor only). Each move costs a cold creation cache and a
  restore that maps the id.
- `SpellCodeDigest._version` names installed code with `importlib.metadata.version(<top-level name>)`, else
  with the first distribution, in sorted order, that `packages_distributions()` lists for that name,
  memoized per top-level name. In a namespace package - several distributions under one top-level name -
  that is whichever sorts first, not the one shipping the module: the id moves when an unrelated
  distribution there upgrades, and stays put when the one shipping the module upgrades, the very change
  decision B names a version for (UNKNOWN whether a cached plan can then replay against changed code).

## Ticket Contract
- ENTRY_GATE: the owner schedules it; an active board row; the holder of spell_code_digest.py takes it;
  the patch gate (a component patch for SpellCodeDigest, an architecture patch for the identity invariant)
  with the owner's calls in Steps.
- EXECUTION_BOUNDARY: `SpellCodeDigest._encode` (its plain-function branch), `_named` and `_version` (the
  shipping distribution), `TAG` if the owner moves the hash domain; their tests; the system documents; the
  release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-18-spell_identity_is_the_code (completed; S1 landed the digest at 0.2.8257);
  its parked S5 (STORY-2026-10-18-spell_id_migration) if records made before must map the ids that move.
- EXIT_GATE: a NamedTuple or TypedDict class has one spell_id with and without -O; installed code from a
  namespace package is named with the distribution that ships its module; no other id moves unless the
  owner moves `TAG`; suites green with the GIL off and on; documents, release note, notch and rebuild done.
- FAILURE_ESCALATION: DECISION_REQUEST when a standard-library function cannot be told by its `__module__`
  (a wrapper made with `functools.wraps`), or when finding the shipping distribution needs more than the
  installed distributions' file lists.

## Scope Boundaries
- In scope: how `SpellCodeDigest` encodes a standard-library function a target holds, and which
  distribution it names for installed code.
- Out of scope: a target's own code under -O (`Nexus.__new__`'s `assert` stays an input: ids are per
  interpreter by the digest's contract); how a module is located (`_is_third_party_module` reads the
  module's own `__file__`, which a module inside a namespace package has); the binding manifest. A
  standard-library class or function registered as the target itself, which `_target_encoding` digests as
  its own code, stays as it is unless the owner widens the task at pickup.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a parked draft on the owner's word ("sure you can make a task for that and
  just leave it at that and move on", chat 2026-10-19), from S1's RISK note; no lane is opened.

## Steps / Checklist
- [ ] The owner schedules it; a holder takes spell_code_digest.py; the patch gate.
- [ ] The owner's calls: move `TAG` (its own rule; every id moves once) or keep it (only the affected ids
      move); the rule for a standard-library wrapper whose `__module__` names the wrapped function's module.
- [ ] Red tests: a NamedTuple class digested in a child interpreter with and without -O gives one id; code
      from a namespace package is named with the distribution that ships it (a metadata fixture).
- [ ] The change; green with the GIL off and on; the parity probe re-run, plain and with -O.
- [ ] System documents (the identity invariant, the Unknowns entry, the component map), the release note
      (which ids move, once), the notch, the rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- `SpellCodeDigest` names a standard-library function a target holds and names installed code with the
  distribution that ships its module; tests that pin both.

## Files / Paths Impacted
- src/melder/aether/spellbook/bind/spell_code_digest.py (`_encode`, `_named`, `_version`; `TAG` on the call)
- tests/unit/melder/spellbook/bind/test_spell_code_digest.py
- tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py
- context_compass/system_docs/src_architecture.md and src_components.md; the graph descriptor of
  spell_code_digest.py; release_docs/next_version_release.md

## Validation
- Not run.
- Recommended commands:
  - python -X gil=0 -m pytest tests/unit/melder/spellbook/bind/test_spell_code_digest.py
    tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py, then the same with -X gil=1
  - python context_compass/artifacts/spell_identity_20261018/probes/probe_spell_id_build_parity.py, plain
    and with -O: only `Nexus.__new__` may differ

## Risks / Rollback Notes
- Every id the change touches moves once: those spells start with a cold creation cache, and a record made
  before maps them on restore (S5 of the identity epic, parked).
- A rule keyed on `__module__` misses a standard-library wrapper that `functools.wraps` gave the wrapped
  function's module (UNKNOWN which wrappers targets hold); settle the rule before coding.
- `packages_distributions()` lists every distribution under a top-level name; telling which one ships a
  module needs their file lists (UNKNOWN cost; memoize per module).
- Rollback: revert the digest hunk (and `TAG`); the moved ids move back.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none (the evidence its Notes cite stays in artifacts/spell_identity_20261018/, retained under the
    completed epic)
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the spell_id's standard-library and namespace-package inputs
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-19T01:14:00Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-19T01:14:00Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Why this task exists, read in source at 0.2.8259. (1) `SpellCodeDigest.spell_id` hashes the cache tag
    (the minor: cpython-314) with the target's encoding; `_encode` encodes a plain function by its code unless
    its module is installed third-party - a standard-library function included - while `_encode` and
    `_class_digest` name a standard-library class (`class:<qualified>`, `mro <qualified>`), and
    `_target_encoding` likewise digests a registered function. So a class holding a standard-library
    function reads that function's compiled code: S1 measured 788 targets byte-identical across 3.14.7's
    builds and GIL modes, and under -O the seven `typing.NamedTuple` classes moved through the `assert` in
    `typing._namedtuple_mro_entries` (S1's MEASURE and RISK notes); patch releases are the open Unknown in
    src_architecture. (2) `_named` names installed code with `_version(module)`:
    `importlib.metadata.version(<top-level name>)`, else the first name in sorted order of
    `packages_distributions()[<top-level name>]`, memoized per top-level name - under a namespace package not
    necessarily the distribution that ships the module. `_is_third_party_module` locates a module by its own
    `__file__`, so the location is right and only the version can be misattributed.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_code_digest.py:202-227
  - src/melder/aether/spellbook/bind/spell_code_digest.py:261-289
  - src/melder/aether/spellbook/bind/spell_code_digest.py:318-355
  - src/melder/aether/spellbook/bind/spell_code_digest.py:602-641
  - src/melder/aether/spellbook/bind/spell_code_digest.py:1170-1193
  - src/melder/aether/spellbook/bind/spell_code_digest.py:1252-1268
  - src/melder/aether/spellbook/bind/spell_code_digest.py:1270-1303
  - context_compass/tickets/stories/completed/2026-10-18_spell_id_hashes_the_object_code_story.md:694-729
  - context_compass/tickets/stories/completed/2026-10-18_spell_id_hashes_the_object_code_story.md:731-757
  - context_compass/system_docs/src_architecture.md:246-255
  IMPACT: Today an id can move with no change to the registered class (-O, a standard-library patch release, an
    unrelated distribution of the same namespace upgrading): a cold creation cache and a restore that maps
    it. And it can stay put when the distribution that ships an installed base class upgrades, the change
    decision B names the version to catch (UNKNOWN whether a cached plan then replays). Naming both makes
    the id follow the object's own code; each affected id moves once.
  NEXT: The owner schedules it; then the patch gate and the owner's calls in Steps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope: name a standard-library function a target holds, and the distribution that ships a namespace
  package's module, in the spell_id, so the id follows the registered object's own code (Objective; the
  why with its evidence in the FACT note).
- State: draft, parked in tickets/tasks/backlog/ on the owner's word (chat 2026-10-19); no board row, no
  lane, no artifacts of its own; nothing started.
- Next: (1) the owner schedules it; (2) the patch gate and the owner's calls in Steps; (3) red tests, the
  change, the documents, the release note, the notch and the rebuild last.

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
