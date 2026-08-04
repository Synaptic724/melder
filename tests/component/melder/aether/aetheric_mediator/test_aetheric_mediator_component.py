"""
Component tests for the aetheric mediator plane.

Tier intent per `tests/component/INFO.MD`: a SMALL REAL SLICE of wiring. Here
that means the real `Mediator` with its real owned children - claim table,
admission orchestrator, information registry, strategy registry - driven through
real registered strategies. Nothing is stubbed. What is NOT here is any melder
runtime: no Aether, no frames, no conduits, because the plane is designed to have
no dependency on them, and proving that is half the point.

The two strategies below are the same shapes the plane exists to serve:
a whole-world load (today's `LoadGate` behaviour) and a frame-scoped load
(single-frame formations, which is where the parallelism win lives).

Run:
    pytest tests/component/melder/aether/aetheric_mediator -q
"""

import threading

import pytest

from melder.aether.aetheric_mediator.admission_result import AdmissionReason
from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.mediator import Mediator
from melder.aether.aetheric_mediator.scope_keys import ScopeKey, ScopePrefix
from melder.aether.aetheric_mediator.transaction_session import (
    OutcomePolicy,
    SessionStatus,
)
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy
from melder.aether.aetheric_mediator.transaction_type import TransactionType


class WholeWorldLoad(TransactionStrategy):
    """
    Whole-world load - the current `LoadGate` behaviour as a claim.

    Claims the root scope EXCLUSIVE, which excludes every frame-scoped peer.
    """

    @staticmethod
    def build_start_plan(*, submitter, metadata):
        return {ScopeKey.world(): ClaimMode.EXCLUSIVE}

    @staticmethod
    def on_start(*, submitter, staged) -> None:
        return None

    @staticmethod
    def on_end(*, submitter, staged) -> None:
        return None


class FrameScopedLoad(TransactionStrategy):
    """
    Frame-scoped load - INTENT on the parent, EXCLUSIVE on the child.

    This is the hierarchical pattern DevOps uses (`ix` on the owning parent,
    `x` on participants) and is what lets disjoint frames proceed in parallel
    while a whole-world claim still excludes them all.
    """

    @staticmethod
    def build_start_plan(*, submitter, metadata):
        return {
            ScopeKey.world(): ClaimMode.INTENT,
            ScopeKey.frame(metadata["frame"]): ClaimMode.EXCLUSIVE,
        }

    @staticmethod
    def on_start(*, submitter, staged) -> None:
        return None

    @staticmethod
    def on_end(*, submitter, staged) -> None:
        return None


@pytest.fixture()
def plane():
    """Build a real plane with both strategies registered, and tear it down."""
    built = Mediator(max_wait_seconds=0.25)
    built.strategies.register(
        transaction_type=TransactionType.CHECKPOINT_LOAD, strategy=WholeWorldLoad
    )
    built.strategies.register(
        transaction_type=TransactionType.FORMATION_LOAD, strategy=FrameScopedLoad
    )
    yield built
    if not built.cleaned:
        built.cleanup()


def _who(identity_id: str) -> Identity:
    """Build a crystallizer-family identity."""
    return Identity(kind="crystallizer", identity_id=identity_id)


