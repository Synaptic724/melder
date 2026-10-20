"""
Apply the 0.2.8232 source change set (lock_residuals_2026_10_11) to a tree.

Usage: python apply_0_2_8232.py <tree root holding src/>

conduit.py and spellbook.py are uniformly CRLF: each file is edited with LF line ends and written back with CRLF.
Every edit asserts its anchor exactly once inside the named method.
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


# ---------------------------------------------------------------- conduit.py
path, text = load("src/melder/aether/conduit/conduit.py")
H = "    def find_contracted_spell(self, spell_id: str) -> Optional[Spell]:"
text = replace_in(text, H, """        Threading:
            Walks the contract maps under the conduit lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.
""", """        Threading:
            Lock-free, like the other Conduit lookups. A link or sever started by a
            peer adds or removes that peer's id in the Book's `_contracted_spells`
            under the Book lock, holding the peer's conduit lock, not this one, so
            the peer ids are taken with one `list(...)` call - exact under
            concurrent writers on 3.14t, where walking the live keys raised
            "dictionary changed size during iteration" - and each peer is answered
            by `Spellbook._find_contracted_spell_by_id`, lock-free and keyed first.
            The copy is O(peers), the order of the walk itself. The Book lock is
            not taken: conjure holds it while phase workers and hooks run, and a
            hook calling this would deadlock. The conduit lock this used to take
            excluded none of those writers and made the parked-copy branch take a
            spell lock under it. A peer linked or severed during the call may be
            missed or still answered. (lock_residuals, 0.2.8232)

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. A teardown of this conduit racing the
            call is unsupported, as for every Conduit lookup.
""")
text = replace_in(text, H, """        self.check_cleaned()
        with self._lock:
            spellbook = self._spellbook

            # Walk all peer conduit contract maps in this spellbook
            for conduit_id in spellbook._contracted_spells.keys():
                # Delegate per-conduit search to Spellbook's helper
                spell = spellbook._find_contracted_spell_by_id(spell_id, conduit_id)
                if spell is not None:
                    return spell

        return None
""", """        self.check_cleaned()
        spellbook = self._spellbook

        # Walk all peer conduit contract maps in this spellbook. No lock is held: the peer ids are copied in one
        # call, because a link or sever the peer starts writes them under the Book lock (lock_residuals, 0.2.8232).
        for conduit_id in list(spellbook._contracted_spells):
            # Delegate per-conduit search to Spellbook's helper
            spell = spellbook._find_contracted_spell_by_id(spell_id, conduit_id)
            if spell is not None:
                return spell

        return None
""")
H = "    def inspect_spell("
text = replace_in(text, H, """            - Delegates to the spellbook's frame-wide inspection while holding the
              CONDUIT lock, so it inherits that method's three-stage search and its
              habit of collapsing every failure into None.
""", """            - Delegates to the spellbook's frame-wide inspection, so it inherits
              that method's three-stage search and its habit of collapsing every
              failure into None.
""")
text = replace_in(text, H, """        Threading:
            Holds the conduit lock across the spellbook call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.
""", """        Threading:
            Takes no lock of its own. Until 0.2.8232 it held the conduit lock across
            the spellbook call, which reaches frame locks (`Aether._check_for_spell`),
            while frame teardown takes the frame lock and then each conduit's lock
            (`Conduit.permanent_cleanup`): the two could hang each other.
            (lock_residuals, 0.2.8232)

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. A teardown of this conduit racing the
            call is unsupported, as for every Conduit lookup.
""")
text = replace_in(text, H, """        self.check_cleaned()
        with self._lock:
            return self._spellbook.inspect_spell(spell, aetheric_frame)
""", """        self.check_cleaned()
        return self._spellbook.inspect_spell(spell, aetheric_frame)
""")
H = "    def cleanup_spell(self, *, spell: Any) -> None:"
text = replace_in(text, H, """            RuntimeError: If the spell has already been disposed, is not owned by
                the owning Spellbook, or is the active member of a multi-member
                index (raised by `Spellbook.cleanup_spell`).
""", """            RuntimeError: If the spell has already been disposed, is being disposed
                by another call, is not owned by the owning Spellbook, or is the
                active member of a multi-member index (raised by
                `Spellbook.cleanup_spell`).
""")
text = replace_in(text, H, """            Takes no lock of its own. The Spellbook takes the Book lock and the
            spell's own lock (never nested); the destroy emission walks the
            ward's contracts under the ward lock, so a concurrent link or sever
            of this conduit waits for it. (cross_object_lock_gaps, 0.2.8231)
