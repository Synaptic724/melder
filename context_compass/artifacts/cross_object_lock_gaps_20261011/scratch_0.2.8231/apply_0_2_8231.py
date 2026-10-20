"""
Apply the 0.2.8231 source change set (cross_object_lock_gaps_2026_10_11) to a tree.

Usage: python apply_0_2_8231.py <tree root holding src/>

Every edit asserts its anchor once and keeps each file's line endings (conduit_ward.py mixes CRLF and LF lines, so
inserted lines take the ending of the line they sit beside).
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
TAG = "(cross_object_lock_gaps, 0.2.8231)"


def load(rel: str) -> tuple[pathlib.Path, list[str]]:
    path = ROOT / rel
    return path, path.read_bytes().decode("utf-8").splitlines(keepends=True)


def save(path: pathlib.Path, lines: list[str]) -> None:
    path.write_bytes("".join(lines).encode("utf-8"))


def eol(line: str) -> str:
    return "\r\n" if line.endswith("\r\n") else "\n"


def method_span(lines: list[str], header: str) -> tuple[int, int]:
    starts = [i for i, line in enumerate(lines) if line.startswith(header)]
    assert len(starts) == 1, (header, starts)
    start = starts[0]
    end = start + 1
    while end < len(lines) and not lines[end].startswith(("    def ", "    @", "    async def ")):
        end += 1
    return start, end


def docstring_close(lines: list[str], start: int, end: int) -> int:
    opens = [i for i in range(start, end) if lines[i].strip() == '"""']
    assert len(opens) >= 2, ("docstring", lines[start])
    return opens[1]


def add_doc(lines: list[str], header: str, doc_lines: list[str]) -> None:
    start, end = method_span(lines, header)
    close = docstring_close(lines, start, end)
    e = eol(lines[close])
    lines[close:close] = [(f"        {text}" if text else "") + e for text in doc_lines]


def replace_span(lines: list[str], header: str, first: str, last: str, new_block: list[str]) -> None:
    start, end = method_span(lines, header)
    firsts = [i for i in range(start, end) if lines[i].rstrip("\r\n") == first]
    lasts = [i for i in range(start, end) if lines[i].rstrip("\r\n") == last]
    assert len(firsts) == 1 and len(lasts) == 1 and firsts[0] <= lasts[0], (header, first, last, firsts, lasts)
    e = eol(lines[firsts[0]])
    lines[firsts[0]:lasts[0] + 1] = [text + e if text else e for text in new_block]


def wrap_walk(lines: list[str], header: str, comment: list[str]) -> None:
    start, end = method_span(lines, header)
    loop = "        for contract in self._contracts.values():"
    hits = [i for i in range(start, end) if lines[i].rstrip("\r\n") == loop]
    assert len(hits) == 1, (header, hits)
    i0 = hits[0]
    e = eol(lines[i0])
    j = i0 + 1
    while j < end:
        text = lines[j].rstrip("\r\n")
        if text and len(text) - len(text.lstrip(" ")) <= 8:
            break
        j += 1
    body = lines[i0:j]
    lines[i0:j] = ([f"        # {c}{e}" for c in comment] + [f"        with self._lock:{e}"]
                   + [("    " + line) if line.strip() else line for line in body])


def replace_once(lines: list[str], old: str, new: list[str]) -> None:
    hits = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == old]
    assert len(hits) == 1, (old, hits)
    e = eol(lines[hits[0]])
    lines[hits[0]:hits[0] + 1] = [text + e if text else e for text in new]


EMIT_THREADING = [
    "Threading:",
    "    Walks this ward's contract registry under the ward lock, the lock link",
    "    (`_create_new_contract`) and sever (`_remove_contract`) write it under.",
    "    The caller runs this after its transaction has ended (notch, index moves,",
    "    bind_inactive) or with none (`Conduit.cleanup_spell`), so the mediator",
    "    does not order it against a link or sever; the ward lock does. Inside it",
    "    the walk takes peer Book and contract locks in the order sever already",
    "    takes (ward -> contract -> Book); contract records, when any, are",
    "    emitted after the lock is released. " + TAG,
]
EMIT_COMMENT = [
    "Under this ward's lock: link and sever write _contracts under it, and this emission runs outside any",
    "transaction window, so the mediator does not order it against them " + TAG + ".",
]

