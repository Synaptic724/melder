"""Pass the selected version's capability at the four register_index call sites (patch meld_state_gate_2026_10_15).

usage: python apply_call_sites.py <tree root> [--check]
The files are melder_0's (spellbook.py; transfer_of_ownership.py): applied to the scratch tree until the owner hands
the four lines over. One keyword per call; the test doubles those calls reach gain the keyword (and Spell.resolvable)
they mirror. Refuses when any anchor is missing or repeated. Re-running on a tree that already has the edits refuses.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_lib import apply  # the helper beside this script

ROOT = pathlib.Path(sys.argv[1])
CHECK = "--check" in sys.argv[2:]

SPELLBOOK = [
    ("one",
     "                self._spell_system_states.register_index(\n"
     "                    spell_index=new_spell.spell_index,\n"
     "                    owner_spellbook_id=self._id,\n"
     "                )\n",
     "                self._spell_system_states.register_index(\n"
     "                    spell_index=new_spell.spell_index,\n"
     "                    owner_spellbook_id=self._id,\n"
     "                    resolvable=new_spell.resolvable,\n"
     "                )\n",
     ""),
    ("one",
     "        self._spell_system_states.register_index(\n"
     "            spell_index=spell_index,\n"
     "            owner_spellbook_id=self._id,\n"
     "        )\n",
     "        self._spell_system_states.register_index(\n"
     "            spell_index=spell_index,\n"
     "            owner_spellbook_id=self._id,\n"
     "            resolvable=spell.resolvable,\n"
     "        )\n",
     ""),
]

TRANSFER = [
    ("one",
     "                tgt_states.register_index(\n"
     "                    spell_index=spell_obj.spell_index,\n"
     "                    owner_spellbook_id=tgt_book._id,\n"
     "                )\n",
     "                tgt_states.register_index(\n"
     "                    spell_index=spell_obj.spell_index,\n"
     "                    owner_spellbook_id=tgt_book._id,\n"
     "                    resolvable=spell_obj.resolvable,\n"
     "                )\n",
     ""),
    ("one",
     "        src_states.register_index(spell_obj.spell_index)\n",
     "        src_states.register_index(spell_obj.spell_index, resolvable=spell_obj.resolvable)\n",
     ""),
]

# The test doubles mirror the production signature and Spell: real Spells always carry `resolvable`, and the
# registry's register_index now takes it, so every double the four call sites reach accepts or carries it.
TRANSFER_FAKE_DOC = (
    "\n"
    "        Args:\n"
    "            spell_index: SpellIndex {what}\n"
    "            owner_spellbook_id: Owning Spellbook id (ignored here).\n"
    "            resolvable: The moved version's capability, as the transfer passes it (ignored here).\n"
    "        \"\"\"\n"
)


def transfer_fake(title: str, what: str, old_spell_line: str) -> list:
    """Steps that give a transfer test's fake registry the keyword and fix its stale Args, plus Spell.resolvable."""
    return [
        ("one",
         "    def register_index(self, spell_index: SpellIndex, owner_spellbook_id: Optional[str] = None) -> None:\n"
         "        \"\"\"\n"
         f"        {title}\n"
         "\n"
         "        Args:\n"
         f"            spell_index: SpellIndex {what}\n"
         f"            {old_spell_line}\n"
         "        \"\"\"\n",
         "    def register_index(\n"
         "            self,\n"
         "            spell_index: SpellIndex,\n"
         "            owner_spellbook_id: Optional[str] = None,\n"
         "            *,\n"
         "            resolvable: Optional[bool] = None,\n"
         "    ) -> None:\n"
         "        \"\"\"\n"
         f"        {title}\n"
         + TRANSFER_FAKE_DOC.format(what=what),
         ""),
        ("one",
         "        _key=f\"key-{spell_id}\",\n"
         "        dependencies=list(dependencies),\n"
         "        existence=existence,\n"
         "        permissions=permissions,\n"
         "    )\n",
         "        _key=f\"key-{spell_id}\",\n"
         "        dependencies=list(dependencies),\n"
         "        existence=existence,\n"
         "        permissions=permissions,\n"
         "        resolvable=True,\n"
         "    )\n",
         ""),
    ]


def component_fake(purpose: str, contract: str) -> list:
    """Steps that give a component spellbook test's fake registry the keyword."""
    return [
        ("one",
         "    def register_index(self, spell_index: object, owner_spellbook_id: object = None) -> None:\n"
         "        \"\"\"\n"
         "        Purpose:\n"
         f"            {purpose}\n"
         "        Contract:\n"
         f"            {contract}\n"
         "        Args:\n"
         "            spell_index: SpellIndex registered for the lineage.\n",
         "    def register_index(\n"
         "            self,\n"
         "            spell_index: object,\n"
         "            owner_spellbook_id: object = None,\n"
         "            *,\n"
         "            resolvable: object = None,\n"
         "    ) -> None:\n"
         "        \"\"\"\n"
         "        Purpose:\n"
         f"            {purpose}\n"
         "        Contract:\n"
         f"            {contract}\n"
         "        Args:\n"
         "            spell_index: SpellIndex registered for the lineage.\n"
         "            owner_spellbook_id: Owning Spellbook id (ignored here).\n"
         "            resolvable: The registered version's capability, as bind passes it (ignored here).\n",
         ""),
    ]


SPELLBOOK_UNIT = [
    ("one",
     "        register_index=lambda spell_index, owner_spellbook_id=None: lineage_calls.append((spell_index, new_spell))\n",
     "        register_index=lambda spell_index, owner_spellbook_id=None, resolvable=None: lineage_calls.append(\n"
     "            (spell_index, new_spell, resolvable)\n"
     "        )\n",
     ""),
    ("one",
     "    assert lineage_calls[0][1] is new_spell\n",
     "    assert lineage_calls[0][1] is new_spell\n"
     "    assert lineage_calls[0][2] is True  # bind passes the bound version's Spell.resolvable\n",
     ""),
    ("one",
     "        register_index=lambda spell_index, owner_spellbook_id=None: None\n",
     "        register_index=lambda spell_index, owner_spellbook_id=None, resolvable=None: None\n",
     ""),
]

apply(ROOT, "src/melder/aether/spellbook/spellbook.py", SPELLBOOK, CHECK)
apply(ROOT, "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py", TRANSFER, CHECK)
apply(ROOT, "tests/unit/melder/spellbook/test_spellbook.py", SPELLBOOK_UNIT, CHECK)
apply(ROOT, "tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py",
      transfer_fake("Register a lineage state for the provided spell index.", "whose state should be created.",
                    "spell: Spell object used to seed state metadata."), CHECK)
apply(ROOT, "tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py",
      transfer_fake("Register a lineage state for the given spell index.", "identifying the lineage.",
                    "spell: Spell object associated with the lineage."), CHECK)
apply(ROOT, "tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py",
      component_fake("Record a lineage registration call from Spellbook.bind.",
                     "- Stores (spell_index, owner_spell) in registration order."), CHECK)
apply(ROOT, "tests/component/melder/spellbook/test_spellbook_component_spellbook.py",
      component_fake("Record a lineage registration from Spellbook.bind.",
                     "- Appends (spell_index, active_spell) to registered_lineages."), CHECK)
