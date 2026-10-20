"""S3: give Creations its managed pool map (ensure/get, cleanup first, extract/restore rows, purge 0)."""
import pathlib

PATH = pathlib.Path("src/melder/aether/conduit/creations/creations.py")
text = PATH.read_text(encoding="utf-8")


def swap(old: str, new: str) -> None:
    global text
    assert text.count(old) == 1, old[:80]
    text = text.replace(old, new)


swap(
    "from melder.aether.spellbook.existence.existence import Existence\n"
    "from melder.utilities.general_base.cleanable import Cleanable\n",
    "from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity\n"
    "from melder.aether.spellbook.existence.existence import Existence\n"
    "from melder.utilities.general_base.cleanable import Cleanable\n",
)

swap(
    """        - Cleanup and reusable clearing are explicit, idempotent, and aggregate
          disposal failures.
        - Disposal names are the established Spell-owned list, retained directly""",
    """        - Managed pools (2026-10-15, managed_spell_quantity): a root store keeps one
          `ManagedSpellQuantity` per `Existence.managed_spell_quantity` version it
          owns in `_managed_quantities[spell_id]`, a map of its own: `_creations`
          never holds a pool, so lookups, live probes and purge never meet one.
          `ensure_managed_quantity` composes it at owner stamping; cleanup cleans
          the pools before the disposable registry; extract/restore move a pool
          as a `managed` row; purge returns 0 for a managed spell.
        - Cleanup and reusable clearing are explicit, idempotent, and aggregate
          disposal failures.
        - Disposal names are the established Spell-owned list, retained directly""",
)

swap(
    """    Owned State:
        `_owner_conduit_id`, a stable `_id`, one store `RLock`, the two
        registries (`_creations`, `_disposable_creations`) and the per-slot
        build-guard table (`_slot_guards`).""",
    """    Owned State:
        `_owner_conduit_id`, a stable `_id`, one store `RLock`, the two
        registries (`_creations`, `_disposable_creations`), the per-slot
        build-guard table (`_slot_guards`) and the managed pools
        (`_managed_quantities`, spell id -> `ManagedSpellQuantity`, 2026-10-15).""",
)

swap(
    """        "_disposable_creations",
        "_slot_guards",
    ]
""",
    """        "_disposable_creations",
        "_slot_guards",
        "_managed_quantities",
    ]
""",
)

swap(
    """        self._slot_guards: Dict[str, RLock] = {}
        # Note: resolution-store selection""",
    """        self._slot_guards: Dict[str, RLock] = {}
        # One pool per managed spell version this (root) store owns, composed at
        # owner stamping (`ensure_managed_quantity`). Kept apart from `_creations`:
        # a pool is not an object, and no resolution path may read one as such.
        self._managed_quantities: Dict[str, ManagedSpellQuantity] = {}
        # Note: resolution-store selection""",
)

swap(
    """        Contract:
            - Idempotent.
            - Detaches live and disposable registries before disposal work.
            - Uses `_disposable_creations` only for explicit teardown work.
            - Raises `ExceptionGroup` after best-effort disposal attempts.""",
    """        Contract:
            - Idempotent.
            - Detaches live and disposable registries, and the managed pools,
              before disposal work.
            - Cleans the managed pools FIRST, newest first (2026-10-15): a pool is
              composed at conjure, before the uniques its objects hold, so the
              registry's newest-first walk would close those uniques under live
              pooled objects. A pool's cleanup disposes its idle objects and every
              child recorded for its objects; objects out stay their holders'.
            - Uses `_disposable_creations` only for explicit teardown work.
            - Raises `ExceptionGroup` after best-effort disposal attempts; a
              pool's failures join it as their own chained `RuntimeError`s.""",
)

