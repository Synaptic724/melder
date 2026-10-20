"""S3's src edits (melder_0, 2026-10-19; patch cleanup_releases_contracts_2026_10_19): every cleanup_spell door
takes the version out of every contract of the Book's root conduit before the Book disposes it.

conduit.py: `Conduit.cleanup_spell` uses the root ward, hands `_emit_spell_disposed` to the Book as
`release_contracts`, and emits the destroy with no member ids. spellbook.py: `Spellbook.cleanup_spell` goes through
the root conduit once conjured; `_dispose_spell` takes `release_contracts` and calls it between its decision and its
disposal. conduit_ward.py: `_emit_spell_disposed`, new; `_emit_index_destroy`'s and `_uncontract_member_spell`'s
docstrings. All-or-nothing: every anchor is checked before anything is written; `--write` writes, else it checks.
Backups go to /tmp/m0_mq/bak_s3/.
"""
import pathlib
import shutil
import sys

REPO = pathlib.Path.home() / "mnt/melder_private"
CONDUIT = REPO / "src/melder/aether/conduit/conduit.py"
SPELLBOOK = REPO / "src/melder/aether/spellbook/spellbook.py"
WARD = REPO / "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
BACKUP = pathlib.Path("/tmp/m0_mq/bak_s3")


def once(text: str, old: str, new: str, label: str) -> str:
    """Replace the single occurrence of `old`."""
    count = text.count(old)
    if count != 1:
        sys.exit(f"ANCHOR {label}: found {count}")
    return text.replace(old, new)


def between(text: str, start: str, end: str, new: str, must: tuple, label: str) -> str:
    """Replace the block from `start` through `end` (inclusive), checking it holds every `must` marker."""
    if text.count(start) != 1:
        sys.exit(f"START {label}: found {text.count(start)}")
    a = text.index(start)
    b = text.index(end, a)
    if text.count(end) != 1:
        sys.exit(f"END {label}: found {text.count(end)}")
    block = text[a:b + len(end)]
    for marker in must:
        if marker not in block:
            sys.exit(f"MARKER {label}: {marker!r} missing")
    return text[:a] + new + text[b + len(end):]


CLEANUP_SPELL = '''    def cleanup_spell(self, *, spell: Any) -> None:
        """
        Public API

        Conduit facade for fully disposing an owned spell. The owning Spellbook
        decides the disposal, every contract that holds the version drops it,
        then the Spellbook disposes it: it removes the spell from every
        resolution surface, destroys its index if it was the sole member, and
        tears the spell object down; when the index was destroyed, its
        index-link borrowers drop their subscription to it.

        Contract:
            - CONTRACTS FIRST, THEN THE DISPOSAL (the owner's order, 2026-10-19):
              after the Spellbook's locked decision and before it disposes
              anything, every contract of the Book's root conduit that holds the
              version - an index link's member Detail or a version grant - drops
              it, with the borrower's entry, active or parked, and its borrowed
              id (`ConduitWard._emit_spell_disposed`). No borrower is left
              holding a version its lender disposed, nor a cleaned Spell.
              (cleanup_releases_contracts_2026_10_19, 0.2.8261)
            - The contracts live on the Book's root conduit, so a call through a
              lesser conduit of its lineage reaches them too; the Spellbook's own
              `cleanup_spell` comes here once the Book has conjured.
            - The Spellbook decides, under its own lock, whether the disposal
              destroys the spell's index, and reports the destroyed index's id;
              the destroy is emitted to index-link borrowers exactly then, after
              the disposal and with no member id, the version having left every
              contract already (an index is destroyed only when the spell was its
              sole member). Nothing about the spell or its index is read here
              before that decision.
            - A refused call (see Raises) changes no contract.
            - Not admitted through a transaction (no cleanup strategy exists), so
              a link or grant of the same version that lands between the release
              and the disposal is not ordered against it.

        Args:
            spell: The owned spell to dispose.

        Raises:
            RuntimeError: If the Conduit is cleaned or has no owning Spellbook.
            RuntimeError: If the spell has already been disposed, is being disposed
                by another call, is not owned by the owning Spellbook, or is the
                active member of a multi-member index (raised by
                `Spellbook._dispose_spell` before any contract changes).
            RuntimeError: From the release, if a borrower's Book holds no entry
                for the version under a lender-side Detail; nothing is disposed,
                and a retry repeats the release.

        Threading:
            Takes no lock of its own. The Spellbook takes the Book lock and the
            spell's own lock (never nested) and runs the release with neither
            held; the release and the destroy emission walk the root ward's
            contracts under the ward lock (ward -> contract -> borrower Book), so
            a concurrent link or sever of the root waits for them.
            (cross_object_lock_gaps, 0.2.8231)
            Of two calls for one spell that overlap, the Spellbook lets the first
            dispose it and refuses the second, so each contract drops the version
            once and the destroy is emitted once. (lock_residuals, 0.2.8232)

        Returns:
            None.
        """
        self.check_cleaned()
        if self._spellbook is None:
            raise RuntimeError("[CONDUIT] No owning Spellbook for cleanup_spell.")
        # The Book's root conduit holds the contracts; a lesser conduit's own ward holds none
        # (cleanup_releases_contracts_2026_10_19, 0.2.8261).
        ward = self._spellbook._conduit._conduit_ward
        # The Spellbook's own locked decision says whether the index went with the spell; the old unlocked
        # pre-read of spell.spell_index here raised AttributeError for a disposed spell and could disagree with
        # what the Spellbook then did (cross_object_lock_gaps, 0.2.8231). Between that decision and the
        # disposal the Book hands the version to `release_contracts`, so every contract drops it while it is
        # still live (the owner's order, 2026-10-19: contracts first, then the cleanup).
        destroyed_index_id = self._spellbook._dispose_spell(spell, release_contracts=ward._emit_spell_disposed)
        # A destroyed SpellIndex shared by index link must be dropped on its receivers so they
        # do not keep a subscription to a dead index. Its member already left every contract, so no member id.
        if destroyed_index_id is not None:
            ward._emit_index_destroy(destroyed_index_id, ())
'''

