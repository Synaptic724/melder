"""
Component tests for the Rift gate (GitHub #274, step 3): removing a Rift closes its gate, newcomers are refused at
once, the threads already inside finish and leave, and only then is the Rift cleaned up.

- `Nexus.remove_rift` waits for an agent inside a `Workstation.call_target` target, inside a `FrameViewer` read and
  inside a room command, and the agent's call returns its value (item 1).
- A newcomer - a workstation call, a viewer read, a command, a Rift agent method - is refused at once while a removal
  waits for an agent inside and while it tears the Rift down (item 2).
- The drain is bounded by `projection_refresh_gate_timeout_seconds`: a removal that runs out of it raises, keeps the
  Rift registered with its gate closed, and a retry after the agent left succeeds (item 3, design 5a/5b).
- An agent that removes its own Rift from inside one of that Rift's calls is not waited for, and its call returns
  normally (item 4, design 5c).
- `Nexus.cleanup` drains every Rift under one deadline before its teardown and logs a timeout (item 5, design 5d).
- A thread already inside a Rift passes that Rift's gate while an ACL refresh or a removal drains it (item 6).
- An ACL refresh does not swap a frame's projections under an in-flight viewer read (item 7, #274 V1).

Order between threads comes from `threading.Event` handshakes set at fixed points - an agent step, a patched Rift
accessor or teardown, a patched gate close - never from sleeps. The one timed window, `_Handshake.OBSERVATION_SECONDS`,
gives a call that must wait the chance to return wrongly: a removal or cleanup that returns within it while an agent is
inside fails its test. Every thread is a daemon joined within `_Handshake.BOUND_SECONDS`, and every held agent is
released in a `finally`, so a broken run fails instead of hanging the suite.
"""
import functools
import logging
import threading
import time
from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Optional, Sequence, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.nexus import Nexus
from melder.nexus.rift.command_system.capability_command_system import CapabilityCommandSystem
from melder.nexus.rift.command_system.command_system import CommandSystem
from melder.nexus.rift.rift import Rift
from melder.nexus.rift.rift_gate.rift_gate import RiftGate
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration

if TYPE_CHECKING:
    from melder.nexus.rift.projection.frame_projection_set import FrameProjectionSet
    from melder.nexus.rift.projection.view_projection import ViewProjection


class _Pricing:
    """A spell that gives the `default` frame descriptor truth, so a Rift can attach it."""

    def __init__(self) -> None:
        """
        Build the spell's one value.

        Returns:
            None.
        """
        self.rate: int = 100


class _Handshake:
    """
    The bounds and gate timeouts every wait, join and timed check of this module uses.

    Contract:
        - Order between threads always comes from events set at the points a schedule names. `BOUND_SECONDS` only
          turns a broken run - a deadlock, or a point never reached - into a failure.
        - `OBSERVATION_SECONDS` is the window in which a removal or cleanup that must wait for an agent inside gets the
          chance to return wrongly. `PROMPT_SECONDS` is how long a refusal, a re-entry or a nested call may take.
        - The `*_TIMEOUT_SECONDS` values are installed as the Nexus `projection_refresh_gate_timeout_seconds`, the
          drain bound of a refresh, a removal and a cleanup: `DRAIN_TIMEOUT_SECONDS` where every agent is released
          well within it, `SHORT_DRAIN_TIMEOUT_SECONDS` and `CLEANUP_TIMEOUT_SECONDS` where an agent outstays it,
          `REFRESH_TIMEOUT_SECONDS` for the ACL refresh an agent's nested call must not park behind.
        - A drain that must wait for an agent that stays inside counts as having waited when it took at least
          `MIN_WAIT_FRACTION` of its timeout.
    """

    BOUND_SECONDS: float = 5.0
    OBSERVATION_SECONDS: float = 0.5
    PROMPT_SECONDS: float = 1.0
    SELF_REMOVAL_SECONDS: float = 2.0
    TIMEOUT_MARGIN_SECONDS: float = 1.0
    DRAIN_TIMEOUT_SECONDS: float = 5.0
    SHORT_DRAIN_TIMEOUT_SECONDS: float = 0.3
    CLEANUP_TIMEOUT_SECONDS: float = 0.4
    REFRESH_TIMEOUT_SECONDS: float = 2.0
    POLL_INTERVAL_SECONDS: float = 0.01
    MIN_WAIT_FRACTION: float = 0.8

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
    One call - an agent's, a removal's, a cleanup's or a newcomer's - run on its own daemon thread.

    Purpose:
        Run Rift work concurrently and still fail, not hang, when that work deadlocks or parks.

    Contract:
        - The thread is created at construction, so a patched step can recognise it before it starts, and is a daemon.
        - `returned` and `raised` keep what the call returned or raised. Only the agent's thread writes them; read them
          after a join that found the thread finished.
    """

    def __init__(self, name: str, call: Callable[[], object]) -> None:
        """
        Prepare the agent's thread without starting it.

        Args:
            name: The thread's name, used in failure messages.
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
        Start the agent's thread.

        Returns:
            None.
        """
        self.thread.start()

    def finished_within(self, seconds: float) -> bool:
        """
        Join the agent's thread for at most `seconds`.

        Args:
            seconds: How long to wait for the thread to finish.

        Returns:
            bool: True when the thread finished within `seconds`.
        """
        self.thread.join(timeout=seconds)
        return not self.thread.is_alive()

    def join_within_bound(self) -> bool:
        """
        Join the agent's thread within `_Handshake.BOUND_SECONDS`.

        Returns:
            bool: True when the thread finished within the bound.
        """
        return self.finished_within(_Handshake.BOUND_SECONDS)

    def run_and_join_within_bound(self) -> bool:
        """
        Start the agent and join it within the bound.

        Returns:
            bool: True when the agent finished within the bound.
        """
        self.start()
        return self.join_within_bound()

    def describe_outcome(self) -> str:
        """
        Describe what the call did, for failure messages.

        Returns:
            str: "was still running", "raised <error>" or "returned <value>".
        """
        if self.thread.is_alive():
            return "was still running"
        if self.raised is not None:
            return "raised {0!r}".format(self.raised)
        return "returned {0!r}".format(self.returned)

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
        Give the workstation and command paths agent code to run: calling the tool (`Workstation.call_target`) and its
        `run` method (`CommandSystem.execute_target_method("run")`) each run the step once, on the caller's thread.

    Contract:
        - Holds no lock and no Melder state of its own.
    """

    def __init__(self, label: str, step: Callable[[], object]) -> None:
        """
        Keep the label and the step.

        Args:
            label: A plain attribute naming the tool.
            step: The agent code each entry point runs.

        Returns:
            None.
        """
        self.label: str = label
        self._step: Callable[[], object] = step

    def __call__(self) -> object:
        """
        Run the step, as `Workstation.call_target` calls the active target.

        Returns:
            object: What the step returned.
        """
        return self._step()

    def run(self) -> object:
        """
        Run the step, as `CommandSystem.execute_target_method("run")` calls it.

        Returns:
            object: What the step returned.
        """
        return self._step()


