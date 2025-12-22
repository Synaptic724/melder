"""
Test helper factory classes for spellbook integration and unit tests.

These classes model simple factory spells and their products to support
DI resolution and SpellMap scenarios without introducing module globals.
"""


class BuiltArtifact:
    """
    Purpose:
        Provide a simple product type returned by factory spells.
    Contract:
        - Stores a stable marker for assertions.
        - Carries no external dependencies.
    """

    def __init__(self, marker: str) -> None:
        """
        Purpose:
            Initialize the built artifact with a marker.
        Contract:
            Stores the provided marker on the instance.
        Args:
            marker: Identifier used for assertions.
        Returns:
            None.
        """
        self.marker = marker


class BuiltPair:
    """
    Purpose:
        Provide a product type with two markers.
    Contract:
        - Stores both markers for multi-arg override tests.
    """

    def __init__(self, left: str, right: str) -> None:
        """
        Purpose:
            Initialize the built pair markers.
        Contract:
            Stores both markers on the instance.
        Args:
            left: Left-side marker.
            right: Right-side marker.
        Returns:
            None.
        """
        self.left = left
        self.right = right


class BasicFactory:
    """
    Purpose:
        Provide a factory spell that returns a basic artifact.
    Contract:
        - build() returns a BuiltArtifact with a fixed marker.
    """

    def build(self) -> BuiltArtifact:
        """
        Purpose:
            Construct a basic built artifact.
        Contract:
            Returns a BuiltArtifact with marker 'built'.
        Returns:
            BuiltArtifact: Newly created artifact instance.
        """
        return BuiltArtifact('built')


class NamedFactory:
    """
    Purpose:
        Provide a factory spell that accepts a marker override.
    Contract:
        - build_named returns a BuiltArtifact using the provided marker.
    """

    def build_named(self, marker: str) -> BuiltArtifact:
        """
        Purpose:
            Construct a built artifact with a caller-supplied marker.
        Contract:
            Returns a BuiltArtifact with the provided marker.
        Args:
            marker: Identifier passed into the built artifact.
        Returns:
            BuiltArtifact: Newly created artifact instance.
        """
        return BuiltArtifact(marker)


class PairFactory:
    """
    Purpose:
        Provide a factory spell that returns a two-marker product.
    Contract:
        - build_pair returns a BuiltPair from the provided markers.
    """

    def build_pair(self, left: str, right: str) -> BuiltPair:
        """
        Purpose:
            Construct a built pair with two markers.
        Contract:
            Returns a BuiltPair with the provided markers.
        Args:
            left: Left-side marker.
            right: Right-side marker.
        Returns:
            BuiltPair: Newly created pair instance.
        """
        return BuiltPair(left, right)


class CountingFactory:
    """
    Purpose:
        Provide a factory spell that tracks invocation count.
    Contract:
        - Each build call increments the internal counter.
        - The counter starts at zero.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the invocation counter.
        Contract:
            Sets calls to zero.
        Returns:
            None.
        """
        self.calls = 0

    def build(self) -> BuiltArtifact:
        """
        Purpose:
            Construct a built artifact and track the call.
        Contract:
            - Increments calls by one.
            - Returns a BuiltArtifact with marker 'counted'.
        Returns:
            BuiltArtifact: Newly created artifact instance.
        """
        self.calls += 1
        return BuiltArtifact('counted')


class ServiceWithArtifact:
    """
    Purpose:
        Provide a service that depends on a built artifact.
    Contract:
        - Stores the injected artifact for assertions.
    """

    def __init__(self, artifact: BuiltArtifact) -> None:
        """
        Purpose:
            Capture the built artifact dependency.
        Contract:
            Stores the artifact on the instance.
        Args:
            artifact: Built artifact injected by DI.
        Returns:
            None.
        """
        self.artifact = artifact
