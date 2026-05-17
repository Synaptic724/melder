from __future__ import annotations

from typing import Tuple

import pytest

from melder.spellbook.spell_crafter.blueprints.patch_maps import (
    MutationEdgePatch,
    MutationPatchMap,
    OverridePatchMap,
    PatchMapBuilder,
    _Specificity,
    apply_mutation_patch_map,
    apply_override_patch_map,
    apply_phase10_mutation_overrides,
    apply_phase10_override_payload,
)
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, PathRegistry, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _build_blueprint() -> Tuple[RootResolutionBlueprint, SocketRef, SocketRef]:
    """
    Purpose:
        Build a minimal rooted blueprint with one normal socket and one mutation socket.
    Contract:
        - The blueprint carries deterministic path ids and socket refs.
        - The DAG contains one existing service dependency for the normal socket.
    """

    dag = DirectedAcyclicWorkGraph()
    dag.add_dependency(
        parent_key="service-id",
        child_key="consumer-id",
        param_name="service",
        socket_kind=SocketKind.NORMAL,
    )

    path_registry = PathRegistry()
    service_path_id = path_registry.extend_path(path_registry.root_path_id, "service")
    mutation_path_id = path_registry.extend_path(path_registry.root_path_id, "mutation")

    service_ref = SocketRef(
        node_id="consumer-id",
        param_name="service",
        param_path_id=service_path_id,
        socket_kind=SocketKind.NORMAL,
    )
    mutation_ref = SocketRef(
        node_id="consumer-id",
        param_name="mutation",
        param_path_id=mutation_path_id,
        socket_kind=SocketKind.MUTATION_CONTRACT,
    )

    dag_index = DagIndex(path_registry=path_registry)
    dag_index.add_socket(service_ref)
    dag_index.add_socket(mutation_ref)

    blueprint = RootResolutionBlueprint(
        root_spell_id="consumer-id",
        root_lineage_id="lineage:consumer-id",
        dag=dag,
        ordered_node_ids=("service-id", "consumer-id"),
        socket_refs=(service_ref, mutation_ref),
        dag_index=dag_index,
    )
    return blueprint, service_ref, mutation_ref


def test_override_patch_map_validation_cleanup_and_specificity_conflicts() -> None:
    """
    Purpose:
        Validate the direct OverridePatchMap object contract.
    Contract:
        - Constructor rejects missing required inputs.
        - cleanup clears owned collections and later property access fails.
        - competing matches on the same socket with the same specificity raise.
    """

    _, service_ref, _ = _build_blueprint()

    with pytest.raises(ValueError, match="root_spell_id must not be None"):
        OverridePatchMap(  # type: ignore[arg-type]
            root_spell_id=None,
            targets_by_spec={},
            specificity_by_spec={},
        )

    with pytest.raises(ValueError, match="targets_by_spec must not be None"):
        OverridePatchMap(  # type: ignore[arg-type]
            root_spell_id="consumer-id",
            targets_by_spec=None,
            specificity_by_spec={},
        )

    with pytest.raises(ValueError, match="specificity_by_spec must not be None"):
        OverridePatchMap(  # type: ignore[arg-type]
            root_spell_id="consumer-id",
            targets_by_spec={},
            specificity_by_spec=None,
        )

    patch_map = OverridePatchMap(
        root_spell_id="consumer-id",
        targets_by_spec={
            "*service": [service_ref],
            "*alias": [service_ref],
        },
        specificity_by_spec={
            "*service": _Specificity.UNIQUE,
            "*alias": _Specificity.UNIQUE,
        },
    )

    assert patch_map.root_spell_id == "consumer-id"

    with pytest.raises(RuntimeError, match="same specificity"):
        patch_map.apply(
            {
                "*service": "left",
                "*alias": "right",
            }
        )

    patch_map.cleanup()

    with pytest.raises(RuntimeError, match="has already been cleaned"):
        _ = patch_map.root_spell_id

    patch_map.cleanup()