class _Hold:
    """
    One point inside a Rift call where an agent stays until the test releases it.

    Contract:
        - `stay_inside` sets `inside`, then waits for `release` within the bound.
        - Every test sets `release` in a `finally`, so a held agent always gets out.
    """

    def __init__(self) -> None:
        """
        Prepare the two events, both unset.

        Returns:
            None.
        """
        self.inside: threading.Event = threading.Event()
        self.release: threading.Event = threading.Event()

    def stay_inside(self) -> None:
        """
        Announce the agent is inside and wait for the release.

        Returns:
            None.

        Raises:
            AssertionError: When the release does not come within the bound.
        """
        self.inside.set()
        _Handshake.wait(self.release, "The test releasing the agent held inside its call")

    def step_returning(self, value: str) -> Callable[[], object]:
        """
        Build agent code that stays inside until the release, then returns `value`.

        Args:
            value: What the step returns once released.

        Returns:
            Callable[[], object]: The step.
        """

        def step() -> object:
            """Stay inside until released, then return the value."""
            self.stay_inside()
            return value

        return step


class _Newcomer:
    """
    The agent doors a newcomer can knock on while a Rift is being removed.

    Contract:
        - `DOORS` names one door per kind the design gates: a direct Workstation call, a viewer read, a room command
          and two Rift agent methods.
        - `resolve_calls` binds every door to one Rift before anything removes it.
        - `knock` runs a door's call on its own daemon thread and joins it within `_Handshake.PROMPT_SECONDS`.
    """

    DOORS: Tuple[str, ...] = (
        "workstation.call_target",
        "viewer.list_frame_names",
        "command.list_supported_command_methods",
        "rift.get_frame_viewer",
        "rift.list_accessible_nexus_frame_names",
    )

    @staticmethod
    def resolve_calls(rift: Rift) -> Dict[str, Callable[[], object]]:
        """
        Bind every door of `DOORS` to `rift` and its room.

        Args:
            rift: The Rift whose doors the newcomer knocks on.

        Returns:
            Dict[str, Callable[[], object]]: Each door's call, keyed by door.
        """
        space = rift.space
        return {
            "workstation.call_target": space.workstation.call_target,
            "viewer.list_frame_names": space.frame_viewer.list_frame_names,
            "command.list_supported_command_methods": space.command_system.list_supported_command_methods,
            "rift.get_frame_viewer": rift.get_frame_viewer,
            "rift.list_accessible_nexus_frame_names": rift.list_accessible_nexus_frame_names,
        }

    @staticmethod
    def knock(door: str, call: Callable[[], object]) -> _Agent:
        """
        Run one newcomer's call on its own thread, waiting at most `_Handshake.PROMPT_SECONDS` for it.

        Args:
            door: The door's name, for the thread name.
            call: The door's call.

        Returns:
            _Agent: The newcomer, finished or still running.
        """
        newcomer = _Agent("newcomer at {0}".format(door), call)
        newcomer.start()
        newcomer.finished_within(_Handshake.PROMPT_SECONDS)
        return newcomer

    @staticmethod
    def refusal_failure(door: str, newcomer: _Agent) -> Optional[str]:
        """
        Describe how a newcomer was not refused at once with RuntimeError.

        Args:
            door: The door's name.
            newcomer: The newcomer `knock` returned.

        Returns:
            Optional[str]: None when the newcomer raised RuntimeError within the prompt bound; otherwise what it did.
        """
        if newcomer.thread.is_alive():
            return "{0} was still running after {1} s (admitted or parked, not refused at once)".format(
                door,
                _Handshake.PROMPT_SECONDS,
            )
        if isinstance(newcomer.raised, RuntimeError):
            return None
        return "{0} {1} instead of raising RuntimeError".format(door, newcomer.describe_outcome())


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


def _conjure_default_frame() -> None:
    """
    Conjure the dynamic, Rift-enabled `default` frame, whose one bound spell gives it descriptor truth.

    Returns:
        None.
    """
    configuration = SpellbookConfiguration(aether_frame="default")
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=True, rift_enabled=True)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(aetheric_frame="default", configuration=configuration)
    spellbook.bind(spell=_Pricing, existence=Existence.unique, permissions="create", spellframe="pricing")
    spellbook.conjure(name="pricing_root", dynamic=True)


def _create_linked_rift(nexus: Nexus, rift_name: str) -> Rift:
    """
    Create one capability Rift attached to `default`.

    Args:
        nexus: The enabled Nexus.
        rift_name: The Rift's name.

    Returns:
        Rift: The Rift.
    """
    rift = nexus.create_rift(
        configuration=nexus.create_rift_configuration().with_space_type(RiftSpaceType.capability),
        rift_name=rift_name,
    )
    rift.create_frame_link("default")
    return rift


