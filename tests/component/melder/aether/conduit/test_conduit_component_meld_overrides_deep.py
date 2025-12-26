"""
Component tests for deep meld overrides across layered dependency graphs.

These tests exercise SpellOverrider through Conduit.meld to validate
deep path targeting, wildcard rules, precedence, and error handling.
"""
from contextlib import contextmanager
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from tests.mocks.spellbook.core_classes import BasicConfig, BasicService
from tests.mocks.spellbook.deep_layers import (
    Depth3LeafA,
    Depth3LeafB,
    Depth3Layer2A,
    Depth3Layer2B,
    Depth3Root,
    Depth5LeafA,
    Depth5LeafB,
    Depth5Layer2A,
    Depth5Layer2B,
    Depth5Layer3A,
    Depth5Layer3B,
    Depth5Layer4A,
    Depth5Layer4B,
    Depth5Root,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_meld_overrides_deep() -> None:
    """
    Purpose:
        Ensure component meld override tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@contextmanager
def _conjured(spellbook: Spellbook) -> Iterator[Conduit]:
    """
    Purpose:
        Yield a Conduit and ensure cleanup after use.
    Contract:
        - Conjures a root conduit.
        - Always cleans up the conduit after yielding.
    Args:
        spellbook: Spellbook used to conjure the conduit.
    Returns:
        Iterator[Conduit]: The active conduit for the test.
    """
    conduit = spellbook.conjure(name="root")
    try:
        yield conduit
    finally:
        conduit.cleanup()


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component meld override tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _bind_depth3_graph(spellbook: Spellbook) -> str:
    """
    Purpose:
        Bind the depth-3 dependency graph from test mocks.
    Contract:
        - Registers all Depth3 classes with unique existence.
        - Returns the spell id for the Depth3Root spell.
    Args:
        spellbook: Spellbook used to register the graph.
    Returns:
        str: Versioned spell id for Depth3Root.
    """
    spellbook.bind(spell=Depth3LeafA, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth3LeafB, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth3Layer2A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth3Layer2B, existence=Existence.unique, permissions="create")
    return spellbook.bind(spell=Depth3Root, existence=Existence.unique, permissions="create")


def _bind_depth5_graph(spellbook: Spellbook) -> str:
    """
    Purpose:
        Bind the depth-5 dependency graph from test mocks.
    Contract:
        - Registers all Depth5 classes with unique existence.
        - Returns the spell id for the Depth5Root spell.
    Args:
        spellbook: Spellbook used to register the graph.
    Returns:
        str: Versioned spell id for Depth5Root.
    """
    spellbook.bind(spell=Depth5LeafA, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth5LeafB, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth5Layer4A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth5Layer4B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth5Layer3A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth5Layer3B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth5Layer2A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=Depth5Layer2B, existence=Existence.unique, permissions="create")
    return spellbook.bind(spell=Depth5Root, existence=Existence.unique, permissions="create")


def _walk_path(root: object, path: tuple[str, ...]) -> object:
    """
    Purpose:
        Traverse a nested object graph using attribute path segments.
    Contract:
        - Each path segment is treated as an attribute name on the current object.
        - Returns the object at the end of the path.
    Args:
        root: Root object to traverse.
        path: Attribute path segments to walk.
    Returns:
        object: The resolved object at the end of the path.
    """
    current = root
    for segment in path:
        current = getattr(current, segment)
    return current


def _depth3_default_markers() -> dict[tuple[str, str], str]:
    """
    Purpose:
        Provide default Depth3 leaf markers keyed by path.
    Contract:
        - Left-left and right-left map to "L3A".
        - Left-right and right-right map to "L3B".
    Returns:
        dict[tuple[str, str], str]: Mapping of leaf paths to markers.
    """
    return {
        ("left", "left"): "L3A",
        ("left", "right"): "L3B",
        ("right", "left"): "L3A",
        ("right", "right"): "L3B",
    }


def _depth3_markers(root: Depth3Root) -> dict[tuple[str, str], str]:
    """
    Purpose:
        Collect Depth3 leaf markers for assertion helpers.
    Contract:
        - Returns markers for the four leaf positions.
    Args:
        root: Depth3Root instance to inspect.
    Returns:
        dict[tuple[str, str], str]: Mapping of leaf paths to marker values.
    """
    return {
        ("left", "left"): root.left.left.marker,
        ("left", "right"): root.left.right.marker,
        ("right", "left"): root.right.left.marker,
        ("right", "right"): root.right.right.marker,
    }


def _make_depth3_leaf(leaf_cls: type, marker: str) -> object:
    """
    Purpose:
        Construct a Depth3 leaf instance with a custom marker.
    Contract:
        - Sets the marker attribute to the supplied value.
    Args:
        leaf_cls: Depth3LeafA or Depth3LeafB class.
        marker: Marker value to assign.
    Returns:
        object: Leaf instance with the custom marker.
    """
    leaf = leaf_cls()
    leaf.marker = marker
    return leaf


def _make_depth3_layer2(
    layer_cls: type,
    left_marker: str,
    right_marker: str,
) -> object:
    """
    Purpose:
        Construct a Depth3 layer-2 instance with custom leaf markers.
    Contract:
        - Creates new leaf instances for left and right.
        - Applies the supplied markers to those leaves.
    Args:
        layer_cls: Depth3Layer2A or Depth3Layer2B class.
        left_marker: Marker for the left leaf.
        right_marker: Marker for the right leaf.
    Returns:
        object: Layer-2 instance with custom leaf markers.
    """
    left_leaf = _make_depth3_leaf(Depth3LeafA, left_marker)
    right_leaf = _make_depth3_leaf(Depth3LeafB, right_marker)
    return layer_cls(left=left_leaf, right=right_leaf)


def _alternate_depth5_path(path: tuple[str, ...]) -> tuple[str, ...]:
    """
    Purpose:
        Build a different depth-5 leaf path for control assertions.
    Contract:
        - Flips each segment from "left" to "right" or vice versa.
    Args:
        path: Original leaf path.
    Returns:
        tuple[str, ...]: A different path of equal length.
    """
    return tuple("right" if segment == "left" else "left" for segment in path)


class _ServiceNode:
    """
    Purpose:
        Provide a node that depends on a BasicService.
    Contract:
        - Stores the injected service instance.
    """

    def __init__(self, service: BasicService) -> None:
        """
        Purpose:
            Capture the injected service dependency.
        Contract:
            Stores the service on the instance.
        Args:
            service: Injected BasicService dependency.
        Returns:
            None.
        """
        self.service = service


class _ConfigNode:
    """
    Purpose:
        Provide a node that depends on a BasicConfig.
    Contract:
        - Stores the injected config instance.
    """

    def __init__(self, config: BasicConfig) -> None:
        """
        Purpose:
            Capture the injected config dependency.
        Contract:
            Stores the config on the instance.
        Args:
            config: Injected BasicConfig dependency.
        Returns:
            None.
        """
        self.config = config


class _MixedNode:
    """
    Purpose:
        Provide a node that combines service and config branches.
    Contract:
        - Stores left and right dependency nodes.
    """

    def __init__(self, left: _ServiceNode, right: _ConfigNode) -> None:
        """
        Purpose:
            Capture the left and right dependencies.
        Contract:
            Stores left and right on the instance.
        Args:
            left: Service branch dependency.
            right: Config branch dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class _RootNode:
    """
    Purpose:
        Provide a root node with mixed and direct service dependencies.
    Contract:
        - Stores the mixed node and a direct BasicService dependency.
    """

    def __init__(self, mixed: _MixedNode, service: BasicService) -> None:
        """
        Purpose:
            Capture the root dependencies.
        Contract:
            Stores mixed and service on the instance.
        Args:
            mixed: Mixed dependency node.
            service: Direct BasicService dependency.
        Returns:
            None.
        """
        self.mixed = mixed
        self.service = service


def _bind_custom_graph(
    spellbook: Spellbook,
    *,
    service_existence: Existence = Existence.many,
    root_existence: Existence = Existence.unique,
) -> str:
    """
    Purpose:
        Bind the custom mixed graph for deep override tests.
    Contract:
        - Registers BasicService, BasicConfig, and custom nodes.
        - Allows customizing the BasicService existence for override scenarios.
        - Returns the spell id for the root node.
    Args:
        spellbook: Spellbook used to register the graph.
        service_existence: Existence policy used for BasicService bindings.
        root_existence: Existence policy used for the root node binding.
    Returns:
        str: Versioned spell id for the root node.
    """
    spellbook.bind(spell=BasicService, existence=service_existence, permissions="create")
    spellbook.bind(spell=BasicConfig, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_ServiceNode, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_ConfigNode, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_MixedNode, existence=Existence.unique, permissions="create")
    return spellbook.bind(spell=_RootNode, existence=root_existence, permissions="create")


@pytest.mark.parametrize(
    "override_path,leaf_cls,marker,attr_path",
    [
        ("left>left", Depth3LeafA, "override-left-left", ("left", "left")),
        ("left>right", Depth3LeafB, "override-left-right", ("left", "right")),
        ("right>left", Depth3LeafA, "override-right-left", ("right", "left")),
        ("right>right", Depth3LeafB, "override-right-right", ("right", "right")),
    ],
)
def test_component_meld_overrides_depth3_path_targets_leaf(
    override_path: str,
    leaf_cls: type,
    marker: str,
    attr_path: tuple[str, str],
) -> None:
    """
    Purpose:
        Validate PATH overrides target depth-3 leaf sockets.
    Contract:
        - The specified leaf socket receives the override object.
        - Non-targeted leaves retain default markers.
    Returns:
        None.
    Raises:
        AssertionError: If the override does not target the expected leaf.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth3_graph(spellbook)
    override_leaf = _make_depth3_leaf(leaf_cls, marker)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={override_path: override_leaf},
        )
        assert _walk_path(root, attr_path) is override_leaf
        expected = _depth3_default_markers()
        expected[attr_path] = marker
        assert _depth3_markers(root) == expected


@pytest.mark.parametrize(
    "override_path,leaf_cls,marker,attr_path",
    [
        (" left > left ", Depth3LeafA, "trim-left-left", ("left", "left")),
        (" left > right ", Depth3LeafB, "trim-left-right", ("left", "right")),
        (" right > left ", Depth3LeafA, "trim-right-left", ("right", "left")),
        (" right > right ", Depth3LeafB, "trim-right-right", ("right", "right")),
    ],
)
def test_component_meld_overrides_depth3_path_trims_whitespace(
    override_path: str,
    leaf_cls: type,
    marker: str,
    attr_path: tuple[str, str],
) -> None:
    """
    Purpose:
        Validate PATH overrides tolerate whitespace around segments.
    Contract:
        - Whitespace in path keys is ignored for matching.
        - The targeted leaf receives the override object.
    Returns:
        None.
    Raises:
        AssertionError: If whitespace paths do not resolve correctly.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth3_graph(spellbook)
    override_leaf = _make_depth3_leaf(leaf_cls, marker)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={override_path: override_leaf},
        )
        assert _walk_path(root, attr_path) is override_leaf


