"""Run hidden_class_probe with the PROPOSED rule patched in (hidden_provider_plugin's patches, no pytest)."""
import sys
import hidden_provider_plugin

probe = hidden_provider_plugin.HiddenProviderProbe(emulate=True)
probe.apply()
import hidden_class_probe
hidden_class_probe.main()
