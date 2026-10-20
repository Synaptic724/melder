"""Apply S8's rollback (patch failed_notch_refusal_2026_10_18) to a source tree by exact anchored edits.

Usage: apply_s8_rollback.py <root> --check|--apply

Every exact edit's old text must occur once in its file as it is on disk; a span edit replaces the text from its
start marker through its end marker, each occurring once. A CRLF file is edited in LF and written back CRLF. Every
new line stays within 120 characters. Nothing is written unless every edit of every file applies (--apply).
"""
import pathlib
import sys

SPELLBOOK = "src/melder/aether/spellbook/spellbook.py"
CONDUIT = "src/melder/aether/conduit/conduit.py"
ERROR = "src/melder/utilities/custom_exceptions/spellbook_validation_error.py"
CCM = "src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py"
UNIT = "tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error_preface.py"

NOTCH_ENTRY = r'''    def _notch_spell(
            self,
            *,
            spell_index: SpellIndex,
            spell: Spell,
            change_reason: SpellStateChangeReason = SpellStateChangeReason.selected_different_spell,
    ) -> Spell:
        """
        Internal -- called by the owning Conduit (Conduit.notch_spell is the public surface).

        Notch a SpellIndex so `spell` becomes its selected (resolvable) spell,
        admitted as a `notch` change-control transaction through the mediator. A
        version that fails its structural check is refused with nothing moved.

        `change_reason` records WHY the active member was repointed; it defaults
        to `selected_different_spell` (a general selection, not a mutation) and is
        threaded into the spell-owned invalidation so the SpellIndex -- and its
        dependents -- are flagged with that reason.

        Contract:
            - Runs inside the `notch` transaction the owning Conduit admits and
              ends (`Conduit.notch_spell`): its seal claims this spellbook, the
              acting conduit, the conduits linked to it and the spell binding key,
              all EXCLUSIVE, and freezes those conduits' creation gates
              (`NotchTransactionStrategy`; corrected 2026-10-16: this said the
              spellbook admits the transaction and claims itself INTENT). It
              performs the selected-spell switch inside the held window.
            - The actual switch (a SpellIndex repoint via `SpellIndex.update`) is
              the SpellIndex-model seam `_apply_notch`.
            - A NOTCH EITHER STANDS OR LEAVES THE STRUCTURE AS IT WAS (2026-10-19;
              STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers, the
              owner's answer: refuse it and throw). The entry records the
              before-state, runs the seam, then checks the incoming version
              (`_check_notched_version`: phases 1-4 for a version never compiled,
              while it is active and so in the pool Phase 3 resolves against).
            - A version that passes, or needs no check, is journaled to the
              research record and returned; the commit's structural validator
              then finds its Phase-4 result and skips it.
            - A version that fails is refused: `_revert_refused_notch` puts the
              before-state back and resets the refused version's Phase 1-4
              artifacts, nothing is journaled, and the error is raised before the
              Conduit fans out to its borrowers, so they are untouched. A retry is
              checked, and refused, again.
            - A notch to the index's active version is a no-op and journals
              nothing.

        Args:
            spell_index: The SpellIndex whose selected spell is switched.
            spell: The already-bound spell to make selected.
            change_reason: Why the active member is repointed; threaded into the
                seam's invalidation.

        Returns:
            Spell: The now-selected `spell`.

        Raises:
            SpellbookValidationError: When `spell` fails its structural check. The
                message's first line says the notch did not happen and names the
                version still active (`_notch_refusal_line`), the validation report
                follows, and the error is chained from the check's own. Nothing has
                moved.
            RuntimeError: If the Spellbook is cleaned or the seam refuses `spell`;
                or when the reversal of a refused notch fails, a Melder bug whose
                message names both versions.
            Exception: Any other error the check raises, as it is, after the
                reversal has run.

        Threading:
            Runs on the notch thread inside the held window. Takes the Book lock to
            read the before-state and adds no lock: the seam and the phase runner
            take the locks they take at a notch commit today.
        """
        self.check_cleaned()
        # The owning Conduit admits the `notch` transaction (it owns the
        # change-control envelope and the conduit-link surface); this entry
        # performs the local selected-spell switch inside that held window. The
        # before-state is read first, while the seal keeps every other operation
        # off this Book, its conduits and the binding key.
        with self._lock:
            restored = self._spells.get(spell_index)
            before_selected = spell_index.selected_spell_id
            before_lookup = self._lookup_spells.get(spell._key)
            before_claim = self._aetheric_frame.get_lookup(spell._key)
        if restored is spell:
            # Already the active member: the seam's no-op, nothing to check or journal.
            return spell
        # The lineage's registration before the switch: whether it is tracked, the
        # dependencies its active version registered, and that version's topology -
        # the check's Phase 3 overwrites both on the lineage.
        tracked_state = self._spell_system_states.get_by_index_id(spell_index.id)
        before_dependencies = tuple(tracked_state.direct_dependencies) if tracked_state is not None else ()
        before_topology = (
            self._spell_system_states.get_local_topology_by_id(restored.spell_id) if restored is not None else None
        )
        self._apply_notch(spell_index=spell_index, spell=spell, change_reason=change_reason)
        # The promoted member's phases 1-4 run HERE, inside the held window, for a
        # member never compiled - the commit validator's own test (no Phase-4
        # result and no Phase-5 root blueprint; `_check_notched_version`), not the
        # Phase-4 result alone: Phase-4/phase-6 results are transient (nulled at
        # conjure end), so they must never be the only compile signal; a rerun
        # once keyed on them fired on every notch, including no-op notches.
        # Running here, not at the transaction commit, lets a failing check undo
        # the switch while the seal still holds (corrected 2026-10-19: the check
        # ran at the NOTCH commit, after the switch, and nothing undid it).
        try:
            self._check_notched_version(spell)
        except Exception as error:
            # A failing check undoes the switch. A validation verdict is raised as the
            # refusal, built first because its report renders from the Phase-4 result
            # still on the spell, which the reversal resets; any other error is
            # re-raised as it is.
            refusal = (
                SpellbookValidationError(error.broken_spells, preface=self._notch_refusal_line(spell, restored))
                if isinstance(error, SpellbookValidationError) else None
            )
            self._revert_refused_notch(
                spell_index=spell_index,
                refused=spell,
                restored=restored,
                before_selected=before_selected,
                before_lookup=before_lookup,
                before_claim=before_claim,
                before_dependencies=before_dependencies,
                before_topology=before_topology,
                tracked=tracked_state is not None,
            )
            if refusal is None:
                raise
            raise refusal from error
        # Research record: the notch stands - journal the promotion
        # (forward-only; None on a first selection; the root declares an
        # unknown incoming id before journaling).
        self._record_research_promotion(
            restored.spell_id if restored is not None else None,
            spell.spell_id,
        )
        return spell
'''