def test_mutation_patch_map_and_phase10_helpers_apply_real_patches() -> None:
    """
    Purpose:
        Validate mutation patch application and top-level phase10 helper contracts.
    Contract:
        - MutationPatchMap applies target ids into returned patch rows.
        - Empty mutation overrides return the original blueprint.
        - Missing phase10 maps raise when required.
        - apply_override_patch_map normalizes non-dict payloads to an empty map.
    """

    blueprint, service_ref, mutation_ref = _build_blueprint()
    mutation_patch_map = MutationPatchMap(
        root_spell_id="consumer-id",
        targets_by_spec={
            "*mutation": [
                MutationEdgePatch(
                    child_spell_id="consumer-id",
                    param_name="mutation",
                    param_path_id=mutation_ref.param_path_id,
                    old_parent_id=None,
                    new_parent_id=None,
                )
            ]
        },
    )
    override_patch_map = OverridePatchMap(
        root_spell_id="consumer-id",
        targets_by_spec={"*service": [service_ref]},
        specificity_by_spec={"*service": _Specificity.UNIQUE},
    )

    patches = mutation_patch_map.apply({"*mutation": "mutator-id"})

    assert len(patches) == 1
    assert patches[0].child_spell_id == "consumer-id"
    assert patches[0].param_name == "mutation"
    assert patches[0].new_parent_id == "mutator-id"

    mutated_blueprint = apply_mutation_patch_map(
        blueprint=blueprint,
        mutation_patch_map=mutation_patch_map,
        mutation_override={"*mutation": "mutator-id"},
    )

    assert mutated_blueprint is not blueprint
    assert any(
        ref.node_id == "mutator-id" and ref.param_name == "mutation"
        for ref in mutated_blueprint.socket_refs
    )

    assert apply_phase10_mutation_overrides(
        blueprint=blueprint,
        mutation_patch_map=mutation_patch_map,
        mutation_override={},
    ) is blueprint

    with pytest.raises(RuntimeError, match="mutation patch map is required"):
        apply_phase10_mutation_overrides(
            blueprint=blueprint,
            mutation_patch_map=None,
            mutation_override={"*mutation": "mutator-id"},
        )

    assert apply_override_patch_map(
        override_patch_map=override_patch_map,
        override_payload=["bad-shape"],
    ) == {}

    with pytest.raises(RuntimeError, match="override patch map is required"):
        apply_phase10_override_payload(
            override_patch_map=None,
            override_payload={"*service": "override"},
        )

    mutation_patch_map.cleanup()
    override_patch_map.cleanup()
    blueprint.cleanup()
    mutated_blueprint.cleanup()


def test_patch_map_builder_builds_override_and_mutation_maps_for_blueprint() -> None:
    """
    Purpose:
        Validate the smallest real PatchMapBuilder contract.
    Contract:
        - Path-key memoization is stable for repeated path ids.
        - Override and mutation maps are built from real blueprint socket refs.
        - Unique and broadcast keys are available for runtime application.
    """

    blueprint, service_ref, mutation_ref = _build_blueprint()
    builder = PatchMapBuilder(blueprint=blueprint)

    service_key = builder._get_path_spec_key(service_ref.param_path_id)
    assert builder._get_path_spec_key(service_ref.param_path_id) == service_key
    assert service_key == "service"

    override_map = builder.build_override_patch_map()
    mutation_map = builder.build_mutation_patch_map()

    assert override_map.apply({"*service": "override"}) == {service_ref: "override"}
    assert override_map.apply({"**service": "broadcast"}) == {service_ref: "broadcast"}

    patches = mutation_map.apply({"*mutation": "mutator-id"})
    assert len(patches) == 1
    assert patches[0].param_path_id == mutation_ref.param_path_id
    assert patches[0].new_parent_id == "mutator-id"

    builder.cleanup()

    with pytest.raises(RuntimeError, match="PatchMapBuilder has already been cleaned"):
        builder._get_path_spec_key(service_ref.param_path_id)

    builder.cleanup()
    override_map.cleanup()
    mutation_map.cleanup()
    blueprint.cleanup()