def test_component_meld_overrides_depth3_multiple_paths_apply() -> None:
    """
    Purpose:
        Validate multiple PATH overrides apply in a single meld.
    Contract:
        - Each targeted leaf receives the correct override object.
    Returns:
        None.
    Raises:
        AssertionError: If multi-path overrides do not apply correctly.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth3_graph(spellbook)
    left_override = _make_depth3_leaf(Depth3LeafA, "multi-left-left")
    right_override = _make_depth3_leaf(Depth3LeafB, "multi-right-right")

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={
                "left>left": left_override,
                "right>right": right_override,
            },
        )
        assert root.left.left is left_override
        assert root.right.right is right_override
        assert root.left.right.marker == "L3B"
        assert root.right.left.marker == "L3A"


@pytest.mark.parametrize(
    "override_path,layer_cls,left_marker,right_marker",
    [
        ("left", Depth3Layer2A, "branch-left-left", "branch-left-right"),
        ("right", Depth3Layer2B, "branch-right-left", "branch-right-right"),
    ],
)
def test_component_meld_overrides_depth3_path_replaces_branch(
    override_path: str,
    layer_cls: type,
    left_marker: str,
    right_marker: str,
) -> None:
    """
    Purpose:
        Validate PATH overrides can replace entire depth-3 branches.
    Contract:
        - The targeted branch node is replaced by the override instance.
        - The other branch remains unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If branch overrides do not apply correctly.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth3_graph(spellbook)
    override_layer = _make_depth3_layer2(
        layer_cls,
        left_marker=left_marker,
        right_marker=right_marker,
    )

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={override_path: override_layer},
        )
        branch = getattr(root, override_path)
        assert branch is override_layer
        assert branch.left.marker == left_marker
        assert branch.right.marker == right_marker
        other_branch = root.right if override_path == "left" else root.left
        assert other_branch.left.marker == "L3A"
        assert other_branch.right.marker == "L3B"


