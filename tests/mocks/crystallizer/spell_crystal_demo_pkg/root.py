"""
Physical root module used by `SpellCrystal` graph-walk tests.
"""

from .nested.provider import NestedDependency
from .shared import SharedDependency


class RootService:
    """
    Minimal root service with two direct physical module dependencies.
    """

    shared_type = SharedDependency
    nested_type = NestedDependency

    def read(self) -> tuple[str, str]:
        """
        Return both dependency markers.
        """
        return SharedDependency().read(), NestedDependency().read()
