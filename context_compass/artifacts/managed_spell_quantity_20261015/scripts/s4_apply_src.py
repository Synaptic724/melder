"""S4 source edits beside the two new modules: the pool's class key and cleanup-safe Spell read, SpellIndex's
selected-version probe, Creations registering and unregistering its pools, Aether hosting the registry, and the
package-root exports. Every anchor must match exactly once or nothing is written for that file."""
import pathlib


import sys

SKIP = set(sys.argv[1:])


def apply(path: str, replacements: list) -> None:
    if path in SKIP:
        print("skipped (already applied)", path)
        return
    file = pathlib.Path(path)
    text = file.read_text(encoding="utf-8")
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path}: anchor matched {count} times, nothing written:\n{old[:240]}")
        text = text.replace(old, new)
    file.write_text(text, encoding="utf-8")
    print("updated", path)


# ---------------------------------------------------------------- ManagedSpellQuantity
apply("src/melder/aether/conduit/creations/managed_spell_quantity.py", [
    (
        "        - `_spell`: the Spell, borrowed (never cleaned here); read by `ReleaseManagedSpell`'s cold resolver (S4).\n",
        "        - `_spell`: the Spell, borrowed (never cleaned here); `ReleaseManagedSpell`'s cold resolver reads it through\n"
        "          `_spell_unless_cleaned` (S4).\n"
        "        - `_managed_class`: the bound class (`spell.spell`), the key `ReleaseManagedSpell` routes releases by;\n"
        "          re-captured when a rebind re-points the pool, and kept after cleanup.\n",
    ),
    (
        "        and deletes the borrowed Spell; every other field stays as a documented tombstone, because an emitted plan,\n",
        "        and deletes the borrowed Spell under the lock; every other field (the class key included) stays as a\n"
        "        documented tombstone, because an emitted plan,\n",
    ),
    (
        '''    __slots__ = AbstractElasticPool.__slots__ + [
        "_spell",
''',
        '''    __slots__ = AbstractElasticPool.__slots__ + [
        "_spell",
        "_managed_class",
''',
    ),
    (
        "        self._spell: Spell = spell\n        self._spell_id: str = spell.spell_id\n",
        "        self._spell: Spell = spell\n"
        "        # The registry's key: a managed spell binds a class, and type(obj) of every object it builds is that class.\n"
        "        self._managed_class: type = spell.spell\n"
        "        self._spell_id: str = spell.spell_id\n",
    ),
    (
        '''            - Deletes the borrowed Spell; the other fields stay as documented tombstones (class docstring).
''',
        '''            - Deletes the borrowed Spell while it holds the lock, so `_spell_unless_cleaned` never meets a half-retired
              pool; the other fields, the class key included, stay as documented tombstones (class docstring).
''',
    ),
    (
        '''            self._children_by_object = {}
            self._orphaned_children = []
            condition.notify_all()
''',
        '''            self._children_by_object = {}
            self._orphaned_children = []
            # Under the lock: `_spell_unless_cleaned` reads the cleaned flag and the Spell under it.
            del self._spell
            condition.notify_all()
''',
    ),
    (
        '''        for children in reversed(orphaned_children):
            failures.extend(self._dispose_children(children))
        del self._spell
        if failures:
''',
        '''        for children in reversed(orphaned_children):
            failures.extend(self._dispose_children(children))
        if failures:
''',
    ),
    (
        '''        self.check_cleaned()
        return self._spell

    @property
    def spell_id(self) -> str:
''',
        '''        self.check_cleaned()
        return self._spell

    def _spell_unless_cleaned(self) -> Optional[Spell]:
        """
        Internal

        Return the borrowed Spell, or None once the pool is torn down.

        Purpose:
            The cleanup-safe read `ReleaseManagedSpell` uses while it resolves a release or describes a pool: a
            teardown racing it answers None instead of raising.

        Threading:
            Reads the cleaned flag and the Spell under `_lock`, the lock `cleanup()` marks the pool cleaned and
            deletes the Spell under. Holds no other lock and runs no user code.

        Returns:
            Optional[Spell]: The Spell of the pool's version, or None when the pool was cleaned.
        """
        with self._lock:
            if self._cleaned:
                return None
            return self._spell

    @property
    def managed_class(self) -> type:
        """
        Return the managed class, the key `ReleaseManagedSpell` routes this pool's releases by.

        Contract:
            The class the managed spell binds (`spell.spell`); every object the pool holds is of exactly this class.
            Re-captured when a rebind re-points the pool at another Spell object. Readable after cleanup.

        Returns:
            type: The managed class.
        """
        return self._managed_class

    @property
    def spell_id(self) -> str:
''',
    ),
    (
        '''            Called only by `Creations.ensure_managed_quantity`, under the store lock, for a Spell with this pool's
            spell id (hence the same options and disposal names). One reference store; no user code.
''',
        '''            Called only by `Creations.ensure_managed_quantity`, under the store lock, for a Spell with this pool's
            spell id (hence the same options and disposal names). Re-captures the class key too: a redefined class is
            a new class object under the same content-stable id, and the store re-registers the pool under it. Two
            reference stores; no user code.
''',
    ),
    (
        '''        self._spell = spell

    def _torn_down_error(self, consequence: str) -> RuntimeError:
''',
        '''        self._spell = spell
        self._managed_class = spell.spell

    def _torn_down_error(self, consequence: str) -> RuntimeError:
''',
    ),
])

