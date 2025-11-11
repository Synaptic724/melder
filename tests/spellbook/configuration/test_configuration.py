# tests/spellbook/test_configuration.py
import unittest
from unittest.mock import MagicMock, patch
import threading

# SUT
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState


class TestConfigurationBasics(unittest.TestCase):
    def test_init_defaults(self):
        cfg = Configuration(aether_frame="alpha")
        self.assertEqual(cfg._aether_frame, "alpha")
        self.assertFalse(cfg._cleaned)
        self.assertFalse(cfg._frozen)
        self.assertIn("system_state", cfg.available_properties)
        self.assertIn("debugging", cfg.available_properties)
        self.assertIn("disposal", cfg.available_properties)
        self.assertIn("disposal_method_names", cfg.available_properties)

    def test_load_default_dictionary_sets_all(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        self.assertTrue(cfg.has_property("system_state"))
        self.assertTrue(cfg.has_property("debugging"))
        self.assertTrue(cfg.has_property("disposal"))
        self.assertTrue(cfg.has_property("disposal_method_names"))
        self.assertIsInstance(cfg.get_property("system_state"), SystemState)
        self.assertEqual(cfg.get_property("system_state"), SystemState.automatic)
        self.assertEqual(cfg.get_property("debugging"), False)
        self.assertEqual(cfg.get_property("disposal"), False)
        self.assertEqual(cfg.get_property("disposal_method_names"), [])

    def test_get_property_missing_raises(self):
        cfg = Configuration()
        with self.assertRaises(KeyError):
            cfg.get_property("not_there")

    def test_has_property_and_iter(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        self.assertTrue(cfg.has_property("system_state"))
        keys = set(iter(cfg))
        self.assertIn("system_state", keys)


class TestEnumConversion(unittest.TestCase):
    def test_set_property_converts_string_to_enum_case_insensitive(self):
        cfg = Configuration()
        cfg.set_property("system_state", "Automatic")  # mixed case
        self.assertEqual(cfg.get_property("system_state"), SystemState.automatic)

    def test_set_property_invalid_enum_string_raises(self):
        cfg = Configuration()
        with self.assertRaises(ValueError):
            cfg.set_property("system_state", "nope")

    def test_set_property_invalid_enum_type_raises(self):
        cfg = Configuration()
        with self.assertRaises(ValueError):
            cfg.set_property("system_state", 123)  # not str or SystemState


class TestSetPropertyAndIdempotency(unittest.TestCase):
    def test_set_property_requires_str_key(self):
        cfg = Configuration()
        with self.assertRaises(TypeError):
            cfg.set_property(123, "x")  # type: ignore[arg-type]

    def test_idempotent_keys_cannot_be_overwritten_before_freeze(self):
        cfg = Configuration()
        cfg.set_property("debugging", False)
        with self.assertRaises(RuntimeError):
            cfg.set_property("debugging", True)

    def test_set_all_properties_then_validate_ok(self):
        cfg = Configuration()
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", True)
        cfg.set_property("disposal", False)
        cfg.set_property("disposal_method_names", ["close"])
        self.assertTrue(cfg.validate())

    def test_validate_missing_properties_raises(self):
        cfg = Configuration()
        # set only some
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", False)
        with self.assertRaises(ValueError) as e:
            cfg.validate()
        self.assertIn("Missing required configuration property", str(e.exception))

    def test_validate_wrong_type_raises(self):
        cfg = Configuration()
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", "yes")  # wrong type
        cfg.set_property("disposal", False)
        cfg.set_property("disposal_method_names", [])
        with self.assertRaises(ValueError):
            cfg.validate()


class TestFreezeAndcleanup(unittest.TestCase):
    def test_freeze_sets_flags_and_blocks_changes(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        cfg.freeze()
        # freeze => immutable, NOT disposed; only assert _frozen
        self.assertTrue(cfg._frozen)
        # _cleaned is disposal-only; do NOT assert it here
        with self.assertRaises(RuntimeError):
            cfg.set_property("debugging", True)
        with self.assertRaises(RuntimeError):
            cfg.clear_properties()

    def test_freeze_fails_if_validation_fails(self):
        cfg = Configuration()
        # Corrupt types so validate fails
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", "nope")  # wrong
        cfg.set_property("disposal", False)
        cfg.set_property("disposal_method_names", [])
        with self.assertRaises(ValueError):
            cfg.freeze()

    def test_cleanup_idempotent(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        cfg.cleanup()
        self.assertTrue(cfg._cleaned)
        self.assertTrue(cfg._frozen)
        # second call should not throw
        cfg.cleanup()
        # After cleaned, clearing should fail (frozen check runs first)
        with self.assertRaises(RuntimeError):
            cfg.clear_properties()

    def test_clear_before_freeze_is_allowed(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        # Unfreeze path: clear should work
        cfg._frozen = False
        cfg._cleaned = False
        cfg.clear_properties()
        self.assertFalse(cfg.has_property("system_state"))
        self.assertFalse(cfg.has_property("debugging"))
        self.assertFalse(cfg.has_property("disposal"))
        self.assertFalse(cfg.has_property("disposal_method_names"))


class TestValidationEnumsConsistency(unittest.TestCase):
    def test_validate_enums_requires_system_state_enum_instance(self):
        cfg = Configuration()
        # Insert invalid type directly to simulate external corruption
        cfg._properties["system_state"] = "automatic"  # NOT converted
        cfg._properties["debugging"] = False
        cfg._properties["disposal"] = False
        cfg._properties["disposal_method_names"] = []
        with self.assertRaises(ValueError) as e:
            cfg.validate()
        self.assertIn("expected SystemState", str(e.exception))


class TestConcurrencyAndLocking(unittest.TestCase):
    def test_reentrant_lock_during_reads(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        # Acquire the lock manually and call get_property -> should not deadlock
        with cfg._lock:
            v = cfg.get_property("debugging")
        self.assertEqual(v, False)

    def test_concurrent_like_updates_sequence(self):
        cfg = Configuration()
        # Simulate interleaved calls that obey idempotency
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", False)
        cfg.set_property("disposal", False)
        cfg.set_property("disposal_method_names", [])
        # Freeze should succeed
        cfg.freeze()
        self.assertTrue(cfg._frozen)
        # Any further change is blocked
        with self.assertRaises(RuntimeError):
            cfg.set_property("debugging", True)


class TestLoadDefaultsAndThenFreeze(unittest.TestCase):
    def test_load_defaults_then_validate_then_freeze(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        self.assertTrue(cfg.validate())
        cfg.freeze()
        # freeze => immutable, NOT disposed; only assert _frozen
        self.assertTrue(cfg._frozen)
        # Do not assert _cleaned here; cleanup is for cleanup/disposal semantics


    def test_load_defaults_idempotent_overwrite_blocked(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        with self.assertRaises(RuntimeError):
            cfg.set_property("system_state", SystemState.dynamic)  # idempotent key already present


class TestEdgeCases(unittest.TestCase):
    def test_disposal_method_names_type(self):
        cfg = Configuration()
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", False)
        cfg.set_property("disposal", False)
        cfg.set_property("disposal_method_names", ["close", "cleanup"])
        self.assertTrue(cfg.validate())

    def test_disposal_method_names_wrong_type_raises(self):
        cfg = Configuration()
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", False)
        cfg.set_property("disposal", False)
        cfg.set_property("disposal_method_names", "close")  # wrong: not a list
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_cannot_clear_when_frozen_or_cleaned(self):
        cfg = Configuration()
        cfg.load_default_dictionary()
        cfg.freeze()
        with self.assertRaises(RuntimeError):
            cfg.clear_properties()
        # Also when cleaned separately
        cfg2 = Configuration()
        cfg2.load_default_dictionary()
        cfg2.cleanup()
        with self.assertRaises(RuntimeError):
            cfg2.clear_properties()

    def test_setting_all_then_overwrite_any_idempotent_raises(self):
        cfg = Configuration()
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", False)
        cfg.set_property("disposal", True)
        cfg.set_property("disposal_method_names", [])
        with self.assertRaises(RuntimeError):
            cfg.set_property("disposal", False)

    def test_freeze_without_defaults_but_all_set_ok(self):
        cfg = Configuration()
        cfg.set_property("system_state", SystemState.automatic)
        cfg.set_property("debugging", True)
        cfg.set_property("disposal", True)
        cfg.set_property("disposal_method_names", ["close"])
        cfg.freeze()
        self.assertTrue(cfg._frozen)

    def test_validate_error_messages_are_informative(self):
        cfg = Configuration()
        # only set one prop
        cfg.set_property("system_state", SystemState.automatic)
        try:
            cfg.validate()
            self.fail("Expected ValueError for missing properties")
        except ValueError as e:
            msg = str(e)
            self.assertIn("Missing required configuration property", msg)
            # Should mention at least one missing key name
            self.assertTrue(any(k in msg for k in ["debugging", "disposal", "disposal_method_names"]))


if __name__ == "__main__":
    unittest.main()
