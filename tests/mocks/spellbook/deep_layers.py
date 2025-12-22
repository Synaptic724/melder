"""
Purpose:
    Provide reusable deep dependency graph classes for integration tests.
Contract:
    - Classes are deterministic and store only dependency references.
    - Leaf nodes expose stable marker values for identity checks.
Args:
    None.
Returns:
    None.
"""


class Depth3LeafA:
    """
    Purpose:
        Provide a leaf dependency for depth-3 graphs.
    Contract:
        - Exposes marker 'L3A' for identity checks.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the leaf marker.
        Contract:
            - Sets marker to 'L3A'.
        Returns:
            None.
        """
        self.marker = 'L3A'


class Depth3LeafB:
    """
    Purpose:
        Provide a leaf dependency for depth-3 graphs.
    Contract:
        - Exposes marker 'L3B' for identity checks.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the leaf marker.
        Contract:
            - Sets marker to 'L3B'.
        Returns:
            None.
        """
        self.marker = 'L3B'


class Depth3Layer2A:
    """
    Purpose:
        Provide a layer-2 branch node for depth-3 graphs.
    Contract:
        - Stores left and right leaf dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth3LeafA, right: Depth3LeafB) -> None:
        """
        Purpose:
            Capture leaf dependencies for the layer-2 node.
        Contract:
            - Stores left and right leaf references.
        Args:
            left: Depth-3 leaf A dependency.
            right: Depth-3 leaf B dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth3Layer2B:
    """
    Purpose:
        Provide a layer-2 branch node for depth-3 graphs.
    Contract:
        - Stores left and right leaf dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth3LeafA, right: Depth3LeafB) -> None:
        """
        Purpose:
            Capture leaf dependencies for the layer-2 node.
        Contract:
            - Stores left and right leaf references.
        Args:
            left: Depth-3 leaf A dependency.
            right: Depth-3 leaf B dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth3Root:
    """
    Purpose:
        Provide a root node for depth-3 graphs.
    Contract:
        - Stores left and right layer-2 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth3Layer2A, right: Depth3Layer2B) -> None:
        """
        Purpose:
            Capture layer-2 dependencies for the root node.
        Contract:
            - Stores left and right layer-2 references.
        Args:
            left: Depth-3 layer-2 node A.
            right: Depth-3 layer-2 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth5LeafA:
    """
    Purpose:
        Provide a leaf dependency for depth-5 graphs.
    Contract:
        - Exposes marker 'L5A' for identity checks.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the leaf marker.
        Contract:
            - Sets marker to 'L5A'.
        Returns:
            None.
        """
        self.marker = 'L5A'


class Depth5LeafB:
    """
    Purpose:
        Provide a leaf dependency for depth-5 graphs.
    Contract:
        - Exposes marker 'L5B' for identity checks.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the leaf marker.
        Contract:
            - Sets marker to 'L5B'.
        Returns:
            None.
        """
        self.marker = 'L5B'


