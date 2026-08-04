"""
The kitchen sink: every transaction family, many threads, one plane.

WHY THIS FILE EXISTS. The plane had thirteen threaded tests and they covered the
claim table, the session join model, admission waiting and cleanup wakeups -
everything that existed before the participation model landed. What they did NOT
cover was anything added with it:

  - NO test drove all EIGHT families concurrently through the real
    `begin` -> `leave` -> `commit` pipeline. The isolation matrix asserts pairwise
    `try_acquire` on a `ClaimTable`, single-threaded, which proves the modes are
    right and proves nothing about the pipeline around them.
  - NO test raced the participant store. Every participation test was
    single-threaded, so `_participants` - new state, new lock discipline, written
    from inside `apply_commit_delta` while claims are held - had never had two
    threads pointed at it.

Free-threaded 3.14t removed the accidental serialisation the GIL used to give,
so "it is under an RLock" is a claim to be tested rather than a design to be
trusted.

ON SINGLETONS, because the question is reasonable and the answer is a real
design position rather than an omission: NOTHING in this plane is a singleton.
There is no `_instance`, no `_initialized`, no `__new__`, and no
`_reset_singleton_for_tests` anywhere in the package. `Mediator` is an ordinary
object constructed and held by Aether, which is what lets a test build as many
independent planes as it wants - and is why the singleton-reset dance the three
subsystem roots need has no counterpart here. The properties that pattern exists
to protect are still real, so they are tested directly at the bottom of this
file: independence, idempotent cleanup, and a clean plane after a dirty one.

Run:
    pytest tests/component/melder/aether/aetheric_mediator -q
"""

import threading
import time

import pytest

from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.mediator import Mediator
from melder.aether.aetheric_mediator.participation import ParticipationState
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.transaction_type import TransactionType

THREADS = 8
ROUNDS = 6
JOIN_TIMEOUT_SECONDS = 30.0

# HOW LONG EACH TRANSACTION HOLDS ITS CLAIMS, and why the number is not zero.
# The first version of this file held nothing: begin, leave, commit with no work
# between them. Measured, that ran 48 world-EXCLUSIVE transactions across eight
# threads with ZERO refusals in 0.00 seconds - every acquisition released before
# the next thread reached the table, so nothing ever contended and every
# assertion here passed without exercising a single race. A concurrency test
# that never achieves concurrency is worse than no test, because it reports
# green.
#
# Three milliseconds is long enough that eight threads genuinely overlap and
# short enough that the whole file stays under a second. The tests below do not
# TRUST that this produces contention - they measure elapsed time against what
# serialised work would cost and fail if the plane was never actually contended.
HOLD_SECONDS = 0.003

# One metadata bundle per family. Every family reads only its own keys and
# ignores the rest, which is asserted in the strategy unit tests - so a single
# mapping can drive all eight without special-casing any of them.
FAMILY_METADATA = {
    TransactionType.CHECKPOINT_LOAD: {},
    TransactionType.FORMATION_LOAD: {"target_frame_name": "A"},
    TransactionType.FRAME_CREATE: {"frame_name": "B"},
    TransactionType.INDEX_GRAFT: {"host_frame_name": "C"},
    TransactionType.SUBSYSTEM_CONFIGURE: {
        "subsystem_name": "crystallizer", "worker_count": 4,
    },
    TransactionType.SUBSYSTEM_ACTIVATE: {"subsystem_name": "nexus"},
    TransactionType.SUBSYSTEM_DEACTIVATE: {"subsystem_name": "nexus"},
    TransactionType.AGENT_REPAIR: {"repair_scopes": [ScopeKey.frame("D")]},
}


@pytest.fixture(name="plane")
def _plane():
    """
    One real plane per test, with a short admission wait.

    The wait is deliberately SMALL rather than zero: zero would make every
    contended thread refuse immediately and the test would never exercise the
    park-and-retry path, which is where the interesting races live.
    """
    built = Mediator(max_wait_seconds=0.25)
    try:
        yield built
    finally:
        built.cleanup()


def _run(workers):
    """
    Start every worker at once and join them all, failing on a stuck thread.

    Returns:
        float: Wall-clock seconds from the barrier release to the last join.
            Several tests assert against this, because ELAPSED TIME IS THE ONLY
            DIRECT EVIDENCE that claims actually excluded each other - a green
            assertion on final state is equally green whether the threads
            serialised or never met.

    Raises:
        AssertionError: If any thread is still alive after the join timeout,
            which is how a deadlock reports itself here rather than hanging the
            whole suite.
    """
    barrier = threading.Barrier(len(workers))
    threads = [
        threading.Thread(target=worker, args=(barrier,)) for worker in workers
    ]
    started = time.monotonic()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=JOIN_TIMEOUT_SECONDS)
    elapsed = time.monotonic() - started
    alive = [thread for thread in threads if thread.is_alive()]
    assert not alive, (
        "{0} thread(s) never finished - the plane deadlocked rather than "
        "refusing".format(len(alive))
    )
    return elapsed


