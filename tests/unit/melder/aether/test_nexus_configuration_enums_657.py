"""Contracts for Nexus and Rift configuration enum string inputs."""

import json
import pickle
from enum import Enum, StrEnum
from typing import Type, Union

import pytest

from melder.nexus.configuration.nexus_configuration import NexusConfiguration
from melder.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.nexus.configuration.rift_configuration import RiftConfiguration
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.configuration.rift_validation_mode import RiftValidationMode
from melder.utilities.helpers.general_helpers import EnumHelpers


class ForeignRoom(StrEnum):
    """An unrelated family whose values overlap a supported room selector."""

    dynamic = "dynamic"
    codegen = "codegen"


class StringSelector(str):
    """An ordinary string subclass accepted by the existing selector boundary."""


@pytest.mark.parametrize(
    "family", [NexusFrameMode, RiftSpaceType, RiftValidationMode],
)
def test_configuration_enum_preserves_value_tokens_and_supports_strings(
    family: Type[Enum],
) -> None:
    """Names, values, by-value lookup, string rendering and JSON stay coherent."""
    assert issubclass(family, StrEnum)
    for member in family:
        assert member.name == member.value
        assert family(member.value) is member
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert pickle.loads(pickle.dumps(member, protocol=4)) is member

    with pytest.raises(ValueError):
        family("not-a-config-mode")


@pytest.mark.parametrize(
    ("configuration_type", "key"),
    [
        (NexusConfiguration, "default_space_type"),
        (RiftConfiguration, "space_type"),
    ],
)
def test_legacy_dynamic_alias_accepts_strings_but_rejects_foreign_enums(
    configuration_type: Type[Union[NexusConfiguration, RiftConfiguration]],
    key: str,
) -> None:
    """The legacy alias is a string input, not a bypass for another family."""
    configuration = configuration_type()
    EnumHelpers.convert_enum_and_check.cache_clear()

    configuration.set_property(key, StringSelector("dynamic"))
    assert configuration.get_property(key) is RiftSpaceType.codegen

    for foreign in (ForeignRoom.dynamic, ForeignRoom.codegen):
        with pytest.raises(ValueError, match="Expected a string or RiftSpaceType member"):
            configuration.set_property(key, foreign)
        assert configuration.get_property(key) is RiftSpaceType.codegen

    configuration.set_property(key, RiftSpaceType.static)
    assert configuration.get_property(key) is RiftSpaceType.static
    configuration.cleanup()


def test_dynamic_is_a_configuration_alias_not_an_enum_value() -> None:
    """Direct by-value construction keeps refusing the legacy configuration alias."""
    with pytest.raises(ValueError):
        RiftSpaceType("dynamic")


@pytest.mark.parametrize(
    ("expected", "payload_hex"),
    [
        (
            NexusFrameMode.single,
            "8004954f000000000000008c2b6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e6e657875735f6672616d655f6d6f6465948c0e4e657875734672616d654d6f646594"
            "93948c0673696e676c6594859452942e",
        ),
        (
            RiftSpaceType.static,
            "8004954d000000000000008c2a6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e726966745f73706163655f74797065948c0d52696674537061636554797065949394"
            "8c0673746174696394859452942e",
        ),
        (
            RiftValidationMode.strict,
            "80049557000000000000008c2f6d656c6465722e6e657875732e636f6e6669677572617469"
            "6f6e2e726966745f76616c69646174696f6e5f6d6f6465948c125269667456616c69646174"
            "696f6e4d6f64659493948c0673747269637494859452942e",
        ),
    ],
)
def test_actual_pre_migration_pickle_still_loads(
    expected: Enum,
    payload_hex: str,
) -> None:
    """Historical protocol-4 payloads resolve through their original modules."""
    assert pickle.loads(bytes.fromhex(payload_hex)) is expected
