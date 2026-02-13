import pytest

from melder.utilities.synchronization.fast_switch import FastSwitch


def test_fast_switch_defaults_false() -> None:
    """
    Purpose:
        Verify default switch starts false with zero tickets.
    """
    switch = FastSwitch()
    assert bool(switch) is False
    assert len(switch) == 0


def test_fast_switch_truthy_init_adds_one_ticket() -> None:
    """
    Purpose:
        Verify truthy initialization starts with one ticket.
    """
    switch = FastSwitch(True)
    assert bool(switch) is True
    assert len(switch) == 1


def test_fast_switch_set_true_and_set_false() -> None:
    """
    Purpose:
        Verify direct mutation methods update ticket count.
    """
    switch = FastSwitch()
    switch.set_true()
    switch.set_true()
    assert len(switch) == 2
    switch.set_false()
    assert len(switch) == 1
    assert bool(switch) is True


def test_fast_switch_value_property_round_trip() -> None:
    """
    Purpose:
        Verify value property delegates to ticket mutations.
    """
    switch = FastSwitch()
    switch.value = True
    assert switch.value is True
    assert len(switch) == 1
    switch.value = False
    assert switch.value is False
    assert len(switch) == 0


def test_fast_switch_repeated_mutation_cycle_resets_to_false() -> None:
    """
    Purpose:
        Verify repeated set_true/set_false cycles return to falsey state.
    """
    switch = FastSwitch()
    switch.set_true()
    assert bool(switch) is True
    assert len(switch) == 1
    switch.set_false()
    assert bool(switch) is False
    assert len(switch) == 0


def test_fast_switch_set_false_underflow_raises_index_error() -> None:
    """
    Purpose:
        Verify non-defensive underflow behavior for empty pop.
    """
    switch = FastSwitch()
    with pytest.raises(IndexError):
        switch.set_false()


def test_fast_switch_cleanup_clears_and_breaks_primitive() -> None:
    """
    Purpose:
        Verify cleanup clears tickets and leaves primitive broken for reuse.
    """
    switch = FastSwitch(True)
    switch.cleanup()
    assert switch._cleaned is True
    assert switch._tickets is None
    with pytest.raises(TypeError):
        _ = len(switch)


def test_fast_switch_clear_tickets_forces_false() -> None:
    """
    Purpose:
        Verify clear_tickets resets state to falsey.
    """
    switch = FastSwitch(True)
    switch.set_true()
    switch.clear_tickets()
    assert len(switch) == 0
    assert bool(switch) is False
