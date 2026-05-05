from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iframeaclruleset import IFrameACLRuleSet

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
