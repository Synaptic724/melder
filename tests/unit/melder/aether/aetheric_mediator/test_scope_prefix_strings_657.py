"""Guard scope-prefix migration without changing transaction isolation keys."""

import base64
import json
import pickle
from enum import StrEnum

import pytest

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.claim_table import ClaimTable
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.scope_keys import ScopeKey, ScopePrefix
from melder.aether.aetheric_mediator.strategies.frame_create_transaction_strategy import (
    FrameCreateTransactionStrategy,
)


class ForeignLegacyScope(StrEnum):
    """Equal legacy strings from an unrelated family cannot select a prefix."""

    WORLD = "world"
    FRAME = "frame"
    SUBSYSTEM = "subsystem"


@pytest.mark.parametrize(
    ("member", "old_value", "old_pickle"),
    (
        (
            ScopePrefix.WORLD,
            "world",
            "gASVSgAAAAAAAACMKm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3Iuc2NvcGVfa2V5c5SMC1Njb3BlUHJlZml4lJOUjAV3b3JsZJSFlFKULg==",
        ),
        (
            ScopePrefix.FRAME,
            "frame",
            "gASVSgAAAAAAAACMKm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3Iuc2NvcGVfa2V5c5SMC1Njb3BlUHJlZml4lJOUjAVmcmFtZZSFlFKULg==",
        ),
        (
            ScopePrefix.SUBSYSTEM,
            "subsystem",
            "gASVTgAAAAAAAACMKm1lbGRlci5hZXRoZXIuYWV0aGVyaWNfbWVkaWF0b3Iuc2NvcGVfa2V5c5SMC1Njb3BlUHJlZml4lJOUjAlzdWJzeXN0ZW2UhZRSlC4=",
        ),
    ),
)
def test_canonical_values_preserve_old_pickle_and_by_value_reads(
        member: ScopePrefix, old_value: str, old_pickle: str,
) -> None:
    """Old serialized tokens resolve while new values exactly match names."""
    assert member.value == member.name
    assert ScopePrefix(member.name) is member
    assert ScopePrefix(old_value) is member
    assert pickle.loads(base64.b64decode(old_pickle)) is member
    assert json.loads(json.dumps(member)) == member.name


@pytest.mark.parametrize("invalid", ("World", " world", "world ", "other", "", 1, None))
def test_scope_prefix_rejects_unknown_and_inexact_values(invalid: object) -> None:
    """The legacy reader does not normalize unrecorded inputs."""
    with pytest.raises(ValueError):
        ScopePrefix(invalid)


@pytest.mark.parametrize("foreign", tuple(ForeignLegacyScope))
def test_scope_prefix_rejects_foreign_legacy_members(foreign: ForeignLegacyScope) -> None:
    """An equal foreign legacy enum does not enter the fallback as a plain string."""
    with pytest.raises(ValueError):
        ScopePrefix(foreign)


def test_scope_builders_keep_the_exact_existing_claim_keys() -> None:
    """New enum values do not split the existing isolation namespace."""
    assert ScopeKey.world() == "world"
    assert ScopeKey.frame("A") == "frame:A"
    assert ScopeKey.subsystem("nexus") == "subsystem:nexus"
    assert ScopeKey.is_world("world")
    assert not ScopeKey.is_world("WORLD")
    with pytest.raises(ValueError):
        ScopeKey.frame("")
    with pytest.raises(ValueError):
        ScopeKey.subsystem("  ")


def test_frame_creation_is_blocked_by_the_existing_world_claim() -> None:
    """The real frame strategy collides with a holder using the old world key."""
    table = ClaimTable()
    try:
        loader = Identity(kind="loader", identity_id="one")
        creator = Identity(kind="agent", identity_id="two")
        plan = FrameCreateTransactionStrategy.build_start_plan(
            submitter=creator, metadata={"frame_name": "A"}
        )
        assert plan == {"world": ClaimMode.INTENT, "frame:A": ClaimMode.EXCLUSIVE}
        assert table.try_acquire(loader, {"world": ClaimMode.EXCLUSIVE}) == ()
        assert table.try_acquire(creator, plan)
        assert table.held_scopes(creator) == ()
        assert table.release_holder(loader) == 1
        assert table.try_acquire(creator, plan) == ()
    finally:
        table.cleanup()
