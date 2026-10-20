"""Edits for the two lookups themselves: spellbook.py and conduit.py (fix #1, owner 2026-10-17)."""
from apply_engine import EditEngine

SPELLBOOK = "src/melder/aether/spellbook/spellbook.py"
CONDUIT = "src/melder/aether/conduit/conduit.py"

FIND_SPELL_BY_SPELL_ID = '''    def find_spell_by_spell_id(self, spell_id: str) -> Optional[Spell]:
        """
        Public API

        Return the spell this Spellbook owns under `spell_id`, or None.

        Purpose:
            Look a spell up by its spell_id - the SHA256 `bind` and
            `bind_inactive` return - and answer with exactly the spell bound
            under it, active or parked. A spell_id and a SpellIndex are separate
            things (owner ruling, 2026-10-17): the spell an index has active is a
            lookup by the index's id (`get_spell_by_index_id`), never the answer
            to a spell_id.

        Contract:
            - Returns the Spell whose `spell_id` is the argument: the active
              version from `_spells_by_id`, else the parked version from
              `_inactive_spells`. Never another version of its index, and never
              the spell the index has active in its place.
            - Searches THIS spellbook's registry only. Spells reachable through
              contracted conduits or through other books in the frame are not
              consulted; `inspect_spell` is the frame-wide search.
            - Answers from the Book's two id maps and never walks a live map.
              Every owned version is a key of one of them: bind publishes an
              active version to `_spells_by_id`; `bind_inactive` and a notch
              park a version in `_inactive_spells`; index moves and parked
              disposal keep that map in step; an ownership transfer migrates
              the whole lineage.
            - O(1): at most two dict reads.
            - Returns None on a miss. This is deliberately unlike the
              `find_spell_index` / `find_spell_key` siblings, which raise on a
              miss; a None here means "this Book owns no spell under this
              spell_id", not "lookup failed".
            - Pure lookup: creates, registers, and mutates nothing.
            - Until @@SINCE@@ this was `find_spell_by_id`, which answered a
              parked spell_id with the spell its index had active.

        Threading:
            Does not acquire `self._lock`, by design: conjure holds that lock
            while it waits on phase workers and runs conduit hooks, and both can
            call this lookup from another thread. Each map read is one atomic
            dict operation and no live map is iterated, so a concurrent bind,
            removal, notch, index move or transfer can never make this raise or
            skip a registered spell. A notch, and a transfer between its flip
            and its inactive-member migration, move spell_ids between the maps
            in steps; a lookup that lands between two steps answers None for
            that spell_id, so answers are not linearized against writers.
            The returned `Spell` is a borrowed reference, not a lease: a
            concurrent removal, notch or transfer can retire or move it after
            this returns. A parked version disposed while the lookup runs is
            returned as it was read, or missed once its spell_id has left the
            map; the lookup never raises for it.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Args:
            spell_id:
                The spell_id of the spell, active or parked.

        Returns:
            Optional[Spell]:
                The spell bound under `spell_id`, or None when this Book owns no
                spell under it.

        Raises:
            RuntimeError: If the spellbook has already been cleaned.
        """
        self.check_cleaned()
        # The active version: one atomic read of the active spell_id map.
        spell = self._spells_by_id.get(spell_id)
        if spell is not None:
            return spell
        # A parked version - staged by bind_inactive or parked by a notch - is the answer itself. Its
        # index is not consulted: the spell the index has active is a lookup by index id
        # (get_spell_by_index_id), not by spell_id. Until @@SINCE@@ this branch returned that spell.
        return self._inactive_spells.get(spell_id)
'''

GET_SPELL_BY_ID_VIA_AETHER = '''    def _get_spell_by_id_via_aether(
            self,
            spell_id: str,
            aetheric_frame_name: str = "default",
    ) -> Spell | None:
        """
        Internal

        Resolve a spell by its spell_id through Aether ownership lookup.

        Contract:
            - Two steps: Aether names the conduit that owns `spell_id`
              (`_get_conduit_by_spell_id`), and that conduit's Spellbook answers
              with the spell bound under it, active or parked
              (`Spellbook.find_spell_by_spell_id`) - never the spell its index has
              active in its place.

        Args:
            spell_id:
                The spell_id (SHA256) to resolve, active or parked.
            aetheric_frame_name:
                Frame name to search. `"default"` is normalized to this
                Spellbook's current frame.

        Returns:
            Optional[Spell]:
                The spell that owns `spell_id` in the owning conduit's Spellbook,
                or None when that Spellbook holds no spell under it (it moved or
                left between the two steps).

        Raises:
            ValueError: If no conduit in the frame claims the id, or the frame does not exist
                (`_get_conduit_by_spell_id`).
            RuntimeError: If the owning conduit has no spellbook.
        """
        owner = self._get_conduit_by_spell_id(spell_id, aetheric_frame_name)
        if owner is None:
            return None
        owner_spellbook = owner._spellbook
        if owner_spellbook is None:
            raise RuntimeError("Owner conduit has no spellbook.")
        return owner_spellbook.find_spell_by_spell_id(spell_id)
'''