@pytest.mark.parametrize(
    "override_path",
    [
        "left>missing",
        "right>left>missing",
        "missing",
        "left>left>left",
    ],
)
def test_component_meld_overrides_depth3_missing_path_raises(
    override_path: str,
) -> None:
    """
    Purpose:
        Validate missing PATH overrides raise MeldExecutionError.
    Contract:
        - Missing paths are rejected during override application.
    Returns:
        None.
    Raises:
        AssertionError: If missing paths do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth3_graph(spellbook)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(
                spell=root_id,
                spell_override={override_path: Depth3LeafA()},
            )


@pytest.mark.parametrize("override_key", ["*left", "*right"])
def test_component_meld_overrides_depth3_unique_raises_on_multiple_matches(
    override_key: str,
) -> None:
    """
    Purpose:
        Validate UNIQUE overrides raise when multiple matches exist.
    Contract:
        - Unique overrides are rejected when more than one socket matches.
    Returns:
        None.
    Raises:
        AssertionError: If unique overrides do not raise on ambiguity.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth3_graph(spellbook)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(
                spell=root_id,
                spell_override={override_key: Depth3LeafA()},
            )


@pytest.mark.parametrize(
    "override_path,leaf_cls,marker,attr_path",
    [
        ("left>left>left>left", Depth5LeafA, "deep-left-left-left-left", ("left", "left", "left", "left")),
        ("left>left>left>right", Depth5LeafB, "deep-left-left-left-right", ("left", "left", "left", "right")),
        ("right>right>right>left", Depth5LeafA, "deep-right-right-right-left", ("right", "right", "right", "left")),
        ("right>right>right>right", Depth5LeafB, "deep-right-right-right-right", ("right", "right", "right", "right")),
    ],
)
def test_component_meld_overrides_depth5_path_targets_deep_leaf(
    override_path: str,
    leaf_cls: type,
    marker: str,
    attr_path: tuple[str, ...],
) -> None:
    """
    Purpose:
        Validate PATH overrides target deep leaves in a depth-5 graph.
    Contract:
        - The specified leaf receives the override object.
        - A control leaf retains its default marker.
    Returns:
        None.
    Raises:
        AssertionError: If deep path overrides do not apply correctly.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth5_graph(spellbook)
    override_leaf = _make_depth3_leaf(leaf_cls, marker)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={override_path: override_leaf},
        )
        assert _walk_path(root, attr_path) is override_leaf
        control_path = _alternate_depth5_path(attr_path)
        control_leaf = _walk_path(root, control_path)
        expected_marker = "L5A" if control_path[-1] == "left" else "L5B"
        assert control_leaf.marker == expected_marker


def test_component_meld_overrides_depth5_multiple_paths_apply() -> None:
    """
    Purpose:
        Validate multiple deep PATH overrides apply in a single meld.
    Contract:
        - Each targeted leaf receives the correct override object.
    Returns:
        None.
    Raises:
        AssertionError: If multi-path overrides do not apply correctly.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth5_graph(spellbook)
    left_override = _make_depth3_leaf(Depth5LeafA, "multi-depth5-left")
    right_override = _make_depth3_leaf(Depth5LeafB, "multi-depth5-right")

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={
                "left>left>left>left": left_override,
                "right>right>right>right": right_override,
            },
        )
        assert _walk_path(root, ("left", "left", "left", "left")) is left_override
        assert _walk_path(root, ("right", "right", "right", "right")) is right_override


