from typing import runtime_checkable, Protocol

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IFrameACLViewProfile(ICleanable, Protocol):
    """
    Reusable view-side ACL profile contract.
    """

    name: str
    version: str
    validation_strategy_name: str
    required_nexus_label: str
    required_nexus_version: str
    minimum_spell_payload_type: str
    minimum_spell_payload_version: str
    frame_ruleset: IFrameACLRuleSet
    conduit_ruleset: IFrameACLRuleSet
    spell_ruleset: IFrameACLRuleSet
    member_ruleset: IFrameACLRuleSet
