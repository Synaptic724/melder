import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
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


def test_meld_deep_graph_depth_3_branches_unique_reuse() -> None:
    """
    Purpose:
        Validate a depth-3 branched dependency graph resolves and reuses singletons.
    Contract:
        - Root depends on two layer-2 nodes, each of which depends on two leaf nodes.
        - Unique dependencies are reused across branches.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies are not wired or reused as expected.
    """
    class _Layer3A:
        """
        Purpose:
            Provide a leaf dependency at layer 3.
        Contract:
            Stores a stable marker for identity checks.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the layer-3 marker.
            Contract:
                Sets marker to "L3A".
            Returns:
                None.
            """
            self.marker = "L3A"

    class _Layer3B:
        """
        Purpose:
            Provide a second leaf dependency at layer 3.
        Contract:
            Stores a stable marker for identity checks.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the layer-3 marker.
            Contract:
                Sets marker to "L3B".
            Returns:
                None.
            """
            self.marker = "L3B"

    class _Layer2A:
        """
        Purpose:
            Provide a layer-2 dependency that branches to two leaves.
        Contract:
            Stores references to both leaf dependencies.
        """
        def __init__(self, left: _Layer3A, right: _Layer3B) -> None:
            """
            Purpose:
                Capture leaf dependencies for layer 2.
            Contract:
                Stores left and right leaf references.
            Args:
                left: Layer-3 leaf A.
                right: Layer-3 leaf B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer2B:
        """
        Purpose:
            Provide a second layer-2 dependency that branches to two leaves.
        Contract:
            Stores references to both leaf dependencies.
        """
        def __init__(self, left: _Layer3A, right: _Layer3B) -> None:
            """
            Purpose:
                Capture leaf dependencies for layer 2.
            Contract:
                Stores left and right leaf references.
            Args:
                left: Layer-3 leaf A.
                right: Layer-3 leaf B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Root:
        """
        Purpose:
            Provide a root object for depth-3 resolution.
        Contract:
            Stores references to both layer-2 dependencies.
        """
        def __init__(self, left: _Layer2A, right: _Layer2B) -> None:
            """
            Purpose:
                Capture layer-2 dependencies at the root.
            Contract:
                Stores left and right layer-2 references.
            Args:
                left: Layer-2 dependency A.
                right: Layer-2 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(spell=_Layer3A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer3B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer2A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer2B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Root, existence=Existence.unique, permissions="create")

    conduit = spellbook.conjure(name="root")
    try:
        root = conduit.meld(spell=_Root)
        assert isinstance(root, _Root)
        assert isinstance(root.left, _Layer2A)
        assert isinstance(root.right, _Layer2B)
        assert root.left.left is root.right.left
        assert root.left.right is root.right.right
        assert root.left.left.marker == "L3A"
        assert root.left.right.marker == "L3B"
    finally:
        conduit.cleanup()


def test_meld_deep_graph_depth_5_branches_unique_reuse() -> None:
    """
    Purpose:
        Validate a depth-5 branched dependency graph resolves and reuses singletons.
    Contract:
        - Root depends on two layer-2 nodes, each layer depends on two nodes below.
        - Leaf nodes are reused across branches for Existence.unique.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies are not wired or reused as expected.
    """
    class _Layer5A:
        """
        Purpose:
            Provide a leaf dependency at layer 5.
        Contract:
            Stores a stable marker for identity checks.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the layer-5 marker.
            Contract:
                Sets marker to "L5A".
            Returns:
                None.
            """
            self.marker = "L5A"

    class _Layer5B:
        """
        Purpose:
            Provide a second leaf dependency at layer 5.
        Contract:
            Stores a stable marker for identity checks.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the layer-5 marker.
            Contract:
                Sets marker to "L5B".
            Returns:
                None.
            """
            self.marker = "L5B"

    class _Layer4A:
        """
        Purpose:
            Provide a layer-4 dependency that branches to layer-5 leaves.
        Contract:
            Stores references to both layer-5 dependencies.
        """
        def __init__(self, left: _Layer5A, right: _Layer5B) -> None:
            """
            Purpose:
                Capture layer-5 dependencies for layer 4.
            Contract:
                Stores left and right layer-5 references.
            Args:
                left: Layer-5 dependency A.
                right: Layer-5 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer4B:
        """
        Purpose:
            Provide a second layer-4 dependency that branches to layer-5 leaves.
        Contract:
            Stores references to both layer-5 dependencies.
        """
        def __init__(self, left: _Layer5A, right: _Layer5B) -> None:
            """
            Purpose:
                Capture layer-5 dependencies for layer 4.
            Contract:
                Stores left and right layer-5 references.
            Args:
                left: Layer-5 dependency A.
                right: Layer-5 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer3A:
        """
        Purpose:
            Provide a layer-3 dependency that branches to layer-4 nodes.
        Contract:
            Stores references to both layer-4 dependencies.
        """
        def __init__(self, left: _Layer4A, right: _Layer4B) -> None:
            """
            Purpose:
                Capture layer-4 dependencies for layer 3.
            Contract:
                Stores left and right layer-4 references.
            Args:
                left: Layer-4 dependency A.
                right: Layer-4 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer3B:
        """
        Purpose:
            Provide a second layer-3 dependency that branches to layer-4 nodes.
        Contract:
            Stores references to both layer-4 dependencies.
        """
        def __init__(self, left: _Layer4A, right: _Layer4B) -> None:
            """
            Purpose:
                Capture layer-4 dependencies for layer 3.
            Contract:
                Stores left and right layer-4 references.
            Args:
                left: Layer-4 dependency A.
                right: Layer-4 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer2A:
        """
        Purpose:
            Provide a layer-2 dependency that branches to layer-3 nodes.
        Contract:
            Stores references to both layer-3 dependencies.
        """
        def __init__(self, left: _Layer3A, right: _Layer3B) -> None:
            """
            Purpose:
                Capture layer-3 dependencies for layer 2.
            Contract:
                Stores left and right layer-3 references.
            Args:
                left: Layer-3 dependency A.
                right: Layer-3 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer2B:
        """
        Purpose:
            Provide a second layer-2 dependency that branches to layer-3 nodes.
        Contract:
            Stores references to both layer-3 dependencies.
        """
        def __init__(self, left: _Layer3A, right: _Layer3B) -> None:
            """
            Purpose:
                Capture layer-3 dependencies for layer 2.
            Contract:
                Stores left and right layer-3 references.
            Args:
                left: Layer-3 dependency A.
                right: Layer-3 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Root:
        """
        Purpose:
            Provide a root object for depth-5 resolution.
        Contract:
            Stores references to both layer-2 dependencies.
        """
        def __init__(self, left: _Layer2A, right: _Layer2B) -> None:
            """
            Purpose:
                Capture layer-2 dependencies at the root.
            Contract:
                Stores left and right layer-2 references.
            Args:
                left: Layer-2 dependency A.
                right: Layer-2 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(spell=_Layer5A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer5B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer4A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer4B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer3A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer3B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer2A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer2B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Root, existence=Existence.unique, permissions="create")

    conduit = spellbook.conjure(name="root")
    try:
        root = conduit.meld(spell=_Root)
        assert root.left.left.left.left is root.right.left.left.left
        assert root.left.left.left.right is root.right.right.right.right
        assert root.left.left.left.left.marker == "L5A"
        assert root.left.left.left.right.marker == "L5B"
        assert root.left is not root.right
    finally:
        conduit.cleanup()


