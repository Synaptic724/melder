"""
Purpose:
- Show unit tests with fixtures and contract-level assertions.

Notes:
- Mock true boundaries only (filesystem, OS, network, time).
- Keep assertions focused on public behavior and error paths.
"""

from unittest import mock

import pytest


class Adder:
    """
    Adds two integers with input validation.
    """

    def add(self, left: int, right: int) -> int:
        """
        Add two integers.

        Args:
            left (int): Left operand.
            right (int): Right operand.

        Returns:
            int: Sum of the operands.

        Raises:
            ValueError: If inputs are not integers.
        """
        if not isinstance(left, int) or not isinstance(right, int):
            raise ValueError("inputs must be int")
        return left + right


@pytest.fixture()
def adder() -> Adder:
    """
    Provide an Adder instance for tests.
    """
    return Adder()


def test_add_happy_path(adder: Adder) -> None:
    """
    Verify add returns the expected sum.
    """
    assert adder.add(2, 3) == 5


def test_add_rejects_non_int(adder: Adder) -> None:
    """
    Verify add raises ValueError for invalid input.
    """
    with pytest.raises(ValueError):
        adder.add(2, "x")


def test_boundary_mock_example() -> None:
    """
    Demonstrate boundary mocking with a stubbed collaborator.
    """
    collaborator = mock.Mock()
    collaborator.compute.return_value = 10
    assert collaborator.compute(3) == 10
    collaborator.compute.assert_called_once_with(3)
