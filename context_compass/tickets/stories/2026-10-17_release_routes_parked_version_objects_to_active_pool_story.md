# Story: release_routes_parked_version_objects_to_active_pool - a release after a notch strands a version's pool

## Metadata
- Story ID: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool
- Epic: EPIC-2026-10-17-correctness_defects
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T21:07:53Z
- Updated: 2026-10-18T00:54:49Z

## User Narrative

As an agent iterating on a managed class, I want its bind settings - mode, limit, queue timeout, reset names - to be
settings of the one spell, not a new version of it, so that changing them keeps one pool whose count stays true, and
every object I release goes back to the pool that leased it.

## Value / MRP Alignment

A pool's count is structure Melder keeps (owner ruling: structure is the contract). Today the settings are hashed
into the spell_id, so the same class bound again with another limit becomes a second version with its own pool, and
a release after a notch can leave a limited_quantity or queue pool counting an object out that it will never get back
- the version then refuses every lease while nothing is out. The owner ruled the hashing itself the bug (chat
2026-10-17): "the bind call itself shouldn't impact the actual SHA256 thats absurd".

## Ticket Contract

- ENTRY_GATE: the owner's direction recorded (DECISION note of 2026-10-17T23:50:39Z); patch docs for the Binding
  Pipeline and the Managed Spell Pools linked here and approved by the owner; the active board row; melder_1's notch
  (0.2.8253) landed, so this lane notches above it with __version__, the release note and the system documents
  released to it.
- EXECUTION_BOUNDARY: part A (free files) - `Bind.sha256_profile` and `Bind.spell_id_inspector` (the managed part
  leaves the fingerprint; `_normalize_managed_options` stays, the Spell keeps the settings),
  `ManagedSpellQuantity._rebind_spell` (re-compose the settings and retention sizes from the new Spell),
  `Creations.ensure_managed_quantity` (rebind outside the store lock), the cache generation (22); regression tests,
  the managed fingerprint tests moved to the new rule; the system documents with their indexes and the graph; the
  release note; one notch; the rebuild last. Part B (after melder_1 releases spellbook.py): `bind_inactive` and
  `add_to_spell_index` refuse a managed version whose class already backs another managed version of the index; the
  collision error names the settings remedy.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probes and their runs (Artifact Links); the managed epic's
  rulings (owner, 2026-10-14: notch and cleanup_spell destroy nothing; identity is not tracked); melder_1's landing
  (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes).
- EXIT_GATE: Q2's bindings are one spell (re-staging the other limit is refused, nothing changed); `cleanup_spell` then
  `bind` with limit 2 keeps the spell_id and the pool, count true and the new limit in force, and an object leased
  before it goes back to that pool; non-managed spell ids byte-identical; Q1 and Q3-Q6 unchanged where they apply;
  regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST if the owner wants existence, disposal names or resolvable out of the spell_id
  too (a larger lane: the creation cache and the stores' disposal records are keyed by spell_id); CONFLICT if a needed
  file is held by another lane.

## Requirements (Functional)

- The spell_id of a managed binding does not depend on its managed settings: one class bound managed at one address
  with one disposal list gets one spell_id whatever its mode, limit, timeout or reset names.
- `bind_inactive` of such a binding onto an index already holding that spell_id is refused as the same spell (the
  collision error), with nothing registered.
- A rebind under the same spell_id (`cleanup_spell`, then `bind` or `bind_inactive`) meets the pool the earlier
  definition left, and the pool takes the new Spell's settings: mode, limit, timeout, reset names and the retention
  sizes they imply. Objects alive stay alive and counted; queue waiters re-check against the new settings.
- A release keeps its routing (one pool of the class: the fast path; several: the cold resolver as today).
- Part B: `bind_inactive` and `add_to_spell_index` refuse a managed version whose class already backs another managed
  version of the index (one class at two addresses or with two disposal lists would otherwise keep two pools).

## Requirements (Non-Functional)

- The warm lease and the warm release keep their cost; emitted plans are unchanged (no plan reads a managed setting).
- No new lock-order edge: the store lock stays a leaf (the rebind runs after it is released); the pool lock stays a
  leaf, taken under the Spell lock as owner stamping already takes it.
- No identity tracking (owner, 2026-10-14: "we don't care about identity").

## Scope Boundaries

- In scope: the managed part of the fingerprint; the pool's re-composition on a same-id rebind; the cache generation;
  part B's staging refusal.
- Out of scope: the address, existence, disposal names and resolvable, which stay in the spell_id (confirmed by the
  owner, 2026-10-18); the resolver's active-version preference; pools of a disposed version (kept by the
  2026-10-14 ruling).