# ---------------------------------------------------------------- SpellIndex
apply("src/melder/aether/spellbook/bind/spell_index.py", [
    (
        '''        with self._lock:
            if self._cleaned:
                return False
            return spell_id in self._spells_in_index

''',
        '''        with self._lock:
            if self._cleaned:
                return False
            return spell_id in self._spells_in_index

    def _is_selected_unless_cleaned(self, spell_id: str) -> bool:
        """
        Internal

        Return whether this index currently selects `spell_id`, answering False once the index is cleaned.

        Purpose:
            Selected-version probe for readers that neither own nor lock the index - `ReleaseManagedSpell`'s cold
            resolver prefers the pool of the version its index selects (STORY-2026-10-15-release_managed_spell).
            `selected_spell_id` is a lock-free read of a field `cleanup()` deletes, so such a reader racing a
            cleanup would meet an AttributeError there.

        Contract:
            - Tests SELECTION, not membership: a parked member of the lineage answers False.
            - Never raises for a cleaned index; returns False.
            - Pure read: changes nothing.

        Threading:
            Reads the cleaned flag and the selected id under `self._lock`, the lock `cleanup()` marks the index
            cleaned and deletes the selected id under, and `update()` repoints it under.

        Args:
            spell_id (str): The version id to test.

        Returns:
            bool: True if this live index selects `spell_id`; False otherwise, and False once the index is cleaned.
        """
        with self._lock:
            if self._cleaned:
                return False
            return self._selected_spell_id == spell_id

''',
    ),
])