# ---------------------------------------------------------------- conduit_ward.py
path, lines = load("src/melder/aether/conduit/conduit_ward/conduit_ward.py")
for header in ("    def _emit_index_notch(", "    def _emit_index_destroy(",
               "    def _emit_index_member_added(", "    def _emit_index_member_removed("):
    add_doc(lines, header, [""] + EMIT_THREADING)
    wrap_walk(lines, header, EMIT_COMMENT)

replace_once(lines, "        added = contract._add(owner_ward, detail)", [
    "        # Under the contract lock, as _uncontract_member_spell removes under it: a borrower's contract",
    "        # inspection walks this detail map under that lock " + TAG + ".",
    "        with contract._lock:",
    "            added = contract._add(owner_ward, detail)",
])
add_doc(lines, "    def _contract_member_spell(", [
    "Threading:",
    "    Writes the owner's Detail under the contract lock (the lock its readers",
    "    and `_uncontract_member_spell` hold) and calls the borrower's Book after",
    "    releasing it. " + TAG,
])

replace_span(lines, "    def _get_spell_in_contracts(",
             "                detail_map = contract._get_detail_map(peer_ward)",
             "                    return peer_ward._id, spell", [
    "                # The peer writes this detail map under the contract lock (members gained or lost, contract",
    "                # grants), outside any lock this ward holds; walk it under the same lock so the walk never",
    "                # meets a resize or a Detail being torn down, and resolve after releasing it",
    "                # " + TAG + ".",
    "                spell_index = None",
    "                with contract._lock:",
    "                    detail_map = contract._get_detail_map(peer_ward)",
    "                    # O(1) first: the detail contracted for exactly this version. The lineage walk runs",
    "                    # only when the id is another version of a contracted lineage; every detail whose index",
    "                    # holds the id shares that index, so both paths resolve the same head.",
    "                    detail = detail_map.get(spell_id)",
    "                    if detail is not None and detail.has_spell(spell_id):",
    "                        spell_index = detail.spell_index",
    "                    else:",
    "                        for detail in detail_map.values():",
    "                            if detail.has_spell(spell_id):",
    "                                spell_index = detail.spell_index",
    "                                break",
    "                if spell_index is None:",
    "                    continue",
    "                try:",
    "                    spell = self._conduit._spellbook._find_contracted_spell(spell_index)",
    "                except Exception as e:",
    "                    self._logger.error(",
    "                        f\"_get_spell_in_contracts: contracted spell lookup failed \"",
    "                        f\"for version={spell_id}, index={spell_index}: {e}\",",
    "                        method_name=\"_get_spell_in_contracts\",",
    "                        exc_info=True,",
    "                        owner_id=self._id,",
    "                        owner_display=self._display_name,",
    "                        mask=True,",
    "                        groups=self._log_groups,",
    "                        system_groups=self._log_sysgroups,",
    "                    )",
    "                    return None",
    "",
    "                if spell is None:",
    "                    return None",
    "                return peer_ward._id, spell",
])
add_doc(lines, "    def _get_spell_in_contracts(", [
    "Threading:",
    "    Holds this ward's lock for the walk of its contracts and each contract's",
    "    lock for the walk of that contract's detail map (the lock its writers",
    "    hold); tries the detail keyed by the id (O(1)) before walking; resolves the",
    "    matched index through this conduit's Book after the contract lock is",
    "    released. " + TAG,
])

replace_span(lines, "    def _get_spells_in_contract_by_conduit(",
             "            peer_ward = contract._get_peer(self)",
             "        return spells_result", [
    "            peer_ward = contract._get_peer(self)",
    "            spellbook = self._conduit._spellbook",
    "",
    "            # Walk both detail maps under the contract lock their writers hold and resolve each id by key",
    "            # through this conduit's Book. Never through the Conduit lookups: find_contracted_spell takes the",
    "            # conduit lock, which link and sever hold before the ward lock held here, and the two deadlocked",
    "            # " + TAG + ".",
    "            with contract._lock:",
    "                # Inbound: spells the peer has granted to us (live in peer's detail map).",
    "                for sid in contract._get_detail_map(peer_ward):",
    "                    spell = spellbook._find_contracted_spell_by_id(sid, peer_ward._id)",
    "                    if spell:",
    '                        spells_result["inbound"].append((sid, spell))',
    "",
    "                # Outbound: spells we have granted to the peer (live in our detail map), answered from this",
    "                # Book's own id maps in O(1).",
    "                for sid in contract._get_detail_map(self):",
    "                    owned_spell = spellbook.find_spell_by_id(sid)",
    "                    if owned_spell is not None:",
    '                        spells_result["outbound"].append((sid, owned_spell))',
    "",
    "        return spells_result",
])
add_doc(lines, "    def _get_spells_in_contract_by_conduit(", [
    "Threading:",
    "    Holds this ward's lock throughout and the contract's lock while it walks",
    "    the two detail maps; resolves each id by key through this conduit's Book,",
    "    taking no conduit lock (link and sever take the conduit lock before the",
    "    ward lock, and the Conduit lookups used here before deadlocked with",
    "    them). " + TAG,
])
save(path, lines)