def test_plane_declares_no_dependency_on_aether():
    """
    Constraint 4, enforced as a test rather than a convention.

    STATIC, not runtime, and deliberately so. A `sys.modules` check cannot
    work here: `melder/__init__.py` eagerly boots `Aether()` at package
    import, so importing ANY `melder.*` module drags the whole runtime in
    (262 modules) before this package is even reached. That measures the
    package root's eager boot, not this package's dependencies.

    What constraint 4 actually means is a SOURCE-LEVEL dependency: no module
    in the plane may import `melder.aether.*` outside the plane itself. That
    is what keeps it constructible before any frame exists and testable in
    isolation, and it is decidable by parsing the source.
    """
    import ast
    import pathlib

    import melder.aether.aetheric_mediator as package

    # `__path__`, NOT `__file__`. Every melder subpackage is a PEP 420
    # namespace package by explicit design (pyproject sets
    # `namespaces = true`; the repo keeps exactly one `__init__.py`, at the
    # package root), and a namespace package has `__file__ is None`.
    package_root = pathlib.Path(next(iter(package.__path__)))
    offenders = []
    for source_path in sorted(package_root.glob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            imported = []
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = [node.module]
            for name in imported:
                if name.startswith("melder.aether.") and not name.startswith(
                    "melder.aether.aetheric_mediator"
                ):
                    offenders.append("{0}: {1}".format(source_path.name, name))

    assert offenders == [], (
        "plane modules declare imports on melder.aether: {0}".format(offenders)
    )


def test_no_plain_lock_anywhere_in_the_lane():
    """
    OWNER INSTRUCTION, STANDING: the mediator uses RLocks, never plain Locks.

    Enforced as a test because I have now reported it wrong once. I grepped the
    PACKAGE, found six RLocks and zero `threading.Lock()`, and reported "every
    lock in the plane is an RLock" - while the concurrency test file I had
    written minutes earlier contained FIVE plain Locks, and the pre-existing
    unit tests two more. The report was true of the directory I looked at and
    false of the lane, which is the same shape of mistake as a jurisdiction
    guard that forbids words nobody uses: the half I thought to check passed.

    So the check now covers SOURCE AND TESTS TOGETHER, and it is a test rather
    than a habit, because a habit is exactly what failed.

    WHY RLOCK IS NOT A PREFERENCE HERE: the plane re-enters its own locks. A
    thread inside `Mediator.cleanup` holding `_lock` calls into children that
    take their own; `TransactionSession` depth-counts same-thread joins;
    `ClaimTable` acquisition walks compatibility while holding. A plain Lock
    deadlocks the moment any of those paths nests, and it deadlocks
    NON-DETERMINISTICALLY under free-threaded 3.14t - the worst possible way to
    find out.

    PARSED, NOT GREPPED, and the first version of this guard is why. A regex
    over lines flagged THIS TEST at two offsets: its own docstring names the
    thing it forbids, and its own pattern string contains it. A textual check
    for a code construct cannot tell code from prose ABOUT that construct, so it
    fails on the one file guaranteed to discuss it - the guard itself.

    `ast` sees calls, not text, so a docstring mentioning the forbidden call is
    invisible to it and a real call is not.
    """
    import ast
    import pathlib

    import melder.aether.aetheric_mediator as package

    plane_root = pathlib.Path(next(iter(package.__path__)))
    repo_root = plane_root.parents[3]

    # THE LANE IS DEFINED BY CONTENT, NOT BY DIRECTORY, and that is the whole
    # point of this paragraph. The first version listed two hard-coded test
    # directories, which is the same scope-by-assumption that produced every
    # other miss in this lane. It was already wrong when written:
    # `tests/component/melder/aether/test_aether_hosted_subsystem_accessors_component.py`
    # imports `Mediator` and sits in NEITHER directory, so a plain Lock there
    # would have been invisible to a guard that reports on "the lane".
    #
    # Any test file that imports the plane IS the lane. A file moving, or a new
    # one landing somewhere nobody predicted, cannot slip out of scope.
    def imports_the_plane(path):
        """True when a file imports anything from the mediator package."""
        text = path.read_text(encoding="utf-8")
        if "aetheric_mediator" not in text:          # cheap reject before parse
            return False
        for node in ast.walk(ast.parse(text)):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any("aetheric_mediator" in name for name in names):
                return True
        return False

    in_scope = sorted(plane_root.rglob("*.py"))
    for candidate in sorted((repo_root / "tests").rglob("*.py")):
        if imports_the_plane(candidate):
            in_scope.append(candidate)

    def is_plain_lock(node):
        """True for `threading.Lock()` or a bare imported `Lock()`."""
        if not isinstance(node, ast.Call):
            return False
        func = node.func
        if isinstance(func, ast.Attribute):
            return func.attr == "Lock"
        if isinstance(func, ast.Name):
            return func.id == "Lock"
        return False

    offenders = []
    for source_path in in_scope:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if is_plain_lock(node):
                offenders.append(
                    "{0}:{1}".format(source_path.name, node.lineno)
                )

    # A guard that silently scanned nothing is worse than no guard. The plane
    # has 24 modules and there are several test files; anything near zero means
    # the discovery above broke, not that the lane got smaller.
    assert len(in_scope) > 25, (
        "the guard found only {0} files in the lane - discovery is "
        "broken".format(len(in_scope))
    )
    assert offenders == [], (
        "plain Lock in the mediator lane - the owner instruction is RLock "
        "everywhere, source AND tests: {0}".format(offenders)
    )


def test_the_two_planes_share_no_scope_key_namespace():
    """
    THE PROPERTY THAT MAKES TWO CLAIM TABLES SAFE, checked on both sides.

    This plane claims `frame:<name>` and the frame's own `ChangeControlManager`
    claims things inside that frame. Nothing arbitrates between the two tables,
    so the ONLY thing preventing them contending for one key is that their
    namespaces are disjoint - and disjointness that nobody checks is a
    convention, not a property.

    Checked STATICALLY, in the style of the two constraint-4 tests above and for
    the same reason: importing the frame plane drags the whole runtime in.

    THE ASYMMETRY THIS CATCHES. `test_no_derived_family_claims_inside_a_frame`
    guards THIS plane against reaching down, and its forbidden list was
    originally wrong in both directions - it named two prefixes the frame plane
    never uses and missed three it does. Nothing at all guarded the other
    direction: if the frame plane ever grew a `world` or `frame:` key, both
    tables would name it, neither would know, and the failure would be a silent
    loss of isolation rather than an error.

    SCOPE OF THE CHECK, stated so it is not over-trusted: it reads string
    literals out of the frame plane's source. A key assembled at runtime from
    parts would not be seen. That is acceptable because the frame plane builds
    its keys as inline f-string literals today, and a helper appearing there is
    itself the signal to revisit this.
    """
    import pathlib
    import re

    import melder.aether.aetheric_mediator as package

    plane_root = pathlib.Path(next(iter(package.__path__)))
    frame_plane = (
        plane_root.parent / "aetheric_frame" / "dev_ops" / "change_control_manager"
    )
    assert frame_plane.is_dir(), (
        "frame plane not found at {0} - this guard has gone stale".format(
            frame_plane
        )
    )

    # The three names THIS plane owns. `ScopePrefix` is the closed vocabulary,
    # so reading it here keeps the two in step automatically.
    ours = {member.value for member in ScopePrefix}

    literal = re.compile(r'f?"([a-z_]+):')
    theirs = set()
    for source_path in sorted(frame_plane.rglob("*.py")):
        text = source_path.read_text(encoding="utf-8")
        theirs.update(literal.findall(text))
        if '"world"' in text:
            theirs.add("world")

    assert theirs, (
        "no scope-key prefixes found in the frame plane - the pattern this "
        "guard matches on has changed and it is no longer checking anything"
    )
    collisions = sorted(ours & theirs)
    assert collisions == [], (
        "the two claim tables both name {0}, and nothing arbitrates between "
        "them. Ours: {1}. Theirs: {2}.".format(
            collisions, sorted(ours), sorted(theirs)
        )
    )


def test_plane_depends_on_nothing_but_utilities():
    """
    The stronger form of constraint 4: exactly one external melder dependency.

    Guards against the plane quietly growing coupling to any other melder
    subsystem, not just to aether.
    """
    import ast
    import pathlib

    import melder.aether.aetheric_mediator as package

    # `__path__`, NOT `__file__`. Every melder subpackage is a PEP 420
    # namespace package by explicit design (pyproject sets
    # `namespaces = true`; the repo keeps exactly one `__init__.py`, at the
    # package root), and a namespace package has `__file__ is None`.
    package_root = pathlib.Path(next(iter(package.__path__)))
    external = set()
    for source_path in sorted(package_root.glob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if name.startswith("melder.") and not name.startswith(
                    "melder.aether.aetheric_mediator"
                ):
                    external.add(name)

    assert external == {"melder.utilities.general_base.cleanable"}, (
        "plane external dependencies drifted: {0}".format(sorted(external))
    )


def test_disjoint_frames_run_in_parallel_and_whole_world_excludes_them(plane):
    """
    The LoadGate re-expression, end to end.

    Two disjoint frame loads coexist on one world via INTENT; a whole-world
    load is excluded while they hold, then admits once they clear.
    """
    first = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    second = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("two"),
        metadata={"frame": "B"},
    )
    assert first is not second

    with pytest.raises(RuntimeError) as excinfo:
        plane.begin(
            transaction_type=TransactionType.CHECKPOINT_LOAD,
            submitter=_who("whole"),
        )
    assert AdmissionReason.WAIT_TIMEOUT.value in str(excinfo.value)
    assert ScopeKey.world() in str(excinfo.value)

    first.leave()
    plane.commit(first)
    second.leave()
    plane.commit(second)

    whole = plane.begin(
        transaction_type=TransactionType.CHECKPOINT_LOAD, submitter=_who("whole")
    )
    whole.leave()
    plane.commit(whole)
    assert plane.describe()["claims"]["scope_count"] == 0


def test_same_frame_contends_while_different_frames_do_not(plane):
    """Isolation is per frame, not global."""
    held = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    with pytest.raises(RuntimeError):
        plane.begin(
            transaction_type=TransactionType.FORMATION_LOAD,
            submitter=_who("two"),
            metadata={"frame": "A"},
        )
    other = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("three"),
        metadata={"frame": "B"},
    )
    other.leave()
    plane.commit(other)
    held.leave()
    plane.commit(held)


