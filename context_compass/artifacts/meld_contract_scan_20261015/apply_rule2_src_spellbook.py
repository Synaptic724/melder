"""Rule 2 / D2 source change: the Book's contracted-map mutators mark consumers; bind and notch feed the walk.

contract_recheck_on_notch_2026_10_16, component_patch_borrower_contracted_maps and component_patch_dependent_walk
(melder_1). usage: python <this script> <tree root> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]
REL = "src/melder/aether/spellbook/spellbook.py"

DEACTIVATE_DOC_OLD = """            - Leaves `_contracted_spell_ids[conduit_id]` untouched: borrowed
              existence is kept across the inactive window.
            - Does not touch the SpellIndex or the framewide lookup.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell (Spell): The active borrowed spell to park.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell is not the active contracted spell for
                its id under `conduit_id`.

        Threading:
            - Acquires the Spellbook lock; the admitting transaction serializes
              the wider operation.
        \"\"\"
"""
DEACTIVATE_DOC_NEW = """            - Leaves `_contracted_spell_ids[conduit_id]` untouched: borrowed
              existence is kept across the inactive window.
            - Does not touch the SpellIndex or the framewide lookup.
            - Once the Book has conjured, marks the Book's SpellContract
              consumers of the copy's key for revalidation after releasing the
              lock (`_mark_contract_dependents_dirty`; rule 2 of
              contract_recheck_on_notch_2026_10_16): their next meld rechecks
              the provider. Mark only.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell (Spell): The active borrowed spell to park.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell is not the active contracted spell for
                its id under `conduit_id`.
            Exception: Whatever the registry's mark raises, logged; the park
                stays published.

        Threading:
            - Acquires the Spellbook lock; the admitting transaction serializes
              the wider operation. The consumer mark runs after the lock is
              released and takes only the registry lock.
        \"\"\"
"""
DEACTIVATE_CODE_OLD = """            parked = self._inactive_contracted_spells.get(conduit_id)
            if parked is None:
                parked = {}
                self._inactive_contracted_spells[conduit_id] = parked
            parked[spell_id] = spell

    def _reactivate_contracted_spell(self, conduit_id: str, spell: Spell) -> None:
"""
DEACTIVATE_CODE_NEW = """            parked = self._inactive_contracted_spells.get(conduit_id)
            if parked is None:
                parked = {}
                self._inactive_contracted_spells[conduit_id] = parked
            parked[spell_id] = spell
            conjured = self._conjured
        # Rule 2: the copy this key's consumers resolved is parked - they recheck at their next meld.
        if conjured:
            self._mark_contract_dependents_dirty({binding_key})

    def _reactivate_contracted_spell(self, conduit_id: str, spell: Spell) -> None:
"""

REACTIVATE_DOC_OLD = """            - Assumes the conduit's contract maps are live (park never drops the
              conduit sub-dicts); does not touch the SpellIndex or framewide
              lookup.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell (Spell): The parked borrowed spell to reactivate.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell is not the parked contracted spell for
                its id under `conduit_id`.

        Threading:
            - Acquires the Spellbook lock; the admitting transaction serializes
              the wider operation.
        \"\"\"
"""
REACTIVATE_DOC_NEW = """            - Assumes the conduit's contract maps are live (park never drops the
              conduit sub-dicts); does not touch the SpellIndex or framewide
              lookup.
            - Once the Book has conjured, marks the Book's SpellContract
              consumers of the copy's key for revalidation after releasing the
              lock (`_mark_contract_dependents_dirty`; rule 2): their next meld
              builds against the copy now active. Mark only.

        Args:
            conduit_id (str): Peer conduit id that owns the contract.
            spell (Spell): The parked borrowed spell to reactivate.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell is not the parked contracted spell for
                its id under `conduit_id`.
            Exception: Whatever the registry's mark raises, logged; the
                reactivation stays published.

        Threading:
            - Acquires the Spellbook lock; the admitting transaction serializes
              the wider operation. The consumer mark runs after the lock is
              released and takes only the registry lock.
        \"\"\"
"""
REACTIVATE_CODE_OLD = """            parked_map.pop(spell_id, None)
            self._contracted_spells[conduit_id][spell_index] = spell
            self._lookup_contracted_spells[conduit_id][binding_key] = spell_index
            self._contracted_spells_by_id[conduit_id][spell_id] = spell
            self._spell_id_pool[spell_id] = spell
