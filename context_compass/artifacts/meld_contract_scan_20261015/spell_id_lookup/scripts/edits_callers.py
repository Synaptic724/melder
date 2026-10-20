"""Edits for the callers that need an index's active spell: conduit_ward.py and transfer_of_ownership.py."""
from apply_engine import EditEngine

WARD = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
TRANSFER = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"

RESOLVE_SPELL = '''    def _resolve_spell(self) -> Any:
        """
        Normalize the caller-provided spell handle into the live spell object.

        Transfer entrypoints allow several spell identifiers for convenience,
        but the transfer machinery itself operates on the concrete spell object
        so it can inspect ownership, dependencies, creations, and lineage
        state.

        Contract:
            - A Spell object is used as given; a `SpellIndex` resolves to the spell
              it has active in the source Book.
            - A spell_id names one member and the transfer moves its whole index,
              so it resolves in two explicit steps: the spell that owns the
              spell_id (`get_spell_by_spell_id`, active or parked), then the spell
              its index has active in the source Book - the SpellIndex branch's
              read. For a spell the source owns that is the spell the spell_id
              lookup itself returned until @@SINCE@@.

        Returns:
            The resolved spell object owned by the source conduit's spellbook.
        Raises:
            RuntimeError: If the provided spell reference cannot be resolved
                into a live spell object - for a spell_id, when the source Book
                has no active spell in the index of the spell that owns it.
        """
        self.check_cleaned()
        # spell may be object, id, or SpellIndex
        if hasattr(self.spell, "spell_id"):
            return self.spell
        if isinstance(self.spell, SpellIndex):
            idx = self.spell
            book = self._source_spellbook
            with book._lock:
                return book._spells.get(idx)
        if isinstance(self.spell, str):
            # The spell_id lookup answers the member itself, a parked one included; the transfer moves
            # the whole index, so ask the source Book for the spell that index has active, as the
            # SpellIndex branch above does.
            member = self.source_conduit.get_spell_by_spell_id(self.spell, self._frame_name)
            member_index = (
                member._spell_index_unless_cleaned() if member is not None else None
            )
            if member_index is not None:
                book = self._source_spellbook
                with book._lock:
                    spell_obj = book._spells.get(member_index)
                if spell_obj is not None:
                    return spell_obj
            raise RuntimeError(
                f"Unable to resolve spell for transfer: the source conduit's Spellbook has no active "
                f"spell in the index of spell_id '{self.spell}'."
            )
        raise RuntimeError("Unable to resolve spell for transfer.")
'''

DEPS_RESOLVABLE_ON_TARGET = '''    def _deps_resolvable_on_target(self, deps: List[str]) -> bool:
        """
        Check whether the target conduit can already resolve the dependency set.

        This is the safety gate for transfers that do not move owned
        dependencies. If the target side cannot already resolve the dependency
        ids, the root lineage would arrive in a knowingly broken state.

        Contract:
            - Each dependency spell_id resolves in two explicit steps: the spell
              that owns it (`get_spell_by_spell_id`, active or parked), then the
              spell its index has active in that spell's Book. A dependency whose
              index has no active spell does not resolve - the answer the
              spell_id lookup itself gave until @@SINCE@@.
            - Any error while resolving counts as unresolvable.

        Args:
            deps: Dependency spell ids discovered during preflight.

        Returns:
            bool: `True` when every dependency id resolves on the target side,
            otherwise `False`.
        """
        self.check_cleaned()
        if not deps:
            return True
        for dep_id in deps:
            try:
                member = self.target_conduit.get_spell_by_spell_id(dep_id, self._frame_name)
                member_index = (
                    member._spell_index_unless_cleaned() if member is not None else None
                )
                if member_index is None:
                    return False
                book = member._spellbook
                with book._lock:
                    spell = book._spells.get(member_index)
                if spell is None:
                    return False
            except Exception:
                return False
        return True
'''