""", """            Takes no lock of its own. The Spellbook takes the Book lock and the
            spell's own lock (never nested); the destroy emission walks the
            ward's contracts under the ward lock, so a concurrent link or sever
            of this conduit waits for it. (cross_object_lock_gaps, 0.2.8231)
            Of two calls for one spell that overlap, the Spellbook lets the first
            dispose it and refuses the second, so the destroy is emitted once.
            (lock_residuals, 0.2.8232)
""")
save(path, text)

# -------------------------------------------------------------- spellbook.py
path, text = load("src/melder/aether/spellbook/spellbook.py")
H = "    def __init__(self, aetheric_frame: str = \"default\", configuration: SpellbookConfiguration | None = None,"
text = replace_in(text, H, """        self._inactive_spells: dict[str, Spell] = {}  # INACTIVE owned: spell_id -> parked spell (off resolution; repopulates the 7 active maps on notch-back)
""", """        self._inactive_spells: dict[str, Spell] = {}  # INACTIVE owned: spell_id -> parked spell (off resolution; repopulates the 7 active maps on notch-back)
        # DISPOSAL IN FLIGHT: ids `cleanup_spell` is disposing right now, read and written only under `_lock`, so a
        # second disposal of the same spell refuses instead of repeating the first (lock_residuals, 0.2.8232).
        self._disposing_spell_ids: set[str] = set()
""")
H = "    def _cleanup_components(self) -> None:"
text = replace_in(text, H, """            - Clears and nulls owned and contracted registries, lookup maps,
              version caches, and spell_id maps.
""", """            - Clears and nulls owned and contracted registries, lookup maps,
              version caches, spell_id maps, and the in-flight disposal marks.
""")
text = replace_in(text, H, """        del self._contracted_indexes
""", """        del self._contracted_indexes

        try:
            self._disposing_spell_ids.clear()
        except Exception as e:
            self._logger.error(f"Error cleaning _disposing_spell_ids: {e}", "_cleanup_components", exc_info=True)
        del self._disposing_spell_ids
""")
H = "    def inspect_spell("
text = replace_in(text, H, """        Threading:
            Holds the Spellbook lock for the entire search, including the frame-wide walk
            across other conduits' spellbooks.
""", """        Threading:
            Holds this Spellbook's lock only while stage 1 walks this Spellbook's own
            spells, the lock bind and removal write them under. Stage 2, stage 3 and
            every registry confirmation run with no lock held here: the Aether and
            frame reads take frame locks, and frame teardown takes this Spellbook's
            lock under its frame lock, so holding it through them could hang
            against a racing frame teardown (until 0.2.8232 it was held for the
            whole search). Stage 2 walks a one-call copy of the frame's conduit map,
            which root registration and removal write under the frame lock, and a
            one-call copy of each other Spellbook's spell map (0.2.8230); a conduit
            or spell added or removed during the walk may be missed or still seen.
            (lock_residuals, 0.2.8232)
