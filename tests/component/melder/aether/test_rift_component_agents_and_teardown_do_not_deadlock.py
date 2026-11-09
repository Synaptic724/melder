"""
Component regressions for agent code and Rift teardown sharing one room (GitHub #274: W5, W4, W6, C3 and the R4
residual): several agents work in one Rift at once, and one may remove it while the others work.

- Agent code runs outside Melder's locks (W5): the target `Workstation.call_target` runs, the method
  `CommandSystem.execute_target_method` runs and the engine call of `CodegenCommandSystem.execute_codegen` can wait
  on another agent's command; `cleanup_target` keeps a selection made while the target's cleanup ran.
- `Nexus.remove_rift` finishes while an agent is mid-command (W4), while a weak workstation binding's collection
  callback publishes under the workstation lock (W6) and while `link_frame` refreshes (C3): the Rift and its room
  mark themselves cleaned under their own lock and clean their children after releasing it.
- An attach that lands inside `remove_rift` keeps no target-frame budget count (R4 residual).

Order between agents comes from nesting or from `threading.Event` handshakes set at fixed points - a lock stand-in's
first entry by a watched thread, a room action hook, a patched Nexus or engine step - never from sleeps. Every agent
thread is a daemon joined within `_Handshake.BOUND_SECONDS`, so a deadlock fails its test instead of hanging the
suite.
"""
import threading
import time
from types import TracebackType
from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Optional, Sequence, Tuple, Type

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.nexus import Nexus
from melder.nexus.rift.codegen_system.codegen_system import CodegenSystem
from melder.nexus.rift.command_system.capability_command_system import CapabilityCommandSystem
from melder.nexus.rift.command_system.codegen_command_system import CodegenCommandSystem
from melder.nexus.rift.command_system.command_system import CommandSystem
from melder.nexus.rift.rift import Rift
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration

if TYPE_CHECKING:
    from melder.nexus.rift.codegen_system.codegen_transaction_context import CodegenTransactionContext
    from melder.nexus.rift.codegen_system.execution.codegen_execution_result import CodegenExecutionResult
    from melder.nexus.rift.projection.frame_projection_set import FrameProjectionSet


class _Pricing:
    """A spell that gives the `default` frame descriptor truth, so a Rift can attach it."""

    def __init__(self) -> None:
        """
        Build the spell's one value.

        Returns:
            None.
        """
        self.rate: int = 100


class _Ledger:
    """
    A spell that gives the `ledger` frame descriptor truth.

    Contract:
        - A class other than `_Pricing`: a spell_id is the hash of the class's code, and a class bound in one
          conjured frame is refused in another.
    """

    def __init__(self) -> None:
        """
        Build the spell's one value.

        Returns:
            None.
        """
        self.entries: List[str] = []


class _Handshake:
    """
    The one bound every wait and join of this module uses.

    Contract:
        - Order between agents always comes from events set at the points a schedule names, or from nesting.
          `BOUND_SECONDS` only turns a broken run - a deadlock, or a point never reached - into a failure.
    """

    BOUND_SECONDS: float = 5.0

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