class Depth5Layer4A:
    """
    Purpose:
        Provide a layer-4 branch node for depth-5 graphs.
    Contract:
        - Stores left and right leaf dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth5LeafA, right: Depth5LeafB) -> None:
        """
        Purpose:
            Capture leaf dependencies for the layer-4 node.
        Contract:
            - Stores left and right leaf references.
        Args:
            left: Depth-5 leaf A dependency.
            right: Depth-5 leaf B dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth5Layer4B:
    """
    Purpose:
        Provide a layer-4 branch node for depth-5 graphs.
    Contract:
        - Stores left and right leaf dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth5LeafA, right: Depth5LeafB) -> None:
        """
        Purpose:
            Capture leaf dependencies for the layer-4 node.
        Contract:
            - Stores left and right leaf references.
        Args:
            left: Depth-5 leaf A dependency.
            right: Depth-5 leaf B dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth5Layer3A:
    """
    Purpose:
        Provide a layer-3 branch node for depth-5 graphs.
    Contract:
        - Stores left and right layer-4 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth5Layer4A, right: Depth5Layer4B) -> None:
        """
        Purpose:
            Capture layer-4 dependencies for the layer-3 node.
        Contract:
            - Stores left and right layer-4 references.
        Args:
            left: Depth-5 layer-4 node A.
            right: Depth-5 layer-4 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth5Layer3B:
    """
    Purpose:
        Provide a layer-3 branch node for depth-5 graphs.
    Contract:
        - Stores left and right layer-4 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth5Layer4A, right: Depth5Layer4B) -> None:
        """
        Purpose:
            Capture layer-4 dependencies for the layer-3 node.
        Contract:
            - Stores left and right layer-4 references.
        Args:
            left: Depth-5 layer-4 node A.
            right: Depth-5 layer-4 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth5Layer2A:
    """
    Purpose:
        Provide a layer-2 branch node for depth-5 graphs.
    Contract:
        - Stores left and right layer-3 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth5Layer3A, right: Depth5Layer3B) -> None:
        """
        Purpose:
            Capture layer-3 dependencies for the layer-2 node.
        Contract:
            - Stores left and right layer-3 references.
        Args:
            left: Depth-5 layer-3 node A.
            right: Depth-5 layer-3 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth5Layer2B:
    """
    Purpose:
        Provide a layer-2 branch node for depth-5 graphs.
    Contract:
        - Stores left and right layer-3 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth5Layer3A, right: Depth5Layer3B) -> None:
        """
        Purpose:
            Capture layer-3 dependencies for the layer-2 node.
        Contract:
            - Stores left and right layer-3 references.
        Args:
            left: Depth-5 layer-3 node A.
            right: Depth-5 layer-3 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth5Root:
    """
    Purpose:
        Provide a root node for depth-5 graphs.
    Contract:
        - Stores left and right layer-2 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth5Layer2A, right: Depth5Layer2B) -> None:
        """
        Purpose:
            Capture layer-2 dependencies for the root node.
        Contract:
            - Stores left and right layer-2 references.
        Args:
            left: Depth-5 layer-2 node A.
            right: Depth-5 layer-2 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7LeafA:
    """
    Purpose:
        Provide a leaf dependency for depth-7 graphs.
    Contract:
        - Exposes marker 'L7A' for identity checks.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the leaf marker.
        Contract:
            - Sets marker to 'L7A'.
        Returns:
            None.
        """
        self.marker = 'L7A'


class Depth7LeafB:
    """
    Purpose:
        Provide a leaf dependency for depth-7 graphs.
    Contract:
        - Exposes marker 'L7B' for identity checks.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the leaf marker.
        Contract:
            - Sets marker to 'L7B'.
        Returns:
            None.
        """
        self.marker = 'L7B'