GET_SPELL_BY_SPELL_ID = '''    def get_spell_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[Spell]:
        """
        Public API

        Return the spell that owns `spell_id` - the spell_id `bind` or
        `bind_inactive` returned - from the Spellbook of the conduit that owns it.

        The method:
          1) Uses Aether to locate the conduit that owns the spell_id.
          2) Looks the spell_id up in that conduit's Spellbook
             (`Spellbook.find_spell_by_spell_id`): the spell bound under it, active or
             parked.
          3) Returns that Spell instance.

        Contract:
            - A lookup by spell_id returns the spell that owns the spell_id, never the
              spell its SpellIndex has active in its place; that is a lookup by the
              index's id (`get_spell_by_index_id`). A spell_id and a SpellIndex are
              separate things (owner ruling, 2026-10-17). Until @@SINCE@@ this method was
              `get_spell_by_id`, and a parked spell_id answered with the spell its index
              had active.
            - Resolves via the spellbook's Aether-wide lookup, so the returned spell may
              belong to a different conduit; ownership and permission are separate
              questions from resolvability.
            - Unlike its siblings, this one does NOT hold the conduit lock across the
              lookup.

        Args:
            spell_id (str): The spell_id of the spell (SHA256), active or parked.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[Spell]: The spell that owns `spell_id`, or None when the owner's
            Spellbook holds no spell under it (it moved or left between the frame lookup
            and the Book's).

        Raises:
            RuntimeError: If the Conduit is cleaned, or the owning conduit has no spellbook.
            ValueError: If no conduit in the frame claims the id - unknown or removed, bound in
                another frame, its owner cleaned, or a lineage between owners while an
                ownership transfer runs - or the frame does not exist. A miss raises, as the
                `get_*` lookups do (owner decision 2026-10-11); until 0.2.8230 this docstring
                promised None.
        """
        self.check_cleaned()
        return self._spellbook._get_spell_by_id_via_aether(
            spell_id,
            aetheric_frame_name,
        )
'''

GET_SPELL_PERMISSIONS = '''    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its spell_id, **within this conduit**.
        This returns the access level ("read", "create", "block") defined when the
        spell was bound.

        Contract:
            - LOCAL ONLY. It resolves through THIS conduit's spellbook
              (`Spellbook.find_spell_by_spell_id`), so a spell reachable by contract from a
              peer conduit is NOT found here.
            - EXACT: the spell_id names one spell, active or parked, and the answer is the
              permissions THAT spell was bound with. Until @@SINCE@@ it matched by lineage,
              and a parked spell_id answered the permissions of the spell its index had
              active.
            - Lock-free (0.2.8230): the lookup answers from the Book's id maps instead of
              walking its live index map under the conduit lock, which a concurrent bind
              or removal could resize mid-walk.
            - NEVER RETURNS None despite the `Optional[str]` annotation: a miss RAISES
              `RuntimeError`. Treat the annotation as wrong and the Raises block as
              authoritative.
            - Returns the permission enum's `.name` STRING, not the enum member.

        Args:
            spell_id (str): The spell_id (SHA256) of the spell, active or parked.

        Returns:
            Optional[str]: The permissions the spell was bound with.

        Raises:
            RuntimeError: If the spell with the given ID is not found in the spellbook.
        """
        self.check_cleaned()
        # Look the spell_id up in the Book's id maps: O(1), the exact spell, and no walk of the live
        # index map.
        target_spell: Optional[Spell] = self._spellbook.find_spell_by_spell_id(spell_id)

        if target_spell is not None:
            perms = target_spell.permissions.name
            return perms

        self._logger.error(f"Spell with ID {spell_id} not found", "get_spell_permissions")
        raise RuntimeError(f"Spell with ID {spell_id} not found in the spellbook.")
'''

RESOLVE_TRANSFER_SPELL = '''    def _resolve_transfer_spell(
            self,
            *,
            spell_id: Optional[str],
            spell_index_id: Optional[str],
    ) -> "Spell":
        """
        Resolve the live spell being transferred from this (source) conduit.

        Purpose:
            Footprint discovery needs the live spell to run the read-only
            transfer preflight and to read its binding key. The source conduit
            owns the spell, so it is resolved directly here (domain side) rather
            than reached for by the DevOps strategy.

        Contract:
            - A transfer moves the whole index (`transfer_spell_ownership`), so the
              live spell is the one the index has active. A `spell_index_id`
              resolves through `get_spell_by_index_id`. A `spell_id` names one
              member and resolves in two explicit steps: the spell that owns it
              (`get_spell_by_spell_id`, active or parked), then the spell that
              member's index has active here (`get_spell_by_index_id`). For a spell
              this conduit owns that is the spell the spell_id lookup itself
              returned until @@SINCE@@.

        Args:
            spell_id: The spell_id of a member of the index, if available.
            spell_index_id: Stable spell-index id, if available.

        Returns:
            Spell: The resolved live spell owned by this conduit.

        Raises:
            RuntimeError: If neither identifier resolves a local spell.
            ValueError: From `get_spell_by_spell_id`, when no conduit in the frame claims
                the spell_id.
        """
        resolved: Optional[Spell] = None
        if isinstance(spell_index_id, str) and spell_index_id.strip():
            resolved = self.get_spell_by_index_id(spell_index_id)
        if resolved is None and isinstance(spell_id, str) and spell_id.strip():
            # The spell_id lookup answers the member itself, a parked one included; the transfer
            # needs the spell its index has active, so ask the index, as the branch above does.
            member = self.get_spell_by_spell_id(spell_id, self._aetheric_frame_name)
            member_index = (
                member._spell_index_unless_cleaned() if member is not None else None
            )
            if member_index is not None:
                resolved = self.get_spell_by_index_id(member_index.id)
        if resolved is None:
            raise RuntimeError(
                "[CONDUIT] Transfer-ownership could not resolve the source spell on this conduit."
            )
        return resolved
'''


