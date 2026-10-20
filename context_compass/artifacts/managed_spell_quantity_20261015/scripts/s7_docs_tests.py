"""S7: promote the managed-spell lane's tests into tests_components and tests_architecture, in one pass.

Run from the repository root:
    python context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_tests.py <NOW> [--dry-run]

Every edit is an exact-anchor replacement that must match once. --dry-run checks every anchor, the added line
lengths and the measured extents, prints what would change, and writes nothing. C1 records are measured from
disk with splitlines, as the documents' own recipe counts.
"""
import pathlib
import re
import sys
from typing import List, Tuple

ROOT = pathlib.Path.cwd()
TC = ROOT / "context_compass/system_docs/tests_components.md"
TA = ROOT / "context_compass/system_docs/tests_architecture.md"
ADDED: List[Tuple[str, str]] = []


def measure(path: str) -> int:
    """Return the line count of a repo-relative file."""
    return len((ROOT / path).read_bytes().decode("utf-8", "replace").splitlines())


def replace_once(text: str, old: str, new: str, label: str) -> str:
    """Replace the single occurrence of `old`; stop when it is missing or repeated."""
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"anchor {label!r} matched {count} times")
    ADDED.append((label, new))
    return text.replace(old, new, 1)


def remeasure(text: str, now: str, label: str) -> Tuple[str, List[str]]:
    """Remeasure every C1 record whose end_line no longer matches its file on disk."""
    lines = text.split("\n")
    changes: List[str] = []
    i = 0
    while i < len(lines):
        found = re.match(r"^- path: `([^`]+)`", lines[i])
        if not found:
            i += 1
            continue
        path = found.group(1)
        fields = [lines[i + k].split(":", 1)[0].strip() for k in range(1, 5)]
        assert fields == ["start_line", "end_line", "loc", "verified_at"], (label, path, fields)
        start = int(lines[i + 1].split(": ")[1])
        end = int(lines[i + 2].split(": ")[1])
        disk = measure(path)
        if end != disk:
            assert start == 1, (label, path, start)
            lines[i + 2] = f"  end_line: {disk}"
            lines[i + 3] = f"  loc: {disk}"
            lines[i + 4] = f"  verified_at: {now}"
            changes.append(f"{label}: {path} {end} -> {disk}")
        i += 5
    return "\n".join(lines), changes


def record(path: str, now: str, note: str) -> str:
    """One measured C1 record with a note."""
    n = measure(path)
    return f"- path: `{path}`\n  start_line: 1\n  end_line: {n}\n  loc: {n}\n  verified_at: {now}\n  note: {note}\n"


UNIT_PROTECTS = """\
- managed spells (0.2.8241-0.2.8246): the member and its Phase 6 rank, the bind options with their refusals and
  ids, the pool in each mode, the release registry and the lease, the plans' managed sites and the owner stamp
  through an ownership transfer (see `### Subcomponent: Managed Spell Pools Unit Cluster` and the spellbook
  clusters)
"""

UNIT_CONCURRENCY = """\
  `test_abstract_elastic_pool_multithreaded.py` runs threads against the pool, and the managed pool and the
  release registry each have a multithreaded file of eight barrier-released threads (see
  `### Flow: Managed Pool Stress Under Eight Threads`); a race in larger code is pinned by a stand-in, not by
  threads"""

COMPONENT_PROTECTS = """\
- managed objects leased and given back through real melds, injections and `Conduit.managed_spell_meld`
  (0.2.8245; see `### Subcomponent: Aether Component Cluster`)
"""

INTEGRATION_PROTECTS = """\
- managed pools through real worlds (0.2.8241-0.2.8246): pools in the owning root's store, leases across frames,
  binding names, notches, borrowers and lessers, the release registry, ownership transfers and a restored world
  (see `### Subcomponent: Conduit Integration Cluster`)
"""

