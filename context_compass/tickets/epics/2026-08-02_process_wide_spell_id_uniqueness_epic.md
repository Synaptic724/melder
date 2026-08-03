# Epic: Process-wide spell_id uniqueness

## Metadata
- Epic ID: EPIC-2026-08-02-process-wide-spell-id-uniqueness
- Status: in_progress
- Owner: cowork
- Agent Name: tester_0
- Priority: p1
- Created: 2026-08-02T20:10:00Z
- Updated: 2026-08-02T20:10:00Z

## Problem / Opportunity

The owner believed a spell_id could only exist once. It cannot, and the gap was
reachable from the public API in four ordinary calls:

```python
book_a = md.Spellbook(aetheric_frame="tenant-a")
book_b = md.Spellbook(aetheric_frame="tenant-a")   # SAME frame
book_a.bind(spell=TenantCache, existence="unique")
book_b.bind(spell=TenantCache, existence="unique") # SAME class -> SAME spell_id
book_a.conjure(); book_b.conjure()                 # both succeeded
```

Two live `Spell` objects, one `spell_id`, one frame, two separate singletons. No
guard fired. Reproduced by the owner before any code was written.

OWNER RULING 2026-08-02: **one spell_id means one spell, process-wide.** Not
per-frame. That is a deliberate semantic change - see the Decision Log, because
it retires a shipped and taught behaviour.

## Context (why now, relationship to architecture)

`spell_id` is a SHA256 over the bind-time fingerprint (`bind.py:572-631`):
schema version, class name/qualname/module/bases/mro/annotations/method_names/
init_signature, then optional spell_name, spellframe, binding_name, existence and
disposal names. **The aetheric frame is not in that list.** So the same target
bound with the same parameters mints the same id in every frame, by construction.

Three guards exist and each covers a different scope:

| guard | scope | why it missed |
| --- | --- | --- |
| `_register_owned_spell_id` (`spellbook.py:1086`) | one Spellbook | different book, different `_spells_by_id` |
| `LookupContainer.claim` (`:117`) | one binding signature, frame-wide | identical id -> idempotent, overwrites silently |
| `_check_for_spell` -> `has_spell` (`:4988`) | spell_id, frame-wide | reads a registry populated only at CONJURE |

The third is the hole. `AethericFrame._selected_spell_registry` is handed the
Spellbook's live `_spell_ids` reference inside `Conduit.__init__`
(`conduit.py:1375-1377`), so two books that bind before either conjures are
invisible to each other. Since the ordinary flow is bind -> bind -> conjure ->
conjure, that guard effectively never fires across Spellbooks.

The design ANTICIPATED this. `EPIC-2026-06-14-spellindex-genuine-index-operations`
states the requirement verbatim: *"the reason 'all ids seen' was tracked is
existence-uniqueness, and a dormant candidate's spell_id is still
allocated/taken... bind could re-mint a duplicate of a sleeping spell."* The
requirement is correct and the check sits in the right place. Only the data
arrives late. This is a WIRING failure, not a design failure.

## MRP alignment

MRP: identity is foundational. A runtime where one id can name two objects cannot
have trustworthy persistence, mutation research residency, or graph semantics
built on top of it - each of those keys on spell_id. Fixing it after those layers
harden is a foundational rewrite, which is exactly what MRP exists to avoid.
Ship the identity law now; polish vocabulary after.

## Ticket Contract
- ENTRY_GATE: owner ruling recorded (below), reproduction confirmed by the owner,
  and a green suite before the first slice.
- EXECUTION_BOUNDARY: `aether.py`, `aether_configuration.py`, `aetheric_frame.py`,
  `spellbook.py`, `lookup_container.py`, and their tests. No changes to meld
  resolution, phase compilation, or the transaction plane.
- DEPENDENCIES: none blocking. S4 touches the crystallizer record contract.
- EXIT_GATE: a spell_id can exist at most once per process; every teardown path
  releases it; owner-run suite green; the naming no longer contradicts the
  semantics.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any legitimate feature requires
  duplicate ids in one process. Clusters were checked and do NOT (see Notes).

