from typing import Tuple

from melder.aether.spellbook.spell_compiler.blueprints.patch_maps import (
    OverridePatchMap,
    _Specificity,
)
from melder.aether.spellbook.spell_compiler.dag.dag_index import SocketRef
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind


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


def _build_two_unique_override_patch_map() -> Tuple[OverridePatchMap, SocketRef, SocketRef]:
    """
    Build a minimal OverridePatchMap with two independent unique socket targets.

    Returns:
        Tuple[OverridePatchMap, SocketRef, SocketRef]:
            Patch map and sockets for ``*left`` / ``*right``.
    """
    left_socket_ref = SocketRef(
        node_id="spell-left",
        param_name="left",
        param_path_id=11,
        socket_kind=SocketKind.NORMAL,
    )
    right_socket_ref = SocketRef(
        node_id="spell-right",
        param_name="right",
        param_path_id=12,
        socket_kind=SocketKind.NORMAL,
    )
    patch_map = OverridePatchMap(
        root_spell_id="root",
        targets_by_spec={
            "*left": [left_socket_ref],
            "*right": [right_socket_ref],
        },
        specificity_by_spec={
            "*left": _Specificity.UNIQUE,
            "*right": _Specificity.UNIQUE,
        },
    )
    return patch_map, left_socket_ref, right_socket_ref


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


def test_apply_with_socket_shape_reuses_multi_key_result_for_same_value_identities() -> None:
    """
    Verify small multi-key payloads reuse cached map/shape for identical value identities.
    """
    patch_map, left_socket_ref, right_socket_ref = _build_two_unique_override_patch_map()
    left_value = object()
    right_value = object()

    first_map, first_shape = patch_map.apply_with_socket_shape(
        spell_override={
            "*left": left_value,
            "*right": right_value,
        },
    )
    second_map, second_shape = patch_map.apply_with_socket_shape(
        spell_override={
            "*left": left_value,
            "*right": right_value,
        },
    )

    assert first_map is second_map
    assert first_shape is second_shape
    assert first_map == {
        left_socket_ref: left_value,
        right_socket_ref: right_value,
    }


def test_apply_with_socket_shape_rebuilds_multi_key_map_when_identity_changes() -> None:
    """
    Verify small multi-key payload cache is invalidated when one value identity changes.
    """
    patch_map, left_socket_ref, right_socket_ref = _build_two_unique_override_patch_map()
    left_value = object()
    right_value_a = object()
    right_value_b = object()

    first_map, first_shape = patch_map.apply_with_socket_shape(
        spell_override={
            "*left": left_value,
            "*right": right_value_a,
        },
    )
    second_map, second_shape = patch_map.apply_with_socket_shape(
        spell_override={
            "*left": left_value,
            "*right": right_value_b,
        },
    )

    assert first_map is not second_map
    assert first_shape == second_shape
    assert first_map == {
        left_socket_ref: left_value,
        right_socket_ref: right_value_a,
    }
    assert second_map == {
        left_socket_ref: left_value,
        right_socket_ref: right_value_b,
    }