MANAGED_CLUSTER = """\
### Subcomponent: Managed Spell Pools Unit Cluster
Parent Component: Unit Test Suite
Purpose:
- cover the managed lifetime's runtime pieces under tests/unit/melder/aether/conduit/ (added 2026-10-15,
  0.2.8243-0.2.8246): the pool of one managed version (`ManagedSpellQuantity`), the Creations pool map, the
  release registry (`ReleaseManagedSpell`) and its lease (`ManagedSpellLease`), the meld doors' store readers
  and the owner stamp an ownership transfer moves
Protects:
- the pool in each mode (`test_managed_spell_quantity.py`): elastic keeps min(20, limit) idle with the kernel
  pools' stretch, settle and decay and never refuses; limited_quantity refuses at its limit before anything is
  built, unless an object came back after the plan's empty pop; a queue waiter is served by a release (the same
  object, no build) or by the place a destroyed or abandoned build frees, raises at its one deadline, and wakes
  with the torn-down error when the root is torn down; a release runs the reset names in order and never
  disposes; a raising reset destroys the object and its recorded children and frees its place; cleanup disposes
  the idle objects, then the children of objects out, then orphans, in one aggregated group, and leaves objects
  out to their holders; the pool keeps no reference to an object out
- the pool under eight threads (`test_managed_spell_quantity_multithreaded.py`): limited_quantity 3 never has
  more than 3 objects alive or out; queue 2 never hangs and never exceeds 2; elastic ends with its count equal to
  its idle objects; six waiters on a full queue all wake with the torn-down error; a queue of 1 never hands one
  object to two leases (see `### Flow: Managed Pool Stress Under Eight Threads`)
- the store (`test_creations_managed_quantities.py`): one pool per version, composed only for a managed spell
  in a live store; an idempotent ensure that re-points a kept pool at a rebound Spell; a pool never in
  `_creations`; purge 0; clears that never touch a pool; pools cleaned before the disposable registry and newest
  first, their failures in the store's group; the `managed` extract/restore row (a replaced pool cleaned, its
  failures raised once the moved pool is in place); the registry calls at ensure, extract, restore and cleanup.
  `test_creations_discard_managed_quantity.py` pins the identity-checked discard: unregistered, never cleaned,
  removed once under concurrent callers
- the registry (`test_release_managed_spell.py`): one process singleton that Aether builds and cleans, a bare
  first construction refused, the reset hook; a release by exact class (a subclass never reaches its base's
  pool), the `spell_id` and `conduit` filters, the selected version preferred (a notch moves the preference)
  and every ambiguity named with its pools; `managed`, `release_all` (every object released, the failures raised
  together) and `describe`. `test_release_managed_spell_multithreaded.py` keeps releases routing while another
  class registers and unregisters, keeps 32 concurrent registrations and removals exact, and lets 64
  registrations racing the registry's cleanup land or raise the cleaned error
- the lease (`test_managed_spell_lease.py`): one release however often it is called; `with` releases on exit
  and when the block raises and never suppresses; a raising reset or a torn-down pool still ends the lease
- the meld doors (`test_meld_doors_managed_spell_quantity.py`): conduit purge answers 0 from the caller's
  store, the SpellSpace purge keeps refusing a managed spell, `meld_existing` refuses it, and both live probes
  report the owner root's pool - an empty or unstamped pool is not live
- the owner stamp through a transfer (`test_transfer_of_ownership_owner_stamps.py`): the flip stamps the
  target's store, gate controller and caching posture; a rollback stamps back and discards and cleans only the
  pools the stamps composed; stamped parked members of every existence are re-stamped and rolled back; a
  raising stamp is still rolled back; a failed move puts the rows back before the stamps; a version staged
  before conjure moves unstamped, as before (stamping such versions is an open owner decision)
- the Conduit bind facade forwarding the four managed options, None when the caller leaves them out
  (`test_conduit_facade.py`)
Key Files (C1):
- `tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py` (the pool, 2026-10-15)
- `tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py` (2026-10-15)
- `tests/unit/melder/aether/conduit/creations/test_creations_managed_quantities.py` (the store, 2026-10-15)
- `tests/unit/melder/aether/conduit/creations/test_creations_discard_managed_quantity.py` (2026-10-15)
- `tests/unit/melder/aether/conduit/creations/test_release_managed_spell.py` (the registry, 2026-10-15)
- `tests/unit/melder/aether/conduit/creations/test_release_managed_spell_multithreaded.py` (2026-10-15)
- `tests/unit/melder/aether/conduit/creations/test_managed_spell_lease.py` (the lease, 2026-10-15)
- `tests/unit/melder/aether/conduit/meld/test_meld_doors_managed_spell_quantity.py` (meld doors, 2026-10-15)
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_owner_stamps.py` (2026-10-15)

"""

STATIC_ROOMS_PROTECTS = """\
- the static rooms treating a managed spell like `many` (0.2.8243): static access names the existence instead
  of probing a store, the status payload says why, and a live pool never makes it a live static spell
"""

CRYSTAL_PROTECTS = """\
- managed options in the record (0.2.8242): a managed crystal records the mode's name, the limit, the timeout
  and the reset names in order; other crystals carry none of the four keys; a payload's options replay as bind
  keywords (none from a 4.1 record or another existence); RecordVersion 4.2.0 still reads 4.1 records
"""

BINDING_PROTECTS = """\
- managed bind options (0.2.8242; `test_bind_managed_spell_options.py`): the mode vocabulary and the elastic
  defaults (limit 256, no timeout, no resets); every refusal - an option on another existence, a function,
  method or existing object, an unknown mode, a bad limit, a timeout outside queue or not finite and positive,
  reset names that are not a list or tuple naming methods of the class; every existing member's spell id
  byte-identical to 0.2.8241 while the part `managed:<mode>:<limit>:<timeout>:<names>` moves a managed
  binding's id; the index minted with that id; the decorator form and `spell_id_inspector` parity. Around it:
  `scan_bind` storing, reserving and replaying the options (`test_scan_bind_managed_options.py`), the Spell's
  read-only properties (`test_spell_managed_spell_options.py`) and `SpellBinder.as_managed_spell_quantity`
  (`test_spellbinder_managed_options.py`)
- the member and its pool stamp (0.2.8241-0.2.8243): `managed_spell_quantity` appended after the six members,
  whose values do not move (`test_existence_managed_spell_quantity.py`); the resolution matrix counting seven
  members, the managed one supported for class spells only (`test_resolution_style_matrix.py`); an owner stamp
  ensuring the version's pool, and no pool for another existence or a stamp without a store
  (`test_spell_managed_quantity_stamp.py`); the selected-version probe, which answers instead of raising under a
  racing cleanup (`test_spell_index_selected_probe.py`); the parity test reading `scan_bind`'s signature in
  the FORWARDREF format (`test_scan_bind_option_parity.py`)
"""

