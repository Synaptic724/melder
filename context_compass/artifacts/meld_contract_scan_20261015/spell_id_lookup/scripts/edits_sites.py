"""Edits for the renamed call sites and the docstrings that cite the old answer."""
from apply_engine import EditEngine

STRATEGY = "src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py"
GRAFT = "src/melder/crystallizer/crystal_loader_system/graft_runner.py"
RESTORE = "src/melder/crystallizer/crystal_loader_system/restore_engine.py"
SPELL_INDEX = "src/melder/aether/spellbook/bind/spell_index.py"
SPELL = "src/melder/aether/spellbook/spell.py"


def register(engine: EditEngine) -> None:
    # A Phase-3 candidate id is an active spell's id: the exact lookup answers what the old one did.
    engine.anchor(
        STRATEGY,
        '            candidate: "Spell | None" = spellbook.find_spell_by_id(candidate_id) if spellbook is not None else None\n',
        '            candidate: "Spell | None" = (\n'
        '                spellbook.find_spell_by_spell_id(candidate_id) if spellbook is not None else None\n'
        '            )\n',
    )
    # A spell just bound is active.
    engine.anchor(
        GRAFT,
        "        live_spell = self._host_book.find_spell_by_id(new_spell_id)\n",
        "        live_spell = self._host_book.find_spell_by_spell_id(new_spell_id)\n",
    )
    engine.anchor(
        GRAFT,
        "            # TRIAGE (2026-07-12): the first cut resolved the adoptee via\n"
        "            # find_spell_by_id, which returns the index's ACTIVE spell\n"
        "            # for ANY member id (spellbook.py:1852-1855) - so adoption\n"
        "            # notched the target's own current selection (a self-notch)\n"
        "            # and the selection never moved. _get_owned_spell is the\n"
        "            # member-resolution seam the notch harness itself uses: it\n"
        "            # returns the owned spell active OR PARKED (the merged\n"
        "            # member is parked by construction). Read-only seam; the\n"
        "            # mediated write remains the public notch verb below.\n",
        "            # TRIAGE (2026-07-12): the first cut resolved the adoptee via\n"
        "            # find_spell_by_id, which then returned the index's ACTIVE\n"
        "            # spell for ANY member id - so adoption notched the target's\n"
        "            # own current selection (a self-notch) and the selection never\n"
        "            # moved. _get_owned_spell is the member-resolution seam the\n"
        "            # notch harness itself uses: it returns the owned spell active\n"
        "            # OR PARKED (the merged member is parked by construction).\n"
        "            # Read-only seam; the mediated write remains the public notch\n"
        "            # verb below. Since @@SINCE@@ the lookup is exact - renamed\n"
        "            # find_spell_by_spell_id, it answers the spell that owns the\n"
        "            # spell_id, active or parked - so it would find this member\n"
        "            # too; the owned seam stays.\n",
    )
    engine.anchor(
        RESTORE,
        "        live_spell = spellbook.find_spell_by_id(new_spell_id)\n",
        "        live_spell = spellbook.find_spell_by_spell_id(new_spell_id)\n",
    )
    # Recorded member ids: only `.spell_index` is read, and a member's own index is the one wanted.
    engine.anchor(
        RESTORE,
        "            live_spell = spellbook.find_spell_by_id(live_member_id)\n",
        "            live_spell = spellbook.find_spell_by_spell_id(live_member_id)\n",
    )
    engine.anchor(
        SPELL_INDEX,
        "            - DOES NOT RETIRE THE PREVIOUS ID. The superseded version stays a\n"
        "              MEMBER, which is exactly why `Spellbook.find_spell_by_id` still\n"
        "              resolves a parked id to the live spell. The member set is the\n"
        "              lineage; the selected id is only the current head.\n",
        "            - DOES NOT RETIRE THE PREVIOUS ID. The superseded version stays a\n"
        "              MEMBER - parked in its Book - so the member set is the lineage\n"
        "              and the selected id only the current head. A lookup by spell_id\n"
        "              (`Spellbook.find_spell_by_spell_id`) answers the superseded spell\n"
        "              itself, never the head; the head is what `selected_spell_id` and a\n"
        "              lookup by index id name.\n",
    )
    engine.anchor(
        SPELL_INDEX,
        "            - Tests MEMBERSHIP OF THE LINEAGE, not equality with the selected id, so a\n"
        "              superseded or parked version still answers True. This is the check\n"
        "              spellbook lookups rely on to resolve old ids to the live spell.\n",
        "            - Tests MEMBERSHIP OF THE LINEAGE, not equality with the selected id, so a\n"
        "              superseded or parked version still answers True. A membership test only:\n"
        "              a spell_id names its own spell (`Spellbook.find_spell_by_spell_id`), not\n"
        "              the lineage's selected head.\n",
    )
    engine.anchor(
        SPELL,
        "        Purpose:\n"
        "            Let a lock-free reader that already holds this Spell - the parked\n"
        "            branch of `Spellbook.find_spell_by_id` - read its index without\n"
        "            racing `cleanup()`, which deletes `spell_index`.\n",
        "        Purpose:\n"
        "            Let a reader that already holds this Spell read its index without\n"
        "            racing `cleanup()`, which deletes `spell_index` - the parked branch\n"
        "            of `Spellbook._find_contracted_spell_by_id`, and the explicit index\n"
        "            steps that turn a spell found by spell_id into the spell its index\n"
        "            has active (the ownership transfer's spell_id handles and the\n"
        "            contract dependency walks). Until @@SINCE@@ its first reader was the\n"
        "            parked branch of `Spellbook.find_spell_by_id`.\n",
    )