def register(engine: EditEngine) -> None:
    engine.block(SPELLBOOK, "Spellbook.find_spell_by_id",
                 "dd65e05c59aec9bb8a94bc3b7a037290bea528cdf844515548a2d7c29b6764a0", FIND_SPELL_BY_SPELL_ID)
    engine.block(SPELLBOOK, "Spellbook._get_spell_by_id_via_aether",
                 "fd26ac56583c07679000bd6f47e91bd492b98329b825368a164e41765303e5de", GET_SPELL_BY_ID_VIA_AETHER)
    engine.block(CONDUIT, "Conduit.get_spell_by_id",
                 "8b79dc3da47815da01880a64641a5ee4ec100c7c479e1303dcba1b47faee6a49", GET_SPELL_BY_SPELL_ID)
    engine.block(CONDUIT, "Conduit.get_spell_permissions",
                 "2280220f8cd16929a7dd9e920821f46ac29c6f5186a0ac47a58ff720e83bfd45", GET_SPELL_PERMISSIONS)
    engine.block(CONDUIT, "Conduit._resolve_transfer_spell",
                 "b0446fc942bba1a466209cc3e6e3e06a9a62f6f81bb8806e0df7ce53b58cb758", RESOLVE_TRANSFER_SPELL)
    # notch_spell's contract.
    engine.anchor(
        CONDUIT,
        "              this call to the exact spell this conduit's Spellbook owns, active or parked.\n"
        "              `get_spell_by_id` / `find_spell_by_id` answer a parked spell_id with the\n"
        "              index's ACTIVE spell, so a parked spell is named by its spell_id here.\n",
        "              this call to the exact spell this conduit's Spellbook owns, active or parked -\n"
        "              the spell `get_spell_by_spell_id` returns for it (until @@SINCE@@\n"
        "              `get_spell_by_id` answered a parked spell_id with the index's ACTIVE spell).\n",
    )
    # _resolve_notch_target's contract.
    engine.anchor(
        CONDUIT,
        "              owning Spellbook's `_get_owned_spell` - the exact owned spell, active or\n"
        "              parked - never through `find_spell_by_id`, which answers a parked spell_id\n"
        "              with the index's active spell.\n",
        "              owning Spellbook's `_get_owned_spell` - the exact owned spell, active or\n"
        "              parked, read under the Book lock; `find_spell_by_spell_id` gives the same\n"
        "              answer without the lock (until @@SINCE@@ its predecessor `find_spell_by_id`\n"
        "              answered a parked spell_id with the index's active spell).\n",
    )
    # _owned_spell_by_id's contract.
    engine.anchor(
        CONDUIT,
        "            - Resolves through the Spellbook's `_get_owned_spell` - the exact owned spell -\n"
        "              never through `find_spell_by_id`, which answers a parked spell_id with the\n"
        "              index's active spell.\n",
        "            - Resolves through the Spellbook's `_get_owned_spell` - the exact owned spell,\n"
        "              read under the Book lock; `find_spell_by_spell_id` gives the same answer\n"
        "              without the lock (until @@SINCE@@ its predecessor `find_spell_by_id` answered a\n"
        "              parked spell_id with the index's active spell).\n",
    )
    # add_to_spell_index's contract.
    engine.anchor(
        CONDUIT,
        "              this call to the exact spell this conduit's Spellbook owns, active or parked;\n"
        "              `get_spell_by_id` / `find_spell_by_id` answer a parked spell_id with the\n"
        "              index's active spell, so a parked spell is named by its spell_id here.\n",
        "              this call to the exact spell this conduit's Spellbook owns, active or parked -\n"
        "              the spell `get_spell_by_spell_id` returns for it (until @@SINCE@@\n"
        "              `get_spell_by_id` answered a parked spell_id with the index's active spell).\n",
    )
    # The notch target's refusal names the renamed lookup in its remedy.
    engine.anchor(
        CONDUIT,
        '                f"passed. Pass its own index - conduit.get_spell_by_id({spell_id!r})"\n',
        '                f"passed. Pass its own index - conduit.get_spell_by_spell_id({spell_id!r})"\n',
    )
