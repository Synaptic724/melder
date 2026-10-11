"""
Apply the 0.2.8233 source change set (direct_spell_cleanup_lock_order_2026_10_11) to a tree.

Usage: python apply_0_2_8233.py <tree root holding src/>

spell.py and spellbook.py are uniformly CRLF: each file is edited with LF line ends and written back with CRLF.
Every edit asserts its anchor exactly once (inside the named method where one is named).
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])


def load(rel: str) -> tuple[pathlib.Path, str]:
    path = ROOT / rel
    raw = path.read_bytes().decode("utf-8")
    assert raw.count("\r\n") == raw.count("\n"), f"{rel} is not uniformly CRLF"
    return path, raw.replace("\r\n", "\n")


def save(path: pathlib.Path, text: str) -> None:
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))


def span(text: str, header: str) -> tuple[int, int]:
    """Character span of one method: its header line up to the next method or decorator at class level."""
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith(header)]
    assert len(starts) == 1, (header, starts)
    start = starts[0]
    end = start + 1
    while end < len(lines) and not lines[end].startswith(("    def ", "    @", "    async def ", "    #region",
                                                          "    #endregion")):
        end += 1
    begin = sum(len(line) + 1 for line in lines[:start])
    finish = sum(len(line) + 1 for line in lines[:end])
    return begin, finish


def replace_in(text: str, header: str, old: str, new: str) -> str:
    begin, finish = span(text, header)
    body = text[begin:finish]
    assert body.count(old) == 1, (header, old[:80], body.count(old))
    return text[:begin] + body.replace(old, new) + text[finish:]


def replace_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, (old[:80], text.count(old))
    return text.replace(old, new)


# ------------------------------------------------------------------ spell.py
path, text = load("src/melder/aether/spellbook/spell.py")

text = replace_once(text, """        "spellframe_kind",
        "implemented_protocols",
    ]
""", """        "spellframe_kind",
        "implemented_protocols",
        "_removal_lock",
    ]
""")

H = "    def __init__("
text = replace_in(text, H, """            is not yet reachable by other threads. `_door_epoch` starts at 0 and
            its bump sites assume per-spell serialization.
""", """            is not yet reachable by other threads. `_door_epoch` starts at 0 and
            its bump sites assume per-spell serialization. `_removal_lock` starts
            as None; the first direct `cleanup()` creates it under `_lock`.
""")
text = replace_in(text, H, """        super().__init__()
        self._lock = RLock()
        self._active = True""", """        super().__init__()
        self._lock = RLock()
        # Serializes direct cleanup() removals of this spell, which run outside `_lock`; created by the first direct
        # cleanup (`_direct_removal_route`) and taken by nothing else (direct_spell_cleanup_lock_order, 0.2.8233).
        self._removal_lock: Optional[RLock] = None
        self._active = True""")

H = "    def cleanup(self) -> None:"
text = replace_in(text, H, """            - Thread-safe: acquires `_lock`, re-checks `_cleaned`, and then
              performs teardown under the guarded section.
""", """            - Thread-safe: acquires `_lock`, re-checks `_cleaned`, and then
              performs teardown under the guarded section.
            - A direct call on a live spell - one its Spellbook is not driving
              (`_spellbook_cleanup` unset) - removes the spell through
              `Spellbook.cleanup_and_remove_spell`, which takes it off every
              registry and then calls back here for the local teardown. That
              removal runs outside `_lock`, under this spell's `_removal_lock`
              (created by the first direct call), so a second direct call waits
              for it and then returns.
""")
text = replace_in(text, H, """              `_spell_index_unless_cleaned` can still take it on a cleaned spell.
""", """              `_spell_index_unless_cleaned` can still take it on a cleaned spell.
              `_removal_lock` is deleted with the other fields; a direct call
              waiting on it holds its own reference.
""")
text = replace_in(text, H, """        Runtime resolution and instance lifecycle remain owned by the Resolution
        / Meld layer, not by this class.

        Returns:
            None.

        \"\"\"