SPELL_DISPOSED = '''
    def _emit_spell_disposed(self, spell_id: str) -> None:
        """
        Internal

        Owner-side emission when this conduit's Book disposes a version (`cleanup_spell`): every
        contract whose owner side holds a Detail for the version - an index link's member Detail
        or a version grant - drops it, with the borrower's entry, active or parked, and its
        borrowed id, through the per-contract removal the index emissions use
        (`_uncontract_member_spell`). The Book calls it after deciding the disposal and before it
        disposes anything, so no borrower is left holding the version, nor a cleaned Spell.
        (cleanup_releases_contracts_2026_10_19, 0.2.8261)

        Contract:
            - A contract that holds no Detail for the version is untouched; no contract is
              severed here (an empty contract is a live link with nothing shared).
            - An active borrower entry going marks the borrower's SpellContract consumers of its
              key for revalidation (`Spellbook._remove_contracted_spell`, rule 2).
            - Each contract it changed is re-emitted into the record after the ward lock is
              released, as `_emit_index_destroy` does; a no-op while the crystallizer is inactive.
            - The index links of an index that dies with the version are dropped after the
              disposal, by `_emit_index_destroy`, not here.

        Args:
            spell_id: The spell_id of the version being disposed.

        Returns:
            None.

        Raises:
            RuntimeError: If this ward is cleaned; from the borrower's Book, if it holds no entry
                for the version under a lender-side Detail (the cleanup then disposes nothing).

        Threading:
            Walks this ward's contract registry under the ward lock, the lock link
            (`_create_new_contract`) and sever (`_remove_contract`) write it under, reads each
            contract's Detail map under the contract lock and reaches the borrower's Book inside
            `_uncontract_member_spell`: ward -> contract -> Book, the order sever and the index
            emissions take. The caller holds no Book lock (`Spellbook._dispose_spell` runs it
            between its two locked sections) and runs outside any transaction.
        """
        self.check_cleaned()
        record_affected_contracts = []
        # Under this ward's lock: link and sever write _contracts under it, and this emission runs outside any
        # transaction window, so the mediator does not order it against them (cross_object_lock_gaps, 0.2.8231).
        with self._lock:
            for contract in self._contracts.values():
                with contract._lock:
                    held = contract._get_detail_map(self).get(spell_id) is not None
                if not held:
                    continue
                record_affected_contracts.append(contract)
                # The version leaves this contract: its Detail, and the borrower's entry and borrowed id.
                self._uncontract_member_spell(contract, self, spell_id)
        # Record: the disposed version left these contracts.
        for record_contract in record_affected_contracts:
            self._emit_contract_record(record_contract)
'''


def conduit(text: str) -> str:
    """`Conduit.cleanup_spell`."""
    return between(
        text,
        "    def cleanup_spell(self, *, spell: Any) -> None:\n",
        "            self._conduit_ward._emit_index_destroy(destroyed_index_id, (spell_id,))\n",
        CLEANUP_SPELL,
        ("destroyed_index_id = self._spellbook._dispose_spell(spell)", "spell_id = spell.spell_id",
         "cross_object_lock_gaps, 0.2.8231", "lock_residuals, 0.2.8232"),
        "Conduit.cleanup_spell")


