"""D3 transfer default (0.2.8239): `move_creations` defaults to True on the transfer verbs; the docstrings say plainly
what each value does. Owner ruling 2026-10-14 (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, Decision Log)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from edit_tool import apply

TREE = pathlib.Path(sys.argv[1])
CONDUIT = TREE / "src/melder/aether/conduit/conduit.py"
WARD = TREE / "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
TRANSFER = TREE / "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"

CONDUIT_EDITS = [
    (
        "            target_conduit: \"Conduit\",\n"
        "            move_creations: bool = False,\n"
        "            include_dependencies: bool = False,\n"
        "            force_unshare: bool = True,\n"
        "            invalidate_after_transfer: bool = True,\n"
        "            mark_dependencies_dirty: bool = False,\n"
        "    ) -> dict:\n"
        "        \"\"\"\n"
        "        Public API (dynamic mode)\n"
        "\n"
        "        Transfer stewardship of a spell to another conduit.\n"
        "\n"
        "        Contract:\n"
        "            - Uses the normal `TRANSFER_OWNERSHIP` transaction path before the\n"
        "              existing `TransferOfOwnership` execution helper runs.\n"
        "            - Keeps request planning and admission in the mediator/strategy\n"
        "              layer while leaving the irreversible runtime move in the transfer\n"
        "              helper for now.\n"
        "\n"
        "        Args:\n"
        "            spell: Spell object, spell_id, or SpellIndex to transfer.\n"
        "            target_conduit: The conduit that will become the new steward.\n"
        "            move_creations:\n"
        "                If True, move conduit-owned creation state; otherwise tear that\n"
        "                source-side conduit-owned state down.\n"
        "                Spellspace-local request objects are intentionally excluded from\n"
        "                ownership transfer and are not preserved onto the target\n"
        "                conduit.\n",
        "            target_conduit: \"Conduit\",\n"
        "            move_creations: bool = True,\n"
        "            include_dependencies: bool = False,\n"
        "            force_unshare: bool = True,\n"
        "            invalidate_after_transfer: bool = True,\n"
        "            mark_dependencies_dirty: bool = False,\n"
        "    ) -> dict:\n"
        "        \"\"\"\n"
        "        Public API (dynamic mode)\n"
        "\n"
        "        Transfer stewardship of a spell to another conduit.\n"
        "\n"
        "        Contract:\n"
        "            - The whole lineage moves: the spell's index, with its active and\n"
        "              parked members, leaves this conduit's Spellbook and frame registry\n"
        "              entry and joins the target's. The target becomes the spell's\n"
        "              owner, so a `unique` instance lives in the target's store from\n"
        "              then on, and this conduit can no longer meld the spell.\n"
        "            - Existing instances follow `move_creations` (below). A transfer\n"
        "              never disposes anything.\n"
        "            - Borrowers are unshared (`force_unshare`) or repointed at the\n"
        "              target; with `include_dependencies`, each direct dependency this\n"
        "              conduit owns is transferred with the same options.\n"
        "            - Uses the normal `TRANSFER_OWNERSHIP` transaction path before the\n"
        "              existing `TransferOfOwnership` execution helper runs.\n"
        "            - Keeps request planning and admission in the mediator/strategy\n"
        "              layer while leaving the irreversible runtime move in the transfer\n"
        "              helper for now.\n"
        "\n"
        "        Args:\n"
        "            spell: Spell object, spell_id, or SpellIndex to transfer.\n"
        "            target_conduit: The conduit that will become the new steward.\n"
        "            move_creations:\n"
        "                True (the default since 0.2.8239): the instances this conduit's\n"
        "                store holds for every member of the spell's index move into the\n"
        "                target's store with the spell. A `unique` stays one object:\n"
        "                whatever already holds it keeps the instance the target now\n"
        "                serves, and the `many` children recorded with a moved holder\n"
        "                move with it. A moved entry replaces whatever the target's store\n"
        "                already holds under that spell id; the replaced instances are\n"
        "                not disposed.\n"
        "                False: nothing moves. The active member's instances are taken\n"
        "                out of this conduit's store and kept only until the transfer\n"
        "                has finished (for its rollback); they are neither moved nor\n"
        "                disposed, Melder stops tracking them, and the target builds its\n"
        "                own on its next meld - for a `unique`, a second instance beside\n"
        "                any that the application or other objects still hold.\n"
        "                Either way, `unique_per_conduit_lineage` instances stay where\n"
        "                they were resolved, and spellspace-local and cluster instances\n"
        "                are not in this conduit's store, so a transfer never touches\n"
        "                them.\n",
    ),
]

WARD_EDITS = [
    (
        "            target_conduit: Conduit,\n"
        "            move_creations: bool = False,\n",
        "            target_conduit: Conduit,\n"
        "            move_creations: bool = True,\n",
    ),
    (
        "            move_creations: If True, move creations; else tear them down at source.\n",
        "            move_creations: True (the default since 0.2.8239, as on\n"
        "                `Conduit.transfer_spell_ownership`) moves this conduit's stored\n"
        "                instances of every index member into the target's store with\n"
        "                the spell; False takes the active member's instances out of this\n"
        "                conduit's store without moving or disposing them. A transfer\n"
        "                never disposes anything.\n",
    ),
]

TRANSFER_EDITS = [
    (
        "        policy choices that define how aggressive the move should be. Those\n"
        "        options decide whether creations are carried forward or torn down,\n",
        "        policy choices that define how aggressive the move should be. Those\n"
        "        options decide whether existing instances are carried to the target or\n"
        "        left out of the transfer (taken out of the source store, not disposed),\n",
    ),
    (
        "            move_creations: When true, transfer creation-side state to the\n"
        "                target instead of tearing it down.\n",
        "            move_creations: When true, move the lineage's instances from the\n"
        "                source conduit's store into the target's (`_move_creations`);\n"
        "                when false, take the active member's instances out of the\n"
        "                source store without moving or disposing them\n"
        "                (`_teardown_creations`). The public verbs default to True\n"
        "                (0.2.8239) and always pass the value; this constructor keeps\n"
        "                False as its own default for direct construction.\n",
    ),
    (
        "        Rehome existing creation state onto the target conduit.\n"
        "\n"
        "        This branch preserves runtime object continuity across ownership\n"
        "        transfer. Instead of destroying existing creations and forcing the new\n"
        "        owner to rebuild them later, it extracts the lineage's creation payload\n"
        "        from the source and restores that payload into the target conduit's\n"
        "        `Creations` store. This applies only to conduit-owned creation state;\n"
        "        spellspace-local request objects are intentionally excluded because\n"
        "        their lifetime is owned by the source spellspace request surface, not\n"
        "        by conduit ownership transfer. A rollback handler is then registered so\n"
        "        the payload can be put back if a later transfer step fails.\n",
        "        Rehome existing creation state onto the target conduit.\n"
        "\n"
        "        This branch preserves runtime object continuity across ownership\n"
        "        transfer, and it is the public verbs' default (`move_creations=True`,\n"
        "        0.2.8239). Instead of leaving the existing instances behind and having\n"
        "        the new owner build its own, it extracts the lineage's creation payload\n"
        "        from the source and restores that payload into the target conduit's\n"
        "        `Creations` store, so a `unique` stays one object and a holder's row\n"
        "        carries the `many` children recorded with it (0.2.8238). The restore\n"
        "        replaces whatever the target store already holds under a member id;\n"
        "        the replaced instances are not disposed. This applies only to\n"
        "        conduit-owned creation state; spellspace-local request objects are\n"
        "        intentionally excluded because their lifetime is owned by the source\n"
        "        spellspace request surface, not by conduit ownership transfer. A\n"
        "        rollback handler is then registered so the payload can be put back if\n"
        "        a later transfer step fails.\n",
    ),
    (
        "        Remove source-side creation state instead of preserving it on the\n"
        "        target.\n"
        "\n"
        "        This is the destructive transfer posture. It is used when the caller\n"
        "        wants ownership to move but does not want live creation objects to be\n"
        "        carried across with it. The extracted payload is still kept for rollback\n"
        "        so a failed transfer can restore the pre-transfer runtime state.\n"
        "\n"
        "        Args:\n"
        "            spell_obj: Spell whose current creations should be torn down rather\n"
        "                than migrated.\n",
        "        Take the active member's instances out of the source store without\n"
        "        moving them.\n"
        "\n"
        "        This is the `move_creations=False` posture, which a caller chooses\n"
        "        explicitly: ownership moves, the existing instances do not (the public\n"
        "        verbs default to moving them, 0.2.8239). The extracted payload is kept\n"
        "        only for this transfer's rollback, so a failed transfer restores the\n"
        "        pre-transfer runtime state; on success it is dropped, so the instances\n"
        "        are neither moved nor disposed and Melder stops tracking them. The\n"
        "        target builds its own on its next meld - for a `unique`, a second\n"
        "        instance beside any that the application or other objects still hold.\n"
        "        Parked members' instances stay in the source store.\n"
        "\n"
        "        Args:\n"
        "            spell_obj: Spell whose active member's instances leave the source\n"
        "                store.\n",
    ),
]

print("conduit", apply(str(CONDUIT), CONDUIT_EDITS))
print("ward", apply(str(WARD), WARD_EDITS))
print("transfer", apply(str(TRANSFER), TRANSFER_EDITS))