NOTCH_HELPERS = r'''    def _check_notched_version(self, spell: Spell) -> None:
        """
        Internal

        Run phases 1-4 for a version a notch just made active, when it was never compiled.

        Contract:
            - The test is the commit structural validator's own
              (`ChangeControlManager._default_structural_validator`): a conjured
              Book, and a version with no Phase-4 result and no Phase-5 root
              blueprint. Phase-4 results are transient (nulled at conjure end), so
              the blueprint is what tells a compiled version - a notch back - from
              one never compiled; a compiled version recompiles through its gated
              verdicts at its next meld.
            - Runs while `spell` is active, so it is in the pool Phase 3 resolves
              against (parked, it is not, and a self-dependency could not resolve
              to itself).
            - A version that passes keeps its Phase 1-4 results; the commit
              validator finds them and skips it.

        Args:
            spell (Spell): The version the seam just promoted.

        Returns:
            None.

        Raises:
            SpellbookValidationError: When the version validates as broken.
            Exception: Any phase execution failure, as the phase runner raises it.

        Threading:
            Called by `_notch_spell` on the notch thread inside the held window,
            without the Book lock, as the commit validator calls the phase runner.
        """
        if not self._conjured:
            return
        if spell.validation_result_phase4 is not None:
            return
        if spell._compiler_artifact._root_blueprint_phase5 is not None:
            return
        self._run_post_conjure_structural_phases([spell])

    @staticmethod
    def _notch_refusal_line(refused: Spell, restored: Optional[Spell]) -> str:
        """
        Internal

        The first line of a refused notch's SpellbookValidationError.

        Contract:
            - One line: the notch did not happen; the refused version and the
              version still active (or that the index still has none), each by
              name and spell_id.

        Args:
            refused (Spell): The version that failed its structural check.
            restored (Optional[Spell]): The version active before the notch, or
                None for an index with no active version.

        Returns:
            str: The refusal line.
        """
        line = (
            f"notch_spell refused: '{refused.spell_name}' (spell_id {refused.spell_id}) failed its structural "
            "check, so the notch did not happen; "
        )
        if restored is None:
            return line + "the index still has no active version."
        return line + (
            f"'{restored.spell_name}' (spell_id {restored.spell_id}) is still the active version of the index."
        )

    def _revert_refused_notch(
            self,
            *,
            spell_index: SpellIndex,
            refused: Spell,
            restored: Optional[Spell],
            before_selected: Optional[str],
            before_lookup: Optional[SpellIndex],
            before_claim: Optional[str],
            before_dependencies: tuple[str, ...],
            before_topology: Optional[SpellLocalTopology],
            tracked: bool,
    ) -> None:
        """
        Internal

        Undo a notch whose incoming version failed its structural check, inside the held window.

        Contract:
            - With an outgoing version (`restored`): the seam runs back toward it
              (`_apply_notch`, change reason `mutation_rolled_back`), as a notch
              back does - `restored` active, selected, claimed and routed by its
              key, registered with SpellSystemStates and the RiskManager, published
              to Nexus; `refused` parked with its creation context cleaned. The
              lineage's dependencies and the topology-derived indexes are then put
              back (`update_dependencies` with `before_dependencies`,
              `register_local_topology` with `before_topology`): the check's Phase 3
              registered `refused`'s on the lineage, and another Book's resolution
              would otherwise read `restored` as depending on them (a self-dependent
              `refused` made `restored` depend on `refused` itself). When
              `refused` is keyed elsewhere, that key's Book lookup and frame claim
              are then set back to their before-values (`_restore_binding_key`),
              since the seam repoints only the key it promotes. A key the two share
              is left as the promotion set it: setting it back would release the
              claim and the lookup wherever staging `refused` dropped them
              (STORY-2026-10-17-staged_version_releases_active_signature), and
              `restored` could not be melded by address.
            - With none (an index `remove_from_spell_index` minted):
              `_revert_refused_activation` parks `refused` again and puts the
              selection, the lineage registration, the RiskManager entry and the
              Nexus record back; then the key is set back.
            - Then `refused`'s Phase 1-4 artifacts are reset, so a retry checks it
              again instead of reading a verdict computed while it was active.
            - Not restored, by design: `restored`'s creation context (the switch
              cleaned it) and its per-conduit verdicts (gated, as after any notch),
              the marks the switch left on dependents (mark only), the Crystallizer's
              twins, which take the switch and then this reversal, and `refused`'s
              own topology under its spell_id (nothing reads it while it is parked;
              its next check replaces it).

        Args:
            spell_index (SpellIndex): The notched index.
            refused (Spell): The version that failed its check, active now.
            restored (Optional[Spell]): The version active before the notch, or None.
            before_selected (Optional[str]): The index's selected spell_id before the notch.
            before_lookup (Optional[SpellIndex]): The Book's address lookup for `refused`'s key before the notch.
            before_claim (Optional[str]): The spell_id holding the frame claim for `refused`'s key before the notch.
            before_dependencies (tuple[str, ...]): The lineage's direct dependencies before the notch.
            before_topology (Optional[SpellLocalTopology]): `restored`'s registered topology, or None.
            tracked (bool): Whether SpellSystemStates tracked the index before the notch.

        Returns:
            None.

        Raises:
            RuntimeError: When any step fails - a Melder bug; the message names both
                versions and the error is chained from the failing step's.

        Threading:
            Called by `_notch_spell` inside the held window. The seam and the helpers
            take the locks a notch takes: the Book lock with the frame lookup's leaf
            lock inside it, then the registry and the RiskManager outside the Book lock.
        """
        try:
            if restored is not None:
                self._apply_notch(
                    spell_index=spell_index,
                    spell=restored,
                    change_reason=SpellStateChangeReason.mutation_rolled_back,
                )
                self._spell_system_states.update_dependencies(spell_index, before_dependencies)
                if before_topology is not None:
                    self._spell_system_states.register_local_topology(spell_index, before_topology)
                if refused._key != restored._key:
                    self._restore_binding_key(refused._key, before_lookup, before_claim)
            else:
                self._revert_refused_activation(
                    spell_index=spell_index, refused=refused, before_selected=before_selected, tracked=tracked,
                )
                self._restore_binding_key(refused._key, before_lookup, before_claim)
            refused._compiler_artifact.reset_phase_artifacts()
        except Exception as error:
            active = (
                f"'{restored.spell_name}' (spell_id {restored.spell_id})" if restored is not None
                else "no active version"
            )
            self._logger.error(
                f"Reversal of the refused notch to spell_id={refused.spell_id} failed: {error}",
                "_revert_refused_notch",
                exc_info=True,
            )
            raise RuntimeError(
                f"notch_spell refused '{refused.spell_name}' (spell_id {refused.spell_id}) but could not put the "
                f"index back to {active}: {error}. The index may be left switched to the refused version. This is "
                "a Melder bug; please report it with this message."
            ) from error

    def _revert_refused_activation(
            self,
            *,
            spell_index: SpellIndex,
            refused: Spell,
            before_selected: Optional[str],
            tracked: bool,
    ) -> None:
        """
        Internal

        Undo a refused notch on an index that had no active version (one `remove_from_spell_index` minted).

        Contract:
            - Parks `refused` again (`_deactivate_owned_spell`) and cleans its
              creation context, sets the selection back to `before_selected` when
              it moved, and emits the index crystal while the Crystallizer
              records - all under the Book lock, as the seam does.
            - SpellSystemStates forgets the index when it did not track it before
              the notch (`unregister_index`), else re-registers it to follow the
              selection; the RiskManager entry the seam added for an untracked
              index is removed, and the Nexus record the seam published is removed.
            - Leaves the binding key to the caller (`_restore_binding_key`).

        Args:
            spell_index (SpellIndex): The notched index.
            refused (Spell): The version that failed its check, active now.
            before_selected (Optional[str]): The index's selected spell_id before the notch.
            tracked (bool): Whether SpellSystemStates tracked the index before the notch.

        Returns:
            None.

        Raises:
            RuntimeError: As the steps raise them (the caller reports a Melder bug).

        Threading:
            The Book lock for the park and the selection (the seam's order); the
            registry, the RiskManager and Nexus outside it.
        """
        with self._lock:
            self._deactivate_owned_spell(refused)
            refused._cleanup_creation_context()
            if before_selected is not None and spell_index.selected_spell_id != before_selected:
                spell_index.update(before_selected)
            if self._crystallizer.activated:
                self._crystallizer.emit(
                    self._crystallizer.create_spell_index_crystal(spell_index, self._id)
                )
        if tracked:
            self._spell_system_states.register_index(spell_index=spell_index, owner_spellbook_id=self._id)
        else:
            self._spell_system_states.unregister_index(spell_index)
        if self._conjured and self._conduit is not None:
            if not tracked:
                self._unregister_spell_with_risk_manager(self._get_required_conduit_surface()._id, refused)
            self._remove_spell_record_from_nexus(refused.spell_id)

    def _restore_binding_key(
            self,
            key: tuple[str, str],
            lookup: Optional[SpellIndex],
            claim: Optional[str],
    ) -> None:
        """
        Internal

        Set one binding key's Book address lookup and frame claim back to the values a refused notch recorded.

        Contract:
            - The Book lookup is set to `lookup`, or removed when it was None.
            - The frame claim is re-pointed to `claim` (`update_lookup`, which sets
              unconditionally), or released when it was None.

        Args:
            key (tuple[str, str]): The `(frame_key, binding_key)` to restore.
            lookup (Optional[SpellIndex]): The index the Book routed the key to, or None.
            claim (Optional[str]): The spell_id that held the frame claim, or None.

        Returns:
            None.

        Threading:
            Under the Book lock, taking the frame lookup's leaf lock inside it as
            the seam does.
        """
        with self._lock:
            if lookup is None:
                self._lookup_spells.pop(key, None)
            else:
                self._lookup_spells[key] = lookup
            if claim is None:
                self._aetheric_frame.release_lookup(key)
            else:
                self._aetheric_frame.update_lookup(key, claim)

'''