BINDING_KEYS = """\
- `tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py` (managed bind options, 2026-10-15)
- `tests/unit/melder/spellbook/test_scan_bind_managed_options.py` (2026-10-15)
- `tests/unit/melder/spellbook/test_spell_managed_spell_options.py` (2026-10-15)
- `tests/unit/melder/spellbook/test_spellbinder_managed_options.py` (2026-10-15)
- `tests/unit/melder/spellbook/test_existence_managed_spell_quantity.py` (2026-10-15)
- `tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py` (2026-10-15)
- `tests/unit/melder/spellbook/bind/test_spell_index_selected_probe.py` (2026-10-15)
"""

COMPILER_PROTECTS = """\
- the managed site (0.2.8245; `test_site_plan_lowering_managed.py`): an automatic owner's pool bound as a plan
  constant, a per-creation read elsewhere and the missing-pool error; the lease taken right before its
  consumer, one leasing site per consumer and one lease per injection path; the reserve-first miss (a refusal
  at the limit builds nothing, a queue lease is served by a release); every lease given back when a sibling,
  the consumer or its publication fails or a shared consumer loses its cold race, failed returns kept as notes
  or one group; disposal-bearing children recorded with the object and disposed when its build fails; overrides
  that remove the site, build it fresh and unpooled, or apply only on a miss; unresolved inputs refused before
  a place is reserved
- the seams a managed spell passes (0.2.8241-0.2.8245): per-path instance keys and occurrences, the manifest's
  "managed" route key, door rows reusing the `many` templates and `rows_contain_managed_step`
  (`test_managed_dispense_seams.py`); route family "managed" (`test_spell_artifact_processor_core.py`); the
  solo family declining a managed spell and many_only a graph holding one (`test_codegen_plan_discovery_core.py`);
  the singleton specializer keeping the plain door (`test_generalized_specializer_wrapper.py`); Phase 6 ranking
  a managed spell with `unique` - it may hold unique, managed and many, never a narrower lifetime, and any
  holder may hold it (`test_scope_ordering_strategy.py`)
"""

PACKAGE_ROOT_PROTECTS = """\
- the managed surface (0.2.8244): `ManagedSpellMode`, `ReleaseManagedSpell`, `ManagedSpellLease` and
  `ManagedSpellExhaustedError` on the root and in `__all__`, each the concrete-path object, while the pool
  class `ManagedSpellQuantity` stays off the root
"""

UTILITIES_PROTECTS = """\
- `ManagedSpellExhaustedError` (0.2.8243): the limited and queue texts - the limit, the timeout printed without
  trailing zeros, the two ways out - caught as a `MeldExecutionError`, with no inner cause
"""

AETHER_COMPONENT_PROTECTS = """\
- managed spells through real melds (0.2.8245; `test_conduit_component_managed_spell_quantity.py`): a released
  object is the next meld's; every door of the spell leases from one pool; a `many` holder takes a lease per
  meld and a stored `unique` holder keeps its own; limited_quantity refuses until a release, and a queue meld
  is served by one or raises at its timeout; a failed holder gives its lease back; overrides remove the site or
  build a fresh object; an elastic trim disposes the object with its recorded child; the activation hooks run on
  every lease; `managed_spell_meld` releases through its `with` (also when the block raises), once without it,
  and refuses another existence; lessers and spellspaces lease from the root's pool; root teardown disposes
  what is idle and leaves objects out; a dynamic root reads its pool per creation.
  `test_conduit_component_purge.py` pins a managed purge: 0, before any lock, the pool kept
"""

CRYSTALLIZER_INTEGRATION_PROTECTS = """\
- managed options through a record (0.2.8242; `test_managed_spell_options_record_integration.py`): the crystal
  records the active and the parked versions' options; a restore rebinds both with their options and spell
  ids, and a spell-index graft into a Book in another frame carries both members' options
"""

SPELLBOOK_INTEGRATION_PROTECTS = """\
- managed bind options through a real Book (0.2.8242; `test_managed_bind_options_integration.py`): the options
  on the Spell, not in its metadata; one class bound unique, managed by default and managed with a limit gets
  three ids; a refused binding (an option on `unique`, a managed function) registers nothing; a root's `bind`
  and `bind_inactive` forward the options; SpellBinder ends in the same Spell
"""

