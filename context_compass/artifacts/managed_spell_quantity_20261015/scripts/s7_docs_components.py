"""S7: promote the managed_spell_quantity lane into src_components.md - a new C3 component for the pools, the
registry and the lease; dated entries in Public API, Spellbook Core, Binding Pipeline, Aether, Crystallizer, Conduit,
Creations, Meld and SpellCompiler; the Ownership Transfer subcomponent; the transfer flow and a new lease flow; the
code map, the inventory and the sources; a diagram; the handoff. Exact anchors; written once at the end.

Run from the repository root: python s7_docs_components.py <NOW>
"""
import ast
import pathlib
import re
import sys

now = sys.argv[1]
DOC = pathlib.Path("context_compass/system_docs/src_components.md")
text = DOC.read_text(encoding="utf-8")
before = set(text.splitlines())


def replace_once(old: str, new: str) -> None:
    global text
    assert text.count(old) == 1, (text.count(old), old[:100])
    text = text.replace(old, new)


def insert_after(anchor: str, block: str) -> None:
    replace_once(anchor, anchor + block)


def all_span() -> str:
    lines = pathlib.Path("src/melder/__init__.py").read_text(encoding="utf-8").split("\n")
    start = next(i + 1 for i, l in enumerate(lines) if l.startswith("__all__ = ["))
    end = next(i + 1 for i in range(start, len(lines)) for l in [lines[i]] if l.startswith("]"))
    return f"{start}-{end}"


