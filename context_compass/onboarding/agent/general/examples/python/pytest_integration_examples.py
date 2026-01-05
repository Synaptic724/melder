"""
Purpose:
- Show integration tests for multi-component behavior.

Notes:
- Keep scope minimal and ensure failures indicate real wiring regressions.
- Use integration markers consistently when the repo supports them.
"""

import pytest


class Service:
    """
    Example service that coordinates two collaborators.
    """

    def __init__(self, left: int, right: int) -> None:
        """
        Initialize the service.

        Args:
            left (int): Left value.
            right (int): Right value.
        """
        self._left = left
        self._right = right

    def total(self) -> int:
        """
        Return the combined total.
        """
        return self._left + self._right


@pytest.mark.integration
def test_service_total_integration() -> None:
    """
    Validate the service integrates values correctly.
    """
    service = Service(4, 6)
    assert service.total() == 10
