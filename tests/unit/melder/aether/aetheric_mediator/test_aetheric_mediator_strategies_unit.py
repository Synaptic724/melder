"""
Unit tests for the plane's six transaction families.

WHY THIS FILE EXISTS: the strategies shipped with no coverage of their own.

HOW ISOLATION IS ASSERTED, and why the first version of this file was wrong:
an earlier revision compared claim plans with a hand-written `_plans_conflict`
helper that reimplemented the compatibility walk. That is the mistake
`pytest_unit.md` calls Rank E - it asserts against a REIMPLEMENTATION rather
than the system, so it would keep passing if `ClaimTable.try_acquire` changed
underneath it and would fail only if the copy drifted. These tests drive the
REAL `ClaimTable` instead: two holders, real acquisition, and the observable
outcome is whether the second acquisition returns blocking evidence.

Run:
    pytest tests/unit/melder/aether/aetheric_mediator -q
"""

import pytest

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.claim_table import ClaimTable
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.strategies.agent_repair_transaction_strategy import (
    AgentRepairTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.checkpoint_load_transaction_strategy import (
    CheckpointLoadTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.formation_load_transaction_strategy import (
    FormationLoadTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.frame_create_transaction_strategy import (
    FrameCreateTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.index_graft_transaction_strategy import (
    IndexGraftTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.subsystem_disable_transaction_strategy import (
    SubsystemDisableTransactionStrategy,
)
from melder.aether.aetheric_mediator.strategies.subsystem_enable_transaction_strategy import (
    SubsystemEnableTransactionStrategy,
)
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy

ALL_FAMILIES = (
    AgentRepairTransactionStrategy,
    CheckpointLoadTransactionStrategy,
    FormationLoadTransactionStrategy,
    FrameCreateTransactionStrategy,
    IndexGraftTransactionStrategy,
    SubsystemDisableTransactionStrategy,
    SubsystemEnableTransactionStrategy,
)

# `agent_repair` is excluded from the jurisdiction sweep because its claim set
# is caller-supplied by contract - a caller passing frame-internal keys is
# asking the wrong plane, which its own docstring records. Excluding it here is
# clearer than skipping inside the test, which hides the exemption in output.
DERIVED_FAMILIES = tuple(
    family for family in ALL_FAMILIES if family is not AgentRepairTransactionStrategy
)

# Every family reads these; each ignores the keys that are not its own.
FULL_METADATA = {
    "frame_name": "A",
    "target_frame_name": "A",
    "host_frame_name": "A",
    "subsystem_name": "crystallizer",
    "repair_scopes": ("frame:A",),
}


@pytest.fixture(name="submitter")
def _submitter():
    """One real claimant. Strategies take an `Identity`, so tests supply one."""
    built = Identity(kind="crystallizer", identity_id="planner")
    try:
        yield built
    finally:
        built.cleanup()


@pytest.fixture(name="table")
def _table():
    """A real claim table - the arbiter these tests assert against."""
    built = ClaimTable()
    try:
        yield built
    finally:
        built.cleanup()


def _blocks_second_holder(table, first_plan, second_plan):
    """
    Acquire two plans on one real table and report whether the second is blocked.

    The observable outcome is `try_acquire`'s own return: an EMPTY tuple means
    granted, a non-empty tuple is blocking evidence. Nothing here interprets
    modes - the table does that, which is the point.
    """
    one = Identity(kind="crystallizer", identity_id="holder-one")
    two = Identity(kind="crystallizer", identity_id="holder-two")
    try:
        granted = table.try_acquire(one, first_plan)
        assert granted == (), "the first holder should always be granted"
        blocks = table.try_acquire(two, second_plan)
        for block in blocks:
            block.cleanup()
        return bool(blocks)
    finally:
        table.release_holder(one)
        table.release_holder(two)
        one.cleanup()
        two.cleanup()


# --------------------------------------------------------------------------
# Contract shape
# --------------------------------------------------------------------------

@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_families_are_classes_not_instances(family):
    """
    The contract forbids per-strategy instance state so concurrency lives
    entirely in the mediator and its claims.
    """
    assert isinstance(family, type)
    assert issubclass(family, TransactionStrategy)


@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_every_plan_is_complete_and_typed(family, submitter):
    """
    The plane has NO implicit default mode, so every key a family emits must
    carry an explicit `ClaimMode`; a bare string would be silently unusable.
    """
    plan = family.build_start_plan(submitter=submitter, metadata={})
    assert plan, "a family that claims nothing would isolate nothing"
    for scope_key, mode in plan.items():
        assert isinstance(scope_key, str) and scope_key
        assert isinstance(mode, ClaimMode)


@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_planning_does_not_mutate_its_inputs(family, submitter):
    """
    `build_start_plan` runs BEFORE admission and is discarded if admission
    refuses, so it must leave the caller's metadata untouched - the frozen
    request goes on to carry that same mapping.
    """
    metadata = dict(FULL_METADATA)
    family.build_start_plan(submitter=submitter, metadata=metadata)
    assert metadata == FULL_METADATA


@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_planning_is_deterministic(family, submitter):
    """Same inputs, same plan - admission must not depend on read timing."""
    first = family.build_start_plan(submitter=submitter, metadata=FULL_METADATA)
    second = family.build_start_plan(submitter=submitter, metadata=FULL_METADATA)
    assert first == second


# --------------------------------------------------------------------------
# Proportionality - what each family claims, and what it refuses to claim
# --------------------------------------------------------------------------

def test_checkpoint_load_takes_the_world_and_nothing_else(submitter):
    """
    Whole-world exclusivity already excludes every other claim, so naming
    further scopes would be noise rather than isolation.
    """
    plan = CheckpointLoadTransactionStrategy.build_start_plan(
        submitter=submitter, metadata={"target_frame_name": "ignored"}
    )
    assert plan == {ScopeKey.world(): ClaimMode.EXCLUSIVE}


def test_formation_load_is_frame_scoped_under_a_world_intent_marker(submitter):
    """The parent/child pair that makes cross-frame restores parallel."""
    plan = FormationLoadTransactionStrategy.build_start_plan(
        submitter=submitter, metadata={"target_frame_name": "A"}
    )
    assert plan == {
        ScopeKey.world(): ClaimMode.INTENT,
        ScopeKey.frame("A"): ClaimMode.EXCLUSIVE,
    }


def test_index_graft_marks_the_frame_with_intent_not_exclusive(submitter):
    """
    A graft touches one book, not the frame. Exclusive here would serialise
    every graft in a frame against every other - the over-claim the strategy
    contract warns about.
    """
    plan = IndexGraftTransactionStrategy.build_start_plan(
        submitter=submitter, metadata={"host_frame_name": "A"}
    )
    assert plan[ScopeKey.frame("A")] is ClaimMode.INTENT


@pytest.mark.parametrize(
    "family",
    [SubsystemEnableTransactionStrategy, SubsystemDisableTransactionStrategy],
)
def test_subsystem_transitions_claim_the_subsystem_exclusively(family, submitter):
    """Enable and disable write the same surface, so they claim identically."""
    plan = family.build_start_plan(
        submitter=submitter, metadata={"subsystem_name": "crystallizer"}
    )
    assert plan == {
        ScopeKey.world(): ClaimMode.INTENT,
        ScopeKey.subsystem("crystallizer"): ClaimMode.EXCLUSIVE,
    }


@pytest.mark.parametrize(
    "family,key",
    [
        (FormationLoadTransactionStrategy, "target_frame_name"),
        (FrameCreateTransactionStrategy, "frame_name"),
        (IndexGraftTransactionStrategy, "host_frame_name"),
        (SubsystemEnableTransactionStrategy, "subsystem_name"),
        (SubsystemDisableTransactionStrategy, "subsystem_name"),
    ],
)
@pytest.mark.parametrize("bad_value", [None, "", 123, [], {}])
def test_unknown_target_degrades_to_whole_world(family, key, bad_value, submitter):
    """
    UNKNOWN REACH TAKES THE LARGEST CLAIM. Planning is pure and runs once before
    admission, so a guessed target that is wrong would isolate the wrong surface
    and admit a genuine conflict. Briefly coarse is the safe error.

    A malformed value is treated as ABSENT rather than raising: planning is not
    payload validation, and refusing would turn a metadata typo into a failed
    restore.
    """
    plan = family.build_start_plan(submitter=submitter, metadata={key: bad_value})
    assert plan == {ScopeKey.world(): ClaimMode.EXCLUSIVE}


# --------------------------------------------------------------------------
# agent_repair - the only family whose claim set is supplied, not derived
# --------------------------------------------------------------------------

def test_repair_claims_exactly_the_scopes_it_is_given(submitter):
    """A repair re-takes the surface a broken transaction left behind."""
    plan = AgentRepairTransactionStrategy.build_start_plan(
        submitter=submitter,
        metadata={"repair_scopes": [ScopeKey.frame("A"), ScopeKey.subsystem("nexus")]},
    )
    assert plan == {
        ScopeKey.world(): ClaimMode.INTENT,
        ScopeKey.frame("A"): ClaimMode.EXCLUSIVE,
        ScopeKey.subsystem("nexus"): ClaimMode.EXCLUSIVE,
    }


def test_repair_drops_malformed_entries_and_deduplicates(submitter):
    """
    One bad entry must not refuse a repair of an already-damaged world, and a
    repeated key must not make the plan depend on how often it was listed.
    """
    plan = AgentRepairTransactionStrategy.build_start_plan(
        submitter=submitter,
        metadata={"repair_scopes": [
            ScopeKey.frame("A"), ScopeKey.frame("A"), "", None, 7, ScopeKey.frame("A"),
        ]},
    )
    assert plan == {
        ScopeKey.world(): ClaimMode.INTENT,
        ScopeKey.frame("A"): ClaimMode.EXCLUSIVE,
    }


def test_repair_refuses_to_iterate_a_bare_string(submitter):
    """
    Iterating a bare string would claim one scope PER CHARACTER - quiet nonsense
    a claim planner must never produce. It degrades to the fallback instead.
    """
    plan = AgentRepairTransactionStrategy.build_start_plan(
        submitter=submitter, metadata={"repair_scopes": ScopeKey.frame("A")}
    )
    assert plan == {ScopeKey.world(): ClaimMode.EXCLUSIVE}


@pytest.mark.parametrize("candidate", [None, [], (), 42])
def test_repair_with_no_usable_scopes_takes_the_world(candidate, submitter):
    """
    An agent that cannot say what it is repairing is about to touch an unknown
    part of a world already known to be broken. The only safe claim for
    unbounded reach into damaged state is all of it.
    """
    plan = AgentRepairTransactionStrategy.build_start_plan(
        submitter=submitter, metadata={"repair_scopes": candidate}
    )
    assert plan == {ScopeKey.world(): ClaimMode.EXCLUSIVE}


# --------------------------------------------------------------------------
# Isolation - asserted through the REAL claim table, not a reimplementation
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "first,second,expect_blocked,why",
    [
        ("ckpt", "form_a", True,
         "world exclusive excludes the world intent marker"),
        ("form_a", "form_b", False,
         "PARALLELISM: disjoint frames are why frame scope exists"),
        ("form_a", "form_a2", True,
         "same frame, both exclusive"),
        ("graft_a", "graft_a2", False,
         "DOCUMENTED GAP: two grafts into one frame both hold intent"),
        ("graft_a", "form_a", True,
         "frame intent is excluded by frame exclusive"),
        ("graft_a", "form_b", False,
         "different frames stay parallel"),
        ("ckpt", "graft_a", True,
         "world exclusive excludes everything"),
        ("en_c", "en_n", False,
         "disjoint subsystems enable in parallel"),
        ("en_c", "form_a", False,
         "subsystem and frame scopes are orthogonal"),
        ("en_c", "ckpt", True,
         "a whole-world replay must not run mid-activation"),
        ("en_c", "dis_c", True,
         "enable and disable of one subsystem must serialise"),
        ("repair_a", "form_a", True,
         "repair holds the frame exclusively"),
    ],
)
def test_isolation_holds_on_a_real_claim_table(
        first, second, expect_blocked, why, submitter, table
):
    """
    Each case states the OPERATIONAL claim in `why`; the assertion proves a real
    `ClaimTable` delivers it. Acquisition order is fixed - `first` is granted,
    then `second` is attempted - so the result is the table's own verdict.
    """
    plans = {
        "ckpt": CheckpointLoadTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={}),
        "form_a": FormationLoadTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"target_frame_name": "A"}),
        "form_a2": FormationLoadTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"target_frame_name": "A"}),
        "form_b": FormationLoadTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"target_frame_name": "B"}),
        "graft_a": IndexGraftTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"host_frame_name": "A"}),
        "graft_a2": IndexGraftTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"host_frame_name": "A"}),
        "en_c": SubsystemEnableTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"subsystem_name": "crystallizer"}),
        "en_n": SubsystemEnableTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"subsystem_name": "nexus"}),
        "dis_c": SubsystemDisableTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"subsystem_name": "crystallizer"}),
        "repair_a": AgentRepairTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"repair_scopes": [ScopeKey.frame("A")]}),
    }
    blocked = _blocks_second_holder(table, plans[first], plans[second])
    assert blocked is expect_blocked, why