class _Agent:
    """
    One agent's call, run on its own daemon thread.

    Purpose:
        Stand in for another agent of the same Rift - or for the caller removing it - so a test can run agent work
        concurrently and still fail, not hang, when that work deadlocks.

    Contract:
        - The thread is created at construction, so a lock stand-in can watch it before it starts, and is a daemon.
        - `returned` and `raised` keep what the call returned or raised. Only the agent's thread writes them; read
          them after a join that found the thread finished.
    """

    def __init__(self, name: str, call: Callable[[], object]) -> None:
        """
        Prepare the agent's thread without starting it.

        Args:
            name: The thread's name, used in failure messages.
            call: The agent's work.

        Returns:
            None.
        """
        self._call: Callable[[], object] = call
        self.returned: object = None
        self.raised: Optional[BaseException] = None
        self.thread: threading.Thread = threading.Thread(target=self._run, name=name, daemon=True)

    def start(self) -> None:
        """
        Start the agent's thread.

        Returns:
            None.
        """
        self.thread.start()

    def join_within_bound(self) -> bool:
        """
        Join the agent's thread within `_Handshake.BOUND_SECONDS`.

        Returns:
            bool: True when the thread finished within the bound.
        """
        self.thread.join(timeout=_Handshake.BOUND_SECONDS)
        return not self.thread.is_alive()

    def run_and_join_within_bound(self) -> bool:
        """
        Start the agent and join it within the bound - what agent code does when it waits on another agent.

        Returns:
            bool: True when the agent finished within the bound.
        """
        self.start()
        return self.join_within_bound()

    def reraise_schedule_failure(self) -> None:
        """
        Re-raise a handshake failure the agent's call raised, so a broken schedule is reported as one.

        Returns:
            None.

        Raises:
            AssertionError: The `_Handshake.wait` failure the call raised, when it raised one.
        """
        if isinstance(self.raised, AssertionError):
            raise self.raised

    @staticmethod
    def still_running(agents: Sequence[_Agent]) -> List[str]:
        """
        Join every agent within one shared bound and name those still running.

        Args:
            agents: The agents to join, all started.

        Returns:
            List[str]: The thread names of the agents still running when the bound ran out.
        """
        deadline = time.monotonic() + _Handshake.BOUND_SECONDS
        for agent in agents:
            agent.thread.join(timeout=max(0.0, deadline - time.monotonic()))
        return [agent.thread.name for agent in agents if agent.thread.is_alive()]

    def _run(self) -> None:
        """
        Run the call on the agent's thread and keep its outcome.

        Returns:
            None.
        """
        try:
            self.returned = self._call()
        except BaseException as error:
            self.raised = error


class _AgentTool:
    """
    An object an agent keeps on its workstation, with one step of agent code behind it.

    Purpose:
        Give the workstation and command paths agent code to run: calling the tool (`Workstation.call_target`), its
        `run` method (`CommandSystem.execute_target_method`) and its `cleanup` method (`Workstation.cleanup_target`)
        each run the step once, on the caller's thread. `label` is a plain attribute another agent's
        `get_target_attribute` can read.

    Contract:
        - `step` is optional: a tool without one runs nothing and returns None.
        - Holds no lock; weakly referenceable (no `__slots__`), so it can also be a weak workstation binding.
    """

    def __init__(self, label: str, step: Optional[Callable[[], object]] = None) -> None:
        """
        Keep the label and the step.

        Args:
            label: The tool's plain attribute.
            step: The agent code each entry point runs, or None for a tool that runs nothing.

        Returns:
            None.
        """
        self.label: str = label
        self._step: Optional[Callable[[], object]] = step

    def __call__(self) -> object:
        """
        Run the step, as `Workstation.call_target` calls the active target.

        Returns:
            object: What the step returned.
        """
        return self._run_step()

    def run(self) -> object:
        """
        Run the step, as `CommandSystem.execute_target_method("run")` calls it.

        Returns:
            object: What the step returned.
        """
        return self._run_step()

    def cleanup(self) -> None:
        """
        Run the step, as `Workstation.cleanup_target` calls the target's cleanup.

        Returns:
            None.
        """
        self._run_step()

    def _run_step(self) -> object:
        """
        Run the step when the tool has one.

        Returns:
            object: What the step returned, or None for a tool without a step.
        """
        if self._step is None:
            return None
        return self._step()