def _build_world(*, drain_timeout_seconds: float, logger: Optional[logging.Logger] = None) -> Tuple[Nexus, Rift]:
    """
    Build an enabled Nexus whose gate drains are bounded by `drain_timeout_seconds`, and one capability Rift attached to
    a dynamic `default` frame.

    Args:
        drain_timeout_seconds: The Nexus `projection_refresh_gate_timeout_seconds`.
        logger: An explicit stdlib logger for Nexus, or None for the provider default.

    Returns:
        Tuple[Nexus, Rift]: The Nexus and the Rift.
    """
    _conjure_default_frame()
    nexus = Nexus(logger=logger)
    nexus_configuration = nexus.create_configuration()
    nexus_configuration.with_rift_creation_enabled(True)
    nexus_configuration.with_direct_rift_access(True)
    nexus_configuration.with_target_frame_override(True)
    nexus_configuration.with_multiple_target_frames(True)
    nexus_configuration.with_max_target_frame_count(8)
    nexus_configuration.with_allowed_target_frame_names(("default",))
    nexus_configuration.with_nexus_frame_mode("indexed")
    nexus_configuration.with_max_nexus_frame_count(8)
    nexus_configuration.with_projection_refresh_gate_timeout_seconds(drain_timeout_seconds)
    nexus_configuration.with_projection_refresh_gate_poll_interval_seconds(_Handshake.POLL_INTERVAL_SECONDS)
    nexus.activate(nexus_configuration)
    return nexus, _create_linked_rift(nexus, "pricing_rift")


def _copy_of_the_current_acl(nexus: Nexus, frame_name: str) -> FrameACLConfiguration:
    """
    Build a locked copy of a frame's current ACL bundle.

    Purpose:
        Registering the copy under a new contract name (`Nexus.register_named_frame_acl_configuration`) is a real frame
        ACL change: the frame's ACL container notifies Nexus, which refreshes the projections of every Rift with the
        frame attached through `Nexus._refresh_rift_projection_sets_for_frames`, while the selected rules stay as they
        were.

    Args:
        nexus: The enabled Nexus.
        frame_name: The frame whose ACL bundle is copied.

    Returns:
        FrameACLConfiguration: The locked copy.
    """
    current = nexus.get_current_frame_acl_configuration(frame_name)
    return FrameACLConfiguration.create_from_selected_configurations(
        frame_name=frame_name,
        view_configuration=current.view_configuration,
        command_configuration=current.command_configuration,
        codegen_configuration=current.codegen_configuration,
        reason="rift gate drain test: the same rules under a new contract name",
        locked=True,
    )


def _nested_call(nested_call: str, rift: Rift) -> Callable[[], object]:
    """
    Resolve the call an agent nests inside its command.

    Args:
        nested_call: "command" for `list_conduit_names(frame_name="default")`, "viewer_read" for
            `FrameViewer.list_frame_names()`.
        rift: The Rift whose room serves the call.

    Returns:
        Callable[[], object]: The nested call.
    """
    space = rift.space
    if nested_call == "command":
        command_system = space.command_system
        assert isinstance(command_system, CapabilityCommandSystem)
        return functools.partial(command_system.list_conduit_names, frame_name="default")
    return space.frame_viewer.list_frame_names


def _hold_the_first_view_projection_read(monkeypatch: pytest.MonkeyPatch, reader: _Agent, hold: _Hold) -> None:
    """
    Pause the reader's first view-projection read, holding the projection it got, until the test releases it.

    Contract:
        - Patches `Rift._get_required_view_projection`: on the reader's thread, once, it takes the projection, stays
          inside `hold`, then returns that projection - a viewer read paused mid-read, holding the projection. Every
          other call reads through.

    Args:
        monkeypatch: Patches `Rift._get_required_view_projection` for this test only.
        reader: The agent whose read is paused.
        hold: Where the read stays.

    Returns:
        None.
    """
    original_read = Rift._get_required_view_projection
    paused: List[bool] = []

    def read_then_stay_inside(self: Rift, frame_name: str) -> ViewProjection:
        """Take the projection; on the reader's first read, stay inside until released; return the projection."""
        projection = original_read(self, frame_name)
        if threading.current_thread() is reader.thread and not paused:
            paused.append(True)
            hold.stay_inside()
        return projection

    monkeypatch.setattr(Rift, "_get_required_view_projection", read_then_stay_inside)


def _remove_while_an_agent_is_inside(nexus: Nexus, rift_id: str, agent: _Agent, hold: _Hold, place: str) -> _Agent:
    """
    Remove the Rift while `agent` is held inside `place`, failing when the removal returns before the agent left.

    Contract:
        - Starts the agent, waits until it is inside, starts the removal and gives it `_Handshake.OBSERVATION_SECONDS`
          to return; it must not. The agent is released in every case, then the agent and the removal are joined
          within one bound.

    Args:
        nexus: The enabled Nexus.
        rift_id: The Rift to remove.
        agent: The agent, not started.
        hold: Where the agent stays inside its call.
        place: The call the agent is inside, for failure messages.

    Returns:
        _Agent: The remover, finished.
    """
    remover = _Agent("remover", lambda: nexus.remove_rift(rift_id))
    try:
        agent.start()
        _Handshake.wait(hold.inside, "The agent entering {0}".format(place))
        remover.start()
        removal_returned_while_inside = remover.finished_within(_Handshake.OBSERVATION_SECONDS)
        assert not removal_returned_while_inside, (
            "Nexus.remove_rift {0} within {1} s while an agent was inside {2}: the removal did not wait for the "
            "agent to leave before cleaning the Rift up.".format(
                remover.describe_outcome(),
                _Handshake.OBSERVATION_SECONDS,
                place,
            )
        )
    finally:
        hold.release.set()
    still_running = _Agent.still_running((agent, remover))
    assert still_running == [], "{0} still running after the agent was released.".format(still_running)
    agent.reraise_schedule_failure()
    return remover