CONDUIT_INTEGRATION_PROTECTS = """\
- managed pools (0.2.8243-0.2.8246; `test_conduit_integration_managed_quantity_pool.py`): conjure, a dynamic
  conjure and post-conjure binds composing each version's pool in the root's store; root teardown disposing
  what the pool holds and an out object's recorded child, never the object; purge 0 and `cleanup_spell`
  leaving the pool; the live probes reading the root's pool, from a lesser too
- leases through real worlds (`test_conduit_integration_managed_spell_quantity.py`): roots in two frames and
  two binding names in one root leasing from their own pools, a dynamic late bind, a notch leasing from the new
  version's pool while the old one keeps its objects, a borrower and a lesser leasing from the owner root's
  pool, and a restored world leasing from an empty pool
- the release registry (`test_conduit_integration_release_managed_spell.py`): conjure registers and teardown
  unregisters; a notch moves a same-class release; two binding names need `spell_id`, two roots are told apart
  by `conduit` (a lesser names its root) and a cleaned conduit filter is refused; Aether's teardown leaves the
  next boot an empty registry
- ownership transfers (`test_conduit_integration_managed_transfer.py`): a move carries the pool, its idle
  objects and the stamp, releases reach the moved pool and a parked version notched in leases from its moved
  pool; no move gives the target fresh pools and disposes nothing; a failed transfer, with or without a move,
  leaves the pools, the stamps and a `unique` object with the owner; a parked `unique` version moved and
  notched in stores its object in the target
"""

CONDUIT_INTEGRATION_KEYS = """\
- `tests/integration/melder/conduit/test_conduit_integration_managed_quantity_pool.py` (2026-10-15)
- `tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py` (2026-10-15)
- `tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py` (2026-10-15)
- `tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py` (2026-10-15)
"""

STRESS_FLOW = """\
### Flow: Managed Pool Stress Under Eight Threads
1. each test builds one `ManagedSpellQuantity` over a Spell stub (the mode, the limit, the timeout, a `reset`
   and a `close`) and hands a body to `_run_threads`, which starts eight threads behind one `threading.Barrier`
   and joins each with a timeout: a thread still alive fails the test as "a worker hung" instead of hanging the
   run.
2. a body leases the way an emitted plan does - `_lease` pops `_idle` and, on `IndexError`, calls `reserve()`
   and builds unless an idle object was served - and gives the object back with `put_back`; `_OutTracker`
   counts the objects out under its own lock and keeps the peak.
3. the assertions are the pool's invariants under contention: no body raised (limited_quantity's refusals are
   caught and counted), the peak out and `count` stay within the limit, `count == idle_count` once everything
   is back, six waiters woken by `cleanup()` raise the torn-down error, and no object is held by two leases at
   once. The release registry's stress file starts its workers the same way, behind one barrier with a join
   timeout.
   EVIDENCE:
   - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:77-124
   - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:127-238
   - tests/unit/melder/aether/conduit/creations/test_release_managed_spell_multithreaded.py:94-122

"""
UNIT_RECORDS = [
    ("tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py",
     "the managed pool per mode: reserve, waits, put_back and resets, destroy, adopt, abandon, cleanup (0.2.8243)."),
    ("tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py",
     "eight barrier-released threads against the pool's limits, waits and teardown (0.2.8243)."),
    ("tests/unit/melder/aether/conduit/creations/test_creations_managed_quantities.py",
     "the Creations pool map: ensure, cleanup order, the managed row, the registry calls (0.2.8243-0.2.8244)."),
    ("tests/unit/melder/aether/conduit/creations/test_creations_discard_managed_quantity.py",
     "the identity-checked discard of a pool a transfer stamp composed (0.2.8246)."),
    ("tests/unit/melder/aether/conduit/creations/test_release_managed_spell.py",
     "the Aether-owned release registry: singleton, routing, filters, ambiguity, lease, describe (0.2.8244)."),
    ("tests/unit/melder/aether/conduit/creations/test_release_managed_spell_multithreaded.py",
     "releases and registrations against the registry's copy-on-write maps under eight threads (0.2.8244)."),
    ("tests/unit/melder/aether/conduit/creations/test_managed_spell_lease.py",
     "the lease: one release, `with` releasing on exit and on raise, never suppressing (0.2.8244)."),
    ("tests/unit/melder/aether/conduit/meld/test_meld_doors_managed_spell_quantity.py",
     "the meld doors' purge, existing-object and live-probe answers for a managed spell (0.2.8243)."),
    ("tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_owner_stamps.py",
     "the owner stamp through a transfer's flip, migration and rollback (0.2.8246)."),
    ("tests/unit/melder/aether/test_static_rooms_managed_spell_quantity.py",
     "static rooms treat a managed spell like `many` (0.2.8243)."),
    ("tests/unit/melder/crystallizer/test_spell_crystal_managed_options.py",
     "the crystal's managed options and RecordVersion 4.2.0 (0.2.8242)."),
    ("tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py",
     "the four managed bind options at the Bind seam: defaults, refusals, the managed id part (0.2.8242)."),
    ("tests/unit/melder/spellbook/bind/test_spell_index_selected_probe.py",
     "SpellIndex's cleanup-safe selected-version probe (0.2.8244)."),
    ("tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py",
     "the plans' managed site: lease, miss, returns, recorded children, overrides (0.2.8245)."),
    ("tests/unit/melder/spellbook/spell_compiler/test_managed_dispense_seams.py",
     "the phase 9-11 seams a managed spell passes (0.2.8245)."),
    ("tests/unit/melder/spellbook/test_existence_managed_spell_quantity.py",
     "the seventh Existence member (0.2.8241)."),
    ("tests/unit/melder/spellbook/test_scan_bind_managed_options.py",
     "scan_bind declaring and replaying the managed options (0.2.8242)."),
    ("tests/unit/melder/spellbook/test_spell_managed_quantity_stamp.py",
     "an owner stamp ensuring the managed version's pool (0.2.8243)."),
    ("tests/unit/melder/spellbook/test_spell_managed_spell_options.py",
     "the Spell's read-only managed options (0.2.8242)."),
    ("tests/unit/melder/spellbook/test_spellbinder_managed_options.py",
     "SpellBinder staging a managed binding (0.2.8242)."),
    ("tests/unit/melder/utilities/custom_exceptions/test_managed_spell_exhausted_error.py",
     "the exhaustion error's texts and type (0.2.8243)."),
]