def test_blocking_evidence_names_the_contended_scope(submitter, table):
    """
    A refusal must be actionable, not a bare False - the blocked caller has to
    be able to say WHICH scope it lost and to whom.
    """
    one = Identity(kind="crystallizer", identity_id="holder-one")
    two = Identity(kind="crystallizer", identity_id="holder-two")
    try:
        held = FormationLoadTransactionStrategy.build_start_plan(
            submitter=submitter, metadata={"target_frame_name": "A"}
        )
        assert table.try_acquire(one, held) == ()
        blocks = table.try_acquire(two, held)
        try:
            assert blocks, "an overlapping claim must produce evidence"
            assert ScopeKey.frame("A") in {block.scope_key for block in blocks}
        finally:
            for block in blocks:
                block.cleanup()
    finally:
        table.release_holder(one)
        table.release_holder(two)
        one.cleanup()
        two.cleanup()


# --------------------------------------------------------------------------
# Jurisdiction - the boundary this plane must not cross
# --------------------------------------------------------------------------

@pytest.mark.parametrize("family", DERIVED_FAMILIES)
def test_no_derived_family_claims_inside_a_frame(family, submitter):
    """
    Anything INSIDE a frame belongs to that frame's own `ChangeControlManager`,
    which has its own claim table. This plane claims `frame:<name>` as ONE UNIT
    and never reaches past it - book or conduit keys would put two planes on one
    vocabulary with no arbiter between them.
    """
    plan = family.build_start_plan(submitter=submitter, metadata=FULL_METADATA)
    forbidden = ("spellbook:", "conduit:", "spell_index:", "ward:")
    for scope_key in plan:
        assert not scope_key.startswith(forbidden), (
            "{0!r} reaches inside a frame".format(scope_key)
        )
