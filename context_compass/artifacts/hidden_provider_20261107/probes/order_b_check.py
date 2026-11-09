"""ORDER cases under the emulated rule, option A (mode 1) vs option B announcers (mode 2)."""
import os
import hidden_provider_plugin
hidden_provider_plugin.HiddenProviderProbe(emulate=os.environ.get("MELDER_PROBE_HIDDEN") in ("1", "2")).apply()
import hidden_class_probe as p
counter = [0]
p.run_order_case("framed", dict(spell=p.English, spellframe=p.Greeter, binding_name="english"), counter)
p.run_order_case("category", dict(spell=p.English, spellframe="greeters"), counter)
p.run_order_case("bare_named", dict(spell=p.English, binding_name="english"), counter)
p.run_order_case("bare", dict(spell=p.English), counter)