""")
OLD_INSPECT = '''        with self._lock:
            try:
                # The spell fingerprint composes bind-time facts (existence,
                # disposal methods, binding name, spell name) that a bare
                # class/function/instance cannot supply, so re-deriving the
                # id from the object alone can never match a registered
                # binding. Resolve by object identity against this
                # Spellbook's registered spells first; fall back to the
                # legacy default-fact fingerprint for foreign objects so
                # cross-book inspection semantics stay unchanged.
                for candidate_spell in self._spells.values():
                    if (
                            candidate_spell.spell is spell
                            or candidate_spell.user_created_object is spell
                    ):
                        candidate_spell_id = candidate_spell.spell_index.selected_spell_id
                        found = Spellbook._aether._check_for_spell(
                            candidate_spell_id,
                            aetheric_frame,
                        )
                        return candidate_spell_id if found else None
                # Frame-wide object inspection: walk the frame's registered
                # conduits' spellbooks so foreign spells (cluster shares,
                # dynamic-link providers) remain inspectable by object, which
                # the legacy fingerprint path provided before bind-time facts
                # joined the id composition.
                if aetheric_frame != "default":
                    frame = Spellbook._aether._aetheric_frames[aetheric_frame]
                else:
                    frame = Spellbook._aether._ensure_default_frame()
                for frame_conduit in frame._conduits.values():
                    conduit_spellbook = frame_conduit._spellbook
                    if conduit_spellbook is None or conduit_spellbook is self:
                        continue
                    # Another Book's map, read without that Book's lock: walk a one-call snapshot.
                    for candidate_spell in list(conduit_spellbook._spells.values()):
                        if (
                                candidate_spell.spell is spell
                                or candidate_spell.user_created_object is spell
                        ):
                            candidate_spell_id = (
                                candidate_spell.spell_index.selected_spell_id
                            )
                            found = Spellbook._aether._check_for_spell(
                                candidate_spell_id,
                                aetheric_frame,
                            )
                            return candidate_spell_id if found else None
                spell_id = self._bind.spell_id_inspector(spell)
                found = Spellbook._aether._check_for_spell(spell_id, aetheric_frame)
                return spell_id if found else None
            except Exception as e:
                self._logger.error(f"Failed to inspect spell: {e}", "inspect_spell", exc_info=True)
                return None
'''
NEW_INSPECT = '''        try:
            # The spell fingerprint composes bind-time facts (existence,
            # disposal methods, binding name, spell name) that a bare
            # class/function/instance cannot supply, so re-deriving the
            # id from the object alone can never match a registered
            # binding. Resolve by object identity against this
            # Spellbook's registered spells first; fall back to the
            # legacy default-fact fingerprint for foreign objects so
            # cross-book inspection semantics stay unchanged.
            # Only this walk holds this Spellbook's lock, the lock its writers hold: the confirmation and the stages
            # below take frame locks, and frame teardown takes this lock under its frame lock
            # (lock_residuals, 0.2.8232).
            matched = False
            candidate_spell_id: Optional[str] = None
            with self._lock:
                for candidate_spell in self._spells.values():
                    if (
                            candidate_spell.spell is spell
                            or candidate_spell.user_created_object is spell
                    ):
                        candidate_spell_id = candidate_spell.spell_index.selected_spell_id
                        matched = True
                        break
            if matched:
                found = Spellbook._aether._check_for_spell(
                    candidate_spell_id,
                    aetheric_frame,
                )
                return candidate_spell_id if found else None
            # Frame-wide object inspection: walk the frame's registered
            # conduits' spellbooks so foreign spells (cluster shares,
            # dynamic-link providers) remain inspectable by object, which
            # the legacy fingerprint path provided before bind-time facts
            # joined the id composition.
            if aetheric_frame != "default":
                frame = Spellbook._aether._aetheric_frames[aetheric_frame]
            else:
                frame = Spellbook._aether._ensure_default_frame()
            # Root registration and removal write the frame's conduit map under the frame lock, which is not held
            # here: walk a one-call snapshot (lock_residuals, 0.2.8232).
            for frame_conduit in list(frame._conduits.values()):
                conduit_spellbook = frame_conduit._spellbook
                if conduit_spellbook is None or conduit_spellbook is self:
                    continue
                # Another Book's map, read without that Book's lock: walk a one-call snapshot.
                for candidate_spell in list(conduit_spellbook._spells.values()):
                    if (
                            candidate_spell.spell is spell
                            or candidate_spell.user_created_object is spell
                    ):
                        candidate_spell_id = (
                            candidate_spell.spell_index.selected_spell_id
                        )
                        found = Spellbook._aether._check_for_spell(
                            candidate_spell_id,
                            aetheric_frame,
                        )
                        return candidate_spell_id if found else None
            spell_id = self._bind.spell_id_inspector(spell)
            found = Spellbook._aether._check_for_spell(spell_id, aetheric_frame)
            return spell_id if found else None
        except Exception as e:
            self._logger.error(f"Failed to inspect spell: {e}", "inspect_spell", exc_info=True)
            return None
'''
text = replace_in(text, H, OLD_INSPECT, NEW_INSPECT)

H = "    def cleanup_spell(self, *, spell: Spell) -> None:"
text = replace_in(text, H, """            RuntimeError: If the spell has already been disposed ("cleanup_spell:
                spell <id> has already been disposed."; before 0.2.8231 a second
                call raised AttributeError), is not owned here, or is the active
                member of a multi-member index.
