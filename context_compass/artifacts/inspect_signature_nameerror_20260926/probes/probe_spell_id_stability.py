"""Print bind-time spell ids for the probe classes; run twice in separate processes and compare.

Usage: python -X gil=0 probe_spell_id_stability.py <src_root>
"""
import sys

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, "/home/claude/work/probes_inspect")

import probe_user_mod as um  # noqa: E402
from melder.aether.aether import Aether  # noqa: E402
from melder.aether.spellbook.spellbook import Spellbook  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402
from melder.aether.spellbook.existence.existence import Existence  # noqa: E402

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
book = Spellbook(aetheric_frame="id-probe")
for cls in (um.Engine, um.Car, um.Garage):
    print(cls.__name__, book.bind(spell=cls, existence=Existence.many, permissions="create"))
print("make_car", book.bind(spell=um.make_car, existence=Existence.unique, permissions="create"))
spell = book.find_spell_by_id(book.bind(spell=um.Car, existence=Existence.many, permissions="create", binding_name="second"))
print("Car init_signature:", spell.profile.binding_profile.init_signature)
print("Car annotations:", spell.profile.binding_profile.annotations)