# ---------------------------------------------------------------- conduit.py
path, lines = load("src/melder/aether/conduit/conduit.py")
start, end = method_span(lines, "    def cleanup_spell(self, *, spell: Any) -> None:")
e = eol(lines[start])
new_method = '''    def cleanup_spell(self, *, spell: Any) -> None:
        """
        Public API

        Conduit facade for fully disposing an owned spell. Delegates to the
        owning Spellbook, which removes the spell from every resolution surface,
        destroys its index if it was the sole member, and tears the spell object
        down; when the index was destroyed, its index-link borrowers drop their
        subscription to it.

        Contract:
            - The Spellbook decides, under its own lock, whether the disposal
              destroys the spell's index, and reports the destroyed index's id;
              the destroy is emitted to index-link borrowers exactly then, with
              the disposed spell as the index's one member (an index is destroyed
              only when the spell was its sole member). Nothing about the spell or
              its index is read here before that decision.
            - Not admitted through a transaction (no cleanup strategy exists).

        Args:
            spell: The owned spell to dispose.

        Raises:
            RuntimeError: If the Conduit is cleaned or has no owning Spellbook.
            RuntimeError: If the spell has already been disposed, is not owned by
                the owning Spellbook, or is the active member of a multi-member
                index (raised by `Spellbook.cleanup_spell`).

        Threading:
            Takes no lock of its own. The Spellbook takes the Book lock and the
            spell's own lock (never nested); the destroy emission walks the
            ward's contracts under the ward lock, so a concurrent link or sever
            of this conduit waits for it. ''' + TAG + '''

        Returns:
            None.
        """
        self.check_cleaned()
        if self._spellbook is None:
            raise RuntimeError("[CONDUIT] No owning Spellbook for cleanup_spell.")
        spell_id = spell.spell_id
        # The Spellbook's own locked decision says whether the index went with the spell; the old unlocked
        # pre-read of spell.spell_index here raised AttributeError for a disposed spell and could disagree with
        # what the Spellbook then did ''' + TAG + '''.
        destroyed_index_id = self._spellbook._dispose_spell(spell)
        # A destroyed index-linked lineage must be dropped on its receivers so they
        # do not keep a subscription to a dead index.
        if destroyed_index_id is not None:
            self._conduit_ward._emit_index_destroy(destroyed_index_id, (spell_id,))

'''
lines[start:end] = [text + e for text in new_method.split("\n")[:-1]]
save(path, lines)

