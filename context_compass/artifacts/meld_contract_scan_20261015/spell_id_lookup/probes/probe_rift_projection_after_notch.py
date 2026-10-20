"""Probe: a capability room's spell lookups after a notch; is the room's projection live or a snapshot?

Usage: python probe_rift_projection_after_notch.py <tree root>  (run with the tree as cwd)
"""
import sys, pathlib
root = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "src"))
sys.path.insert(0, str(root))
from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.nexus import Nexus
from melder.nexus.rift.command_system.command_system import CommandSystem
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration

class PricingV1:
    def __init__(self): self.rate = 100
class PricingV2:
    def __init__(self): self.rate = 250

AetherUtilitySystem._reset_singleton_for_tests(); Nexus._reset_singleton_for_tests(); Aether._reset_singleton_for_tests()
a = Aether(); Spellbook._aether = a; Conduit._aether = a; CommandSystem._aether = a
cfg = SpellbookConfiguration(aether_frame="default"); cfg.load_default_dictionary()
configure_frame_posture_for_spellbook_configuration(cfg, dynamic=True, rift_enabled=True)
cfg.set_property("phase_scheduler_workers_per_spellbook", 1)
book = Spellbook(aetheric_frame="default", configuration=cfg)
v1 = book.bind(spell=PricingV1, existence=Existence.unique, permissions="create")
root_c = book.conjure(name="pricing_root", dynamic=True)
index = book._spells_by_id[v1].spell_index
v2 = root_c.bind_inactive(spell=PricingV2, spell_index=index, existence=Existence.unique, permissions="create")
nexus = Nexus(); nc = nexus.create_configuration()
for m, v in [("with_rift_creation_enabled", True), ("with_direct_rift_access", True), ("with_target_frame_override", True),
             ("with_multiple_target_frames", True), ("with_max_target_frame_count", 8), ("with_allowed_target_frame_names", ("default",)),
             ("with_nexus_frame_mode", "indexed"), ("with_max_nexus_frame_count", 8)]:
    getattr(nc, m)(v)
nexus.activate(nc)
rift = nexus.create_rift(configuration=nexus.create_rift_configuration().with_space_type(RiftSpaceType.capability), rift_name="pricing_rift")
rift.create_frame_link("default")
cmd = rift.space.command_system
def recs():
    d = rift._get_required_command_projection("default").frame_descriptor
    return sorted((r.spell_id[:8], r.spell_index_id[:8]) for r in d.spell_records_by_key.values())
print("v1", v1[:8], "v2", v2[:8], "index", index.id[:8])
print("records before notch:", recs())
root_c.notch_spell(spell_index=index, spell_id=v2)
print("records after notch (no refresh):", recs())
name = "get_spell_by_spell_id" if hasattr(cmd, "get_spell_by_spell_id") else "get_spell_by_id"
def ask(label, call):
    try:
        s = call()
        print(label, "->", s.spell_id[:8], s.spell.__name__)
    except Exception as e:
        print(label, "raised", type(e).__name__, str(e)[:100])
for vid, tag in ((v1, "v1"), (v2, "v2")):
    ask(f"{name}({tag})", lambda: getattr(cmd, name)(vid, frame_name="default"))
    ask(f"get_spell_by_source_id({tag})", lambda: cmd.get_spell_by_source_id(f"{book.id}:{vid}", frame_name="default"))
ask("get_spell_by_index_id", lambda: cmd.get_spell_by_index_id(index.id, frame_name="default"))
rift.refresh_runtime_projections()
print("records after refresh:", recs())