COMPONENT_RECORDS = [
    ("tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py",
     "leases through real melds, injections and `managed_spell_meld` (0.2.8245)."),
]

INTEGRATION_RECORDS = [
    ("tests/integration/melder/conduit/test_conduit_integration_managed_quantity_pool.py",
     "pools in the owning root's store through conjure, binds, teardown and the probes (0.2.8243)."),
    ("tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py",
     "leases through real worlds: frames, binding names, notches, borrowers, lessers, a restore (0.2.8245)."),
    ("tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py",
     "the registry routing releases to the pools of live roots (0.2.8244)."),
    ("tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py",
     "pools and owner stamps through moves, no-moves and failed transfers (0.2.8246)."),
    ("tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py",
     "managed options through record, restore and graft (0.2.8242)."),
    ("tests/integration/melder/spellbook/test_managed_bind_options_integration.py",
     "managed bind options through a real Spellbook and its root (0.2.8242)."),
]

CHANGED_SOURCES = [
    "tests/component/melder/aether/conduit/test_conduit_component_purge.py",
    "tests/unit/melder/aether/conduit/test_conduit_facade.py",
    "tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py",
    "tests/unit/melder/spellbook/spell_compiler/test_generalized_specializer_wrapper.py",
    "tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_core.py",
    "tests/unit/melder/spellbook/spell_crafter/system/validation/test_scope_ordering_strategy.py",
    "tests/unit/melder/spellbook/test_resolution_style_matrix.py",
    "tests/unit/melder/test_package_public_surface.py",
]

TC_HANDOFF = """\
2026-10-15 managed spells (0.2.8241-0.2.8246): the lane's 28 test files join the catalog - a new Managed Spell
Pools Unit Cluster (the pool and its stress file, the Creations pool map and discard, the release registry and
its stress file, the lease, the meld doors and the transfer stamps), dated Protects lines in ten existing
clusters (key files in nine), a line in each suite and a stress flow; the nine test files the lane changed are
named where their contracts sit. The core set is 247 paths, equal to the code map. Every code-map extent was
checked against disk: the 28 new records were measured and the 20 stale ones remeasured - 19 were already stale
at the 0.2.8240 commit, one (`test_scan_bind_option_parity.py`) is this lane's - and every other record matched.
Tier and subtree counts are recounted from disk: 833 test modules in the three tiers; four subtree counts had
not followed earlier lanes (unit aether and spellbook, component spellbook, integration conduit).

"""

TA_INVENTORY_OLD = """\
Current Python test inventory from direct filesystem count:
- `unit/`: 465 `.py` files (334 on 2026-06-13)
- `component/`: 143 `.py` files (81)
- `integration/`: 149 `.py` files (88)
- `mocks/`: 44 `.py` files (42)
- `experimentation/`: 196 `.py` files, 33 of them `test_*.py` (not counted before)
Recounted 2026-09-26 with `find tests/<tier> -name '*.py'` (pycache excluded)."""

TA_INVENTORY_NEW = """\
Current Python test inventory from direct filesystem count:
- `unit/`: 505 `.py` files, 502 of them `test_*.py` (465 on 2026-09-26, 334 on 2026-06-13)
- `component/`: 167 `.py` files, 165 of them `test_*.py` (143, 81)
- `integration/`: 173 `.py` files, 166 of them `test_*.py` (149, 88)
- `mocks/`: 44 `.py` files (44, 42)
- `experimentation/`: 204 `.py` files, 33 of them `test_*.py` (196 on 2026-09-26)
Recounted 2026-10-15 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 833 `test_*.py`
modules are the count `tests_components` states."""

TA_CORE_OLD = """\
Core is the deduplicated union of every `Key Files (C1)` list in
`tests_components.md`, plus the harness surfaces this document names as
entrypoints. Every range below was MEASURED from disk on 2026-08-02, not carried"""

TA_CORE_NEW = """\
Core here is the harness and entrypoint surfaces this document names - the runner configuration, the
conftests, the shared support modules, the benches, the mock corpus and the CI driver: 36 paths, every one of
them in the core set of `tests_components` (the deduplicated union of its `Key Files (C1)` lists, 247 paths on
2026-10-15; corrected 2026-10-15 - this paragraph called this map that union). Every range below was MEASURED
from disk on 2026-08-02, not carried"""

