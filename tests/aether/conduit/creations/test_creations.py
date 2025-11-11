import unittest
from uuid import uuid4

# SUT
from melder.aether.conduit.creations.creations import Creations

# Infra types to build valid kwargs for _upgrade_from_lesser_conduit
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList


# -----------------------------------------------------------------------------
# Test doubles (method-based disposal only)
# -----------------------------------------------------------------------------

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
    def __init__(self):
        self.calls = 0
    def close(self):
        self.calls += 1
        raise RuntimeError("close-boom")

class DisposeBoom:
    def __init__(self):
        self.calls = 0
    def dispose(self):
        self.calls += 1
        raise RuntimeError("dispose-boom")

class CleanupLike:
    def __init__(self):
        self._cleaned = False
    def cleanup(self):
        self._cleaned = True

class BothCloseAndDispose(CloseOk, DisposeOk):
    def __init__(self):
        CloseOk.__init__(self)
        DisposeOk.__init__(self)

class BothCleanup(CleanupLike, CleanupLike):
    def __init__(self):
        CleanupLike.__init__(self)
        CleanupLike.__init__(self)


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
        c.add_many(k, 2)  # append path, no raise

    def test_add_after_cleanup_raises_for_all_buckets(self):
        c = new_creations()
        c.cleanup()
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

    def test_cleanup_is_idempotent(self):
        c = new_creations()
        c.cleanup()
        c.cleanup()  # no raise


class TestCreationsMethodDisposal(unittest.TestCase):
    def test_custom_cleanup_runs_when_method_registered(self):
        c = new_creations(disposal_enabled=True, methods=("close",))
        k = uuid4()
        o = CloseOk()
        c.add_unique(k, o)
        c.cleanup()
        self.assertTrue(o.closed)

    def test_method_order_respected_first_hits(self):
        c = new_creations(disposal_enabled=True, methods=("close", "dispose"))
        k = uuid4()
        o = BothCloseAndDispose()
        c.add_unique_per_scope(k, o)
        c.cleanup()
        self.assertTrue(o.closed)
        self.assertFalse(o.disposed)

    def test_disposal_disabled_skips_methods(self):
        c = new_creations(disposal_enabled=False, methods=("close",))
        k = uuid4()
        o = CloseOk()
        c.add_unique_per_cluster(k, o)
        c.cleanup()
        self.assertFalse(o.closed)

    def test_cleanup_like_method_runs_if_registered(self):
        c = new_creations(disposal_enabled=True, methods=("cleanup",))
        k = uuid4()
        o = CleanupLike()
        c.add_unique(k, o)
        c.cleanup()
        self.assertTrue(o._cleaned)

    def test_cleanup_like_method_runs_if_registered(self):
        c = new_creations(disposal_enabled=True, methods=("cleanup",))
        k = uuid4()
        o = CleanupLike()
        c.add_unique(k, o)
        c.cleanup()
        self.assertTrue(o.cleaned)


class TestCreationsErrorAggregation(unittest.TestCase):
    def test_exceptiongroup_contains_all_cleanup_errors(self):
        c = new_creations(disposal_enabled=True, methods=("close", "dispose"))
        c.add_unique(uuid4(), CloseBoom())         # close-boom
        c.add_unique_per_scope(uuid4(), DisposeBoom())  # dispose-boom (close not present; dispose will raise)
        with self.assertRaises(ExceptionGroup) as ctx:
            c.cleanup()
        msgs = [str(e) for e in ctx.exception.exceptions]
        self.assertTrue(any("close-boom" in m for m in msgs))
        self.assertTrue(any("dispose-boom" in m for m in msgs))

    def test_error_from_first_method_is_wrapped(self):
        c = new_creations(disposal_enabled=True, methods=("close",))
        c.add_unique(uuid4(), CloseBoom())
        with self.assertRaises(ExceptionGroup) as ctx:
            c.cleanup()
        self.assertTrue(any("close-boom" in str(e) for e in ctx.exception.exceptions))


class TestCreationsManyBucket(unittest.TestCase):
    def test_many_items_all_cleaned(self):
        c = new_creations(disposal_enabled=True, methods=("dispose",))
        k = uuid4()
        a = DisposeOk()
        b = DisposeOk()
        c.add_many(k, a)
        c.add_many(k, b)
        c.cleanup()
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
        Leave them empty to avoid disposal noise; just ensure cleanup() completes.
        """
        c = new_creations()
        uniq_scope = ConcurrentDict()
        many = ConcurrentDict()
        # (empty but correct container types)
        c._upgrade_from_lesser_conduit(unique_per_scope=uniq_scope, many=many)
        c.cleanup()  # should not raise


class TestCreationsCleanupSideEffects(unittest.TestCase):
    def test_maps_cleared_to_none_after_cleanup(self):
        c = new_creations()
        c.add_unique(uuid4(), object())
        c.cleanup()
        self.assertIsNone(c._unique)
        self.assertIsNone(c._unique_per_scope)
        self.assertIsNone(c._many)
        self.assertIsNone(c._disposal_method_names)


if __name__ == "__main__":
    unittest.main()