# ---- the new C3 component --------------------------------------------------------------------------------------
NEW_COMPONENT = """### Component: Managed Spell Pools (ManagedSpellQuantity, ReleaseManagedSpell, ManagedSpellLease)
Purpose:
- Lease and take back the objects of `Existence.managed_spell_quantity` spells (0.2.8241-0.2.8246): one pool per
  managed spell version in its owning root's Creations, a process-wide registry that routes a released object back
  to its pool, and a lease that gives one object back once.

Responsibilities:
- `ManagedSpellQuantity` (an `AbstractElasticPool`): keep one version's idle objects (`_idle`, newest last), count
  the objects built and alive, reserve a place for a build (elastic: always; limited_quantity: below the limit, else
  an object released since the plan's empty pop, else `ManagedSpellExhaustedError`; queue: the same, waiting up to
  the timeout before it refuses), put an object back (the reset names in order, outside every lock, then the
  append; queue wakes one waiter; above the baseline the elastic band trims the oldest), give a failed build's
  place back (`abandon`), record the disposal-bearing `many` children built for an object (`adopt`), destroy an
  object (its disposal methods, then its recorded children newest first) and clean up (idle objects and every
  recorded child, failures in one ExceptionGroup). `create_object` and `acquire` refuse: the emitted plan builds,
  never the pool.
- `ReleaseManagedSpell`: the Aether-hosted singleton registry. `release(obj)` routes by `type(obj)` (one dict get)
  to the one matching pool, or resolves by `spell_id`, by `conduit`'s root and by the version its index selects;
  `managed(obj)` returns a lease, `release_all(objects)` releases each and raises one group, `describe(cls)` reports
  every pool of a class.
- `ManagedSpellLease`: hold one object and its pool; `release()` gives it back once; `with` releases on exit, even
  when the block raised, and never suppresses.
- `ManagedSpellExhaustedError`: the refusal of limited_quantity (at its limit) and queue (at its timeout).

Inputs:
- The Spell's normalized options (mode, limit, timeout, reset names), its disposal names and its identity, read when
  `Creations.ensure_managed_quantity` composes the pool at owner stamping.
- Objects built by the emitted plans (a site's miss) and objects handed back by their holders.

Outputs:
- Leased objects (the plan's inline pop, or the miss's build) and refusals. `ManagedSpellQuantity.describe()`: the
  retention keys, identity (spell id and name, binding, frame, composing root), policy (mode, limit, timeout, reset
  and disposal names), `count`, `out_count` and `children_recorded`; `ReleaseManagedSpell().describe(cls)`: one such
  snapshot per pool of the class, plus `holding_conduit_id` and `active_version`.

Owned State:
- Pool: `_idle` (assigned once, drained, never swapped, so a plan may bind its `pop`), `_count`, `_condition` over
  the base `_lock`, `_children_by_object` (`id(obj)` -> children), `_orphaned_children`, descriptive tombstones
  (spell id and name, binding, frame, owner conduit id, mode, limit, timeout, reset and disposal names,
  `managed_class`), a borrowed Spell behind `spell`.
- Registry: `_pools_by_class` and `_registrations`, republished whole (copy-on-write) under a leaf `_lock`; the
  class-level `_instance`, `_singleton_lock` and `_initialized`.
- Lease: the object and its pool (borrowed) and `_released`.

Lifecycle/Cleanup:
- A pool is composed at owner stamping (conjure, a post-conjure bind or bind_inactive, an ownership transfer's
  stamps) and lives in the root store's `_managed_quantities` until the store gives it up: an extract (a transfer's
  move or no-move) unregisters it, a restore installs it in another store, `discard_managed_quantity` removes one a
  failed transfer's stamp composed, and the store's cleanup cleans it before the disposable registry.
- The registry is built last by `Aether.__init__` and cleaned by `Aether.cleanup` right after the frames; its
  cleanup publishes empty maps as tombstones and resets the singleton bookkeeping; `_reset_singleton_for_tests()`
  clears it for a fresh world.
- Objects that are out are their holders': no reference to them is kept, so root teardown disposes only idle
  objects and recorded children. Nothing returns an object automatically, except the emitted plan returning the
  leases it took for a holder that is never built.

Concurrency/Threading:
- The warm lease (`deque.pop`) and a resetless release below the baseline take no lock; `deque.pop` and `append` are
  atomic per object on free-threaded 3.14.
- The pool lock is a leaf held for `count`, the children maps and condition waits only; resets, constructors and
  disposal never run under it. A queue wait is bounded by the required timeout.
- The registry lock is a leaf held only to publish; every read is lock-free. Creations registers and unregisters
  outside its store lock: owner stamping holds the Spell lock, takes the store's leaf lock for the map, releases it,
  then takes the registry's leaf lock to publish. No edge joins frame -> conduit -> Book.

Invariants/Guarantees:
- One pool per (root store, managed spell version). `count` (objects built and alive) rises only in `reserve()`,
  after the mode's check, so it never exceeds the limit of a limited_quantity or queue pool; a released object the
  pool never built (a fresh override object) is pooled uncounted, because releases are trusted, never checked.
- The registry holds exactly the pools live root stores hold.
- A leasing site feeds exactly one consumer, so each lease goes to one holder or to the melding caller; the plan
  gives a lease back only when its consumer's construction fails or loses its cold race.
- A transfer disposes nothing: a pool moves as the store's `managed` row and the owner stamp follows it (0.2.8246).

Failure Modes:
- `ManagedSpellExhaustedError` (limited_quantity at its limit; queue at its timeout) before anything is built.
- RuntimeError "The pool of managed spell '<name>' was torn down with its root conduit; ..." from a release, a
  reserve or an adopt after teardown (a woken queue waiter included).
- ValueError from a release: not managed, ambiguous, no match; TypeError for filters of the wrong type.
- A raising reset destroys the object, frees its place and propagates (an ExceptionGroup when its disposal failed
  too).
- `ReleaseManagedSpell()` before an Aether built it: ValueError naming the boot order.

Observability:
- `ReleaseManagedSpell().describe(cls)` and `ManagedSpellQuantity.describe()`; the live-creation probes answer a
  managed spell from its pool (`storage_scope_kind` "managed_pool", the count).

Extension Points:
- Bind options only: the mode, the limit, the queue timeout and the reset names (`managed_spell_reset_methods`),
  plus the Spell's disposal names, which run when the pool destroys an object.

Key Files (C1):
- `src/melder/aether/conduit/creations/managed_spell_quantity.py`
- `src/melder/aether/conduit/creations/release_managed_spell.py`
- `src/melder/aether/conduit/creations/managed_spell_lease.py`
- `src/melder/aether/spellbook/existence/managed_spell_mode.py`
- `src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py`
- `src/melder/aether/conduit/creations/creations.py`

"""
replace_once("### Component: Meld Resolution Runtime\n", NEW_COMPONENT + "### Component: Meld Resolution Runtime\n" + """\
Managed doors, probes and purge (2026-10-15, 0.2.8243-0.2.8245): route "managed" maps onto the existing `many` door
templates in the four route tables (both fast bits), so the no-overrides door calls the normal plan, the override door
`_execute_with_overrides`, and the hooks doors report `created=True` on every lease, running the activation hooks for a
reused object too; no template is added or recompiled. Both live-creation probes answer a managed spell from its owner
store's pool (`Meld._describe_managed_pool_status`: `is_live` when `count > 0`, `creation_count` the count,
`storage_scope_kind` "managed_pool", `storage_owner_conduit_id` the owner root; no store or no pool -> 0).
`ConduitMeld._get_purge_creations` selects the caller's own store for a managed spell, where purge returns 0;
`SpellSpaceMeld.purge` refuses it ("purge it from its authorized conduit"). The Nexus static rooms treat a managed
spell like `many` (no stored object to hand out). See Component: Managed Spell Pools.
EVIDENCE: `src/melder/aether/conduit/meld/meld.py:Meld._describe_managed_pool_status`,
`src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld._get_purge_creations`,
`src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld.purge` and
`src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py`.

""")

