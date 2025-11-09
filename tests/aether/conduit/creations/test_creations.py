# tests/aether/conduit/creations/test_creations.py

import unittest
from uuid import uuid4

# SUT
from melder.aether.conduit.creations.creations import Creations

# Infra types to build valid kwargs for _upgrade_from_lesser_conduit
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList

# Interface
from melder.utilities.interfaces.interfaces import ISealable


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
        raise RuntimeError("boom")

class CleanupOk:
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True

class CleanupAlsoOk:
    def __init__(self):
        self.disposed = False
    def dispose(self):
        self.disposed = True

class CleanupBoom:
    def __init__(self):
        self.calls = 0
    def close(self):
        self.calls += 1
        raise RuntimeError("nope")


def new_creations(disposal_enabled=True, methods=("close", "dispose")) -> Creations:
    return Creations(disposal_enabled=disposal_enabled, disposal_method_names=list(methods))


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

class TestCreationsBasics(unittest.TestCase):
    def test_add_unique_happy(self):
        c = new_creations()
        k = uuid4()
        c.add_unique(k, object())  # no raise

    def test_add_unique_duplicate_key_raises(self):
        c = new_creations()
        k = uuid4()
        c.add_unique(k, object())
        with self.assertRaises(ValueError):
            c.add_unique(k, object())

    def test_add_unique_per_lineage_happy(self):
        c = new_creations()
        k = uuid4()
        c.add_unique_per_lineage(k, object())  # no raise

    def test_add_unique_per_lineage_duplicate(self):
        c = new_creations()
        k = uuid4()
        c.add_unique_per_lineage(k, object())
        with self.assertRaises(ValueError):
            c.add_unique_per_lineage(k, object())

    def test_add_unique_per_cluster_happy(self):
        c = new_creations()
        k = uuid4()
        c.add_unique_per_cluster(k, object())  # no raise

    def test_add_unique_per_cluster_duplicate(self):
        c = new_creations()
        k = uuid4()
        c.add_unique_per_cluster(k, object())
        with self.assertRaises(ValueError):
            c.add_unique_per_cluster(k, object())

    def test_add_unique_per_scope_happy(self):
        c = new_creations()
        k = uuid4()
        c.add_unique_per_scope(k, object())  # no raise

    def test_add_unique_per_scope_duplicate(self):
        c = new_creations()
        k = uuid4()
        c.add_unique_per_scope(k, object())
        with self.assertRaises(ValueError):
            c.add_unique_per_scope(k, object())

    def test_add_many_creates_collection_and_appends(self):
        c = new_creations()
        k = uuid4()
        c.add_many(k, 1)
        c.add_many(k, 2)  # no raise; append path

    def test_add_after_seal_raises_for_all_buckets(self):
        c = new_creations()
        c.seal()
        with self.assertRaises(RuntimeError):
            c.add_unique(uuid4(), object())
        with self.assertRaises(RuntimeError):
            c.add_unique_per_scope(uuid4(), object())
        with self.assertRaises(RuntimeError):
            c.add_unique_per_lineage(uuid4(), object())
        with self.assertRaises(RuntimeError):
            c.add_unique_per_cluster(uuid4(), object())
        with self.assertRaises(RuntimeError):
            c.add_many(uuid4(), object())

    def test_seal_is_idempotent(self):
        c = new_creations()
        c.seal()
        c.seal()  # no raise