def test_meld_deep_graph_depth_7_branches_unique_reuse() -> None:
    """
    Purpose:
        Validate a depth-7 branched dependency graph resolves and reuses singletons.
    Contract:
        - Root depends on two layer-2 nodes, each layer depends on two nodes below.
        - Leaf nodes are reused across branches for Existence.unique.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies are not wired or reused as expected.
    """
    class _Layer7A:
        """
        Purpose:
            Provide a leaf dependency at layer 7.
        Contract:
            Stores a stable marker for identity checks.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the layer-7 marker.
            Contract:
                Sets marker to "L7A".
            Returns:
                None.
            """
            self.marker = "L7A"

    class _Layer7B:
        """
        Purpose:
            Provide a second leaf dependency at layer 7.
        Contract:
            Stores a stable marker for identity checks.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the layer-7 marker.
            Contract:
                Sets marker to "L7B".
            Returns:
                None.
            """
            self.marker = "L7B"

    class _Layer6A:
        """
        Purpose:
            Provide a layer-6 dependency that branches to layer-7 leaves.
        Contract:
            Stores references to both layer-7 dependencies.
        """
        def __init__(self, left: _Layer7A, right: _Layer7B) -> None:
            """
            Purpose:
                Capture layer-7 dependencies for layer 6.
            Contract:
                Stores left and right layer-7 references.
            Args:
                left: Layer-7 dependency A.
                right: Layer-7 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer6B:
        """
        Purpose:
            Provide a second layer-6 dependency that branches to layer-7 leaves.
        Contract:
            Stores references to both layer-7 dependencies.
        """
        def __init__(self, left: _Layer7A, right: _Layer7B) -> None:
            """
            Purpose:
                Capture layer-7 dependencies for layer 6.
            Contract:
                Stores left and right layer-7 references.
            Args:
                left: Layer-7 dependency A.
                right: Layer-7 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer5A:
        """
        Purpose:
            Provide a layer-5 dependency that branches to layer-6 nodes.
        Contract:
            Stores references to both layer-6 dependencies.
        """
        def __init__(self, left: _Layer6A, right: _Layer6B) -> None:
            """
            Purpose:
                Capture layer-6 dependencies for layer 5.
            Contract:
                Stores left and right layer-6 references.
            Args:
                left: Layer-6 dependency A.
                right: Layer-6 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer5B:
        """
        Purpose:
            Provide a second layer-5 dependency that branches to layer-6 nodes.
        Contract:
            Stores references to both layer-6 dependencies.
        """
        def __init__(self, left: _Layer6A, right: _Layer6B) -> None:
            """
            Purpose:
                Capture layer-6 dependencies for layer 5.
            Contract:
                Stores left and right layer-6 references.
            Args:
                left: Layer-6 dependency A.
                right: Layer-6 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer4A:
        """
        Purpose:
            Provide a layer-4 dependency that branches to layer-5 nodes.
        Contract:
            Stores references to both layer-5 dependencies.
        """
        def __init__(self, left: _Layer5A, right: _Layer5B) -> None:
            """
            Purpose:
                Capture layer-5 dependencies for layer 4.
            Contract:
                Stores left and right layer-5 references.
            Args:
                left: Layer-5 dependency A.
                right: Layer-5 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer4B:
        """
        Purpose:
            Provide a second layer-4 dependency that branches to layer-5 nodes.
        Contract:
            Stores references to both layer-5 dependencies.
        """
        def __init__(self, left: _Layer5A, right: _Layer5B) -> None:
            """
            Purpose:
                Capture layer-5 dependencies for layer 4.
            Contract:
                Stores left and right layer-5 references.
            Args:
                left: Layer-5 dependency A.
                right: Layer-5 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer3A:
        """
        Purpose:
            Provide a layer-3 dependency that branches to layer-4 nodes.
        Contract:
            Stores references to both layer-4 dependencies.
        """
        def __init__(self, left: _Layer4A, right: _Layer4B) -> None:
            """
            Purpose:
                Capture layer-4 dependencies for layer 3.
            Contract:
                Stores left and right layer-4 references.
            Args:
                left: Layer-4 dependency A.
                right: Layer-4 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer3B:
        """
        Purpose:
            Provide a second layer-3 dependency that branches to layer-4 nodes.
        Contract:
            Stores references to both layer-4 dependencies.
        """
        def __init__(self, left: _Layer4A, right: _Layer4B) -> None:
            """
            Purpose:
                Capture layer-4 dependencies for layer 3.
            Contract:
                Stores left and right layer-4 references.
            Args:
                left: Layer-4 dependency A.
                right: Layer-4 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer2A:
        """
        Purpose:
            Provide a layer-2 dependency that branches to layer-3 nodes.
        Contract:
            Stores references to both layer-3 dependencies.
        """
        def __init__(self, left: _Layer3A, right: _Layer3B) -> None:
            """
            Purpose:
                Capture layer-3 dependencies for layer 2.
            Contract:
                Stores left and right layer-3 references.
            Args:
                left: Layer-3 dependency A.
                right: Layer-3 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer2B:
        """
        Purpose:
            Provide a second layer-2 dependency that branches to layer-3 nodes.
        Contract:
            Stores references to both layer-3 dependencies.
        """
        def __init__(self, left: _Layer3A, right: _Layer3B) -> None:
            """
            Purpose:
                Capture layer-3 dependencies for layer 2.
            Contract:
                Stores left and right layer-3 references.
            Args:
                left: Layer-3 dependency A.
                right: Layer-3 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Root:
        """
        Purpose:
            Provide a root object for depth-7 resolution.
        Contract:
            Stores references to both layer-2 dependencies.
        """
        def __init__(self, left: _Layer2A, right: _Layer2B) -> None:
            """
            Purpose:
                Capture layer-2 dependencies at the root.
            Contract:
                Stores left and right layer-2 references.
            Args:
                left: Layer-2 dependency A.
                right: Layer-2 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(spell=_Layer7A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer7B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer6A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer6B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer5A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer5B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer4A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer4B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer3A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer3B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer2A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer2B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Root, existence=Existence.unique, permissions="create")

    conduit = spellbook.conjure(name="root")
    try:
        root = conduit.meld(spell=_Root)
        left_leaf = root.left.left.left.left.left.left
        right_leaf = root.right.left.left.left.left.left
        assert left_leaf is right_leaf
        assert left_leaf.marker == "L7A"
        assert root.left.left.left.left.left.right is root.right.left.left.left.left.right
        assert root.left.left.left.left.left.right.marker == "L7B"
        assert root.left is not root.right
    finally:
        conduit.cleanup()


def test_meld_deep_graph_depth_9_branches_unique_reuse() -> None:
    """
    Purpose:
        Validate a depth-9 branched dependency graph resolves and reuses singletons.
    Contract:
        - Root depends on two layer-2 nodes, each layer depends on two nodes below.
        - Leaf nodes are reused across branches for Existence.unique.
    Returns:
        None.
    Raises:
        AssertionError: If dependencies are not wired or reused as expected.
    """
    class _Layer9A:
        """
        Purpose:
            Provide a leaf dependency at layer 9.
        Contract:
            Stores a stable marker for identity checks.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the layer-9 marker.
            Contract:
                Sets marker to "L9A".
            Returns:
                None.
            """
            self.marker = "L9A"

    class _Layer9B:
        """
        Purpose:
            Provide a second leaf dependency at layer 9.
        Contract:
            Stores a stable marker for identity checks.
        """
        def __init__(self) -> None:
            """
            Purpose:
                Initialize the layer-9 marker.
            Contract:
                Sets marker to "L9B".
            Returns:
                None.
            """
            self.marker = "L9B"

    class _Layer8A:
        """
        Purpose:
            Provide a layer-8 dependency that branches to layer-9 leaves.
        Contract:
            Stores references to both layer-9 dependencies.
        """
        def __init__(self, left: _Layer9A, right: _Layer9B) -> None:
            """
            Purpose:
                Capture layer-9 dependencies for layer 8.
            Contract:
                Stores left and right layer-9 references.
            Args:
                left: Layer-9 dependency A.
                right: Layer-9 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer8B:
        """
        Purpose:
            Provide a second layer-8 dependency that branches to layer-9 leaves.
        Contract:
            Stores references to both layer-9 dependencies.
        """
        def __init__(self, left: _Layer9A, right: _Layer9B) -> None:
            """
            Purpose:
                Capture layer-9 dependencies for layer 8.
            Contract:
                Stores left and right layer-9 references.
            Args:
                left: Layer-9 dependency A.
                right: Layer-9 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer7A:
        """
        Purpose:
            Provide a layer-7 dependency that branches to layer-8 nodes.
        Contract:
            Stores references to both layer-8 dependencies.
        """
        def __init__(self, left: _Layer8A, right: _Layer8B) -> None:
            """
            Purpose:
                Capture layer-8 dependencies for layer 7.
            Contract:
                Stores left and right layer-8 references.
            Args:
                left: Layer-8 dependency A.
                right: Layer-8 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer7B:
        """
        Purpose:
            Provide a second layer-7 dependency that branches to layer-8 nodes.
        Contract:
            Stores references to both layer-8 dependencies.
        """
        def __init__(self, left: _Layer8A, right: _Layer8B) -> None:
            """
            Purpose:
                Capture layer-8 dependencies for layer 7.
            Contract:
                Stores left and right layer-8 references.
            Args:
                left: Layer-8 dependency A.
                right: Layer-8 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer6A:
        """
        Purpose:
            Provide a layer-6 dependency that branches to layer-7 nodes.
        Contract:
            Stores references to both layer-7 dependencies.
        """
        def __init__(self, left: _Layer7A, right: _Layer7B) -> None:
            """
            Purpose:
                Capture layer-7 dependencies for layer 6.
            Contract:
                Stores left and right layer-7 references.
            Args:
                left: Layer-7 dependency A.
                right: Layer-7 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer6B:
        """
        Purpose:
            Provide a second layer-6 dependency that branches to layer-7 nodes.
        Contract:
            Stores references to both layer-7 dependencies.
        """
        def __init__(self, left: _Layer7A, right: _Layer7B) -> None:
            """
            Purpose:
                Capture layer-7 dependencies for layer 6.
            Contract:
                Stores left and right layer-7 references.
            Args:
                left: Layer-7 dependency A.
                right: Layer-7 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer5A:
        """
        Purpose:
            Provide a layer-5 dependency that branches to layer-6 nodes.
        Contract:
            Stores references to both layer-6 dependencies.
        """
        def __init__(self, left: _Layer6A, right: _Layer6B) -> None:
            """
            Purpose:
                Capture layer-6 dependencies for layer 5.
            Contract:
                Stores left and right layer-6 references.
            Args:
                left: Layer-6 dependency A.
                right: Layer-6 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer5B:
        """
        Purpose:
            Provide a second layer-5 dependency that branches to layer-6 nodes.
        Contract:
            Stores references to both layer-6 dependencies.
        """
        def __init__(self, left: _Layer6A, right: _Layer6B) -> None:
            """
            Purpose:
                Capture layer-6 dependencies for layer 5.
            Contract:
                Stores left and right layer-6 references.
            Args:
                left: Layer-6 dependency A.
                right: Layer-6 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer4A:
        """
        Purpose:
            Provide a layer-4 dependency that branches to layer-5 nodes.
        Contract:
            Stores references to both layer-5 dependencies.
        """
        def __init__(self, left: _Layer5A, right: _Layer5B) -> None:
            """
            Purpose:
                Capture layer-5 dependencies for layer 4.
            Contract:
                Stores left and right layer-5 references.
            Args:
                left: Layer-5 dependency A.
                right: Layer-5 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer4B:
        """
        Purpose:
            Provide a second layer-4 dependency that branches to layer-5 nodes.
        Contract:
            Stores references to both layer-5 dependencies.
        """
        def __init__(self, left: _Layer5A, right: _Layer5B) -> None:
            """
            Purpose:
                Capture layer-5 dependencies for layer 4.
            Contract:
                Stores left and right layer-5 references.
            Args:
                left: Layer-5 dependency A.
                right: Layer-5 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer3A:
        """
        Purpose:
            Provide a layer-3 dependency that branches to layer-4 nodes.
        Contract:
            Stores references to both layer-4 dependencies.
        """
        def __init__(self, left: _Layer4A, right: _Layer4B) -> None:
            """
            Purpose:
                Capture layer-4 dependencies for layer 3.
            Contract:
                Stores left and right layer-4 references.
            Args:
                left: Layer-4 dependency A.
                right: Layer-4 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer3B:
        """
        Purpose:
            Provide a second layer-3 dependency that branches to layer-4 nodes.
        Contract:
            Stores references to both layer-4 dependencies.
        """
        def __init__(self, left: _Layer4A, right: _Layer4B) -> None:
            """
            Purpose:
                Capture layer-4 dependencies for layer 3.
            Contract:
                Stores left and right layer-4 references.
            Args:
                left: Layer-4 dependency A.
                right: Layer-4 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer2A:
        """
        Purpose:
            Provide a layer-2 dependency that branches to layer-3 nodes.
        Contract:
            Stores references to both layer-3 dependencies.
        """
        def __init__(self, left: _Layer3A, right: _Layer3B) -> None:
            """
            Purpose:
                Capture layer-3 dependencies for layer 2.
            Contract:
                Stores left and right layer-3 references.
            Args:
                left: Layer-3 dependency A.
                right: Layer-3 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Layer2B:
        """
        Purpose:
            Provide a second layer-2 dependency that branches to layer-3 nodes.
        Contract:
            Stores references to both layer-3 dependencies.
        """
        def __init__(self, left: _Layer3A, right: _Layer3B) -> None:
            """
            Purpose:
                Capture layer-3 dependencies for layer 2.
            Contract:
                Stores left and right layer-3 references.
            Args:
                left: Layer-3 dependency A.
                right: Layer-3 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    class _Root:
        """
        Purpose:
            Provide a root object for depth-9 resolution.
        Contract:
            Stores references to both layer-2 dependencies.
        """
        def __init__(self, left: _Layer2A, right: _Layer2B) -> None:
            """
            Purpose:
                Capture layer-2 dependencies at the root.
            Contract:
                Stores left and right layer-2 references.
            Args:
                left: Layer-2 dependency A.
                right: Layer-2 dependency B.
            Returns:
                None.
            """
            self.left = left
            self.right = right

    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook.bind(spell=_Layer9A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer9B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer8A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer8B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer7A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer7B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer6A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer6B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer5A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer5B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer4A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer4B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer3A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer3B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer2A, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Layer2B, existence=Existence.unique, permissions="create")
    spellbook.bind(spell=_Root, existence=Existence.unique, permissions="create")

    conduit = spellbook.conjure(name="root")
    try:
        root = conduit.meld(spell=_Root)
        leaf_left = root.left.left.left.left.left.left.left.left
        leaf_right = root.right.left.left.left.left.left.left.left
        assert leaf_left is leaf_right
        assert leaf_left.marker == "L9A"
        assert root.left.left.left.left.left.left.left.right is root.right.left.left.left.left.left.left.right
        assert root.left.left.left.left.left.left.left.right.marker == "L9B"
        assert root.left is not root.right
    finally:
        conduit.cleanup()
