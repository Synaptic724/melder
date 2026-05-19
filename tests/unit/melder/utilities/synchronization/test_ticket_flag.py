import pytest

from melder.utilities.synchronization.ticket_flag import TicketFlag


def test_ticket_flag_defaults_falsey() -> None:
    """
    Purpose:
        Verify default initialization starts with zero tickets.
    """
    flag = TicketFlag()
    assert bool(flag) is False
    assert len(flag) == 0
    assert flag.value is False


def test_ticket_flag_init_truthy_starts_with_one_ticket() -> None:
    """
    Purpose:
        Verify truthy initialization creates one initial ticket.
    """
    flag = TicketFlag(True)
    assert bool(flag) is True
    assert len(flag) == 1
    assert flag.value is True


def test_value_set_true_appends_ticket() -> None:
    """
    Purpose:
        Verify setting value=True appends one ticket.
    """
    flag = TicketFlag()
    flag.value = True
    assert len(flag) == 1
    flag.value = True
    assert len(flag) == 2


def test_value_set_false_pops_one_ticket() -> None:
    """
    Purpose:
        Verify setting value=False removes one ticket.
    """
    flag = TicketFlag()
    flag.value = True
    flag.value = True
    flag.value = False
    assert len(flag) == 1
    assert bool(flag) is True


def test_value_set_false_empty_is_noop() -> None:
    """
    Purpose:
        Verify setting value=False on empty state is a no-op.
    """
    flag = TicketFlag()
    flag.value = False
    assert len(flag) == 0
    assert bool(flag) is False


def test_set_true_and_set_false_delegate_to_value_semantics() -> None:
    """
    Purpose:
        Verify explicit set_true/set_false methods follow ticket semantics.
    """
    flag = TicketFlag()
    flag.set_true()
    flag.set_true()
    assert len(flag) == 2
    flag.set_false()
    assert len(flag) == 1
    assert bool(flag) is True


def test_clear_tickets_forces_falsey_state() -> None:
    """
    Purpose:
        Verify clear_tickets removes all tickets.
    """
    flag = TicketFlag()
    flag.set_true()
    flag.set_true()
    flag.clear_tickets()
    assert len(flag) == 0
    assert bool(flag) is False


def test_has_tickets_and_active_ticket_count() -> None:
    """
    Purpose:
        Verify helper methods mirror bool and len views.
    """
    flag = TicketFlag()
    assert flag.has_tickets() is False
    assert flag.active_ticket_count() == 0
    flag.set_true()
    assert flag.has_tickets() is True
    assert flag.active_ticket_count() == 1


def test_context_manager_adds_and_removes_one_ticket() -> None:
    """
    Purpose:
        Verify context entry increments and exit decrements by one ticket.
    """
    flag = TicketFlag()
    with flag:
        assert len(flag) == 1
        assert bool(flag) is True
    assert len(flag) == 0
    assert bool(flag) is False


def test_context_manager_does_not_suppress_exceptions() -> None:
    """
    Purpose:
        Verify __exit__ returns False so exceptions propagate.
    """
    flag = TicketFlag()
    with pytest.raises(ValueError, match="boom"):
        with flag:
            raise ValueError("boom")
    assert len(flag) == 0


def test_cleanup_clears_and_nuls_ticket_storage() -> None:
    """
    Purpose:
        Verify cleanup clears tickets and nulls internal storage.
    """
    flag = TicketFlag()
    flag.set_true()
    flag.cleanup()
    assert flag._cleaned is True


def test_cleanup_is_idempotent() -> None:
    """
    Purpose:
        Verify repeated cleanup calls are safe.
    """
    flag = TicketFlag()
    flag.cleanup()
    flag.cleanup()
    assert flag._cleaned is True


@pytest.mark.parametrize(
    "operation",
    [
        lambda f: bool(f),
        lambda f: len(f),
        lambda f: f.value,
        lambda f: setattr(f, "value", True),
        lambda f: f.set_true(),
        lambda f: f.set_false(),
        lambda f: f.clear_tickets(),
        lambda f: f.has_tickets(),
        lambda f: f.active_ticket_count(),
        lambda f: f.__enter__(),
        lambda f: f.__exit__(None, None, None),
    ],
)
def test_methods_raise_after_cleanup(operation) -> None:
    """
    Purpose:
        Verify all guarded operations raise after cleanup.
    """
    flag = TicketFlag()
    flag.cleanup()
    with pytest.raises(RuntimeError, match="TicketFlag has already been cleaned"):
        operation(flag)