@pytest.mark.parametrize(
    "override_path",
    [
        "left>left>left>missing",
        "left>missing>left>left",
        "missing",
    ],
)
def test_component_meld_overrides_depth5_missing_path_raises(
    override_path: str,
) -> None:
    """
    Purpose:
        Validate missing depth-5 paths raise MeldExecutionError.
    Contract:
        - Missing paths are rejected during override application.
    Returns:
        None.
    Raises:
        AssertionError: If missing paths do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth5_graph(spellbook)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(
                spell=root_id,
                spell_override={override_path: Depth5LeafA()},
            )


@pytest.mark.parametrize(
    "override_path,leaf_cls,marker,attr_path",
    [
        (" left > left > left > left ", Depth5LeafA, "trim-depth5-left", ("left", "left", "left", "left")),
        (" right > right > right > right ", Depth5LeafB, "trim-depth5-right", ("right", "right", "right", "right")),
    ],
)
def test_component_meld_overrides_depth5_path_trims_whitespace(
    override_path: str,
    leaf_cls: type,
    marker: str,
    attr_path: tuple[str, ...],
) -> None:
    """
    Purpose:
        Validate depth-5 path overrides tolerate whitespace.
    Contract:
        - Whitespace in path keys is ignored for matching.
        - The targeted leaf receives the override object.
    Returns:
        None.
    Raises:
        AssertionError: If whitespace paths do not resolve correctly.
    """
    spellbook = _make_spellbook()
    root_id = _bind_depth5_graph(spellbook)
    override_leaf = _make_depth3_leaf(leaf_cls, marker)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={override_path: override_leaf},
        )
        assert _walk_path(root, attr_path) is override_leaf


def test_component_meld_overrides_custom_many_instances_are_distinct() -> None:
    """
    Purpose:
        Validate Existence.many yields distinct service instances per path.
    Contract:
        - The root service instance differs from the mixed-left service instance.
    Returns:
        None.
    Raises:
        AssertionError: If per-path instances are not distinct.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(spell=root_id)
        assert root.service is not root.mixed.left.service