# ---------------------------------------------------------------- spellbook.py
path, lines = load("src/melder/aether/spellbook/spellbook.py")
start, end = method_span(lines, "    def cleanup_spell(self, *, spell: Spell) -> None:")
body = "".join(lines[start:end]).replace("\r\n", "\n")
old_head = '''        self.check_cleaned()
        spell_id = spell.spell_id
        if spell._spellbook is not self:
            self._logger.error(
                f"cleanup_spell: spell {spell_id} is not owned by this spellbook.",
                "cleanup_spell",
                exc_info=True,
            )
            raise RuntimeError(
                f"cleanup_spell: spell {spell_id} is not owned by this spellbook."
            )
        index = spell.spell_index
        with self._lock:
            is_active = spell_id in self._spells_by_id
            is_sole = index.is_sole_member(spell_id)
            if is_active and not is_sole:
'''
new_head = '''        self.check_cleaned()
        spell_id = spell.spell_id
        owned = False
        is_active = False
        is_sole = False
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
            # Spell.cleanup, so it is never taken under it ''' + TAG + '''.
            if spell._spell_index_unless_cleaned() is None:
                raise RuntimeError(f"cleanup_spell: spell {spell_id} has already been disposed.")
            self._logger.error(
                f"cleanup_spell: spell {spell_id} is not owned by this spellbook.",
                "cleanup_spell",
                exc_info=True,
            )
            raise RuntimeError(
                f"cleanup_spell: spell {spell_id} is not owned by this spellbook."
            )
        with self._lock:
            if is_active and not is_sole:
'''
assert body.count(old_head) == 1
body = body.replace(old_head, new_head)
old_active = '''            spell.invalidate_spell(change_reason=SpellStateChangeReason.cleaned_up_spell)
            self.cleanup_and_remove_spell(spell)
        else:
'''
new_active = '''            spell.invalidate_spell(change_reason=SpellStateChangeReason.cleaned_up_spell)
            self.cleanup_and_remove_spell(spell)
            return index_id
        else:
'''
assert body.count(old_active) == 1
body = body.replace(old_active, new_active)
old_tail = '''            spell._spellbook_cleanup = True
            spell.cleanup()
'''
new_tail = '''            spell._spellbook_cleanup = True
            spell.cleanup()
            return index_id if index_emptied else None
'''
assert body.count(old_tail) == 1 and body.endswith(old_tail + "\n")
body = body.replace(old_tail, new_tail)
old_def = "    def cleanup_spell(self, *, spell: Spell) -> None:\n"
assert body.startswith(old_def)
doc_end = body.index('        """\n', body.index('"""') + 3) + len('        """\n')
old_doc = body[len(old_def):doc_end]
dispose_doc = '''        """
        Internal

        The body of `cleanup_spell`, returning what the owning Conduit needs to
        tell index-link borrowers: the id of the index the disposal destroyed, or
        None when the index survived.

        Contract:
            - Same checks, order and disposal as `cleanup_spell`.
            - Returns the destroyed index's id when the spell was the sole member
              of its index (an active sole member, or the last inactive member);
              None when other members keep the index alive.

        Args:
            spell: The owned spell to dispose.

        Returns:
            Optional[str]: The destroyed index's id, or None.

        Raises:
            RuntimeError: As `cleanup_spell`.

        Threading:
            As `cleanup_spell`. ''' + TAG + '''
        """
'''
old_doc_lines = old_doc
assert "            - NOTE: not yet sealed by a mediator transaction (no cleanup strategy\n" in old_doc_lines
new_public_doc = old_doc_lines.replace(
    '''        Raises:
            RuntimeError: If the spell is not owned here, or it is the active
                member of a multi-member index.
''',
    '''        Raises:
            RuntimeError: If the spell has already been disposed ("cleanup_spell:
                spell <id> has already been disposed."; before 0.2.8231 a second
                call raised AttributeError), is not owned here, or is the active
                member of a multi-member index.

        Threading:
            Ownership, activity and sole membership are read under the Book lock
            from the Book's own maps; a spell no longer in them is classified
            through the spell's own lock (`Spell._spell_index_unless_cleaned`),
            outside the Book lock, because `Spell.cleanup` takes the spell lock
            before the Book lock. ''' + TAG + '''
''')
assert new_public_doc != old_doc_lines
public = old_def + new_public_doc + "        self._dispose_spell(spell)\n\n"
dispose = "    def _dispose_spell(self, spell: Spell) -> Optional[str]:\n" + dispose_doc + body[doc_end:]
new_text = public + dispose
e = eol(lines[start])
lines[start:end] = [text + e for text in new_text.split("\n")[:-1]]
start, end = method_span(lines, "    def _find_contracted_spell_by_id(self, spell_id: str, conduit_id: str) -> Spell | None:")
body = "".join(lines[start:end]).replace("\r\n", "\n")
DQ = '"' * 3
old_threading = (
    "        Threading:\n"
    "            Lock-free. Walks a one-call snapshot of the contracted map, which grants and revocations change\n"
    "            while no lock is held here, and probes each index with `SpellIndex._has_spell_unless_cleaned`:\n"
    "            the lender can clean an index this map still holds, and a cleaned index owns nothing (0.2.8230).\n"
    "        " + DQ + "\n"
)
new_threading = (
    "        Threading:\n"
    "            Lock-free. Answers by key first " + TAG + ": the active borrowed copy is held in\n"
    "            `_contracted_spells_by_id` under its own version id, and a parked one in\n"
    "            `_inactive_contracted_spells`, whose index (read under the parked spell's own lock) keys the\n"
    "            lineage's active copy in `_contracted_spells` - single-key reads, no copy. Only a version this\n"
    "            Book holds no copy of falls back to the walk: a one-call snapshot of the contracted map, which\n"
    "            grants and revocations change while no lock is held here, probing each index with\n"
    "            `SpellIndex._has_spell_unless_cleaned` (the lender can clean an index this map still holds, and\n"
    "            a cleaned index owns nothing; 0.2.8230).\n"
    "        " + DQ + "\n"
)
assert body.count(old_threading) == 1
body = body.replace(old_threading, new_threading)
old_lookup = (
    "        # Pull the map of SpellIndex? Spell for this conduit\n"
    "        spell_map = self._contracted_spells.get(conduit_id)\n"
    "        if spell_map is None:\n"
    "            return None\n"
)
new_lookup = (
    "        # O(1) first: the active borrowed copy under its own version id.\n"
    "        active_by_id = self._contracted_spells_by_id.get(conduit_id)\n"
    "        if active_by_id is not None:\n"
    "            active = active_by_id.get(spell_id)\n"
    "            if active is not None:\n"
    "                return active\n"
    "        # Pull the map of SpellIndex? Spell for this conduit\n"
    "        spell_map = self._contracted_spells.get(conduit_id)\n"
    "        if spell_map is None:\n"
    "            return None\n"
    "        # Still O(1): a parked borrowed copy's index keys its lineage's active copy.\n"
    "        parked = self._inactive_contracted_spells.get(conduit_id)\n"
    "        if parked is not None:\n"
    "            parked_spell = parked.get(spell_id)\n"
    "            if parked_spell is not None:\n"
    "                parked_index = parked_spell._spell_index_unless_cleaned()\n"
    "                if parked_index is not None:\n"
    "                    head = spell_map.get(parked_index)\n"
    "                    if head is not None:\n"
    "                        return head\n"
)
assert body.count(old_lookup) == 1
body = body.replace(old_lookup, new_lookup)
e = eol(lines[start])
lines[start:end] = [text + e for text in body.split("\n")[:-1]]
save(path, lines)

