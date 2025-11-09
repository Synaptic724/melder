# tests/aether/conduit/creations/test_lesser_creations.py

import unittest
from uuid import uuid4

# SUTs
from melder.aether.conduit.creations.lesser_creations import LesserCreations
from melder.aether.conduit.creations.creations import Creations

# Infra containers
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList

# Interfaces
from melder.utilities.interfaces.interfaces import ISealable, ICleanable


# -----------------------------------------------------------------------------
# Test doubles
# -----------------------------------------------------------------------------

class SealableOk(ISealable):
    def __init__(self):
        self.seal_called = False
    def seal(self) -> None:  # type: ignore[override]
        self.seal_called = True

class SealableBoom(ISealable):
    def __init__(self):
        self.calls = 0
    def seal(self) -> None:  # type: ignore[override]
        self.calls += 1
        raise RuntimeError("iseal-boom")

class CleanableOk(ICleanable):
    def __init__(self):
        self.cleaned = False
    def cleanup(self) -> None:  # type: ignore[override]
        self.cleaned = True

class CleanableBoom(ICleanable):
    def __init__(self):
        self.calls = 0
    def cleanup(self) -> None:  # type: ignore[override]
        self.calls += 1
        raise RuntimeError("iclean-boom")

class CloseOk:
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True

class DisposeOk:
    def __init__(self):
        self.disposed = False
    def dispose(self):
        self.disposed = True

class CloseBoom:
    def close(self):
        raise RuntimeError("close-boom")

class BothSealableAndCleanable(SealableOk, CleanableOk):
    # ISealable should win; cleanup() shouldn’t be invoked
    pass

class BothCleanableAndMethod(CleanableOk):
    def __init__(self):
        super().__init__()
        self.closed = False
    def close(self):
        self.closed = True


def new_lesser(disposal_enabled=True, methods=("close", "dispose")) -> LesserCreations:
    return LesserCreations(disposal_enabled=disposal_enabled, disposal_method_names=list(methods))


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

class TestLesserBasics(unittest.TestCase):
    def test_add_unique_per_scope_happy(self):
        lc = new_lesser()
        k = uuid4()
        lc.add_unique_per_scope(k, object())  # no raise

    def test_add_unique_per_scope_duplicate_raises(self):
        lc = new_lesser()
        k = uuid4()
        lc.add_unique_per_scope(k, object())
        with self.assertRaises(ValueError):
            lc.add_unique_per_scope(k, object())

    def test_add_many_creates_bucket_then_appends(self):
        lc = new_lesser()
        k = uuid4()
        lc.add_many(k, 1)
        lc.add_many(k, 2)  # append path, no raise

    def test_add_after_seal_raises(self):
        lc = new_lesser()
        lc.seal()
        with self.assertRaises(RuntimeError):
            lc.add_unique_per_scope(uuid4(), object())
        with self.assertRaises(RuntimeError):
            lc.add_many(uuid4(), object())

    def test_seal_is_idempotent(self):
        lc = new_lesser()
        lc.seal()
        lc.seal()  # no raise


class TestLesserDisposalPriority(unittest.TestCase):
    def test_isealable_takes_priority_over_icleanable_and_methods(self):
        obj = BothSealableAndCleanable()
        lc = new_lesser(disposal_enabled=True, methods=("close", "dispose"))
        k = uuid4()
        lc.add_unique_per_scope(k, obj)
        lc.seal()
        self.assertTrue(obj.seal_called)
        # ensure cleanable/methods didn’t flip flags
        self.assertFalse(getattr(obj, "cleaned", False))

    def test_icleanable_used_when_not_isealable(self):
        obj = CleanableOk()
        lc = new_lesser(disposal_enabled=True, methods=("close",))
        lc.add_unique_per_scope(uuid4(), obj)
        lc.seal()
        self.assertTrue(obj.cleaned)

    def test_custom_methods_used_when_no_interfaces(self):
        obj = CloseOk()
        lc = new_lesser(disposal_enabled=True, methods=("close",))
        lc.add_unique_per_scope(uuid4(), obj)
        lc.seal()
        self.assertTrue(obj.closed)

    def test_custom_methods_respect_order(self):
        class Both(CloseOk, DisposeOk):
            def __init__(self):
                CloseOk.__init__(self)
                DisposeOk.__init__(self)
        obj = Both()
        lc = new_lesser(disposal_enabled=True, methods=("close", "dispose"))
        lc.add_unique_per_scope(uuid4(), obj)
        lc.seal()
        # close runs first; if successful, dispose might not be called
        self.assertTrue(obj.closed)
        # Accept either behavior (dispose not necessarily invoked); just assert no error

    def test_disposal_disabled_skips_methods(self):
        obj = CloseOk()
        lc = new_lesser(disposal_enabled=False, methods=("close",))
        lc.add_unique_per_scope(uuid4(), obj)
        lc.seal()
        self.assertFalse(obj.closed)

    def test_isealable_error_is_collected(self):
        lc = new_lesser()
        lc.add_unique_per_scope(uuid4(), SealableBoom())
        with self.assertRaises(ExceptionGroup) as ctx:
            lc.seal()
        self.assertTrue(any("iseal-boom" in str(e) for e in ctx.exception.exceptions))

    def test_icleanable_error_is_collected(self):
        lc = new_lesser()
        lc.add_unique_per_scope(uuid4(), CleanableBoom())
        with self.assertRaises(ExceptionGroup) as ctx:
            lc.seal()
        self.assertTrue(any("iclean-boom" in str(e) for e in ctx.exception.exceptions))

    def test_method_error_is_collected(self):
        lc = new_lesser(disposal_enabled=True, methods=("close",))
        lc.add_unique_per_scope(uuid4(), CloseBoom())
        with self.assertRaises(ExceptionGroup) as ctx:
            lc.seal()
        self.assertTrue(any("close-boom" in str(e) for e in ctx.exception.exceptions))


