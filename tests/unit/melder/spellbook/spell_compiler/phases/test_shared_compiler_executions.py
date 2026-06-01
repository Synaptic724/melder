"""Unit tests for current-surface `SharedCompilerExecutions` helpers."""

from types import SimpleNamespace

from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


def test_ensure_codegen_ir_initializes_expected_payload_shape() -> None:
    """Codegen IR storage should initialize with the current phase buckets."""
    artifact = SpellCompilerArtifact("spell-1")

    payload = SharedCompilerExecutions.ensure_codegen_ir(artifact)

    assert payload == {
        "phase2_5": {},
        "phase8_11": {},
        "signatures": {},
    }
    assert artifact._codegen_ir is payload


def test_hash_codegen_signature_is_deterministic_for_equal_inputs() -> None:
    """Codegen signature hashing should stay deterministic for equal ordered inputs."""
    signature_a = SharedCompilerExecutions.hash_codegen_signature(
        "root",
        ("dep", "root"),
        (("row", 1),),
    )
    signature_b = SharedCompilerExecutions.hash_codegen_signature(
        "root",
        ("dep", "root"),
        (("row", 1),),
    )
    signature_c = SharedCompilerExecutions.hash_codegen_signature(
        "root",
        ("root",),
        (("row", 1),),
    )

    assert signature_a == signature_b
    assert signature_a != signature_c


def test_build_phase5_socket_rows_returns_sorted_socket_schema_rows() -> None:
    """Phase-5 socket-row export should produce deterministic sorted primitive rows."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._root_blueprint_phase5 = SimpleNamespace(
        socket_refs=[
            SimpleNamespace(
                node_id="root",
                param_name="z",
                param_path_id=3,
                socket_kind=SimpleNamespace(value=4),
            ),
            SimpleNamespace(
                node_id="dep",
                param_name="a",
                param_path_id=1,
                socket_kind=SimpleNamespace(value=2),
            ),
        ],
    )

    rows = SharedCompilerExecutions.build_phase5_socket_rows(artifact)

    assert rows == (
        ("dep", "a", 1, 2),
        ("root", "z", 3, 4),
    )


def test_reset_phase2_5_codegen_ir_clears_only_phase2_5_segment() -> None:
    """Phase-2-to-5 IR reset should preserve unrelated IR buckets."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._codegen_ir = {
        "phase2_5": {"payload": 1},
        "phase8_11": {"other": 2},
        "signatures": {
            "phase2_5": "sig-a",
            "phase8_11": "sig-b",
        },
    }

    SharedCompilerExecutions.reset_phase2_5_codegen_ir(artifact)

    assert artifact._codegen_ir["phase2_5"] == {}
    assert artifact._codegen_ir["phase8_11"] == {"other": 2}
    assert "phase2_5" not in artifact._codegen_ir["signatures"]
    assert artifact._codegen_ir["signatures"]["phase8_11"] == "sig-b"