def test_same_identity_same_thread_joins(plane):
    """Re-entry by one actor must not deadlock it against itself."""
    who = _who("one")
    outer = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=who,
        metadata={"frame": "A"},
    )
    inner = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=who,
        metadata={"frame": "A"},
    )
    assert inner is outer
    assert outer.depth == 2
    inner.leave()
    outer.leave()
    plane.commit(outer)
    assert plane.describe()["claims"]["scope_count"] == 0


def test_commit_stamps_freshness_before_releasing(plane):
    """`apply_commit_delta` must run while claims are still held."""
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    session.leave()
    plane.commit(session)

    fact = plane.reporting.get_fact(ScopeKey.frame("A"))
    assert fact is not None
    assert fact["fact_family"] == TransactionType.FORMATION_LOAD.value
    stale = plane.reporting.stale_regions(
        regions=(ScopeKey.frame("A"), "frame:NEVER"), max_age_seconds=3600.0
    )
    assert stale == ("frame:NEVER",), "never-reported regions count as stale"


def test_leave_broken_keeps_the_world_but_releases_the_claims(plane):
    """Leaving the WORLD broken must never wedge the PLANE."""
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "C"},
        outcome_policy=OutcomePolicy.LEAVE_BROKEN,
    )

    def must_not_run() -> None:
        raise AssertionError("LEAVE_BROKEN must not invoke inverses")

    session.register_rollback_action(
        action=must_not_run, description="tear down frame:C posture"
    )
    session.leave()
    status, residue = plane.fail(session, "stage 6 raised")

    assert status is SessionStatus.BROKEN
    assert residue == ("tear down frame:C posture",)
    assert ScopeKey.frame("C") not in plane.describe()["claims"]["scopes"]

    reclaimed = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("repair"),
        metadata={"frame": "C"},
    )
    reclaimed.leave()
    plane.commit(reclaimed)


