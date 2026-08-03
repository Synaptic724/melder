"""
Unit tests for the plane's six transaction families.

WHY THIS FILE EXISTS: the strategies were written and verified by loading the
package's modules in isolation on a Python 3.10 sandbox with `StrEnum` and
`Cleanable` SUBSTITUTED, because that sandbox cannot obtain a 3.14t interpreter.
That proved the claim arithmetic and nothing about the shipped wiring. These
tests run on the repo's own interpreter against the REAL vocabulary, which is
the gap they close.

WHAT IS ACTUALLY BEING TESTED: not "does the method return a dict" but the two
properties the plane exists to provide -

    PROPORTIONALITY  a family claims what its operation reaches, and no more.
    ISOLATION        the claims two families produce conflict exactly when the
                     operations genuinely conflict.

The second is checked through `ClaimCompatibility` rather than by eyeballing the
modes, because that matrix is the thing admission actually consults.

Run:
    pytest tests/unit/melder/aether/aetheric_mediator -q
"""

import pytest

from melder.aether.aetheric_mediator.claim_mode import ClaimCompatibility, ClaimMode
from melder.aether.aetheric_mediator.scope_keys import ScopeKey
from melder.aether.aetheric_mediator.strategies import (
    AgentRepairTransactionStrategy,
    CheckpointLoadTransactionStrategy,
    FormationLoadTransactionStrategy,
    IndexGraftTransactionStrategy,
    SubsystemDisableTransactionStrategy,
    SubsystemEnableTransactionStrategy,
)
from melder.aether.aetheric_mediator.transaction_strategy import TransactionStrategy

ALL_FAMILIES = (
    AgentRepairTransactionStrategy,
    CheckpointLoadTransactionStrategy,
    FormationLoadTransactionStrategy,
    IndexGraftTransactionStrategy,
    SubsystemDisableTransactionStrategy,
    SubsystemEnableTransactionStrategy,
)


def _plans_conflict(first, second) -> bool:
    """
    Report whether two claim plans could not both be held.

    This mirrors what the claim table does on acquisition: a conflict exists
    when the two plans name a common scope whose modes are incompatible.
    Disjoint scopes never conflict, which is the entire basis of the plane's
    parallelism.
    """
    for scope_key, held in first.items():
        if scope_key in second and not ClaimCompatibility.permits(
                held=held, requested=second[scope_key]
        ):
            return True
    return False


# --------------------------------------------------------------------------
# Contract shape
# --------------------------------------------------------------------------

@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_families_are_classes_with_no_instance_state(family):
    """
    Registered as CLASSES, never instances - the contract forbids per-strategy
    state so concurrency lives entirely in the mediator and its claims.
    """
    assert isinstance(family, type)
    assert issubclass(family, TransactionStrategy)


@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_every_plan_is_complete_and_typed(family):
    """
    The plane has NO implicit default mode, so every key a family emits must
    carry an explicit `ClaimMode`. A plain string would be silently unusable.
    """
    plan = family.build_start_plan(submitter=None, metadata={})
    assert plan, "a family that claims nothing would isolate nothing"
    for scope_key, mode in plan.items():
        assert isinstance(scope_key, str) and scope_key
        assert isinstance(mode, ClaimMode)


@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_build_start_plan_is_pure(family):
    """
    `build_start_plan` runs BEFORE admission and is discarded if admission
    refuses, so it must not mutate its inputs. It is also called with the same
    metadata the frozen request will carry.
    """
    metadata = {"target_frame_name": "A", "host_frame_name": "A",
                "subsystem_name": "crystallizer", "repair_scopes": ["frame:A"]}
    before = dict(metadata)
    first = family.build_start_plan(submitter=None, metadata=metadata)
    second = family.build_start_plan(submitter=None, metadata=metadata)
    assert metadata == before, "metadata was mutated by planning"
    assert first == second, "planning is not deterministic"


# --------------------------------------------------------------------------
# Proportionality - what each family claims, and what it refuses to claim
# --------------------------------------------------------------------------

