import sys
sys.path.insert(0, "src")
sys.path.insert(0, ".")
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration

class Disp:
    def __init__(self):
        self.cleanup_calls = 0
    def cleanup(self):
        self.cleanup_calls += 1

Aether._reset_singleton_for_tests()
a = Aether(); Spellbook._aether = a; Conduit._aether = a
c = SpellbookConfiguration()
set_frame_system_state_for_spellbook_configuration(c, "automatic")
c.set_property("disposal", True)
c.set_property("disposal_method_names", ["cleanup"])
c.load_default_dictionary()
c.set_property("phase_scheduler_workers_per_spellbook", 1)
sb = Spellbook(configuration=c)
sid = sb.bind(spell=Disp, existence=Existence.many, permissions="create")
conduit = sb.conjure(name="root")
try:
    with conduit.enter_spellspace() as space:
        x = space.meld(spell_id=sid)
        bucket = space._creations.get_creation(sid)
        print("space bucket:", type(bucket).__name__, len(bucket) if isinstance(bucket, list) else bucket)
        print("space probe:", space._meld.describe_live_creation_status(spell=sid))
        print("conduit probe:", conduit.describe_live_creation_status(spell=sid))
    print("after exit cleanup_calls:", x.cleanup_calls)
finally:
    conduit.permanent_cleanup()