""", """        Threading:
            The Book removal takes the Spellbook lock, frame locks and the Nexus
            record, while Book teardown (`Spellbook._cleanup_spells`, also
            reached from root and frame teardown) and conjure's ownership
            stamping (`define_conduit_into_spells`) take this spell's `_lock`
            under the Spellbook lock. Holding `_lock` across the removal hung both
            threads when they met (before 0.2.8233); now `_lock` covers only the
            decision (`_direct_removal_route`) and the local teardown. Nothing
            else in Melder takes `_removal_lock`, so it closes no lock-order
            cycle; a caller holding this spell's lock (`with spell:`) or another
            Melder lock around a direct call brings the old order back. A direct
            call racing its Book's teardown returns when the teardown cleaned the
            spell first, or raises the Book's cleaned RuntimeError; it does not
            hang. (direct_spell_cleanup_lock_order, 0.2.8233)

        Runtime resolution and instance lifecycle remain owned by the Resolution
        / Meld layer, not by this class.

        Returns:
            None.

        Raises:
            RuntimeError: On a direct call, from
                `Spellbook.cleanup_and_remove_spell`: the spell is not its Book's
                current active version (a parked version, for one), or the Book
                has been cleaned and did not clean this spell.

        \"\"\"
""")
text = replace_in(text, H, """        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            if not self._spellbook_cleanup:
                self._spellbook.cleanup_and_remove_spell(self)
                return

            if self.profile""", """        if self._cleaned:
            return
        direct_removal = self._direct_removal_route()
        if direct_removal is not None:
            # A direct call on a live spell: the Book takes it off its registries and calls back here with
            # `_spellbook_cleanup` set. Run that outside `_lock` - Book and frame teardown and conjure take `_lock`
            # under the Book lock - and serialize it per spell on the removal lock
            # (direct_spell_cleanup_lock_order, 0.2.8233).
            spellbook, removal_lock = direct_removal
            with removal_lock:
                if not self._cleaned:
                    spellbook.cleanup_and_remove_spell(self)
            return
        with self._lock:
            if self._cleaned:
                return

            if self.profile""")
text = replace_in(text, H, """            del self._spellbook_cleanup
            del self._spell_system_states
""", """            del self._spellbook_cleanup
            del self._removal_lock
            del self._spell_system_states
""")

text = replace_once(text, """            del self._compiler_artifact
            del self.spell_index


    #endregion Disposal
""", """            del self._compiler_artifact
            del self.spell_index

    def _direct_removal_route(self) -> Optional[tuple[Spellbook, RLock]]:
        \"\"\"
        Internal

        Decide under `_lock` whether `cleanup()` must remove this spell through
        its Spellbook, and hand back what that removal runs with.

        Purpose:
            Let `cleanup()` take its decision under the spell lock and run the
            Book removal after leaving it, so the spell lock is never held while
            the Spellbook, frame and Nexus locks are taken
            (direct_spell_cleanup_lock_order, 0.2.8233).

        Contract:
            - Returns None for a cleaned spell, and for a cleanup its Spellbook
              drives (`_spellbook_cleanup` set: Book teardown,
              `cleanup_and_remove_spell`, the parked disposal, Bind's retirement
              of an unpublished spell); `cleanup()` then runs the local teardown.
            - Otherwise returns the owning Spellbook and this spell's removal
              lock, creating the lock into `_removal_lock` on first use, so every
              direct cleanup of this spell meets the same lock.

        Threading:
            Reads and creates under `_lock` - the lock the teardown deletes the
            fields under - and calls nothing while holding it. The returned lock
            is taken by `cleanup()` alone, after this returns.

        Returns:
            Optional[tuple[Spellbook, RLock]]:
                The Book and the removal lock for a direct cleanup, or None.
        \"\"\"
        with self._lock:
            if self._cleaned or self._spellbook_cleanup:
                return None
            removal_lock = self._removal_lock
            if removal_lock is None:
                removal_lock = RLock()
                self._removal_lock = removal_lock
            return self._spellbook, removal_lock


    #endregion Disposal
