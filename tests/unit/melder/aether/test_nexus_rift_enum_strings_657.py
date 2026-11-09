"""Contract checks for the native Rift policy enum string migration."""

import hashlib
import json
import pickle
from enum import Enum, StrEnum
from typing import Type

import pytest

from melder.nexus.configuration.rift_access_mode import RiftAccessMode
from melder.nexus.configuration.rift_creation_mode import RiftCreationMode
from melder.utilities.helpers.general_helpers import EnumHelpers


@pytest.mark.parametrize("family", [RiftAccessMode, RiftCreationMode])
def test_existing_value_tokens_still_construct_members(family: Type[Enum]) -> None:
    """Old JSON string tokens and by-value construction retain each member."""
    for member in family:
        assert member.name == member.value
        assert family(json.loads(json.dumps(member.value))) is member

    with pytest.raises(ValueError):
        family("not-a-rift-policy")


@pytest.mark.parametrize("family", [RiftAccessMode, RiftCreationMode])
def test_policy_members_support_string_and_json_use(family: Type[Enum]) -> None:
    """Every migrated member exposes its name as its string and JSON value."""
    assert issubclass(family, StrEnum)
    for member in family:
        assert isinstance(member, str)
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert pickle.loads(pickle.dumps(member, protocol=4)) is member


def test_equal_policy_strings_keep_distinct_enum_families() -> None:
    """The requested string equality leaves two distinct runtime families."""
    assert RiftAccessMode.open == "open"
    assert RiftCreationMode.open == "open"
    assert RiftAccessMode.open == RiftCreationMode.open
    assert type(RiftAccessMode.open) is not type(RiftCreationMode.open)


@pytest.mark.parametrize(
    ("target", "foreign", "expected"),
    [
        (RiftAccessMode, RiftCreationMode.open, RiftAccessMode.open),
        (RiftCreationMode, RiftAccessMode.open, RiftCreationMode.open),
        (
            RiftAccessMode,
            RiftCreationMode.token_required,
            RiftAccessMode.token_required,
        ),
        (
            RiftCreationMode,
            RiftAccessMode.token_required,
            RiftCreationMode.token_required,
        ),
    ],
)
@pytest.mark.parametrize("raw_first", [False, True])
def test_native_helper_rejects_equal_foreign_family_after_cache_warming(
    target: Type[Enum],
    foreign: Enum,
    expected: Enum,
    raw_first: bool,
) -> None:
    """A matching raw value never authorizes a member of the other family."""
    EnumHelpers.convert_enum_and_check.cache_clear()
    if raw_first:
        assert EnumHelpers.convert_enum_and_check(expected.name, target) is expected

    with pytest.raises(ValueError):
        EnumHelpers.convert_enum_and_check(foreign, target)

    assert EnumHelpers.convert_enum_and_check(expected.name, target) is expected
    assert EnumHelpers.convert_enum_and_check(expected, target) is expected


def test_pre_migration_protocol_four_pickles_still_load() -> None:
    """Load actual pre-change bytes for every member through their original modules."""
    snapshots = (
        (
            RiftAccessMode.open,
            "8004954d000000000000008c2b6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e726966745f6163636573735f6d6f6465948c0e526966744163636573734d6f646594"
            "93948c046f70656e94859452942e",
        ),
        (
            RiftAccessMode.token_required,
            "80049557000000000000008c2b6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e726966745f6163636573735f6d6f6465948c0e526966744163636573734d6f646594"
            "93948c0e746f6b656e5f726571756972656494859452942e",
        ),
        (
            RiftAccessMode.system_only,
            "80049554000000000000008c2b6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e726966745f6163636573735f6d6f6465948c0e526966744163636573734d6f646594"
            "93948c0b73797374656d5f6f6e6c7994859452942e",
        ),
        (
            RiftCreationMode.open,
            "80049551000000000000008c2d6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e726966745f6372656174696f6e5f6d6f6465948c10526966744372656174696f6e4d"
            "6f64659493948c046f70656e94859452942e",
        ),
        (
            RiftCreationMode.token_required,
            "8004955b000000000000008c2d6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e726966745f6372656174696f6e5f6d6f6465948c10526966744372656174696f6e4d"
            "6f64659493948c0e746f6b656e5f726571756972656494859452942e",
        ),
        (
            RiftCreationMode.prebuilt_only,
            "8004955a000000000000008c2d6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e726966745f6372656174696f6e5f6d6f6465948c10526966744372656174696f6e4d"
            "6f64659493948c0d7072656275696c745f6f6e6c7994859452942e",
        ),
    )
    payloads = [bytes.fromhex(encoded) for _, encoded in snapshots]
    assert hashlib.sha256(b"".join(payloads)).hexdigest() == (
        "ec828d9f741039d534a725f86923f44c703adfa178b1b2a58e1337cea56cd3d3"
    )
    for (expected, _), payload in zip(snapshots, payloads):
        assert pickle.loads(payload) is expected