# ---------------------------------------------------------------- aetheric_frame.py
path, lines = load("src/melder/aether/aetheric_frame/aetheric_frame.py")
for header in ("    def has_spell(self, spell_id: str) -> bool:", "    def spells_in_index(self) -> set[str]:"):
    start, end = method_span(lines, header)
    hits = [i for i in range(start, end) if lines[i].rstrip("\r\n") == "        with self._lock:"]
    assert len(hits) == 1, (header, hits)
    e = eol(lines[hits[0]])
    lines[hits[0] + 1:hits[0] + 1] = [
        "            # Again under the lock cleanup() deletes the registries under: a racing cleanup raises the" + e,
        "            # documented RuntimeError, never AttributeError " + TAG + "." + e,
        "            self.check_cleaned()" + e,
    ]
    add_doc(lines, header, [
        "",
        "Raises:",
        "    RuntimeError: If the frame is cleaned, including by a cleanup that",
        "        races this call (checked again under the frame lock). " + TAG,
    ])
# The public spells_in_index copies each conjured Book's LIVE `_spell_ids` with one update call: the Book writes that
# set under its own lock, so the element-by-element copy raised "Set changed size during iteration" (Note 10).
replace_span(lines, "    def spells_in_index(self) -> set[str]:",
             "            for spell_id_set in self._selected_spell_registry.values():",
             "                    result.add(spell_id)", [
    "            # One update call per conjured Book: each value is a LIVE reference to that Book's `_spell_ids`, which",
    "            # the Book writes under its own lock, not this one, so an element-by-element copy raised \"Set changed",
    "            # size during iteration\" while that Book bound " + TAG + ".",
    "            for spell_id_set in self._selected_spell_registry.values():",
    "                result.update(spell_id_set)",
])
add_doc(lines, "    def spells_in_index(self) -> set[str]:", [
    "",
    "Threading:",
    "    Holds the frame lock for the read and takes each conjured Book's live",
    "    `_spell_ids` with one `set.update` call, so a bind into that Book on",
    "    another thread cannot tear the copy. " + TAG,
])
start, end = method_span(lines, "    def find_index_for_spell(self, spell_id: str) -> SpellIndex | None:")
e = eol(lines[start])
probes = '''    def _has_spell_unless_cleaned(self, spell_id: str) -> bool:
        \"\"\"
        Internal

        `has_spell` for a caller that does not own this frame: False once the
        frame is cleaned instead of raising.

        Purpose:
            Let Aether's cross-frame duplicate sweep ask a frame that another
            thread may be tearing down; a frame being torn down holds nothing.

        Returns:
            bool: `has_spell(spell_id)` while the frame is live; False when cleaned.

        Threading:
            Takes the frame lock once - the lock cleanup() sets `_cleaned` and
            deletes the registries under, and keeps - so the check and the read
            cannot interleave with it. The membership test is `has_spell`'s: one
            `in` per conjured Book's live `_spell_ids`, a single call that a
            concurrent bind into that Book cannot tear. No re-entry, no second
            check on the bind path, no other lock. ''' + TAG + '''
        \"\"\"
        if not spell_id:
            return False
        with self._lock:
            if self._cleaned:
                return False
            for spell_id_set in self._selected_spell_registry.values():
                if spell_id in spell_id_set:
                    return True
        return False

    def _find_index_for_spell_unless_cleaned(self, spell_id: str) -> Optional[SpellIndex]:
        \"\"\"
        Internal

        `find_index_for_spell` for a caller that does not own this frame: None
        once the frame is cleaned instead of raising.

        Returns:
            Optional[SpellIndex]: The index whose lineage holds `spell_id` while the
                frame is live; None when none does or the frame is cleaned.

        Threading:
            Takes the frame lock once, as `_has_spell_unless_cleaned`, and asks each
            index `SpellIndex._has_spell_unless_cleaned` under that index's lock (the
            frame -> index order `find_index_for_spell` already takes): one O(1)
            membership test per index, where `find_index_for_spell` copies every
            index's member set, and an index cleaned meanwhile answers False
            instead of raising. ''' + TAG + '''
        \"\"\"
        if not spell_id:
            return None
        with self._lock:
            if self._cleaned:
                return None
            for spell_set in self._spell_registry.values():
                for spell_index in spell_set:
                    if spell_index._has_spell_unless_cleaned(spell_id):
                        return spell_index
        return None

    def _spells_in_index_unless_cleaned(self) -> set[str]:
        \"\"\"
        Internal

        `spells_in_index` for a caller that does not own this frame: an empty
        set once the frame is cleaned instead of raising.

        Returns:
            set[str]: The frame's cached version ids while it is live; empty when
                cleaned.

        Threading:
            As `_has_spell_unless_cleaned`; each conjured Book's live `_spell_ids`
            is taken with one `set.update` call, exact while that Book binds.
            ''' + TAG + '''
        \"\"\"
        result: set[str] = set()
        with self._lock:
            if self._cleaned:
                return result
            for spell_id_set in self._selected_spell_registry.values():
                result.update(spell_id_set)
        return result

'''
lines[end:end] = [text + e for text in probes.split("\n")[:-1]]
save(path, lines)