NEXUS_REMOVE = r'''    def _remove_spell_record_from_nexus(self, spell_id: str) -> None:
        """
        Internal

        Remove one published SpellRecord of this Spellbook from Nexus.

        Contract:
            - The gates of `_publish_spell_record_to_nexus`: a publishing frame and
              a conjured Book with a root conduit; otherwise nothing happens.
            - Used when a refused notch takes back the record its switch published
              for a version that is parked again (`_revert_refused_activation`).

        Args:
            spell_id:
                The spell_id whose record is removed.

        Returns:
            None.
        """
        if not self._nexus_publish_enabled:
            return
        if not self._conjured or self._conduit is None:
            return
        self._nexus._remove_spell_record(
            self._id,
            spell_id,
            self._aetheric_frame_name,
        )

'''

ERROR_INIT = r'''    def __init__(
            self,
            broken_spells: list[Spell],
            *,
            system_diagnostics: Optional[Sequence[SystemDiagnostic]] = None,
            preface: Optional[str] = None,
    ) -> None:
        """
        Purpose:
            Build a validation error whose message explains every recorded failure.
        Contract:
            - Keeps `broken_spells` exactly as supplied (tooling reads the spells).
            - Renders the message once from the spells' Phase 4/6 results and the
              ERROR entries of `system_diagnostics`; WARNING diagnostics are ignored.
            - Remains resilient when spell or diagnostic attributes are missing or
              cleaned; a failed read degrades that field only.
            - `preface`, when given, is the message's first line and the message
              above follows it unchanged; without it the message is byte-identical.
              It is checked before anything is rendered (2026-10-19).
        Args:
            broken_spells: Spells refused by validation (may be empty).
            system_diagnostics: Optional conduit resolution diagnostics that explain
                the refusal (the conjure and local-rerun gates pass them).
            preface: One line of text to put before the message, or None (the
                default). A refused notch passes one (`Spellbook._notch_spell`).
        Returns:
            None.
        Raises:
            TypeError: When `preface` is not one line of text: not a str, empty, or
                holding a line break (`_check_preface`).
        """
        if preface is not None:
            self._check_preface(preface)
        self.broken_spells = broken_spells
        if not broken_spells and not system_diagnostics:
            message = "SpellbookValidationError raised with no broken spells."
        else:
            message = self._render(broken_spells, system_diagnostics or ())
        if preface is not None:
            message = preface + "\n" + message
        super().__init__(message)

    @staticmethod
    def _check_preface(preface: object) -> None:
        """
        Purpose:
            Refuse a preface that is not one line of text.
        Contract:
            - Accepts a non-empty str with no line break - none of the boundaries
              `str.splitlines` splits on - so the preface is exactly the message's
              first line.
        Args:
            preface: The value passed as `preface` (not None).
        Returns:
            None.
        Raises:
            TypeError: When it is not a str, is empty, or holds a line break; the
                message names what it got.
        """
        if not isinstance(preface, str):
            received = type(preface).__name__
        elif not preface:
            received = "an empty str"
        elif preface.splitlines() != [preface]:
            received = "a str with a line break"
        else:
            return
        raise TypeError(
            "SpellbookValidationError(preface=...) takes one line of text, a non-empty str; got "
            f"{received}. Pass the one line to put before the report, or leave preface out."
        )
'''