## State Transition Event

- from_state: ready
- to_state: in_progress
- transition_reason: the owner chose the direction (chat 2026-10-17): the bind call's settings must not change the
  spell_id, and the version is notched for the cache (DECISION note). Filed draft -> ready at 2026-10-17T21:07:53Z.

## Dependencies / Related Work
- The managed epic (EPIC-2026-10-14-managed_spell_quantity, completed): its lifecycle table chose "resolver prefers
  the active version" for notch and cleanup_spell.

## Tasks (Implementation Checklist)

- [x] Task: the owner's answer on the open question (2026-10-17: the managed settings leave the spell_id).
- [x] Task: the owner's confirmation of the scope (2026-10-18: only the four settings; DECISION note).
- [x] Task: patch docs for the Binding Pipeline and the Managed Spell Pools (written 2026-10-18T00:07:52Z,
  linked below); the owner's go for part A (2026-10-18).
- [ ] Task: part A with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Task: part B after melder_1 releases spellbook.py.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria

- Worker bound managed (limited_quantity, limit 1) and Worker with limit 2 at the same address and disposal list have
  one spell_id; `bind_inactive` of the second onto the first's index is refused and nothing changes.
- `cleanup_spell` of Worker, then `bind` of it with limit 2: the spell_id is the same, the pool is the same object with
  its idle objects and count, it leases up to 2, and releasing an object leased before the rebind keeps the count true.
- Every managed spell_id differs once from the one 0.2.8253 gave; every other spell_id is byte-identical.
- Part B: staging Worker into Worker's index under another binding name is refused.

## Validation / Test Plan

- Regression tests named for the symptom, e.g. `test_managed_settings_do_not_change_the_spell_id`,
  `test_restaging_a_settings_only_version_is_refused_as_the_same_spell` and
  `test_rebinding_with_new_managed_settings_recomposes_its_pool`; the managed fingerprint tests moved to the new rule;
  GIL off and on; probes Q1-Q6 and S1-S2 re-run. Not run: no fix exists yet.

## UX / API / Data Notes

- **Breaking change:** every managed spell's spell_id moves once (non-managed ids do not), and staging the same class
  with only other settings is refused as the same spell; change settings with `cleanup_spell` and a new `bind`.
- Bundles written before the notch are cold once (the cache admits only its own release; generation 22 records it).
- A record made by 0.2.8242-0.2.8253 restores with mapped ids (restore maps a changed SHA); one holding two
  settings-only versions of one class in one index cannot rebuild both - the patch decides refusal or a shortfall.
- Under process-wide spell ids, two frames binding one managed class at one address now share its spell_id, so the
  second bind is refused as any other duplicate is.

## Risks / Mitigations

- A new limit below the live count: nothing is destroyed; the pool builds again only once the count falls below it.
- A mode change with queue waiters: the rebind wakes them so each re-checks under the new settings.
- The restore and graft edge above: decided in the patch docs before code.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions

- Answered (owner, chat 2026-10-18): only the four managed settings leave the spell_id; the address, existence,
  disposal names and resolvable stay (DECISION note).
- Open, for the talk after part A: part B's staging refusal; a legacy record holding two settings-only versions of
  one class in one index (with no extra code its restore fails whole on the collision); whether anything more of
  the bind call leaves the spell_id.
- Answered (owner, 2026-10-17): the earlier options 1-4 - option 2, settings out of the spell_id, as a bug fix
  (DECISION note).

## Decision Log
- 2026-10-17T21:07:53Z: filed under EPIC-2026-10-17-correctness_defects from sweep A6 (Notes).
- 2026-10-17T23:25:30Z: the open question reframed to options 1-4 with 3 recommended; the earlier (a) withdrawn
  (STRATEGY_DISCUSSION note).
- 2026-10-17T23:50:39Z: the owner chose option 2 as a bug fix - the bind call's settings must not change
  the spell_id; notch the version for the cache; melder_0 takes the lane (DECISION note).
