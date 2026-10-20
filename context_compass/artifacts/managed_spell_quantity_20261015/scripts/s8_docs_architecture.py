"""S8: promote parked_versions_wired_at_conjure_2026_10_16 into src_architecture (exact replacements, LF).

Run from the repository root: python s8_docs_architecture.py <NOW>
Every old text must occur exactly once; nothing is written unless all of them do.
"""
import pathlib
import sys

NOW = sys.argv[1]
DOC = pathlib.Path("context_compass/system_docs/src_architecture.md")
SCS = "`src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem.define_conduit_into_spells`"

EDITS = [
    # Boot and configuration sequence, step 4.
    ("   - Fires pre/activated/post hooks and wires ownership into spells.\n",
     "   - Fires pre/activated/post hooks and wires ownership into spells: every active version, and every version\n"
     "     parked with `bind_inactive` before conjure, which gets the owner stamp alone (0.2.8248).\n"),
    # Sequence: Conjure Conduit.
    ("   - Fire conjure hooks and wire Conduit into spells.\n",
     "   - Fire conjure hooks and wire Conduit into spells: each active version gets the owner stamp, its resolution\n"
     "     flag cleared and an existing object registered; each version parked with `bind_inactive` before conjure gets\n"
     "     the owner stamp alone (0.2.8248), so after a notch it melds like a version staged after conjure.\n"
     "     EVIDENCE: " + SCS + ".\n"),
    # Pipeline diagram.
    ("  -> wire ownership into spells\n",
     "  -> wire ownership into spells (active versions; parked versions get the stamp alone)\n"),
    # New operational invariant, newest first.
    ("## Operational Invariants\n- Non-resolvable definitions hold no Book flag (2026-10-16, 0.2.8247):",
     "## Operational Invariants\n"
     "- Parked versions are wired at conjure (2026-10-16, 0.2.8248): after conjure every version a Book owns carries the\n"
     "  owner stamp - `Spell._add_owned_conduit` with the root's id, name and store, its dynamic flag and gate controller\n"
     "  and the Book's caching posture, which configures the version's CreationContextFactory and, for a managed version,\n"
     "  composes its pool in the root's store and registers it with `ReleaseManagedSpell`. `define_conduit_into_spells`\n"
     "  stamps the active versions as before (each also has its resolution flag cleared and an existing object registered\n"
     "  in the root's store), then, under the same Book lock, every version in `_inactive_spells` with the same arguments\n"
     "  and nothing else, which is what a post-conjure `bind_inactive` gives a version it parks. A parked version stays off\n"
     "  resolution until a notch promotes it - a meld of its id raises KeyError \"No spell found with spell_id\" - and a\n"
     "  parked existing object is not registered as live; no disposal is lost by that, because Bind resolves disposal\n"
     "  names only for a class binding profile, so an existing-object spell carries none. A stamp that raises is logged\n"
     "  per version and the loop goes on, the active loop's policy. Locks: Book -> spell -> store leaf -> registry leaf,\n"
     "  the order every stamp takes; no new edge. Until 0.2.8248 conjure walked `_spells` only and a notch stamps nothing\n"
     "  (`_apply_notch`), so a version staged before conjure had no factory and its first meld after a notch raised for\n"
     "  every existence (owner ruling, 2026-10-16: \"bind_inactive should behave the same before and after conjure\").\n"
     "  Restore and graft stage members after conjure through `conduit.bind_inactive`, so they took the wired path\n"
     "  already.\n"
     "  EVIDENCE: " + SCS + ",\n"
     "  `src/melder/aether/spellbook/spellbook.py:Spellbook.bind_inactive`, `Spellbook._apply_notch`,\n"
     "  `src/melder/aether/spellbook/spell.py:Spell._add_owned_conduit`,\n"
     "  `src/melder/aether/spellbook/bind/bind.py:Bind._bind_logic` and\n"
     "  `src/melder/crystallizer/crystal_loader_system/restore_engine.py:RestoreEngine._bind_one_staged`.\n"
     "- Non-resolvable definitions hold no Book flag (2026-10-16, 0.2.8247):"),
    # Transfer invariant.
    ("failed transfer left the active member on the target's store. A version staged with `bind_inactive` before conjure\n"
     "  carries no stamp and moves as before. Stamps run",
     "failed transfer left the active member on the target's store. Since 0.2.8248 conjure stamps the versions staged\n"
     "  with `bind_inactive` before it too, so every member carries a stamp; only one whose stamp raised at conjure\n"
     "  (logged) carries none and moves as before. Stamps run"),
    # Managed leases in emitted plans: generation 21.
    ("compared), and no cache generation moves: plans are emitted at hydration. The warm path takes no lock.\n",
     "compared). Plans are emitted at hydration, so no cache generation had to move; generation 21 (0.2.8248,\n"
     "  \"managed_spell_lease_codegen\") retires the bundles written before this codegen anyway, on the owner's ruling\n"
     "  that a codegen change bumps the cache: each is cold once after the upgrade and is rewritten at 21. The warm path\n"
     "  takes no lock.\n"),
    # Failure mode: the missing-pool error.
    ("A version with no pool to lease from - its owner root torn down, or a version staged\n"
     "  with `bind_inactive` before conjure and notched in after it - raises MeldExecutionError \"Managed spell '<name>' has\n"
     "  no pool to lease from: ...\".",
     "A version with no pool to lease from - its owner root torn down, or its owner store\n"
     "  holding no pool for it - raises MeldExecutionError \"Managed spell '<name>' has no pool to lease from: its owner root\n"
     "  was torn down, or its owner store holds no pool for this version. Meld it through a live root that owns it.\"\n"
     "  (0.2.8248; the pre-conjure staging cause and its \"stage the version after conjure\" remedy are gone)."),
    # Failure mode: parked before conjure, now fixed.
    ("- A version staged with `bind_inactive` before `conjure` is never owner-stamped (conjure stamps the Book's active\n"
     "  spells only, and a notch stamps nothing), so after a notch to it its first meld raises RuntimeError \"Spell has no\n"
     "  configured CreationContextFactory.\" for every existence, and a managed consumer raises the missing-pool error. Stage\n"
     "  versions after conjure. Stamping parked versions at conjure is open for the owner's decision; unchanged.\n"
     "  EVIDENCE: " + SCS + ",\n",
     "- A version staged with `bind_inactive` before `conjure` melds after a notch (fixed in 0.2.8248). Conjure stamped\n"
     "  the Book's active versions only and a notch stamps nothing, so after a notch to such a version its first meld\n"
     "  raised RuntimeError \"Spell has no configured CreationContextFactory.\" for every existence, and a managed consumer\n"
     "  raised the missing-pool error; staging the version after conjure was the workaround. Conjure now stamps every\n"
     "  parked version (owner ruling, 2026-10-16).\n"
     "  EVIDENCE: " + SCS + ",\n"),
    # Settle-then-inherit citations moved three lines with the bind_inactive comment.
    ("  - src/melder/aether/spellbook/spellbook.py:6790-6833\n"
     "    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6820-6832,\n"
     "    effective-mode return :6833; remeasured 2026-10-16 at 0.2.8247)\n"
     "  - src/melder/aether/spellbook/spellbook.py:7046\n",
     "  - src/melder/aether/spellbook/spellbook.py:6793-6836\n"
     "    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6823-6835,\n"
     "    effective-mode return :6836; remeasured 2026-10-16 at 0.2.8248)\n"
     "  - src/melder/aether/spellbook/spellbook.py:7049\n"),
    # Code map.
    ("  end_line: 7615\n  loc: 7615\n  verified_at: 2026-10-16T01:12:19Z\n",
     "  end_line: 7618\n  loc: 7618\n  verified_at: " + NOW + "\n"),
    ("bind and `_apply_notch` pass the selected\n    version's `resolvable` to `register_index` (0.2.8247).\n",
     "bind and `_apply_notch` pass the selected\n    version's `resolvable` to `register_index` (0.2.8247); `bind_inactive`'s comment on versions parked before\n"
     "    conjure holds since conjure stamps them (0.2.8248).\n"),
    ("  end_line: 3508\n  loc: 3508\n  verified_at: 2026-10-11T15:21:03Z\n",
     "  end_line: 3545\n  loc: 3545\n  verified_at: " + NOW + "\n"),
    ("the book-wide factories and the cleanup pass walk snapshots (0.2.8230).\n",
     "the book-wide factories and the cleanup pass walk snapshots (0.2.8230); conjure stamps\n"
     "    the versions parked before it (`define_conduit_into_spells`, 0.2.8248).\n"),
    ("  end_line: 2119\n  loc: 2119\n  verified_at: 2026-10-15T21:20:35Z\n",
     "  end_line: 2121\n  loc: 2121\n  verified_at: " + NOW + "\n"),
    ("the inline pop, the reserve-first miss, the lease return (0.2.8245).\n",
     "the inline pop, the reserve-first miss, the lease return (0.2.8245); the missing-pool\n"
     "    message without the pre-conjure staging cause (0.2.8248).\n"),
    ("  end_line: 2155\n  loc: 2155\n  verified_at: 2026-10-16T01:12:19Z\n",
     "  end_line: 2158\n  loc: 2158\n  verified_at: " + NOW + "\n"),
    ("the flip and its rollback pass the moved version's `resolvable` to\n    `register_index` (0.2.8247).\n",
     "the flip and its rollback pass the moved version's `resolvable` to\n    `register_index` (0.2.8247); "
     "`_migrate_inactive_members` documents the conjure stamp of pre-conjure staged versions\n    (0.2.8248).\n"),
    ("  end_line: 892\n  loc: 892\n  verified_at: 2026-10-04T11:45:00Z\n",
     "  end_line: 900\n  loc: 900\n  verified_at: " + NOW + "\n"),
    ("persistence;\n    generation 20 (0.2.8222).\n",
     "persistence;\n    generation 21, \"managed_spell_lease_codegen\" (0.2.8248).\n"),
    # Handoff, newest first.
    ("## Context / Handoff Summary\n\n2026-10-16 non-resolvable definitions leave the Book flag (0.2.8247):",
     "## Context / Handoff Summary\n\n"
     "2026-10-16 parked versions wired at conjure (0.2.8248): conjure stamps every version parked with `bind_inactive`\n"
     "before it with the owner stamp alone, as a post-conjure `bind_inactive` does, so such a version melds after a notch\n"
     "for every existence (owner ruling: \"bind_inactive should behave the same before and after conjure\"); the creation\n"
     "cache moves to generation 21, retiring bundles written before the managed lease codegen (owner: a codegen change\n"
     "bumps the cache); the missing-pool message loses its pre-conjure cause. The boot and conjure sequences, a new\n"
     "operational invariant, the transfer and managed-lease invariants, two failure modes (one now a fixed defect), the\n"
     "code map (five files remeasured), the pipeline diagram and the settle-then-inherit citations (three lines further\n"
     "down spellbook.py) carry it; the component map carries the per-component contracts. The 2026-10-15 entry's open\n"
     "item, stamping versions staged before conjure, is closed.\n\n"
     "2026-10-16 non-resolvable definitions leave the Book flag (0.2.8247):"),
]


def main() -> None:
    """Apply every edit or none."""
    text = DOC.read_bytes().decode("utf-8")
    assert "\r\n" not in text
    for old, new in EDITS:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"expected one occurrence, found {count}: {old[:90]!r}")
        text = text.replace(old, new)
    DOC.write_bytes(text.encode("utf-8"))
    long_lines = [n for n, line in enumerate(text.split("\n"), 1) if len(line) > 120 and "`" not in line]
    print("edits", len(EDITS), "lines", len(text.split("\n")) - 1, "long non-code lines", long_lines[:20])


if __name__ == "__main__":
    main()
