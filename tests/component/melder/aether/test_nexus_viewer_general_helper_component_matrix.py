from typing import Dict, List, Optional

import pytest

from melder.nexus.acl.frame_acl_compiler import FrameACLCompiler
from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.nexus.acl.configurations.profiles.rules.frame_acl_rule import FrameACLRule
from melder.nexus.acl.configurations.profiles.rules.frame_acl_ruleset import FrameACLRuleSet
from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.nexus.frame_acl_manager import FrameACLManager
from melder.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from tests._nexus_viewer_matrix_support import (
    build_descriptor,
    build_projection_backed_viewer_from_state,
)


def _profile_by_name(profile_name: str) -> FrameACLViewProfile:
    if profile_name == "safe":
        return FrameACLViewProfile.create_safe()
    if profile_name == "hybrid":
        return FrameACLViewProfile.create_hybrid()
    if profile_name == "permissive":
        return FrameACLViewProfile.create_permissive()
    raise ValueError(profile_name)


def _build_configuration(
        profile_name: str,
        *,
        frame_rules: Optional[List[FrameACLRule]] = None,
        conduit_rules: Optional[List[FrameACLRule]] = None,
        spell_rules: Optional[List[FrameACLRule]] = None,
) -> FrameACLConfiguration:
    configuration = FrameACLConfiguration.create_new_from_acl_configuration(
        FrameACLConfiguration.create_default("ops"),
        reason="matrix",
    )
    configuration.set_view_configuration(
        FrameACLViewConfiguration.from_profile(
            _profile_by_name(profile_name),
            frame_override_ruleset=FrameACLRuleSet(
                "{0}_frame_override".format(profile_name),
                rules=frame_rules or [],
            ),
            conduit_override_ruleset=FrameACLRuleSet(
                "{0}_conduit_override".format(profile_name),
                rules=conduit_rules or [],
            ),
            spell_override_ruleset=FrameACLRuleSet(
                "{0}_spell_override".format(profile_name),
                rules=spell_rules or [],
            ),
        )
    )
    configuration.finalize()
    return configuration


def _build_compiled_viewer(
        profile_name: str,
        *,
        payload_type: str,
        frame_rules: Optional[List[FrameACLRule]] = None,
        conduit_rules: Optional[List[FrameACLRule]] = None,
        spell_rules: Optional[List[FrameACLRule]] = None,
) -> FrameViewer:
    manager = FrameACLManager()
    compiler = FrameACLCompiler(manager.frame_acl_profile_builder)
    descriptor = build_descriptor("ops", spell_payload_types=(payload_type,), conduit_count=1)
    configuration = _build_configuration(
        profile_name,
        frame_rules=frame_rules,
        conduit_rules=conduit_rules,
        spell_rules=spell_rules,
    )
    compiled_surface = compiler.compile_frame_access_surface(
        descriptor,
        configuration,
    )
    return build_projection_backed_viewer_from_state(
        "ops",
        descriptor,
        configuration,
        compiled_surface,
    )


SPELL_DETAIL_COMPONENT_CASES = [
    ("safe", "general", "payload_not_detailed"),
    ("hybrid", "general", "payload_not_detailed"),
    ("permissive", "general", "payload_not_detailed"),
    ("safe", "detailed", "acl_restricted"),
    ("hybrid", "detailed", "available"),
    ("permissive", "detailed", "available"),
    ("safe", "general", "payload_not_detailed"),
    ("hybrid", "general", "payload_not_detailed"),
    ("permissive", "general", "payload_not_detailed"),
    ("safe", "detailed", "acl_restricted"),
]


@pytest.mark.parametrize(
    ("profile_name", "payload_type", "expected_reason"),
    SPELL_DETAIL_COMPONENT_CASES,
)
def test_component_spell_detail_matrix(
        profile_name: str,
        payload_type: str,
        expected_reason: str,
) -> None:
    viewer = _build_compiled_viewer(
        profile_name,
        payload_type=payload_type,
    )

    detail = viewer.describe_spell_detail(
        frame_name="ops",
        spell_source_id="ops-spellbook:ops-spell-1",
    )

    assert detail["reason"] == expected_reason


