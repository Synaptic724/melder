from __future__ import annotations

import logging

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_spellbook_logger_factory_upgrades_aether_logger() -> None:
    """
    Purpose:
        Validate a logger factory upgrades the Aether logger.
    Contract:
        - The logger factory is invoked for the Spellbook and Aether.
        - Aether's SafeLogger wraps a non-null underlying logger.
    Returns:
        None.
    Raises:
        AssertionError: If the Aether logger is not upgraded.
    """
    created_for: list[object] = []

    def logger_factory(obj: object) -> logging.Logger:
        """
        Purpose:
            Provide a stable stdlib logger for the requested object.
        Contract:
            - Records each object for verification.
            - Returns a stdlib logger instance.
        Args:
            obj: Object requesting a logger.
        Returns:
            logging.Logger: The logger instance.
        """
        created_for.append(obj)
        return logging.getLogger(f"spellbook-integration.{obj.__class__.__name__}")

    configuration = Configuration(aether_frame="log-frame")
    configuration.set_logger_factory(logger_factory)

    spellbook = Spellbook(aetheric_frame="log-frame", configuration=configuration)

    assert any(isinstance(obj, Aether) for obj in created_for)
    assert Spellbook._aether._logger is not None
    assert Spellbook._aether._logger._logger is not None
    assert spellbook._logger is not None