@pytest.mark.parametrize(
    "override_path,value,attr_path,attr_name",
    [
        ("mixed>left>service>marker", "marker-left", ("mixed", "left", "service"), "marker"),
        ("mixed>right>config>label", "label-right", ("mixed", "right", "config"), "label"),
    ],
)
def test_component_meld_overrides_custom_path_targets_nested_values(
    override_path: str,
    value: str,
    attr_path: tuple[str, ...],
    attr_name: str,
) -> None:
    """
    Purpose:
        Validate PATH overrides target nested constructor parameters.
    Contract:
        - The nested dependency parameter is replaced with the override value.
    Returns:
        None.
    Raises:
        AssertionError: If nested overrides do not apply correctly.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={override_path: value},
        )
        target = _walk_path(root, attr_path)
        assert getattr(target, attr_name) == value


def test_component_meld_overrides_custom_multiple_paths_apply() -> None:
    """
    Purpose:
        Validate multiple nested PATH overrides apply in one meld.
    Contract:
        - Each nested parameter reflects its override value.
    Returns:
        None.
    Raises:
        AssertionError: If multi-path overrides do not apply correctly.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={
                "mixed>left>service>marker": "multi-left",
                "mixed>right>config>label": "multi-right",
                "service>marker": "multi-root",
            },
        )
        assert root.mixed.left.service.marker == "multi-left"
        assert root.mixed.right.config.label == "multi-right"
        assert root.service.marker == "multi-root"


def test_component_meld_overrides_custom_broadcast_marker_targets_all() -> None:
    """
    Purpose:
        Validate BROADCAST overrides apply to all marker sockets.
    Contract:
        - Both BasicService markers receive the broadcast value.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast marker overrides do not apply.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={"**marker": "broadcast"},
        )
        assert root.service.marker == "broadcast"
        assert root.mixed.left.service.marker == "broadcast"


def test_component_meld_overrides_custom_broadcast_service_targets_all() -> None:
    """
    Purpose:
        Validate BROADCAST overrides can replace multiple service dependencies.
    Contract:
        - Both service sockets receive the same override instance.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast service overrides do not apply.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)
    override_service = BasicService(marker="override-service")

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={"**service": override_service},
        )
        assert root.service is override_service
        assert root.mixed.left.service is override_service


def test_component_meld_overrides_custom_broadcast_with_path_precedence() -> None:
    """
    Purpose:
        Validate PATH overrides take precedence over BROADCAST overrides.
    Contract:
        - A specific path override wins over a broadcast marker override.
    Returns:
        None.
    Raises:
        AssertionError: If precedence does not favor PATH overrides.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={
                "**marker": "broadcast",
                "mixed>left>service>marker": "path",
            },
        )
        assert root.mixed.left.service.marker == "path"
        assert root.service.marker == "broadcast"


def test_component_meld_overrides_custom_unique_right_targets_single() -> None:
    """
    Purpose:
        Validate UNIQUE overrides can replace a single branch node.
    Contract:
        - Unique override replaces the only "right" node in the graph.
    Returns:
        None.
    Raises:
        AssertionError: If the unique override does not apply.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)
    override_node = _ConfigNode(config=BasicConfig(label="override"))

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={"*right": override_node},
        )
        assert root.mixed.right is override_node
        assert root.mixed.right.config.label == "override"