swap(
    """            self._cleaned = True
            disposable_creations = self._disposable_creations
            creations = self._creations
            self._creations = {}
            self._disposable_creations = {}

        try:
            errors = self._dispose_disposable_registry(disposable_creations)
        except Exception as exc:
            errors = [exc]
        disposable_creations.clear()
        creations.clear()

        del self._creations
        del self._disposable_creations
        del self._slot_guards""",
    """            self._cleaned = True
            disposable_creations = self._disposable_creations
            creations = self._creations
            managed_quantities = self._managed_quantities
            self._creations = {}
            self._disposable_creations = {}
            self._managed_quantities = {}

        errors = self._cleanup_managed_quantities(list(reversed(managed_quantities.values())))
        managed_quantities.clear()
        try:
            errors.extend(self._dispose_disposable_registry(disposable_creations))
        except Exception as exc:
            errors.append(exc)
        disposable_creations.clear()
        creations.clear()

        del self._creations
        del self._disposable_creations
        del self._managed_quantities
        del self._slot_guards""",
)

swap(
    """    def get_creation(self, spell_id: str) -> Optional[Any]:
        \"\"\"
        Return one scoped live object by spell id.

        Contract:
            - Reads only `_creations`.
            - Never consults `_disposable_creations`.
            - Returns the stored object directly.
        \"\"\"
        return self._creations.get(spell_id)
""",
    """    def get_creation(self, spell_id: str) -> Optional[Any]:
        \"\"\"
        Return one scoped live object by spell id.

        Contract:
            - Reads only `_creations`.
            - Never consults `_disposable_creations`.
            - Returns the stored object directly.
        \"\"\"
        return self._creations.get(spell_id)

    def ensure_managed_quantity(self, spell: Spell) -> ManagedSpellQuantity:
        \"\"\"
        Return the pool of one managed spell version in this store, composing it on first use.

        Purpose:
            Give every `Existence.managed_spell_quantity` version a pool in its
            owner root's store the moment the owner is stamped
            (`Spell._add_owned_conduit`: conjure, a post-conjure bind or
            bind_inactive, the transfer flip), so a lease always finds one.

        Contract:
            - Idempotent: one pool per (store, spell id); a second call returns
              the same pool. A rebind under the same content-stable id meets the
              pool its earlier definition left (as a slotted replacement meets
              its slot, 0.2.8219), which is re-pointed at the new Spell object.
            - A new pool is composed from the Spell's options and owned by this
              store's conduit (`owner_conduit_id`); it holds no object yet.
            - Never touches `_creations` or `_disposable_creations`.

        Args:
            spell:
                A Spell bound with `Existence.managed_spell_quantity`.

        Returns:
            ManagedSpellQuantity: The version's pool in this store.

        Raises:
            RuntimeError:
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
        \"\"\"
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

    def get_managed_quantity(self, spell_id: str) -> Optional[ManagedSpellQuantity]:
        \"\"\"
        Return the pool this store holds for one managed spell version, if any.

        Contract:
            - One lock-free dict read of `_managed_quantities`; None when the
              store holds no pool under the id (not managed, not stamped here, or
              moved away by an ownership transfer).
            - Never builds a pool.

        Args:
            spell_id:
                The managed version id.

        Returns:
            Optional[ManagedSpellQuantity]: The pool, or None.

        Raises:
            AttributeError:
                After `cleanup()`, like every other live-surface read of a
                retired store.
        \"\"\"
        return self._managed_quantities.get(spell_id)

    @staticmethod
    def _cleanup_managed_quantities(pools: List[ManagedSpellQuantity]) -> List[Exception]:
        \"\"\"
        Clean detached pools in the given order and collect their failures.

        Contract:
            - Every pool is cleaned even after one fails.
            - A pool's `ExceptionGroup` is flattened into its chained
              `RuntimeError`s, so the store's own group keeps one error per failing
              disposal method; any other exception is kept as raised.
            - Takes no lock: the caller detached the pools first.

        Args:
            pools:
                The pools to clean, in cleaning order.

        Returns:
            List[Exception]: The collected failures, in attempt order.
        \"\"\"
        errors: List[Exception] = []
        for pool in pools:
            try:
                pool.cleanup()
            except ExceptionGroup as group:
                errors.extend(group.exceptions)
            except Exception as exc:
                errors.append(exc)
        return errors
""",
)

swap(
    """            - Unrelated keys, the registration and this reusable store survive.

        Args:
            spell:
                Existing definition discovered by Meld.""",
    """            - Unrelated keys, the registration and this reusable store survive.
            - A managed spell (`Existence.managed_spell_quantity`) returns 0 and
              touches nothing: purge is not part of the managed design (owner,
              2026-10-15), and its objects live in a pool, never in `_creations`.

        Args:
            spell:
                Existing definition discovered by Meld.""",
)