# AethericFrame.cleanup keeps the frame lock, as Spell keeps its own: the probes above and the re-checks in
# has_spell / spells_in_index take it on a frame another thread may have cleaned.
path, lines = load("src/melder/aether/aetheric_frame/aetheric_frame.py")
replace_once(lines, "        del self._lock", [
    "        # `_lock` is kept, a documented post-cleanup field: the cleanup-safe probes",
    "        # (`_has_spell_unless_cleaned` and kin) and the re-checks in has_spell and",
    "        # spells_in_index take it on a frame another thread may have cleaned, as Spell",
    "        # keeps its lock for `_spell_index_unless_cleaned` " + TAG + ".",
])
add_doc(lines, "    def cleanup(self) -> None:", [
    "",
    "Lifecycle:",
    "    Deletes the frame's owned references but keeps `_lock` (and the",
    "    `_cleaned` flag), so a reader that holds the frame - Aether's cross-frame",
    "    sweep - can take the lock on a cleaned frame and read `_cleaned` under it.",
    "    " + TAG,
])
save(path, lines)

# ---------------------------------------------------------------- aether.py
path, lines = load("src/melder/aether/aether.py")


def replace_in_method(lines: list[str], header: str, old: str, new: list[str]) -> None:
    start, end = method_span(lines, header)
    hits = [i for i in range(start, end) if lines[i].rstrip("\r\n") == old]
    assert len(hits) == 1, (header, old, hits)
    e = eol(lines[hits[0]])
    lines[hits[0]:hits[0] + 1] = [text + e if text else e for text in new]


