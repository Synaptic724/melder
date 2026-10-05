"""Run the 0.2.8212 release-note examples verbatim (each in its own section of one process)."""
print("--- example 1 (Aether regime)")
from melder import Aether, AetherConfiguration, Spellbook

per_frame = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
Aether().configure(per_frame)                    # before the first frame: accepted
Spellbook(aetheric_frame="tenant_a")             # the first frame seals the per-frame regime
print("configured regime:", Aether().configuration.process_wide_unique_spell_ids)
try:
    Aether().configure(AetherConfiguration().with_defaults())
except RuntimeError as error:
    print("refused:", str(error)[:100])

print("--- example 2 (Nexus)")
from melder import Nexus
nexus = Nexus()
nexus.activate(nexus.create_configuration())
new_configuration = nexus.create_configuration().with_max_active_rift_count(3)
try:
    nexus.activate(new_configuration)
except RuntimeError as error:
    print("refused:", error)
nexus.deactivate()
nexus.activate(new_configuration)
print("active:", nexus.activated, "cap:", nexus.configuration.get_property("max_active_rift_count"))

print("--- example 4 (snapshot)")
from melder import Crystallizer, CrystallizerConfiguration

wanted = CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(3)
Crystallizer().configure(CrystallizerConfiguration().with_defaults().with_max_persistence_crystals(3))
installed = Crystallizer().configuration
same_policy = wanted.get_configuration_dictionary() == installed.get_configuration_dictionary()
print("same_policy:", same_policy)