def spellbook(text: str) -> str:
    """`Spellbook.cleanup_spell` and `_dispose_spell`."""
    text = once(
        text,
        "        Fully dispose an owned spell. Invalidate it FIRST so the spell and its\n"
        "        SpellIndex are flagged dirty (and dependents are rechecked) while the index\n"
        "        and dependency edges still exist, then take it off every resolution\n"
        "        surface, destroying its index when the spell was that index's only member.\n",
        "        Fully dispose an owned spell. On a conjured Book every contract that holds\n"
        "        the version drops it first, through the root conduit's `cleanup_spell`.\n"
        "        Then invalidate it so the spell and its SpellIndex are flagged dirty (and\n"
        "        dependents are rechecked) while the index and dependency edges still exist,\n"
        "        then take it off every resolution surface, destroying its index when the\n"
        "        spell was that index's only member.\n",
        "cleanup_spell summary")
    text = once(
        text,
        "            - Invalidation happens FIRST (`spell.invalidate_spell()`): the creation\n",
        "            - Invalidation happens before any teardown (`spell.invalidate_spell()`): the creation\n",
        "cleanup_spell invalidation bullet")
    text = once(
        text,
        "            - NOTE: not yet sealed by a mediator transaction (no cleanup strategy\n"
        "              exists); the map mutations run under the Spellbook lock.\n\n"
        "        Args:\n"
        "            spell: The owned spell to dispose.\n\n"
        "        Raises:\n"
        "            RuntimeError: If the spell has already been disposed (\"cleanup_spell:\n",
        "            - NOTE: not yet sealed by a mediator transaction (no cleanup strategy\n"
        "              exists); the map mutations run under the Spellbook lock.\n"
        "            - On a conjured Book the call goes through its root conduit's\n"
        "              `cleanup_spell`: after this Book's decision and before its\n"
        "              disposal, every contract that holds the version drops it - an\n"
        "              index link's member Detail or a version grant, with the borrower's\n"
        "              entry and borrowed id - and an index that dies with it leaves its\n"
        "              index links (cleanup_releases_contracts_2026_10_19, 0.2.8261).\n"
        "              Before conjure no contract exists and the Book disposes it\n"
        "              directly.\n\n"
        "        Args:\n"
        "            spell: The owned spell to dispose.\n\n"
        "        Raises:\n"
        "            RuntimeError: If the spell has already been disposed (\"cleanup_spell:\n",
        "cleanup_spell conjured bullet")
    text = once(
        text,
        "        self._dispose_spell(spell)\n\n"
        "    def _dispose_spell(self, spell: Spell) -> Optional[str]:\n",
        "        self.check_cleaned()\n"
        "        if self._conduit is not None:\n"
        "            # Conjured: the root conduit's cleanup_spell runs this Book's disposal with the contract release\n"
        "            # first, so no borrower keeps the version (cleanup_releases_contracts_2026_10_19, 0.2.8261). Before\n"
        "            # conjure no conduit and no contract exist.\n"
        "            self._conduit.cleanup_spell(spell=spell)\n"
        "            return\n"
        "        self._dispose_spell(spell)\n\n"
        "    def _dispose_spell(\n"
        "            self,\n"
        "            spell: Spell,\n"
        "            *,\n"
        "            release_contracts: Optional[Callable[[str], None]] = None,\n"
        "    ) -> Optional[str]:\n",
        "cleanup_spell body and _dispose_spell signature")
    text = once(
        text,
        "              disposal ends (finished or failed), so a second call for the same\n"
        "              spell that starts meanwhile refuses before it touches anything.\n\n"
        "        Args:\n"
        "            spell: The owned spell to dispose.\n\n"
        "        Returns:\n"
        "            Optional[str]: The destroyed index's id, or None.\n\n"
        "        Raises:\n"
        "            RuntimeError: As `cleanup_spell`.\n\n"
        "        Threading:\n"
        "            As `cleanup_spell`. (cross_object_lock_gaps, 0.2.8231; the in-flight\n"
        "            mark, lock_residuals, 0.2.8232)\n",
        "              disposal ends (finished or failed), so a second call for the same\n"
        "              spell that starts meanwhile refuses before it touches anything.\n"
        "            - `release_contracts`, when given, is called once with the spell_id\n"
        "              after the decision and the refusals and before anything is\n"
        "              invalidated or disposed: `Conduit.cleanup_spell` passes the root\n"
        "              ward's `_emit_spell_disposed`, so every contract drops the version\n"
        "              while it is still live. A refused call never reaches it; a raise\n"
        "              from it ends the call with nothing disposed, and the finally\n"
        "              clears the in-flight mark. (cleanup_releases_contracts_2026_10_19,\n"
        "              0.2.8261)\n\n"
        "        Args:\n"
        "            spell: The owned spell to dispose.\n"
        "            release_contracts: Optional hook taking the spell_id, run between the\n"
        "                decision and the disposal; None disposes with no contract release\n"
        "                (an unconjured Book holds no contract).\n\n"
        "        Returns:\n"
        "            Optional[str]: The destroyed index's id, or None.\n\n"
        "        Raises:\n"
        "            RuntimeError: As `cleanup_spell`.\n"
        "            Exception: Whatever `release_contracts` raises; nothing is disposed.\n\n"
        "        Threading:\n"
        "            As `cleanup_spell`. (cross_object_lock_gaps, 0.2.8231; the in-flight\n"
        "            mark, lock_residuals, 0.2.8232) `release_contracts` runs with no Book\n"
        "            lock held: the decision's section is released before it and the\n"
        "            disposal's sections are taken after it.\n",
        "_dispose_spell docstring")
    text = once(
        text,
        "        # Reached only when this call marked the spell above: nothing between the mark and here can raise.\n"
        "        try:\n",
        "        # Reached only when this call marked the spell above: nothing between the mark and here can raise.\n"
        "        try:\n"
        "            # CONTRACTS FIRST (the owner's order, 2026-10-19): the caller's hook takes the version out of every\n"
        "            # contract that holds it while it is still live, before anything below invalidates or disposes it;\n"
        "            # a raise here leaves it undisposed and the finally clears the mark\n"
        "            # (cleanup_releases_contracts_2026_10_19, 0.2.8261).\n"
        "            if release_contracts is not None:\n"
        "                release_contracts(spell_id)\n",
        "_dispose_spell hook call")
    return text