""", """            RuntimeError: If the spell has already been disposed ("cleanup_spell:
                spell <id> has already been disposed."; before 0.2.8231 a second
                call raised AttributeError), is not owned here, or is the active
                member of a multi-member index.
            RuntimeError: If another cleanup_spell of the same spell is still
                running ("cleanup_spell: spell <id> is already being disposed by
                another call."; before 0.2.8232 both calls ran the disposal).
""")
text = replace_in(text, H, """            Ownership, activity and sole membership are read under the Book lock
            from the Book's own maps; a spell no longer in them is classified
            through the spell's own lock (`Spell._spell_index_unless_cleaned`),
            outside the Book lock, because `Spell.cleanup` takes the spell lock
            before the Book lock. (cross_object_lock_gaps, 0.2.8231)
""", """            Ownership, activity and sole membership are read under the Book lock
            from the Book's own maps; a spell no longer in them is classified
            through the spell's own lock (`Spell._spell_index_unless_cleaned`),
            outside the Book lock, so the two locks are never nested here: a
            direct `Spell.cleanup` takes them spell -> Book, Book cleanup takes
            them Book -> spell. (cross_object_lock_gaps, 0.2.8231)
            The same locked section marks the spell id as being disposed and the
            disposal clears the mark when it ends, so of two calls for one spell
            that overlap, the second refuses before touching anything. The spell
            lock is not held across the disposal: that would take the Book and
            frame locks under it, against Book and frame teardown, which take the
            spell lock under theirs. (lock_residuals, 0.2.8232)
""")

H = "    def _dispose_spell(self, spell: Spell) -> Optional[str]:"
text = replace_in(text, H, """            - Returns the destroyed index's id when the spell was the sole member
              of its index (an active sole member, or the last inactive member);
              None when other members keep the index alive.
""", """            - Returns the destroyed index's id when the spell was the sole member
              of its index (an active sole member, or the last inactive member);
              None when other members keep the index alive.
            - Marks the spell id in `_disposing_spell_ids` in the decision's own
              Book-locked section, and clears it under the Book lock when the
              disposal ends (finished or failed), so a second call for the same
              spell that starts meanwhile refuses before it touches anything.
""")
text = replace_in(text, H, """            As `cleanup_spell`. (cross_object_lock_gaps, 0.2.8231)
""", """            As `cleanup_spell`. (cross_object_lock_gaps, 0.2.8231; the in-flight
            mark, lock_residuals, 0.2.8232)
""")
text = replace_in(text, H, """        is_sole = False
        with self._lock:
            is_active = self._spells_by_id.get(spell_id) is spell
            owned = is_active or self._inactive_spells.get(spell_id) is spell
            if owned:
                # Still in this Book's maps, so no cleanup has popped it, and Spell.cleanup deletes the spell's
                # fields only after that pop (under this lock): its index is live here. Index moves repoint it
                # under this lock too.
                index = spell.spell_index
                index_id = index.id
                is_sole = index.is_sole_member(spell_id)
        if not owned:
            # Classified outside the Book lock: the spell's own lock is taken before this Book's lock by
            # Spell.cleanup, so it is never taken under it (cross_object_lock_gaps, 0.2.8231).
""", """        is_sole = False
        already_disposing = False
        with self._lock:
            # A disposal of this spell already in flight: refuse before reading or touching anything
            # (lock_residuals, 0.2.8232).
            already_disposing = spell_id in self._disposing_spell_ids
            if not already_disposing:
                is_active = self._spells_by_id.get(spell_id) is spell
                owned = is_active or self._inactive_spells.get(spell_id) is spell
                if owned:
                    # Still in this Book's maps, so no cleanup has popped it, and Spell.cleanup deletes the spell's
                    # fields only after that pop (under this lock): its index is live here. Index moves repoint it
                    # under this lock too.
                    index = spell.spell_index
                    index_id = index.id
                    is_sole = index.is_sole_member(spell_id)
                    if is_sole or not is_active:
                        # This call disposes it: mark it in the decision's own locked section, so a second call
                        # that starts before this one ends refuses instead of repeating the disposal; cleared in the
                        # finally below (lock_residuals, 0.2.8232).
                        self._disposing_spell_ids.add(spell_id)
        if already_disposing:
            raise RuntimeError(
                f"cleanup_spell: spell {spell_id} is already being disposed by another call."
            )
        if not owned:
            # Classified outside the Book lock, so the two locks are never nested here: a direct Spell.cleanup takes
            # this Book's lock under the spell lock, and Book cleanup takes the spell lock under this Book's lock
            # (cross_object_lock_gaps, 0.2.8231; corrected lock_residuals, 0.2.8232).
""")
# Wrap the disposal branches (from the CLEAN UP comment to the end of the method) in try/finally.
begin, finish = span(text, H)
body = text[begin:finish]
anchor = "        # CLEAN UP. Only an ACTIVE spell is invalidated first: flag it + its lineage\n"
assert body.count(anchor) == 1
head, tail = body.split(anchor, 1)
tail = anchor + tail
tail_lines = tail.split("\n")
while tail_lines and tail_lines[-1] == "":
    tail_lines.pop()
trailing_blank = body[len(body.rstrip("\n")):]
indented = "\n".join(("    " + line) if line else line for line in tail_lines)
wrapped = (
    "        # Reached only when this call marked the spell above: nothing between the mark and here can raise.\n"
    "        try:\n"
    + indented + "\n"
    "        finally:\n"
    "            # The disposal is over, finished or failed: a later call for this spell decides afresh\n"
    "            # (lock_residuals, 0.2.8232).\n"
    "            with self._lock:\n"
    "                self._disposing_spell_ids.discard(spell_id)\n"
)
text = text[:begin] + head + wrapped + trailing_blank[1:] + text[finish:]
save(path, text)
print("applied 0.2.8232 to", ROOT)