# ---- dated entries -------------------------------------------------------------------------------------------
insert_after(
    "Purpose:\n- Provide the package entrypoint and import-time guardrails.\n\n",
    "Managed-spell root exports (2026-10-15, 0.2.8244): `ManagedSpellMode`, `ReleaseManagedSpell`, `ManagedSpellLease`\n"
    "and `ManagedSpellExhaustedError` join `__all__` beside `Existence` (the owner's 2026-07-19 root ruling: user-held\n"
    "surfaces, front-facing enums and user-catchable errors reach the flat facade); `ManagedSpellQuantity` stays off the\n"
    "root.\n"
    f"EVIDENCE: `src/melder/__init__.py:{all_span()}`.\n\n",
)
insert_after(
    "### Component: Spellbook Core (Binding and Conjure)\n",
    "Managed bind options (2026-10-15, 0.2.8242-0.2.8243): `bind` and `bind_inactive` take the keyword-only\n"
    "`managed_spell_mode`, `managed_spell_limit`, `managed_spell_timeout_seconds` and `managed_spell_reset_methods` (all\n"
    "None by default) and pass them to Bind, which normalizes, refuses and fingerprints them (Component: Binding\n"
    "Pipeline); the Conduit facades forward them. Owner stamping - `define_conduit_into_spells` at conjure, the\n"
    "post-conjure bind paths, an ownership transfer's stamps - composes a managed version's pool in the root store\n"
    "through `Spell._add_owned_conduit`.\n"
    "EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.bind`, `Spellbook.bind_inactive` and\n"
    "`src/melder/aether/spellbook/spell.py:Spell._add_owned_conduit`.\n\n",
)
insert_after(
    "Purpose:\n- Convert user objects into registered spell metadata with stable index identities.\n\n",
    """Managed options (2026-10-15, 0.2.8242): `Bind._normalize_managed_options` runs once, after the disposal names and
before the fingerprint. Another existence takes no `managed_spell_*` option (ValueError); a managed binding is a class
(TypeError otherwise); mode None means elastic, else a `ManagedSpellMode` member or its name; the limit is an int >= 1
(elastic defaults to 256, limited_quantity and queue require one, a bool is refused); a timeout only for queue, required
there, finite and > 0; reset names are a list or tuple of non-empty strings naming callable attributes of the class,
kept in order. `sha256_profile` appends `managed:<mode>:<limit>:<timeout>:<names>` only for managed bindings, so every
other spell id is byte-identical; `spell_id_inspector` matches bind. The Spell keeps the normalized values behind
read-only properties (`managed_spell_mode`, `managed_spell_limit`, `managed_spell_timeout_seconds`,
`managed_spell_reset_methods`; None, None, None and () otherwise), deleted at cleanup. `scan_bind` takes the four as
target options (28 reserved metadata keys) and `SpellBinder.as_managed_spell_quantity` is the fluent form.
`SpellIndex._is_selected_unless_cleaned(spell_id)` answers the release registry's selected-version question without
raising on a cleaned index (0.2.8244).
EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._normalize_managed_options`, `Bind.sha256_profile`,
`src/melder/aether/spellbook/spell.py:Spell.managed_spell_mode`, `src/melder/aether/spellbook/bind/scan.py:scan_bind`,
`src/melder/aether/spellbook/spellbinder.py:SpellBinder.as_managed_spell_quantity` and
`src/melder/aether/spellbook/bind/spell_index.py:SpellIndex._is_selected_unless_cleaned`.

""",
)
insert_after(
    "Purpose:\n- Global singleton for all frames and shared registries.\n\n",
    "ReleaseManagedSpell, the seventh hosted root (2026-10-15, 0.2.8244): `Aether.__init__` builds\n"
    "`ReleaseManagedSpell(aether=self)` last, after Nexus, and `Aether.cleanup` cleans it right after the frames - whose\n"
    "root stores unregistered their pools while they were torn down - and before the other hosted roots.\n"
    "`ReleaseManagedSpell()` returns the hosted instance; releasing never goes through Aether (owner ruling 2026-10-13).\n"
    "See Component: Managed Spell Pools.\n"
    "EVIDENCE: `src/melder/aether/aether.py:Aether.__init__` and `Aether.cleanup`.\n\n",
)
insert_after(
    "  world surfaces used for crystallized spell loading and activation.\n\n",
    "Managed options in the record (2026-10-15, 0.2.8242): `SpellCrystal` captures the four managed options only for\n"
    "`managed_spell_quantity` spells (mode by name, limit, timeout, reset names as a list) and `describe()` adds the four\n"
    "keys only then; `SpellCrystal.managed_bind_options(payload)` gives the bind keywords a payload carries ({} without\n"
    "them), which `RestoreEngine._bind_one_active` / `_bind_one_staged` and `GraftRunner._bind_selected` /\n"
    "`_park_members` / `_merge_members` pass to bind. RecordVersion 4.1.0 -> 4.2.0 (minor: added keys). Pools are\n"
    "runtime state: a restore rebuilds them empty at conjure.\n"
    "EVIDENCE: `src/melder/crystallizer/crystals/spell_crystal.py:SpellCrystal.managed_bind_options`,\n"
    "`src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._bind_one_active` and\n"
    "`src/melder/crystallizer/persistence/record_version.py:RecordVersion`.\n\n",
)
insert_after(
    "Purpose:\n- Execution scope for resolving spells and managing object lifecycles.\n\n",
    "Managed leases (2026-10-15, 0.2.8242-0.2.8245): `Conduit.managed_spell_meld(spell=None, *, spell_id=None,\n"
    "spellframe=None, binding_name=None, override=None)` resolves its target as `meld` does, refuses `spell` with\n"
    "`spell_id` and a spell of another existence (ValueError, nothing melded), reads the version's pool from its owner\n"
    "store (none: the missing-pool MeldExecutionError), melds the version by id and returns `ManagedSpellLease(obj,\n"
    "pool)`. With own-parameter overrides the object is fresh and its release still adds it to the pool. `bind` and\n"
    "`bind_inactive` forward the four managed options to the Book.\n"
    "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.managed_spell_meld`.\n\n",
)
insert_after(
    "Purpose:\n- Instance lifecycle registry for Conduits and scoped spellspaces.\n\n",
    """Managed pools (2026-10-15, 0.2.8243-0.2.8246): a root store keeps `_managed_quantities` (spell id ->
`ManagedSpellQuantity`) beside `_creations`, so resolution, lookups and purge never meet a pool.
`ensure_managed_quantity(spell)` returns or composes the version's pool under the store lock (idempotent; a rebind
under the same id re-points it) and registers it with `ReleaseManagedSpell` after the lock; `get_managed_quantity` is
a lock-free read; `discard_managed_quantity(spell_id, pool)` removes that pool only while it is the one under the id,
unregisters it after the lock and never cleans it (a failed transfer's rollback, 0.2.8246). `cleanup()` detaches the
pools with the other maps, unregisters them and cleans them FIRST, newest first, then the disposable registry, the
pools' failures joining the store's ExceptionGroup: a pool is composed at conjure, before the uniques its objects hold.
`extract_spell_creations` adds a `{"scope": "managed", "disposable": False, "stored": pool}` row and unregisters the
pool; `restore_spell_creations` installs a managed row, registers it under the receiving root and cleans the pool it
replaced after the store lock. `purge` returns 0 for a managed spell before any lock; `reset_for_pool` and `clear_all`
run only on lesser and spellspace stores, which hold no pool. See Component: Managed Spell Pools.
EVIDENCE: `src/melder/aether/conduit/creations/creations.py:Creations.ensure_managed_quantity`,
`Creations.discard_managed_quantity`, `Creations.cleanup`, `Creations.extract_spell_creations`,
`Creations.restore_spell_creations` and `Creations.purge`.

""",
)
insert_after(
    "- `_disposable_creations`\n- `_slot_guards` (spell id -> build RLock; entries never replaced or removed while live)\n",
    "- `_managed_quantities` (spell id -> `ManagedSpellQuantity`; root stores only, 0.2.8243)\n",
)
insert_after(
    "- unique_per_spell_space: scoped to a SpellSpace.\n",
    "- managed_spell_quantity: leased from the owning root's pool and given back through ReleaseManagedSpell\n"
    "  (0.2.8241-0.2.8246).\n",
)
insert_after(
    "Purpose:\n- Compile per-spell artifacts and validate correctness before resolution.\n\n",
    """Managed sites (2026-10-15, 0.2.8241 and 0.2.8245): `Existence.managed_spell_quantity` maps to route family "managed"
in `SpellArtifactProcessor._build_model_shell`, and Phase 6 `ScopeOrderingStrategy` ranks it 0 with `unique` (a managed
holder may depend on unique, managed and many spells; any holder may depend on it). A managed site is per path: both
`_is_shared_existence` predicates (occurrence instance processor, occurrence graph analyzer) answer False for it, as
for `many`. Solo discovery declines a model holding a managed spell, so the generalized family's site plan is the only
lowering that dispenses; the generalized manifest takes route key "managed"; `rows_contain_managed_step(rows)` makes
`_install_specializing_door` keep the plain door. SitePlanEmission has four site kinds: shared, `many`, LEASING
managed (no winning key on its own parameters: placed like a shared site with its own `_miss{i}`, feeding exactly
one consumer) and FRESH managed (built like a `many` step, never pooled). A lease is emitted right before its
consumer's construction region - `try: v{i} = pp{i}()` with the pool's bound `pop` as a plan constant (automatic
owner, store set, pool present at emission) or `h{i}._idle.pop()` after a per-creation pool read, then
`except IndexError: v{i} = _miss{i}(...)`. The leasing miss checks unresolved inputs, calls `h{i}.reserve()`, builds
its children and the object inside a `try` whose handler calls `h{i}.abandon(kids, exc)`, and adopts the object's
disposal-bearing `many` children (`kids{i}.append((vK, dmK))` instead of `register_many`). A consumer's leases are
one `try` from the first lease through its construction (a shared consumer's guard, recheck and publication
included): an exception returns them (`_return_leases`), and a lost cold race returns the unused ones
(`_return_unused_leases`); the three runtime helpers are bound only into plans with a managed site. Plans without a
managed step are byte-identical, and no cache generation moves.
EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_leased_region`,
`SitePlanEmission._emit_leasing_miss`, `SitePlanEmission._emit_lease`, `SitePlanRuntimeHelpers.return_leases`,
`SitePlanRuntimeHelpers.return_unused_leases`, `SitePlanRuntimeHelpers.raise_missing_managed_pool`,
`src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:ScopeOrderingStrategy` and
`src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py`.

""",
)