# ---------------------------------------------------------------- Creations
apply("src/melder/aether/conduit/creations/creations.py", [
    (
        '''from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.spellbook.existence.existence import Existence
''',
        '''from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.existence.existence import Existence
''',
    ),
    (
        '''          `ensure_managed_quantity` composes it at owner stamping; cleanup cleans
          the pools before the disposable registry; extract/restore move a pool
          as a `managed` row; purge returns 0 for a managed spell.
''',
        '''          `ensure_managed_quantity` composes it at owner stamping; cleanup cleans
          the pools before the disposable registry; extract/restore move a pool
          as a `managed` row; purge returns 0 for a managed spell. The store
          registers every pool it takes with `ReleaseManagedSpell` and
          unregisters every pool it gives up (S4), outside the store lock, so
          the registry holds exactly the pools live stores hold.
''',
    ),
    (
        '''            - Cleans the managed pools FIRST, newest first (2026-10-15): a pool is
''',
        '''            - Unregisters the managed pools from `ReleaseManagedSpell`, then
              cleans them FIRST, newest first (2026-10-15): a pool is
''',
    ),
    (
        '''        errors = self._cleanup_managed_quantities(list(reversed(managed_quantities.values())))
        managed_quantities.clear()
''',
        '''        pools = list(reversed(managed_quantities.values()))
        # Outside the store lock (a leaf): no release can be routed to a pool this store is about to retire.
        self._unregister_managed_quantities(pools)
        errors = self._cleanup_managed_quantities(pools)
        managed_quantities.clear()
''',
    ),
    (
        '''            - A new pool is composed from the Spell's options and owned by this
              store's conduit (`owner_conduit_id`); it holds no object yet.
            - Never touches `_creations` or `_disposable_creations`.
''',
        '''            - A new pool is composed from the Spell's options and owned by this
              store's conduit (`owner_conduit_id`); it holds no object yet.
            - Registers the pool with `ReleaseManagedSpell` under this store's
              root (idempotent; a rebind that brought another class object
              re-keys it), so a release of its class reaches it.
            - Never touches `_creations` or `_disposable_creations`.
''',
    ),
    (
        '''            RuntimeError:
                If this store has been permanently cleaned.
            ValueError:
                If the spell is not `Existence.managed_spell_quantity` (the pool
                refuses it; nothing is stored).

        Threading:
            The map read and write run under the store lock, a leaf; composing a
            pool runs no user code. Called under the Spell's lock by owner
            stamping, the established build-lock-then-store-lock order. Pools are
            registered with `ReleaseManagedSpell` after this lock is released
            (STORY-2026-10-15-release_managed_spell, S4).
        """
        with self._lock:
            self.check_cleaned()
            spell_id = spell.spell_id
            pool = self._managed_quantities.get(spell_id)
            if pool is None:
                pool = ManagedSpellQuantity(spell=spell, owner_conduit_id=self._owner_conduit_id)
                self._managed_quantities[spell_id] = pool
            else:
                pool._rebind_spell(spell)
        return pool
''',
        '''            RuntimeError:
                If this store has been permanently cleaned, or no live
                `ReleaseManagedSpell` exists to register with.
            ValueError:
                If the spell is not `Existence.managed_spell_quantity` (the pool
                refuses it; nothing is stored), or no Aether built the registry.

        Threading:
            The map read and write run under the store lock, a leaf; composing a
            pool runs no user code. Called under the Spell's lock by owner
            stamping, the established build-lock-then-store-lock order. The pool
            is registered with `ReleaseManagedSpell` after this lock is released
            (its own lock is a leaf held only to publish), so the order is Spell
            lock -> registry lock and the store lock stays a leaf.
        """
        with self._lock:
            self.check_cleaned()
            spell_id = spell.spell_id
            pool = self._managed_quantities.get(spell_id)
            if pool is None:
                pool = ManagedSpellQuantity(spell=spell, owner_conduit_id=self._owner_conduit_id)
                self._managed_quantities[spell_id] = pool
            else:
                pool._rebind_spell(spell)
            owner_conduit_id = self._owner_conduit_id
        ReleaseManagedSpell().register(pool, root_conduit_id=owner_conduit_id)
        return pool
''',
    ),
    (
        '''    @staticmethod
    def _cleanup_managed_quantities(pools: List[ManagedSpellQuantity]) -> List[Exception]:
''',
        '''    @staticmethod
    def _unregister_managed_quantities(pools: List[ManagedSpellQuantity]) -> None:
        """
        Unregister pools this store gives up from `ReleaseManagedSpell`.

        Contract:
            - Unregisters each pool from the live registry (idempotent there).
            - Does nothing when no live registry exists: Aether cleans the registry only after its frames, so a store
              torn down later (or after a test reset the registry) has nothing to unregister from.
            - Takes no store lock: the caller detached the pools first.

        Args:
            pools:
                The pools to unregister.

        Returns:
            None.
        """
        registry = ReleaseManagedSpell._live_instance()
        if registry is None:
            return
        for pool in pools:
            registry.unregister(pool)

    @staticmethod
    def _cleanup_managed_quantities(pools: List[ManagedSpellQuantity]) -> List[Exception]:
''',
    ),
    (
        '''              same `ManagedSpellQuantity` object with its idle objects, count and
              children records - and this store gives the pool up.
''',
        '''              same `ManagedSpellQuantity` object with its idle objects, count and
              children records - and this store gives the pool up, unregistering
              it from `ReleaseManagedSpell` after the store lock (S4).
''',
    ),
    (
        '''                elif disposable_entry is not None:
                    entry["disposal_methods"] = disposable_entry[1]
                extracted.append(entry)

        return extracted
''',
        '''                elif disposable_entry is not None:
                    entry["disposal_methods"] = disposable_entry[1]
                extracted.append(entry)

        if pool is not None:
            # A pool in flight between stores is not routable until a restore registers it again.
            self._unregister_managed_quantities([pool])
        return extracted
''',
    ),
    (
        '''            - A `managed` row installs its pool under the spell id (2026-10-15).
              A different pool already there - the empty one an ownership
              transfer's flip composed at the target's stamp - is replaced and
              cleaned after the lock is released; the store's own pool is kept.
''',
        '''            - A `managed` row installs its pool under the spell id (2026-10-15).
              A different pool already there - the empty one an ownership
              transfer's flip composed at the target's stamp - is replaced and
              cleaned after the lock is released; the store's own pool is kept.
            - After the lock, in this order (S4): the replaced pool is
              unregistered from `ReleaseManagedSpell`, the installed pool is
              registered under this store's root, then the replaced pool is
              cleaned - so the moved pool is routable even when that cleanup
              fails.
''',
    ),
    (
        '''        replaced_pools: List[ManagedSpellQuantity] = []
        with self._lock:
''',
        '''        replaced_pools: List[ManagedSpellQuantity] = []
        installed_pools: List[ManagedSpellQuantity] = []
        with self._lock:
            owner_conduit_id = self._owner_conduit_id
''',
    ),
    (
        '''                    if replaced is not None and replaced is not stored_value:
                        replaced_pools.append(replaced)
                    self._managed_quantities[spell_id] = stored_value
                    continue
''',
        '''                    if replaced is not None and replaced is not stored_value:
                        replaced_pools.append(replaced)
                    self._managed_quantities[spell_id] = stored_value
                    installed_pools.append(stored_value)
                    continue
''',
    ),
    (
        '''        if replaced_pools:
            errors = self._cleanup_managed_quantities(replaced_pools)
''',
        '''        self._unregister_managed_quantities(replaced_pools)
        for installed in installed_pools:
            ReleaseManagedSpell().register(installed, root_conduit_id=owner_conduit_id)
        if replaced_pools:
            errors = self._cleanup_managed_quantities(replaced_pools)
''',
    ),
])

