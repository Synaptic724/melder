import logging
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.spellbook.configuration.configuration import Configuration
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
from melder.utilities.logger.safe_logger import SafeLogger


class _LockProbe:
    """
    Minimal lock probe used to verify Conduit context management.

    Contract:
        - acquire() increments acquire_calls and returns True.
        - release() increments release_calls.
    """

    def __init__(self) -> None:
        """
        Initialize the probe with zeroed counters.

        Returns:
            None: This constructor has no return value.
        """
        self.acquire_calls = 0
        self.release_calls = 0

    def acquire(self) -> bool:
        """
        Record a lock acquire and return True.

        Returns:
            bool: Always True to emulate a successful acquire.
        """
        self.acquire_calls += 1
        return True

    def release(self) -> None:
        """
        Record a lock release.

        Returns:
            None: This method only updates internal counters.
        """
        self.release_calls += 1

    def __enter__(self) -> "_LockProbe":
        """
        Enter the probe as a context manager.

        Contract:
            - Calls acquire() once and returns self.

        Returns:
            _LockProbe: The lock probe instance.
        """
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the probe as a context manager.

        Contract:
            - Calls release() once.
            - Does not suppress exceptions.

        Args:
            exc_type: Exception type, if any.
            exc_value: Exception value, if any.
            traceback: Traceback object, if any.

        Returns:
            None: Always returns None to avoid suppressing exceptions.
        """
        self.release()


def test_init_rejects_non_configuration(spellbook_stub: MagicMock) -> None:
    """
    Verify Conduit rejects non-IConfiguration inputs.

    Contract:
        - __init__ raises TypeError when configuration is not IConfiguration.

    Args:
        spellbook_stub (MagicMock): Spellbook stub used for construction.

    Raises:
        AssertionError: If the expected TypeError is not raised.
    """
    with pytest.raises(TypeError, match="IConfiguration"):
        Conduit(
            spellbook=spellbook_stub,
            configuration=object(),
            conduit_state=ConduitState.lesser,
            aetheric_frame="default",
            policy=Policies.default,
        )


def test_lesser_conduit_drops_name(
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify lesser conduits do not retain names assigned at construction.

    Contract:
        - A name passed to a lesser conduit is discarded.

    Args:
        configuration_automatic (Configuration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub used for construction.

    Raises:
        AssertionError: If the name is preserved for a lesser conduit.
    """
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
        name="alpha",
    )
    try:
        assert conduit.name is None
    finally:
        conduit.cleanup()


def test_name_setter_allows_initial_assignment(conduit_normal: Conduit) -> None:
    """
    Verify a normal conduit allows a one-time name assignment.

    Contract:
        - Setting name when unset succeeds.
        - The assigned name is visible via the property.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If the name is not stored after assignment.
    """
    conduit_normal.name = "primary"
    assert conduit_normal.name == "primary"


def test_name_setter_rejects_second_assignment(conduit_normal: Conduit) -> None:
    """
    Verify a conduit name cannot be reassigned.

    Contract:
        - Attempting to set name twice raises RuntimeError.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If the second assignment does not raise.
    """
    conduit_normal.name = "first"
    with pytest.raises(RuntimeError, match="name is set"):
        conduit_normal.name = "second"


def test_get_active_spellspace_returns_none_when_empty(conduit_lesser: Conduit) -> None:
    """
    Verify get_active_spellspace returns None with an empty stack.

    Contract:
        - No active SpellSpace is reported when none were entered.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If a non-None SpellSpace is returned.
    """
    assert conduit_lesser.get_active_spellspace() is None