# ---- ownership transfer subcomponent and flows -----------------------------------------------------------------
insert_after(
    "  own version. That is the expected path in a runtime agents iterate in (src_architecture, Runtime Model).\n",
    "- Owner stamps follow the lineage (0.2.8246): the flip stamps the active member and `_migrate_inactive_members`\n"
    "  every moved parked member that carries a stamp through `_restamp`, which registers the stamp-back to the source\n"
    "  first and, for a managed version whose pool the target store did not hold, the discard of the pool its stamp\n"
    "  composed (`Creations.discard_managed_quantity`). A managed version's pool moves as its `managed` row with\n"
    "  `move_creations=True`; with `False` the active member's pool leaves the source with its rows and the target\n"
    "  leases from the fresh pool its stamp composed. A failed transfer stamps every member back and discards the\n"
    "  composed pools after the rows went back.\n",
)
replace_once(
    "- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`\n\n### Subcomponent: ConduitCluster Auto-Sharing\n",
    "- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`\n"
    "- `src/melder/aether/conduit/creations/creations.py`\n\n### Subcomponent: ConduitCluster Auto-Sharing\n",
)
insert_after(
    "   - Flips registries/spellbooks under SafeGuard lock.\n",
    "   - Re-stamps every stamped member onto the target root, each stamp-back registered first (0.2.8246).\n",
)
replace_once(
    "### Flow: Conduit.has_live_creation -> Meld Probe\n",
    """### Flow: Managed Lease -> Release
1. A meld (or an injection inside one) reaches a managed site of the emitted plan: the plan pops the version pool's
   idle deque - a plan constant on an automatic root, a per-creation read of
   `spells[i]._owner_creations._managed_quantities[sid]` elsewhere (none: the missing-pool MeldExecutionError).
2. An empty pool calls the site's miss: the unresolved-input check, `ManagedSpellQuantity.reserve()` (limited:
   refuse at the limit; queue: wait, or refuse at the timeout; an idle object released meanwhile returns at once),
   the children and the object in a `try` (a failure calls `abandon`, which gives the place back and disposes the
   children), then `adopt` records the object's disposal-bearing `many` children.
3. The holder (or the melding caller) uses the object; `Conduit.managed_spell_meld` wraps it in a
   `ManagedSpellLease`.
4. `ReleaseManagedSpell().release(obj)` (or the lease's `release()` or `with` exit): one dict get by `type(obj)`,
   the cold resolver when several pools or a filter apply, then `ManagedSpellQuantity.put_back(obj)`: the reset names
   in order outside every lock, the append, then an elastic trim above the baseline or a queue notify.
5. Root teardown: `Creations.cleanup` unregisters and cleans the root's pools first (idle objects and every recorded
   child), then its disposable registry.

### Flow: Conduit.has_live_creation -> Meld Probe
""",
)

