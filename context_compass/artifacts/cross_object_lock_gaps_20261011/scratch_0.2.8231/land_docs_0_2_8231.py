"""Land the 0.2.8231 docs: src_architecture and src_components. Exact anchors; keeps EOL. usage: <repo>"""
import datetime, pathlib, re, sys

REPO = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
CHANGED = [
    "src/melder/aether/spellbook/spellbook.py",
    "src/melder/aether/conduit/conduit.py",
    "src/melder/aether/conduit/conduit_ward/conduit_ward.py",
    "src/melder/aether/aether.py",
    "src/melder/aether/aetheric_frame/aetheric_frame.py",
]
LOC = {rel: len((REPO / rel).read_bytes().decode("utf-8").splitlines()) for rel in CHANGED}


def edit(rel, ops):
    path = REPO / rel
    data = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in data
    text = data.replace("\r\n", "\n")
    for kind, anchor, payload in ops:
        if kind == "codemap":
            pattern = re.compile(r"(- path: `" + re.escape(anchor) + r"`\n  start_line: 1\n  end_line: )\d+(\n  loc: )\d+"
                                 r"(\n  verified_at: )\S+\n")
            text, n = pattern.subn(lambda m: f"{m.group(1)}{payload}{m.group(2)}{payload}{m.group(3)}{NOW}\n", text)
            if n != 1:
                raise SystemExit(f"{rel}: code map entry x{n} for {anchor}")
            continue
        if text.count(anchor) != 1:
            raise SystemExit(f"{rel}: anchor x{text.count(anchor)}: {anchor[:70]!r}")
        if kind == "before":
            text = text.replace(anchor, payload + anchor, 1)
        elif kind == "after":
            text = text.replace(anchor, anchor + payload, 1)
        elif kind == "replace":
            text = text.replace(anchor, payload, 1)
    long = [line for line in text.split("\n") if len(line) > 120 and "0.2.8231" in line]
    if long:
        raise SystemExit(f"{rel}: new lines over 120: {long}")
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"{rel}: {len(ops)} edits ({'CRLF' if crlf else 'LF'})")


ARCH_INVARIANT = """- Cross-object locks (2026-10-11, 0.2.8231): a reader and a writer of one map take the same lock, or the reader
  takes a view its writers publish whole. The owner-side index emissions (`ConduitWard._emit_index_notch`,
  `_emit_index_destroy`, `_emit_index_member_added`, `_emit_index_member_removed`) walk the ward's contract registry
  under the ward lock, the lock link and sever write it under: they run after the owner's transaction has ended
  (notch, index moves, bind_inactive) or with none (`Conduit.cleanup_spell`), so the frame mediator, which serializes
  LINK/UNLINK against those transactions, never orders them against a link or sever. Contract detail maps are read
  and written under the contract lock (`_contract_member_spell` included); the borrower reads answer by key first,
  and the contract listing resolves ids through the Book (`_find_contracted_spell_by_id`, `find_spell_by_id`), never
  through the Conduit lookups, whose conduit lock taken under the ward lock deadlocked with link and sever (conduit
  lock, then ward locks). `Conduit.cleanup_spell` emits the index destroy that `Spellbook._dispose_spell` reports
  from its decision under the Book lock. Bind's cross-frame sweep and `_get_all_spell_ids` read
  `Aether._aetheric_frame_view`, a tuple of `(name, frame)` pairs republished under the Aether lock by frame birth,
  detach and teardown - no copy per bind - and ask each other frame through cleanup-safe probes that take its lock
  once (frame cleanup keeps the lock) and answer a cleaned frame as empty. Frame reads of a conjured Book's live
  `_spell_ids` take each set in one call. Lock orders: ward -> contract -> Book (as sever), ward -> Book (as link),
  frame -> SpellIndex; nothing these walks run under a ward lock takes a conduit, frame or Aether lock, so frame
  teardown (frame -> conduit -> ward) closes no cycle with them, and links are same-frame only.
  EVIDENCE: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_index_destroy`,
  `ConduitWard._get_spells_in_contract_by_conduit`, `src/melder/aether/conduit/conduit.py:Conduit.cleanup_spell`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook._dispose_spell`,
  `src/melder/aether/aether.py:Aether._check_for_spell` and
  `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame._has_spell_unless_cleaned`.
"""