## Goals
- One spell_id, one spell, process-wide, enforced at bind and at conjure.
- Every destruction path removes the id from the authoritative set.
- Configuration surface with a safe default and a documented off-switch.
- Names that describe what the structures hold.

## Non-goals
- Changing how spell_id is computed. The fingerprint is correct.
- Reworking `LookupContainer`. Signatures are a separate axis (see Notes).
- Fixing the notch signature accumulation - separate concern, separate ticket.
- Cluster redesign.

## Scope boundaries
- In scope: identity allocation, its registries, its lifecycle, its vocabulary.
- Out of scope: resolution, activity/selection, contracts, meld, phases.

## Requirements

Functional:
- R1 Bind refuses a spell_id already allocated anywhere in the process.
- R2 Conjure refuses before the Conduit is built, not during construction.
- R3 Destroying a spell releases its id; a rebind of the same target then works.
- R4 `process_wide_unique_spell_ids` defaults True and cannot change once a frame
  exists.
- R5 A recorded/restored world preserves the configured regime.

Non-functional:
- N1 No new lock on the bind hot path beyond what the frame already takes.
- N2 The membership test stays O(1); no per-id frame round trips.
- N3 Refusals name the offending spells, not only their SHAs.

## Acceptance criteria
- The four-call reproduction above raises, naming the spell and the frame.
- Two frames binding the same class raise under the default regime.
- Cleanup then rebind of the same target succeeds (no namespace poisoning).
- Owner-run full suite green on 3.14t.
- `rg "_selected_spell_registry"` returns nothing outside history.

## Risks / Mitigations
- RISK: teardown paths drop a REFERENCE today. Against a shared set that removes
  nothing, so a cleaned Spellbook poisons the process namespace permanently and
  rebinding throws forever. MITIGATION: S3 is its own story with its own tests;
  do not fold it into S2.
- RISK: default-True retires per-frame multi-tenancy, which
  `UX_and_AIX_experiences/03_advanced/02_frames_as_worlds.py` teaches as a
  feature. MITIGATION: owner ruled deliberately; the example must be rewritten,
  not deleted - it is now wrong on three counts (see Notes).
- RISK: flipping the regime mid-process strands ids across two registries.
  MITIGATION: freeze-guarded setter; frames read once at birth.
- ROLLBACK: every slice is additive except S5. Reverting S1 restores the hole
  without breaking callers.

## Validation plan
- Component: `test_spellbook_component_spell_id_integrity.py` (landed, 3 tests -
  one positive, two negative controls that guard against over-blocking).
- Regression: full owner-run suite per slice. Baseline 3224 passed / 23 skipped.
- NOT unit-testable in isolation: the bind/conjure ordering hole needs two real
  Spellbooks and a real frame, so component is the right tier.

## Decision log
- 2026-08-02 OWNER: spell_id uniqueness is PROCESS-WIDE, not per-frame.
  Consequence accepted: two frames may no longer bind the same target.
- 2026-08-02 OWNER: `process_wide_unique_spell_ids` defaults to True.
- 2026-08-02 OWNER: the two failing fixtures were flawed, not the check.
- 2026-08-02 OWNER: `Spellbook.bind_inactive` becomes public.
- 2026-08-02 tester_0: the conjure sweep is a PREFLIGHT for error quality; the
  authoritative check-and-set belongs at the frame write, under its own lock.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner ruling recorded, reproduction confirmed, and S1 has
  already landed green against a 3224-test sweep.

## Applicable Anti-Patterns
- [ ] Do not edit a diagnostic probe's fixture to make it green - that deletes
      the finding it was written to catch.
- [ ] Do not trust a field name or docstring over source. This subsystem's names
      are wrong at four consecutive layers (see Notes).
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without owner acceptance and board sync.