class Depth7Layer6A:
    """
    Purpose:
        Provide a layer-6 branch node for depth-7 graphs.
    Contract:
        - Stores left and right leaf dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7LeafA, right: Depth7LeafB) -> None:
        """
        Purpose:
            Capture leaf dependencies for the layer-6 node.
        Contract:
            - Stores left and right leaf references.
        Args:
            left: Depth-7 leaf A dependency.
            right: Depth-7 leaf B dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer6B:
    """
    Purpose:
        Provide a layer-6 branch node for depth-7 graphs.
    Contract:
        - Stores left and right leaf dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7LeafA, right: Depth7LeafB) -> None:
        """
        Purpose:
            Capture leaf dependencies for the layer-6 node.
        Contract:
            - Stores left and right leaf references.
        Args:
            left: Depth-7 leaf A dependency.
            right: Depth-7 leaf B dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer5A:
    """
    Purpose:
        Provide a layer-5 branch node for depth-7 graphs.
    Contract:
        - Stores left and right layer-6 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer6A, right: Depth7Layer6B) -> None:
        """
        Purpose:
            Capture layer-6 dependencies for the layer-5 node.
        Contract:
            - Stores left and right layer-6 references.
        Args:
            left: Depth-7 layer-6 node A.
            right: Depth-7 layer-6 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer5B:
    """
    Purpose:
        Provide a layer-5 branch node for depth-7 graphs.
    Contract:
        - Stores left and right layer-6 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer6A, right: Depth7Layer6B) -> None:
        """
        Purpose:
            Capture layer-6 dependencies for the layer-5 node.
        Contract:
            - Stores left and right layer-6 references.
        Args:
            left: Depth-7 layer-6 node A.
            right: Depth-7 layer-6 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer4A:
    """
    Purpose:
        Provide a layer-4 branch node for depth-7 graphs.
    Contract:
        - Stores left and right layer-5 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer5A, right: Depth7Layer5B) -> None:
        """
        Purpose:
            Capture layer-5 dependencies for the layer-4 node.
        Contract:
            - Stores left and right layer-5 references.
        Args:
            left: Depth-7 layer-5 node A.
            right: Depth-7 layer-5 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer4B:
    """
    Purpose:
        Provide a layer-4 branch node for depth-7 graphs.
    Contract:
        - Stores left and right layer-5 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer5A, right: Depth7Layer5B) -> None:
        """
        Purpose:
            Capture layer-5 dependencies for the layer-4 node.
        Contract:
            - Stores left and right layer-5 references.
        Args:
            left: Depth-7 layer-5 node A.
            right: Depth-7 layer-5 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer3A:
    """
    Purpose:
        Provide a layer-3 branch node for depth-7 graphs.
    Contract:
        - Stores left and right layer-4 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer4A, right: Depth7Layer4B) -> None:
        """
        Purpose:
            Capture layer-4 dependencies for the layer-3 node.
        Contract:
            - Stores left and right layer-4 references.
        Args:
            left: Depth-7 layer-4 node A.
            right: Depth-7 layer-4 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer3B:
    """
    Purpose:
        Provide a layer-3 branch node for depth-7 graphs.
    Contract:
        - Stores left and right layer-4 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer4A, right: Depth7Layer4B) -> None:
        """
        Purpose:
            Capture layer-4 dependencies for the layer-3 node.
        Contract:
            - Stores left and right layer-4 references.
        Args:
            left: Depth-7 layer-4 node A.
            right: Depth-7 layer-4 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer2A:
    """
    Purpose:
        Provide a layer-2 branch node for depth-7 graphs.
    Contract:
        - Stores left and right layer-3 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer3A, right: Depth7Layer3B) -> None:
        """
        Purpose:
            Capture layer-3 dependencies for the layer-2 node.
        Contract:
            - Stores left and right layer-3 references.
        Args:
            left: Depth-7 layer-3 node A.
            right: Depth-7 layer-3 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Layer2B:
    """
    Purpose:
        Provide a layer-2 branch node for depth-7 graphs.
    Contract:
        - Stores left and right layer-3 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer3A, right: Depth7Layer3B) -> None:
        """
        Purpose:
            Capture layer-3 dependencies for the layer-2 node.
        Contract:
            - Stores left and right layer-3 references.
        Args:
            left: Depth-7 layer-3 node A.
            right: Depth-7 layer-3 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth7Root:
    """
    Purpose:
        Provide a root node for depth-7 graphs.
    Contract:
        - Stores left and right layer-2 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth7Layer2A, right: Depth7Layer2B) -> None:
        """
        Purpose:
            Capture layer-2 dependencies for the root node.
        Contract:
            - Stores left and right layer-2 references.
        Args:
            left: Depth-7 layer-2 node A.
            right: Depth-7 layer-2 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9LeafA:
    """
    Purpose:
        Provide a leaf dependency for depth-9 graphs.
    Contract:
        - Exposes marker 'L9A' for identity checks.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the leaf marker.
        Contract:
            - Sets marker to 'L9A'.
        Returns:
            None.
        """
        self.marker = 'L9A'