def _drive(plane, identity, transaction_type, metadata, hold=HOLD_SECONDS):
    """
    Run one transaction end to end, HOLDING its claims for `hold` seconds.

    The hold is the whole point: without it a transaction releases before any
    other thread reaches the table and the plane is never contended. See the
    note on `HOLD_SECONDS`.

    Returns True on commit, False on refusal. A refusal is a legitimate outcome
    under contention and is NOT an error - the plane's contract is bounded
    waiting and then a refusal carrying evidence. What WOULD be an error is a
    refusal that leaked the session or its claims, which the callers assert
    afterwards by reading the table.
    """
    try:
        session = plane.begin(
            transaction_type=transaction_type,
            submitter=identity,
            metadata=metadata,
        )
    except RuntimeError:
        return False
    try:
        if hold:
            time.sleep(hold)
    finally:
        session.leave()
        plane.commit(session)
    return True


# --------------------------------------------------------------------------
# Contention is REAL, proven by the clock rather than assumed
# --------------------------------------------------------------------------

def test_world_exclusive_transactions_actually_serialise(plane):
    """
    THE CONTROL FOR EVERY OTHER TEST IN THIS FILE.

    Eight threads each run three whole-world transactions holding `world`
    EXCLUSIVE for `HOLD_SECONDS`. EXCLUSIVE admits one holder, so the 24 holds
    cannot overlap and the wall clock cannot come in under their sum. If it
    does, the transactions were not excluding each other and every "no torn
    row" assertion in this file was measuring an empty room.

    The bound is deliberately loose - 70% of the theoretical serial cost -
    because thread scheduling and the admission retry loop add jitter in both
    directions. It is still far above what OVERLAPPING work could produce.
    """
    rounds = 3
    holds = THREADS * rounds

    def make_worker(index):
        """Build one worker driving whole-world transactions."""
        def worker(barrier):
            identity = Identity(kind="crystallizer", identity_id=f"w-{index}")
            try:
                barrier.wait()
                for _ in range(rounds):
                    _drive(plane, identity, TransactionType.CHECKPOINT_LOAD, {})
            finally:
                identity.cleanup()
        return worker

    elapsed = _run([make_worker(index) for index in range(THREADS)])

    serial_cost = holds * HOLD_SECONDS
    assert elapsed >= serial_cost * 0.7, (
        "{0} world-exclusive holds of {1}s finished in {2:.3f}s - they did NOT "
        "serialise, so nothing in this file was actually contended".format(
            holds, HOLD_SECONDS, elapsed
        )
    )
    assert plane.describe()["claims"]["scope_count"] == 0


def test_disjoint_frames_do_not_serialise_under_threads(plane):
    """
    The converse, and the reason `world` INTENT exists at all.

    Eight threads load EIGHT DIFFERENT frames, each holding `world` ix plus its
    own `frame:<name>` x. Intent markers coexist and the child keys are
    disjoint, so none of these should wait for any other - the wall clock should
    land near ONE hold, not eight.

    Without this test the previous one is satisfiable by a plane that simply
    serialises everything, which would be a global mutex with extra vocabulary.
    """
    rounds = 3

    def make_worker(index):
        """Build one worker loading its own frame."""
        def worker(barrier):
            identity = Identity(kind="crystallizer", identity_id=f"f-{index}")
            try:
                barrier.wait()
                for _ in range(rounds):
                    _drive(
                        plane, identity, TransactionType.FORMATION_LOAD,
                        {"target_frame_name": f"frame-{index}"},
                    )
            finally:
                identity.cleanup()
        return worker

    elapsed = _run([make_worker(index) for index in range(THREADS)])

    serial_cost = THREADS * rounds * HOLD_SECONDS
    assert elapsed < serial_cost * 0.5, (
        "disjoint frame loads took {0:.3f}s against a serial cost of {1:.3f}s - "
        "they are serialising against each other, which is the over-claim the "
        "mode vocabulary exists to prevent".format(elapsed, serial_cost)
    )
    assert plane.describe()["claims"]["scope_count"] == 0


# --------------------------------------------------------------------------
# The kitchen sink
# --------------------------------------------------------------------------

