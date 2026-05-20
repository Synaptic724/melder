from __future__ import annotations

from types import SimpleNamespace

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
    OccurrencePlan,
    OccurrencePlanBuilder,
    OccurrencePlanSelection,
    select_occurrence_plan,
)


def _make_plan() -> OccurrencePlan:
    """
    Purpose:
        Build a minimal concrete OccurrencePlan for direct object-layer tests.
    Contract:
        - Uses non-empty containers so cleanup effects are observable.
    """

    return OccurrencePlan(
        root_spell_id="root",
        occurrence_graph={("root", 0): {"dep": [("dep", 1)]}, ("dep", 1): {}},
        execution_order=["dep", "root"],
        instance_keys_by_spell_id={"root": [("root", None)], "dep": [("dep", None)]},
        canonical_occurrences_by_spell_id={"root": ("root", 0), "dep": ("dep", 1)},
        root_instance_key=("root", None),
        shared_spell_ids={"root", "dep"},
        contract_overrides_by_occurrence={("dep", 1): {"value": "override"}},
        contract_overrides_by_spell_id={"dep": [(("dep", 1), {"value": "override"})]},
        contract_dependencies_complete=True,
        path_registry=SimpleNamespace(root_path_id=0),
    )


def test_select_occurrence_plan_handles_none_and_returns_runtime_selection() -> None:
    """
    Purpose:
        Validate the top-level Phase 8 selection helper.
    Contract:
        - None plans return None.
        - Concrete plans produce an OccurrencePlanSelection wrapper.
        - Selection fields mirror the underlying plan object.
    """

    assert select_occurrence_plan(None, root_spell_id="root") is None

    plan = _make_plan()
    try:
        selection = select_occurrence_plan(plan, root_spell_id="root")

        assert isinstance(selection, OccurrencePlanSelection)
        assert selection.occurrence_graph is plan.occurrence_graph
        assert selection.execution_order is plan.execution_order
        assert selection.instance_keys_by_spell_id is plan.instance_keys_by_spell_id
        assert selection.canonical_occurrences_by_spell_id is plan.canonical_occurrences_by_spell_id
        assert selection.root_instance_key == ("root", None)
        assert selection.shared_spell_ids is plan.shared_spell_ids
        assert selection.contract_overrides_by_occurrence is plan.contract_overrides_by_occurrence
        assert selection.contract_overrides_by_spell_id is plan.contract_overrides_by_spell_id
    finally:
        plan.cleanup()


def test_occurrence_plan_properties_cleanup_and_constructor_validation() -> None:
    """
    Purpose:
        Validate the direct OccurrencePlan object contract.
    Contract:
        - Properties expose stored runtime metadata before cleanup.
        - cleanup clears owned containers and future property access fails.
        - Constructor rejects missing required inputs.
    """

    plan = _make_plan()
    occurrence_graph = plan.occurrence_graph
    execution_order = plan.execution_order
    shared_spell_ids = plan.shared_spell_ids
    overrides_by_occurrence = plan.contract_overrides_by_occurrence
    overrides_by_spell_id = plan.contract_overrides_by_spell_id

    assert plan.root_spell_id == "root"
    assert plan.root_instance_key == ("root", None)
    assert plan.instance_keys_by_spell_id == {"root": [("root", None)], "dep": [("dep", None)]}
    assert plan.canonical_occurrences_by_spell_id == {"root": ("root", 0), "dep": ("dep", 1)}
    assert plan.contract_dependencies_complete is True
    assert plan.path_registry.root_path_id == 0

    plan.cleanup()

    assert occurrence_graph == {}
    assert execution_order == []
    assert shared_spell_ids == set()
    assert overrides_by_occurrence == {}
    assert overrides_by_spell_id == {}

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        _ = plan.root_spell_id

    plan.cleanup()

    with pytest.raises(ValueError, match="root_spell_id must not be None"):
        OccurrencePlan(  # type: ignore[arg-type]
            root_spell_id=None,
            occurrence_graph={},
            execution_order=[],
            instance_keys_by_spell_id={},
            canonical_occurrences_by_spell_id={},
            root_instance_key=("root", None),
            shared_spell_ids=set(),
            contract_overrides_by_occurrence={},
            contract_overrides_by_spell_id={},
            contract_dependencies_complete=True,
            path_registry=SimpleNamespace(root_path_id=0),
        )

    with pytest.raises(ValueError, match="occurrence_graph must not be None"):
        OccurrencePlan(  # type: ignore[arg-type]
            root_spell_id="root",
            occurrence_graph=None,
            execution_order=[],
            instance_keys_by_spell_id={},
            canonical_occurrences_by_spell_id={},
            root_instance_key=("root", None),
            shared_spell_ids=set(),
            contract_overrides_by_occurrence={},
            contract_overrides_by_spell_id={},
            contract_dependencies_complete=True,
            path_registry=SimpleNamespace(root_path_id=0),
        )


def test_occurrence_plan_builder_validates_required_inputs_and_selection_helpers() -> None:
    """
    Purpose:
        Validate the remaining direct helper contracts on OccurrencePlanBuilder.
    Contract:
        - Builder rejects missing required inputs.
        - Shared existences are non-many; many remains non-shared.
        - Canonical occurrence selection is stable and smallest-first.
        - Instance key routing respects shared vs many existences.
    """

    with pytest.raises(ValueError, match="root_spell must not be None"):
        OccurrencePlanBuilder(  # type: ignore[arg-type]
            root_spell=None,
            blueprint=SimpleNamespace(path_registry=SimpleNamespace(root_path_id=0)),
            spell_lookup={},
            system_states=None,
        )

    with pytest.raises(ValueError, match="blueprint must not be None"):
        OccurrencePlanBuilder(  # type: ignore[arg-type]
            root_spell=SimpleNamespace(),
            blueprint=None,
            spell_lookup={},
            system_states=None,
        )

    shared_spell = SimpleNamespace(existence=Existence.unique)
    many_spell = SimpleNamespace(existence=Existence.many)

    builder = OccurrencePlanBuilder(
        root_spell=SimpleNamespace(
            spell_index=SimpleNamespace(current="root"),
            spell_name="Root",
            existence=Existence.unique,
        ),
        blueprint=SimpleNamespace(path_registry=SimpleNamespace(root_path_id=0)),
        spell_lookup={"shared": shared_spell, "many": many_spell},
        system_states=None,
    )

    assert builder._is_shared_existence(Existence.unique) is True
    assert builder._is_shared_existence(Existence.many) is False
    assert builder._select_canonical_occurrence((("spell", 7), ("spell", 2), ("spell", 5))) == (
        "spell",
        2,
    )
    assert builder._instance_key_for_occurrence(("shared", 7)) == ("shared", None)
    assert builder._instance_key_for_occurrence(("many", 7)) == ("many", 7)

    builder.cleanup()

    with pytest.raises(RuntimeError, match="OccurrencePlanBuilder has already been cleaned"):
        builder._should_collapse_shared_occurrences()

    builder.cleanup()