# ---- code map (core) -------------------------------------------------------------------------------------------
a = text.index("## C1 Code Map (Core)\n")
b = text.index("### Full Package Inventory (exhaustive, retained)\n")
section = text[a:b]
entry = re.compile(r"- path: `(?P<path>[^`]+)`\n  start_line: 1\n  end_line: (?P<end>\d+)\n  loc: (?P<loc>\d+)\n  verified_at: (?P<ver>\S+)\n")
changed = []


def remeasure(m: re.Match) -> str:
    path = m.group("path")
    p = pathlib.Path(path)
    if not p.exists():
        return m.group(0)
    n = len(p.read_text(encoding="utf-8").splitlines())
    if n == int(m.group("end")):
        return m.group(0)
    changed.append(path)
    return f"- path: `{path}`\n  start_line: 1\n  end_line: {n}\n  loc: {n}\n  verified_at: {now}\n"


section = entry.sub(remeasure, section)
anchor = re.search(r"- path: `src/melder/aether/conduit/creations/conduit_creations.py`\n(?:  .*\n)+", section)
assert anchor
block = ""
for path in (
    "src/melder/aether/conduit/creations/managed_spell_quantity.py",
    "src/melder/aether/conduit/creations/release_managed_spell.py",
    "src/melder/aether/conduit/creations/managed_spell_lease.py",
    "src/melder/aether/spellbook/existence/managed_spell_mode.py",
    "src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py",
):
    n = len(pathlib.Path(path).read_text(encoding="utf-8").splitlines())
    block += f"- path: `{path}`\n  start_line: 1\n  end_line: {n}\n  loc: {n}\n  verified_at: {now}\n"