REPUBLISH = "self._aetheric_frame_view = tuple(self._aetheric_frames.items())"
replace_once(lines, "                self._aetheric_frames: dict[str, AethericFrame] = {}", [
    "                self._aetheric_frames: dict[str, AethericFrame] = {}",
    "                # Immutable (name, frame) view of _aetheric_frames, republished under the Aether lock by",
    "                # every registry write (frame birth, detach, teardown). Readers that must visit every frame -",
    "                # bind's cross-frame duplicate sweep - take it in one read instead of copying the dict per",
    "                # call " + TAG + ".",
    "                self._aetheric_frame_view: tuple[tuple[str, AethericFrame], ...] = ()",
])
replace_once(lines, "                    self._aetheric_frames.clear() # This cleans the ConcurrentDictionary", [
    "                    self._aetheric_frames.clear() # This cleans the ConcurrentDictionary",
    "                    self._aetheric_frame_view = ()",
])
replace_once(lines, "                del self._aetheric_frames", [
    "                del self._aetheric_frames",
    "                del self._aetheric_frame_view",
])
replace_in_method(lines, "    def _detach_cleaned_frame(", "            self._aetheric_frames.pop(frame_name, None)", [
    "            self._aetheric_frames.pop(frame_name, None)",
    "            " + REPUBLISH,
])
for header in ("    def _ensure_frame_locked(", "    def _create_frame("):
    replace_in_method(lines, header, "            self._aetheric_frames[aetheric_frame_name] = frame", [
        "            self._aetheric_frames[aetheric_frame_name] = frame",
        "            " + REPUBLISH,
    ])
view_comment = [
    "        # The published frame view: one read, no copy of the registry per call. Frame birth",
    "        # (_ensure_frame_locked, _create_frame) and detach (_detach_cleaned_frame) write the registry",
    "        # under the Aether lock and the plane's FRAME_CREATE claim, neither of which a bind holds, so a",
    '        # live walk raised "dictionary changed size during iteration". A frame born after the view',
    "        # was read holds no spell yet; one being torn down holds nothing, so the cleanup-safe probes",
    "        # answer for it as empty " + TAG + ".",
    "        frames = self._aetheric_frame_view",
]
replace_span(lines, "    def _check_for_spell(",
             "        if len(self._aetheric_frames) <= 1:",
             "                return other_frame.find_index_for_spell(spell_id)",
             view_comment + [
    "        if len(frames) <= 1:",
    "            return None",
    "",
    "        for other_name, other_frame in frames:",
    "            if other_name == aetheric_frame_name:",
    "                continue",
    "            if other_frame._has_spell_unless_cleaned(spell_id):",
    "                return other_frame._find_index_for_spell_unless_cleaned(spell_id)",
])
replace_span(lines, "    def _get_all_spell_ids(",
             "        if len(self._aetheric_frames) <= 1:",
             "            combined |= other_frame.spells_in_index()",
             view_comment + [
    "        if len(frames) <= 1:",
    "            return spell_ids",
    "",
    "        combined = set(spell_ids)",
    "        for other_name, other_frame in frames:",
    "            if other_name == aetheric_frame_name:",
    "                continue",
    "            combined |= other_frame._spells_in_index_unless_cleaned()",
])
for header in ("    def _check_for_spell(", "    def _get_all_spell_ids("):
    add_doc(lines, header, [
        "Threading:",
        "    The cross-frame sweep holds no Aether lock and copies nothing: it walks",
        "    the immutable frame view the registry's writers republish under the",
        "    Aether lock, and asks each other frame through its cleanup-safe probes,",
        "    so a frame born, cleaned or detached meanwhile never makes it raise.",
        "    " + TAG,
    ])
save(path, lines)
print("applied")
