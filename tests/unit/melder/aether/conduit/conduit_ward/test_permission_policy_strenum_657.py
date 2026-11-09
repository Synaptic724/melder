"""Permission/policy exact strings and legacy numeric compatibility."""

import json
import pickle
from enum import Enum, StrEnum

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.helpers.general_helpers import EnumHelpers


@pytest.mark.parametrize(
    ("enum_type", "pickle_prefix"),
    [
        (
            Permissions,
            "80049554000000000000008c3a6d656c6465722e6165746865722e636f6e647569742e636f6e647569745f"
            "776172642e7065726d697373696f6e732e7065726d697373696f6e73948c0b5065726d697373696f6e73"
            "9493944b",
        ),
        (
            Policies,
            "8004954b000000000000008c346d656c6465722e6165746865722e636f6e647569742e636f6e647569745f"
            "776172642e706f6c69636965732e706f6c6963696573948c08506f6c69636965739493944b",
        ),
    ],
)
def test_policy_permission_preserve_old_numeric_and_pickle_inputs(
    enum_type: type[Enum], pickle_prefix: str,
) -> None:
    """Exact string values retain historical numeric and pickle construction."""
    for number, member in enumerate(enum_type, start=1):
        old_pickle = bytes.fromhex(pickle_prefix) + bytes([number]) + bytes.fromhex("859452942e")
        assert isinstance(member, StrEnum)
        assert member.value == member.name
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert enum_type(number) is member
        assert enum_type(float(number)) is member
        assert pickle.loads(old_pickle) is member


@pytest.mark.parametrize("enum_type", [Permissions, Policies])
@pytest.mark.parametrize("invalid", [0, 6, "unknown", None, []])
def test_policy_permission_reject_unknown_values(enum_type: type[Enum], invalid: object) -> None:
    """Unknown values retain the ordinary enum refusal."""
    with pytest.raises(ValueError):
        enum_type(invalid)


@pytest.mark.parametrize("raw_first", [True, False])
def test_enum_helper_keeps_foreign_family_separate_in_both_cache_orders(raw_first: bool) -> None:
    """An equal foreign StrEnum must never reuse a cached raw-string admission."""
    class ForeignPermission(StrEnum):
        create = "create"

    class ForeignPolicy(StrEnum):
        default = "default"

    for family, foreign, token, expected in (
        (Permissions, ForeignPermission.create, "create", Permissions.create),
        (Policies, ForeignPolicy.default, "default", Policies.default),
    ):
        EnumHelpers.convert_enum_and_check.cache_clear()
        if raw_first:
            assert EnumHelpers.convert_enum_and_check(token, family) is expected
        with pytest.raises(ValueError):
            EnumHelpers.convert_enum_and_check(foreign, family)
        assert EnumHelpers.convert_enum_and_check(token, family) is expected
        assert EnumHelpers.convert_enum_and_check(expected, family) is expected
    EnumHelpers.convert_enum_and_check.cache_clear()