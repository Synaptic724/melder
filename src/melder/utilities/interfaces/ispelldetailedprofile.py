from typing import Any, Dict, Protocol, runtime_checkable
from melder.utilities.interfaces.ispellgeneralprofile import ISpellGeneralProfile

@runtime_checkable
class ISpellDetailedProfile(ISpellGeneralProfile, Protocol):
    """
    Structural contract for the richer detailed spell profile.

    Purpose:
        Extend the general profile with deep class/callable/member inspection
        payloads for richer downstream consumers.
    """

    class_profile: Any
    callable_profile: Any
    metadata: Dict[str, Any]
    instance_members: Dict[str, Any]
    dynamic_access: Dict[str, bool]