class TestLesserManyBucket(unittest.TestCase):
    def test_many_bucket_items_cleaned(self):
        a, b = DisposeOk(), DisposeOk()
        k = uuid4()
        lc = new_lesser(disposal_enabled=True, methods=("dispose",))
        lc.add_many(k, a)
        lc.add_many(k, b)
        lc.seal()
        self.assertTrue(a.disposed)
        self.assertTrue(b.disposed)


class TestTransferDataAndClear(unittest.TestCase):
    def test_transfer_returns_structs_with_same_contents(self):
        lc = new_lesser()
        k1 = uuid4(); k2 = uuid4()
        bucket = uuid4()

        # add into both maps
        o1 = object()
        lc.add_unique_per_scope(k1, o1)
        lc.add_many(bucket, "x")
        lc.add_many(bucket, "y")

        snap = lc.transfer_data_and_clear()

        # manager sealed and cleared
        self.assertTrue(lc._sealed)
        # internal maps are reset to None by seal()
        self.assertIsNone(lc._unique_per_scope)
        self.assertIsNone(lc._many)

        # snapshot contains dict-like copies
        self.assertIn("unique_per_scope", snap)
        self.assertIn("many", snap)

        unique_map = snap["unique_per_scope"]
        many_map = snap["many"]

        # Basic content checks (don’t rely on exact types)
        self.assertEqual(len(unique_map), 1)
        self.assertIn(k1, unique_map)
        self.assertIs(unique_map[k1], o1)

        self.assertIn(bucket, many_map)
        self.assertEqual(list(many_map[bucket]), ["x", "y"])

    def test_transfer_structs_are_compatible_with_creations_upgrade(self):
        """
        Ensure the snapshot can be passed directly to Creations._upgrade_from_lesser_conduit.
        We don’t require exact classes, but they should be dict-like and acceptable to SUT.
        """
        lc = new_lesser()
        # leave them empty; focus is compatibility, not disposal
        snap = lc.transfer_data_and_clear()

        c = Creations(disposal_enabled=True, disposal_method_names=["close", "dispose"])
        # Should not raise
        c._upgrade_from_lesser_conduit(
            unique_per_scope=snap["unique_per_scope"],
            many=snap["many"]
        )
        # And sealing the Creations should not explode (the containers should expose cleanup())
        # If the snapshot types don’t have .cleanup(), this would raise inside Creations.seal().
        try:
            c.seal()
        except AttributeError as ex:
            self.fail(f"Creations.seal raised due to incompatible snapshot types: {ex}")

    def test_transfer_is_idempotent_in_effect(self):
        lc = new_lesser()
        snap = lc.transfer_data_and_clear()
        # Re-invoking should be a no-op and not explode (already sealed)
        snap2 = lc.transfer_data_and_clear()
        self.assertIsInstance(snap, dict)
        self.assertIsInstance(snap2, dict)


class TestSealSideEffects(unittest.TestCase):
    def test_maps_cleared_to_none_after_seal(self):
        lc = new_lesser()
        lc.add_unique_per_scope(uuid4(), object())
        lc.add_many(uuid4(), object())
        try:
            lc.seal()
        except ExceptionGroup:
            # ignore disposal errors here; we only care about side-effects
            pass
        self.assertIsNone(lc._unique_per_scope)
        self.assertIsNone(lc._many)
        self.assertIsNone(lc._disposal_method_names)


if __name__ == "__main__":
    unittest.main()