def test_rift_removal_waits_for_an_agent_inside_call_target_and_the_call_returns_its_value() -> None:
    """
    `Nexus.remove_rift` does not return while an agent is inside a `Workstation.call_target` target; the call then
    returns its value and the Rift is gone.

    Symptom (GitHub #274, step 3): a direct workstation call takes no gate ticket and the removal never drains its
    gate, so the removal tore the room down under the running target.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    rift_id = rift.id
    workstation = rift.space.workstation
    hold = _Hold()
    workstation.bind_method("nightly_job", _AgentTool("nightly job", hold.step_returning("nightly prices")))
    workstation.set_target("nightly_job")
    agent = _Agent("agent", workstation.call_target)

    remover = _remove_while_an_agent_is_inside(nexus, rift_id, agent, hold, "Workstation.call_target")

    assert agent.raised is None, "The agent's call_target {0} after the removal waited.".format(
        agent.describe_outcome()
    )
    assert agent.returned == "nightly prices"
    assert remover.raised is None
    assert nexus.has_rift(rift_id) is False


def test_rift_removal_waits_for_an_agent_inside_a_viewer_read_and_the_read_returns_its_value(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    `Nexus.remove_rift` does not return while an agent's `FrameViewer` read is paused mid-read; the read then returns
    its value and the Rift is gone.

    Symptom (GitHub #274, step 3): a viewer read takes no gate ticket, so the removal cleaned the Rift and its
    projections under the read.

    Args:
        monkeypatch: Patches `Rift._get_required_view_projection` for this test only.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    rift_id = rift.id
    viewer = rift.space.frame_viewer
    expected_root_conduit_ids = viewer.list_root_conduit_ids(frame_name="default")
    hold = _Hold()
    reader = _Agent("reader", lambda: viewer.list_root_conduit_ids(frame_name="default"))
    _hold_the_first_view_projection_read(monkeypatch, reader, hold)

    remover = _remove_while_an_agent_is_inside(nexus, rift_id, reader, hold, "FrameViewer.list_root_conduit_ids")

    assert reader.raised is None, "The viewer read {0} after the removal waited.".format(reader.describe_outcome())
    assert reader.returned == expected_root_conduit_ids
    assert remover.raised is None
    assert nexus.has_rift(rift_id) is False


def test_rift_removal_waits_for_an_agent_inside_a_command_and_the_command_returns_its_value() -> None:
    """
    `Nexus.remove_rift` does not return while an agent is inside `CommandSystem.execute_target_method`; the command
    then returns its value and the Rift is gone.

    Symptom (GitHub #274, step 3): the command holds a gate ticket, but the removal never closes or drains the gate,
    so it cleaned the room - and the gate the command must release its ticket on - under the running method.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    rift_id = rift.id
    space = rift.space
    command_system = space.command_system
    hold = _Hold()
    space.workstation.bind_object("nightly_job", _AgentTool("nightly job", hold.step_returning("nightly prices")))
    space.workstation.set_target("nightly_job")
    agent = _Agent("agent", lambda: command_system.execute_target_method("run"))

    remover = _remove_while_an_agent_is_inside(nexus, rift_id, agent, hold, "CommandSystem.execute_target_method")

    assert agent.raised is None, "The agent's command {0} after the removal waited.".format(agent.describe_outcome())
    assert agent.returned == "nightly prices"
    assert remover.raised is None
    assert nexus.has_rift(rift_id) is False


@pytest.mark.parametrize("door", _Newcomer.DOORS)
def test_newcomers_are_refused_at_once_while_a_removal_waits_for_an_agent_inside(door: str) -> None:
    """
    While `Nexus.remove_rift` waits for an agent inside a `call_target` target, a newcomer at any agent door raises
    RuntimeError at once, and the removal is still waiting afterwards.

    Purpose:
        Pin that the removal closes the gate BEFORE it drains: a newcomer is refused during the wait, not parked until
        the agent leaves and not admitted into a Rift about to be cleaned.

    Symptom (GitHub #274, step 3): the removal neither waits nor closes the gate; it cleans the Rift at once, so there
    is no waiting removal for a newcomer to be refused by.

    Args:
        door: The agent door the newcomer knocks on.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    rift_id = rift.id
    workstation = rift.space.workstation
    hold = _Hold()
    workstation.bind_method("nightly_job", _AgentTool("nightly job", hold.step_returning("nightly prices")))
    workstation.set_target("nightly_job")
    newcomer_call = _Newcomer.resolve_calls(rift)[door]
    agent = _Agent("agent", workstation.call_target)
    remover = _Agent("remover", lambda: nexus.remove_rift(rift_id))
    try:
        agent.start()
        _Handshake.wait(hold.inside, "The agent entering Workstation.call_target")
        remover.start()
        removal_returned_while_inside = remover.finished_within(_Handshake.OBSERVATION_SECONDS)
        assert not removal_returned_while_inside, (
            "Nexus.remove_rift {0} within {1} s while an agent was inside Workstation.call_target: there was no "
            "waiting removal for the newcomer at {2} to be refused by.".format(
                remover.describe_outcome(),
                _Handshake.OBSERVATION_SECONDS,
                door,
            )
        )
        failure = _Newcomer.refusal_failure(door, _Newcomer.knock(door, newcomer_call))
        assert failure is None, "{0} while Nexus.remove_rift waited for an agent inside its Rift.".format(failure)
        assert remover.thread.is_alive(), (
            "Nexus.remove_rift {0} before the agent inside was released.".format(remover.describe_outcome())
        )
    finally:
        hold.release.set()
    still_running = _Agent.still_running((agent, remover))

    assert still_running == [], "{0} still running after the agent was released.".format(still_running)
    agent.reraise_schedule_failure()
    assert agent.returned == "nightly prices"
    assert remover.raised is None
    assert nexus.has_rift(rift_id) is False


@pytest.mark.parametrize("door", _Newcomer.DOORS)
def test_newcomers_are_refused_at_once_while_a_removal_tears_the_rift_down(
        monkeypatch: pytest.MonkeyPatch,
        door: str,
) -> None:
    """
    While `Nexus.remove_rift` is tearing a Rift down, a newcomer at any agent door raises RuntimeError at once.

    Purpose:
        The removal is held at the Rift's teardown (`Rift._clean_owned_state`, on the removal's thread) until the
        newcomer has knocked. By then the removal has closed the gate, so every door must refuse - not admit the
        newcomer into a Rift whose room is about to be cleaned.

    Symptom (GitHub #274, step 3): the removal never closes the gate, and a direct workstation call and a command
    still reach a room that is being cleaned; the viewer read and the Rift methods are refused only because the Rift
    is already marked cleaned.

    Args:
        monkeypatch: Patches `Rift._clean_owned_state` for this test only.
        door: The agent door the newcomer knocks on.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    rift_id = rift.id
    workstation = rift.space.workstation
    workstation.bind_method("quick_job", _AgentTool("quick job", lambda: "quick prices"))
    workstation.set_target("quick_job")
    newcomer_call = _Newcomer.resolve_calls(rift)[door]
    teardown_reached = threading.Event()
    knocked = threading.Event()
    remover = _Agent("remover", lambda: nexus.remove_rift(rift_id))
    original_teardown = Rift._clean_owned_state

    def hold_the_teardown_until_the_newcomer_knocked(self: Rift) -> None:
        """On the removal's thread, hold the Rift's teardown until the newcomer has knocked; then tear down."""
        if threading.current_thread() is remover.thread:
            teardown_reached.set()
            _Handshake.wait(knocked, "The newcomer knocking at {0}".format(door))
        original_teardown(self)

    monkeypatch.setattr(Rift, "_clean_owned_state", hold_the_teardown_until_the_newcomer_knocked)
    failures: List[Optional[str]] = []
    try:
        remover.start()
        _Handshake.wait(teardown_reached, "The removal reaching the Rift's teardown")
        failures.append(_Newcomer.refusal_failure(door, _Newcomer.knock(door, newcomer_call)))
    finally:
        knocked.set()
    removal_finished = remover.join_within_bound()

    assert failures == [None], "{0} while Nexus.remove_rift was tearing the Rift down.".format(failures[0])
    assert removal_finished, "Nexus.remove_rift did not finish within {0} s.".format(_Handshake.BOUND_SECONDS)
    remover.reraise_schedule_failure()
    assert remover.raised is None
    assert nexus.has_rift(rift_id) is False


def test_rift_removal_times_out_on_an_agent_that_stays_inside_and_keeps_the_rift_with_its_gate_closed() -> None:
    """
    A removal whose drain outlasts `projection_refresh_gate_timeout_seconds` raises RuntimeError after about that
    timeout, keeps the Rift registered with its gate closed to newcomers, and a retry after the agent left succeeds.

    Purpose:
        Pin the bound and the refusal of the design (5a/5b): the drain waits up to the configured timeout, polling at
        the configured interval; on timeout the removal is refused rather than tearing down with an agent inside, and
        the gate it closed stays closed.

    Symptom (GitHub #274, step 3): the removal never waits, so it does not time out: it removes the Rift with the
    agent still inside.

    Returns:
        None.
    """
    timeout_seconds = _Handshake.SHORT_DRAIN_TIMEOUT_SECONDS
    nexus, rift = _build_world(drain_timeout_seconds=timeout_seconds)
    rift_id = rift.id
    workstation = rift.space.workstation
    hold = _Hold()
    workstation.bind_method("nightly_job", _AgentTool("nightly job", hold.step_returning("nightly prices")))
    workstation.set_target("nightly_job")
    newcomer_calls = _Newcomer.resolve_calls(rift)
    agent = _Agent("agent", workstation.call_target)
    removal_seconds: List[float] = []

    def remove_and_time() -> None:
        """Remove the Rift, keeping how long the call took whether it returned or raised."""
        started = time.monotonic()
        try:
            nexus.remove_rift(rift_id)
        finally:
            removal_seconds.append(time.monotonic() - started)

    remover = _Agent("remover", remove_and_time)
    newcomer_failures: List[str] = []
    try:
        agent.start()
        _Handshake.wait(hold.inside, "The agent entering Workstation.call_target")
        removal_finished = remover.run_and_join_within_bound()
        assert removal_finished, "Nexus.remove_rift did not finish within {0} s.".format(_Handshake.BOUND_SECONDS)
        assert isinstance(remover.raised, RuntimeError), (
            "Nexus.remove_rift {0} while an agent stayed inside Workstation.call_target past "
            "projection_refresh_gate_timeout_seconds={1}: it must raise RuntimeError and keep the Rift.".format(
                remover.describe_outcome(),
                timeout_seconds,
            )
        )
        assert removal_seconds[0] >= timeout_seconds * _Handshake.MIN_WAIT_FRACTION, (
            "Nexus.remove_rift gave up after {0:.3f} s, before its {1} s drain timeout.".format(
                removal_seconds[0],
                timeout_seconds,
            )
        )
        assert removal_seconds[0] < timeout_seconds + _Handshake.TIMEOUT_MARGIN_SECONDS, (
            "Nexus.remove_rift took {0:.3f} s against a {1} s drain timeout.".format(
                removal_seconds[0],
                timeout_seconds,
            )
        )
        assert nexus.has_rift(rift_id) is True, "The timed-out removal did not keep the Rift registered."
        for door in _Newcomer.DOORS:
            failure = _Newcomer.refusal_failure(door, _Newcomer.knock(door, newcomer_calls[door]))
            if failure is not None:
                newcomer_failures.append(failure)
    finally:
        hold.release.set()
    agent_finished = agent.join_within_bound()

    assert newcomer_failures == [], (
        "The gate of the Rift whose removal timed out did not stay closed: {0}.".format("; ".join(newcomer_failures))
    )
    assert agent_finished, "The agent did not finish within {0} s of its release.".format(_Handshake.BOUND_SECONDS)
    agent.reraise_schedule_failure()
    assert agent.raised is None
    assert agent.returned == "nightly prices"
    retry = _Agent("retry", lambda: nexus.remove_rift(rift_id))
    assert retry.run_and_join_within_bound(), "The retried removal did not finish within the bound."
    assert retry.raised is None, "The retried removal {0} after the agent left.".format(retry.describe_outcome())
    assert nexus.has_rift(rift_id) is False


def test_an_agent_removing_its_own_rift_from_inside_call_target_is_not_waited_for() -> None:
    """
    An agent inside a `call_target` target of Rift R removes R: the removal returns promptly, well inside a large drain
    timeout, R is gone, and the outer `call_target` returns normally.

    Purpose:
        Pin self-removal (design 5c) for the workstation door: the removal must not count the calling thread's own
        ticket, which would wait out the whole timeout and then refuse.

    Before step 3 a workstation call took no ticket, so this passed then; it guards the door now that it takes one.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    rift_id = rift.id
    workstation = rift.space.workstation

    def remove_my_own_rift() -> object:
        """Remove the Rift this call runs in and return how long the removal took."""
        started = time.monotonic()
        nexus.remove_rift(rift_id)
        return time.monotonic() - started

    workstation.bind_method("retire_job", _AgentTool("retire job", remove_my_own_rift))
    workstation.set_target("retire_job")
    agent = _Agent("agent", workstation.call_target)

    assert agent.run_and_join_within_bound(), "call_target did not finish within {0} s.".format(
        _Handshake.BOUND_SECONDS
    )
    assert agent.raised is None, "call_target {0} after its target removed its own Rift.".format(
        agent.describe_outcome()
    )
    assert isinstance(agent.returned, float)
    assert agent.returned < _Handshake.SELF_REMOVAL_SECONDS, (
        "Removing its own Rift from inside call_target took {0:.2f} s against a {1} s drain timeout: the removal "
        "waited for the caller's own ticket.".format(agent.returned, _Handshake.DRAIN_TIMEOUT_SECONDS)
    )
    assert nexus.has_rift(rift_id) is False


def test_an_agent_removing_its_own_rift_from_inside_a_command_is_not_waited_for_and_the_command_returns() -> None:
    """
    An agent inside `CommandSystem.execute_target_method` on Rift R removes R: the removal returns promptly, R is gone,
    and the outer command returns its value with no exception.

    Purpose:
        Pin self-removal (design 5c) for the command door: the removal does not wait for the caller's own ticket, and
        the command's exit - its ticket release, its room memory, its post-hooks - is skipped quietly on the cleaned
        room.

    Symptom (GitHub #274, step 3): the command's exit ran on the room the removal had just cleaned and raised.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    rift_id = rift.id
    space = rift.space
    command_system = space.command_system

    def remove_my_own_rift() -> object:
        """Remove the Rift this command runs in and return how long the removal took."""
        started = time.monotonic()
        nexus.remove_rift(rift_id)
        return time.monotonic() - started

    space.workstation.bind_object("retire_job", _AgentTool("retire job", remove_my_own_rift))
    space.workstation.set_target("retire_job")
    agent = _Agent("agent", lambda: command_system.execute_target_method("run"))

    assert agent.run_and_join_within_bound(), "execute_target_method did not finish within {0} s.".format(
        _Handshake.BOUND_SECONDS
    )
    assert agent.raised is None, "execute_target_method {0} after its method removed its own Rift.".format(
        agent.describe_outcome()
    )
    assert isinstance(agent.returned, float)
    assert agent.returned < _Handshake.SELF_REMOVAL_SECONDS, (
        "Removing its own Rift from inside a command took {0:.2f} s against a {1} s drain timeout: the removal "
        "waited for the caller's own ticket.".format(agent.returned, _Handshake.DRAIN_TIMEOUT_SECONDS)
    )
    assert nexus.has_rift(rift_id) is False


def test_nexus_cleanup_waits_for_an_agent_inside_before_tearing_the_rift_down() -> None:
    """
    `Nexus.cleanup` does not finish while an agent is inside a `call_target` target; once released, the agent's call
    returns its value and the cleanup completes.

    Symptom (GitHub #274, step 3): `Nexus.cleanup` cleaned every Rift at once, with the agent still inside.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    workstation = rift.space.workstation
    hold = _Hold()
    workstation.bind_method("nightly_job", _AgentTool("nightly job", hold.step_returning("nightly prices")))
    workstation.set_target("nightly_job")
    agent = _Agent("agent", workstation.call_target)
    cleaner = _Agent("cleaner", nexus.cleanup)
    try:
        agent.start()
        _Handshake.wait(hold.inside, "The agent entering Workstation.call_target")
        cleaner.start()
        cleanup_finished_while_inside = cleaner.finished_within(_Handshake.OBSERVATION_SECONDS)
        assert not cleanup_finished_while_inside, (
            "Nexus.cleanup {0} within {1} s while an agent was inside Workstation.call_target: it tore the Rift "
            "down without waiting for the agent to leave.".format(
                cleaner.describe_outcome(),
                _Handshake.OBSERVATION_SECONDS,
            )
        )
    finally:
        hold.release.set()
    still_running = _Agent.still_running((agent, cleaner))

    assert still_running == [], "{0} still running after the agent was released.".format(still_running)
    agent.reraise_schedule_failure()
    assert agent.raised is None
    assert agent.returned == "nightly prices"
    assert cleaner.raised is None
    assert nexus.cleaned is True


def test_nexus_cleanup_gives_up_on_agents_that_stay_inside_after_one_shared_timeout_and_logs_it(
        caplog: pytest.LogCaptureFixture,
) -> None:
    """
    With an agent inside each of three Rifts that never leaves, `Nexus.cleanup` still completes - after about one
    `projection_refresh_gate_timeout_seconds`, not one per Rift - and logs the timeout.

    Purpose:
        Pin design 5d's bound: one deadline across all Rifts, then the teardown proceeds anyway and the timeout is
        logged at WARNING or above on the Nexus logger. The message wording is not pinned.

    Symptom (GitHub #274, step 3): `Nexus.cleanup` does not wait for the agents at all, so it neither waits nor logs.

    Args:
        caplog: Captures the Nexus logger's records.

    Returns:
        None.
    """
    logger_name = "melder.tests.rift_gate_drains_before_teardown"
    timeout_seconds = _Handshake.CLEANUP_TIMEOUT_SECONDS
    nexus, first_rift = _build_world(drain_timeout_seconds=timeout_seconds, logger=logging.getLogger(logger_name))
    rifts = (first_rift, _create_linked_rift(nexus, "ledger_rift"), _create_linked_rift(nexus, "audit_rift"))
    holds: List[_Hold] = []
    agents: List[_Agent] = []
    for rift in rifts:
        hold = _Hold()
        workstation = rift.space.workstation
        workstation.bind_method("nightly_job", _AgentTool("nightly job", hold.step_returning("nightly prices")))
        workstation.set_target("nightly_job")
        holds.append(hold)
        agents.append(_Agent("agent in {0}".format(rift.rift_name), workstation.call_target))
    cleanup_seconds: List[float] = []

    def clean_and_time() -> None:
        """Clean Nexus up, keeping how long the call took whether it returned or raised."""
        started = time.monotonic()
        try:
            nexus.cleanup()
        finally:
            cleanup_seconds.append(time.monotonic() - started)

    cleaner = _Agent("cleaner", clean_and_time)
    cleanup_finished = False
    try:
        for agent, hold in zip(agents, holds):
            agent.start()
            _Handshake.wait(hold.inside, "{0} entering Workstation.call_target".format(agent.thread.name))
        with caplog.at_level(logging.DEBUG, logger=logger_name):
            cleanup_finished = cleaner.run_and_join_within_bound()
    finally:
        for hold in holds:
            hold.release.set()
    agents_still_running = _Agent.still_running(agents)

    assert cleanup_finished, "Nexus.cleanup did not finish within {0} s.".format(_Handshake.BOUND_SECONDS)
    assert cleaner.raised is None, "Nexus.cleanup {0}.".format(cleaner.describe_outcome())
    assert nexus.cleaned is True
    assert cleanup_seconds[0] >= timeout_seconds * _Handshake.MIN_WAIT_FRACTION, (
        "Nexus.cleanup returned after {0:.3f} s with an agent inside each of three Rifts: it did not wait for them "
        "(projection_refresh_gate_timeout_seconds={1}).".format(cleanup_seconds[0], timeout_seconds)
    )
    assert cleanup_seconds[0] < timeout_seconds * 2, (
        "Nexus.cleanup took {0:.3f} s against a {1} s timeout: it waited once per Rift, not under one deadline across "
        "all Rifts.".format(cleanup_seconds[0], timeout_seconds)
    )
    nexus_records = [record for record in caplog.records if record.name == logger_name]
    assert any(record.levelno >= logging.WARNING for record in nexus_records), (
        "Nexus.cleanup logged nothing at WARNING or above about its drain timeout; it logged {0}.".format(
            [(record.levelname, record.getMessage()) for record in nexus_records]
        )
    )
    assert agents_still_running == [], "{0} still running after their release.".format(agents_still_running)


@pytest.mark.parametrize("nested_call", ["command", "viewer_read"])
def test_an_agent_inside_a_command_passes_its_own_gate_while_an_acl_refresh_drains_it(
        monkeypatch: pytest.MonkeyPatch,
        nested_call: str,
) -> None:
    """
    A thread inside a Rift command passes that Rift's gate at once - for a nested command or a nested viewer read -
    while an ACL refresh has disabled the gate and drains it; the refresh completes after the thread leaves.

    Purpose:
        Pin re-entry (item 6) against the reversible close: the refresh disables the gate (`RiftGate.close`, patched to
        announce it) and waits for the agent's ticket, so the agent must be let through to finish and leave. The
        frame ACL change is real: a copy of the current rules registered under a new contract name.

    Symptom (GitHub #274, step 3): the nested command parked in `admit_ticket` behind the disabled gate until the
    refresh - waiting for this same thread - timed out after `projection_refresh_gate_timeout_seconds`, and the
    refresh raised. Before step 3 the nested viewer read took no ticket, so that case passed and now guards the door.

    Args:
        monkeypatch: Patches `RiftGate.close` and `Rift.refresh_runtime_projections` for this test only.
        nested_call: What the agent does inside its command once the gate is disabled.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.REFRESH_TIMEOUT_SECONDS)
    space = rift.space
    command_system = space.command_system
    nested = _nested_call(nested_call, rift)
    expected_nested = nested()
    acl_copy = _copy_of_the_current_acl(nexus, "default")
    inside = threading.Event()
    gate_disabled = threading.Event()
    nested_done = threading.Event()
    nested_outcomes: List[Tuple[str, object, float]] = []

    def nest_a_call_once_the_gate_is_disabled() -> object:
        """Inside the command: wait until the refresh disabled the gate, then make the nested call and time it."""
        inside.set()
        _Handshake.wait(gate_disabled, "The ACL refresh disabling the agent's gate")
        started = time.monotonic()
        try:
            nested_outcomes.append(("returned", nested(), time.monotonic() - started))
        except Exception as error:
            nested_outcomes.append(("raised", error, time.monotonic() - started))
        nested_done.set()
        return "nightly prices"

    space.workstation.bind_object("nightly_job", _AgentTool("nightly job", nest_a_call_once_the_gate_is_disabled))
    space.workstation.set_target("nightly_job")
    agent = _Agent("agent", lambda: command_system.execute_target_method("run"))
    refresher = _Agent(
        "refresher",
        lambda: nexus.register_named_frame_acl_configuration("default", acl_copy, contract_name="gate_drain_probe"),
    )
    original_close = RiftGate.close
    original_refresh = Rift.refresh_runtime_projections
    refreshes: List[bool] = []

    def close_then_announce(self: RiftGate) -> None:
        """Disable the gate; on the refresher's thread, announce it."""
        original_close(self)
        if threading.current_thread() is refresher.thread:
            gate_disabled.set()

    def record_then_refresh(
            self: Rift,
            *,
            frame_names: Optional[Sequence[str]] = None,
    ) -> Dict[str, FrameProjectionSet]:
        """On the refresher's thread, record whether the agent's nested call was done; then refresh."""
        if threading.current_thread() is refresher.thread:
            refreshes.append(nested_done.is_set())
        return original_refresh(self, frame_names=frame_names)

    monkeypatch.setattr(RiftGate, "close", close_then_announce)
    monkeypatch.setattr(Rift, "refresh_runtime_projections", record_then_refresh)

    agent.start()
    _Handshake.wait(inside, "The agent entering its command")
    refresher.start()
    still_running = _Agent.still_running((agent, refresher))

    assert still_running == [], "{0} still running: the nested call and the ACL refresh froze.".format(still_running)
    agent.reraise_schedule_failure()
    assert len(nested_outcomes) == 1
    outcome, value, nested_seconds = nested_outcomes[0]
    assert outcome == "returned" and value == expected_nested, (
        "The agent's nested {0} {1} {2!r} while an ACL refresh drained its gate.".format(nested_call, outcome, value)
    )
    assert nested_seconds < _Handshake.PROMPT_SECONDS, (
        "The agent's nested {0} took {1:.2f} s while an ACL refresh drained its gate: it parked behind the refresh "
        "that was waiting for this same thread.".format(nested_call, nested_seconds)
    )
    assert agent.raised is None, "The agent's command {0}.".format(agent.describe_outcome())
    assert agent.returned == "nightly prices"
    assert refresher.raised is None, "The ACL refresh {0}: it did not complete after the agent left.".format(
        refresher.describe_outcome()
    )
    assert refreshes == [True], "The ACL refresh swapped projections before the agent's nested call was done."


@pytest.mark.parametrize("nested_call", ["command", "viewer_read"])
def test_an_agent_inside_a_command_passes_its_own_gate_while_a_removal_closes_it(nested_call: str) -> None:
    """
    A thread inside a Rift command passes that Rift's gate - for a nested command or a nested viewer read - while a
    removal has closed the gate and waits for it; then the command returns and the removal completes.

    Purpose:
        Pin re-entry (item 6) against the terminal close: the removal must let the thread it is waiting for finish its
        work and leave, not refuse it.

    Symptom (GitHub #274, step 3): the removal did not wait; it cleaned the room under the command, so the nested
    call was refused as cleaned and the command's own exit failed.

    Args:
        nested_call: What the agent does inside its command once the removal is under way.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    rift_id = rift.id
    space = rift.space
    command_system = space.command_system
    nested = _nested_call(nested_call, rift)
    expected_nested = nested()
    inside = threading.Event()
    go_nested = threading.Event()
    nested_outcomes: List[Tuple[str, object]] = []

    def nest_a_call_once_the_removal_is_under_way() -> object:
        """Inside the command: wait for the test's go-ahead, then make the nested call."""
        inside.set()
        _Handshake.wait(go_nested, "The test letting the agent make its nested call")
        try:
            nested_outcomes.append(("returned", nested()))
        except Exception as error:
            nested_outcomes.append(("raised", error))
        return "nightly prices"

    space.workstation.bind_object("nightly_job", _AgentTool("nightly job", nest_a_call_once_the_removal_is_under_way))
    space.workstation.set_target("nightly_job")
    agent = _Agent("agent", lambda: command_system.execute_target_method("run"))
    remover = _Agent("remover", lambda: nexus.remove_rift(rift_id))
    try:
        agent.start()
        _Handshake.wait(inside, "The agent entering its command")
        remover.start()
        # Give the removal its time to close the gate; whether it returned is item 1's concern, not asserted here.
        remover.finished_within(_Handshake.OBSERVATION_SECONDS)
    finally:
        go_nested.set()
    still_running = _Agent.still_running((agent, remover))

    assert still_running == [], "{0} still running: the nested call and the removal froze.".format(still_running)
    agent.reraise_schedule_failure()
    assert nested_outcomes == [("returned", expected_nested)], (
        "The agent's nested {0} gave {1!r} while a removal closed its gate: a thread already inside must pass "
        "it.".format(nested_call, nested_outcomes)
    )
    assert agent.raised is None, "The agent's command {0}.".format(agent.describe_outcome())
    assert agent.returned == "nightly prices"
    assert remover.raised is None
    assert nexus.has_rift(rift_id) is False


def test_an_acl_refresh_waits_for_an_in_flight_viewer_read_before_swapping_its_projection(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    An ACL change on a frame does not swap that frame's projections while a viewer read is paused mid-read holding the
    old projection; the read completes with its value and the refresh completes after it.

    Purpose:
        Pin item 7 (GitHub #274, V1). The read is paused right after it took its view projection; the frame ACL change
        is real: a copy of the current rules registered under a new contract name. The swap
        (`Rift.refresh_runtime_projections`, patched to record) must not run while the read is paused.

    Symptom (GitHub #274, V1): a viewer read takes no gate ticket, so the refresh's drain did not wait for it and
    the refresh cleaned the projection under the read, which then raised the cleaned RuntimeError.

    Args:
        monkeypatch: Patches `Rift._get_required_view_projection` and `Rift.refresh_runtime_projections` for this
            test only.

    Returns:
        None.
    """
    nexus, rift = _build_world(drain_timeout_seconds=_Handshake.DRAIN_TIMEOUT_SECONDS)
    viewer = rift.space.frame_viewer
    expected_root_conduit_ids = viewer.list_root_conduit_ids(frame_name="default")
    acl_copy = _copy_of_the_current_acl(nexus, "default")
    hold = _Hold()
    reader = _Agent("reader", lambda: viewer.list_root_conduit_ids(frame_name="default"))
    refresher = _Agent(
        "refresher",
        lambda: nexus.register_named_frame_acl_configuration("default", acl_copy, contract_name="gate_drain_probe"),
    )
    _hold_the_first_view_projection_read(monkeypatch, reader, hold)
    original_refresh = Rift.refresh_runtime_projections
    swapped = threading.Event()
    swaps_while_the_read_was_paused: List[bool] = []

    def record_then_refresh(
            self: Rift,
            *,
            frame_names: Optional[Sequence[str]] = None,
    ) -> Dict[str, FrameProjectionSet]:
        """On the refresher's thread, record whether the read was still paused; then swap the projections."""
        if threading.current_thread() is refresher.thread:
            swaps_while_the_read_was_paused.append(not hold.release.is_set())
            swapped.set()
        return original_refresh(self, frame_names=frame_names)

    monkeypatch.setattr(Rift, "refresh_runtime_projections", record_then_refresh)
    try:
        reader.start()
        _Handshake.wait(hold.inside, "The viewer read taking its view projection")
        refresher.start()
        # Give a refresh that does not wait for the read its chance to swap under it.
        swapped.wait(timeout=_Handshake.OBSERVATION_SECONDS)
    finally:
        hold.release.set()
    still_running = _Agent.still_running((reader, refresher))

    assert still_running == [], "{0} still running: the viewer read and the ACL refresh froze.".format(still_running)
    reader.reraise_schedule_failure()
    assert swaps_while_the_read_was_paused == [False], (
        "The ACL refresh swapped the frame's projections while a viewer read was paused holding the old projection "
        "(GitHub #274, V1): the refresh did not wait for the in-flight read."
    )
    assert reader.raised is None, "The viewer read {0}.".format(reader.describe_outcome())
    assert reader.returned == expected_root_conduit_ids
    assert refresher.raised is None, "The ACL refresh {0}.".format(refresher.describe_outcome())
