"""S3: owner stamping ensures the pool; the meld doors and the static rooms read a managed spell."""
import pathlib


def edit(path: str, swaps: list) -> None:
    file = pathlib.Path(path)
    text = file.read_text(encoding="utf-8")
    for old, new in swaps:
        assert text.count(old) == 1, (path, old[:90])
        text = text.replace(old, new)
    file.write_text(text, encoding="utf-8")
    print("updated", path)


edit("src/melder/aether/spellbook/spell.py", [
    (
        """        - Reconfigure CreationContextFactory dependencies for the new owner.
        - Invalidate the spell-owned CreationContext because ownership/scoping changed.
""",
        """        - Reconfigure CreationContextFactory dependencies for the new owner.
        - Invalidate the spell-owned CreationContext because ownership/scoping changed.
        - Give an `Existence.managed_spell_quantity` version its pool in the owner's store
          (`creations.ensure_managed_quantity(self)`, idempotent; 2026-10-15): every stamp - conjure, a
          post-conjure bind or bind_inactive, the transfer flip - ends with the version's pool in the store it
          was stamped with. No pool is composed when the stamp carries no store.
""",
    ),
    (
        """            self._owner_conduit_id = conduit_id
            self._owner_conduit_name = conduit_name
            self._owner_creations = creations
            self._caching_enabled = caching_enabled
""",
        """            self._owner_conduit_id = conduit_id
            self._owner_conduit_name = conduit_name
            self._owner_creations = creations
            self._caching_enabled = caching_enabled
            # Spell lock, then the store's leaf lock: the established build-lock-first order.
            if self.existence is Existence.managed_spell_quantity and creations is not None:
                creations.ensure_managed_quantity(self)
""",
    ),
])

edit("src/melder/aether/conduit/meld/conduit_meld.py", [
    (
        """            - SpellSpace lifetime is refused even when a space is active.
            - Does not remove entries, take creation locks, or invoke callbacks.
""",
        """            - SpellSpace lifetime is refused even when a space is active.
            - A managed spell (`Existence.managed_spell_quantity`) uses this
              caller's own store, where `Creations.purge` returns 0 for it: its
              objects live in a pool, and purge is not part of the managed design
              (2026-10-15), so there is nothing to authorize.
            - Does not remove entries, take creation locks, or invoke callbacks.
""",
    ),
    (
        """        existence = spell.existence
        if existence in (Existence.many, Existence.unique_per_conduit):
            return self._conduit_creations
        if existence is Existence.unique_per_spell_space:""",
        """        existence = spell.existence
        if existence in (Existence.many, Existence.unique_per_conduit, Existence.managed_spell_quantity):
            return self._conduit_creations
        if existence is Existence.unique_per_spell_space:""",
    ),
    (
        """            - `unique` reads the Spell owner's `owner_creations`;
              `unique_per_conduit_lineage` the lineage-root store;
              `unique_per_conduit_cluster` the cluster's team store, and is
              not live while no leader is elected.
            - spellspace-request spells never reach this helper because the
              conduit-facing door rejects them earlier.
        \"\"\"""",
        """            - `unique` reads the Spell owner's `owner_creations`;
              `unique_per_conduit_lineage` the lineage-root store;
              `unique_per_conduit_cluster` the cluster's team store, and is
              not live while no leader is elected.
            - `managed_spell_quantity` reads the pool in the Spell owner's store
              (2026-10-15): live while the pool's count (objects alive, idle plus
              out) is above 0, `creation_count` that count, storage scope
              `"managed_pool"`; a version with no owner store or no pool yet is
              not live.
            - spellspace-request spells never reach this helper because the
              conduit-facing door rejects them earlier.
        \"\"\"""",
    ),
    (
        """                "active_spellspace_id": None,
                "creation_count": 1 if creation is not None else 0,
            }

        raise RuntimeError(
            "Unsupported existence '{0}' for live creation probe.".format(
                existence,
            )
        )""",
        """                "active_spellspace_id": None,
                "creation_count": 1 if creation is not None else 0,
            }

        if existence is Existence.managed_spell_quantity:
            return self._describe_managed_pool_status(spell, query_conduit_id)

        raise RuntimeError(
            "Unsupported existence '{0}' for live creation probe.".format(
                existence,
            )
        )

    @staticmethod
    def _describe_managed_pool_status(spell: Spell, query_conduit_id: str) -> Dict[str, object]:
        \"\"\"
        Return the live-creation status of a managed spell from its owner store's pool.

        Contract:
            - Reads `spell._owner_creations.get_managed_quantity(spell_id)`; a
              version with no owner store (not stamped yet) or no pool reports 0.
            - `is_live` when the pool's count is above 0; `creation_count` is the
              count (objects built and alive, idle plus out), read without a lock.
            - Never creates, leases or mutates anything.

        Args:
            spell: The resolved managed spell.
            query_conduit_id: The conduit the probe was asked through.

        Returns:
            Dict[str, object]: The status payload, storage scope `"managed_pool"`.
        \"\"\"
        store = spell._owner_creations
        pool = store.get_managed_quantity(spell.spell_id) if store is not None else None
        count = pool.count if pool is not None else 0
        return {
            "is_live": count > 0,
            "spell_id": spell.spell_id,
            "spell_name": spell.spell_name,
            "existence": spell.existence.name,
            "query_conduit_id": query_conduit_id,
            "storage_scope_kind": "managed_pool",
            "storage_owner_conduit_id": spell._owner_conduit_id,
            "active_spellspace_id": None,
            "creation_count": count,
        }""",
    ),
])

edit("src/melder/aether/conduit/meld/spellspace_meld.py", [
    (
        """            - `unique` reads the Spell owner's `owner_creations`;
              `unique_per_conduit_lineage` the owner conduit's lineage-root
              store; `unique_per_conduit_cluster` the cluster's team store,
              and is not live while no leader is elected.
""",
        """            - `unique` reads the Spell owner's `owner_creations`;
              `unique_per_conduit_lineage` the owner conduit's lineage-root
              store; `unique_per_conduit_cluster` the cluster's team store,
              and is not live while no leader is elected.
            - `managed_spell_quantity` reads the pool in the Spell owner's root
              store, as the conduit door does (2026-10-15): a managed object is
              never space-local, so `active_spellspace_id` is None.
""",
    ),
    (
        """                "active_spellspace_id": None,
                "creation_count": 1 if creation is not None else 0,
            }

        raise RuntimeError(
            "Unsupported existence '{0}' for live creation probe.".format(
                existence,
            )
        )""",
        """                "active_spellspace_id": None,
                "creation_count": 1 if creation is not None else 0,
            }

        if existence is Existence.managed_spell_quantity:
            return ConduitMeld._describe_managed_pool_status(spell, query_conduit_id)

        raise RuntimeError(
            "Unsupported existence '{0}' for live creation probe.".format(
                existence,
            )
        )""",
    ),
])
