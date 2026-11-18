"""
Unit tests for the RiftGate ticket model the Rift gate design needs (GitHub #274, step 3).

- A thread already inside passes the gate again at once while the gate is disabled (`close()`, an ACL refresh's
  reversible close) or terminally closed by another thread's `close_and_wait_until_free` (a removal), so it can
  finish and leave; a thread without a ticket is still refused.
- The gate counts threads, not calls.
- A drain run by a thread that holds a ticket does not wait for that thread's own ticket.
- Releasing a ticket after the gate was cleaned is a no-op.

Each re-entry runs on a daemon thread joined within `_Bound.PROMPT_SECONDS`, and a parked thread is released in a
`finally`, so a gate that parks or refuses a re-entering thread fails its test instead of hanging the suite. Every
successful `admit_ticket` is paired with one `unregister_ticket`, as `CommandSystem` pairs them.
"""
import threading
import time
from typing import Callable, List, Optional

from melder.nexus.rift.rift_gate.rift_gate import RiftGate


class _Bound:
    """
    The bounds every wait and join of this module uses.

    Contract:
        - Order between threads comes from events, or from a bounded wait on the gate's own public state;
          `BOUND_SECONDS` only turns a point never reached into a failure.
        - `PROMPT_SECONDS` is how long a re-entry or a refusal may take; `SELF_DRAIN_TIMEOUT_SECONDS` is the drain
          timeout a thread uses on its own gate, which must return within `SELF_DRAIN_PROMPT_SECONDS`.
    """

    BOUND_SECONDS: float = 5.0
    PROMPT_SECONDS: float = 1.0
    POLL_SECONDS: float = 0.001
    DRAIN_INTERVAL_SECONDS: float = 0.01
    SELF_DRAIN_TIMEOUT_SECONDS: float = 1.0
    SELF_DRAIN_PROMPT_SECONDS: float = 0.5

    @classmethod
    def wait(cls, event: threading.Event, point: str) -> None:
        """
        Wait until `event` is set, failing when it is not set within the bound.

        Args:
            event: The event that marks `point`.
            point: What the event marks, for the failure message.

        Returns:
            None.

        Raises:
            AssertionError: When the event is not set within `BOUND_SECONDS`.
        """
        if not event.wait(timeout=cls.BOUND_SECONDS):
            raise AssertionError("{0} did not happen within {1} s.".format(point, cls.BOUND_SECONDS))

    @classmethod
    def wait_until(cls, condition: Callable[[], bool], point: str) -> None:
        """
        Wait until `condition()` holds, re-checking it every `POLL_SECONDS`, failing after the bound.

        Args:
            condition: A read of the gate's public state.
            point: What the condition marks, for the failure message.

        Returns:
            None.

        Raises:
            AssertionError: When the condition does not hold within `BOUND_SECONDS`.
        """
        deadline = time.monotonic() + cls.BOUND_SECONDS
        pause = threading.Event()
        while not condition():
            if time.monotonic() >= deadline:
                raise AssertionError("{0} did not happen within {1} s.".format(point, cls.BOUND_SECONDS))
            pause.wait(cls.POLL_SECONDS)


class _Worker:
    """
    One call run on its own daemon thread, keeping what it returned or raised.

    Contract:
        - `returned` and `raised` are written only by the worker's thread; read them after a join that found the
          thread finished.
    """

    def __init__(self, name: str, call: Callable[[], object]) -> None:
        """
        Prepare the worker's thread without starting it.

        Args:
            name: The thread's name.
            call: The work the thread runs.

        Returns:
            None.
        """
        self._call: Callable[[], object] = call
        self.returned: object = None
        self.raised: Optional[BaseException] = None
        self.thread: threading.Thread = threading.Thread(target=self._run, name=name, daemon=True)

    def start(self) -> None:
        """
        Start the worker's thread.

        Returns:
            None.
        """
        self.thread.start()

    def finished_within(self, seconds: float) -> bool:
        """
        Join the worker's thread for at most `seconds`.

        Args:
            seconds: How long to wait for the thread to finish.

        Returns:
            bool: True when the thread finished within `seconds`.
        """
        self.thread.join(timeout=seconds)
        return not self.thread.is_alive()

    def _run(self) -> None:
        """
        Run the call and keep its outcome.

        Returns:
            None.
        """
        try:
            self.returned = self._call()
        except BaseException as error:
            self.raised = error


