"""Trace what refreshes a borrower's Book flag across repeated notches of an index-linked lineage (melder_1, 2026-10-15).

Run on the scratch tree with PYTHONPATH=src; --mutate disables SpellSystemState._republish_validity; --stack prints
who publishes each structural `valid`.
"""
import sys
from melder import Aether, Conduit
from melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager import RiskManager
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_state import SpellSystemState
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook

MUTATE = "--mutate" in sys.argv
if MUTATE:
    SpellSystemState._republish_validity = lambda self: None

LOG = []
orig_react = Spellbook._reactivate_contracted_spell
orig_add = Spellbook._add_contracted_spell
orig_reg = RiskManager.register_spell
orig_struct = RiskManager.on_structural_validity_change


def react(self, conduit_id, spell):
    LOG.append(f"reactivate book={self._id[-6:]} spell={spell.spell_id[:8]}")
    return orig_react(self, conduit_id, spell)


def add(self, spell, conduit_id):
    LOG.append(f"add_contracted book={self._id[-6:]} spell={spell.spell_id[:8]}")
    return orig_add(self, spell, conduit_id)


def reg(self, conduit_id, spell):
    LOG.append(f"register_spell conduit={conduit_id[-6:]} spell={spell.spell_id[:8]}")
    return orig_reg(self, conduit_id, spell)


def struct(self, lineage_id, validity):
    LOG.append(f"structural lineage={lineage_id[-6:]} {validity.name if validity else None}")
    if "--stack" in sys.argv and validity is not None and validity.name == "valid":
        import traceback
        LOG.append("".join(traceback.format_stack(limit=14)[:-1]))
    return orig_struct(self, lineage_id, validity)


Spellbook._reactivate_contracted_spell = react
Spellbook._add_contracted_spell = add
RiskManager.register_spell = reg
RiskManager.on_structural_validity_change = struct


class Widget:
    def __init__(self) -> None:
        self.built = True


class WidgetDefinition:
    def __init__(self) -> None:
        pass


Aether._reset_singleton_for_tests()
world = Aether()
Spellbook._aether = world
Conduit._aether = world
frame = "trace"
lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                   system_caching_enabled=False)
borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
widget_id = lender_book.bind(spell=Widget, spellframe="widgets", binding_name="widget", existence="many",
                             permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
lender.link(borrower)
index = lender_book.find_spell_by_id(widget_id).spell_index
with borrower.transaction("link", conduits=[borrower, lender]):
    borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
borrower.validate_contracts_and_define()
borrower.meld(spell_id=widget_id)
states = lender_book._spell_system_states
print("after first borrower meld: borrower flag", borrower_book._spellbook_validation_required,
      "validity", states.get_by_index_id(index.id).validity.name)
definition_id = lender.bind_inactive(spell=WidgetDefinition, spell_index=index, spellframe="widgets",
                                     binding_name="widget", existence="many", permissions="create", resolvable=False)
LOG.clear()
lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[definition_id])
print("notch to definition:", LOG)
print("  borrower flag", borrower_book._spellbook_validation_required, "validity",
      states.get_by_index_id(index.id).validity.name)
LOG.clear()
lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[widget_id])
print("notch back:", LOG)
print("  borrower flag", borrower_book._spellbook_validation_required, "validity",
      states.get_by_index_id(index.id).validity.name)
borrower.meld(spell_id=widget_id)
print("after borrower meld of v1: borrower flag", borrower_book._spellbook_validation_required, "validity",
      states.get_by_index_id(index.id).validity.name)
LOG.clear()
lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[definition_id])
print("second notch to definition:", [x for x in LOG if not x.startswith("  File")])
print("  borrower flag", borrower_book._spellbook_validation_required, "validity",
      states.get_by_index_id(index.id).validity.name)
LOG.clear()
lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[widget_id])
print("second notch back:", LOG)
res = borrower_book._spell_system_states.get_conduit_resolution_state(borrower.id)
print("  borrower flag", borrower_book._spellbook_validation_required, "validity",
      states.get_by_index_id(index.id).validity.name, "borrower verdict v1", res.get_spell_validity(widget_id).name)
borrower.meld(spell_id=widget_id)
print("after borrower meld: verdict v1", res.get_spell_validity(widget_id).name)
borrower.cleanup()
lender.cleanup()