CONDUIT_ACCESS_COMPONENT_CASES = [
    ("safe", False, False),
    ("hybrid", True, True),
    ("permissive", True, True),
    ("safe", False, False),
    ("hybrid", True, True),
    ("permissive", True, True),
    ("safe", False, False),
    ("hybrid", True, True),
    ("permissive", True, True),
    ("safe", False, False),
]


@pytest.mark.parametrize(
    ("profile_name", "expect_policy", "expect_peers"),
    CONDUIT_ACCESS_COMPONENT_CASES,
)
def test_component_conduit_access_matrix(
        profile_name: str,
        expect_policy: bool,
        expect_peers: bool,
) -> None:
    viewer = _build_compiled_viewer(
        profile_name,
        payload_type="general",
    )

    explanation = viewer.explain_conduit_access(
        frame_name="ops",
        conduit_id="ops-conduit-1",
    )

    assert explanation["policy_visible"] is expect_policy
    assert explanation["peer_links_visible"] is expect_peers


FRAME_ACCESS_COMPONENT_CASES = [
    ("safe", None, True),
    ("hybrid", None, True),
    ("permissive", None, True),
    (
        "safe",
        [
            FrameACLRule(
                rule_name="hide_frame_payload",
                operation="show_payload",
                effect="deny",
            )
        ],
        False,
    ),
    (
        "hybrid",
        [
            FrameACLRule(
                rule_name="hide_frame_payload",
                operation="show_payload",
                effect="deny",
            )
        ],
        False,
    ),
    (
        "permissive",
        [
            FrameACLRule(
                rule_name="hide_frame_payload",
                operation="show_payload",
                effect="deny",
            )
        ],
        False,
    ),
    ("safe", None, True),
    ("hybrid", None, True),
    ("permissive", None, True),
    ("safe", None, True),
]


@pytest.mark.parametrize(
    ("profile_name", "frame_rules", "expect_payload"),
    FRAME_ACCESS_COMPONENT_CASES,
)
def test_component_frame_access_matrix(
        profile_name: str,
        frame_rules: list[FrameACLRule] | None,
        expect_payload: bool,
) -> None:
    viewer = _build_compiled_viewer(
        profile_name,
        payload_type="general",
        frame_rules=frame_rules,
    )

    contract = viewer.describe_frame_access_contract(
        frame_name="ops",
    )

    assert (len(contract["frame_payload_fields"]) > 0) is expect_payload


VIEWER_ROUTE_COMPONENT_CASES = [
    ("describe_frame_inventory", {"frame_name": "ops"}, "frame_name"),
    ("describe_frame_access_contract", {"frame_name": "ops"}, "view_profile_name"),
    ("describe_frame_payload", {"frame_name": "ops"}, "payload"),
    ("describe_conduits", {"frame_name": "ops"}, None),
    ("describe_spells", {"frame_name": "ops"}, None),
    ("explain_spell_access", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "reason"),
    ("explain_conduit_access", {"frame_name": "ops", "conduit_id": "ops-conduit-1"}, "reason"),
    ("describe_conduit_topology", {"frame_name": "ops", "conduit_id": "ops-conduit-1"}, "spell_count"),
    ("describe_spell_payload", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "payload_type"),
    ("describe_spell_detail", {"frame_name": "ops", "spell_source_id": "ops-spellbook:ops-spell-1"}, "reason"),
]


@pytest.mark.parametrize(
    ("tool_name", "kwargs", "expected_key"),
    VIEWER_ROUTE_COMPONENT_CASES * 2,
)
def test_component_viewer_route_matrix(
        tool_name: str,
        kwargs: Dict[str, object],
        expected_key: Optional[str],
) -> None:
    viewer = _build_compiled_viewer(
        "hybrid",
        payload_type="detailed",
    )

    result = getattr(viewer, tool_name)(**kwargs)

    if expected_key is None:
        assert len(result) >= 1
    else:
        assert expected_key in result