"""
REACTIVATE_CODE_NEW = """            parked_map.pop(spell_id, None)
            self._contracted_spells[conduit_id][spell_index] = spell
            self._lookup_contracted_spells[conduit_id][binding_key] = spell_index
            self._contracted_spells_by_id[conduit_id][spell_id] = spell
            self._spell_id_pool[spell_id] = spell
            conjured = self._conjured
        # Rule 2: this key's consumers resolve the reactivated copy now - they rebuild at their next meld.
        if conjured:
            self._mark_contract_dependents_dirty({binding_key})
"""

ADD_DOC_OLD = """        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            spell (Spell): The spell object to add.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        Raises:
            RuntimeError: If the contracted spell's binding key collides with existing bindings.
        \"\"\"
"""
ADD_DOC_NEW = """        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Once the Book has conjured, the Book's SpellContract consumers of the
        copy's key are marked for revalidation after the Book lock is released
        (`_mark_contract_dependents_dirty`; rule 2 of
        contract_recheck_on_notch_2026_10_16), so their next meld builds against
        the new copy; the mark walks on to what depends on them.

        Args:
            spell (Spell): The spell object to add.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        Raises:
            RuntimeError: If the contracted spell's binding key collides with existing bindings.
            Exception: Whatever a registry mark raises, logged; the added copy stays published.
        \"\"\"
"""
ADD_CODE_OLD = """        if should_mark and frame_key:
            self._mark_collection_dependents_dirty({frame_key})
        self._try_update_staged_contract_keys(conduit_id)
"""
ADD_CODE_NEW = """        if should_mark and frame_key:
            self._mark_collection_dependents_dirty({frame_key})
        if should_mark:
            # Rule 2: a new active copy for this key - its consumers rebuild against it at their next meld.
            self._mark_contract_dependents_dirty({spell_key})
        self._try_update_staged_contract_keys(conduit_id)
"""

REMOVE_DOC_OLD = """        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            spell_id (str): The version SHA of the spell to remove.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        \"\"\"

        removed_spell = None
        with self._lock:
"""
REMOVE_DOC_NEW = """        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Removing an ACTIVE copy (an uncontract, an index unlink or destroy, a
        version leaving its index) marks the Book's SpellContract consumers of
        its key for revalidation after the Book lock is released, once the Book
        has conjured (`_mark_contract_dependents_dirty`; rule 2): their next meld
        fails with the first meld's missing-provider report. A parked copy is
        dropped without a mark - no consumer resolves it.

        Args:
            spell_id (str): The version SHA of the spell to remove.
            conduit_id (str): The ID of the peer conduit the spell was contracted from.
        Raises:
            RuntimeError: If the conduit has no contracted maps or holds no copy of `spell_id`.
            Exception: Whatever the registry's mark raises, logged; the removal stays published.
        \"\"\"

        removed_spell = None
        removed_key: Optional[tuple[str, str]] = None
        conjured = False
        with self._lock:
"""
REMOVE_CODE_OLD = """                else:
                    conduit_spell_ids.discard(spell_id)
                removed_spell = spell
        self._try_update_staged_contract_keys(conduit_id)
        if removed_spell is not None and self._conjured and self._conduit is not None:
            self._unregister_spell_with_risk_manager(self._conduit._id, removed_spell)
"""
REMOVE_CODE_NEW = """                else:
                    conduit_spell_ids.discard(spell_id)
                removed_spell = spell
                removed_key = key
                conjured = self._conjured
        # Rule 2: the active copy for this key is gone - its consumers recheck (and fail) at their next meld.
        if removed_key is not None and conjured:
            self._mark_contract_dependents_dirty({removed_key})
        self._try_update_staged_contract_keys(conduit_id)
        if removed_spell is not None and self._conjured and self._conduit is not None:
            self._unregister_spell_with_risk_manager(self._conduit._id, removed_spell)
"""

CLEAR_DOC_OLD = """        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Args:
            conduit_id (str): The ID of the peer conduit whose contracted spells are to be cleared
        \"\"\"

        removed_spells: list[Spell] = []
        with self._lock:
