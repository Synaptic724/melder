from unittest.mock import MagicMock

from melder.aether.conduit.conduit import Conduit


def test_get_resolution_state_returns_state_for_normal(
    conduit_normal: Conduit,
) -> None:
    """
    Purpose:
        Validate resolution state lookup for a normal conduit.
    Contract:
        - Returns the state registered under the conduit id.
        - Does not mutate state or run validation.
    Args:
        conduit_normal: Normal conduit fixture.
    Returns:
        None.
    Raises:
        AssertionError: If lookup does not return the expected state.
    """
    resolution_state = object()
    spell_system_states = MagicMock()
    spell_system_states.get_conduit_resolution_state.return_value = resolution_state
    conduit_normal._spellbook._spell_system_states = spell_system_states

    result = conduit_normal.get_resolution_state()

    assert result is resolution_state
    spell_system_states.get_conduit_resolution_state.assert_called_once_with(conduit_normal._id)


def test_get_resolution_state_uses_root_for_lesser(
    conduit_dynamic_lesser: Conduit,
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Purpose:
        Validate lesser conduits resolve state via the root conduit id.
    Contract:
        - Uses the root conduit id for lookup.
    Args:
        conduit_dynamic_lesser: Lesser conduit fixture.
        conduit_dynamic_normal: Root conduit fixture.
    Returns:
        None.
    Raises:
        AssertionError: If lookup does not use the root conduit id.
    """
    conduit_dynamic_lesser._conduit_ward._root_conduit = conduit_dynamic_normal
    resolution_state = object()
    spell_system_states = MagicMock()
    spell_system_states.get_conduit_resolution_state.return_value = resolution_state
    conduit_dynamic_lesser._spellbook._spell_system_states = spell_system_states

    result = conduit_dynamic_lesser.get_resolution_state()

    assert result is resolution_state
    spell_system_states.get_conduit_resolution_state.assert_called_once_with(
        conduit_dynamic_normal._id
    )


def test_validate_resolution_runs_phases_for_normal(
    conduit_normal: Conduit,
) -> None:
    """
    Purpose:
        Ensure validate_resolution runs structural and resolution phases.
    Contract:
        - Calls structural phases when refresh_structural is True.
        - Runs resolution phases for the conduit id.
        - Returns the resulting resolution state.
    Args:
        conduit_normal: Normal conduit fixture.
    Returns:
        None.
    Raises:
        AssertionError: If phase calls or return values are incorrect.
    """
    resolution_state = object()
    spell_system_states = MagicMock()
    spell_system_states.get_conduit_resolution_state.return_value = resolution_state
    spellbook = conduit_normal._spellbook
    spellbook._spell_system_states = spell_system_states
    spellbook._run_structural_phases = MagicMock()
    spellbook._run_resolution_phases_for_conduit = MagicMock()

    result = conduit_normal.validate_resolution()

    assert result is resolution_state
    spellbook._run_structural_phases.assert_called_once_with()
    spellbook._run_resolution_phases_for_conduit.assert_called_once_with(conduit_normal._id)
    spell_system_states.get_conduit_resolution_state.assert_called_once_with(conduit_normal._id)


def test_validate_resolution_skips_structural_when_disabled(
    conduit_normal: Conduit,
) -> None:
    """
    Purpose:
        Confirm validate_resolution can skip structural phases.
    Contract:
        - Does not call structural phases when refresh_structural is False.
    Args:
        conduit_normal: Normal conduit fixture.
    Returns:
        None.
    Raises:
        AssertionError: If structural phases are executed.
    """
    resolution_state = object()
    spell_system_states = MagicMock()
    spell_system_states.get_conduit_resolution_state.return_value = resolution_state
    spellbook = conduit_normal._spellbook
    spellbook._spell_system_states = spell_system_states
    spellbook._run_structural_phases = MagicMock()
    spellbook._run_resolution_phases_for_conduit = MagicMock()

    result = conduit_normal.validate_resolution(refresh_structural=False)

    assert result is resolution_state
    spellbook._run_structural_phases.assert_not_called()
    spellbook._run_resolution_phases_for_conduit.assert_called_once_with(conduit_normal._id)


def test_validate_resolution_uses_root_for_lesser(
    conduit_dynamic_lesser: Conduit,
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Purpose:
        Ensure validate_resolution uses the root conduit id for lesser conduits.
    Contract:
        - Runs resolution phases against the root conduit id.
    Args:
        conduit_dynamic_lesser: Lesser conduit fixture.
        conduit_dynamic_normal: Root conduit fixture.
    Returns:
        None.
    Raises:
        AssertionError: If root conduit id is not used.
    """
    conduit_dynamic_lesser._conduit_ward._root_conduit = conduit_dynamic_normal
    resolution_state = object()
    spell_system_states = MagicMock()
    spell_system_states.get_conduit_resolution_state.return_value = resolution_state
    spellbook = conduit_dynamic_lesser._spellbook
    spellbook._spell_system_states = spell_system_states
    spellbook._run_structural_phases = MagicMock()
    spellbook._run_resolution_phases_for_conduit = MagicMock()

    result = conduit_dynamic_lesser.validate_resolution(refresh_structural=False)

    assert result is resolution_state
    spellbook._run_structural_phases.assert_not_called()
    spellbook._run_resolution_phases_for_conduit.assert_called_once_with(
        conduit_dynamic_normal._id
    )
