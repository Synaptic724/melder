"""String, binding and historical-pickle contracts for SpellframeKind."""

import hashlib
import json
import pickle
from enum import StrEnum
from typing import Optional, Protocol, Tuple

import pytest

from melder.aether.spellbook.bind.binding_manifest import BindingManifest
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellframe_kind.spellframe_kind import SpellframeKind


class ExampleProtocol(Protocol):
    """A protocol frame used to verify the actual kind signature."""

    def serve(self) -> str:
        """Return a marker."""
        ...


def test_spellframe_kind_is_string_backed_without_changing_values() -> None:
    """Every member retains its declared name/value and gains string behavior."""
    assert issubclass(SpellframeKind, StrEnum)
    assert [member.name for member in SpellframeKind] == ["none", "category", "contract"]
    for member in SpellframeKind:
        assert member.name == member.value
        assert SpellframeKind(member.value) is member
        assert str(member) == member.name
        assert json.loads(json.dumps(member)) == member.name
        assert pickle.loads(pickle.dumps(member, protocol=4)) is member

    with pytest.raises(ValueError):
        SpellframeKind("unknown-frame-kind")


@pytest.mark.parametrize(
    ("frame", "kind", "signature", "binding_hash"),
    [
        (
            None,
            SpellframeKind.none,
            ("none", "example", "__default__"),
            "ed1d1f634fcdbdf53498c96519da9667be410a9a18783f27b7c19a12888a05b0",
        ),
        (
            "example",
            SpellframeKind.category,
            ("category", "example", "__default__"),
            "b72eba061eaa6006f2c62942954713b9bc5237bf6f851f1b0569e650fe7e6d67",
        ),
    ],
)
def test_binding_signature_and_manifest_hash_keep_prechange_values(
    frame: Optional[str],
    kind: SpellframeKind,
    signature: Tuple[str, str, str],
    binding_hash: str,
) -> None:
    """Real signature and manifest builders retain their pre-change output."""
    assert SpellIndex.signature_of(
        spellframe=frame, spell_name="Example", binding_name=None,
    ) == signature
    manifest = BindingManifest.build(
        key=("example", "example"),
        spellframe=frame,
        spellframe_kind=kind,
        binding_name=None,
        existence=Existence.unique,
        disposal_method_names=(),
        resolvable=True,
        managed_spell_mode=None,
        managed_spell_limit=None,
        managed_spell_timeout_seconds=None,
        managed_spell_reset_methods=(),
    )
    assert manifest.binding_hash == binding_hash


def test_protocol_signature_stays_a_contract() -> None:
    """A protocol frame still produces the contract signature, not category."""
    assert SpellIndex.signature_of(
        spellframe=ExampleProtocol, spell_name="Example", binding_name=None,
    ) == ("contract", "exampleprotocol", "__default__")


def test_pre_migration_protocol_four_pickles_still_load() -> None:
    """Read all three actual pre-change enum payloads through the original module."""
    snapshots = (
        (
            SpellframeKind.none,
            "80049559000000000000008c376d656c6465722e6165746865722e7370656c6c626f6f6b2e"
            "7370656c6c6672616d655f6b696e642e7370656c6c6672616d655f6b696e64948c0e537065"
            "6c6c6672616d654b696e649493948c046e6f6e6594859452942e",
        ),
        (
            SpellframeKind.category,
            "8004955d000000000000008c376d656c6465722e6165746865722e7370656c6c626f6f6b2e"
            "7370656c6c6672616d655f6b696e642e7370656c6c6672616d655f6b696e64948c0e537065"
            "6c6c6672616d654b696e649493948c0863617465676f727994859452942e",
        ),
        (
            SpellframeKind.contract,
            "8004955d000000000000008c376d656c6465722e6165746865722e7370656c6c626f6f6b2e"
            "7370656c6c6672616d655f6b696e642e7370656c6c6672616d655f6b696e64948c0e537065"
            "6c6c6672616d654b696e649493948c08636f6e747261637494859452942e",
        ),
    )
    payloads = [bytes.fromhex(encoded) for _, encoded in snapshots]
    assert hashlib.sha256(b"".join(payloads)).hexdigest() == (
        "9779f59fdf3a6ca502462e3d382fd53c5b67be1693d1bbc20aeaf36aab019846"
    )
    for (expected, _), payload in zip(snapshots, payloads):
        assert pickle.loads(payload) is expected
