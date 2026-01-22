"""
Structure profile models and builders for tooling and diagnostics.

This package exposes object models that summarize spellbook/conduit/frame
structure without enforcing policies. Consumers should apply ACL or
visibility filtering downstream.
"""

from melder.aether.structure_profiles.structure_profile_builder import (
    StructureProfileBuilder,
    StructureProfileTooling,
)
from melder.aether.structure_profiles.structure_profile_models import (
    StructureHint,
    SpellStructureRecord,
    ConduitStructureProfile,
    FrameStructureProfile,
)