# (file, kind, a, b, new): kind "exact" replaces a with new; kind "span" replaces a..b (inclusive) with new.
EDITS = [
    (SPELLBOOK, "exact",
     "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n",
     None,
     "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n"
     "    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellLocalTopology\n"),
    (SPELLBOOK, "exact",
     "from melder.utilities.caching_system.caching_system import CachingSystem\n"
     "from melder.utilities.general_base.cleanable import Cleanable\n",
     None,
     "from melder.utilities.caching_system.caching_system import CachingSystem\n"
     "from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError\n"
     "from melder.utilities.general_base.cleanable import Cleanable\n"),
    (SPELLBOOK, "span", "    def _notch_spell(\n", "        return notched_spell\n", NOTCH_ENTRY),
    (SPELLBOOK, "exact",
     "        subscriptions to the incoming one; the borrower Book's contracted-map mutators\n"
     "        mark its consumers (rule 2).\n",
     None,
     "        subscriptions to the incoming one; the borrower Book's contracted-map mutators\n"
     "        mark its consumers (rule 2).\n"
     "\n"
     "        The seam journals nothing to the research record: its entry\n"
     "        (`_notch_spell`) journals the promotion once the notch stands, after the\n"
     "        incoming version's structural check. When that check fails, the entry runs\n"
     "        this seam back toward the outgoing version (`_revert_refused_notch`, change\n"
     "        reason `mutation_rolled_back`), as a notch back does (2026-10-19).\n"),
    (SPELLBOOK, "exact",
     "        # Research record: the selection moved - journal the promotion\n"
     "        # (forward-only; None on a first selection; the root declares an\n"
     "        # unknown incoming id before journaling).\n"
     "        self._record_research_promotion(\n"
     "            outgoing.spell_id if outgoing is not None else None,\n"
     "            new_id,\n"
     "        )\n",
     None,
     "        # Research record: the entry (`_notch_spell`) journals the promotion once\n"
     "        # the notch stands - after the incoming version's structural check - so a\n"
     "        # refused notch, and this seam run back to undo it, journal nothing\n"
     "        # (2026-10-19; the promotion was journaled here until then).\n"),
    (SPELLBOOK, "exact",
     "        # Phases 1-4 for the promoted member now run at the NOTCH transaction\n"
     "        # commit: the strategy stages this binding key and the generalized\n"
     "        # structural commit validator delegates back to this spellbook's own\n"
     "        # phase runner, exactly like a bind commit. No hand-rolled structural\n"
     "        # run here -- the seam owns the swap, the commit owns the checks.\n",
     None,
     "        # Phases 1-4 for the promoted member run in the entry (`_notch_spell`),\n"
     "        # after this seam returns and still inside the held window, for a member\n"
     "        # never compiled; when they fail, the entry runs this seam back toward the\n"
     "        # outgoing version. The strategy still stages this binding key, so the\n"
     "        # structural commit validator meets the member and skips it (its Phase-4\n"
     "        # result is present). No structural run here -- the seam owns the swap,\n"
     "        # the entry owns the check (corrected 2026-10-19: the check ran at the\n"
     "        # NOTCH commit, after the switch, and nothing undid it).\n"),
    (SPELLBOOK, "exact",
     "        return spell\n\n    def _add_to_spell_index(self, *, spell: Spell, target_index: SpellIndex) -> Spell:\n",
     None,
     "        return spell\n\n" + NOTCH_HELPERS
     + "    def _add_to_spell_index(self, *, spell: Spell, target_index: SpellIndex) -> Spell:\n"),
    (SPELLBOOK, "exact",
     "        Used by the active bind path. Notch does NOT stage -- it promotes an\n"
     "        existing member under a NOTCH transaction, whose commit never fires the\n"
     "        bind structural validator, so it runs the structural phases directly via\n"
     "        `_run_post_conjure_structural_phases`.\n",
     None,
     "        Used by the active bind path. Notch does NOT stage -- it promotes an\n"
     "        existing member under a NOTCH transaction, and its entry (`_notch_spell`)\n"
     "        runs the structural phases for a never-compiled member directly via\n"
     "        `_run_post_conjure_structural_phases`, inside the held window, refusing\n"
     "        the notch when they fail. The NOTCH commit does fire the structural\n"
     "        validator (it resolves the strategy's staged binding key), which then\n"
     "        finds the Phase-4 result and skips (corrected 2026-10-19: this said the\n"
     "        commit never fires it).\n"),
    (SPELLBOOK, "exact",
     "    def _remove_spells_from_nexus(self) -> None:\n",
     None,
     NEXUS_REMOVE + "    def _remove_spells_from_nexus(self) -> None:\n"),
    (CONDUIT, "exact",
     "            - Notching to the index's active version is a no-op: nothing moves and no\n"
     "              borrower is touched.\n",
     None,
     "            - Notching to the index's active version is a no-op: nothing moves and no\n"
     "              borrower is touched.\n"
     "            - A VERSION THAT FAILS ITS STRUCTURAL CHECK IS REFUSED WITH NOTHING MOVED\n"
     "              (2026-10-19): a version never compiled is checked (phases 1-4) inside the\n"
     "              held window once it is active, and when the check fails the Spellbook\n"
     "              puts the structure back before this call raises - the index selects the\n"
     "              version it selected, that version stays active, claimed and routed, the\n"
     "              refused one is parked again with no verdict kept, nothing is journaled or\n"
     "              published for it, and no borrower is touched. A retry is checked, and\n"
     "              refused, again.\n"),
    (CONDUIT, "exact",
     "        Raises:\n"
     "            ValueError: When both or neither of `spell` and `spell_id` are given; when the\n"
     "                spell is not owned by this conduit's Spellbook (a spell_id nothing here\n"
     "                bound, a disposed spell, another Book's spell); when it belongs to another\n"
     "                SpellIndex.\n"
     "            TypeError: When `spell_id` is not a string, or a string is given as `spell`.\n"
     "            RuntimeError: If the Conduit is cleaned, the frame is not dynamic, or the\n"
     "                Conduit has no owning Spellbook; and whatever the transaction or the\n"
     "                switch raises.\n",
     None,
     "        Raises:\n"
     "            SpellbookValidationError: When the version fails its structural check. Its first\n"
     "                line says the notch did not happen and names the version still active; the\n"
     "                validation report follows. Nothing has moved.\n"
     "            ValueError: When both or neither of `spell` and `spell_id` are given; when the\n"
     "                spell is not owned by this conduit's Spellbook (a spell_id nothing here\n"
     "                bound, a disposed spell, another Book's spell); when it belongs to another\n"
     "                SpellIndex.\n"
     "            TypeError: When `spell_id` is not a string, or a string is given as `spell`.\n"
     "            RuntimeError: If the Conduit is cleaned, the frame is not dynamic, or the\n"
     "                Conduit has no owning Spellbook; and whatever the transaction or the\n"
     "                switch raises, including a reversal of a refused notch that fails (a\n"
     "                Melder bug; the message names both versions).\n"),
    (CONDUIT, "exact",
     "            result = self._spellbook._notch_spell(spell_index=spell_index, spell=spell, change_reason=change_reason)\n",
     None,
     "            # A version that fails its structural check raises here with the switch already\n"
     "            # undone by the Spellbook; the transaction then ends as failed and no borrower is\n"
     "            # touched (2026-10-19).\n"
     "            result = self._spellbook._notch_spell(spell_index=spell_index, spell=spell, change_reason=change_reason)\n"),
    (ERROR, "exact",
     "        - Footers count the hidden warnings and explain `[internal]`.\n",
     None,
     "        - Footers count the hidden warnings and explain `[internal]`.\n"
     "        - With `preface` (2026-10-19) that one line comes first and the message\n"
     "          above follows it unchanged; a refused notch passes one, saying the\n"
     "          notch did not happen (`Spellbook._notch_spell`, which\n"
     "          `Conduit.notch_spell` calls inside its transaction).\n"),
    (ERROR, "span",
     "    def __init__(\n            self,\n            broken_spells: list[Spell],\n",
     "        super().__init__(self._render(broken_spells, system_diagnostics or ()))\n",
     ERROR_INIT),
    (CCM, "exact",
     "          (notch-back / no-op notch) from a never-compiled bind_inactive one;\n"
     "          compiled members recompile through meld's gated validation lane\n",
     None,
     "          (notch-back / no-op notch) from a never-compiled bind_inactive one;\n"
     "          compiled members recompile through meld's gated validation lane\n"
     "        - for a notch the entry (`Spellbook._notch_spell`) runs this same check\n"
     "          itself, inside the held window, and refuses the notch with nothing\n"
     "          moved when it fails, so a notched member that reaches this validator\n"
     "          has been checked or compiled already and is skipped (2026-10-19)\n"),
    (UNIT, "exact",
     "def test_an_empty_preface_is_refused() -> None:\n"
     "    \"\"\"An empty preface would add a blank first line, so it is refused like a non-str one.\"\"\"\n"
     "    with pytest.raises(TypeError, match=r\"takes one line of text, a non-empty str; got an empty str\"):\n"
     "        SpellbookValidationError(_broken_spell(), preface=\"\")\n",
     None,
     "def test_an_empty_preface_is_refused() -> None:\n"
     "    \"\"\"An empty preface would add a blank first line, so it is refused like a non-str one.\"\"\"\n"
     "    with pytest.raises(TypeError, match=r\"takes one line of text, a non-empty str; got an empty str\"):\n"
     "        SpellbookValidationError(_broken_spell(), preface=\"\")\n"
     "\n"
     "\n"
     "@pytest.mark.parametrize(\"preface\", [\"first\\nsecond\", \"first\\r\\nsecond\", \"ends with a break\\n\", "
     "\"first\\u2028second\"])\n"
     "def test_a_preface_with_a_line_break_is_refused(preface: str) -> None:\n"
     "    \"\"\"A preface with a line break would put a second line before the report, so it is refused too.\"\"\"\n"
     "    with pytest.raises(TypeError, match=r\"takes one line of text, a non-empty str; got a str with a line break\"):\n"
     "        SpellbookValidationError(_broken_spell(), preface=preface)\n"),
]


