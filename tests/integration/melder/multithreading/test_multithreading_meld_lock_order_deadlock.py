"""
Deadlock regression tests for meld's store-lock / Spell-lock ordering.

WHAT IS BEING CLAIMED
---------------------
Concurrent melds (and a meld racing a purge) on one conduit tree must always finish.

THE DEFECT THESE TESTS PIN (fixed 2026-09-25)
---------------------------------------------
Until melder 0.2.52 several ordinary shapes deadlocked:

    - A `unique_per_conduit`, lineage, cluster or SpellSpace-scoped meld door held
      its creations-store lock for the WHOLE build, including dependency steps.
    - A `unique` build takes that spell's Spell lock first, and then a store lock:
      to check/publish itself in its owner store, or to register a disposal-bearing
      `many` dependency into the caller's store.
    - On a normal root the per-conduit store, the lineage store (also for every
      lesser of that root) and every owned unique's store are ONE object.

So one thread held a store and waited for a Spell lock while another held that
Spell lock and waited for the store. Reproduced on melder 0.2.3 and 0.2.52, GIL and
free-threaded 3.14.

The fix gives build-once exclusion its own lock per slot (`Creations.slot_guard`;
`Spell._lock` for `unique`) and makes the store lock a leaf that is only held for
dict reads and writes. Evidence and design: STORY-2026-09-25-verify-override-writer-
and-contract, TASK-2026-09-25-implement-creation-slot-build-guards.

WHY A CHILD PROCESS
-------------------
A real deadlock cannot be undone inside the process that has it: the stuck threads
keep both locks forever and any later cleanup of that world would hang too. Each
scenario therefore runs in its own interpreter. The child joins its threads against
one shared deadline, prints one JSON verdict and leaves through `os._exit`, so stuck
daemon threads and exit-time cleanup can never hang it. The parent adds a hard
`subprocess.run(timeout=...)` backstop on top.

HOW THE INTERLEAVING IS FORCED
------------------------------
Public behaviour only; no Melder lock is patched. Thread A always starts the
consumer meld and parks inside a user constructor (the `DeadlockLeaf` built as the
first plan step, or `NestedMeldConsumer` itself) while its door holds the store.
The competitor then runs until it provably holds the Spell lock:

    - competitor `meld`: thread C melds the unique service; its own `DeadlockLeaf`
      constructor runs inside the service build (Spell lock held) and releases A.
    - competitor `purge`: thread P purges the not-yet-built service; the coordinator
      releases A once P has either finished or is observed (via its stack) inside
      `Creations._detach_purge_entries`, i.e. holding the Spell lock and waiting on
      the store. That frame name is the one private detail this file depends on.
    - competitor `nested`: like `meld`, but thread A's consumer has NO dependency on
      the service; its constructor melds the service itself (service-locator style).

If a gate is never reached the child reports `precondition_not_reached` and the test
FAILS outright with a different message than a deadlock, so a broken harness and a
reintroduced deadlock are never confused.

EXPECTATIONS
------------
Every case must complete. `FORMERLY_DEADLOCKING_CASES` are the shapes that hung
before the fix (plus `unique -> many -> unique_per_conduit`, which the fix design had
to cover); a `MeldDeadlockDetected` there means the store lock is once again held
across a build. `SAFE_CASES` were safe before the fix and prove the harness can
report success. Do NOT loosen the assertions or the timeouts to make a case green.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from threading import Event, Thread, current_thread
from typing import Dict, List, Optional

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.spellbook.spellbook import Spellbook

pytestmark = pytest.mark.integration


class MeldDeadlockDetected(AssertionError):
    """
    Raised by the parent test when the child reports that its threads deadlocked.

    Purpose:
        Name the one failure that means "the lock-order deadlock is back", distinct
        from every other failure (a missed gate, a crash, a whole-child timeout).
    """


class ScenarioGate:
    """
    Hold the events and borrowed door that order the threads inside one child process.

    Contract:
        - `a_parked` is set by thread A from inside its gating constructor, while
          A's consumer door holds its store.
        - `release_a` lets thread A leave that constructor; it is set by the
          competitor (meld/nested) or by the coordinator (purge).
        - `competitor_inside` is set by thread C from inside the service build.
        - `nested_door` is the door `NestedMeldConsumer` melds the service through.
        - Owned by `MeldDeadlockScenario.run_child`; borrowed by the fixture classes
          through class attributes for one child run only.
    """

    def __init__(self, gate_timeout_seconds: float, nested_door: Optional[object]) -> None:
        """
        Create the unset events.

        Args:
            gate_timeout_seconds: How long thread A waits to be released before its
                gating constructor raises `TimeoutError`.
            nested_door: Conduit or SpellSpace used by `NestedMeldConsumer`, if any.
        """
        self.a_parked: Event = Event()
        self.release_a: Event = Event()
        self.competitor_inside: Event = Event()
        self.gate_timeout_seconds: float = gate_timeout_seconds
        self.nested_door: Optional[object] = nested_door

    def park_thread_a(self) -> None:
        """
        Signal that thread A is inside its gating constructor and wait for release.

        Raises:
            TimeoutError: If nothing releases thread A within the gate timeout.
        """
        self.a_parked.set()
        if not self.release_a.wait(self.gate_timeout_seconds):
            raise TimeoutError("thread A was never released")


class DeadlockLeaf:
    """
    Transient (`many`) dependency of the service; its constructor is the usual gate.

    Contract:
        - With no gate installed (warm-up, parent process) it does nothing.
        - In thread `meld-A` it parks thread A while A's door holds the store.
        - In thread `meld-C` it records that C is inside the service build (holding
          the service's Spell lock) and releases thread A.
    """

    gate: Optional[ScenarioGate] = None

    def __init__(self) -> None:
        """Apply the scenario gate for the current thread, if a gate is installed."""
        gate = DeadlockLeaf.gate
        if gate is None:
            return
        thread_name = current_thread().name
        if thread_name == "meld-A":
            gate.park_thread_a()
        elif thread_name == "meld-C":
            gate.competitor_inside.set()
            gate.release_a.set()

    def close(self) -> None:
        """Disposal method used by the scenarios that declare one."""


class ChainTool:
    """`unique_per_conduit` dependency of `ChainLeaf`: a slotted step inside a unique's plan."""


class ChainLeaf(DeadlockLeaf):
    """
    `many` gate leaf that itself depends on a `unique_per_conduit` tool.

    Contract:
        - Gates exactly like `DeadlockLeaf` (same class-level gate).
        - Makes a `unique` build's plan reach a slotted step on the caller's store
          BEFORE the gate: unique -> many -> unique_per_conduit.
    """

    def __init__(self, tool: ChainTool) -> None:
        """
        Borrow the tool, then apply the inherited gate.

        Args:
            tool: The per-conduit dependency built earlier in the same plan.
        """
        self.tool: ChainTool = tool
        super().__init__()


class ChainService:
    """Frame-wide singleton (`unique`) whose leaf reaches a per-conduit step."""

    def __init__(self, leaf: ChainLeaf) -> None:
        """
        Borrow the chained leaf.

        Args:
            leaf: Transient dependency that holds a per-conduit tool.
        """
        self.leaf: ChainLeaf = leaf


class DeadlockService:
    """Frame-wide singleton (`unique`) that holds one leaf."""

    def __init__(self, leaf: DeadlockLeaf) -> None:
        """
        Borrow the leaf.

        Args:
            leaf: Transient dependency built for this service.
        """
        self.leaf: DeadlockLeaf = leaf


class DeadlockConsumer:
    """Consumer of the unique service; its Existence and door vary per scenario."""

    def __init__(self, service: DeadlockService, value: int = 0) -> None:
        """
        Borrow the service and keep one plain input for the override scenario.

        Args:
            service: The frame-wide singleton this consumer depends on.
            value: Plain parameter targeted by the override scenario.
        """
        self.service: DeadlockService = service
        self.value: int = value


class NestedMeldConsumer:
    """
    Consumer with NO dependency edge to the service; its constructor melds the service.

    Contract:
        - With no gate installed it simply melds the service through the gate-free
          door stored on the class for warm-up.
        - In thread `meld-A` it parks first (door holds the store), then melds.
    """

    gate: Optional[ScenarioGate] = None
    warmup_door: Optional[object] = None
    service_type: type = DeadlockService

    def __init__(self) -> None:
        """Meld the service from inside this constructor, gated when a gate is installed."""
        gate = NestedMeldConsumer.gate
        if gate is None:
            door = NestedMeldConsumer.warmup_door
        else:
            if current_thread().name == "meld-A":
                gate.park_thread_a()
            door = gate.nested_door
        if not isinstance(door, (Conduit, SpellSpace)):
            raise RuntimeError("NestedMeldConsumer has no door to meld through")
        self.service: object = door.meld(spell=NestedMeldConsumer.service_type)


class MeldDeadlockScenario:
    """
    Describe, run (in a child process) and judge one lock-order scenario.

    Spec fields (all JSON-serialisable):
        consumer_existence: Existence name of the consumer.
        door: "root", "lessers" (A and C on two different lessers of one root) or
            "space" (A and C on one shared manual SpellSpace).
        competitor: "meld", "purge" or "nested".
        leaf_disposal: Whether `DeadlockLeaf` declares a disposal method.
        override: Whether thread A melds the consumer with `{"value": 7}`.
        service_chain: Optional. "direct" (default): the service is `DeadlockService`.
            "many_to_per_conduit": the service is `ChainService`, whose `many` leaf
            depends on a `unique_per_conduit` tool (unique -> many -> per_conduit).

    Timeouts:
        GATE_TIMEOUT_SECONDS bounds each ordering gate, DEADLOCK_TIMEOUT_SECONDS is
        one deadline shared by all thread joins, CHILD_TIMEOUT_SECONDS is the
        parent's hard backstop for the whole child.
    """

    GATE_TIMEOUT_SECONDS: float = 10.0
    DEADLOCK_TIMEOUT_SECONDS: float = 5.0
    CHILD_TIMEOUT_SECONDS: float = 120.0
    POLL_SECONDS: float = 0.01
    MODULE_PATH: str = "tests.integration.melder.multithreading.test_multithreading_meld_lock_order_deadlock"

    FORMERLY_DEADLOCKING_CASES: List[object] = [
        pytest.param({"consumer_existence": "unique_per_conduit", "door": "root", "competitor": "meld",
                      "leaf_disposal": False, "override": False}, id="per_conduit-root-meld"),
        pytest.param({"consumer_existence": "unique_per_conduit_lineage", "door": "root", "competitor": "meld",
                      "leaf_disposal": False, "override": False}, id="lineage-root-meld"),
        pytest.param({"consumer_existence": "unique_per_conduit_lineage", "door": "lessers", "competitor": "meld",
                      "leaf_disposal": False, "override": False}, id="lineage-two_lessers-meld"),
        pytest.param({"consumer_existence": "unique_per_conduit", "door": "root", "competitor": "meld",
                      "leaf_disposal": False, "override": True}, id="per_conduit-root-meld-override"),
        pytest.param({"consumer_existence": "unique_per_conduit", "door": "root", "competitor": "purge",
                      "leaf_disposal": False, "override": False}, id="per_conduit-root-purge"),
        pytest.param({"consumer_existence": "unique_per_conduit", "door": "root", "competitor": "nested",
                      "leaf_disposal": False, "override": False}, id="per_conduit-root-nested_meld"),
        pytest.param({"consumer_existence": "unique_per_conduit", "door": "root", "competitor": "meld",
                      "leaf_disposal": True, "override": False}, id="per_conduit-root-meld-disposal_leaf"),
        # Not reproducible as a deadlock before the fix (the competitor blocked before its gate), but it
        # is the composition the fix had to cover without restricting users: a unique's plan reaches a
        # per-conduit step on the same store thread A is building into.
        pytest.param({"consumer_existence": "unique_per_conduit", "door": "root", "competitor": "nested",
                      "leaf_disposal": False, "override": False, "service_chain": "many_to_per_conduit"},
                     id="per_conduit-root-nested_meld-unique_many_per_conduit"),
    ]

    SAFE_CASES: List[object] = [
        pytest.param({"consumer_existence": "many", "door": "root", "competitor": "meld",
                      "leaf_disposal": False, "override": False}, id="many-root-meld"),
        pytest.param({"consumer_existence": "unique_per_conduit", "door": "lessers", "competitor": "meld",
                      "leaf_disposal": False, "override": False}, id="per_conduit-two_lessers-meld"),
        pytest.param({"consumer_existence": "unique_per_spell_space", "door": "space", "competitor": "meld",
                      "leaf_disposal": False, "override": False}, id="space-shared_space-meld"),
        # Predicted to deadlock and observed NOT to (2026-09-25): a unique built through a SpellSpace
        # only touches its owner root's store, never the space store thread A holds. Kept as a tripwire.
        pytest.param({"consumer_existence": "unique_per_spell_space", "door": "space", "competitor": "meld",
                      "leaf_disposal": True, "override": False}, id="space-shared_space-meld-disposal_leaf"),
    ]

    @staticmethod
    def _finish(verdict: Dict[str, object]) -> None:
        """
        Print one JSON verdict and terminate the child immediately.

        `os._exit` is deliberate: deadlocked daemon threads still hold Melder locks,
        so normal interpreter shutdown or exit-time cleanup could block forever.

        Args:
            verdict: JSON-serialisable outcome record.
        """
        sys.stdout.write(json.dumps(verdict) + "\n")
        sys.stdout.flush()
        os._exit(0)

    @staticmethod
    def _thread_holds_spell_lock_in_purge(thread: Thread) -> bool:
        """
        Report whether `thread` is currently inside `Creations._detach_purge_entries`.

        Purge takes the unique Spell lock before calling that method, so a thread
        observed inside it holds the Spell lock and is at (or past) the store lock.

        Args:
            thread: The purge thread to inspect.

        Returns:
            bool: True when that frame is on the thread's current stack.
        """
        frame = sys._current_frames().get(thread.ident) if thread.ident is not None else None
        while frame is not None:
            if frame.f_code.co_name == "_detach_purge_entries":
                return True
            frame = frame.f_back
        return False

    @staticmethod
    def run_child(spec_json: str) -> None:
        """
        Build one world, force the scenario's interleaving and report what happened.

        Args:
            spec_json: JSON-encoded scenario spec (see the class docstring).

        Returns:
            Never returns; always leaves through `_finish`.
        """
        spec: Dict[str, object] = json.loads(spec_json)
        existence = str(spec["consumer_existence"])
        chained = spec.get("service_chain", "direct") == "many_to_per_conduit"
        service_type: type = ChainService if chained else DeadlockService
        consumer_type: type = NestedMeldConsumer if spec["competitor"] == "nested" else DeadlockConsumer
        book = Spellbook(aetheric_frame=f"meld-deadlock-{os.getpid()}")
        book.bind(spell=DeadlockLeaf, existence="many",
                  disposal_method_names=["close"] if spec["leaf_disposal"] else None)
        book.bind(spell=DeadlockService, existence="unique")
        if chained:
            book.bind(spell=ChainTool, existence="unique_per_conduit")
            book.bind(spell=ChainLeaf, existence="many")
            book.bind(spell=ChainService, existence="unique")
        NestedMeldConsumer.service_type = service_type
        book.bind(spell=consumer_type, existence=existence)
        root = book.conjure(name=f"meld-deadlock-{os.getpid()}")

        door_a: object
        door_c: object
        if spec["door"] == "root":
            door_a = door_c = root
        elif spec["door"] == "lessers":
            door_a = root.create_lesser_conduit()
            door_c = root.create_lesser_conduit()
        else:
            door_a = door_c = root.create_spellspace()
        if not isinstance(door_a, (Conduit, SpellSpace)) or not isinstance(door_c, (Conduit, SpellSpace)):
            MeldDeadlockScenario._finish({"outcome": "precondition_not_reached", "detail": "no usable door"})

        # Warm the compiled contexts (no gate installed), then return the consumer and
        # the service to the never-built state. Purge authority: space-scoped entries
        # through the space, per-conduit entries through their own conduit, lineage
        # and unique entries through the root.
        NestedMeldConsumer.warmup_door = door_a
        door_a.meld(spell=consumer_type)
        if existence == "unique_per_spell_space" or existence == "unique_per_conduit":
            door_a.purge(consumer_type)
        elif existence == "unique_per_conduit_lineage":
            root.purge(consumer_type)
        root.purge(service_type)
        if chained:
            # The competitor's unique build must reach a NOT-yet-built per-conduit step.
            door_c.purge(ChainTool)

        gate = ScenarioGate(MeldDeadlockScenario.GATE_TIMEOUT_SECONDS, nested_door=door_a)
        DeadlockLeaf.gate = gate
        NestedMeldConsumer.gate = gate
        outcomes: Dict[str, List[str]] = {"A": [], "competitor": []}
        override = {"value": 7} if spec["override"] else None

        def run_a() -> None:
            """Thread A: meld the consumer through door A and record the outcome."""
            try:
                result = door_a.meld(spell=consumer_type, override=override)
                outcomes["A"].append(type(result).__name__)
            except Exception as error:  # recorded for the parent's verdict
                outcomes["A"].append(f"{type(error).__name__}: {error}")

        def run_competitor() -> None:
            """Competitor: meld (C) or purge (P) the service; record the outcome."""
            try:
                if spec["competitor"] == "purge":
                    outcomes["competitor"].append(f"purged={root.purge(service_type)}")
                else:
                    outcomes["competitor"].append(type(door_c.meld(spell=service_type)).__name__)
            except Exception as error:  # recorded for the parent's verdict
                outcomes["competitor"].append(f"{type(error).__name__}: {error}")

        competitor_name = "purge-P" if spec["competitor"] == "purge" else "meld-C"
        thread_a = Thread(target=run_a, name="meld-A", daemon=True)
        competitor = Thread(target=run_competitor, name=competitor_name, daemon=True)
        thread_a.start()
        if not gate.a_parked.wait(MeldDeadlockScenario.GATE_TIMEOUT_SECONDS):
            MeldDeadlockScenario._finish({"outcome": "precondition_not_reached",
                                          "detail": "thread A never parked", **outcomes})
        competitor.start()
        if spec["competitor"] == "purge":
            gate_deadline = time.monotonic() + MeldDeadlockScenario.GATE_TIMEOUT_SECONDS
            while not (not competitor.is_alive()
                       or MeldDeadlockScenario._thread_holds_spell_lock_in_purge(competitor)):
                if time.monotonic() > gate_deadline:
                    MeldDeadlockScenario._finish({"outcome": "precondition_not_reached",
                                                  "detail": "purge never reached its store step", **outcomes})
                time.sleep(MeldDeadlockScenario.POLL_SECONDS)
            gate.release_a.set()
        elif not gate.competitor_inside.wait(MeldDeadlockScenario.GATE_TIMEOUT_SECONDS):
            MeldDeadlockScenario._finish({"outcome": "precondition_not_reached",
                                          "detail": "competitor never entered the service build", **outcomes})

        deadline = time.monotonic() + MeldDeadlockScenario.DEADLOCK_TIMEOUT_SECONDS
        for thread in (thread_a, competitor):
            thread.join(max(0.0, deadline - time.monotonic()))
        stuck = [thread.name for thread in (thread_a, competitor) if thread.is_alive()]
        if stuck:
            MeldDeadlockScenario._finish({"outcome": "deadlock", "stuck_threads": stuck, **outcomes})
        MeldDeadlockScenario._finish({"outcome": "completed", **outcomes})

    @staticmethod
    def assert_completes(spec: Dict[str, object]) -> None:
        """
        Launch the child for one scenario and assert every thread completed normally.

        Args:
            spec: Scenario spec (see the class docstring).

        Raises:
            MeldDeadlockDetected: The child reported stuck threads.
            pytest.fail.Exception: Any other non-completion (missed gate, crash,
                whole-child timeout, unexpected meld or purge result).
        """
        repository = Path(__file__).resolve().parents[4]
        environment = dict(os.environ)
        environment["PYTHONPATH"] = os.pathsep.join((str(repository / "src"), str(repository)))
        child_code = (
            f"from {MeldDeadlockScenario.MODULE_PATH} import MeldDeadlockScenario; "
            f"MeldDeadlockScenario.run_child({json.dumps(spec)!r})"
        )
        try:
            result = subprocess.run(
                [sys.executable, "-c", child_code], cwd=repository, env=environment, text=True,
                capture_output=True, timeout=MeldDeadlockScenario.CHILD_TIMEOUT_SECONDS, check=False,
            )
        except subprocess.TimeoutExpired:
            pytest.fail(f"child exceeded {MeldDeadlockScenario.CHILD_TIMEOUT_SECONDS}s without a verdict")
        lines = [line for line in result.stdout.splitlines() if line.startswith("{")]
        if result.returncode != 0 or not lines:
            pytest.fail(f"child failed (rc={result.returncode}): {result.stderr[-2000:]}")
        verdict = json.loads(lines[-1])
        if verdict["outcome"] == "deadlock":
            raise MeldDeadlockDetected(f"threads deadlocked: {verdict}")
        if verdict["outcome"] != "completed":
            pytest.fail(f"scenario did not run as designed: {verdict}")
        expected_a = "NestedMeldConsumer" if spec["competitor"] == "nested" else "DeadlockConsumer"
        assert verdict["A"] == [expected_a], verdict
        if spec["competitor"] == "purge":
            assert len(verdict["competitor"]) == 1 and verdict["competitor"][0].startswith("purged="), verdict
        else:
            expected_service = (
                "ChainService" if spec.get("service_chain", "direct") == "many_to_per_conduit"
                else "DeadlockService"
            )
            assert verdict["competitor"] == [expected_service], verdict


@pytest.mark.parametrize("spec", MeldDeadlockScenario.FORMERLY_DEADLOCKING_CASES)
def test_formerly_deadlocking_shape_completes(spec: Dict[str, object]) -> None:
    """
    Purpose:
        Pin each shape that deadlocked while meld doors held the store lock across a build.

    Contract:
        - Every thread completes with its normal result.
        - `MeldDeadlockDetected` means the store lock is again held while a thread waits
          on a unique's Spell lock (or another build lock); any other non-completion,
          including a missed ordering gate, also fails.
    """
    MeldDeadlockScenario.assert_completes(spec)


@pytest.mark.parametrize("spec", MeldDeadlockScenario.SAFE_CASES)
def test_meld_lock_order_safe_shape_completes(spec: Dict[str, object]) -> None:
    """
    Purpose:
        Prove the harness reports success and pin shapes that were safe before the fix.

    Contract:
        - Every thread completes with its normal result under the same gates and timing.
        - A failure here means either the harness is wrong or a new lock-order hazard
          appeared in a shape that used to be safe.
    """
    MeldDeadlockScenario.assert_completes(spec)