## Noting Behavior
- Epic notes: program direction, cross-story tradeoffs, tranche order.

## Notes

- DATETIME: 2026-08-02T20:10:00Z
  TYPE: FACT
  CLAIM: THE NAMES ARE WRONG AT FOUR CONSECUTIVE LAYERS, and this cost most of a
    session. `Spellbook._spell_ids` is honest ("ALL owned ids"). The frame aliases
    that exact object as `_selected_spell_registry` - "selected" reads as ACTIVE,
    but it holds active AND parked ids. `has_spell`'s docstring says it reads
    "SpellIndex member-id sets"; it reads the spellbook's owned-id set.
    `Aether._check_for_spell` and the refusal text both say "the Aether registry";
    Aether stores no spell ids at all and only routes to a frame. Four names, four
    different wrong descriptions of one object.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:329-329
  - src/melder/aether/aetheric_frame/aetheric_frame.py:174-176
  - src/melder/aether/aetheric_frame/aetheric_frame.py:792-816
  - src/melder/aether/aether.py:1731-1762
  IMPACT: Two readers reached OPPOSITE wrong conclusions from these names in one
    session - the owner read "selected" as active-only, the agent concluded the
    LookupContainer was the real authority. Neither is a comprehension failure;
    the labels are load-bearing and wrong.
  NEXT: S5 renames to existence vocabulary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T20:10:00Z
  TYPE: FACT
  CLAIM: THE NAME IS A RENAME FOSSIL, and the ticket history explains it exactly.
    `EPIC-2026-06-16-spellindex-terminology-rename` mapped `_version_registry` ->
    `_selected_spell_registry` as one of 401 mechanical sites, explicitly scoped
    "no behavior change... no model reconciliation". At that moment the field WAS
    a derived cache of selected ids, so the name fit. Four days later
    `EPIC-2026-06-14` redefined the contents to active UNION inactive for
    existence-uniqueness, and on 2026-06-28 the implementation replaced
    re-derivation with a live `_spell_ids` reference (also fixing a ~15% slowdown).
    The semantics changed; the name did not follow, because the rename epic had
    forbidden semantic work and the build epic was not a rename lane.
  EVIDENCE:
  - context_compass/tickets/epics/completed/2026-06-16_spellindex_terminology_rename_epic.md:76-76
  - context_compass/tickets/epics/completed/2026-06-14_spellindex_genuine_index_operations_epic.md:725-745
  - context_compass/tickets/epics/completed/2026-06-14_spellindex_genuine_index_operations_epic.md:820-830
  IMPACT: Neither epic was wrong in isolation. The gap is that no step re-checked
    identifiers against contents afterwards. This repo has a staleness protocol for
    DOCUMENTS and none for IDENTIFIERS.
  NEXT: S5 carries this history as its rationale so the rename is not re-litigated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T20:10:00Z
  TYPE: FACT
  CLAIM: THREE FINISHED MECHANISMS AIMED AT THIS PROBLEM ARE WIRED TO NOTHING.
    (1) `Spellbook._check_all_spells` - the conjure-time sweep, documented, FOUR
    green tests, ZERO production callers. `test_spellbook.py:4879` stubs it with
    `lambda: None`, which only makes sense if something once called it.
    (2) `AethericFrame.has_lookup_spell_id` - framewide, spell_id-keyed, O(1), no
    callers. (3) `LookupContainer.contains_spell_id` - same, no callers beyond the
    frame's own wrapper. HYPOTHESIS for (1): it takes the SPELLBOOK lock while the
    frame write takes the FRAME lock, so it could never have been atomic - it may
    be unwireable at the correctness level required, not merely unwired.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2675-2718
  - src/melder/aether/aetheric_frame/aetheric_frame.py:977-987
  - src/melder/aether/aetheric_frame/lookup_container.py:240-251
  IMPACT: Four passing tests assert a system-wide collision guarantee that cannot
    run. A reviewer asking "do we guard id collisions?" finds them and gets a yes.
  NEXT: S6 - delete or wire, decided once, with the tests following the decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T20:10:00Z
  TYPE: FACT
  CLAIM: BIND DECLARES NOTHING TO THE TRANSACTION PLANE; NOTCH DECLARES
    EVERYTHING. `notch_spell` passes `spell_index_id`, `spell_id` AND
    `binding_key` into its change-control metadata. `bind` opens a BIND
    transaction keyed on `_transaction_identity` (per-Spellbook) and
    `_bind_inactive` passes `scope_keys=None, scope_hashes=None,
    binding_keys=None`. `conjure` passes only `spellbook_id`. So the operation
    that CREATES an identity tells the admission plane nothing about what it is
    touching, while the operation that merely REPOINTS one tells it everything.
    Two Spellbooks therefore share no declared scope and the mediator has nothing
    to serialize them on - conjures are NOT serialized per frame.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4443-4448
  - src/melder/aether/spellbook/spellbook.py:4121-4148
  - src/melder/aether/spellbook/spellbook.py:6142-6149
  IMPACT: Explains why no amount of transaction work would have caught this, and
    why the authoritative check must be a lock-held check-and-set at the frame
    write rather than a transaction scope.
  NEXT: Record as a finding; not a story here. Candidate for its own epic.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T20:10:00Z
  TYPE: FACT
  CLAIM: CLUSTERS DO NOT REQUIRE DUPLICATE IDS - checked, because they were the
    strongest candidate for a legitimate exception. `ConduitCluster` shares owner
    spells to members via `Conduit.add_spell_to_contract`, so a borrowed spell
    lands in `_contracted_spell_ids`, NOT `_spell_ids`. Members do not bind their
    own copy. BUT the ruling exposes a real constraint: a member conduit cannot
    bind anything with a hard constructor dependency on a cluster-shared spell,
    because the dependency resolves at conjure and the share arrives afterwards.
    The integration probe that hit this was deleted under owner ruling; the
    correct expression is likely `SpellContract` (late-bound cross-conduit
    socket), which is HYPOTHESIS - `spell_contract.py` was not read.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:4247-4260
  - context_compass/tickets/epics/2026-08-02_process_wide_spell_id_uniqueness_epic.md
  IMPACT: No exemption needed in the uniqueness rule. Cluster coverage is intact
    (~226 cluster test functions across 47 files); one probe was removed.
  NEXT: Open a separate ticket for the member-dependency question if it recurs.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T20:10:00Z
  TYPE: RISK
  CLAIM: THE ADVANCED-TIER EXAMPLE IS NOW WRONG ON THREE COUNTS and currently
    passes, which is how it stayed wrong. `03_advanced/02_frames_as_worlds.py`
    claims (1) two frames binding one class is a supported pattern - retired by
    this ruling; (2) "name uniqueness is a per-frame law" - the spell_ids are
    BYTE-IDENTICAL across frames, not merely similar; (3) "'unique' = one instance
    per FRAME" - disproved at runtime, the owner ran both books on ONE frame and
    still got two singletons, because `Creations` is conduit-affine.
  EVIDENCE:
  - UX_and_AIX_experiences/03_advanced/02_frames_as_worlds.py
  IMPACT: A teaching artifact asserting three false things about identity, in the
    tier that exists to explain frames.
  NEXT: Rewrite under S2 once the regime lands; do not delete - the arc needs an
    act three.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary

The identity law is the point: one spell_id, one spell, process-wide. S1 has
landed and is green - the conjure preflight refuses the owner's reproduction with
a named spell and frame. The configuration surface exists and defaults on. What
remains is the unified set itself (S2), and the part that will actually bite (S3):
every teardown path today drops a per-frame REFERENCE, which against a shared set
removes nothing and would poison the process namespace permanently.

Read the Notes before touching this subsystem. The names in it are wrong at four
layers and cost most of a session; source is authoritative, docstrings are not.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