class _HandshakeLock:
    """
    Stand-in for a Melder object's `_lock` that marks the moment one watched thread reaches it.

    Purpose:
        Melder code takes `self._lock` while holding whatever locks its callers took, so the watched thread's first
        entry is a fixed point of its schedule - the removal reaching the workstation or command-system lock while
        it tears the room down, or a binder's weak-collection callback reaching the room lock. The other agent waits
        for that point instead of for time.

    Contract:
        - Wraps one real `RLock`, the lock type the Melder objects use, so nested entries re-enter.
        - The watched thread's first entry sets `reached` and then, when `proceed` was given, waits for it within
          `_Handshake.BOUND_SECONDS`; only then does it acquire. Every other entry acquires plainly.
        - `reached` is set before the acquisition, so a watched thread that then blocks on the lock has already
          announced itself. A wait that runs out raises before the lock is taken, so it never leaves the lock held.
        - Supports `with` and explicit `acquire`/`release`, like the `RLock` it replaces.

    Threading:
        - Only the watched thread clears `_watched`. Another thread reading it sees the watched thread or None,
          never itself, and acquires plainly either way.
    """

    def __init__(
            self,
            watched: threading.Thread,
            reached: threading.Event,
            proceed: Optional[threading.Event] = None,
    ) -> None:
        """
        Prepare an unheld lock that watches one thread's first entry.

        Args:
            watched: The thread whose first entry is the schedule point.
            reached: Set when the watched thread first enters, before it acquires.
            proceed: When given, the watched thread's first entry waits for it before acquiring.

        Returns:
            None.
        """
        self._lock: threading.RLock = threading.RLock()
        self._watched: Optional[threading.Thread] = watched
        self._watched_name: str = watched.name
        self._reached: threading.Event = reached
        self._proceed: Optional[threading.Event] = proceed

    def __enter__(self) -> _HandshakeLock:
        """
        Announce the watched thread's first entry, then acquire.

        Returns:
            _HandshakeLock: This lock, as `with` binds it.
        """
        self.acquire()
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None:
        """
        Release the matching acquisition; never suppress the block's exception.

        Args:
            exc_type: The exception type raised in the block, or None.
            exc: The exception raised in the block, or None.
            tb: Its traceback, or None.

        Returns:
            None.
        """
        self._lock.release()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """
        Announce the watched thread's first entry, then acquire the real lock.

        Args:
            blocking: As for `RLock.acquire`.
            timeout: As for `RLock.acquire`.

        Returns:
            bool: Whether the real lock was acquired.

        Raises:
            AssertionError: When the watched thread's first entry waits for `proceed` longer than the bound.
        """
        self._announce_first_entry()
        return self._lock.acquire(blocking, timeout)

    def release(self) -> None:
        """
        Release one acquisition of the real lock.

        Returns:
            None.
        """
        self._lock.release()

    def _announce_first_entry(self) -> None:
        """
        On the watched thread's first entry, set `reached` and wait for `proceed` when one was given.

        Returns:
            None.

        Raises:
            AssertionError: When `proceed` is not set within the bound.
        """
        if threading.current_thread() is not self._watched:
            return
        self._watched = None
        self._reached.set()
        if self._proceed is not None:
            _Handshake.wait(self._proceed, "The go-ahead for {0} at the lock".format(self._watched_name))


