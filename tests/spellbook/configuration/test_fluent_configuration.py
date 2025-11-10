# tests/spellbook/configuration/test_fluent_configuration.py
import unittest

from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState


class TestConfigurationFluentAPI(unittest.TestCase):
    # --- happy paths that DON'T set the same idempotent key twice ---

    def test_with_system_state_accepts_enum_on_fresh_config(self):
        cfg = Configuration().with_system_state(SystemState.dynamic)
        self.assertEqual(cfg.get_property("system_state"), SystemState.dynamic)

    def test_with_system_state_accepts_str_case_insensitive_on_fresh_config(self):
        cfg = Configuration().with_system_state("DyNaMiC")
        self.assertEqual(cfg.get_property("system_state"), SystemState.dynamic)

    def test_with_debugging_sets_flag_on_fresh_config(self):
        cfg = Configuration().with_debugging(True)
        self.assertTrue(cfg.get_property("debugging"))

    def test_with_disposal_sets_flag_on_fresh_config(self):
        cfg = Configuration().with_disposal(True)
        self.assertTrue(cfg.get_property("disposal"))

    def test_with_disposal_method_names_sets_once(self):
        cfg = Configuration().with_disposal_method_names(["close", "cleanup"])
        self.assertEqual(cfg.get_property("disposal_method_names"), ["close", "cleanup"])

    def test_add_disposal_methods_sets_once_from_empty(self):
        # On a fresh config, the key is unset; a single additive set is allowed.
        cfg = Configuration().add_disposal_methods("close", "cleanup", "close", "finalize")
        self.assertEqual(cfg.get_property("disposal_method_names"),
                         ["close", "cleanup", "finalize"])

    def test_chaining_returns_self_without_double_setting_same_key(self):
        # IMPORTANT: do not call with_defaults() if you plan to set idempotent keys explicitly.
        cfg = (
            Configuration()
            .with_system_state("dynamic")
            .with_debugging(True)
            .with_disposal(False)
            .with_disposal_method_names(["close", "cleanup"])
        )
        self.assertIsInstance(cfg, Configuration)
        self.assertEqual(cfg.get_property("system_state"), SystemState.dynamic)
        self.assertTrue(cfg.get_property("debugging"))
        self.assertFalse(cfg.get_property("disposal"))
        self.assertEqual(cfg.get_property("disposal_method_names"), ["close", "cleanup"])

# REPLACE in tests/spellbook/configuration/test_fluent_configuration.py

    def test_finalize_freezes_and_blocks_any_further_mutation(self):
        # Set EACH idempotent key exactly once, then freeze.
        cfg = (
            Configuration()
            .with_system_state("dynamic")
            .with_debugging(True)
            .with_disposal(False)
            .with_disposal_method_names([])
            .finalize()
        )
        self.assertTrue(cfg._frozen)
        with self.assertRaises(RuntimeError):
            cfg.with_disposal(True)        # frozen -> no mutations
        with self.assertRaises(RuntimeError):
            cfg.add_disposal_methods("x")  # frozen -> no mutations


    def test_build_aliases_finalize(self):
        # Use defaults to set ALL required props once, then freeze.
        cfg = Configuration().with_defaults().build()
        self.assertTrue(cfg._frozen)
        # Any further set on an idempotent key must raise (frozen OR overwrite).
        with self.assertRaises(RuntimeError):
            cfg.with_system_state("dynamic")


    # --- idempotency: second set on the same key must raise ---

    def test_with_system_state_overwrite_raises(self):
        cfg = Configuration().with_system_state("automatic")
        with self.assertRaises(RuntimeError):
            cfg.with_system_state("dynamic")

    def test_with_debugging_overwrite_raises(self):
        cfg = Configuration().with_debugging(False)
        with self.assertRaises(RuntimeError):
            cfg.with_debugging(True)

    def test_with_disposal_overwrite_raises(self):
        cfg = Configuration().with_disposal(False)
        with self.assertRaises(RuntimeError):
            cfg.with_disposal(True)

    def test_with_disposal_method_names_overwrite_raises(self):
        cfg = Configuration().with_disposal_method_names(["close"])
        with self.assertRaises(RuntimeError):
            cfg.with_disposal_method_names(["cleanup"])

    def test_add_disposal_methods_second_call_raises(self):
        cfg = Configuration().add_disposal_methods("close", "cleanup")
        with self.assertRaises(RuntimeError):
            cfg.add_disposal_methods("finalize")  # second set -> overwrite -> raise

    # --- defaults helper: once defaults set keys, trying to set again must raise ---

    def test_with_defaults_then_attempt_to_set_idempotent_keys_raises(self):
        cfg = Configuration().with_defaults()
        # defaults already set: setting again should raise
        with self.assertRaises(RuntimeError):
            cfg.with_system_state("dynamic")
        with self.assertRaises(RuntimeError):
            cfg.with_debugging(True)
        with self.assertRaises(RuntimeError):
            cfg.with_disposal(True)
        with self.assertRaises(RuntimeError):
            cfg.with_disposal_method_names(["close"])

    # --- presets are incompatible with idempotent system_state after defaults ---

    def test_dynamic_defaults_raises_under_current_idempotent_contract(self):
        # dynamic_defaults() calls with_defaults() then tries to set system_state again.
        with self.assertRaises(RuntimeError):
            Configuration().dynamic_defaults()

    def test_automatic_defaults_raises_under_current_idempotent_contract(self):
        # automatic_defaults() calls with_defaults() then tries to set system_state again.
        with self.assertRaises(RuntimeError):
            Configuration().automatic_defaults()


if __name__ == "__main__":
    unittest.main()