swap(
    """        self.check_cleaned()
        if not purge_all and creation is None:
            raise ValueError("Single-object purge requires a creation reference.")
        existence = spell.existence
        if existence is Existence.unique:""",
    """        self.check_cleaned()
        if not purge_all and creation is None:
            raise ValueError("Single-object purge requires a creation reference.")
        existence = spell.existence
        if existence is Existence.managed_spell_quantity:
            return 0
        if existence is Existence.unique:""",
)

swap(
    """              (an ownership transfer's move or its rollback) takes the children
              wherever the holder goes.

        Threading:
            - Performs extraction under `_lock` so the local slot shape stays
              consistent while the payload is detached.
        \"\"\"
        extracted: List[Dict[str, Any]] = []
        with self._lock:
            live_value = self._creations.get(spell_id)""",
    """              (an ownership transfer's move or its rollback) takes the children
              wherever the holder goes.
            - A managed spell's pool travels as one row (2026-10-15):
              `{"scope": "managed", "disposable": False, "stored": pool}` - the
              same `ManagedSpellQuantity` object with its idle objects, count and
              children records - and this store gives the pool up.

        Threading:
            - Performs extraction under `_lock` so the local slot shape stays
              consistent while the payload is detached.
        \"\"\"
        extracted: List[Dict[str, Any]] = []
        with self._lock:
            pool = self._managed_quantities.pop(spell_id, None)
            if pool is not None:
                extracted.append({"scope": "managed", "disposable": False, "stored": pool})
            live_value = self._creations.get(spell_id)""",
)

swap(
    """            - A unique row with `children` rebuilds the holder's
              `HolderDisposalEntry` (0.2.8238); rows without it restore exactly
              as before.

        Returns:
            None.
        \"\"\"
        if not creations:
            return

        with self._lock:""",
    """            - A unique row with `children` rebuilds the holder's
              `HolderDisposalEntry` (0.2.8238); rows without it restore exactly
              as before.
            - A `managed` row installs its pool under the spell id (2026-10-15).
              A different pool already there - the empty one an ownership
              transfer's flip composed at the target's stamp - is replaced and
              cleaned after the lock is released; the store's own pool is kept.

        Raises:
            RuntimeError:
                For a row that does not fit the local slot shape.
            ExceptionGroup:
                When cleaning a replaced pool failed; raised after the restore
                completed, with the moved pool in place.

        Returns:
            None.
        \"\"\"
        if not creations:
            return

        replaced_pools: List[ManagedSpellQuantity] = []
        with self._lock:""",
)

swap(
    """                stored_value = entry["stored"]
                disposal_methods = entry.get("disposal_methods")

                if scope == "unique":""",
    """                stored_value = entry["stored"]
                disposal_methods = entry.get("disposal_methods")

                if scope == "managed":
                    replaced = self._managed_quantities.get(spell_id)
                    if replaced is not None and replaced is not stored_value:
                        replaced_pools.append(replaced)
                    self._managed_quantities[spell_id] = stored_value
                    continue

                if scope == "unique":""",
)

swap(
    """                raise RuntimeError(
                    f"Unknown creation scope '{scope}' while restoring spell '{spell_id}'."
                )
""",
    """                raise RuntimeError(
                    f"Unknown creation scope '{scope}' while restoring spell '{spell_id}'."
                )

        if replaced_pools:
            errors = self._cleanup_managed_quantities(replaced_pools)
            if errors:
                raise ExceptionGroup(
                    f"Errors occurred cleaning the managed pool replaced while restoring spell '{spell_id}'",
                    errors,
                )
""",
)

swap(
    """            - Leaves this `Creations` instance reusable after the clear
              completes. Slot guards are kept (they are per spell id, not per
              generation).
""",
    """            - Leaves this `Creations` instance reusable after the clear
              completes. Slot guards are kept (they are per spell id, not per
              generation).
            - Leaves the managed pools untouched: only root stores hold pools,
              and the reusable clears run on lesser and spellspace stores only (a
              lesser's pool return, a spellspace's exit), never on a root's.
""",
)

PATH.write_text(text, encoding="utf-8")
print("creations.py updated")