def test_a_thread_holding_a_ticket_is_admitted_again_at_once_while_the_gate_is_disabled() -> None:
    """
    A thread that holds a ticket passes `admit_ticket` again at once while the gate is disabled (`close()`).

    Purpose:
        An ACL refresh disables the gate and drains it; a thread already inside must be let through so it can finish
        its nested work and leave, or the drain waits on a thread that waits on the drain.

    Symptom (GitHub #274, step 3): `admit_ticket` parked every caller of a disabled gate, the ticket holder too, until
    the gate reopened.

    Returns:
        None.
    """
    gate = RiftGate()
    admitted = threading.Event()
    gate_disabled = threading.Event()
    readmissions: List[str] = []

    def hold_then_enter_again() -> None:
        """Take a ticket, wait until the gate is disabled, take it again, then release both."""
        gate.admit_ticket()
        admitted.set()
        _Bound.wait(gate_disabled, "The test disabling the gate")
        gate.admit_ticket()
        readmissions.append("admitted again")
        gate.unregister_ticket()
        gate.unregister_ticket()

    holder = _Worker("holder", hold_then_enter_again)
    holder.start()
    entered_again_at_once = False
    try:
        _Bound.wait(admitted, "The holder taking its ticket")
        gate.close()
        gate_disabled.set()
        entered_again_at_once = holder.finished_within(_Bound.PROMPT_SECONDS)
    finally:
        # Reopen so a holder parked in admit_ticket gets out.
        gate.open()
        holder.finished_within(_Bound.BOUND_SECONDS)

    assert entered_again_at_once, (
        "A thread holding a ticket did not pass admit_ticket within {0} s while the gate was disabled: it parked "
        "behind a close that waits for it to leave.".format(_Bound.PROMPT_SECONDS)
    )
    assert holder.raised is None
    assert readmissions == ["admitted again"]
    assert gate.active_ticket_count() == 0


def test_a_thread_holding_a_ticket_is_admitted_again_while_another_thread_closes_and_drains_the_gate() -> None:
    """
    A thread that holds a ticket passes `admit_ticket` again while another thread's `close_and_wait_until_free` has
    closed the gate terminally; a thread without a ticket is still refused; once the holder released everything, the
    closer returns.

    Purpose:
        A removal closes the gate for good and waits for the threads inside; they must be able to finish their nested
        work and leave, while newcomers are refused.

    Symptom (GitHub #274, step 3): `admit_ticket` raised "RiftGate is closed." for the ticket holder too.

    Returns:
        None.
    """
    gate = RiftGate()
    admitted = threading.Event()
    go_again = threading.Event()
    readmissions: List[str] = []

    def hold_then_enter_again() -> None:
        """Take a ticket, wait for the go-ahead, try to take it again, then release every ticket taken."""
        gate.admit_ticket()
        tickets_taken = 1
        admitted.set()
        _Bound.wait(go_again, "The test's go-ahead once the gate is closed")
        try:
            gate.admit_ticket()
            tickets_taken += 1
            readmissions.append("admitted again")
        except RuntimeError as error:
            readmissions.append("raised RuntimeError({0!r})".format(str(error)))
        for _ in range(tickets_taken):
            gate.unregister_ticket()

    holder = _Worker("holder", hold_then_enter_again)
    closer = _Worker(
        "closer",
        lambda: gate.close_and_wait_until_free(
            timeout=_Bound.BOUND_SECONDS,
            interval=_Bound.DRAIN_INTERVAL_SECONDS,
        ),
    )
    newcomers: List[_Worker] = []
    try:
        holder.start()
        _Bound.wait(admitted, "The holder taking its ticket")
        closer.start()
        _Bound.wait_until(gate.is_closed, "The closer closing the gate")
        newcomer = _Worker("newcomer", gate.admit_ticket)
        newcomers.append(newcomer)
        newcomer.start()
        newcomer.finished_within(_Bound.PROMPT_SECONDS)
    finally:
        go_again.set()
    holder_finished = holder.finished_within(_Bound.BOUND_SECONDS)
    closer_finished = closer.finished_within(_Bound.BOUND_SECONDS)

    assert not newcomers[0].thread.is_alive() and isinstance(newcomers[0].raised, RuntimeError), (
        "A thread without a ticket was not refused at once by the closed gate: it {0}.".format(
            "was still running" if newcomers[0].thread.is_alive() else "raised {0!r}".format(newcomers[0].raised)
        )
    )
    assert holder_finished
    assert holder.raised is None
    assert readmissions == ["admitted again"], (
        "A thread holding a ticket {0} while another thread's close_and_wait_until_free drained the gate: it must "
        "pass so it can finish and leave.".format(readmissions)
    )
    assert closer_finished, "close_and_wait_until_free did not return after the holder released its tickets."
    assert closer.raised is None
    assert gate.is_closed() is True
    assert gate.active_ticket_count() == 0