class Depth9LeafB:
    """
    Purpose:
        Provide a leaf dependency for depth-9 graphs.
    Contract:
        - Exposes marker 'L9B' for identity checks.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self) -> None:
        """
        Purpose:
            Initialize the leaf marker.
        Contract:
            - Sets marker to 'L9B'.
        Returns:
            None.
        """
        self.marker = 'L9B'


class Depth9Layer8A:
    """
    Purpose:
        Provide a layer-8 branch node for depth-9 graphs.
    Contract:
        - Stores left and right leaf dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9LeafA, right: Depth9LeafB) -> None:
        """
        Purpose:
            Capture leaf dependencies for the layer-8 node.
        Contract:
            - Stores left and right leaf references.
        Args:
            left: Depth-9 leaf A dependency.
            right: Depth-9 leaf B dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer8B:
    """
    Purpose:
        Provide a layer-8 branch node for depth-9 graphs.
    Contract:
        - Stores left and right leaf dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9LeafA, right: Depth9LeafB) -> None:
        """
        Purpose:
            Capture leaf dependencies for the layer-8 node.
        Contract:
            - Stores left and right leaf references.
        Args:
            left: Depth-9 leaf A dependency.
            right: Depth-9 leaf B dependency.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer7A:
    """
    Purpose:
        Provide a layer-7 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-8 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer8A, right: Depth9Layer8B) -> None:
        """
        Purpose:
            Capture layer-8 dependencies for the layer-7 node.
        Contract:
            - Stores left and right layer-8 references.
        Args:
            left: Depth-9 layer-8 node A.
            right: Depth-9 layer-8 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer7B:
    """
    Purpose:
        Provide a layer-7 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-8 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer8A, right: Depth9Layer8B) -> None:
        """
        Purpose:
            Capture layer-8 dependencies for the layer-7 node.
        Contract:
            - Stores left and right layer-8 references.
        Args:
            left: Depth-9 layer-8 node A.
            right: Depth-9 layer-8 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer6A:
    """
    Purpose:
        Provide a layer-6 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-7 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer7A, right: Depth9Layer7B) -> None:
        """
        Purpose:
            Capture layer-7 dependencies for the layer-6 node.
        Contract:
            - Stores left and right layer-7 references.
        Args:
            left: Depth-9 layer-7 node A.
            right: Depth-9 layer-7 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer6B:
    """
    Purpose:
        Provide a layer-6 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-7 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer7A, right: Depth9Layer7B) -> None:
        """
        Purpose:
            Capture layer-7 dependencies for the layer-6 node.
        Contract:
            - Stores left and right layer-7 references.
        Args:
            left: Depth-9 layer-7 node A.
            right: Depth-9 layer-7 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer5A:
    """
    Purpose:
        Provide a layer-5 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-6 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer6A, right: Depth9Layer6B) -> None:
        """
        Purpose:
            Capture layer-6 dependencies for the layer-5 node.
        Contract:
            - Stores left and right layer-6 references.
        Args:
            left: Depth-9 layer-6 node A.
            right: Depth-9 layer-6 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer5B:
    """
    Purpose:
        Provide a layer-5 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-6 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer6A, right: Depth9Layer6B) -> None:
        """
        Purpose:
            Capture layer-6 dependencies for the layer-5 node.
        Contract:
            - Stores left and right layer-6 references.
        Args:
            left: Depth-9 layer-6 node A.
            right: Depth-9 layer-6 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer4A:
    """
    Purpose:
        Provide a layer-4 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-5 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer5A, right: Depth9Layer5B) -> None:
        """
        Purpose:
            Capture layer-5 dependencies for the layer-4 node.
        Contract:
            - Stores left and right layer-5 references.
        Args:
            left: Depth-9 layer-5 node A.
            right: Depth-9 layer-5 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer4B:
    """
    Purpose:
        Provide a layer-4 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-5 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer5A, right: Depth9Layer5B) -> None:
        """
        Purpose:
            Capture layer-5 dependencies for the layer-4 node.
        Contract:
            - Stores left and right layer-5 references.
        Args:
            left: Depth-9 layer-5 node A.
            right: Depth-9 layer-5 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer3A:
    """
    Purpose:
        Provide a layer-3 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-4 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer4A, right: Depth9Layer4B) -> None:
        """
        Purpose:
            Capture layer-4 dependencies for the layer-3 node.
        Contract:
            - Stores left and right layer-4 references.
        Args:
            left: Depth-9 layer-4 node A.
            right: Depth-9 layer-4 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer3B:
    """
    Purpose:
        Provide a layer-3 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-4 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer4A, right: Depth9Layer4B) -> None:
        """
        Purpose:
            Capture layer-4 dependencies for the layer-3 node.
        Contract:
            - Stores left and right layer-4 references.
        Args:
            left: Depth-9 layer-4 node A.
            right: Depth-9 layer-4 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer2A:
    """
    Purpose:
        Provide a layer-2 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-3 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer3A, right: Depth9Layer3B) -> None:
        """
        Purpose:
            Capture layer-3 dependencies for the layer-2 node.
        Contract:
            - Stores left and right layer-3 references.
        Args:
            left: Depth-9 layer-3 node A.
            right: Depth-9 layer-3 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Layer2B:
    """
    Purpose:
        Provide a layer-2 branch node for depth-9 graphs.
    Contract:
        - Stores left and right layer-3 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer3A, right: Depth9Layer3B) -> None:
        """
        Purpose:
            Capture layer-3 dependencies for the layer-2 node.
        Contract:
            - Stores left and right layer-3 references.
        Args:
            left: Depth-9 layer-3 node A.
            right: Depth-9 layer-3 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class Depth9Root:
    """
    Purpose:
        Provide a root node for depth-9 graphs.
    Contract:
        - Stores left and right layer-2 dependencies.
    Args:
        None.
    Returns:
        None.
    """
    def __init__(self, left: Depth9Layer2A, right: Depth9Layer2B) -> None:
        """
        Purpose:
            Capture layer-2 dependencies for the root node.
        Contract:
            - Stores left and right layer-2 references.
        Args:
            left: Depth-9 layer-2 node A.
            right: Depth-9 layer-2 node B.
        Returns:
            None.
        """
        self.left = left
        self.right = right


def get_depth_3_classes() -> tuple[type, ...]:
    """
    Purpose:
        Return the classes required to bind a depth-3 graph.
    Returns:
        tuple[type, ...]: Classes in dependency order for binding.
    """
    return (
        Depth3LeafA,
        Depth3LeafB,
        Depth3Layer2A,
        Depth3Layer2B,
        Depth3Root,
    )


def get_depth_5_classes() -> tuple[type, ...]:
    """
    Purpose:
        Return the classes required to bind a depth-5 graph.
    Returns:
        tuple[type, ...]: Classes in dependency order for binding.
    """
    return (
        Depth5LeafA,
        Depth5LeafB,
        Depth5Layer4A,
        Depth5Layer4B,
        Depth5Layer3A,
        Depth5Layer3B,
        Depth5Layer2A,
        Depth5Layer2B,
        Depth5Root,
    )


def get_depth_7_classes() -> tuple[type, ...]:
    """
    Purpose:
        Return the classes required to bind a depth-7 graph.
    Returns:
        tuple[type, ...]: Classes in dependency order for binding.
    """
    return (
        Depth7LeafA,
        Depth7LeafB,
        Depth7Layer6A,
        Depth7Layer6B,
        Depth7Layer5A,
        Depth7Layer5B,
        Depth7Layer4A,
        Depth7Layer4B,
        Depth7Layer3A,
        Depth7Layer3B,
        Depth7Layer2A,
        Depth7Layer2B,
        Depth7Root,
    )


def get_depth_9_classes() -> tuple[type, ...]:
    """
    Purpose:
        Return the classes required to bind a depth-9 graph.
    Returns:
        tuple[type, ...]: Classes in dependency order for binding.
    """
    return (
        Depth9LeafA,
        Depth9LeafB,
        Depth9Layer8A,
        Depth9Layer8B,
        Depth9Layer7A,
        Depth9Layer7B,
        Depth9Layer6A,
        Depth9Layer6B,
        Depth9Layer5A,
        Depth9Layer5B,
        Depth9Layer4A,
        Depth9Layer4B,
        Depth9Layer3A,
        Depth9Layer3B,
        Depth9Layer2A,
        Depth9Layer2B,
        Depth9Root,
    )