ARCH_FAILURE = """- Index-link notifications, contract reads and binds across frames no longer fail under concurrent changes (fixed in
  0.2.8231): `cleanup_spell`, `notch_spell`, `add_to_spell_index`, `remove_from_spell_index` and `bind_inactive` no
  longer raise RuntimeError "dictionary changed size during iteration" after their change committed when a link or
  sever of the same conduit runs, and no longer leave a borrower subscribed to a destroyed index or without an active
  copy; `get_spell_in_contracts` and `get_spells_in_contract_by_conduit` no longer raise that error, "Detail has
  already been cleaned." or AttributeError while the lender moves index members, and the listing no longer hangs
  against `sever_link` or `link` of the same conduit; `bind` with two or more frames no longer fails with that error,
  "AethericFrame has already been cleaned." or AttributeError while a frame is born or torn down; and a conjure's
  duplicate-id check no longer raises "Set changed size during iteration" while another Book of the frame binds. A
  second `cleanup_spell` of a disposed spell raises RuntimeError "cleanup_spell: spell <id> has already been
  disposed." (it raised AttributeError), and `AethericFrame.has_spell` / `spells_in_index` racing the frame's
  cleanup raise their documented RuntimeError (they raised AttributeError).
  EVIDENCE: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_index_notch`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook._dispose_spell` and
  `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame.spells_in_index`.
"""

ARCH_HANDOFF = """2026-10-11 cross-object locks (0.2.8231): the owner-side index emissions walk a ward's contracts under the ward lock,
contract detail maps are read and written under the contract lock, the contract listing resolves through the Book
instead of the conduit-locked Conduit lookups (a deadlock with link and sever), `cleanup_spell` emits the destroy the
Book's locked decision reports, and bind's cross-frame sweep reads a frame view Aether republishes on frame birth and
detach and asks frames through cleanup-safe probes; the frame copies each Book's live id set in one call. The
operational invariants, the failure modes and the code map carry it; the component map carries the per-component
rules.

"""

COMP_CORE_THREADING = """- `_find_contracted_spell_by_id` answers by key before that walk (0.2.8231): the active borrowed copy is
  `_contracted_spells_by_id[conduit_id][spell_id]`; a parked one in `_inactive_contracted_spells` keys its lineage's
  active copy through its index (`Spell._spell_index_unless_cleaned`, the parked spell's own lock). Only a version the
  Book holds no copy of falls back to the snapshot walk. The contract listing calls it under the ward and contract
  locks, which is safe because no Book path takes a ward or contract lock.
- `cleanup_spell` runs `_dispose_spell` (0.2.8231): ownership, activity and sole membership are read under `_lock` by
  identity from `_spells_by_id` / `_inactive_spells` - while the spell is in them its fields are live, because
  `Spell.cleanup` deletes them only after the Book has popped it - and a spell no longer in them is classified outside
  `_lock` through `Spell._spell_index_unless_cleaned`, because `Spell.cleanup` takes the spell lock before `_lock`.
  `_dispose_spell` returns the destroyed index's id (None when the index survived), which `Conduit.cleanup_spell`
  emits to index-link borrowers.
"""

COMP_CORE_FAILURE = """- RuntimeError "cleanup_spell: spell <id> has already been disposed." for a spell already disposed (0.2.8231; it
  raised AttributeError), besides the "not owned by this spellbook" and multi-member refusals.
"""

COMP_AETHER_THREADING = """- `_aetheric_frame_view` (0.2.8231) is an immutable tuple of `(name, frame)` pairs that every registry write
  (`_ensure_frame_locked`, `_create_frame`, `_detach_cleaned_frame`; teardown clears it) replaces under the Aether
  lock. The cross-frame duplicate sweeps (`_check_for_spell`, `_get_all_spell_ids`) read it once and walk it with no
  lock and no copy: bind holds neither the Aether lock nor the plane's FRAME_CREATE claim that frame birth and detach
  take, and the live registry raised "dictionary changed size during iteration" under it. A frame born after the read
  holds no spell yet; a frame torn down meanwhile answers as empty through the frame probes.
"""

COMP_FRAME_TEARDOWN_OLD = """- The frame does not hold its lock while calling into an owned conduit's own
  cleanup; teardown clears the registry first and cascades afterwards.
"""

