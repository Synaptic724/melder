"""S6: apply the owner-stamp change to creations.py and transfer_of_ownership.py (exact-anchor edits).

Run from the repository root: python s6_apply_src.py
"""
import pathlib

CREATIONS = pathlib.Path("src/melder/aether/conduit/creations/creations.py")
TRANSFER = pathlib.Path("src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py")


def replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, (old[:80], text.count(old))
    return text.replace(old, new, 1)


DISCARD = '''
    def discard_managed_quantity(self, spell_id: str, pool: ManagedSpellQuantity) -> bool:
        """
        Give up one pool this store holds, when it is still the pool under the id.

        Purpose:
            Take back a pool an owner stamp composed in this store. An ownership
            transfer's rollback uses it to remove the empty pool its stamp of the
            target root composed (`TransferOfOwnership._discard_composed_pool`,
            2026-10-15), so a failed transfer leaves the target store as it was.

        Contract:
            - Removes `pool` only when it is the pool this store holds under
              `spell_id` (identity). Any other pool under the id, or none, is left
              as it is and the call answers False, so a pool the store held before
              the stamp, or one an extract already took, is never touched.
            - Unregisters the removed pool from `ReleaseManagedSpell` after the
              store lock, as every store verb that gives a pool up does (S4).
            - Never cleans the pool and never touches `_creations` or
              `_disposable_creations`: the removed pool is the caller's, who
              decides its end (the transfer's rollback cleans it).
            - Idempotent for one pool: a second call answers False.

        Args:
            spell_id:
                The managed version id the pool is held under.
            pool:
                The pool to give up.

        Returns:
            bool: True when the pool was removed; False when this store does not
            hold it under `spell_id`.

        Raises:
            RuntimeError:
                If this store has been permanently cleaned (its cleanup already
                gave its pools up), as `ensure_managed_quantity` refuses.

        Threading:
            The identity check and the removal run under the store lock, a leaf,
            so of two racing calls exactly one removes the pool; the unregister
            runs after the lock, so the registry's leaf lock is never taken under
            the store lock.
        """
        with self._lock:
            self.check_cleaned()
            if self._managed_quantities.get(spell_id) is not pool:
                return False
            del self._managed_quantities[spell_id]
        self._unregister_managed_quantities([pool])
        return True
'''

text = CREATIONS.read_text(encoding="utf-8")
anchor = '''        return self._managed_quantities.get(spell_id)

    @staticmethod
    def _unregister_managed_quantities(pools: List[ManagedSpellQuantity]) -> None:
'''
text = replace_once(
    text,
    anchor,
    '''        return self._managed_quantities.get(spell_id)
''' + DISCARD + '''
    @staticmethod
    def _unregister_managed_quantities(pools: List[ManagedSpellQuantity]) -> None:
''',
)
CREATIONS.write_text(text, encoding="utf-8")

text = TRANSFER.read_text(encoding="utf-8")

# 1) The flip stamps through _restamp (stamp-back registered first, the composed pool's discard after).
old_flip = '''            # SpellIndex no longer records an owner; the spell's _spellbook
            # (set above) and _owner_conduit_id (set here) are the record.
            spell_obj._owner_conduit_id = self.target_conduit._id
            caching_enabled = tgt_book._resolve_system_caching_enabled()
            spell_obj._add_owned_conduit(
                self.target_conduit._id,
                self.target_conduit._name,
                self.target_conduit._creations,
                dynamic_environment=self.target_conduit.__dynamic_environment__,
                creation_gate_controller=self.target_conduit._creation_gate_controller,
                caching_enabled=caching_enabled,
            )
'''
new_flip = '''            # SpellIndex no longer records an owner; the spell's _spellbook
            # (set above) and _owner_conduit_id (set here) are the record.
            spell_obj._owner_conduit_id = self.target_conduit._id
            # The full owner stamp (store, factory, caching posture; a managed
            # version's pool in the target store), with its rollback: a failed
            # transfer stamps the member back onto the source and discards a
            # pool this stamp composed (2026-10-15).
            self._restamp(spell_obj)
'''
text = replace_once(text, old_flip, new_flip)