def test_unwind_runs_inverses_then_releases(plane):
    """The other outcome: walk the world back, then free the scope."""
    order = []
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "D"},
        outcome_policy=OutcomePolicy.UNWIND,
    )
    for name in ("postured frame", "conjured conduit"):
        session.register_rollback_action(
            action=(lambda name=name: order.append(name)),
            description="undo {0}".format(name),
        )
    session.leave()
    status, failures = plane.fail(session, "stage 6 raised")

    assert status is SessionStatus.ABORTED
    assert order == ["conjured conduit", "postured frame"]
    assert failures == ()
    assert plane.describe()["claims"]["scope_count"] == 0


def test_reporting_answers_along_three_axes_while_in_flight(plane):
    """Live activity indexes are the 'what is happening now' half."""
    session = plane.begin(
        transaction_type=TransactionType.FORMATION_LOAD,
        submitter=_who("one"),
        metadata={"frame": "A"},
    )
    assert len(plane.reporting.activity_by_scope(ScopeKey.frame("A"))) == 1
    assert len(
        plane.reporting.activity_by_submitter(
            submitter_kind="crystallizer", submitter_id="one"
        )
    ) == 1
    assert len(plane.reporting.activity_by_type("formation_load")) == 1

    session.leave()
    plane.commit(session)
    assert plane.reporting.activity_by_scope(ScopeKey.frame("A")) == ()