COMP_FRAME_THREADING = """- Teardown holds the frame lock throughout: `cleanup` takes it, sets `_cleaned` and runs
  `_cleanup_data_structures`, which cleans each conduit (`permanent_cleanup`, reaching its ward) before clearing the
  registries, and then detaches from Aether (frame -> Aether). Corrected 2026-10-11: this said the frame did not hold
  its lock while cleaning its conduits. `cleanup` keeps `_lock` (0.2.8231), a documented post-cleanup field like
  Spell's, so the probes below and the re-checks in `has_spell` and `spells_in_index` can take it on a frame another
  thread has cleaned.
- Cleanup-safe probes (0.2.8231) for Aether's cross-frame sweeps - `_has_spell_unless_cleaned`,
  `_find_index_for_spell_unless_cleaned`, `_spells_in_index_unless_cleaned` - take the frame lock once and answer
  False / None / an empty set when the frame reads cleaned; otherwise one `in` per Book set, an O(1)
  `SpellIndex._has_spell_unless_cleaned` per index (frame -> SpellIndex, as `find_index_for_spell`, which copies each
  index's member set) and one `set.update` per Book set. `has_spell` and `spells_in_index` re-check cleaned under the
  lock, so a racing cleanup raises their documented RuntimeError, never AttributeError.
- `_selected_spell_registry` holds LIVE references to each conjured Book's `_spell_ids`, which the Book writes under
  its own lock, not the frame lock: frame reads take each set in one call (`in`, `set.update`; 0.2.8231), where the
  element-by-element copy in `spells_in_index` raised "Set changed size during iteration" while that Book bound
  (the conjure preflight, `Spellbook._spell_id_integrity_checker`, reads it).
"""

COMP_FRAME_FAILURE = """- RuntimeError "AethericFrame has already been cleaned." from `has_spell` and `spells_in_index` on a cleaned frame,
  also when the cleanup races the call (0.2.8231; that race raised AttributeError).

"""

COMP_CONDUIT_THREADING = """- `cleanup_spell` takes no lock of its own and reads nothing about the spell before the Book decides (0.2.8231): it
  emits `_emit_index_destroy(index_id, (spell_id,))` exactly when `Spellbook._dispose_spell` reports the index it
  destroyed. The emission walks the ward's contracts under the ward lock, so a concurrent `link` or `sever_link` of
  this conduit waits for it. The old unlocked pre-read of `spell.spell_index` raised AttributeError for a disposed
  spell and could disagree with what the Book then did.
"""

COMP_CONDUIT_FAILURE = """- RuntimeError from `cleanup_spell` for a spell already disposed ("cleanup_spell: spell <id> has already been
  disposed."; 0.2.8231, it raised AttributeError), not owned by this conduit's Book, or the active member of a
  multi-member index.
"""

COMP_WARD_THREADING = """- The four owner-side index emissions walk `_contracts` under the ward lock (0.2.8231), the lock link
  (`_create_new_contract`) and sever (`_remove_contract`) write it under. They run after the owner's transaction has
  ended (notch, index moves, bind_inactive) or with none (`cleanup_spell`), where the frame mediator - which
  serializes LINK/UNLINK against those transactions - does not reach, and a link admitted in that window made them
  raise "dictionary changed size during iteration" after the owner's change committed, leaving borrowers not yet
  visited out of step. Inside the walk: contract locks (ward -> contract, as sever), peer Book calls (ward -> Book,
  as link), IndexDetail and SpellIndex locks; contract records are emitted after the ward lock.
- A contract's detail maps are read and written under the contract lock (0.2.8231): `_contract_member_spell` adds
  under it, as `_uncontract_member_spell` removes; `_get_spell_in_contracts` walks under it, trying the detail keyed
  by the id first, and resolves the matched index after releasing it; `_get_spells_in_contract_by_conduit` walks both
  maps under it and resolves every id by key through this conduit's Book (inbound
  `Spellbook._find_contracted_spell_by_id`, outbound `Spellbook.find_spell_by_id`). It no longer calls
  `Conduit.find_contracted_spell`, which takes the conduit lock: link and sever take the conduit lock and then the
  ward locks, and the listing held the ward lock while it waited for the conduit lock - the two deadlocked.
"""

COMP_WARD_FAILURE = """- The emissions and the contract reads no longer raise the size-change RuntimeError, "Detail has already been
  cleaned." or AttributeError under concurrent links, severs and member moves, and the listing no longer hangs
  against a link or sever of its conduit (0.2.8231).
"""

