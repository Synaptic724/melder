"""The epic (owner-directed, 2026-10-14): detailed implementation notes for the next agent, additive."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
EPIC = os.path.join(CC, "tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
ART = "context_compass/artifacts/managed_shell_spike_20261014"
TASK_REL = "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md"
S = "src/melder/aether"
CG = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system"
TS = now_utc()
HEAD = "  AUTHOR: fable_0\n  AUTHOR_ROLE: synaptic_python_developer\n"

N1 = f"""- DATETIME: {TS}
{HEAD}  TYPE: DECISION
  CLAIM: THE SETTLED SHAPE (owner rulings of 2026-10-14 in chat with fable_0; implementation handed to the next
    agent by the owner: "add a ton of detailed notes to the epic, I'll get opus to do the rest").
    (1) `Existence.managed_spell_quantity`, a seventh `auto()` member; class spells only (the callable and
    existing-object families stay unique-only). (2) The
    Spell retains every managed requirement as bind options - the mode (`elastic` | `limited_quantity` | `queue`), the
    limit, the queue timeout, the elastic idle cap, and the optional `managed_spell_reset_methods` list - no settings
    object, no composition frame; they are hashed into the spell id for managed bindings only, so no existing id
    moves, and the crystal records them. (3) The holder is `ManagedSpellQuantity(deque)`: the deque holds the IDLE
    objects of one managed spell in one root; the mode and numbers are composed from the Spell when the root's owner
    store is stamped at conjure, and the holder lives in the root's Creations under the spell id as a new record
    shape beside the slotted object and the `many` list; `count` is an int of objects built and alive (limited and
    queue accounting), not a list - the holder keeps NO reference to any object it handed out ("we don't care about
    identity"); one leaf lock plus a Condition, used only on the cold paths (the limited check, the queue wait and
    notify, the elastic trim's count); the elastic system is built into the subclass optionally (trim the oldest idle
    above `max_idle` on append, defaults 20/256 like the kernel pools; the 0.2.8234 decay band only if idle memory
    ever matters). (4) Dispense is inlined in the emitted plan - `try: v = h.pop()` / `except IndexError:
    v = _miss(...)` - no method call, no lock (`deque.pop`/`append` are atomic per object on 3.14t); the miss:
    limited raises when
    `count >= limit`, queue waits `cond.wait_for(count < limit or idle, timeout)` then raises, elastic always builds;
    `count += 1`, then the site's children, then the object; a failed build takes `count` back and disposes the
    children it built. (5) `ReleaseManagedSpell`: a dict keyed by the managed class (`type(obj)` is the class object,
    identity-hashed, one dict get) whose value is the pair `(holder, spell_id)` - the holder for the release itself,
    the spell id as the key into the root's Creations for every cold path; root conduits register their pairs at
    conjure (and a post-conjure bind, and the transfer flip) and unregister at teardown; `release(obj)` runs the reset
    names registered at bind, if any, then `append` - "that's how you clean it up and return it and that's it";
    `release(obj, target)` with the meld-style target when the same class has two pairs (two binding names in one
    frame, or the same id in two frames under per-frame ids); the bare call raises an ambiguity then. Helpers on the
    class are welcome: `managed(obj)` (a small `__enter__`/`__exit__` class, never a generator), `release_all(...)`,
    `describe(cls)`. (6) `Conduit.managed_spell_meld("target")`: meld plus the lease class whose `__exit__` releases
    through the dispensing holder. (7) Nothing is destroyed on notch or cleanup_spell: the old version's holder and
    its objects stay until the scope is destroyed or purged (0.2.8219's "product left alive in its slot" applies);
    `purge(instance)` disposes that object and takes `count` down; `purge_all` disposes the idle objects; root teardown
    disposes the idle objects and drops the registry pair (out objects are the user's - no references are kept, so
    they are not Melder's to destroy; F8's "and out objects" clause is withdrawn). (8) Overrides on a managed site are
    allowed: the key-set plan skips the site, the supplied object is used, no lease is taken (reverses default (g)).
    Injection into any holder is a lease that holder keeps for its life; no Phase 6 rule (managed ranks with
    `unique`: it depends only on `unique`, anyone may depend on it). A managed object's disposal-bearing `many`
    children: a side map id(object) -> children, written only at build and only when there are any, read only when
    that object is destroyed (trim, purge) - never on the warm path. (9) A reset that raises: the object is not
    appended; it is disposed, `count` goes down, the error propagates (owner default (b)). (10) Cache generation 21
    retires executors emitted before managed sites; RecordVersion moves for the recorded options.
  EVIDENCE:
  - {TASK_REL}:356-460
  - {ART}/probe_deque_holder.py:28-104
  - {ART}/logs/probe_deque_holder_run1.txt:1-7
  IMPACT: Requirements F3, F5, F6, F7, F8 and F9 of this epic read with these rulings (next note); the measured
    warm cycle is three to five warm `unique` reads.
  NEXT: the implementation plan (PLAN note below) and the seam map (FACT note below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

"""
N2 = f"""- DATETIME: {TS}
{HEAD}  TYPE: DECISION
  CLAIM: WHICH REQUIREMENT LINES THE RULINGS SUPERSEDE (read F1-F13 and the open questions with this). F2: the
    options live on the Spell (plain bind keywords), the ManagedQuantity working names are dropped; the class merge
    the owner asked for is "no second object at all". F3: the pool is the `deque` holder in the root's Creations
    under the spell id, not a new ConduitCreations location; it holds idle objects and `count`, no record of out
    objects. F5: the release core checks nothing - no "out from this pool" test, no double or foreign refusal; the
    reset is optional and its return value is ignored; a raising reset destroys the object and raises. F6: one way
    back, `ReleaseManagedSpell` (mixin and protocol member dropped), plus the `with`. F7: the index maps the class to
    `(holder, spell_id)` pairs; registered at conjure, removed at teardown. F8: root teardown destroys IDLE objects
    only (no references to out objects exist); purge of one object destroys it; the elastic trim destroys idle
    objects; disposal runs only on destroy. F9 stands as written. F11: overrides allowed (Q6 answered: allow). F12:
    inspection is `describe(cls)` - mode, count, idle; no outstanding-object listing (no references). Open questions:
    Q1 reset optional, return ignored, raise destroys; Q2 a release after its root was torn down raises plainly (the
    pair is gone); Q3 purge with no instance destroys the idle objects, out objects come back as usual; Q4 queue
    stays, timeout required; Q5 managed depends only on unique, anyone may depend on it, `many` children follow the
    object; Q6 allowed; Q7 names: `ManagedSpellQuantity`, `ReleaseManagedSpell`, `managed_spell_reset_methods`,
    `Conduit.managed_spell_meld`; no `conduit.release_managed_spell`; Q8 root scopes; Q9 elastic 20/256 at bind,
    limited and queue keep what they built; Q10 no held-too-long warning; Q11 one way to declare the reset (bind).
  EVIDENCE:
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:99-128
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-258
  - {TASK_REL}:356-460
  IMPACT: Nothing in F1-F13 needs rewriting by hand; this note is the overlay the implementer applies.
  NEXT: the seam map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
N3 = f"""- DATETIME: {TS}
{HEAD}  TYPE: FACT
  CLAIM: THE SEAM MAP, read on the 0.2.8238 working copy (every range opened, not searched). (a) The enum:
    `existence.py:60-117`, six `auto()` members, `__str__` returns the bare name; the seventh is additive.
    (b) The resolution matrix: `resolution_style_matrix.py:108-165` - `EXPECTED_EXISTENCE_COUNT = 6`,
    `ALL_EXISTENCE_NAMES`, `NON_UNIQUE_EXISTENCE_NAMES` and the family policy (class_based supports all; callable
    and existing-object families are unique-only and list the non-unique names as unsupported) - add the member to
    all three tuples and the count; `validate()` refuses an unclassified name. (c) The route family:
    `spell_artifact_processor.py:118-146` maps Existence to `route_family` and raises on an unknown member - add
    `"managed"`; the manifests whitelist it: `strategies/many_only/manifest/many_only_manifest.py:196-214` and
    `strategies/generalized/manifest/generalized_manifest.py:72-90`. (d) The door templates:
    `shared_assets/creation_runtime_door_compiler.py:498-865`, one `(route, lane)` template per existence; the
    `unique` templates at 602-629 (no overrides) and 796-821 (hooks) are the model: the managed template reads the
    holder from `_owner_creations._creations.get(_spell_id)`, inlines `try: creation = holder.pop() / except
    IndexError:` and calls the plan's miss; the warm lane of `Conduit.meld` (`conduit.py:4878-4938`) calls the
    emitted door and never reads a store, so it does not change. (e) The lowering: `site_plan_lowering.py:1331-1470`
    - `_emit_context` places shared sites and `many` steps, `_owner_store_constant` (S9) binds an automatic unique
    site's store as `c{{i}}`, `_emit_shared_hit` emits the read/miss pair, `_emit_miss` emits the children-first miss;
    a managed site is a third shape: bind the holder as `h{{i}}` under the S9 condition (automatic owner, stamped
    store), emit the inline pop, and a miss that reserves (`count`) before the children. (f) The store:
    `creations.py` - record shapes and locks 10-120; `_dispose_disposable_registry` 470-560 and `_dispose_entry`
    576; `purge` 1082 and `_detach_purge_entries` 1188; `extract_spell_creations` 1302-1376 and
    `restore_spell_creations` 1377-1470 - each dispatches by isinstance on the three shapes today; the holder is
    the fourth and gets an explicit branch in all five. (g) Ownership stamping: `Spell._add_owned_conduit`
    (`spell.py:1558-1606`) is called at conjure (`spellbook_creation_system.py:1350-1375`), at a post-conjure
    `bind_inactive` (`spellbook.py:5255-5290`) and `bind` (5590-5620), and at the transfer flip
    (`transfer_of_ownership.py:1470-1505`), after which `_move_creations` (1506-1545) extracts and restores the
    spell's records per lineage member - compose the holder and register the pair here; the holder is the same object
    after a move. (h) The doors outside the store: `conduit_meld.py:843-1086` and `spellspace_meld.py:783-1027`
    (live-creation probes, purge resolution, existing lookups) need the holder branch. (i) Phase 6:
    `scope_ordering_strategy.py:80-121`, the `scope_rank` dict; managed = 0 with unique. (j) Bind:
    `Spellbook.bind` 5400-5450 (keywords) and 5540-5545 (non-hook kwargs flow into `spell.metadata`, which the
    fingerprint does NOT hash); `Bind._bind_logic` 571-640 and the `disposal_method_names` flow 464-570 are the
    model for the reset names; `Bind.sha256_profile` 911-1010 hashes spellframe, names, existence, disposal names
    and resolvable - add the managed options there with a default that leaves every non-managed hash byte-identical
    (the `resolvable` precedent). (k) Cache: `caching_system.py:190-212`, generation 20 is current; add 21.
    (l) Records: `record_version.py:84` CURRENT 4.1.0; the spell crystal must carry the options.
    (m) Notch and disposal leave products alone: `_apply_notch` (`spellbook.py:3824-3965`) parks the outgoing
    version and tears down its creation context only; `_dispose_spell` (4325-4420) cleans the Spell.
  EVIDENCE:
  - {S}/spellbook/existence/existence.py:60-117
  - {S}/spellbook/resolution_style_matrix.py:108-165
  - {S}/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:118-146
  - {CG}/strategies/many_only/manifest/many_only_manifest.py:196-214
  - {CG}/strategies/generalized/manifest/generalized_manifest.py:72-90
  - {CG}/shared_assets/creation_runtime_door_compiler.py:498-865
  - {CG}/shared_assets/site_plan_lowering.py:1331-1470
  - {S}/conduit/conduit.py:4878-4938
  - {S}/conduit/creations/creations.py:10-120
  - {S}/conduit/creations/creations.py:470-620
  - {S}/conduit/creations/creations.py:1082-1206
  - {S}/conduit/creations/creations.py:1302-1470
  - {S}/spellbook/spell.py:1558-1606
  - {S}/spellbook/spellbook_creation_system.py:1350-1375
  - {S}/spellbook/spellbook.py:5255-5290
  - {S}/spellbook/spellbook.py:5590-5620
  - {S}/conduit/conduit_ward/transfer/transfer_of_ownership.py:1470-1545
  - {S}/conduit/meld/conduit_meld.py:843-1086
  - {S}/conduit/meld/spellspace_meld.py:783-1027
  - {S}/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121
  - {S}/spellbook/spellbook.py:5400-5450
  - {S}/spellbook/bind/bind.py:464-640
  - {S}/spellbook/bind/bind.py:880-1010
  - src/melder/utilities/caching_system/caching_system.py:190-212
  - src/melder/crystallizer/persistence/record_version.py:84-85
  - {S}/spellbook/spellbook.py:3824-3965
  IMPACT: Every edit point is named with its model; the only UNKNOWN left is which crystal fields carry the options
    (`spell_crystal.py` and the restore engine's bind replay were not opened for this).
  NEXT: the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

"""
N4 = f"""- DATETIME: {TS}
{HEAD}  TYPE: MEASURE
  CLAIM: THE NUMBERS (VM, CPython 3.14.7t, `-X gil=0`, caching off; the probes and logs are in the artifacts
    folder). Reference: a warm `unique` site read 30 ns; `Manager()` construction 70 ns; a whole
    `conduit.meld("Worker")` 337 ns; a fresh Iris logger meld on MelderOps 74-82 us (parent epic). The owner's deque
    holder, acquire + release per cycle, one idle object: elastic 140 ns through `ReleaseManagedSpell` / 90 ns
    through the known holder (with a declared `reset()` 215 / 149); limited_quantity(4) 124 / 82; queue(4, 1.0 s)
    265 / 239. The spike's earlier `ManagedShell` (entries, weakrefs, a locked warm path) cost 505 / 407, 484 / 389
    and 567 / 461 for the same modes, and inside a real emitted plan 715 ns per Worker creation against 166 ns
    plain; a lock-free variant of it saved only 115-145 ns per cycle and lost the teardown invariants - both are
    reference only now. Stress: limited(3) never exceeds 3 under 8 threads; queue(1, 0.25 s) waits then raises at
    its timeout; a waiter is served by a release (the same object, no build). The `contextlib.contextmanager` form
    of the `with` costs about 600 ns more than a plain class - emit a class. Rerun: `python -X gil=0
    <artifacts>/probe_deque_holder.py` (standalone), `probe_plan_shape.py` and `probe_plan_capture.py` (need
    `tests/experimentation` and the repo on the path, cwd anywhere; they build a world through the certification
    harness and capture the emitted plan).
  EVIDENCE:
  - {ART}/logs/probe_deque_holder_run1.txt:1-7
  - {ART}/logs/probe_door_modes_run2.txt:1-4
  - {ART}/logs/probe_plan_shape_run1.txt:1-11
  - {ART}/logs/probe_modes_run2.txt:1-19
  - {ART}/logs/probe_cost_variants_run1.txt:1-8
  - {ART}/logs/probe_plan_capture_worker_source.txt:1-23
  IMPACT: Success metric 1 (about 5 us to acquire, about 1 us to return) is met by 30x; metric 2 (routing about
    100 ns) by the singleton's +50 ns; the benchmark task of this epic can reuse the probes.
  NEXT: the plan.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

"""
N5 = f"""- DATETIME: {TS}
{HEAD}  TYPE: PLAN
  CLAIM: IMPLEMENTATION ORDER AND TESTS (one lane, one writer per file; each `src/` change notches 0.0001 and adds
    its release-note entry; assets rebuilt last). 1. Enum, matrix, route family and manifest whitelists (seams a-c);
    unit: `ResolutionStyleMatrix.validate()` green with seven members, the processor maps the member. 2. Bind
    options on the Spell, the fingerprint (managed only), the crystal fields and RecordVersion; unit: a non-managed
    binding's id is byte-identical before and after, a managed binding's id changes with its mode/limit/timeout/
    reset names, record and restore round-trip the options. 3. `ManagedSpellQuantity(deque)` and the Creations
    composition at `_add_owned_conduit`, the five readers' branch, purge semantics (one object; idle on purge_all),
    teardown disposes idle; unit per mode: count accounting, limited raise, queue wait/timeout/served-by-release,
    elastic trim at max_idle, reset order and the raising reset; stress: limited never exceeds N under threads.
    4. `ReleaseManagedSpell` (register at the three stamping points and the transfer, unregister at teardown; the
    pair; the ambiguity rule and the target form), the lease class, `Conduit.managed_spell_meld`; unit: routing,
    ambiguity, release after teardown raises plainly; component: `with` releases on exit. 5. The door templates and
    the lowering site shape (the inline pop, the reserve-first miss, children before the object, failure path);
    component: a direct meld dispenses and reuses, injection into a `many` holder and into a `unique` holder, an
    override skips the site, a `many` child with disposal dies with its managed object on trim/purge, a transfer
    moves the holder and releases keep working, a notch leaves the old holder in place; integration: two roots in
    one frame with the same class under two binding names (ambiguity, target), per-frame ids with one id in two
    frames, crystallizer record/restore of a managed world. 6. Phase 6 rank entry; unit: managed may depend on
    unique only, any holder may depend on managed. 7. Cache generation 21; unit: an old-generation bundle is cold.
    8. Docs: src_architecture (boundary list, the meld sequence, operational invariants, failure modes, code map),
    src_components (Creations, Meld doors, Bind, the lowering, Phase 6), tests docs, graph descriptors, the README's
    Existence section, the running release note; `AGENT_PURPOSE` on every new public surface. Benchmarks: the
    probes above as the before/after; no regression on the existing meld paths (the harness's five shapes).
  EVIDENCE:
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:160-200
  - context_compass/special_instructions/agent_contribution_guide.md:1-97
  - {ART}/probe_deque_holder.py:28-104
  IMPACT: The stories of this epic can be cut along steps 1-2, 3-4, 5, 6-7 and 8.
  NEXT: the owner assigns the implementer; TASK-2026-10-14-investigate_managed_shell_design closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
LOG = f"""- 2026-10-14 (final shape, fable_0 for the owner): the Spell keeps the managed options; `ManagedSpellQuantity(deque)`
  of idle objects in the root's Creations under the spell id, an int `count`, no references to out objects;
  `ReleaseManagedSpell` maps the class to `(holder, spell_id)` pairs, registered at conjure, removed at teardown;
  release = optional reset + append; nothing destroyed on notch or cleanup_spell; overrides allowed; the seven-point
  implementation plan and the seam map are in the Notes of this timestamp. The owner hands implementation to the next
  agent ("I'll get opus to do the rest").
"""
for block, label in ((N1, "N1"), (N2, "N2"), (N3, "N3"), (N4, "N4"), (N5, "N5"), (LOG, "LOG")):
    bad = check_line_lengths(block, exempt=r"^  - (context_compass|src|tickets)/")
    if bad:
        raise SystemExit(f"{label}: lines over cap: {bad}")
epic, nl = read_text(EPIC)   # re-read immediately before the edit; additive, anchored
epic = replace_once(epic, "\n## Closure Confirmation\n", "\n" + N1 + N2 + N3 + N4 + N5 + "## Closure Confirmation\n",
                    "closure heading")
epic = replace_once(epic, "## Decision Log\n- 2026-10-14 (owner, chat with fable_0): the holder is a `deque`",
                    "## Decision Log\n" + LOG + "- 2026-10-14 (owner, chat with fable_0): the holder is a `deque`",
                    "decision log head")
epic = replace_once(
    epic,
    "- [ ] Task: TASK-2026-10-14-investigate_managed_shell_design (fable_0) - the owner's shell shape investigated\n"
    "      with a VM spike; feeds the patch docs. tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md\n",
    "- [x] Task: TASK-2026-10-14-investigate_managed_shell_design (fable_0) - the owner's shell shape investigated\n"
    "      with a VM spike; done 2026-10-14: the settled shape, seam map, numbers and plan are in this epic's Notes.\n"
    "      tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md\n",
    "task line")
epic = replace_once(
    epic,
    "- ARTIFACT_PATHS:\n  - artifacts/melder_object_pools_20261011/ (probes and runs, shared with EPIC-2026-10-05)\n",
    "- ARTIFACT_PATHS:\n  - artifacts/melder_object_pools_20261011/ (probes and runs, shared with EPIC-2026-10-05)\n"
    "  - artifacts/managed_shell_spike_20261014/ (the spike: the deque-holder probe, the earlier shell prototype,\n"
    "    the captured plan and door probes, logs; retained from the closed investigation task)\n",
    "artifact paths")
write_text(EPIC, epic, nl)
print("epic handoff notes written", TS)