def test_seeded_family_runs_without_local_registration(plane):
    """
    Every vocabulary member has a family at construction, so a type this fixture
    never registered still admits with a real claim set.

    This REPLACES an earlier test that expected `begin(AGENT_REPAIR)` to raise
    `KeyError`. That expectation was correct while the registry started empty;
    `StrategyBuilder` now seeds a family for EVERY vocabulary member in
    `__init__`, mirroring the DevOps plane, so an unregistered member is no
    longer reachable.

    The fixture registers only CHECKPOINT_LOAD and FORMATION_LOAD, which is what
    makes this meaningful: AGENT_REPAIR is served by the SEEDED family, not by
    anything this test set up. And the claim it produces is checked rather than
    assumed - a repair naming no scopes has unbounded reach into a world already
    known to be broken, so it must take the whole world.
    """
    session = plane.begin(
        transaction_type=TransactionType.AGENT_REPAIR, submitter=_who("one")
    )
    try:
        assert sorted(session.staged.granted_scopes) == [ScopeKey.world()]
    finally:
        session.leave()
        plane.commit(session)


def test_seeded_repair_family_claims_only_what_it_is_given(plane):
    """A repair that names its scopes claims those, not the world."""
    session = plane.begin(
        transaction_type=TransactionType.AGENT_REPAIR,
        submitter=_who("one"),
        metadata={"repair_scopes": [ScopeKey.frame("A")]},
    )
    try:
        assert sorted(session.staged.granted_scopes) == [
            ScopeKey.frame("A"),
            ScopeKey.world(),
        ]
    finally:
        session.leave()
        plane.commit(session)


def test_concurrent_frame_loads_do_not_serialise(plane):
    """
    Sixteen threads over four frames: same-frame serialises, cross-frame does
    not, and the plane drains completely afterwards.
    """
    errors = []
    barrier = threading.Barrier(16)

    def worker(index: int) -> None:
        frame = "F{0}".format(index % 4)
        who = Identity(kind="crystallizer", identity_id="w{0}".format(index))
        barrier.wait()
        try:
            session = plane.begin(
                transaction_type=TransactionType.FORMATION_LOAD,
                submitter=who,
                metadata={"frame": frame},
            )
        except RuntimeError:
            return
        try:
            session.leave()
            plane.commit(session)
        except Exception as error:  # pragma: no cover - surfaced by assert
            errors.append("{0}: {1}".format(type(error).__name__, error))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(16)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == [], "commit path raised under concurrency: {0}".format(errors)
    assert plane.describe()["claims"]["scope_count"] == 0
    assert plane.describe()["admission"]["in_flight_count"] == 0


def test_plane_cleanup_is_idempotent_and_tears_down_children(plane):
    """Cleaning the root must clean everything it owns, twice safely."""
    plane.cleanup()
    plane.cleanup()
    assert plane.cleaned is True
    with pytest.raises(RuntimeError):
        plane.describe()