COMP_HANDOFF = """2026-10-11 cross-object locks (0.2.8231): ConduitWard and Contracts carries the ward-lock rule for the owner-side
emissions, the contract-lock rule for detail maps and the listing's resolution through the Book (the deadlock it
removes); Spellbook Core carries `_dispose_spell` and the by-key contracted lookup; the Conduit Runtime carries
`cleanup_spell`'s emission; the Aether Singleton carries the published frame view; AethericFrame Services carries the
probes, the kept lock, the one-call reads of the Books' id sets and the corrected teardown lock note; the code map
extents of the changed files are remeasured.

"""

edit("context_compass/system_docs/src_architecture.md", [
    ("before", "- Spell-map walks (2026-10-11, 0.2.8230):", ARCH_INVARIANT),
    ("before", "- Concurrent binds and removals no longer make", ARCH_FAILURE),
    ("codemap", CHANGED[0], LOC[CHANGED[0]]),
    ("codemap", CHANGED[1], LOC[CHANGED[1]]),
    ("codemap", CHANGED[2], LOC[CHANGED[2]]),
    ("codemap", CHANGED[3], LOC[CHANGED[3]]),
    ("codemap", CHANGED[4], LOC[CHANGED[4]]),
    ("replace", "    publishes its spell maps under the Book lock (0.2.8230).\n",
     "    publishes its spell maps under the Book lock (0.2.8230); `cleanup_spell` decides through `_dispose_spell` and\n"
     "    contracted lookups answer by key (0.2.8231).\n"),
    ("replace", "  note: conduit lifecycle and meld facade.\n",
     "  note: conduit lifecycle and meld facade; `cleanup_spell` emits the index destroy the Book reports (0.2.8231).\n"),
    ("replace", "  note: contracts and lineage.\n",
     "  note: contracts and lineage; owner-side emissions under the ward lock, contract reads under the contract\n"
     "    lock, the listing resolved through the Book (0.2.8231).\n"),
    ("replace", "  note: global singleton, frame registry and the noncreating frame lookups (0.2.8208).\n",
     "  note: global singleton, frame registry and the noncreating frame lookups (0.2.8208); the published frame view\n"
     "    the cross-frame sweeps read (0.2.8231).\n"),
    ("replace", "  note: per-frame state and control plane.\n",
     "  note: per-frame state and control plane; cleanup-safe probes, the frame lock kept after cleanup (0.2.8231).\n"),
    ("before", "2026-10-11 spell-map walks (0.2.8230): bind publishes", ARCH_HANDOFF),
])

edit("context_compass/system_docs/src_components.md", [
    ("after", "  caller-held lock.\n", COMP_CORE_THREADING),
    ("after", "  never fire. `_get_spell_by_id_via_aether` returns None only when the owner's `find_spell_by_id` misses.\n",
     COMP_CORE_FAILURE),
    ("after", "- Class-level RLock guards singleton initialization and updates.\n", COMP_AETHER_THREADING),
    ("replace", COMP_FRAME_TEARDOWN_OLD, COMP_FRAME_THREADING),
    ("before", "Observability:\n- TWO log calls in the whole module (the second since 0.2.8203), both routed", COMP_FRAME_FAILURE),
    ("after", "  to walk the Book's live index map under the conduit lock, which a bind or removal on another thread could resize\n"
     "  mid-walk.\n", COMP_CONDUIT_THREADING),
    ("after", "  2026-10-11; they promised None).\n", COMP_CONDUIT_FAILURE),
    ("after", "  answers False, so `_get_spell_in_contracts` and `_find_governing_index_link` pass over it.\n", COMP_WARD_THREADING),
    ("after", "  cleanup raised disposal failures (0.2.8203; before, they were logged).\n", COMP_WARD_FAILURE),
    ("codemap", CHANGED[0], LOC[CHANGED[0]]),
    ("codemap", CHANGED[1], LOC[CHANGED[1]]),
    ("codemap", CHANGED[2], LOC[CHANGED[2]]),
    ("codemap", CHANGED[3], LOC[CHANGED[3]]),
    ("codemap", CHANGED[4], LOC[CHANGED[4]]),
    ("before", "2026-10-11 spell-map walks (0.2.8230): Spellbook Core carries the rule", COMP_HANDOFF),
])
print("LOC", LOC, "NOW", NOW)
