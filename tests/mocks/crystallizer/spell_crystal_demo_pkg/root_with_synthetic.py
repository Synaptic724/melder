"""
Mixed root module used by component tests for physical/synthetic mapping.
"""

from synthetic_spell_crystal_component_dep import SyntheticDependency

from .shared import SharedDependency


class MixedRootService:
    """
    Root service with one physical and one synthetic direct dependency.
    """

    shared_type = SharedDependency
    synthetic_type = SyntheticDependency

    def read(self) -> tuple[str, str]:
        """
        Return both dependency markers.
        """
        return SharedDependency().read(), SyntheticDependency().read()