TA_WORKER_HANG = """\
- WORKER HANG (unit-tier stress files): the managed pool's and the release registry's stress files start eight
  threads behind one barrier and join each with a timeout, so a deadlock or a lost wake-up fails the test (the
  pool's file names it "a worker hung") instead of stalling the CI cell; the queue pools there also give every
  waiting lease a deadline of its own.
  EVIDENCE: tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:94-124
"""

TA_HANDOFF = """\
2026-10-15 managed spells (no notch here; the lane landed 0.2.8241-0.2.8246): the inventory is recounted from
disk (unit 505 `.py`, component 167, integration 173, mocks 44, experimentation 204; 833 test modules in the
three tiers); the two stale code-map extents, both stale since earlier lanes (`test_nexus.py` 6374,
`test_command_system_direct.py` 477), are remeasured and every other extent matched disk; and the code-map header
no longer calls this map the union of `tests_components`' key files - it is the 36 surfaces this document names.
Failure Modes gains the worker-hang guard of the unit tier's two managed stress files. The lane adds no tier,
conftest, marker or shared support module; its 28 test files are catalogued in `tests_components`.

"""


def edit_tests_components(text: str, now: str) -> Tuple[str, List[str]]:
    """Apply the tests_components edits, append the measured records, then remeasure stale ones."""
    r = replace_once
    text = r(text, "- Updated: 2026-10-14\n\n## Scope", "- Updated: 2026-10-15\n\n## Scope", "tc updated")
    anchor = "  `### Flow: Concurrent-Writer Stand-In`)\n\nInputs:\n- local runtime classes and helper fixtures"
    text = r(text, anchor, anchor.replace(")\n\nInputs:", ")\n" + UNIT_PROTECTS + "\nInputs:"), "unit protects")
    text = r(text, "  `test_abstract_elastic_pool_multithreaded.py` runs threads against the pool; a\n"
                   "  race in larger code is pinned by a stand-in, not by threads", UNIT_CONCURRENCY, "unit threads")
    text = r(text, "480 `test_*.py` modules among 483 `.py` files (recounted 2026-10-14)",
             "502 `test_*.py` modules among 505 `.py` files (recounted 2026-10-15)", "unit count")
    text = r(text, "- The aether tree carries 189 `test_*.py` modules", "- The aether tree carries 202 `test_*.py` modules",
             "unit aether")
    text = r(text, "the 47 test_*.py modules in\n  tests/unit/melder/crystallizer/",
             "the 48 test_*.py modules in\n  tests/unit/melder/crystallizer/", "unit crystallizer")
    text = r(text, "- The spellbook tree carries 146 `test_*.py` modules",
             "- The spellbook tree carries 157 `test_*.py` modules", "unit spellbook")
    text = r(text, "the 52 test_*.py modules in\n  tests/unit/melder/utilities/",
             "the 53 test_*.py modules in\n  tests/unit/melder/utilities/", "unit utilities")
    anchor = "  fixtures (`test_agent_text_reader_component.py`)\n\nInputs:"
    text = r(text, anchor, anchor.replace(")\n\nInputs:", ")\n" + COMPONENT_PROTECTS + "\nInputs:"), "comp protects")
    text = r(text, "- 164 `test_*.py` modules among 166 `.py` files (recounted 2026-10-14)",
             "- 165 `test_*.py` modules among 167 `.py` files (recounted 2026-10-15)", "comp count")
    text = r(text, "the 75 test_*.py modules in\n  tests/component/melder/aether/",
             "the 76 test_*.py modules in\n  tests/component/melder/aether/", "comp aether")
    text = r(text, "- The spellbook tree carries 74 `test_*.py` modules",
             "- The spellbook tree carries 77 `test_*.py` modules", "comp spellbook")
    anchor = "  (see `### Subcomponent: Live Sim Integration Cluster`)\n\nInputs:"
    text = r(text, anchor, anchor.replace(")\n\nInputs:", ")\n" + INTEGRATION_PROTECTS + "\nInputs:"), "int protects")
    text = r(text, "- 158 `test_*.py` modules among 165 `.py` files (recounted 2026-10-14);",
             "- 166 `test_*.py` modules among 173 `.py` files (recounted 2026-10-15);", "int count")
    for name, old_n, new_n in (("conduit", 37, 43), ("crystallizer", 17, 18), ("spellbook", 49, 50)):
        text = r(text, f"the {old_n} test_*.py modules in\n  tests/integration/melder/{name}/",
                 f"the {new_n} test_*.py modules in\n  tests/integration/melder/{name}/", f"int {name}")
    text = edit_clusters(text)
    text = r(text, "test_compiler_pool_snapshot_reads.py:148-235\n\n## C1 Code Map (Core)",
             "test_compiler_pool_snapshot_reads.py:148-235\n\n" + STRESS_FLOW + "## C1 Code Map (Core)", "flow")
    text = r(text, "above - 217 paths (recounted 2026-10-14) - and nothing else.",
             "above - 247 paths (recounted 2026-10-15) - and nothing else.", "core set")
    text = r(text, "The 802 test modules of the", "The 833 test modules of the", "tier modules")
    records = "".join(record(p, now, n) for p, n in UNIT_RECORDS + COMPONENT_RECORDS + INTEGRATION_RECORDS)
    text = r(text, "\n## Diagrams\n### ASCII Component Diagram (C3/C2)",
             "\n" + records + "\n## Diagrams\n### ASCII Component Diagram (C3/C2)", "records")
    new_paths = [p for p, _ in UNIT_RECORDS + COMPONENT_RECORDS + INTEGRATION_RECORDS]
    sources = ("- module docstrings, test names and test docstrings of the 28 managed-spell files below, the bodies of\n"
               "  the two multithreaded ones, and the CR-insensitive diffs of the eight changed files after them\n"
               "  (read 2026-10-15)\n"
               + "".join(f"- `{p}`\n" for p in new_paths + CHANGED_SOURCES))
    anchor = "- `tests/unit/melder/aether/test_configuration_read_accessors.py`\n- direct filesystem inventory of `tests/`"
    text = r(text, anchor, anchor.replace("\n- direct", "\n" + sources + "- direct"), "sources")
    anchor = ("## Context / Handoff Summary\n\n2026-10-14 slotted lifetimes (0.2.8236-0.2.8240): the Conduit "
              "Integration Cluster gains")
    text = r(text, anchor, anchor.replace("Summary\n\n", "Summary\n\n" + TC_HANDOFF), "handoff")
    return remeasure(text, now, "tests_components")