TRANSFER_OWNED_DEPENDENCIES = '''    def _transfer_owned_dependencies(self, deps: List[str]) -> None:
        """
        Transfer source-owned dependency lineages alongside the root lineage.

        This is the ownership-preserving dependency strategy. Each dependency is
        transferred with a nested `TransferOfOwnership`, but the recursion is
        deliberately shallow for this pass: nested transfers do not continue
        pulling their own dependencies unless a higher-level caller explicitly
        requests that behavior.

        Contract:
            - A dependency spell_id names the version the root was compiled
              against; the sub-transfer moves that version's whole index, handed
              the spell the index has active in the source Book. It is resolved in
              two explicit steps - the spell that owns the spell_id
              (`get_spell_by_spell_id`, active or parked), then its index's active
              spell - because the spell_id lookup answers the version itself since
              @@SINCE@@. A parked Spell object is never handed to a sub-transfer.
            - A dependency the source does not own, or whose index has no active
              spell, is skipped; so is one whose sub-transfer fails.

        Args:
            deps: Dependency spell ids discovered during preflight.
        """
        self.check_cleaned()
        for dep_id in deps:
            try:
                dep_member = self.source_conduit.get_spell_by_spell_id(dep_id, self._frame_name)
                dep_index = (
                    dep_member._spell_index_unless_cleaned() if dep_member is not None else None
                )
                if dep_index is None:
                    continue
                book = self._source_spellbook
                with book._lock:
                    dep_spell = book._spells.get(dep_index)
                if dep_spell is None:
                    continue
                if dep_spell._owner_conduit_id != self.source_conduit._id:
                    continue
                sub_transfer = TransferOfOwnership(
                    source_conduit=self.source_conduit,
                    target_conduit=self.target_conduit,
                    spell=dep_spell,
                    move_creations=self.move_creations,
                    include_dependencies=False,  # avoid deep recursion unless explicitly requested
                    force_unshare=self.force_unshare,
                    invalidate_after_transfer=self.invalidate_after_transfer,
                    mark_dependencies_dirty=self.mark_dependencies_dirty,
                )
                sub_transfer.execute()
                # Mark dependency lineage dirty if requested
                if self.invalidate_after_transfer:
                    if isinstance(dep_spell.spell_index, SpellIndex):
                        self._mark_lineage_dirty(dep_spell)
            except Exception:
                continue
'''