def _apply_one(text: str, kind: str, first: str, last: str, new: str, where: str) -> str:
    """Apply one exact or span edit to LF text; raise SystemExit when an anchor is missing or repeated."""
    if text.count(first) != 1:
        raise SystemExit("%s: anchor found %d times: %r" % (where, text.count(first), first[:90]))
    for line in new.split("\n"):
        if len(line) > 120:
            raise SystemExit("%s: new line over 120 chars (%d): %s" % (where, len(line), line))
    if kind == "exact":
        return text.replace(first, new)
    start = text.index(first)
    if text.count(last) != 1:
        raise SystemExit("%s: span end found %d times: %r" % (where, text.count(last), last[:90]))
    end = text.index(last, start) + len(last)
    return text[:start] + new + text[end:]


def main() -> None:
    """Apply every edit in memory; write the files only with --apply, then read each back."""
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    root = pathlib.Path(sys.argv[1])
    texts = {}
    crlf = {}
    for rel, kind, first, last, new in EDITS:
        if rel not in texts:
            raw = (root / rel).read_bytes().decode("utf-8")
            crlf[rel] = "\r\n" in raw
            if crlf[rel] and raw.count("\r\n") != raw.count("\n"):
                raise SystemExit(rel + ": mixed line endings")
            texts[rel] = raw.replace("\r\n", "\n")
        texts[rel] = _apply_one(texts[rel], kind, first, last, new, rel)
    for rel, text in texts.items():
        print(rel, "crlf" if crlf[rel] else "lf", "lines now:", text.count("\n"))
    if sys.argv[2] == "--apply":
        for rel, text in texts.items():
            out = text.replace("\n", "\r\n") if crlf[rel] else text
            (root / rel).write_bytes(out.encode("utf-8"))
            if (root / rel).read_bytes().decode("utf-8") != out:
                raise SystemExit("read-back mismatch: " + rel)
        print("applied")


main()