# ---------------------------------------------------------------- Aether
apply("src/melder/aether/aether.py", [
    (
        '''from melder.aether.aetheric_mediator.transaction_type import TransactionType
''',
        '''from melder.aether.aetheric_mediator.transaction_type import TransactionType
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
''',
    ),
    (
        '''        - Hosts the singleton MutationResearch root above frame-local runtime
          state.
''',
        '''        - Hosts the singleton MutationResearch root above frame-local runtime
          state.
        - Hosts `ReleaseManagedSpell`, the registry managed objects are given
          back through: built last at boot, cleaned right after the frames.
''',
    ),
    (
        '''        frame registry and hosts the singleton subsystems: `AetherUtilitySystem`,
        `Crystallizer`, `Nexus`, the `MutationResearch` root, and the
        `LoadGate`. All three subsystem roots are constructed EAGERLY in
        `__init__`, in that order - Crystallizer leads because the other two
        read it out of this host as they build.
''',
        '''        frame registry and hosts the singleton subsystems: `AetherUtilitySystem`,
        `Crystallizer`, `Nexus`, the `MutationResearch` root, the
        `LoadGate` and `ReleaseManagedSpell`. All three subsystem roots are
        constructed EAGERLY in `__init__`, in that order - Crystallizer leads
        because the other two read it out of this host as they build - and the
        release registry is built last, because nothing reads it at boot.
''',
    ),
    (
        '''            Create the root `Aether` host and construct the hosted
            singleton-level subsystems (Crystallizer, utility system, LoadGate,
            and the private `Nexus` root). Frames are lazy by design: no
''',
        '''            Create the root `Aether` host and construct the hosted
            singleton-level subsystems (Crystallizer, utility system, LoadGate,
            the private `Nexus` root, and last `ReleaseManagedSpell`, the
            registry of managed pools). Frames are lazy by design: no
''',
    ),
    (
        '''                self._nexus: Nexus = Nexus(aether=self)
                # BUG-002 (2026-07-17 audit): the once-only latch flips while
''',
        '''                self._nexus: Nexus = Nexus(aether=self)
                # ReleaseManagedSpell is built LAST (owner ruling 2026-10-15: a singleton like Aether, created and
                # owned here at boot, cleaned by this host, with the same reset hook). It is the class-keyed registry
                # of managed pools that `ReleaseManagedSpell()` hands back; it reads no other hosted root, and root
                # stores register their pools in it only once frames exist.
                self._release_managed_spell: ReleaseManagedSpell = ReleaseManagedSpell(aether=self)
                # BUG-002 (2026-07-17 audit): the once-only latch flips while
''',
    ),
    (
        '''            - Cleans the hosted Nexus singleton and utility system when they exist.
''',
        '''            - Cleans the hosted Nexus singleton and utility system when they exist.
            - Cleans `ReleaseManagedSpell` right after the frames: their root
              stores unregister their pools as they are torn down, so the
              registry is empty when it is retired.
''',
    ),
    (
        '''                if self._aetheric_frames is not None:
                    self.cleanup_aetheric_frames() # This will clean each individual frame
                    self._aetheric_frames.clear() # This cleans the ConcurrentDictionary
                    self._aetheric_frame_view = ()
''',
        '''                if self._aetheric_frames is not None:
                    self.cleanup_aetheric_frames() # This will clean each individual frame
                    self._aetheric_frames.clear() # This cleans the ConcurrentDictionary
                    self._aetheric_frame_view = ()
                # The frames' root stores unregistered their pools while they were torn down; nothing can register
                # one any more, so the release registry is retired here, before the other hosted roots.
                self._release_managed_spell.cleanup()
''',
    ),
    (
        '''                del self._load_gate
                del self._aetheric_mediator
''',
        '''                del self._load_gate
                del self._aetheric_mediator
                del self._release_managed_spell
''',
    ),
])

