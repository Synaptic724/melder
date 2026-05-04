import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class IFrameACLCodegenConfiguration(ICleanable, Protocol):
    """
    Typed frame codegen ACL configuration contract.

    Contract:
        - Carries one codegen-policy profile identity/version pair.
        - Owns detached frame, conduit, spell, and capability override rulesets.
        - Represents the codegen-side sibling inside a frame ACL bundle.
        - Is configuration data only; it does not validate or execute codegen
          work by itself.
    """

    configuration_id: str
    source_configuration_id: Optional[str]
    previous_configuration_id: Optional[str]
    created_at: str
    reason: str
    locked: bool
    profile_name: str
    profile_version: str
    precision_profile_name: Optional[str]
    precision_profile_version: Optional[str]
    frame_override_ruleset: IFrameACLRuleSet
    conduit_override_ruleset: IFrameACLRuleSet
    spell_override_ruleset: IFrameACLRuleSet
    capability_override_ruleset: IFrameACLRuleSet

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Return the configuration as a JSON-compatible dictionary.

        Returns:
            Dict[str, Any]: JSON-compatible configuration payload.
        """
        ...

    def to_json_string(self) -> str:
        """
        Return the configuration as a normalized JSON string.

        Returns:
            str: Normalized JSON payload string.
        """
        ...

    def clone(self) -> "IFrameACLCodegenConfiguration":
        """
        Return a detached configuration copy.

        Returns:
            IFrameACLCodegenConfiguration: Detached configuration copy.
        """
        ...

    def finalize(self) -> None:
        """
        Lock the configuration against further mutation.

        Returns:
            None.
        """
        ...

    def set_profiles(
            self,
            profile: IFrameACLCodegenProfile,
            *,
            precision_profile: Optional[IFrameACLCodegenProfile] = None,
    ) -> None:
        """
        Replace the base and optional precision profiles on the mutable config.

        Returns:
            None.
        """
        ...
