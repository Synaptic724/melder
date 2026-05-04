from typing import runtime_checkable, Protocol, Dict, Any

from melder.utilities.interfaces.assets.ispellgeneralprofile import ISpellGeneralProfile


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