def test_every_family_under_threads_leaves_no_claim_behind(plane):
    """
    THE HEADLINE. Eight families, eight threads, six rounds each, all racing.

    The assertion that matters is the one at the end: the claim table is EMPTY.
    Every transaction here either commits or is refused, and both paths must
    release. A family that leaked a claim on the refusal path would wedge the
    plane permanently and would be invisible in any single-threaded test,
    because single-threaded work is never refused.
    """
    families = list(FAMILY_METADATA.items())
    outcomes = []
    outcomes_lock = threading.Lock()

    def make_worker(index):
        """Build one worker that cycles the families from its own identity."""
        def worker(barrier):
            identity = Identity(kind="subsystem", identity_id=f"racer-{index}")
            try:
                barrier.wait()
                committed = 0
                for round_number in range(ROUNDS):
                    transaction_type, metadata = families[
                        (index + round_number) % len(families)
                    ]
                    if _drive(plane, identity, transaction_type, metadata):
                        committed += 1
                with outcomes_lock:
                    outcomes.append(committed)
            finally:
                identity.cleanup()
        return worker

    elapsed = _run([make_worker(index) for index in range(THREADS)])

    assert len(outcomes) == THREADS, "a thread died without recording an outcome"
    assert sum(outcomes) > 0, (
        "every transaction was refused - the wait is too short to prove anything"
    )
    # Two of the eight families take `world` EXCLUSIVE, so a run this size
    # cannot complete in the time one hold costs. If it did, the holds never
    # overlapped and the leak assertions below saw an idle plane.
    assert elapsed > HOLD_SECONDS * 2, (
        "{0} transactions across {1} threads finished in {2:.3f}s - the plane "
        "was never contended".format(THREADS * ROUNDS, THREADS, elapsed)
    )
    snapshot = plane.describe()
    assert snapshot["claims"]["scope_count"] == 0, (
        "claims survived their transactions: {0}".format(snapshot["claims"])
    )
    assert snapshot["admission"]["in_flight_count"] == 0
    assert snapshot["reporting"]["active_count"] == 0


def test_contended_and_disjoint_families_both_make_progress(plane):
    """
    A whole-world family must not starve the frame-scoped ones into never
    committing, and disjoint frame work must not serialise behind it.

    This is the property the mode vocabulary exists for, asserted through the
    real pipeline rather than through `try_acquire`: `world` EXCLUSIVE excludes
    everything, but it is held only for the length of one transaction, so a
    frame load racing it should still get through within the wait.
    """
    committed = {"checkpoint": 0, "frame_a": 0, "frame_b": 0}
    counter_lock = threading.Lock()

    def make_worker(label, transaction_type, metadata):
        """Build one worker that repeatedly drives a single family."""
        def worker(barrier):
            identity = Identity(kind="subsystem", identity_id=label)
            try:
                barrier.wait()
                for _ in range(ROUNDS):
                    if _drive(plane, identity, transaction_type, metadata):
                        with counter_lock:
                            committed[label] += 1
            finally:
                identity.cleanup()
        return worker

    _run([
        make_worker("checkpoint", TransactionType.CHECKPOINT_LOAD, {}),
        make_worker("frame_a", TransactionType.FORMATION_LOAD,
                    {"target_frame_name": "A"}),
        make_worker("frame_b", TransactionType.FORMATION_LOAD,
                    {"target_frame_name": "B"}),
    ])

    assert committed["frame_a"] > 0 and committed["frame_b"] > 0, (
        "frame-scoped work starved behind the world claim: {0}".format(committed)
    )
    assert committed["checkpoint"] > 0, (
        "the world claim never won: {0}".format(committed)
    )
    assert plane.describe()["claims"]["scope_count"] == 0


# --------------------------------------------------------------------------
# The participation store under contention
# --------------------------------------------------------------------------

