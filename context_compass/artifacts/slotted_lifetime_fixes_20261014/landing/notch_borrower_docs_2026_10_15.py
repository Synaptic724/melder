"""
TASK-2026-10-15-describe_notch_borrower_follow_as_feature: rewrite the three passages that called the notch's
borrower updates a "known limitation" (owner, chat 2026-10-15: "its not a limitation its a feature"). Docs only.
Each anchor must match once; the documents stay LF and gain no non-ASCII character. Run from the repository root.
"""
import pathlib

DOCS = pathlib.Path("context_compass/system_docs")


def edit(name: str, pairs: list) -> None:
    path = DOCS / name
    raw = path.read_bytes().decode("utf-8")
    assert "\r\n" not in raw
    text = raw
    for old, new in pairs:
        assert text.count(old) == 1, (name, old[:70], text.count(old))
        text = text.replace(old, new)
    assert sum(ord(c) > 127 for c in text) == sum(ord(c) > 127 for c in raw)
    path.write_bytes(text.encode("utf-8"))
    print("edited", name, len(raw.splitlines()), "->", len(text.splitlines()))


edit("src_architecture.md", [
    ("inside the held transaction window. Notch is currently OWNER-SIDE ONLY:\n"
     "contracted borrowers are not fanned out, so a notch on a shared index does not\n"
     "yet update borrowers' contracted maps.\n"
     "EVIDENCE: src/melder/aether/spellbook/spellbook.py:3757-4192 (the three seams, remeasured 2026-09-30).\n",
     "inside the held transaction window. Versions coexist by design (owner ruling 2026-10-15): a notch\n"
     "moves which version is active, the borrowers follow it, and older versions stay alive. After the\n"
     "window the conduit has every linked borrower park its copy of the outgoing version and moves\n"
     "index-link borrowers to the new one, which they build at their next meld. MutationResearch records\n"
     "the versions, compositions pin specific ones, and the creation stores key objects by version id,\n"
     "so a `unique` can have one live object per version while agents iterate on one object and converge\n"
     "on the version they want (corrected 2026-10-15: this paragraph called the borrower update a missing\n"
     "fan-out).\n"
     "EVIDENCE: src/melder/aether/spellbook/spellbook.py:3757-4192 (the three seams, remeasured 2026-09-30);\n"
     "`src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._deactivate_borrowed_spell` and\n"
     "`src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_index_notch` (the borrowers).\n"),
    ("6. KNOWN LIMITATION: notch fan-out to contracted borrowers is not implemented,\n"
     "   so borrowers of a SHARED index keep stale contracted maps until the\n"
     "   cross-conduit slice lands.\n",
     "6. After the window the conduit updates its borrowers, by design (corrected 2026-10-15; this step\n"
     "   called it a missing fan-out): `Conduit._deactivate_borrowed_spell` has every linked peer park its\n"
     "   contracted copy of the outgoing version, and `ConduitWard._emit_index_notch` moves each index-link\n"
     "   contract's subscription to the new version, parking the old copy and activating the new one on\n"
     "   the receiver. Borrowers build the new version at their next meld; objects built from older\n"
     "   versions stay alive, so agents iterating on one object keep their work while it converges.\n"),
    ("   - src/melder/aether/spellbook/spellbook.py:4107-4192\n",
     "   - src/melder/aether/spellbook/spellbook.py:4107-4192\n"
     "   - src/melder/aether/conduit/conduit.py:5461-5549\n"
     "   - src/melder/aether/conduit/conduit.py:5746-5775\n"
     "   - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2380\n"),
    ("## Context / Handoff Summary\n\n",
     "## Context / Handoff Summary\n\n"
     "2026-10-15 notch borrowers (documentation only, owner ruling): the Architecture Summary and the SpellIndex\n"
     "Mutation Entry sequence no longer call the borrower update a missing fan-out. A notch moves which version is\n"
     "active; the conduit has every linked borrower park its copy of the outgoing version and moves index-link\n"
     "borrowers to the new one; older versions and their objects stay alive, because versions coexist by design\n"
     "(MutationResearch, compositions, one `unique` object per version).\n\n"),
])

edit("src_components.md", [
    ("- KNOWN LIMITATION (current slice boundary, not a defect): notch is OWNER-SIDE\n"
     "  ONLY. Contracted borrowers are not fanned out, so a notch on a SHARED index\n"
     "  does not yet update borrowers' contracted maps. Cross-conduit fan-out under\n"
     "  the same seal is the next slice.\n",
     "- Borrowers follow a notch, by design (corrected 2026-10-15; this line called it a\n"
     "  missing fan-out). After the notch transaction ends, `Conduit.notch_spell` has every\n"
     "  linked peer park its contracted copy of the outgoing version\n"
     "  (`_deactivate_borrowed_spell`), and `ConduitWard._emit_index_notch` moves each\n"
     "  index-link contract to the new version (the receiver parks the old copy and activates\n"
     "  the new one). Borrowers build the new version at their next meld. Older versions and\n"
     "  their objects stay alive: versions coexist (MutationResearch records them, compositions\n"
     "  pin them), which is how several agents iterate on one object and converge on a version.\n"),
    ("## Context / Handoff Summary\n\n",
     "## Context / Handoff Summary\n\n"
     "2026-10-15 notch borrowers (documentation only, owner ruling): the SpellIndex Mutation Surface says borrowers\n"
     "follow a notch - every linked peer parks its copy of the outgoing version, index-link borrowers move to the new\n"
     "one - and that older versions stay alive by design, instead of calling it a missing fan-out.\n\n"),
])
