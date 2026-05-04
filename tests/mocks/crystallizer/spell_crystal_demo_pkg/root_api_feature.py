"""
API-feature root used by `SpellCrystal` physical-graph tests.
"""

from .api.feature import ApiFeatureDependency


class ApiFeatureRootService:
    """
    Root service that starts one layer below the API surface.
    """

    feature_type = ApiFeatureDependency