def _reset_runtime_singletons() -> None:
    """
    Give every test a fresh Melder world.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    CommandSystem._aether = aether


@pytest.fixture(autouse=True)
def _isolated_runtime() -> Iterator[None]:
    """
    Reset the singletons around each test.

    Yields:
        None.
    """
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


def _conjure_frame(
        frame_name: str,
        spell: Type[object],
        spellframe: str,
        root_name: str,
        *,
        ai_native: bool,
) -> None:
    """
    Conjure one dynamic, Rift-enabled frame whose one bound spell gives it descriptor truth.

    Args:
        frame_name: The frame to conjure.
        spell: The spell class bound in it.
        spellframe: The spell's spellframe.
        root_name: The root conduit's name.
        ai_native: Whether the frame is AI-native, which a codegen room requires.

    Returns:
        None.
    """
    configuration = SpellbookConfiguration(aether_frame=frame_name)
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=True,
        rift_enabled=True,
        ai_native_enabled=ai_native,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(aetheric_frame=frame_name, configuration=configuration)
    spellbook.bind(spell=spell, existence=Existence.unique, permissions="create", spellframe=spellframe)
    spellbook.conjure(name=root_name, dynamic=True)


def _build_world(
        *,
        space_type: RiftSpaceType = RiftSpaceType.capability,
        ledger_frame: bool = False,
) -> Tuple[Nexus, Rift]:
    """
    Build an enabled Nexus and one Rift of the given room type, attached to a dynamic `default` frame.

    Args:
        space_type: The Rift's room type; a codegen room gets AI-native frames.
        ledger_frame: Whether to conjure a second frame, `ledger`, that the Nexus also allows but the Rift has not
            attached.

    Returns:
        Tuple[Nexus, Rift]: The Nexus and the Rift.
    """
    ai_native = space_type == RiftSpaceType.codegen
    _conjure_frame("default", _Pricing, "pricing", "pricing_root", ai_native=ai_native)
    allowed_frame_names: Tuple[str, ...] = ("default",)
    if ledger_frame:
        _conjure_frame("ledger", _Ledger, "ledger", "ledger_root", ai_native=ai_native)
        allowed_frame_names = ("default", "ledger")
    nexus = Nexus()
    nexus_configuration = nexus.create_configuration()
    nexus_configuration.with_rift_creation_enabled(True)
    nexus_configuration.with_direct_rift_access(True)
    nexus_configuration.with_target_frame_override(True)
    nexus_configuration.with_multiple_target_frames(True)
    nexus_configuration.with_max_target_frame_count(8)
    nexus_configuration.with_allowed_target_frame_names(allowed_frame_names)
    nexus_configuration.with_nexus_frame_mode("indexed")
    nexus_configuration.with_max_nexus_frame_count(8)
    nexus.activate(nexus_configuration)
    rift = nexus.create_rift(
        configuration=nexus.create_rift_configuration().with_space_type(space_type),
        rift_name="pricing_rift",
    )
    rift.create_frame_link("default")
    return nexus, rift


def test_call_target_runs_its_target_without_blocking_another_agents_target_read() -> None:
    """
    A target run by `call_target` can wait on another agent's `get_target_attribute` in the same room.

    Purpose:
        Pin the workstation half of W5: `Workstation.call_target` resolves its target under the workstation lock and
        runs it with none held, so agent code inside the target can wait on any other agent of the room.

    Symptom (GitHub #274, W5): `call_target` held the workstation lock for the whole target run, and another agent's
    `get_target_attribute` reads the active target under that lock, so it blocked until the target returned - and a
    target waiting on it never returned. Here the target starts the read on another thread and joins it within the
    bound.

    Returns:
        None.
    """
    _, rift = _build_world()
    space = rift.space
    workstation = space.workstation
    command_system = space.command_system
    reader = _Agent("reader", lambda: command_system.get_target_attribute("label"))
    workstation.bind_method(
        "nightly_job",
        _AgentTool(label="nightly pricing", step=reader.run_and_join_within_bound),
    )
    workstation.set_target("nightly_job")

    read_finished_inside_the_target = workstation.call_target()
    reader.join_within_bound()

    assert read_finished_inside_the_target is True, (
        "Another agent's get_target_attribute did not finish within {0} s while call_target ran its target: the "
        "target ran under the workstation lock (W5).".format(_Handshake.BOUND_SECONDS)
    )
    assert reader.raised is None
    assert reader.returned == "nightly pricing"


def test_execute_target_method_runs_its_method_without_blocking_another_agents_command() -> None:
    """
    A method run by `execute_target_method` can wait on another agent's command in the same room.

    Purpose:
        Pin the command half of W5: `execute_target_method` takes no command-system lock, so the method runs with no
        Melder lock held. The other agent runs `list_conduit_names`, which keeps the command lock, so only the
        executing side's release lets it through.

    Symptom (GitHub #274, W5): `execute_target_method` held the command lock while the method ran, so every other
    command of the room blocked behind agent code - and a method waiting on one never returned. Here the method
    starts the other command on another thread and joins it within the bound.

    Returns:
        None.
    """
    _, rift = _build_world()
    space = rift.space
    command_system = space.command_system
    assert isinstance(command_system, CapabilityCommandSystem)
    lister = _Agent("lister", lambda: command_system.list_conduit_names(frame_name="default"))
    space.workstation.bind_object(
        "nightly_job",
        _AgentTool(label="nightly pricing", step=lister.run_and_join_within_bound),
    )
    space.workstation.set_target("nightly_job")

    listing_finished_inside_the_method = command_system.execute_target_method("run")
    lister.join_within_bound()

    assert listing_finished_inside_the_method is True, (
        "Another agent's list_conduit_names did not finish within {0} s while execute_target_method ran its "
        "method: the method ran under the command lock (W5).".format(_Handshake.BOUND_SECONDS)
    )
    assert lister.raised is None
    assert lister.returned == ("pricing_root",)


def test_cleanup_target_keeps_the_target_selected_while_its_cleanup_ran() -> None:
    """
    A target selected while `cleanup_target` ran the old target's cleanup is still selected afterwards.

    Purpose:
        Pin the selection half of `cleanup_target`'s W5 change: it runs the cleanup methods with no workstation lock
        held, so another agent may select a target meanwhile, and it clears the selection only when it still names
        the binding it cleaned.

    Symptom (GitHub #274, W5): `cleanup_target` cleared the selection unconditionally after the cleanup methods, so
    a target selected during them was dropped. Here the cleanup itself selects the next target, on the same
    thread.

    Returns:
        None.
    """
    _, rift = _build_world()
    workstation = rift.space.workstation
    next_report = _AgentTool(label="next report")
    workstation.bind_object("next_report", next_report)
    workstation.bind_object(
        "spent_tool",
        _AgentTool(label="spent tool", step=lambda: workstation.set_target("next_report")),
    )
    workstation.set_target("spent_tool")

    workstation.cleanup_target()

    assert workstation.describe_bindings()["target_name"] == ["next_report"], (
        "cleanup_target cleared the target selected while the spent tool's cleanup ran."
    )
    assert workstation.get_target() is next_report


def test_execute_codegen_runs_the_engine_without_blocking_another_agents_command(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The codegen engine call of `execute_codegen` can wait on another agent's command in the same room.

    Purpose:
        Pin the codegen half of W5: `execute_codegen` reads the attached `CodegenSystem` under the command lock and
        calls `execute_codegen_request` after releasing it. The engine call is patched at the class to start
        another agent's `list_conduit_names` - which keeps the command lock - join it within the bound, then
        delegate.

    Symptom (GitHub #274, W5): `execute_codegen` held the command lock across the whole engine call, which runs
    agent code, so every other command of the room blocked behind it.

    Args:
        monkeypatch: Patches `CodegenSystem.execute_codegen_request` for this test only.

    Returns:
        None.
    """
    _, rift = _build_world(space_type=RiftSpaceType.codegen)
    command_system = rift.space.command_system
    assert isinstance(command_system, CodegenCommandSystem)
    lister = _Agent("lister", lambda: command_system.list_conduit_names(frame_name="default"))
    original_execute = CodegenSystem.execute_codegen_request
    listing_finished_inside_the_engine: List[bool] = []

    def let_another_agent_command_then_execute(
            self: CodegenSystem,
            code: str,
            *,
            frame_name: str,
    ) -> Tuple[CodegenTransactionContext, CodegenExecutionResult]:
        """Run another agent's command to completion (within the bound), then execute the request."""
        listing_finished_inside_the_engine.append(lister.run_and_join_within_bound())
        return original_execute(self, code, frame_name=frame_name)

    monkeypatch.setattr(CodegenSystem, "execute_codegen_request", let_another_agent_command_then_execute)

    payload = command_system.execute_codegen("result = 1", frame_name="default")
    lister.join_within_bound()

    assert listing_finished_inside_the_engine == [True], (
        "Another agent's list_conduit_names did not finish within {0} s while execute_codegen ran the engine: the "
        "engine ran under the command lock (W5).".format(_Handshake.BOUND_SECONDS)
    )
    assert lister.raised is None
    assert lister.returned == ("pricing_root",)
    assert payload == {"accepted": True, "frame_name": "default", "result": 1}


def test_rift_removal_and_an_agent_mid_call_target_running_a_command_both_finish() -> None:
    """
    `Nexus.remove_rift` and an agent whose `call_target` target is inside a room command both finish.

    Purpose:
        Pin W4. The agent is held inside the command's action-hook scope by a pre-hook until the removal reaches
        the workstation lock (announced by a lock stand-in) or finishes; then both must end within the bound. The
        removal must succeed; the agent may fail, since its room went away under it.

    Symptom (GitHub #274, W4): the agent held the workstation lock across its target (`call_target`) and needed the
    room lock to leave the command, while the removal held the room lock across `RiftSpace.cleanup` and needed the
    workstation lock to clean the workstation: a deadlock.

    Returns:
        None.
    """
    nexus, rift = _build_world()
    rift_id = rift.id
    space = rift.space
    workstation = space.workstation
    command_system = space.command_system
    inside_the_command = threading.Event()
    removal_progressed = threading.Event()

    def remove_the_rift() -> None:
        """Remove the Rift; announce the end too, so the agent is never left waiting on a removal that is over."""
        try:
            nexus.remove_rift(rift_id)
        finally:
            removal_progressed.set()

    def hold_the_command_until_the_removal_progressed() -> None:
        """Pre-hook: hold the agent inside the command until the removal reached the workstation lock."""
        inside_the_command.set()
        _Handshake.wait(removal_progressed, "The removal reaching the workstation lock")

    agent = _Agent("agent", workstation.call_target)
    remover = _Agent("remover", remove_the_rift)
    workstation._lock = _HandshakeLock(watched=remover.thread, reached=removal_progressed)
    space.register_action_pre_hook(
        "command",
        "list_supported_command_methods",
        hold_the_command_until_the_removal_progressed,
    )
    workstation.bind_method(
        "helper",
        _AgentTool(label="helper", step=command_system.list_supported_command_methods),
    )
    workstation.set_target("helper")

    agent.start()
    _Handshake.wait(inside_the_command, "The agent entering its room command")
    remover.start()
    still_running = _Agent.still_running((agent, remover))

    assert still_running == [], (
        "{0} still running after {1} s: Nexus.remove_rift and an agent mid-call_target deadlocked (W4).".format(
            still_running,
            _Handshake.BOUND_SECONDS,
        )
    )
    agent.reraise_schedule_failure()
    assert remover.raised is None


def test_rift_removal_and_a_weak_binding_collected_under_the_workstation_lock_both_finish() -> None:
    """
    `Nexus.remove_rift` and a rebind whose dropped object's weak alias publishes a room event both finish.

    Purpose:
        Pin W6. The binder rebinds a name whose old object is also weakly bound, so the old object dies under the
        workstation lock and its weak binding's collection callback publishes a room event. A stand-in room lock
        holds that publish at its entry until the removal reaches the workstation lock (or finishes); then both
        must end within the bound, and the removal and the rebind must succeed.

    Symptom (GitHub #274, W6): the callback needed the room lock while its thread held the workstation lock, and
    the removal held the room lock across `RiftSpace.cleanup` while it needed the workstation lock: a deadlock.

    Returns:
        None.
    """
    nexus, rift = _build_world()
    rift_id = rift.id
    space = rift.space
    workstation = space.workstation
    publish_reached_the_room_lock = threading.Event()
    removal_progressed = threading.Event()

    def rebind_a_name_whose_old_object_is_weakly_bound() -> None:
        """Bind a tool strongly and weakly, then rebind its strong name so it dies under the workstation lock."""
        tool = _AgentTool(label="old tool")
        workstation.bind_object("tool", tool, weak_ref=False)
        workstation.bind_object("tool_alias", tool, weak_ref=True)
        # The tools are created and dropped on this thread, so the old one is freed as the rebind drops it.
        del tool
        workstation.bind_object("tool", _AgentTool(label="new tool"), weak_ref=False)

    def remove_the_rift() -> None:
        """Remove the Rift; announce the end too, so the binder is never left waiting on a removal that is over."""
        try:
            nexus.remove_rift(rift_id)
        finally:
            removal_progressed.set()

    binder = _Agent("binder", rebind_a_name_whose_old_object_is_weakly_bound)
    remover = _Agent("remover", remove_the_rift)
    space._lock = _HandshakeLock(
        watched=binder.thread,
        reached=publish_reached_the_room_lock,
        proceed=removal_progressed,
    )
    workstation._lock = _HandshakeLock(watched=remover.thread, reached=removal_progressed)

    binder.start()
    _Handshake.wait(publish_reached_the_room_lock, "The weak binding's collection event reaching the room lock")
    remover.start()
    still_running = _Agent.still_running((binder, remover))

    assert still_running == [], (
        "{0} still running after {1} s: Nexus.remove_rift and a weak binding's collection event deadlocked "
        "(W6).".format(still_running, _Handshake.BOUND_SECONDS)
    )
    assert remover.raised is None
    assert binder.raised is None


def test_rift_removal_and_a_link_frame_refresh_both_finish(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    `Nexus.remove_rift` and a `command_system.link_frame` whose refresh is under way both finish.

    Purpose:
        Pin C3. A patched `Nexus.create_frame_projection_sets_for_rift` holds the link's refresh, with its sets
        built, until the removal reaches the command lock (announced by a lock stand-in) or finishes; then both must
        end within the bound. The removal must succeed; the link may fail, since its Rift went away under it.

    Symptom (GitHub #274, C3): `link_frame` held the command lock across the refresh, which needs the Rift lock to
    apply its sets, while the removal held the Rift lock across `Rift.cleanup` and needed the command lock to clean
    the command system: a deadlock.

    Args:
        monkeypatch: Patches `Nexus.create_frame_projection_sets_for_rift` for this test only.

    Returns:
        None.
    """
    nexus, rift = _build_world()
    rift_id = rift.id
    command_system = rift.space.command_system
    sets_built = threading.Event()
    removal_progressed = threading.Event()

    def remove_the_rift() -> None:
        """Remove the Rift; announce the end too, so the link is never left waiting on a removal that is over."""
        try:
            nexus.remove_rift(rift_id)
        finally:
            removal_progressed.set()

    linker = _Agent("linker", lambda: command_system.link_frame("default"))
    remover = _Agent("remover", remove_the_rift)
    original_build = Nexus.create_frame_projection_sets_for_rift

    def build_then_wait_for_the_removal(
            self: Nexus,
            *args: object,
            **kwargs: object,
    ) -> Dict[str, FrameProjectionSet]:
        """Build the link's sets, then hold its refresh until the removal reached the command lock."""
        projection_sets = original_build(self, *args, **kwargs)
        if threading.current_thread() is linker.thread:
            sets_built.set()
            _Handshake.wait(removal_progressed, "The removal reaching the command lock")
        return projection_sets

    monkeypatch.setattr(Nexus, "create_frame_projection_sets_for_rift", build_then_wait_for_the_removal)
    command_system._lock = _HandshakeLock(watched=remover.thread, reached=removal_progressed)

    linker.start()
    _Handshake.wait(sets_built, "The link's refresh building its projection sets")
    remover.start()
    still_running = _Agent.still_running((linker, remover))

    assert still_running == [], (
        "{0} still running after {1} s: Nexus.remove_rift and a link_frame refresh deadlocked (C3).".format(
            still_running,
            _Handshake.BOUND_SECONDS,
        )
    )
    linker.reraise_schedule_failure()
    assert remover.raised is None


def test_attach_landing_inside_rift_removal_leaves_no_budget_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    An attach whose publish lands inside `Nexus.remove_rift` keeps no target-frame budget count and raises the
    cleaned error.

    Purpose:
        Pin the R4 residual: `remove_rift` marks the Rift cleaned under the Rift lock in its registry phase and
        decrements the budget for exactly the frames attached then, so an attach that publishes later finds the Rift
        cleaned, gives its reservation back and raises. The attach of `ledger` runs on this thread and reserves its
        slot before the removal starts, so it is past the registry check that refuses a removed Rift. From inside
        that reservation the removal starts on another thread, and it is held at its teardown - after its registry
        phase - until the attach has finished, so the attach publishes in between. The teardown is
        `Rift._clean_owned_state` since the fix; before it, `remove_rift` called `Rift.cleanup` at that point, where
        this test held it when it failed first.

    Symptom (GitHub #274, R4 residual): the removal decremented the frames it listed in its registry phase, the
    attach published `ledger` after that list and before the Rift was cleaned, and the `ledger` count was never
    given back - the frame's budget slot leaked.

    Args:
        monkeypatch: Patches `Nexus._reserve_target_frame` and `Rift._clean_owned_state` for this test only.

    Returns:
        None.
    """
    nexus, rift = _build_world(ledger_frame=True)
    rift_id = rift.id
    removal_reached_cleanup = threading.Event()
    attach_finished = threading.Event()
    reservations: List[str] = []
    attach_errors: List[Exception] = []

    def remove_the_rift() -> None:
        """Remove the Rift; announce the end too, so the attach is never left waiting on a removal that is over."""
        try:
            nexus.remove_rift(rift_id)
        finally:
            removal_reached_cleanup.set()

    remover = _Agent("remover", remove_the_rift)
    original_reserve = Nexus._reserve_target_frame
    original_teardown = Rift._clean_owned_state

    def reserve_then_let_the_removal_run_its_registry_phase(self: Nexus, target_frame_name: str) -> None:
        """Reserve the slot; on the first reservation, start the removal and wait until it reached its teardown."""
        original_reserve(self, target_frame_name)
        if not reservations:
            reservations.append(target_frame_name)
            remover.start()
            _Handshake.wait(removal_reached_cleanup, "The removal finishing its registry phase")

    def hold_the_teardown_until_the_attach_finished(self: Rift) -> None:
        """On the removal's thread, hold the Rift's teardown until the attach has finished; then tear down."""
        if threading.current_thread() is remover.thread:
            removal_reached_cleanup.set()
            _Handshake.wait(attach_finished, "The attach finishing")
        original_teardown(self)

    monkeypatch.setattr(Nexus, "_reserve_target_frame", reserve_then_let_the_removal_run_its_registry_phase)
    monkeypatch.setattr(Rift, "_clean_owned_state", hold_the_teardown_until_the_attach_finished)

    try:
        rift.create_frame_link("ledger")
    except AssertionError:
        raise
    except Exception as error:
        attach_errors.append(error)
    finally:
        attach_finished.set()
    removal_finished = remover.join_within_bound()

    assert reservations == ["ledger"]
    assert removal_finished, "Nexus.remove_rift did not finish within {0} s.".format(_Handshake.BOUND_SECONDS)
    remover.reraise_schedule_failure()
    assert remover.raised is None
    assert "ledger" not in nexus._target_frame_ref_counts, (
        "The attach that published inside remove_rift kept a budget count: {0}.".format(
            nexus._target_frame_ref_counts
        )
    )
    assert "default" not in nexus._target_frame_ref_counts
    assert len(attach_errors) == 1 and isinstance(attach_errors[0], RuntimeError), (
        "The attach that landed inside remove_rift raised {0!r}, not the cleaned RuntimeError.".format(attach_errors)
    )
    assert "Rift has already been cleaned" in str(attach_errors[0])