def test_the_gate_counts_a_thread_admitted_twice_as_one_ticket() -> None:
    """
    One thread admitted twice counts as one active ticket; the paired releases bring the count back to zero.

    Purpose:
        The gate counts threads inside, not calls in flight, so a nested call does not look like a second thread to a
        drain.

    Symptom (GitHub #274, step 3): every `admit_ticket` appended a ticket, so one thread admitted twice counted 2.

    Returns:
        None.
    """
    gate = RiftGate()
    gate.admit_ticket()
    gate.admit_ticket()
    try:
        count_while_inside = gate.active_ticket_count()
    finally:
        gate.unregister_ticket()
        gate.unregister_ticket()

    assert count_while_inside == 1, (
        "One thread admitted twice counted {0} active tickets: the gate counted calls, not threads.".format(
            count_while_inside
        )
    )
    assert gate.active_ticket_count() == 0


def test_a_thread_holding_a_ticket_closes_and_drains_the_gate_without_waiting_for_itself() -> None:
    """
    A thread holding a ticket calls `close_and_wait_until_free`: it returns promptly, not counting its own ticket, and
    the gate is closed.

    Purpose:
        An agent that removes its own Rift from inside one of that Rift's calls drains a gate it is inside; waiting for
        its own ticket would wait out the whole timeout and then refuse.

    Symptom (GitHub #274, step 3): the drain counted the caller's own ticket and raised the timeout RuntimeError.

    Returns:
        None.
    """
    gate = RiftGate()
    gate.admit_ticket()
    drain_errors: List[RuntimeError] = []
    started = time.monotonic()
    try:
        gate.close_and_wait_until_free(
            timeout=_Bound.SELF_DRAIN_TIMEOUT_SECONDS,
            interval=_Bound.DRAIN_INTERVAL_SECONDS,
        )
    except RuntimeError as error:
        drain_errors.append(error)
    drain_seconds = time.monotonic() - started
    gate.unregister_ticket()

    assert drain_errors == [], (
        "close_and_wait_until_free raised {0!r} after {1:.2f} s on a thread holding a ticket: it waited for the "
        "closing thread's own ticket.".format(drain_errors, drain_seconds)
    )
    assert drain_seconds < _Bound.SELF_DRAIN_PROMPT_SECONDS
    assert gate.is_closed() is True
    assert gate.active_ticket_count() == 0


def test_releasing_a_ticket_after_the_gate_was_cleaned_is_a_no_op() -> None:
    """
    A ticket released after the gate was cleaned raises nothing.

    Purpose:
        A thread that was inside when its Rift was torn down - its own removal, or a cleanup that gave up waiting -
        still releases its ticket on the way out; that release must be quiet.

    Symptom (GitHub #274, step 3): `unregister_ticket` raised the cleaned RuntimeError.

    Returns:
        None.
    """
    gate = RiftGate()
    gate.admit_ticket()
    gate.cleanup()
    release_errors: List[RuntimeError] = []
    try:
        gate.unregister_ticket()
    except RuntimeError as error:
        release_errors.append(error)

    assert release_errors == [], "Releasing a ticket after cleanup raised {0!r}.".format(release_errors)
    assert gate.cleaned is True