def test_create_spellspace_returns_owned_space_without_activation(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify create_spellspace returns a SpellSpace owned by the conduit.

    Contract:
        - The returned SpellSpace is associated with the conduit.
        - Creating a SpellSpace does not make it active.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If ownership or activation expectations fail.
    """
    space = conduit_lesser.create_spellspace()
    assert isinstance(space, SpellSpace)
    assert space.owner_conduit is conduit_lesser
    assert conduit_lesser.get_active_spellspace() is None


def test_enter_spellspace_pushes_active_and_cleans_on_exit(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify enter_spellspace activates a SpellSpace and cleans it on exit.

    Contract:
        - The yielded SpellSpace is active during the context.
        - The SpellSpace is cleaned after leaving the context.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If activation or cleanup expectations fail.
    """
    with conduit_lesser.enter_spellspace() as space:
        assert conduit_lesser.get_active_spellspace() is space
        assert space.cleaned is False
    assert conduit_lesser.get_active_spellspace() is None
    assert space.cleaned is True


def test_enter_spellspace_nested_restores_previous_active(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify nested spellspaces restore the previous active space.

    Contract:
        - Inner contexts supersede the active spellspace.
        - Exiting inner context restores the prior active spellspace.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If the active spellspace does not restore correctly.
    """
    with conduit_lesser.enter_spellspace() as outer:
        assert conduit_lesser.get_active_spellspace() is outer
        with conduit_lesser.enter_spellspace() as inner:
            assert conduit_lesser.get_active_spellspace() is inner
        assert conduit_lesser.get_active_spellspace() is outer
        assert inner.cleaned is True
    assert conduit_lesser.get_active_spellspace() is None
    assert outer.cleaned is True


def test_enter_spellspace_cleans_on_exception(conduit_lesser: Conduit) -> None:
    """
    Verify spellspace cleanup occurs even when the body raises.

    Contract:
        - The spellspace is cleaned on exit even if an exception occurs.
        - The active stack is cleared after the context.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If cleanup does not occur after an exception.
    """
    with pytest.raises(ValueError, match="boom"):
        with conduit_lesser.enter_spellspace() as space:
            raise ValueError("boom")
    assert conduit_lesser.get_active_spellspace() is None
    assert space.cleaned is True


def test_enter_spellspace_raises_on_stack_corruption(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify exiting a corrupted spellspace stack raises SpellSpaceScopeError.

    Contract:
        - Stack integrity checks run on context exit.
        - Corruption triggers SpellSpaceScopeError.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If stack corruption does not raise.
    """
    with pytest.raises(SpellSpaceScopeError, match="stack corruption"):
        with conduit_lesser.enter_spellspace():
            conduit_lesser._spellspace_stack.set([])


def test_context_manager_acquires_and_releases_lock(conduit_lesser: Conduit) -> None:
    """
    Verify Conduit context manager acquires and releases the lock.

    Contract:
        - __enter__ acquires the lock.
        - __exit__ releases the lock.
        - The context returns the same Conduit instance.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If acquire/release behavior is incorrect.
    """
    lock = _LockProbe()
    conduit_lesser._lock = lock
    with conduit_lesser as ctx:
        assert ctx is conduit_lesser
    assert lock.acquire_calls == 1
    assert lock.release_calls == 1


def test_logger_factory_used_when_logger_missing(
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify a logger factory is used when no logger is provided.

    Contract:
        - Configuration factory is called with the conduit instance.
        - The resulting SafeLogger is assigned to the conduit.

    Args:
        configuration_automatic (Configuration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub used for construction.

    Raises:
        AssertionError: If factory usage or logger assignment fails.
    """
    seen = []

    def factory(obj: object) -> logging.Logger:
        """
        Produce a logger for the given object and record the call.

        Args:
            obj (object): The object requesting a logger.

        Returns:
            logging.Logger: A standard library logger instance.
        """
        seen.append(obj)
        return logging.getLogger("conduit-factory")

    configuration_automatic.set_logger_factory(factory)
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
    )
    try:
        assert seen == [conduit]
        assert isinstance(conduit._logger, SafeLogger)
    finally:
        conduit.cleanup()


def test_explicit_logger_skips_factory(
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify an explicit logger bypasses the configuration factory.

    Contract:
        - Logger factory is not called when logger is provided.
        - The conduit receives a SafeLogger wrapper.

    Args:
        configuration_automatic (Configuration): Automatic configuration.
        spellbook_stub (MagicMock): Spellbook stub used for construction.

    Raises:
        AssertionError: If the factory is used or logger is missing.
    """
    seen = []

    def factory(obj: object) -> logging.Logger:
        """
        Produce a logger for the given object and record the call.

        Args:
            obj (object): The object requesting a logger.

        Returns:
            logging.Logger: A standard library logger instance.
        """
        seen.append(obj)
        return logging.getLogger("unused-factory")

    configuration_automatic.set_logger_factory(factory)
    explicit_logger = logging.getLogger("explicit")
    conduit = Conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.lesser,
        aetheric_frame="default",
        policy=Policies.default,
        logger=explicit_logger,
    )
    try:
        assert seen == []
        assert isinstance(conduit._logger, SafeLogger)
    finally:
        conduit.cleanup()


def test_cleanup_is_idempotent_for_lesser_conduit(conduit_lesser: Conduit) -> None:
    """
    Verify cleanup is idempotent for a lesser conduit.

    Contract:
        - Multiple cleanup calls do not raise.
        - cleaned flag is set after cleanup completes.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    conduit_lesser._conduit_ward = MagicMock()
    conduit_lesser._meld = MagicMock()
    conduit_lesser._creations = MagicMock()
    conduit_lesser.cleanup()
    conduit_lesser.cleanup()
    assert conduit_lesser.cleaned is True


def test_cleanup_calls_spellbook_cleanup_for_normal_conduit(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify normal conduit cleanup invokes spellbook cleanup.

    Contract:
        - Normal conduit cleanup calls spellbook.cleanup().
        - Cleanup completes without raising when Aether is stubbed.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used during cleanup.

    Raises:
        AssertionError: If spellbook cleanup is not invoked.
    """
    conduit_normal._conduit_ward = MagicMock()
    conduit_normal._meld = MagicMock()
    conduit_normal._creations = MagicMock()
    spellbook = conduit_normal._spellbook
    conduit_normal.cleanup()
    assert spellbook.cleanup.called is True
