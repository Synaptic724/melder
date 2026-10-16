"""Apply the public notch target to src/melder/aether/conduit/conduit.py (TASK-2026-10-16-public_notch_target_...).

Replaces the whole `notch_spell` method - from its `def` line to the line before `def add_to_spell_index` - with the
new method and its two helpers, after checking the old block is the 0.2.8248 text (line count and key lines).

Run from the repository root:  python context_compass/artifacts/public_notch_target_20261016/scripts/apply_notch_target.py
"""
import pathlib

PATH = pathlib.Path("src/melder/aether/conduit/conduit.py")

NEW_BLOCK = '''    def notch_spell(
            self,
            *,
            spell_index: Any,
            spell: Any = None,
            spell_id: Optional[str] = None,
            change_reason: SpellStateChangeReason = SpellStateChangeReason.selected_different_spell,
    ) -> Any:
        """
        Public API

        Conduit facade for a SpellIndex notch: make one version of an index its
        active (resolvable) member. This conduit admits the `notch` change-control
        transaction and the owning Spellbook makes the switch inside the held window.

        Purpose:
            Promote a staged version - the notch in stage -> notch -> meld - or go back
            to a parked one. Name the version by `spell_id`, the id `bind` or
            `bind_inactive` returned, or by its Spell object.

        Contract:
            - DYNAMIC MODE ONLY; refused on an automatic frame.
            - EXACTLY ONE TARGET: `spell_id` or `spell`. An id is resolved inside this
              call to the exact version this conduit's Spellbook owns, active or parked.
              `get_spell_by_id` / `find_spell_by_id` answer a parked id with the index's
              ACTIVE spell, so a parked version is named by its id here.
            - THE TARGET IS CHECKED before the transaction starts and again inside the
              held window: it must be a version this conduit's Spellbook owns and a member
              of `spell_index`. The second check runs under the notch seal (the Spellbook
              and its conduits claimed EXCLUSIVE), so no other index operation can move the
              target between that check and the switch. A refused call changes nothing.
            - REPOINTS THE ACTIVE MEMBER of an existing index - it does not create, bind or
              remove anything. The previous member stays in the lineage, parked, and a
              notch back by its id restores it.
            - Notching to the index's active version is a no-op: nothing moves and no
              borrower is touched.
            - After the window, every linked peer parks its copy of the outgoing version and
              index-link borrowers move to the new one, which they build at their next meld.
            - The default `change_reason` is `selected_different_spell`, which records
              an ordinary selection rather than a mutation. Pass a mutation reason
              explicitly when that is what happened, because this default will
              otherwise misattribute the change in the state history.
            - Admitted as a `notch` change-control transaction by this conduit, so it
              participates in change control rather than bypassing it.

        Args:
            spell_index: The SpellIndex whose active member is switched.
            spell: The version to make active, as a Spell object; exclusive with `spell_id`.
            spell_id: The id of the version to make active (as `bind` or `bind_inactive`
                returned it); exclusive with `spell`.
            change_reason: Why the active member was repointed; defaults to
                `selected_different_spell` (general selection, not a mutation).

        Returns:
            Any: The now-active Spell (the owning Spellbook's notch result).

        Raises:
            ValueError: When both or neither of `spell` and `spell_id` are given; when the
                version is not owned by this conduit's Spellbook (an id nothing here bound,
                a disposed version, another Book's version); when it belongs to another
                SpellIndex.
            TypeError: When `spell_id` is not a string, or a string is given as `spell`.
            RuntimeError: If the Conduit is cleaned, the frame is not dynamic, or the
                Conduit has no owning Spellbook; and whatever the transaction or the
                switch raises.

        Example:
            id_v2 = conduit.bind_inactive(spell=ReportV2, spell_index=index, existence="unique")
            conduit.notch_spell(spell_index=index, spell_id=id_v2)
            conduit.meld(spell_id=id_v2)    # a ReportV2
        """
        self.check_cleaned()
        if not self.__dynamic_environment__:
            self._logger.error(
                "notch_spell called in non-dynamic env",
                "notch_spell",
            )
            raise RuntimeError(
                "Dynamic environment is not enabled. SpellIndex notch requires dynamic mode."
            )
        if self._spellbook is None:
            raise RuntimeError("[CONDUIT] No owning Spellbook for notch_spell.")
        # Resolve the target - by id or by object - and check it before anything starts.
        # The resolved Spell is rebound to `spell`, so everything below reads one object
        # whichever form named it.
        spell = self._resolve_notch_target(spell_index=spell_index, spell=spell, spell_id=spell_id)
        mediator = self._get_required_transaction_mediator()
        metadata: Dict[str, Any] = {
            "origin_surface": "conduit.notch_spell",
            "spellbook_id": self._spellbook._id,
            "owner_conduit_id": self._id,
            "spell_index_id": spell_index._id,
            "spell_id": spell.spell_id,
            "binding_key": spell._key,
            # Runtime-freeze facade (patch notch_conduit_gate_freeze_2026_07_12,
            # unelect precedent): the notch strategy's on_start quiesces the
            # sealed conduits' CreationGates through this DevOps facade so no
            # in-flight meld/validator can straddle the active-member repoint;
            # on_end reopens on every exit path via root finalize.
            "conduit_lineage_gate_ops": (
                self._aetheric_frame.dev_ops_manager.conduit_lineage_gate_ops
            ),
        }
        # The index's current active member is the outgoing spell. The conduit
        # admits the notch (it owns the change-control envelope); the owning
        # spellbook performs the local switch inside the held window; then this
        # conduit -- the only thing that knows about links -- walks its peers so
        # each borrower's spellbook parks its now-stale borrowed copy.
        outgoing_id = spell_index.selected_spell_id
        mediator.start_transaction(
            identity=self._transaction_identity,
            transaction_type=ChangeTransactionType.NOTCH,
            metadata=metadata,
        )
        try:
            # Check the target again under the notch seal: an index operation that ran
            # between the check above and admission may have moved it, and none can run
            # from here to the switch.
            self._owned_notch_target(spell_index=spell_index, spell_id=spell.spell_id, spell=spell)
            result = self._spellbook._notch_spell(spell_index=spell_index, spell=spell, change_reason=change_reason)
        except Exception:
            mediator.end_transaction(expected_type="notch", success=False)
            raise
        mediator.end_transaction(expected_type="notch", success=True)
        if outgoing_id is not None and outgoing_id != spell.spell_id:
            self._deactivate_borrowed_spell(outgoing_id)
            # Index-link receivers follow the lineage: move their subscription head
            # to the new active member (park old, activate new) via the ward.
            self._conduit_ward._emit_index_notch(spell_index, outgoing_id, spell.spell_id)
        return result

    def _resolve_notch_target(
            self,
            *,
            spell_index: SpellIndex,
            spell: Optional[Spell],
            spell_id: Optional[str],
    ) -> Spell:
        """
        Internal

        Resolve the version `notch_spell` was asked to make active, and check it.

        Contract:
            - Exactly one of `spell` and `spell_id`. A `spell_id` must be a str, and a str
              is never taken as `spell` (an id goes in `spell_id=`).
            - The version is resolved and checked by `_owned_notch_target`: through the
              owning Spellbook's `_get_owned_spell` - the exact owned version, active or
              parked - never through `find_spell_by_id`, which answers a parked id with the
              index's active spell.
            - Reads only: nothing is started or changed, so a refusal leaves the world as
              it was.

        Args:
            spell_index: The index the caller asked to notch.
            spell: The version as a Spell object, or None.
            spell_id: The version id, or None.

        Returns:
            Spell: The owned version to make active.

        Raises:
            ValueError: Both or neither given; a version this conduit's Spellbook does not
                own; a version of another index.
            TypeError: A `spell_id` that is not a str; a str given as `spell`.
        """
        if spell is not None and spell_id is not None:
            raise ValueError("notch_spell accepts either `spell` or `spell_id`, not both.")
        if spell is None and spell_id is None:
            raise ValueError(
                "notch_spell needs the version to make active: pass spell_id=<the id bind or "
                "bind_inactive returned>, or spell=<its Spell object>."
            )
        if spell_id is not None:
            if type(spell_id) is not str:
                raise TypeError(f"notch_spell `spell_id` must be a string; got {type(spell_id).__name__}.")
            return self._owned_notch_target(spell_index=spell_index, spell_id=spell_id, spell=None)
        if isinstance(spell, str):
            raise TypeError(
                "notch_spell `spell` takes a Spell object; to name a version by its id, pass "
                f"spell_id={spell!r}."
            )
        return self._owned_notch_target(spell_index=spell_index, spell_id=spell.spell_id, spell=spell)

    def _owned_notch_target(
            self,
            *,
            spell_index: SpellIndex,
            spell_id: str,
            spell: Optional[Spell],
    ) -> Spell:
        """
        Internal

        Return the version `spell_id` names if this conduit's Spellbook owns it and it
        belongs to `spell_index`; refuse it otherwise.

        Contract:
            - Ownership first: the Spellbook's `_get_owned_spell(spell_id)` must return a
              version, and, when `spell` was given, that very object (a disposed or rebound
              version, or another Book's Spell, is not owned). A cleaned Spell keeps its
              `spell_id`, so it is refused here before its deleted `spell_index` is read.
            - Membership second: the version's `spell_index` must be `spell_index` - the
              check `remove_from_spell_index`'s seam makes. A version of another index
              would otherwise be filed under its own index while this one is repointed.
            - Called by `notch_spell` before the transaction starts and again inside the
              held window, where the notch seal keeps every other index operation out.

        Args:
            spell_index: The index the caller asked to notch.
            spell_id: The id of the version to check.
            spell: The Spell object the caller gave, or None when it named the id.

        Returns:
            Spell: The owned version.

        Raises:
            ValueError: The version is not owned by this conduit's Spellbook, or belongs to
                another SpellIndex; the message names the version and the remedy.

        Threading:
            `_get_owned_spell` takes the Spellbook lock alone and releases it; the identity
            reads take no lock.
        """
        owned = self._spellbook._get_owned_spell(spell_id)
        if owned is None or (spell is not None and owned is not spell):
            raise ValueError(
                f"notch_spell: version {spell_id!r} is not owned by this conduit's Spellbook. "
                "Notch it through the conduit of the Spellbook that owns it, or stage the class "
                "on this index with bind_inactive(spell_index=...), which returns the id to pass."
            )
        if owned.spell_index is not spell_index:
            raise ValueError(
                f"notch_spell: version {spell_id!r} belongs to another SpellIndex, not the one "
                f"passed. Pass that version's own index - conduit.get_spell_by_id({spell_id!r})"
                ".spell_index - or move the version onto this index with add_to_spell_index first."
            )
        return owned

'''


def main() -> None:
    """Swap the method block, checking the old one first."""
    text = PATH.read_bytes().decode("utf-8")
    if "\r\n" in text:
        raise SystemExit("conduit.py is expected to be LF")
    start = text.index("    def notch_spell(\n")
    end = text.index("    def add_to_spell_index(self, *, spell: Any, target_index: Any) -> Any:\n")
    old = text[start:end]
    if old.count("\n") != 90:
        raise SystemExit(f"old block has {old.count(chr(10))} lines, expected 90")
    for needle in (
        "            spell: Any,\n            change_reason",
        "result = self._spellbook._notch_spell(spell_index=spell_index, spell=spell, change_reason=change_reason)",
        "self._conduit_ward._emit_index_notch(spell_index, outgoing_id, spell.spell_id)",
    ):
        if needle not in old:
            raise SystemExit(f"old block lacks {needle[:60]!r}")
    PATH.write_bytes((text[:start] + NEW_BLOCK + text[end:]).encode("utf-8"))
    print("notch_spell replaced:", old.count("\n"), "->", NEW_BLOCK.count("\n"), "lines")


if __name__ == "__main__":
    main()