def protects(text: str, last_line: str, block: str, label: str) -> str:
    """Insert `block` after the cluster's last Protects line, right before its Key Files."""
    anchor = last_line + "\nKey Files (C1):"
    return replace_once(text, anchor, last_line + "\n" + block + "Key Files (C1):", label)


def keys_after(text: str, last_key_and_next: str, new_keys: str, label: str) -> str:
    """Append `new_keys` to a cluster's Key Files, before the blank line and the next heading."""
    head, tail = last_key_and_next.split("\n\n", 1)
    return replace_once(text, last_key_and_next, head + "\n" + new_keys + "\n" + tail, label)


def edit_clusters(text: str) -> str:
    """Add the Managed Spell Pools Unit Cluster and the dated lines of ten existing clusters."""
    text = protects(text, "  (its builders refuse once it reads True), reads that change nothing, and the cleaned refusal",
                    STATIC_ROOMS_PROTECTS, "aether unit protects")
    text = keys_after(text, "- `tests/unit/melder/aether/test_command_system_direct.py`\n\n"
                            "### Subcomponent: Aetheric Mediator Lifecycle Unit Cluster",
                      "- `tests/unit/melder/aether/test_static_rooms_managed_spell_quantity.py` (static rooms, 2026-10-15)\n",
                      "aether unit keys")
    anchor = "### Subcomponent: Crystallizer Unit Cluster\nParent Component: Unit Test Suite"
    text = replace_once(text, anchor, MANAGED_CLUSTER + anchor, "managed cluster")
    text = protects(text, "  importable; `with_defaults()` takes the working directory as the user root, with descent off",
                    CRYSTAL_PROTECTS, "crystallizer unit protects")
    text = keys_after(text, "- `tests/unit/melder/crystallizer/crystal_analysis/test_custody_boundary_characterization.py`"
                            " (2026-10-10)\n\n### Subcomponent: MutationResearch Unit Cluster",
                      "- `tests/unit/melder/crystallizer/test_spell_crystal_managed_options.py` (record 4.2.0, 2026-10-15)\n",
                      "crystallizer unit keys")
    text = protects(text, "  every manifest entry rooted at `melder`", BINDING_PROTECTS, "binding protects")
    text = keys_after(text, "- `tests/unit/melder/spellbook/test_spellbook_creation_system_dependency_flags.py` (target-pass"
                            " flags, 2026-09-30)\n\n### Subcomponent: Spellbook Compiler Unit Cluster",
                      BINDING_KEYS, "binding keys")
    text = protects(text, "  results through fresh and pass-cached validation (`test_duplicate_spell_name_strategy.py`).",
                    COMPILER_PROTECTS, "compiler protects")
    text = keys_after(text, "- `tests/unit/melder/spellbook/spell_crafter/validation/strategies/"
                            "test_duplicate_spell_name_strategy.py`\n\n### Subcomponent: Package Root Unit Cluster",
                      "- `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering_managed.py`"
                      " (2026-10-15)\n"
                      "- `tests/unit/melder/spellbook/spell_compiler/test_managed_dispense_seams.py` (2026-10-15)\n",
                      "compiler keys")
    text = protects(text, "  impact and cite stay index-shaped", PACKAGE_ROOT_PROTECTS, "package root protects")
    text = protects(text, "  concurrent burst stay within bounds", UTILITIES_PROTECTS, "utilities protects")
    text = keys_after(text, "- `tests/unit/melder/utilities/general_base/test_cleanable_cleanup_contexts.py`\n\n"
                            "### Subcomponent: Repository Tooling Unit Cluster",
                      "- `tests/unit/melder/utilities/custom_exceptions/test_managed_spell_exhausted_error.py` (2026-10-15)\n",
                      "utilities keys")
    text = protects(text, "  for holders built where they live; the opt-in singleton specializer builds one child, not one"
                          " per warm meld", AETHER_COMPONENT_PROTECTS, "aether component protects")
    text = keys_after(text, "- `tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder"
                            ".py` (2026-10-14)\n\n### Subcomponent: Crystallizer Component Cluster",
                      "- `tests/component/melder/aether/conduit/test_conduit_component_managed_spell_quantity.py`"
                      " (2026-10-15)\n", "aether component keys")
    text = protects(text, "  reads back with no drift verdict while the fingerprinted project module reports drift",
                    CRYSTALLIZER_INTEGRATION_PROTECTS, "crystallizer integration protects")
    text = keys_after(text, "- `tests/integration/melder/crystallizer/test_recorded_leaf_source_read_integration.py` (leaf"
                            " source reads, 2026-10-10)\n\n### Subcomponent: MutationResearch Integration Cluster",
                      "- `tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py`"
                      " (2026-10-15)\n", "crystallizer integration keys")
    text = protects(text, "  Contracted validation tests verify independent owner/borrower bindings and validity after"
                          " unlink.", SPELLBOOK_INTEGRATION_PROTECTS, "spellbook integration protects")
    text = keys_after(text, "- `tests/integration/melder/spellbook/test_spellbook_integration_validation_system.py`\n\n"
                            "### Subcomponent: Conduit Integration Cluster",
                      "- `tests/integration/melder/spellbook/test_managed_bind_options_integration.py` (2026-10-15)\n",
                      "spellbook integration keys")
    text = protects(text, "  `move_creations=False` builds a new instance on the target", CONDUIT_INTEGRATION_PROTECTS,
                    "conduit integration protects")
    text = keys_after(text, "- `tests/integration/melder/conduit/test_conduit_integration_holder_children_lifetime.py`"
                            " (2026-10-14)\n\n### Subcomponent: Multithreading Integration Cluster",
                      CONDUIT_INTEGRATION_KEYS, "conduit integration keys")
    return text