"""
CLEAR_DOC_NEW = """        When a link transaction is active, this also refreshes staged contract
        keys for the peer conduit so change-control commit hooks can observe
        the updated contract scope.

        Once the Book has conjured, the Book's SpellContract consumers of every
        active copy's key are marked for revalidation after the Book lock is
        released (`_mark_contract_dependents_dirty`; rule 2) - the keys the
        copies were filed under (`_make_spell_key`, as `_add_contracted_spell`
        files them), so the mark names exactly the keys the clear drops.

        Args:
            conduit_id (str): The ID of the peer conduit whose contracted spells are to be cleared
        Raises:
            RuntimeError: If the conduit has no contracted maps.
            Exception: Whatever the registry's mark raises, logged; the clear stays published.
        \"\"\"

        removed_spells: list[Spell] = []
        cleared_keys: set[tuple[str, str]] = set()
        conjured = False
        with self._lock:
"""
CLEAR_CODE_OLD = """            spell_map = self._contracted_spells[conduit_id]
            removed_spells = list(spell_map.values())
            for spell in spell_map.values():
"""
CLEAR_CODE_NEW = """            spell_map = self._contracted_spells[conduit_id]
            removed_spells = list(spell_map.values())
            cleared_keys = {
                self._make_spell_key(spell.spellframe, spell.spell_name, spell.binding_name)
                for spell in removed_spells
            }
            conjured = self._conjured
            for spell in spell_map.values():
"""
CLEAR_TAIL_OLD = """            parked = self._inactive_contracted_spells.get(conduit_id)
            if parked is not None:
                parked.clear()
        self._try_update_staged_contract_keys(conduit_id)
"""
CLEAR_TAIL_NEW = """            parked = self._inactive_contracted_spells.get(conduit_id)
            if parked is not None:
                parked.clear()
        # Rule 2: every active copy this clear dropped leaves its key's consumers without a provider.
        if cleared_keys and conjured:
            self._mark_contract_dependents_dirty(cleared_keys)
        self._try_update_staged_contract_keys(conduit_id)
"""

MARK_OLD = """            self._logger.error(
                f"Failed to mark collection dependents dirty: {e}",
                "_mark_collection_dependents_dirty",
                exc_info=True,
            )
            raise

"""
MARK_NEW = '''            self._logger.error(
                f"Failed to mark collection dependents dirty: {e}",
                "_mark_collection_dependents_dirty",
                exc_info=True,
            )
            raise

    def _mark_contract_dependents_dirty(self, contract_keys: set[tuple[str, str]]) -> None:
        """
        Internal

        Mark this Book's SpellContract consumers of `contract_keys` for revalidation after a contracted copy changed.

        Purpose:
            Rule 2 of contract_recheck_on_notch_2026_10_16: a satisfied SpellContract is not checked on every meld.
            Instead every change of an active contracted (borrowed) copy - a lender's notch and notch back, a parked
            or reactivated version-anchored copy, an add, a removal, an index unlink or destroy, a contract clear -
            marks the consumers of the copy's key, so their next meld reruns phases 1-4 (Phase 4 rechecks the
            provider) and rebuilds against the copy now active, or fails with the first meld's error. Mark only:
            objects already built keep their provider.

        Contract:
            - A no-op for no keys. Otherwise one `SpellSystemStates.mark_contract_dependents_dirty` call for this
              Book, which gates the consumers (`contract_unvalidated`) and walks on to what depends on them.
            - The five contracted-map mutators call it after releasing the Book lock, and only once the Book has
              conjured: before conjure, conjure runs phases 1-4 for every spell anyway.

        Args:
            contract_keys: The normalized `(frame_key, binding_key)` keys of the copies that changed.

        Returns:
            None.

        Raises:
            RuntimeError: If the spell system state is unavailable.
            Exception: Whatever the registry raises, after logging it; the map change the mark follows stays
                published.

        Threading:
            Called with the Book lock free. The registry lock it takes is never held while a Book, ward, contract
            or conduit lock is taken (registry -> state -> RiskManager), so no lock-order cycle can close.
        """
        if not contract_keys:
            return
        if self._spell_system_states is None:
            self._logger.error("SpellSystemStates unavailable for revalidation", "_mark_contract_dependents_dirty")
            raise RuntimeError("SpellSystemStates unavailable for revalidation.")
        try:
            self._spell_system_states.mark_contract_dependents_dirty(
                spellbook_id=self._id,
                contract_keys=contract_keys,
            )
        except Exception as e:
            self._logger.error(
                f"Failed to mark contract dependents dirty: {e}",
                "_mark_contract_dependents_dirty",
                exc_info=True,
            )
            raise

'''

BIND_OLD = """                self._spell_system_states.register_index(
                    spell_index=new_spell.spell_index,
                    owner_spellbook_id=self._id,
                    resolvable=new_spell.resolvable,
                )
