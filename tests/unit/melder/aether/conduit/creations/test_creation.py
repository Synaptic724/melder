import threading
import pytest
from unittest.mock import MagicMock, patch

# Adjust the import path based on your actual project structure
from melder.aether.conduit.creations.creation import Creation


class TestCreation:
    """
    Tests for the Creation wrapper class.

    Covers Rank A (Behavioral) and Rank B (Lifecycle) tests as per AGENTS.md.
    """

    @pytest.fixture
    def sample_value(self):
        """Returns a simple object to be wrapped."""
        return {"data": "test_payload"}

    @pytest.fixture
    def creation(self, sample_value):
        """Returns a Creation instance wrapping the sample value."""
        return Creation(sample_value)

    # ------------------------------------------------------------------
    # Rank A: Behavioral Unit Contract Tests
    # ------------------------------------------------------------------

    def test_initialization_sets_contract_fields(self, creation, sample_value):
        """
        Verify that a new Creation has a unique ID, the correct value, and is not cleaned.
        """
        # Assert: ID is a string and looks like a ULID (length check is a decent proxy)
        assert isinstance(creation.id, str)
        assert len(creation.id) == 26  # ULID length

        # Assert: Value is preserved
        assert creation.value is sample_value

        # Assert: Not cleaned by default (checking internal state via Cleanable contract if exposed,
        # or implicitly via behavior)
        # Note: Accessing private _cleaned for test verification is acceptable in unit tests
        # per common python testing practices, though AGENTS.md prefers public behavior.
        # We'll rely on the behavior that properties still work.
        assert creation.value is not None

    def test_repr_includes_identity_and_value(self, creation):
        """
        Verify __repr__ provides useful debugging info (id and value).
        """
        repr_str = repr(creation)
        assert "Creation" in repr_str
        assert f"id={creation.id}" in repr_str
        assert "value={'data': 'test_payload'}" in repr_str

    # ------------------------------------------------------------------
    # Rank B: State Transition Tests (Lifecycle/Cleanup)
    # ------------------------------------------------------------------

    def test_cleanup_is_idempotent_and_nulls_references(self, creation):
        """
        Verify that cleanup nulls internal references and can be called multiple times without error.
        """
        # Act: First cleanup
        creation.cleanup()

        # Assert: References are nulled
        # We access protected members here to verify the deleted-field contract
        # for owned cleanup surfaces.
        assert not hasattr(creation, "_value")
        assert not hasattr(creation, "_lock")
        assert creation._cleaned is True

        # Act: Second cleanup (idempotence check)
        try:
            creation.cleanup()
        except Exception as e:
            pytest.fail(f"cleanup() raised an exception on second call: {e}")

    def test_cleanup_does_not_dispose_wrapped_value(self):
        """
        Verify the contract that Creation.cleanup() does NOT call close/cleanup on the wrapped object.
        """
        # Arrange
        mock_value = MagicMock()
        creation = Creation(mock_value)

        # Act
        creation.cleanup()

        # Assert: The wrapper is cleaned, but the inner object was untouched
        assert not hasattr(creation, "_value")
        mock_value.cleanup.assert_not_called()
        mock_value.close.assert_not_called()

    def test_disposal_metadata_properties_reflect_live_and_cleaned_state(self, sample_value):
        """
        Verify disposal metadata properties expose live values and clear after cleanup.

        Contract:
        - `has_disposal_methods` and `disposal_method_names` report constructor metadata while active.
        - Both properties return None after cleanup.
        """
        creation = Creation(
            sample_value,
            has_disposal_methods=True,
            disposal_methods=["close", "dispose"],
        )

        assert creation.has_disposal_methods is True
        assert creation.disposal_method_names == ["close", "dispose"]

        creation.cleanup()

        with pytest.raises(AttributeError):
            _ = creation.has_disposal_methods
        with pytest.raises(AttributeError):
            _ = creation.disposal_method_names

    def test_cleanup_returns_when_another_cleanup_completes_before_second_check(self, sample_value):
        """
        Verify cleanup returns cleanly when the object is already cleaned inside the lock.

        Contract:
        - The second `_cleaned` guard returns without raising.
        - State written by the concurrent cleanup remains intact.
        """

        class ConcurrentCleanupLock:
            """
            Context manager that simulates another cleanup finishing before the second check.
            """

            def __init__(self, creation: Creation) -> None:
                """
                Store the creation whose state will be flipped during entry.

                Args:
                    creation: Creation instance under test.
                """
                self._creation = creation

            def __enter__(self) -> "ConcurrentCleanupLock":
                """
                Simulate a completed cleanup before the guarded re-check executes.

                Returns:
                    This context manager instance.
                """
                self._creation._cleaned = True
                self._creation._value = None
                self._creation._has_disposal_methods = None
                self._creation._disposal_methods = None
                self._creation._lock = None
                return self

            def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> bool:
                """
                Exit without suppressing exceptions.

                Args:
                    exc_type: Exception type if any.
                    exc_value: Exception instance if any.
                    traceback: Traceback object if any.
                Returns:
                    False so exceptions are not swallowed.
                """
                return False

        creation = Creation(
            sample_value,
            has_disposal_methods=True,
            disposal_methods=["close"],
        )
        creation._lock = ConcurrentCleanupLock(creation)

        creation.cleanup()

        assert creation.value is None
        assert creation.has_disposal_methods is None
        assert creation.disposal_method_names is None

    # ------------------------------------------------------------------
    # Rank B: Concurrency/Locking Tests
    # ------------------------------------------------------------------

    def test_context_manager_acquires_and_releases_lock(self, sample_value):
        """
        Verify that using Creation as a context manager operates the internal lock.
        """
        # Arrange: Mock the RLock to verify calls
        with patch("threading.RLock") as MockRLock:
            mock_lock_instance = MockRLock.return_value

            # Initialize with mocked lock
            creation = Creation(sample_value)

            # Act
            with creation as c:
                assert c is creation
                # Verify acquire was called upon entry
                mock_lock_instance.acquire.assert_called_once()
                # Verify release has NOT been called yet
                mock_lock_instance.release.assert_not_called()

            # Assert: Release called upon exit
            mock_lock_instance.release.assert_called_once()

    def test_context_manager_releases_lock_on_exception(self, sample_value):
        """
        Purpose:
            Verify the context manager releases the lock when exceptions occur.
        Contract:
            - acquire is called on entry.
            - release is called on exit even when the body raises.
            - exceptions propagate to the caller.
        Returns:
            None.
        Raises:
            AssertionError: If the lock is not released or errors are swallowed.
        """
        with patch("threading.RLock") as MockRLock:
            mock_lock_instance = MockRLock.return_value
            creation = Creation(sample_value)

            with pytest.raises(ValueError, match="boom"):
                with creation:
                    raise ValueError("boom")

            mock_lock_instance.acquire.assert_called_once()
            mock_lock_instance.release.assert_called_once()