# 2) Parked members that carry a stamp are re-stamped onto the target after their maps move.
old_migrate = '''        if moved:
            self._register_rollback(
                partial(self._rollback_inactive_members, moved, src_book, tgt_book)
            )

    def _rollback_inactive_members(
'''
new_migrate = '''        if moved:
            self._register_rollback(
                partial(self._rollback_inactive_members, moved, src_book, tgt_book)
            )
        # Outside the Book locks, under the conduit locks `execute` holds - where
        # the flip stamps the active member. A member never stamped (a version
        # staged with bind_inactive before conjure) carries no store and is moved
        # as before; every other member gets the target's stamp (2026-10-15).
        for inactive_spell, _member_id in moved:
            if inactive_spell._owner_creations is not None:
                self._restamp(inactive_spell)

    def _rollback_inactive_members(
'''
text = replace_once(text, old_migrate, new_migrate)

# 3) The migrate docstring states the re-stamp.
old_doc = '''        member is moved `src._inactive_spells -> tgt._inactive_spells` (plus the
        `_spell_ids` existence set) and has its `_spellbook` / `_spell_system_states`
        / `_owner_conduit_id` repointed to the target. The active map, `_spell_id_pool`,
        and risk manager are intentionally untouched -- inactive members stay off
        resolution. A single rollback handler reverses the whole batch on failure.
'''
new_doc = '''        member is moved `src._inactive_spells -> tgt._inactive_spells` (plus the
        `_spell_ids` existence set) and has its `_spellbook` / `_spell_system_states`
        / `_owner_conduit_id` repointed to the target. The active map, `_spell_id_pool`,
        and risk manager are intentionally untouched -- inactive members stay off
        resolution. A single rollback handler reverses the whole batch on failure.

        Then, outside the Book locks, every moved member that carries an owner
        stamp (its `_owner_creations` is set) is stamped onto the target through
        `_restamp`, exactly as the flip stamps the active member (2026-10-15): it
        names the target root's store, so a notch on the target builds or leases
        from the target's store, and a managed version gets its pool there (a
        moving transfer then replaces that pool with the moved one). Each stamp
        registers its own stamp-back and, for a pool it composed, its discard. A
        member never stamped - a version staged with `bind_inactive` before
        conjure - keeps no store and is moved as before.
'''
text = replace_once(text, old_doc, new_doc)