def test_racing_lifecycle_edges_never_leave_a_torn_row(plane):
    """
    THE INVARIANT THE EXCLUSIVE CLAIM IS FOR. State and conditions move together
    or not at all.

    Writers race activate against deactivate on ONE subsystem while a reader
    checks, continuously, that the two halves of a row agree: `emits` must be
    True EXACTLY when the state is ACTIVE.

    THE READER TAKES ONE RENDERED ROW, AND THE FIRST VERSION OF THIS TEST DID
    NOT - it called `participation_state(...)` and then `is_participating(...)`,
    which is TWO lock acquisitions with a window between them. It failed
    immediately, reporting `(ACTIVE, False)`. That was a real finding about the
    API and a bug in the test rather than in the plane: each verb is internally
    consistent, but the registry cannot make two separate calls consistent with
    each other, because nothing is held across them. A caller that needs both
    halves must take them from ONE read, which is exactly what
    `describe_participants()` builds under a single acquisition.

    So the assertion below is the honest one, and the trap the first version
    fell into is now written into the contract on both verbs.
    """
    failures = []
    reads = []
    bookkeeping = threading.Lock()
    # A COUNTDOWN, not a flag. An earlier version set a single Event in each
    # writer's `finally`, so the FIRST writer to finish stopped the reader and
    # the row was only sampled during the opening moments of the race. The
    # reader must outlive every writer or it is watching an empty room.
    running = threading.Semaphore(0)
    remaining = {"writers": THREADS}

    def writer(index):
        """Build one worker that hammers one lifecycle edge."""
        transaction_type = (
            TransactionType.SUBSYSTEM_ACTIVATE if index % 2 == 0
            else TransactionType.SUBSYSTEM_DEACTIVATE
        )
        metadata = {"subsystem_name": "crystallizer"}
        if index % 2 == 0:
            metadata["worker_count"] = index

        def worker(barrier):
            identity = Identity(kind="subsystem", identity_id=f"w-{index}")
            try:
                barrier.wait()
                for _ in range(ROUNDS):
                    _drive(plane, identity, transaction_type, metadata)
            finally:
                identity.cleanup()
                with bookkeeping:
                    remaining["writers"] -= 1
                running.release()
        return worker

    def reader(barrier):
        """Assert the row is self-consistent, continuously, while it moves."""
        barrier.wait()
        checks = 0
        while True:
            with bookkeeping:
                if remaining["writers"] == 0:
                    break
            for row in plane.reporting.describe_participants():
                if row["emits"] != (
                        row["state"] == ParticipationState.ACTIVE.value
                ):
                    with bookkeeping:
                        failures.append(row)
            checks += 1
        with bookkeeping:
            reads.append(checks)

    _run([writer(index) for index in range(THREADS)] + [reader])

    assert not failures, (
        "torn participant row observed {0} time(s); first: {1}".format(
            len(failures), failures[0]
        )
    )
    assert reads and reads[0] > 100, (
        "the reader sampled the row only {0} time(s) - it did not overlap the "
        "writers, so it proved nothing".format(reads[0] if reads else 0)
    )
    final = plane.participation_state("crystallizer")
    assert final in (ParticipationState.ACTIVE, ParticipationState.INACTIVE)
    assert plane.is_participating("crystallizer") is (
        final is ParticipationState.ACTIVE
    )
    assert plane.describe()["claims"]["scope_count"] == 0


def test_disjoint_subsystems_all_land_with_no_lost_updates(plane):
    """
    Activating eight different subsystems at once must record EIGHT rows.

    Disjoint `subsystem:<name>` keys share only the `world` INTENT marker, which
    coexists with itself, so none of these should even contend. A lost row here
    would mean the store dropped a write under concurrency - the classic
    read-modify-write bug in a dict that only shows up with real threads.
    """
    names = [f"subsystem-{index}" for index in range(THREADS)]

    def make_worker(name):
        """Build one worker that activates exactly one subsystem."""
        def worker(barrier):
            identity = Identity(kind="subsystem", identity_id=name)
            try:
                barrier.wait()
                _drive(
                    plane, identity, TransactionType.SUBSYSTEM_ACTIVATE,
                    {"subsystem_name": name, "worker_count": 1},
                )
            finally:
                identity.cleanup()
        return worker

    _run([make_worker(name) for name in names])

    assert plane.participants() == tuple(sorted(names))
    assert plane.participants_in_state(ParticipationState.ACTIVE) == tuple(
        sorted(names)
    )
    for name in names:
        assert plane.reporting.participant_conditions(name) == {
            "worker_count": 1
        }


