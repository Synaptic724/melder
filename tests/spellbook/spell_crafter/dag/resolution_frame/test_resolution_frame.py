import unittest
from typing import Any, Dict

from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import ResolutionFrame  # adjust import path as needed


class TestResolutionFrame(unittest.TestCase):
    def test_frame_has_unique_id(self):
        frame1 = ResolutionFrame()
        frame2 = ResolutionFrame()
        self.assertIsInstance(frame1.id, str)
        self.assertIsInstance(frame2.id, str)
        self.assertNotEqual(frame1.id, frame2.id)

    def test_overrides_are_copied_not_aliased(self):
        source: Dict[str, Any] = {"a": 1}
        frame = ResolutionFrame(source)
        source["a"] = 2
        self.assertEqual(frame.get_override("a"), 1)

    def test_overrides_property_returns_copy(self):
        frame = ResolutionFrame({"x": 10})
        overrides = frame.overrides
        self.assertEqual(overrides["x"], 10)
        overrides["x"] = 20
        self.assertEqual(frame.get_override("x"), 10)

    def test_results_property_returns_copy(self):
        frame = ResolutionFrame()
        frame.set_result("node1", object())
        results = frame.results
        self.assertIn("node1", results)
        results.pop("node1")
        self.assertTrue(frame.has_result("node1"))

    def test_errors_property_returns_copy(self):
        frame = ResolutionFrame()
        err = RuntimeError("boom")
        frame.register_error("node1", err)
        errors = frame.errors
        self.assertIn("node1", errors)
        errors.pop("node1")
        self.assertIsNotNone(frame.get_error("node1"))

    def test_has_override_true_when_key_present(self):
        frame = ResolutionFrame({"param": 123})
        self.assertTrue(frame.has_override("param"))

    def test_has_override_false_when_key_missing(self):
        frame = ResolutionFrame({"param": 123})
        self.assertFalse(frame.has_override("other"))

    def test_get_override_returns_value(self):
        frame = ResolutionFrame({"param": "value"})
        self.assertEqual(frame.get_override("param"), "value")

    def test_get_override_raises_key_error_when_missing(self):
        frame = ResolutionFrame()
        with self.assertRaises(KeyError):
            _ = frame.get_override("missing")

    def test_results_initially_empty(self):
        frame = ResolutionFrame()
        self.assertEqual(frame.results, {})
        self.assertFalse(frame.has_result("any"))

    def test_set_and_get_result_round_trip(self):
        frame = ResolutionFrame()
        obj = object()
        frame.set_result("node1", obj)
        self.assertTrue(frame.has_result("node1"))
        self.assertIs(frame.get_result("node1"), obj)

    def test_get_result_raises_key_error_when_missing(self):
        frame = ResolutionFrame()
        with self.assertRaises(KeyError):
            _ = frame.get_result("missing")

    def test_register_error_and_get_error_round_trip(self):
        frame = ResolutionFrame()
        err = ValueError("bad")
        frame.register_error("node1", err)
        self.assertIs(frame.get_error("node1"), err)

    def test_get_error_returns_none_when_not_recorded(self):
        frame = ResolutionFrame()
        self.assertIsNone(frame.get_error("nodeX"))

    def test_register_error_rejects_empty_node_id(self):
        frame = ResolutionFrame()
        with self.assertRaises(ValueError):
            frame.register_error("", RuntimeError("x"))

    def test_register_error_rejects_none_error(self):
        frame = ResolutionFrame()
        with self.assertRaises(ValueError):
            frame.register_error("node1", None)  # type: ignore[arg-type]

    def test_cleanup_clears_overrides_results_and_errors(self):
        frame = ResolutionFrame({"a": 1})
        frame.set_result("node1", 123)
        frame.register_error("node2", RuntimeError("boom"))

        frame.cleanup()

        # After cleanup, internal mappings should be nulled out
        self.assertIsNone(frame._overrides)
        self.assertIsNone(frame._results)
        self.assertIsNone(frame._errors)

    def test_cleanup_is_idempotent(self):
        frame = ResolutionFrame({"a": 1})
        frame.set_result("node1", 123)
        frame.register_error("node2", RuntimeError("boom"))

        frame.cleanup()
        frame.cleanup()  # should not raise

        # Still nulled out after second cleanup
        self.assertIsNone(frame._overrides)
        self.assertIsNone(frame._results)
        self.assertIsNone(frame._errors)


    def test_operations_raise_after_cleanup_set_result(self):
        frame = ResolutionFrame()
        frame.cleanup()
        with self.assertRaises(Exception):
            frame.set_result("node1", 1)

    def test_operations_raise_after_cleanup_get_override(self):
        frame = ResolutionFrame({"a": 1})
        frame.cleanup()
        with self.assertRaises(Exception):
            _ = frame.get_override("a")


if __name__ == "__main__":
    unittest.main()