""")
save(path, text)

# -------------------------------------------------------------- spellbook.py
path, text = load("src/melder/aether/spellbook/spellbook.py")

H = "    def cleanup_and_remove_spell(self, spell: Spell | str) -> None:"
text = replace_in(text, H, """        Raises:
            RuntimeError:
                If the spell is not found locally or is not owned by this
                Spellbook.
        \"\"\"
        self.check_cleaned()
        target_spell: Spell | None
        target_spell_id: str
        with self._lock:
            if isinstance(spell, str):""", """        Raises:
            RuntimeError:
                If the spell is not found locally or is not owned by this
                Spellbook.
            RuntimeError:
                If this Spellbook has been cleaned - including one torn down
                while the call waited for its lock, unless that teardown cleaned
                the Spell given (then the call returns).

        Threading:
            Resolves the spell, unregisters its index and drops it from `_spells`
            and `_lookup_spells` under the Spellbook lock; releases the lock for
            the risk-manager and Aether/frame calls; takes it again to drop the
            id maps (the Nexus record is removed after); releases the frame
            lookup; and cleans the spell and its index last, holding no Spellbook
            or frame lock itself. A direct `Spell.cleanup()` reaches here outside
            its spell lock (0.2.8233), so Book teardown and conjure's ownership
            stamping, which take spell locks under the Spellbook lock, never wait
            on a removal that waits on them. A call that passes `check_cleaned()`
            and then waits for the lock while the Book is torn down re-checks
            under it: teardown cleaned every active spell, so a Spell it cleaned
            returns and anything else raises the cleaned-Book error. A teardown
            that starts after the first locked section is not ordered against the
            rest of the removal (callers quiesce removals before tearing a Book
            down). (direct_spell_cleanup_lock_order, 0.2.8233)
        \"\"\"
        self.check_cleaned()
        target_spell: Spell | None
        target_spell_id: str
        with self._lock:
            if self._cleaned:
                # Torn down while this call waited for the lock: the maps below are gone. Book teardown cleaned every
                # active spell, so a Spell it cleaned has nothing left to remove; anything else gets the error a call
                # made after the teardown gets (direct_spell_cleanup_lock_order, 0.2.8233).
                if not isinstance(spell, str) and spell._cleaned:
                    return
                self.check_cleaned()
            if isinstance(spell, str):""")

H = "    def cleanup_spell(self, *, spell: Spell) -> None:"
text = replace_in(text, H, """            outside the Book lock, so the two locks are never nested here: a
            direct `Spell.cleanup` takes them spell -> Book, Book cleanup takes
            them Book -> spell. (cross_object_lock_gaps, 0.2.8231)
""", """            outside the Book lock, so the two locks are never nested here: Book
            cleanup and conjure's ownership stamping take them Book -> spell, and
            a direct `Spell.cleanup` no longer holds its spell lock when it
            reaches the Book (direct_spell_cleanup_lock_order, 0.2.8233).
            (cross_object_lock_gaps, 0.2.8231)
""")

H = "    def _dispose_spell(self, spell: Spell) -> Optional[str]:"
text = replace_in(text, H, """            # Classified outside the Book lock, so the two locks are never nested here: a direct Spell.cleanup takes
            # this Book's lock under the spell lock, and Book cleanup takes the spell lock under this Book's lock
            # (cross_object_lock_gaps, 0.2.8231; corrected lock_residuals, 0.2.8232).
""", """            # Classified outside the Book lock, so the two locks are never nested here: Book cleanup and conjure's
            # ownership stamping take the spell lock under this Book's lock (cross_object_lock_gaps, 0.2.8231;
            # corrected lock_residuals, 0.2.8232), and a direct Spell.cleanup no longer takes this Book's lock under
            # the spell lock (direct_spell_cleanup_lock_order, 0.2.8233).
""")
save(path, text)
print("applied 0.2.8233 to", ROOT)