def test_configure_racing_activate_never_reports_a_running_subsystem_as_stopped(
        plane,
):
    """
    `record_conditions` reads the current state and writes it back, which is the
    plane's only read-before-write. It is safe ONLY because the read and the
    write happen inside one lock acquisition AND the family holds
    `subsystem:<name>` EXCLUSIVE for the whole transaction.

    Racing configure against activate is the test that would break it: if the
    preservation rule ever became a check-then-set across the lock, a configure
    would land CONFIGURED on top of a subsystem that had just activated, and the
    plane would report a running subsystem as not running.
    """
    observed = []
    observed_lock = threading.Lock()

    def make_worker(index):
        """Alternate configure and activate against one subsystem."""
        configuring = index % 2 == 0
        transaction_type = (
            TransactionType.SUBSYSTEM_CONFIGURE if configuring
            else TransactionType.SUBSYSTEM_ACTIVATE
        )
        metadata = {"subsystem_name": "nexus"}
        if configuring:
            metadata["worker_count"] = index

        def worker(barrier):
            identity = Identity(kind="subsystem", identity_id=f"c-{index}")
            try:
                barrier.wait()
                for _ in range(ROUNDS):
                    _drive(plane, identity, transaction_type, metadata)
                    with observed_lock:
                        observed.append(plane.participation_state("nexus"))
            finally:
                identity.cleanup()
        return worker

    _run([make_worker(index) for index in range(THREADS)])

    assert observed, "no state was ever observed"
    assert all(
        state in (ParticipationState.CONFIGURED, ParticipationState.ACTIVE)
        for state in observed
    ), (
        "a configure/activate race produced a state neither family writes: "
        "{0}".format({state for state in observed})
    )
    assert plane.describe()["claims"]["scope_count"] == 0


# --------------------------------------------------------------------------
# Lifecycle - what "singleton reset" would have protected, tested directly
# --------------------------------------------------------------------------

def test_two_planes_are_completely_independent():
    """
    NOTHING HERE IS A SINGLETON, and this is the test that makes that safe to
    rely on. Two planes share no class-level state, so a claim held in one must
    not be visible to - or block - the other.

    If this ever fails, some part of the plane has acquired process-wide state
    and every test that builds its own plane has been lying.
    """
    first = Mediator(max_wait_seconds=0.1)
    second = Mediator(max_wait_seconds=0.1)
    holder = Identity(kind="crystallizer", identity_id="holder")
    try:
        session = first.begin(
            transaction_type=TransactionType.CHECKPOINT_LOAD, submitter=holder
        )
        try:
            assert first.describe()["claims"]["scope_count"] == 1
            assert second.describe()["claims"]["scope_count"] == 0

            other = second.begin(
                transaction_type=TransactionType.CHECKPOINT_LOAD,
                submitter=holder,
            )
            other.leave()
            second.commit(other)

            first.register_participant("crystallizer")
            assert first.has_participant("crystallizer") is True
            assert second.has_participant("crystallizer") is False
        finally:
            session.leave()
            first.commit(session)
    finally:
        holder.cleanup()
        first.cleanup()
        second.cleanup()


def test_a_fresh_plane_after_a_cleaned_one_starts_empty():
    """
    The reset equivalent: build a plane, dirty it, clean it, build another.

    The second plane must show no trace of the first - no claims, no roster, no
    activity. This is what `_reset_singleton_for_tests` buys the subsystem roots
    and what construction buys here, and it is worth asserting rather than
    assuming, because a module-level default or a mutable class attribute would
    break it silently.
    """
    first = Mediator(max_wait_seconds=0.1)
    holder = Identity(kind="crystallizer", identity_id="holder")
    try:
        first.register_participant("crystallizer")
        session = first.begin(
            transaction_type=TransactionType.SUBSYSTEM_ACTIVATE,
            submitter=holder,
            metadata={"subsystem_name": "crystallizer", "worker_count": 4},
        )
        session.leave()
        first.commit(session)
        assert first.participants() == ("crystallizer",)
    finally:
        first.cleanup()

    second = Mediator(max_wait_seconds=0.1)
    try:
        assert second.participants() == ()
        assert second.participation_state("crystallizer") is None
        assert second.describe()["claims"]["scope_count"] == 0
        assert second.describe()["reporting"]["participant_count"] == 0
        assert second.strategies.missing_types() == ()
    finally:
        holder.cleanup()
        second.cleanup()


def test_concurrent_cleanup_of_the_plane_runs_exactly_once():
    """
    Eight threads calling `cleanup()` at once must not double-free the children.

    The plane cleans a claim table, an orchestrator, a registry, a strategy
    builder and every live session. Without the re-check under the lock, two
    threads would both pass the fast-path check and both tear those down - and
    the loser would call `cleanup()` on already-deleted slots.
    """
    plane = Mediator(max_wait_seconds=0.1)
    errors = []
    errors_lock = threading.Lock()

    def worker(barrier):
        """Tear the plane down from every thread at once."""
        barrier.wait()
        try:
            plane.cleanup()
        except Exception as exc:  # noqa: BLE001 - the failure IS the finding
            with errors_lock:
                errors.append(exc)

    _run([worker for _ in range(THREADS)])

    assert not errors, "concurrent cleanup raised: {0!r}".format(errors[:2])
    assert plane.cleaned is True
    with pytest.raises(RuntimeError):
        plane.participants()