def test_checkpoint_load_takes_the_world_and_nothing_else():
    """
    Whole-world exclusivity already excludes every other claim, so naming
    additional scopes would be noise rather than isolation.
    """
    plan = CheckpointLoadTransactionStrategy.build_start_plan(
        submitter=None, metadata={"target_frame_name": "ignored"}
    )
    assert plan == {ScopeKey.world(): ClaimMode.EXCLUSIVE}


def test_formation_load_is_frame_scoped_under_a_world_intent_marker():
    """The parent/child pair that makes cross-frame restores parallel."""
    plan = FormationLoadTransactionStrategy.build_start_plan(
        submitter=None, metadata={"target_frame_name": "A"}
    )
    assert plan == {
        ScopeKey.world(): ClaimMode.INTENT,
        ScopeKey.frame("A"): ClaimMode.EXCLUSIVE,
    }


def test_index_graft_marks_the_frame_with_intent_not_exclusive():
    """
    A graft does not own the frame it works in - it touches one book. Exclusive
    here would serialise every graft in a frame against every other, which is
    the over-claim the strategy contract warns about.
    """
    plan = IndexGraftTransactionStrategy.build_start_plan(
        submitter=None, metadata={"host_frame_name": "A"}
    )
    assert plan[ScopeKey.frame("A")] is ClaimMode.INTENT


@pytest.mark.parametrize(
    "family",
    [SubsystemEnableTransactionStrategy, SubsystemDisableTransactionStrategy],
)
def test_subsystem_transitions_claim_the_subsystem_exclusively(family):
    """Enable and disable write the same surface, so they claim identically."""
    plan = family.build_start_plan(
        submitter=None, metadata={"subsystem_name": "crystallizer"}
    )
    assert plan == {
        ScopeKey.world(): ClaimMode.INTENT,
        ScopeKey.subsystem("crystallizer"): ClaimMode.EXCLUSIVE,
    }


@pytest.mark.parametrize(
    "family,key",
    [
        (FormationLoadTransactionStrategy, "target_frame_name"),
        (IndexGraftTransactionStrategy, "host_frame_name"),
        (SubsystemEnableTransactionStrategy, "subsystem_name"),
        (SubsystemDisableTransactionStrategy, "subsystem_name"),
    ],
)
@pytest.mark.parametrize("bad_value", [None, "", 123, [], {}])
def test_unknown_target_degrades_to_whole_world(family, key, bad_value):
    """
    UNKNOWN REACH TAKES THE LARGEST CLAIM. Planning is pure and runs once before
    admission, so a guessed target that is wrong would isolate the wrong surface
    and admit a genuine conflict. Being briefly coarse is the safe error.

    A malformed value is treated as ABSENT rather than raising: planning is not
    payload validation, and refusing here would turn a metadata typo into a
    failed restore.
    """
    plan = family.build_start_plan(submitter=None, metadata={key: bad_value})
    assert plan == {ScopeKey.world(): ClaimMode.EXCLUSIVE}


# --------------------------------------------------------------------------
# agent_repair - the only family whose claim set is supplied, not derived
# --------------------------------------------------------------------------

def test_repair_claims_exactly_the_scopes_it_is_given():
    """A repair re-takes the surface a broken transaction left behind."""
    plan = AgentRepairTransactionStrategy.build_start_plan(
        submitter=None,
        metadata={"repair_scopes": [ScopeKey.frame("A"), ScopeKey.subsystem("nexus")]},
    )
    assert plan == {
        ScopeKey.world(): ClaimMode.INTENT,
        ScopeKey.frame("A"): ClaimMode.EXCLUSIVE,
        ScopeKey.subsystem("nexus"): ClaimMode.EXCLUSIVE,
    }


def test_repair_drops_malformed_entries_and_deduplicates():
    """
    One bad entry must not refuse a repair of an already-damaged world, and a
    repeated key must not make the plan depend on how many times it was listed.
    """
    plan = AgentRepairTransactionStrategy.build_start_plan(
        submitter=None,
        metadata={"repair_scopes": [
            ScopeKey.frame("A"), ScopeKey.frame("A"), "", None, 7, ScopeKey.frame("A"),
        ]},
    )
    assert plan == {
        ScopeKey.world(): ClaimMode.INTENT,
        ScopeKey.frame("A"): ClaimMode.EXCLUSIVE,
    }