section = section[: anchor.end()] + block + section[anchor.end():]
text = text[:a] + section + text[b:]


# ---- the package inventory -------------------------------------------------------------------------------------
def first_class_line(path: str) -> str:
    """The inventory text of a module: its first class docstring's first paragraph, joined, without the period."""
    tree = ast.parse(pathlib.Path(path).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            paragraphs = [
                " ".join(line.strip() for line in block.split("\n") if line.strip())
                for block in (ast.get_docstring(node) or "").split("\n\n")
            ]
            return [p for p in paragraphs if p][0].rstrip(".")
    raise AssertionError(path)


def inventory_row(path: str) -> str:
    """One entry by the inventory's rule: one line up to 120 characters, else the text on its own line, cut to 93
    characters plus '...' when it runs past 100 (the 39 cut entries measured 92-93)."""
    text = first_class_line(path)
    one = f"- `{path}` - {text}"
    if len(one) <= 120:
        return one + "\n"
    if len(text) > 100:
        text = text[:93].rstrip() + "..."
    return f"- `{path}`\n  {text}\n"


insert_after(
    "- `src/melder/aether/conduit/creations/creations.py` - Scoped live creation registry\n",
    inventory_row("src/melder/aether/conduit/creations/managed_spell_lease.py")
    + inventory_row("src/melder/aether/conduit/creations/managed_spell_quantity.py")
    + inventory_row("src/melder/aether/conduit/creations/release_managed_spell.py"),
)
insert_after(
    "- `src/melder/aether/spellbook/existence/existence.py` - Lifecycle mode for a spell binding\n",
    inventory_row("src/melder/aether/spellbook/existence/managed_spell_mode.py"),
)
replace_once(
    "- `src/melder/utilities/custom_exceptions/meld_execution_error.py`\n",
    inventory_row("src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py")
    + "- `src/melder/utilities/custom_exceptions/meld_execution_error.py`\n",
)
insert_after(
    "Module count: 574 (excluding `__init__.py`), measured 2026-08-01.\n",
    "\n2026-10-15: the five managed-spell modules (0.2.8242-0.2.8244) were added by hand, each with its first class\n"
    "docstring line by the same rule; the rest of the walk is unchanged and the count above is not remeasured.\n",
)

# ---- sources, diagram, handoff ---------------------------------------------------------------------------------
replace_once(
    "- `src/melder/aether/conduit/creations/conduit_creations.py`\n- `src/melder/aether/conduit/creations/creations.py`\n"
    "- `src/melder/aether/conduit/meld/conduit_meld.py`\n",
    "- `src/melder/aether/conduit/creations/conduit_creations.py`\n- `src/melder/aether/conduit/creations/creations.py`\n"
    "- `src/melder/aether/conduit/creations/managed_spell_quantity.py`\n"
    "- `src/melder/aether/conduit/creations/release_managed_spell.py`\n"
    "- `src/melder/aether/conduit/creations/managed_spell_lease.py`\n"
    "- `src/melder/aether/spellbook/existence/managed_spell_mode.py`\n"
    "- `src/melder/aether/conduit/meld/conduit_meld.py`\n",
)
replace_once(
    "- `src/melder/utilities/general_base/cleanable.py`\n- `src/melder/utilities/custom_exceptions/spell_space_scope_error.py`\n",
    "- `src/melder/utilities/general_base/cleanable.py`\n- `src/melder/utilities/custom_exceptions/spell_space_scope_error.py`\n"
    "- `src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py`\n",
)
replace_once(
    "### Mermaid: Ownership Transfer\n",
    """### Mermaid: Managed Pools
```mermaid
flowchart LR
  B[Owner stamp: conjure, bind, transfer] --> E[Creations.ensure_managed_quantity]
  E --> Q[ManagedSpellQuantity in the root store]
  E --> R[ReleaseManagedSpell registers it]
  P[Emitted plan] -->|pop, or miss: reserve, build, adopt| Q
  H[Holder] -->|release obj| R
  R -->|type obj, put_back| Q
  C[Creations.cleanup] -->|unregister, clean first| Q
  T[Ownership transfer] -->|managed row moves; stamp follows| Q
```

### Mermaid: Ownership Transfer
""",
)
insert_after(
    "## Context / Handoff Summary\n\n",
    "2026-10-15 managed spells (0.2.8241-0.2.8246; promoted at the end of their lane): the new component Managed Spell\n"
    "Pools (ManagedSpellQuantity, ReleaseManagedSpell, ManagedSpellLease) carries the pools, the registry and the lease;\n"
    "dated entries carry the root exports (Public API), the bind options (Spellbook Core, Binding Pipeline), the hosted\n"
    "registry (Aether), the record (Crystallizer), `managed_spell_meld` (Conduit Runtime), the pool map and its store\n"
    "verbs (Creations), the doors, probes and purge (Meld Resolution Runtime) and the managed site kinds (SpellCompiler);\n"
    "the Ownership Transfer subcomponent and its flow carry the owner stamps (0.2.8246); a lease-and-release flow and a\n"
    "diagram join. The code map adds the five modules and remeasures every changed file; the inventory adds the\n"
    "modules by hand. Open for the owner: stamping versions staged before conjure (src_architecture, Failure Modes).\n\n",
)

added = [l for l in text.splitlines() if l not in before]
long = [l for l in added if len(l) > 120 and "src/melder" not in l]
assert not long, long
DOC.write_text(text, encoding="utf-8")
print("src_components updated:", len(text.splitlines()), "lines; remeasured:", len(changed))
for c in changed:
    print("  ", c)