class TestCreationsDisposalPriority(unittest.TestCase):
    def test_isealable_takes_priority_over_custom_cleanup(self):
        class Both(SealableOk):
            def __init__(self):
                super().__init__()
                self.closed = False
            def close(self):
                self.closed = True

        c = new_creations(disposal_enabled=True, methods=("close",))
        k = uuid4()
        o = Both()
        c.add_unique(k, o)
        c.seal()
        self.assertTrue(o.seal_called, "ISealable.seal should have been called")

    def test_custom_cleanup_runs_when_not_isealable(self):
        c = new_creations(disposal_enabled=True, methods=("close",))
        k = uuid4()
        o = CleanupOk()
        c.add_unique(k, o)
        c.seal()
        self.assertTrue(o.closed)

    def test_custom_cleanup_respects_method_order(self):
        class Both(CleanupOk):
            def __init__(self):
                super().__init__()
                self.disposed = False
            def dispose(self):
                self.disposed = True

        c = new_creations(disposal_enabled=True, methods=("close", "dispose"))
        k = uuid4()
        o = Both()
        c.add_unique_per_scope(k, o)
        c.seal()
        self.assertTrue(o.closed)
        # Since close() succeeded, dispose() need not be called; ensure it's not set True by accident.
        self.assertFalse(o.disposed)

    def test_disposal_disabled_skips_custom_methods(self):
        c = new_creations(disposal_enabled=False, methods=("close",))
        k = uuid4()
        o = CleanupOk()
        c.add_unique_per_cluster(k, o)
        c.seal()
        self.assertFalse(o.closed)


class TestCreationsErrorAggregation(unittest.TestCase):
    def test_exceptiongroup_contains_all_cleanup_errors(self):
        c = new_creations(disposal_enabled=True, methods=("close",))
        c.add_unique(uuid4(), CleanupBoom())
        c.add_unique_per_scope(uuid4(), CleanupBoom())
        with self.assertRaises(ExceptionGroup) as ctx:
            c.seal()
        self.assertGreaterEqual(len(ctx.exception.exceptions), 2)

    def test_error_from_isealable_is_wrapped(self):
        c = new_creations()
        c.add_unique(uuid4(), SealableBoom())
        with self.assertRaises(ExceptionGroup) as ctx:
            c.seal()
        self.assertTrue(any("Failed to seal ISeal object" in str(e) for e in ctx.exception.exceptions))


class TestCreationsManyBucket(unittest.TestCase):
    def test_many_items_all_cleaned(self):
        c = new_creations(disposal_enabled=True, methods=("dispose",))
        k = uuid4()
        a = CleanupAlsoOk()
        b = CleanupAlsoOk()
        c.add_many(k, a)
        c.add_many(k, b)
        c.seal()
        self.assertTrue(a.disposed)
        self.assertTrue(b.disposed)


class TestCreationsUpgradeFromLesser(unittest.TestCase):
    def test_upgrade_rejects_when_both_not_empty(self):
        """
        SUT raises only if BOTH _unique_per_scope and _many are non-empty
        (because it checks with AND). Populate both to trigger.
        """
        c = new_creations()
        # populate both via public APIs
        c.add_unique_per_scope(uuid4(), object())
        k_many = uuid4()
        c.add_many(k_many, object())
        with self.assertRaises(RuntimeError):
            c._upgrade_from_lesser_conduit(unique_per_scope=ConcurrentDict(), many=ConcurrentDict())

    def test_upgrade_transfers_references_with_valid_types(self):
        """
        Pass actual ConcurrentDict/ConcurrentList so later .cleanup() calls exist.
        Leave them empty to avoid disposal noise; just ensure seal() completes.
        """
        c = new_creations()
        uniq_scope = ConcurrentDict()
        many = ConcurrentDict()
        # (empty but correct container types)
        c._upgrade_from_lesser_conduit(unique_per_scope=uniq_scope, many=many)
        c.seal()  # should not raise


class TestCreationsSealSideEffects(unittest.TestCase):
    def test_maps_cleared_to_none_after_seal(self):
        c = new_creations()
        c.add_unique(uuid4(), object())
        c.seal()
        self.assertIsNone(c._unique)
        self.assertIsNone(c._unique_per_scope)
        self.assertIsNone(c._many)
        self.assertIsNone(c._disposal_method_names)


if __name__ == "__main__":
    unittest.main()
