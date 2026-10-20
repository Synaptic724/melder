"""Write docs_spec.json: the README, governed-change, UX expert 26 and concept-map edits for replace.py.

Run from the repository root:  python context_compass/artifacts/public_notch_target_20261016/scripts/docs_spec.py
then:                          python context_compass/artifacts/public_notch_target_20261016/scripts/replace.py <spec>
"\n" in old/new stands for each file's own newline (these regions are CRLF).
"""
import json
import pathlib

SPEC = [
    {
        "path": "README.md",
        "old": (
            "#    It is parked and unresolvable: nothing melds it, nothing sees it yet.\n"
            "id_v2 = conduit.bind_inactive(\n"
        ),
        "new": (
            "#    It is parked and unresolvable: nothing melds it, nothing sees it yet.\n"
            "id_v1 = index.selected_spell_id     # the version serving now\n"
            "id_v2 = conduit.bind_inactive(\n"
        ),
    },
    {
        "path": "README.md",
        "old": "conduit.notch_spell(spell_index=index, spell=spell_v2)\n",
        "new": "conduit.notch_spell(spell_index=index, spell_id=id_v2)\n",
    },
    {
        "path": "README.md",
        "old": "conduit.notch_spell(spell_index=index, spell=spell_v1)   # instant revert\n",
        "new": "conduit.notch_spell(spell_index=index, spell_id=id_v1)   # instant revert\n",
    },
    {
        "path": "docs/expert/governed-change.md",
        "old": (
            "`bind_inactive` places a candidate into the existing SpellIndex while the selected\n"
            "member remains unchanged. Expert 17 asserts the member set, unchanged selection,\n"
            "and unchanged resolved result.\n"
            "\n"
            "The runtime's promoting verb is `notch_spell`, which accepts a Spell object. The\n"
            "saved public staging lesson deliberately stops before hand-driving that operation:\n"
            "its demonstrated lookup by the parked ID returns the currently active member.\n"
            "Do not substitute a private-map access or claim that this lesson performs a full swap.\n"
            "The README's notch sketch assumes those version objects are already held.\n"
        ),
        "new": (
            "`bind_inactive` places a candidate into the existing SpellIndex while the selected\n"
            "member remains unchanged, and returns the candidate's id. Expert 17 asserts the\n"
            "member set, unchanged selection, and unchanged resolved result.\n"
            "\n"
            "Promotion is `notch_spell(spell_index=..., spell_id=...)` given that id: the candidate\n"
            "becomes the selected member and the next meld builds it, and a notch back by the\n"
            "previous id restores the old version, which stayed parked. Expert 17 runs the whole\n"
            "loop on public calls, as does the README's sketch. Name a parked version by its id:\n"
            "a lookup by a parked id returns the currently active member. `notch_spell` refuses a\n"
            "version of another index, or one another Spellbook owns, before it changes anything.\n"
        ),
    },
    {
        "path": "UX_and_AIX_experiences/04_expert/26_codegen_create_modify_iterate.py",
        "old": (
            "    # The loop stops where the public surface stops (expert 17): the\n"
            "    # promoting verb takes the parked OBJECT, and no public door hands\n"
            "    # one out - both id->object doors resolve to the ACTIVE member.\n"
        ),
        "new": (
            "    # Promotion is expert 17's lesson: notch_spell(spell_index=...,\n"
            "    # spell_id=staged) makes the staged version active. This lesson keeps\n"
            "    # it parked, and a lookup by its id still answers with the ACTIVE\n"
            "    # member - which is why the notch is given the id itself.\n"
        ),
    },
    {
        "path": "UX_and_AIX_experiences/04_expert/_concept_map.txt",
        "old": (
            "  17 notch_swapping_a_live_object (LINEAGES AND THE STAGING HALF. bind\n"
            "     -> bind_inactive (park a candidate on the SAME index, selection\n"
            "     unchanged) -> notch_spell (repoint the selection). THE FIRST TWO\n"
            "     ARE USER SURFACE AND THE THIRD IS NOT DRIVEN BY HAND - notch_spell\n"
            "     takes the parked OBJECT, which lives in the Spellbook's private\n"
            "     parking lot, and the Spellbook is not what you notch from. The\n"
            "     lesson stops at that boundary and demonstrates it (a parked id\n"
            "     resolves to the ACTIVE member) instead of poking through it.\n"
        ),
        "new": (
            "  17 notch_swapping_a_live_object (LINEAGES AND A HOT SWAP END TO END.\n"
            "     bind -> bind_inactive (park a candidate on the SAME index,\n"
            "     selection unchanged; it returns the candidate's id) -> notch_spell\n"
            "     (repoint the selection) -> meld -> notch back. ALL THREE VERBS ARE\n"
            "     USER SURFACE: notch_spell takes the id bind_inactive returned\n"
            "     (`spell_id=`) and resolves the exact version inside the call - a\n"
            "     lookup by a parked id still resolves to the ACTIVE member, which\n"
            "     is why the version is named by id (owner ruling 2026-10-16; until\n"
            "     then the verb took only the parked OBJECT and the lesson stopped\n"
            "     at staging). A version of another index, or of another Spellbook,\n"
            "     is refused before anything moves.\n"
        ),
    },
    {
        "path": "UX_and_AIX_experiences/04_expert/_concept_map.txt",
        "old": (
            "ARC D COMPLETE (lessons 16-17) - changing a running world: rewiring it\n"
            "  through link/pull/meld, and staging a version swap onto a lineage.\n"
        ),
        "new": (
            "ARC D COMPLETE (lessons 16-17) - changing a running world: rewiring it\n"
            "  through link/pull/meld, and staging and taking a version swap on a lineage.\n"
        ),
    },
    {
        "path": "UX_and_AIX_experiences/04_expert/_concept_map.txt",
        "old": (
            "    demonstrates rather than laments that a parked id resolves to the\n"
            "    active member. It touches no private map.\n"
        ),
        "new": (
            "    demonstrates rather than laments that a parked id resolves to the\n"
            "    active member. It touches no private map.\n"
            "    SUPERSEDED 2026-10-16 (owner ruling: \"just use the private version\n"
            "    if its inside the public call thats reasonable\"): `notch_spell` takes\n"
            "    `spell_id=` and resolves the parked version inside the call, so the\n"
            "    loop runs on public calls and lesson 17 takes the swap and the\n"
            "    rollback. The facade rule stands - the Spellbook is still not what\n"
            "    you notch from; the conduit's verb does the resolving.\n"
        ),
    },
]

out = pathlib.Path("context_compass/artifacts/public_notch_target_20261016/scripts/docs_spec.json")
out.write_text(json.dumps(SPEC, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote", out, len(SPEC), "entries")
