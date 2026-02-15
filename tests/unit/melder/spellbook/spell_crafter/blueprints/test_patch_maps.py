from typing import Tuple

from melder.spellbook.spell_crafter.blueprints.patch_maps import (
    OverridePatchMap,
    _Specificity,
)
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _build_single_unique_override_patch_map() -> Tuple[OverridePatchMap, SocketRef]:
    """
    Build a minimal OverridePatchMap with one unique socket target.

    Returns:
        Tuple[OverridePatchMap, SocketRef]:
            Patch map and the single socket it resolves for ``*dep``.
    """
    socket_ref = SocketRef(
        node_id="spell-1",
        param_name="dep",
        param_path_id=7,
        socket_kind=SocketKind.NORMAL,
    )
    patch_map = OverridePatchMap(
        root_spell_id="spell-1",
        targets_by_spec={
            "*dep": [socket_ref],
        },
        specificity_by_spec={
            "*dep": _Specificity.UNIQUE,
        },
    )
    return patch_map, socket_ref


def test_apply_with_socket_shape_reuses_single_key_result_for_same_value_identity() -> None:
    """
    Verify one-key apply reuses cached map/shape when key and value identity match.
    """
    patch_map, socket_ref = _build_single_unique_override_patch_map()
    shared_value = object()

    first_map, first_shape = patch_map.apply_with_socket_shape(
        spell_override={"*dep": shared_value},
    )
    second_map, second_shape = patch_map.apply_with_socket_shape(
        spell_override={"*dep": shared_value},
    )

    assert first_map is second_map
    assert first_shape is second_shape
    assert first_map == {socket_ref: shared_value}
    assert first_shape == (
        (
            "spell-1",
            7,
            "dep",
            SocketKind.NORMAL.value,
        ),
    )


def test_apply_with_socket_shape_rebuilds_single_key_map_for_new_value_identity() -> None:
    """
    Verify one-key apply rebuilds the map when value identity changes.
    """
    patch_map, socket_ref = _build_single_unique_override_patch_map()
    first_value = object()
    second_value = object()

    first_map, first_shape = patch_map.apply_with_socket_shape(
        spell_override={"*dep": first_value},
    )
    second_map, second_shape = patch_map.apply_with_socket_shape(
        spell_override={"*dep": second_value},
    )

    assert first_map is not second_map
    assert first_shape is second_shape
    assert first_map == {socket_ref: first_value}
    assert second_map == {socket_ref: second_value}