# 4) The helpers, placed after _rollback_inactive_members.
old_after = '''                    inactive_spell._spellbook = src_book
                    inactive_spell._spell_system_states = src_states
                    inactive_spell._owner_conduit_id = source_conduit_id
        except Exception:
            pass

'''
assert text.count(old_after) == 1
HELPERS = '''                    inactive_spell._spellbook = src_book
                    inactive_spell._spell_system_states = src_states
                    inactive_spell._owner_conduit_id = source_conduit_id
        except Exception:
            pass

    def _stamp_owner(self, spell: Any, conduit: Any, spellbook: Any) -> None:
        """
        Stamp `conduit` as `spell`'s owner, the way conjure and bind stamp.

        Purpose:
            One owner stamp for every transfer step that moves a member's owner:
            the root's id, name and creations store, its dynamic flag and the
            frame's CreationGateController, and the caching posture of the Book
            that owns the member (`SpellbookCreationSystem.define_conduit_into_spells`
            and the post-conjure bind paths write the same values).

        Contract:
            - Delegates to `Spell._add_owned_conduit`, which clears the spell's
              CreationContext, rebuilds its CreationContextFactory and, for an
              `Existence.managed_spell_quantity` version, ensures its pool in the
              stamped store (composed when the store holds none).
            - Registers nothing: `_restamp` owns the rollback bookkeeping, and a
              rollback calls this to stamp a member back.

        Args:
            spell: The member to stamp.
            conduit: The root conduit that owns the member after the stamp.
            spellbook: That root's Book (its caching posture is stamped).

        Returns:
            None.

        Raises:
            Exception: Whatever `_add_owned_conduit` raises (a cleaned store, no
                live `ReleaseManagedSpell` for a managed version).

        Threading:
            Takes the spell's lock, then the store's leaf lock, then the
            registry's leaf lock (inside `_add_owned_conduit`). The forward stamps
            run under both conduit locks and outside the Book locks, as the flip's
            stamp always has; rollbacks run with no conduit lock.
        """
        self.check_cleaned()
        spell._add_owned_conduit(
            conduit._id,
            conduit._name,
            conduit._creations,
            dynamic_environment=conduit.__dynamic_environment__,
            creation_gate_controller=conduit._creation_gate_controller,
            caching_enabled=spellbook._resolve_system_caching_enabled(),
        )

    def _restamp(self, spell: Any) -> None:
        """
        Stamp a member onto the target root, registering the rollback that undoes it.

        Purpose:
            Make the owner stamp follow the lineage both ways (2026-10-15): the
            flip stamps the active member through this, and
            `_migrate_inactive_members` every parked member that carries a stamp,
            so after a transfer each names the target's store, and after a failed
            one the store it named before.

        Contract:
            - Before stamping, registers `_stamp_owner(spell, source, source Book)`,
              so a stamp that raises midway is still stamped back.
            - Stamps the member onto the target (`_stamp_owner`).
            - For an `Existence.managed_spell_quantity` member whose version had no
              pool in the target store before the stamp, registers - even when the
              stamp raised - `_discard_composed_pool` for the pool the stamp
              composed there. A pool the target store already held is never
              registered for discard, so a rollback never touches it.
            - Rollback runs newest first, so for one member the discard runs
              before the stamp-back, and both run after the row rollbacks, which
              are registered later.

        Args:
            spell: The member whose owner moves to the target root.

        Returns:
            None.

        Raises:
            Exception: Whatever the stamp raises, after the rollback bookkeeping
                above; the caller's transfer then rolls back.
        """
        self.check_cleaned()
        target_creations = self.target_conduit._creations
        managed = spell.existence is Existence.managed_spell_quantity
        held_pool = managed and target_creations.get_managed_quantity(spell.spell_id) is not None
        self._register_rollback(
            partial(self._stamp_owner, spell, self.source_conduit, self._source_spellbook)
        )
        try:
            self._stamp_owner(spell, self.target_conduit, self._target_spellbook)
        finally:
            if managed and not held_pool:
                composed = target_creations.get_managed_quantity(spell.spell_id)
                if composed is not None:
                    self._register_rollback(
                        partial(self._discard_composed_pool, target_creations, spell.spell_id, composed)
                    )

    def _discard_composed_pool(self, creations: Any, spell_id: str, pool: Any) -> None:
        """
        Rollback step: take back the pool a stamp of this transfer composed, and clean it.

        Contract:
            - `creations.discard_managed_quantity(spell_id, pool)` removes the pool
              only while it is still that store's pool under the id, and
              unregisters it. When the store no longer holds it - a moving
              transfer replaced it with the moved pool, which the row rollback
              already took back to the source - nothing happens.
            - A removed pool is cleaned. It is empty: the lineage is disabled for
              the whole transfer, so nothing was ever leased from it, and the
              cleanup disposes nothing ("a transfer disposes nothing").

        Args:
            creations: The target store the stamp composed the pool in.
            spell_id: The managed version id.
            pool: The pool the stamp composed.

        Returns:
            None.
        """
        self.check_cleaned()
        if creations.discard_managed_quantity(spell_id, pool):
            pool.cleanup()

'''
text = text.replace(old_after, HELPERS, 1)
TRANSFER.write_text(text, encoding="utf-8")
print("applied")