# ---------------------------------------------------------------- package root
apply("src/melder/__init__.py", [
    (
        '''- BIND: Spellbook, SpellBinder, scan_bind (decorator), Spell,
  SpellIndex; vocabulary Existence, Permissions, Policies, SystemState.
- RESOLVE: Conduit (meld, lesser conduits, link/sever), SpellSpace,
  declarative descriptors SpellMap and SpellContract.
''',
        '''- BIND: Spellbook, SpellBinder, scan_bind (decorator), Spell,
  SpellIndex; vocabulary Existence, ManagedSpellMode, Permissions,
  Policies, SystemState.
- RESOLVE: Conduit (meld, lesser conduits, link/sever), SpellSpace,
  declarative descriptors SpellMap and SpellContract; managed objects go
  back through ReleaseManagedSpell (release, managed -> ManagedSpellLease).
''',
    ),
    (
        '''  PhaseTimeoutError, DeadReferenceError, UnresolvedInputError.
''',
        '''  PhaseTimeoutError, DeadReferenceError, UnresolvedInputError,
  ManagedSpellExhaustedError.
''',
    ),
    (
        '''from melder.aether.conduit.conduit import Conduit
''',
        '''from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_lease import ManagedSpellLease
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
''',
    ),
    (
        '''from melder.aether.spellbook.existence.existence import Existence
''',
        '''from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
''',
    ),
    (
        '''from melder.utilities.custom_exceptions.internal_registration_error import (
    InternalRegistrationError,
)
''',
        '''from melder.utilities.custom_exceptions.internal_registration_error import (
    InternalRegistrationError,
)
from melder.utilities.custom_exceptions.managed_spell_exhausted_error import (
    ManagedSpellExhaustedError,
)
''',
    ),
    (
        '''    "LaneType",
    "MeldExecutionError",
''',
        '''    "LaneType",
    "ManagedSpellExhaustedError",
    "ManagedSpellLease",
    "ManagedSpellMode",
    "MeldExecutionError",
''',
    ),
    (
        '''    "ProtocolCrafter",
    "ResearchSet",
''',
        '''    "ProtocolCrafter",
    "ReleaseManagedSpell",
    "ResearchSet",
''',
    ),
])
