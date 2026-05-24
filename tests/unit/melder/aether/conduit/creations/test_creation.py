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
        Verify that a new Creation preserves the wrapped value and starts live.
        """
        assert creation.value is sample_value
        assert creation.has_disposal_methods is False
        assert creation.disposal_method_names == []
        assert creation._cleaned is False

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

    # ------------------------------------------------------------------
    # Rank B: Concurrency/Locking Tests
    # ------------------------------------------------------------------