- 2026-10-18T00:42:22Z: the owner confirmed the scope (the four settings only) and gave the go for part A;
  part B, the legacy record and anything more are for the talk after it (DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py (cases Q1-Q6)
  - artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_same_id_staging.py (cases S1, S2: the same spell_id staged; a settings change today)
  - artifacts/correctness_defects_20261017/runs/probe_same_id_staging_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_same_id_staging_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_settings_rebind.py (cases R1-R3: a settings change on the tree and on the prototype)
  - artifacts/correctness_defects_20261017/runs/probe_settings_rebind_tree_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_settings_rebind_tree_gil1.txt
  - artifacts/correctness_defects_20261017/runs/probe_settings_rebind_proto_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_settings_rebind_proto_gil1.txt
  - system_docs/patches/active/managed_settings_spell_id_2026_10_17/architecture_patch.md
  - system_docs/patches/active/managed_settings_spell_id_2026_10_17/component_patch_binding_fingerprint.md
  - system_docs/patches/active/managed_settings_spell_id_2026_10_17/component_patch_managed_pool_rebind.md
  - system_docs/patches/active/managed_settings_spell_id_2026_10_17/code_description_patch_managed_pool_rebind.md
  - system_docs/patches/active/managed_settings_spell_id_2026_10_17/component_patch_creation_cache_generation.md
  - system_docs/patches/active/managed_settings_spell_id_2026_10_17/component_patch_staging_refusal.md
- DISPOSITION: retain_as_reference (probes and runs); promote_to_documentation (the patch docs)
- CLEANUP_TRIGGER: the probes are re-run at the fix and kept as the defect's reproducers; the patch docs are
  promoted into the system documents at landing and archived under system_docs/patches/completed/

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - which pool a released managed object goes back to when versions of one index share a class
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T21:07:53Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T21:07:53Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8252. `ReleaseManagedSpell.release` takes its fast path only for
    a class with one pool; otherwise `_resolve_pool` keeps the pools matching the filters and, when several remain,
    the one whose version its index selects (`_is_selected_version`). Two versions of one index that bind the same
    class have one pool each, so after a notch every unfiltered release of the class goes to the new active version.
    `put_back` pools any object without counting it, and the count of the pool that leased it - raised by its own
    `reserve()` - never comes down. Probe Q2 (A limited_quantity limit 1, B the same class limit 2): Worker #2
    leased from A, B staged and notched in, `release(obj)`: B count 0 idle 1, A count 1 idle 0; B serves #2 next;
    after a notch back A raises ManagedSpellExhaustedError "has all 1 objects out" with nothing out. Q3 (the same
    with `spell_id=A`) stays right; Q6 (versions that are two classes) routes by class. Identical with the GIL off
    and on (ids masked).
  EVIDENCE:
  - src/melder/aether/conduit/creations/release_managed_spell.py:357-399
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - src/melder/aether/conduit/creations/release_managed_spell.py:625-645
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:474-545
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:548-606
  - context_compass/tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md:401-412
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py:1-205
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil0.txt:1-64
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil1.txt:1-64
  IMPACT: A limited_quantity or queue version can refuse every lease after a notch back while nothing is out.
  NEXT: The owner's answer on the open question, then patch docs for the resolver.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T23:25:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Talked through with the owner (chat 2026-10-17: he asked to see the class diff and to talk S6 "properly").
    The two versions in probe Q2 are one class object: only the bind's `managed_spell_limit` differs (1 vs 2), and
    managed settings are hashed into the spell_id, so B is a second version with its own pool; a changed class is a
    new class object and routes by class (Q6). A pool's count is the objects it built that are alive and `put_back`
    pools any object uncounted, so an object leased before a notch and released after it leaves the old pool counting
    it out for good and the new pool holding one it never counted (it can exceed its limit by it, a trim there can
    drop its count, and the object's children stay recorded in the old pool). The earlier recommendation (a) is
    withdrawn: notch and cleanup_spell keep the old pool registered for the root's life, so a ValueError on an
    ambiguous release would fire on every release of the class once a second version is staged, and a holder of an
    injected object has no spell_id to pass. Options put to the owner: (1) pools remember what they lent - exact,
    a record per lease, reversing the 2026-10-14 identity ruling, whose design measured 3-4x cheaper per cycle than
    the earlier shell that kept an out-record; (2) managed settings leave the spell_id - alone it does not close the
    hole (the same class under another binding name) and every managed spell_id moves once; (3) one managed version
    per class per index, refused at `bind_inactive` and `add_to_spell_index` - recommended: no lease or release cost,
    no spell_id moves, the rulings stand, settings-only versions are lost; (4) one shared pool per class per index,
    its settings following the active version - keeps settings-only versions, reworks the pool ownership of
    0.2.8241-0.2.8248.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:1019-1150
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:474-606
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:704-759
  - context_compass/tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md:401-414
  - context_compass/tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md:673-687
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py:31-121
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil0.txt:9-22
  IMPACT: The fix and its file follow the choice: option 3 sits in spellbook.py (melder_1's), option 1 in
    release_managed_spell.py, managed_spell_quantity.py and the plan emission, option 4 across the managed stack.
  NEXT: The owner's choice among options 1-4; then rewrite this story's boundary, requirements and acceptance to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T23:50:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's ruling (chat 2026-10-17): "yeah so the bind call itself shouldn't impact the actual SHA256 thats
    absurd" and "this means you gotta notch the version for the cache because this is a bug". S6 takes option 2 as a
    bug fix: the four managed settings (mode, limit, timeout, reset names) leave the spell_id, so Q2's two bindings of
    one class at one address are one spell with one pool. bind and bind_inactive hash alike; only arguments enter the
    SHA (`sha256_profile`: resolvable as the domain, spellframe, binding_name, existence, the resolved disposal names
    and, for a managed binding, the settings part). With the settings out: re-staging a settings-only version meets
    the existing collision refusal (probe S1); changing a managed spell's settings is `cleanup_spell` then `bind`,
    which keeps the spell_id (probe S2 shows a new id today), so `Creations.ensure_managed_quantity` meets the same
    pool and `ManagedSpellQuantity._rebind_spell` must re-compose its settings from the new Spell (today it assumes
    them equal, "hence the same options"). No emitted plan reads a managed setting (only the pool and the record do),
    so plans are unaffected; the cache admits only bundles stamped with the running release, so the notch retires
    every bundle, and a cache generation bump records it. Scope put to the owner for confirmation: the address stays
    in the spell_id (one class under two names is two spells); existence, disposal names and resolvable stay (they
    shape the plan the creation cache stores under the spell_id, whose full hit is keyed by spell ids and the world
    stamp). Residual: one class staged in one index at another address (or with other disposal names) still makes
    two pools; proposed refusal at staging, in spellbook.py after melder_1's release.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:1019-1150
  - src/melder/aether/spellbook/bind/bind.py:1217-1250
  - src/melder/aether/spellbook/bind/bind.py:774-805
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:130-196
  - src/melder/aether/conduit/creations/managed_spell_quantity.py:835-857
  - src/melder/aether/conduit/creations/creations.py:1118-1174
  - src/melder/utilities/caching_system/caching_system.py:773-830
  - src/melder/aether/spellbook/spellbook_creation_system.py:616-708
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_same_id_staging.py:1-79
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_same_id_staging_gil0.txt:1-6
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_same_id_staging_gil1.txt:1-6
  IMPACT: S6 has its direction; the fix sits in free files (bind.py, managed_spell_quantity.py, creations.py,
    caching_system.py); only the residual refusal waits for spellbook.py. Every managed spell_id moves once.
  NEXT: The owner's confirmation of the scope; patch docs for the Binding Pipeline and Managed Spell Pools meanwhile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T00:03:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The direction holds on a prototype (a /tmp mirror of src/ and tests/; the repo untouched), and the tree shows
    the defect on the plain settings-change path too. Tree (probe R1): Worker limit 1 with one object out,
    `cleanup_spell`, `bind` with limit 2 - a new spell_id and a second pool; releasing the first object with no filter
    puts it into the new pool uncounted while the disposed version's pool counts it out for good. R2: staging limit 2
    is a second spell; R3: a mode change is a second pool. Prototype (the managed part dropped from `sha256_profile`;
    `_rebind_spell` re-composes mode, limit, timeout, reset names and retention sizes under the pool lock, called by
    `ensure_managed_quantity` after the store lock): R1 the same spell_id and pool object, limit 2, counts true after
    the release; R2 refused ("Spell ID collision detected"); R3 count 3 above limit 1 stays, the fixed capacity trims
    one per release. Test impact in the mirror: 2 unit tests (the managed part's form; each option moving the id) and
    13 integration tests that build a second version from one class with other settings fail; the other managed
    suites pass (2858, 672, 123 and 80 passed). Identical with the GIL off and on (ids masked).
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_settings_rebind.py:1-141
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_settings_rebind_tree_gil0.txt:1-42
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_settings_rebind_tree_gil1.txt:1-42
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_settings_rebind_proto_gil0.txt:1-34
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_settings_rebind_proto_gil1.txt:1-34
  - tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py:481-518
  - tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py
  - tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py
  IMPACT: Part A is two small src changes plus tests; the failing tests encode the old rule (a second version made
    from one class by its settings) and move to versions made from two classes.
  NEXT: Patch docs (architecture, Binding Pipeline and Managed Spell Pools components, the pool's code description).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T00:07:52Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written for the owner's approval (system_docs/patches/active/managed_settings_spell_id_2026_10_17:
    the architecture patch, three component patches for part A, the pool's code description, and part B's component
    patch). Mapping, patch section -> implementation -> validation: (1) Binding Pipeline -> `Bind.sha256_profile`
    loses the managed part and its four keywords, `_managed_fingerprint_part` retires, `_bind_logic` and
    `spell_id_inspector` hash without the settings -> the moved fingerprint unit tests, probe S1-S2; (2) Managed Spell
    Pools and the code description -> `ManagedSpellQuantity._rebind_spell` re-composes (equal settings: a pure
    re-point), `Creations.ensure_managed_quantity` calls it after the store lock -> pool and Creations unit tests (per
    mode change, waiters, a lock probe), a multithreaded rebind test, probe R1-R3 as integration tests; (3)
    CachingSystem -> generation 22 "managed_settings_leave_spell_id" -> a generation unit test; (4) the docstrings
    that state the old rule (ManagedSpellMode, SpellCrystal now; Spell and RestoreEngine after melder_1's landing);
    (5) the 13 integration tests that built a second version from one class's settings move to versions of two
    classes; (6) part B after melder_1 releases spellbook.py. Two decisions are the owner's: the scope, and a legacy
    record holding two settings-only versions in one index (recommended: the restore refuses it whole).
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_settings_spell_id_2026_10_17/architecture_patch.md:1-105
  - context_compass/system_docs/patches/active/managed_settings_spell_id_2026_10_17/component_patch_binding_fingerprint.md:1-77
  - context_compass/system_docs/patches/active/managed_settings_spell_id_2026_10_17/component_patch_managed_pool_rebind.md:1-78
  - context_compass/system_docs/patches/active/managed_settings_spell_id_2026_10_17/code_description_patch_managed_pool_rebind.md:1-56
  - context_compass/system_docs/patches/active/managed_settings_spell_id_2026_10_17/component_patch_creation_cache_generation.md:1-45
  - context_compass/system_docs/patches/active/managed_settings_spell_id_2026_10_17/component_patch_staging_refusal.md:1-60
  IMPACT: The entry gate needs only the owner's approval and melder_1's landing; no src/ edit before both.
  NEXT: The owner's approval of the patch docs and his answers on the scope and the legacy record.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T00:08:19Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: melder_1 answered (M1-25, 2026-10-17T23:54:28Z, re M0-188 and M0-189): it takes 0.2.8253 next (re-read at
    the notch), then its release-note entry, the graph and the rebuild last; `__version__`, the release note, the four
    system documents with their indexes and the graph are free after that rebuild, announced by NOTICE M1-26 with the
    number taken. spellbook.py, conduit.py and fix #1's other files (among them spell.py and restore_engine.py) stay
    held until the owner decides its closure. bind.py, managed_spell_quantity.py, creations.py and caching_system.py
    are not in fix #1 and it does not touch them.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:2680-2705
  IMPACT: Part A can land after M1-26 in its own files; the docstrings of Spell and RestoreEngine that state the old
    rule move to part B's turn (they sit in fix #1's held files), with spellbook.py's refusal.
  NEXT: Wait for M1-26 and the owner's approval of the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T00:42:22Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: melder_1 landed 0.2.8253 (M1-26, 2026-10-18T00:26:52Z; consumed): fix #1 whole, rebuilt last with both
    checks OK. `__version__`, the release note (header 0.2.8253), the four system documents with their indexes and
    the graph are free now, so this lane notches above it (re-read at the notch). The system-documents builder still
    unlinks its payloads, so on the connected folder the rebuild goes through a /tmp mirror. spellbook.py, conduit.py
    and fix #1's other src files stay held until the owner decides its closure.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md:2856-2881
  - context_compass/artifacts/meld_contract_scan_20261015/spell_id_lookup/runs/rebuild_assets_0_2_8253_check.txt:1-7
  - src/melder/__version__.py:12-12
  IMPACT: Part A's landing gate is met (step 2 of the architecture patch's migration order); part B still waits
    for spellbook.py.
  NEXT: Part A, on the owner's go (DECISION note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T00:42:22Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner confirmed the scope and gave the go (chat 2026-10-18): "just do the 4 you know then come back
    later, and we can talk about it but the bind signature can be left out of SHA256 binding I think it makes sense
    so if you agree with that unless you have an objection the rest make sense". Part A lands now with exactly the
    four managed settings (mode, limit, queue timeout, reset names) out of the spell_id. The address, existence,
    disposal names and resolvable stay in it, and melder_0 agrees with no objection: existence, disposal names and
    resolvable shape the plan the creation cache keeps under the spell_id, and the address keeps two bindings of
    one class apart. For the talk after part A: part B's staging refusal; a legacy record holding two settings-only
    versions of one class in one index (with no extra code its restore fails whole on the collision, the answer
    recommended); and whether anything more of the bind call should leave the spell_id.
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_settings_spell_id_2026_10_17/architecture_patch.md:1-106
  - src/melder/aether/spellbook/bind/bind.py:1019-1150
  IMPACT: Part A's entry gate is met (patch docs linked, mapping in the PLAN note, the owner's go, M1-26); S6 moves
    to implementation.
  NEXT: Re-read bind.py's fingerprint, managed_spell_quantity.py and creations.py whole on 0.2.8253; then red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T00:54:49Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Part A's tests are written and red on 0.2.8253 (15 failed, 167 passed, identical with the GIL off and on):
    the bind fingerprint (settings give one spell_id; the inspector, like bind, hashes none), the pool's rebind (a
    new limit, a smaller limit with nothing destroyed, elastic <-> limited_quantity sizes, a queue waiter woken into
    a raised limit, limited -> queue waits, new reset names, describe), the store's rebind (same pool, new settings;
    the store lock free during the rebind) and three integration cases on a real dynamic root (a settings-only
    re-stage refused with nothing changed; `cleanup_spell` + `bind` with limit 2 keeps the spell_id and pool and
    the first object goes back; elastic -> limited_quantity 1 keeps three objects alive and counted). The equal-
    settings rebind, the torn-down rebind and a racing-rebind stress (8 leasers, 1 rebinder) pass already.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/runs/s6_red_gil0.txt:1-312
  - context_compass/artifacts/correctness_defects_20261017/runs/s6_red_gil1.txt:1-312
  - tests/integration/melder/conduit/test_conduit_integration_managed_settings_rebind.py:1-184
  IMPACT: The tests encode the acceptance criteria before the fix; the src change is next.
  NEXT: Apply part A to src/ (scripts/s6_part_a_src.py) and re-run green, GIL off and on.
  REREAD: HELPFUL
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

- Scope: the managed settings leave the spell_id (the owner's ruling); a same-id rebind re-composes its pool; the
  notch and a cache generation bump retire old bundles; part B refuses the residual same-class staging. Defect
  proven on 0.2.8252 (Notes); probes and runs in Artifact Links.
- State: in_progress (melder_0), implementation. The direction and the scope are the owner's (DECISION notes
  of 2026-10-17T23:50:39Z and 2026-10-18T00:42:22Z): only the four managed settings leave the spell_id.
  melder_1's 0.2.8253 landed (M1-26). Part A sits in free files (bind.py, managed_spell_quantity.py,
  creations.py, caching_system.py); part B in spellbook.py (melder_1's until its release).
- Next: (1) part A with its tests, docs, notch (above 0.2.8253) and the rebuild last; (2) report to the owner
  and talk through part B, the legacy record and anything more of the bind call; (3) part B after melder_1's
  release of spellbook.py.

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