def ward(text: str) -> str:
    """`_emit_spell_disposed`, and two docstrings."""
    text = once(
        text,
        "            member_ids: The index's member version ids, captured by the caller BEFORE\n"
        "                teardown (the live index is already cleaned when this runs).\n",
        "            member_ids: The index's member version ids still contracted under it,\n"
        "                captured by the caller BEFORE teardown (the live index is already\n"
        "                cleaned when this runs); empty from `Conduit.cleanup_spell`, whose\n"
        "                version left every contract before the disposal\n"
        "                (`_emit_spell_disposed`; cleanup_releases_contracts_2026_10_19, 0.2.8261).\n",
        "_emit_index_destroy member_ids")
    text = once(
        text,
        "        Remove ONE per-member spell contract for an index-link: drop (and clean) the\n"
        "        spell Detail on the owner side and untrack the borrower's contracted copy.\n"
        "        Idempotent.\n",
        "        Remove ONE per-member spell contract for an index-link: drop (and clean) the\n"
        "        spell Detail on the owner side and untrack the borrower's contracted copy.\n"
        "        Also the per-contract removal of a disposed version, a version grant included\n"
        "        (`_emit_spell_disposed`; cleanup_releases_contracts_2026_10_19, 0.2.8261).\n"
        "        Idempotent on the owner side; the borrower's removal raises when its Book holds\n"
        "        no entry for the version (`Spellbook._remove_contracted_spell`).\n",
        "_uncontract_member_spell docstring")
    anchor = ("                # The index dropped this member; eagerly remove its per-member contract\n"
              "                # (and the borrower's copy). Idempotent -- a no-op if it was never mapped.\n"
              "                self._uncontract_member_spell(contract, self, member_id)\n")
    return once(text, anchor, anchor + SPELL_DISPOSED, "_emit_spell_disposed")


def main() -> None:
    """Check every edit; write when asked."""
    staged = {CONDUIT: conduit(CONDUIT.read_text(encoding="utf-8")),
              SPELLBOOK: spellbook(SPELLBOOK.read_text(encoding="utf-8")),
              WARD: ward(WARD.read_text(encoding="utf-8"))}
    for path, text in staged.items():
        if "\r" in text:
            sys.exit(f"CR in {path}")
        for number, line in enumerate(text.split("\n"), 1):
            if len(line) > 120:
                print(f"WIDE {path.name}:{number}: {len(line)}")
    if "--write" not in sys.argv:
        print("CHECK OK", [path.name for path in staged])
        return
    BACKUP.mkdir(parents=True, exist_ok=True)
    for path, text in staged.items():
        shutil.copy2(path, BACKUP / (path.name + ".pre_s3"))
        path.write_text(text, encoding="utf-8", newline="\n")
        print("wrote", path.relative_to(REPO))


if __name__ == "__main__":
    main()