def test_component_meld_overrides_custom_unique_over_broadcast() -> None:
    """
    Purpose:
        Validate UNIQUE overrides take precedence over BROADCAST overrides.
    Contract:
        - Unique override value is used when both target the same socket.
    Returns:
        None.
    Raises:
        AssertionError: If precedence does not favor UNIQUE overrides.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)
    broadcast_config = BasicConfig(label="broadcast")
    unique_config = BasicConfig(label="unique")

    with _conjured(spellbook) as conduit:
        root = conduit.meld(
            spell=root_id,
            spell_override={
                "**config": broadcast_config,
                "*config": unique_config,
            },
        )
        assert root.mixed.right.config is unique_config
        assert root.mixed.right.config.label == "unique"


def test_component_meld_overrides_custom_shared_duplicate_param_raises() -> None:
    """
    Purpose:
        Validate shared spells reject multiple overrides for the same parameter.
    Contract:
        - Multiple overrides for a shared BasicService parameter raise.
        - The error is raised even when override values match.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate shared overrides do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook, service_existence=Existence.unique)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Multiple overrides"):
            conduit.meld(
                spell=root_id,
                spell_override={
                    "service>marker": "dup",
                    "mixed>left>service>marker": "dup",
                },
            )


def test_component_meld_overrides_custom_shared_existing_instance_raises() -> None:
    """
    Purpose:
        Validate overrides are rejected when a shared root already exists.
    Contract:
        - A second meld with overrides raises MeldExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If shared-instance overrides do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        conduit.meld(spell=root_id)
        with pytest.raises(MeldExecutionError, match="already exists"):
            conduit.meld(
                spell=root_id,
                spell_override={"service>marker": "override"},
            )


def test_component_meld_overrides_custom_shared_dependency_existing_raises() -> None:
    """
    Purpose:
        Validate overrides are rejected when a shared dependency already exists.
    Contract:
        - A new root meld with overrides raises when the shared dependency
          is already instantiated.
    Returns:
        None.
    Raises:
        AssertionError: If shared dependency overrides do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(
        spellbook,
        service_existence=Existence.unique,
        root_existence=Existence.many,
    )

    with _conjured(spellbook) as conduit:
        conduit.meld(spell=root_id)
        with pytest.raises(MeldExecutionError, match="already exists"):
            conduit.meld(
                spell=root_id,
                spell_override={"service>marker": "override"},
            )


def test_component_meld_overrides_custom_unique_missing_raises() -> None:
    """
    Purpose:
        Validate UNIQUE overrides raise when no sockets match.
    Contract:
        - Missing unique targets raise MeldExecutionError.
    Returns:
        None.
    Raises:
        AssertionError: If missing unique overrides do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(
                spell=root_id,
                spell_override={"*missing": BasicConfig(label="missing")},
            )


def test_component_meld_overrides_custom_unique_conflict_raises() -> None:
    """
    Purpose:
        Validate conflicting UNIQUE overrides raise errors.
    Contract:
        - Conflicting unique overrides with the same specificity are rejected.
    Returns:
        None.
    Raises:
        AssertionError: If conflicting unique overrides do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(
                spell=root_id,
                spell_override={
                    "*config": BasicConfig(label="a"),
                    "* config": BasicConfig(label="b"),
                },
            )


@pytest.mark.parametrize(
    "override_map",
    [
        {None: "value"},
        {"": "value"},
        {"   ": "value"},
        {">": "value"},
        {"*": "value"},
        {"**": "value"},
    ],
)
def test_component_meld_overrides_custom_invalid_keys_raise(
    override_map: dict[object, object],
) -> None:
    """
    Purpose:
        Validate invalid override keys raise MeldExecutionError.
    Contract:
        - Invalid keys are rejected during override application.
    Returns:
        None.
    Raises:
        AssertionError: If invalid override keys do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(spell=root_id, spell_override=override_map)


def test_component_meld_overrides_custom_conflicting_broadcast_raises() -> None:
    """
    Purpose:
        Validate conflicting BROADCAST overrides raise errors.
    Contract:
        - Conflicting broadcast overrides with the same specificity are rejected.
    Returns:
        None.
    Raises:
        AssertionError: If conflicting broadcast overrides do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(
                spell=root_id,
                spell_override={
                    "**marker": "a",
                    "** marker": "b",
                },
            )


def test_component_meld_overrides_custom_conflicting_path_raises() -> None:
    """
    Purpose:
        Validate conflicting PATH overrides raise errors.
    Contract:
        - Conflicting path overrides with the same specificity are rejected.
    Returns:
        None.
    Raises:
        AssertionError: If conflicting path overrides do not raise.
    """
    spellbook = _make_spellbook()
    root_id = _bind_custom_graph(spellbook)

    with _conjured(spellbook) as conduit:
        with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
            conduit.meld(
                spell=root_id,
                spell_override={
                    "mixed>left>service>marker": "a",
                    " mixed > left > service > marker ": "b",
                },
            )