def register(engine: EditEngine) -> None:
    # The grant and ungrant check: renamed call, nothing else changes.
    engine.anchor(
        WARD,
        "            spell = self._conduit.get_spell_by_id(spell_id, aetheric_frame)\n",
        "            spell = self._conduit.get_spell_by_spell_id(spell_id, aetheric_frame)\n",
    )
    # _link_spell_dependencies' walk: explicit index step in the owner's Book.
    engine.anchor(
        WARD,
        "            dep_spell = owner_conduit.get_spell_by_id(dep_id, aetheric_frame)\n"
        "            if dep_spell is None:\n"
        "                raise RuntimeError(f\"Dependency '{dep_id}' not found in owner conduit '{owner_conduit._id}'.\")\n",
        "            # The root was compiled against `dep_id`; a notch may have parked that spell since. The\n"
        "            # dependency is granted at the version its index has active now, in two explicit steps:\n"
        "            # the spell that owns `dep_id` (the spell_id lookup answers that spell itself, a parked\n"
        "            # one included), then the spell its index has active in the owner's Book. Until @@SINCE@@\n"
        "            # the spell_id lookup returned the active spell directly.\n"
        "            dep_member = owner_conduit.get_spell_by_spell_id(dep_id, aetheric_frame)\n"
        "            dep_index = (\n"
        "                dep_member._spell_index_unless_cleaned() if dep_member is not None else None\n"
        "            )\n"
        "            dep_spell = (\n"
        "                owner_conduit._spellbook._find_spell(dep_index) if dep_index is not None else None\n"
        "            )\n"
        "            if dep_spell is None:\n"
        "                raise RuntimeError(f\"Dependency '{dep_id}' not found in owner conduit '{owner_conduit._id}'.\")\n",
    )
    # _preflight_contract_dependency_collisions' walk: the same step, so it checks the version the link grants.
    engine.anchor(
        WARD,
        "            dep_spell = owner_conduit.get_spell_by_id(dep_id, aetheric_frame)\n"
        "            if dep_spell is None:\n"
        "                raise RuntimeError(\n"
        "                    f\"Dependency '{dep_id}' not found in owner conduit '{owner_conduit._id}'.\"\n"
        "                )\n",
        "            # The same two explicit steps as `_link_spell_dependencies`' walk: the spell that owns\n"
        "            # `dep_id`, then the spell its index has active in the owner's Book - the version the link\n"
        "            # grants.\n"
        "            dep_member = owner_conduit.get_spell_by_spell_id(dep_id, aetheric_frame)\n"
        "            dep_index = (\n"
        "                dep_member._spell_index_unless_cleaned() if dep_member is not None else None\n"
        "            )\n"
        "            dep_spell = (\n"
        "                owner_conduit._spellbook._find_spell(dep_index) if dep_index is not None else None\n"
        "            )\n"
        "            if dep_spell is None:\n"
        "                raise RuntimeError(\n"
        "                    f\"Dependency '{dep_id}' not found in owner conduit '{owner_conduit._id}'.\"\n"
        "                )\n",
    )
    # The contract listing's outbound half: each granted spell_id lists the spell that owns it.
    engine.anchor(
        WARD,
        "                # Outbound: spells we have granted to the peer (live in our detail map), answered from this\n"
        "                # Book's own id maps in O(1).\n"
        "                for sid in contract._get_detail_map(self):\n"
        "                    owned_spell = spellbook.find_spell_by_id(sid)\n",
        "                # Outbound: spells we have granted to the peer (live in our detail map), each the spell that\n"
        "                # owns the granted spell_id, answered from this Book's own id maps in O(1).\n"
        "                for sid in contract._get_detail_map(self):\n"
        "                    owned_spell = spellbook.find_spell_by_spell_id(sid)\n",
    )
    # _transfer_spell_ownership: a spell_id handle resolves through its index, as the SpellIndex branch does.
    engine.anchor(
        WARD,
        "        else:\n"
        "            resolved_spell = self._conduit.get_spell_by_id(\n"
        "                spell,\n"
        "                self._conduit._aetheric_frame_name,\n"
        "            )\n",
        "        else:\n"
        "            # A spell_id names one member, and the transfer moves its whole index: resolve the spell\n"
        "            # that owns the spell_id (a parked one included), then the spell its index has active\n"
        "            # here - the SpellIndex branch above. Until @@SINCE@@ the spell_id lookup returned the\n"
        "            # active spell directly.\n"
        "            member = self._conduit.get_spell_by_spell_id(\n"
        "                spell,\n"
        "                self._conduit._aetheric_frame_name,\n"
        "            )\n"
        "            member_index = (\n"
        "                member._spell_index_unless_cleaned() if member is not None else None\n"
        "            )\n"
        "            resolved_spell = (\n"
        "                self._conduit.get_spell_by_index_id(member_index.id)\n"
        "                if member_index is not None\n"
        "                else None\n"
        "            )\n",
    )
    engine.anchor(
        WARD,
        "            spell: Spell object, spell_id, or SpellIndex to transfer.\n"
        "            target_conduit: The conduit that will become the new steward.\n"
        "            move_creations: True (the default since 0.2.8239, as on\n",
        "            spell: Spell object, spell_id, or SpellIndex to transfer; a spell_id or\n"
        "                SpellIndex resolves to the spell its index has active (the whole\n"
        "                index moves).\n"
        "            target_conduit: The conduit that will become the new steward.\n"
        "            move_creations: True (the default since 0.2.8239, as on\n",
    )
    engine.block(TRANSFER, "TransferOfOwnership._resolve_spell",
                 "6d6042fa2be045b699db49c36e985a904325cd516e675fdba334302841de3b47", RESOLVE_SPELL)
    engine.block(TRANSFER, "TransferOfOwnership._deps_resolvable_on_target",
                 "5ef4a93fb22a72bc91b1b80f19e791024ed91033b14a39c7bac6d1b8576fb4b8", DEPS_RESOLVABLE_ON_TARGET)
    engine.block(TRANSFER, "TransferOfOwnership._transfer_owned_dependencies",
                 "4665bdd4c9d6e84aac4869c8b4dfbee0483d1c2a59f18ef873f26e6a68c7feef", TRANSFER_OWNED_DEPENDENCIES)
    # _dirty_dependencies marks the spell's index, which every member shares: renamed call only.
    engine.anchor(
        TRANSFER,
        "                dep_spell = self.source_conduit.get_spell_by_id(dep_id, self._frame_name)\n",
        "                dep_spell = self.source_conduit.get_spell_by_spell_id(dep_id, self._frame_name)\n",
    )