def test_repair_refuses_to_iterate_a_bare_string():
    """
    Iterating a bare string would claim one scope PER CHARACTER - the kind of
    quiet nonsense a claim planner must never produce. It degrades to the
    whole-world fallback instead.
    """
    plan = AgentRepairTransactionStrategy.build_start_plan(
        submitter=None, metadata={"repair_scopes": ScopeKey.frame("A")}
    )
    assert plan == {ScopeKey.world(): ClaimMode.EXCLUSIVE}


@pytest.mark.parametrize("candidate", [None, [], (), 42, object()])
def test_repair_with_no_usable_scopes_takes_the_world(candidate):
    """
    An agent that cannot say what it is repairing is about to touch an unknown
    part of a world already known to be broken. The only safe claim for
    unbounded reach into damaged state is all of it.
    """
    plan = AgentRepairTransactionStrategy.build_start_plan(
        submitter=None, metadata={"repair_scopes": candidate}
    )
    assert plan == {ScopeKey.world(): ClaimMode.EXCLUSIVE}


# --------------------------------------------------------------------------
# Isolation - the property the plane exists for, checked through the matrix
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "first,second,expect_conflict,why",
    [
        ("ckpt", "form_a", True,
         "world exclusive excludes the world intent marker"),
        ("form_a", "form_b", False,
         "PARALLELISM: disjoint frames are the reason frame scope exists"),
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
def test_isolation_matches_the_matrix(first, second, expect_conflict, why):
    """
    Each case states the OPERATIONAL claim in `why`; the assertion proves the
    claim arithmetic actually delivers it.
    """
    plans = {
        "ckpt": CheckpointLoadTransactionStrategy.build_start_plan(
            submitter=None, metadata={}),
        "form_a": FormationLoadTransactionStrategy.build_start_plan(
            submitter=None, metadata={"target_frame_name": "A"}),
        "form_a2": FormationLoadTransactionStrategy.build_start_plan(
            submitter=None, metadata={"target_frame_name": "A"}),
        "form_b": FormationLoadTransactionStrategy.build_start_plan(
            submitter=None, metadata={"target_frame_name": "B"}),
        "graft_a": IndexGraftTransactionStrategy.build_start_plan(
            submitter=None, metadata={"host_frame_name": "A"}),
        "graft_a2": IndexGraftTransactionStrategy.build_start_plan(
            submitter=None, metadata={"host_frame_name": "A"}),
        "en_c": SubsystemEnableTransactionStrategy.build_start_plan(
            submitter=None, metadata={"subsystem_name": "crystallizer"}),
        "en_n": SubsystemEnableTransactionStrategy.build_start_plan(
            submitter=None, metadata={"subsystem_name": "nexus"}),
        "dis_c": SubsystemDisableTransactionStrategy.build_start_plan(
            submitter=None, metadata={"subsystem_name": "crystallizer"}),
        "repair_a": AgentRepairTransactionStrategy.build_start_plan(
            submitter=None, metadata={"repair_scopes": [ScopeKey.frame("A")]}),
    }
    assert _plans_conflict(plans[first], plans[second]) is expect_conflict, why


# --------------------------------------------------------------------------
# Jurisdiction - the boundary this plane must not cross
# --------------------------------------------------------------------------

@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_no_family_claims_inside_a_frame(family):
    """
    Anything INSIDE a frame belongs to that frame's own `ChangeControlManager`,
    which has its own claim table. This plane claims `frame:<name>` as ONE UNIT
    and never reaches past it - claiming book or conduit keys would put two
    planes on one vocabulary with no arbiter between them.

    The `agent_repair` family is exempted from the scope-key check because its
    set is caller-supplied by design; a caller passing frame-internal keys is
    asking the wrong plane, which its own docstring records.
    """
    if family is AgentRepairTransactionStrategy:
        pytest.skip("claim set is caller-supplied by contract")
    metadata = {"target_frame_name": "A", "host_frame_name": "A",
                "subsystem_name": "crystallizer"}
    plan = family.build_start_plan(submitter=None, metadata=metadata)
    forbidden = ("spellbook:", "conduit:", "spell_index:", "ward:")
    for scope_key in plan:
        assert not scope_key.startswith(forbidden), (
            "{0!r} reaches inside a frame".format(scope_key)
        )
