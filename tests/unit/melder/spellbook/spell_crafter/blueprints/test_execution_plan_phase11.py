"""Unit tests for Phase 11 execution plan artifacts."""
from typing import Dict, Optional

import pytest

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
    ExecutionPlanBuilder,
    ExecutionPlanStep,
)
from melder.spellbook.spell_crafter.blueprints.injection_plan import InjectionPlan
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import OccurrencePlan
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import InstanceKey


class _SpellStub:
    """
    Spell stub used for execution plan builder tests.
    """

    def __init__(self, *, spell_id: str, existence: Existence) -> None:
        """
        Initialize the stub with an existence policy.
        """
        self.spell_id = spell_id
        self.existence = existence
        self.has_disposal_methods = False


def _make_occurrence_plan(
    *,
    root_id: str,
    instance_keys_by_spell_id: Dict[str, list[InstanceKey]],
    canonical_occurrences_by_spell_id: Dict[str, tuple[str, tuple[str, ...]]],
) -> OccurrencePlan:
    """
    Build a minimal OccurrencePlan for testing.
    """
    return OccurrencePlan(
        root_spell_id=root_id,
        occurrence_graph={},
        execution_order=list(instance_keys_by_spell_id.keys()),
        instance_keys_by_spell_id=instance_keys_by_spell_id,
        canonical_occurrences_by_spell_id=canonical_occurrences_by_spell_id,
        root_instance_key=(root_id, None),
        shared_spell_ids=set(),
        contract_overrides_by_occurrence={},
        contract_overrides_by_spell_id={},
        contract_dependencies_complete=True,
    )


@pytest.mark.parametrize(
    "field_name,field_value",
    [
        ("spell_id", None),
        ("instance_key", None),
        ("occurrence", None),
        ("existence", None),
        ("creation_target", None),
        ("action", None),
        ("register", None),
    ],
)
def test_execution_plan_step_requires_fields(field_name: str, field_value: Optional[object]) -> None:
    """
    Purpose:
        Ensure ExecutionPlanStep validates required fields.
    Contract:
        - Missing required inputs raise ValueError.
    """
    kwargs = {
        "spell_id": "root",
        "instance_key": ("root", None),
        "occurrence": ("root", ()),
        "existence": Existence.unique,
        "creation_target": "owner",
        "action": "reuse",
        "inject_spec": None,
        "register": True,
    }
    kwargs[field_name] = field_value
    with pytest.raises(ValueError):
        ExecutionPlanStep(**kwargs)


def test_execution_plan_cleanup_clears_steps() -> None:
    """
    Purpose:
        Verify cleanup clears owned step list.
    Contract:
        - cleanup clears steps and marks plan as cleaned.
    """
    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[
            ExecutionPlanStep(
                spell_id="root",
                instance_key=("root", None),
                occurrence=("root", ()),
                existence=Existence.unique,
                creation_target="owner",
                action="reuse",
                inject_spec=None,
                register=True,
            )
        ],
    )

    plan.cleanup()

    assert plan.steps == []


@pytest.mark.parametrize(
    "existence,expected_action",
    [
        (Existence.many, "construct"),
        (Existence.unique, "reuse"),
        (Existence.unique_per_conduit, "reuse"),
    ],
)
def test_execution_plan_builder_action_for_existence(
    existence: Existence,
    expected_action: str,
) -> None:
    """
    Purpose:
        Ensure action selection aligns with existence policies.
    Contract:
        - Existence.many uses construct; others use reuse.
    """
    plan = _make_occurrence_plan(
        root_id="root",
        instance_keys_by_spell_id={"root": [("root", None)]},
        canonical_occurrences_by_spell_id={"root": ("root", ())},
    )
    builder = ExecutionPlanBuilder(
        occurrence_plan=plan,
        injection_plan=None,
        spell_lookup={"root": _SpellStub(spell_id="root", existence=existence)},
    )
    execution_plan = builder.build()

    assert execution_plan.steps[0].action == expected_action


@pytest.mark.parametrize(
    "existence,expected_target",
    [
        (Existence.unique_per_conduit, "caller"),
        (Existence.unique_per_spell_space, "spellspace"),
        (Existence.many, "caller"),
        (Existence.unique, "owner"),
    ],
)
def test_execution_plan_builder_creation_target_for_existence(
    existence: Existence,
    expected_target: str,
) -> None:
    """
    Purpose:
        Ensure creation targets are derived from existence policies.
    Contract:
        - unique_per_conduit -> caller, unique_per_spell_space -> spellspace,
          many -> caller, otherwise owner.
    """
    plan = _make_occurrence_plan(
        root_id="root",
        instance_keys_by_spell_id={"root": [("root", None)]},
        canonical_occurrences_by_spell_id={"root": ("root", ())},
    )
    builder = ExecutionPlanBuilder(
        occurrence_plan=plan,
        injection_plan=None,
        spell_lookup={"root": _SpellStub(spell_id="root", existence=existence)},
    )
    execution_plan = builder.build()

    assert execution_plan.steps[0].creation_target == expected_target


def test_execution_plan_builder_requires_canonical_occurrence() -> None:
    """
    Purpose:
        Ensure shared instance keys require canonical occurrences.
    Contract:
        - Missing canonical occurrence raises ValueError.
    """
    plan = _make_occurrence_plan(
        root_id="root",
        instance_keys_by_spell_id={"root": [("root", None)]},
        canonical_occurrences_by_spell_id={},
    )
    builder = ExecutionPlanBuilder(
        occurrence_plan=plan,
        injection_plan=None,
        spell_lookup={"root": _SpellStub(spell_id="root", existence=Existence.unique)},
    )

    with pytest.raises(ValueError):
        builder.build()


def test_execution_plan_builder_records_occurrence_path() -> None:
    """
    Purpose:
        Ensure ExecutionPlanStep stores the canonical occurrence.
    Contract:
        - Steps expose the canonical occurrence for shared instances.
    """
    plan = _make_occurrence_plan(
        root_id="root",
        instance_keys_by_spell_id={"root": [("root", None)]},
        canonical_occurrences_by_spell_id={"root": ("root", ("p",))},
    )
    builder = ExecutionPlanBuilder(
        occurrence_plan=plan,
        injection_plan=None,
        spell_lookup={"root": _SpellStub(spell_id="root", existence=Existence.unique)},
    )
    execution_plan = builder.build()

    assert execution_plan.steps[0].occurrence == ("root", ("p",))


def test_execution_plan_builder_rejects_mismatched_injection_plan() -> None:
    """
    Purpose:
        Ensure execution plan builder validates injection plan root id.
    Contract:
        - Root mismatch raises ValueError.
    """
    plan = _make_occurrence_plan(
        root_id="root",
        instance_keys_by_spell_id={"root": [("root", None)]},
        canonical_occurrences_by_spell_id={"root": ("root", ())},
    )
    injection_plan = InjectionPlan(root_spell_id="other", instance_injections={})
    builder = ExecutionPlanBuilder(
        occurrence_plan=plan,
        injection_plan=injection_plan,
        spell_lookup={"root": _SpellStub(spell_id="root", existence=Existence.unique)},
    )

    with pytest.raises(ValueError):
        builder.build()