"""
BIND_NEW = """                self._spell_system_states.register_index(
                    spell_index=new_spell.spell_index,
                    owner_spellbook_id=self._id,
                    resolvable=new_spell.resolvable,
                    binding_key=new_spell._key,
                )
"""

NOTCH_DOC_OLD = """            5. Re-register the index so it is structurally gated + dirty; meld-time
               revalidation recompiles lazily on next resolve.

        Contracted borrowers are NOT yet fanned out here (owner-side only); a notch
        on a shared index does not yet update borrowers' contracted maps -- that is
        the next slice (cross-conduit fan-out under the same seal).
"""
NOTCH_DOC_NEW = """            5. Re-register the index so it is structurally gated + dirty; meld-time
               revalidation recompiles lazily on next resolve.
            6. Mark every lineage downstream of this one for revalidation
               (`SpellSystemStates.mark_dependents_for_revalidation`; D2 of
               contract_recheck_on_notch_2026_10_16): its dependents by registry
               edge, in any Book, and the SpellContract consumers of its binding
               key, transitively. Mark only: each rechecks and rebuilds at its next
               meld; objects already built keep what they were built with.

        Borrowers are updated by the owning Conduit after the transaction window, not
        here: `Conduit._deactivate_borrowed_spell` parks every linked peer's copy of the
        outgoing version and `ConduitWard._emit_index_notch` moves index-link
        subscriptions to the incoming one; the borrower Book's contracted-map mutators
        mark its consumers (rule 2).
"""
NOTCH_CODE_OLD = """        self._spell_system_states.register_index(
            spell_index=spell_index,
            owner_spellbook_id=self._id,
            resolvable=spell.resolvable,
        )
"""
NOTCH_CODE_NEW = """        self._spell_system_states.register_index(
            spell_index=spell_index,
            owner_spellbook_id=self._id,
            resolvable=spell.resolvable,
            binding_key=spell._key,
        )
        # D2: everything downstream of the notched lineage - its dependents by registry edge, in any Book, and the
        # SpellContract consumers of its binding key - revalidates at its next meld (mark only).
        self._spell_system_states.mark_dependents_for_revalidation((spell_index.id,))
"""
NOTCH_COMMENT_OLD = """        # Mark the lineage structurally changed so dependents revalidate, and clear
        # the promoted member's stale CreationContext. invalidate_spell also sets
"""
NOTCH_COMMENT_NEW = """        # Mark the promoted lineage structurally changed (the walk above marked its
        # dependents) and clear its stale CreationContext. invalidate_spell also sets
"""

STEPS = [
    ("one", DEACTIVATE_DOC_OLD, DEACTIVATE_DOC_NEW, ""),
    ("one", DEACTIVATE_CODE_OLD, DEACTIVATE_CODE_NEW, ""),
    ("one", REACTIVATE_DOC_OLD, REACTIVATE_DOC_NEW, ""),
    ("one", REACTIVATE_CODE_OLD, REACTIVATE_CODE_NEW, ""),
    ("one", ADD_DOC_OLD, ADD_DOC_NEW, ""),
    ("one", ADD_CODE_OLD, ADD_CODE_NEW, ""),
    ("one", REMOVE_DOC_OLD, REMOVE_DOC_NEW, ""),
    ("one", REMOVE_CODE_OLD, REMOVE_CODE_NEW, ""),
    ("one", CLEAR_DOC_OLD, CLEAR_DOC_NEW, ""),
    ("one", CLEAR_CODE_OLD, CLEAR_CODE_NEW, ""),
    ("one", CLEAR_TAIL_OLD, CLEAR_TAIL_NEW, ""),
    ("one", MARK_OLD, MARK_NEW, ""),
    ("one", BIND_OLD, BIND_NEW, ""),
    ("one", NOTCH_DOC_OLD, NOTCH_DOC_NEW, ""),
    ("one", NOTCH_CODE_OLD, NOTCH_CODE_NEW, ""),
    ("one", NOTCH_COMMENT_OLD, NOTCH_COMMENT_NEW, ""),
]

apply(ROOT, REL, STEPS, CHECK)