def edit_tests_architecture(text: str, now: str) -> Tuple[str, List[str]]:
    """Apply the tests_architecture edits, then remeasure its stale records."""
    r = replace_once
    text = r(text, "- Updated: 2026-10-06", "- Updated: 2026-10-15", "ta updated")
    text = r(text, TA_INVENTORY_OLD, TA_INVENTORY_NEW, "ta inventory")
    text = r(text, TA_CORE_OLD, TA_CORE_NEW, "ta core")
    text = r(text, "  recipe under `## Indexing`.\n\n## C1 Code Map (Core Only)",
             "  recipe under `## Indexing`.\n" + TA_WORKER_HANG + "\n## C1 Code Map (Core Only)", "ta worker hang")
    anchor = "- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py`\n- `.gitignore`"
    added = ("\n- `tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py`"
             "\n- `tests/unit/melder/aether/conduit/creations/test_release_managed_spell_multithreaded.py`"
             "\n- `.gitignore`")
    text = r(text, anchor, anchor.replace("\n- `.gitignore`", added), "ta sources")
    anchor = "## Context / Handoff Summary\n\n2026-10-06 speed tests beside CI"
    text = r(text, anchor, anchor.replace("Summary\n\n", "Summary\n\n" + TA_HANDOFF), "ta handoff")
    return remeasure(text, now, "tests_architecture")


def long_added_lines() -> List[str]:
    """Return added lines over 120 characters that are not a single unbreakable path."""
    found: List[str] = []
    for label, block in ADDED:
        for line in block.split("\n"):
            if len(line) <= 120:
                continue
            if re.fullmatch(r"\s*-( path:)? `[^`]+`( \([^)]*\))?", line):
                continue
            found.append(f"{label} ({len(line)}): {line}")
    return found


def main() -> None:
    """Edit both documents, or with --dry-run report what would change."""
    now = sys.argv[1]
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", now), now
    dry = "--dry-run" in sys.argv[2:]
    tc = TC.read_bytes().decode("utf-8")
    ta = TA.read_bytes().decode("utf-8")
    assert "\r" not in tc and "\r" not in ta
    tc_new, tc_changes = edit_tests_components(tc, now)
    ta_new, ta_changes = edit_tests_architecture(ta, now)
    for change in tc_changes + ta_changes:
        print("REMEASURED", change)
    print("tests_components lines", tc.count("\n"), "->", tc_new.count("\n"))
    print("tests_architecture lines", ta.count("\n"), "->", ta_new.count("\n"))
    long_lines = long_added_lines()
    for line in long_lines:
        print("LONG", line)
    if long_lines:
        raise SystemExit(f"{len(long_lines)} added lines over 120 characters")
    if dry:
        print("dry run: nothing written")
        return
    TC.write_bytes(tc_new.encode("utf-8"))
    TA.write_bytes(ta_new.encode("utf-8"))
    print("written")


if __name__ == "__main__":
    main()
