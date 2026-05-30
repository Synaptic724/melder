"""Unit tests for current-surface compiler phase 8 helper semantics."""

from types import SimpleNamespace
from typing import Any

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_8 as compiler_phase_8_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_8 import (
    CompilerPhase8,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind


class _SpellIndexStub:
    """Hashable SpellIndex stand-in for phase tests."""

    __slots__ = [
        "current",
        "id",
    ]

    def __init__(self, spell_id: str) -> None:
        """Store current and lineage ids."""
        self.current = spell_id
        self.id = "lineage-{0}".format(spell_id)

    def __hash__(self) -> int:
        """Keep the stub usable in dictionaries like real SpellIndex."""
        return hash((self.current, self.id))


def _make_spellbook_stub() -> Any:
    """Build a minimal spellbook stub for phase 8 helper tests."""
    return SimpleNamespace(
        _spell_id_pool={},
        _spells={},
        _spells_by_id={},
        _lookup_contracted_spells={},
        _contracted_spells={},
        _aetheric_frame_configuration=SimpleNamespace(system_state=SystemState.dynamic),
    )


def _make_spell_stub(spell_id: str, *, spellbook: Any) -> Any:
    """Build a minimal spell stub for phase 8 helper tests."""
    spell = SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=_SpellIndexStub(spell_id),
        spell_type=SpellType.SPELL,
        existence=Existence.unique,
        is_existing_creation=False,
        mutation_override=None,
        _mutation_override=None,
        _spellbook=spellbook,
    )
    spellbook._spell_id_pool[spell_id] = spell
    spellbook._spells_by_id[spell_id] = spell
    return spell


def test_build_phase8_occurrence_plan_fast_key_serializes_visible_state_and_rejects_mutations() -> None:
    """Phase 8 fast-key helper should serialize visible state and reject mutation overrides."""
    phase = CompilerPhase8()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)
    dep_spell = _make_spell_stub("dep", spellbook=spellbook)
    spellbook._lookup_contracted_spells = {
        "peer": {
            ("frame", "binding"): dep_spell.spell_index,
        }
    }
    spellbook._contracted_spells = {
        "peer": {
            dep_spell.spell_index: dep_spell,
        }
    }
    spell_system_states = SimpleNamespace(
        _local_topologies={
            "root": SimpleNamespace(
                sockets=[
                    SimpleNamespace(param_name="svc", target_spell_ids=("dep",)),
                ]
            )
        }
    )
    path_registry = object()
    blueprint = SimpleNamespace(
        root_spell_id="root",
        ordered_node_ids=("dep", "root"),
        path_registry=path_registry,
        socket_refs=[
            SimpleNamespace(
                node_id="root",
                param_name="svc",
                param_path_id=7,
                target_spell_ids=("dep",),
                socket_kind=SocketKind.NORMAL,
            )
        ],
    )

    fast_key = phase._build_phase8_occurrence_plan_fast_key(
        root_blueprint=blueprint,
        spell_lookup=spellbook._spell_id_pool,
        spellbook=spellbook,
        spell_system_states=spell_system_states,
    )

    assert fast_key == (
        "root",
        ("dep", "root"),
        id(path_registry),
        (("root", "svc", 7, SocketKind.NORMAL.value),),
        (
            ("dep", "dep", Existence.unique.name, False),
            ("root", "root", Existence.unique.name, False),
        ),
        (("root", (("svc", ("dep",)),)),),
        SystemState.dynamic,
        (("peer", "frame", "binding", "dep"),),
    )

    dep_spell.mutation_override = {"svc": "mutated"}
    assert phase._build_phase8_occurrence_plan_fast_key(
        root_blueprint=blueprint,
        spell_lookup=spellbook._spell_id_pool,
        spellbook=spellbook,
        spell_system_states=spell_system_states,
    ) is None


def test_build_phase8_occurrence_plan_input_signature_hashes_mutation_semantics() -> None:
    """Phase 8 signature helper should hash normalized mutation payload semantics."""
    phase = CompilerPhase8()
    spellbook = _make_spellbook_stub()
    root_spell = _make_spell_stub("root", spellbook=spellbook)
    root_spell.mutation_override = {"svc": ["x", "y"]}
    captured_parts: list[tuple[Any, ...]] = []

    original_hash = compiler_phase_8_module.SharedCompilerExecutions.hash_codegen_signature
    compiler_phase_8_module.SharedCompilerExecutions.hash_codegen_signature = (
        lambda *parts: captured_parts.append(parts) or "phase8-signature"
    )
    try:
        blueprint = SimpleNamespace(
            root_spell_id="root",
            ordered_node_ids=("root",),
            path_registry=object(),
            socket_refs=[
                SimpleNamespace(
                    node_id="root",
                    param_name="svc",
                    param_path_id=7,
                    target_spell_ids=("dep",),
                    socket_kind=SocketKind.NORMAL,
                )
            ],
        )

        signature = phase._build_phase8_occurrence_plan_input_signature(
            root_blueprint=blueprint,
            spell_lookup=spellbook._spell_id_pool,
            spellbook=spellbook,
            spell_system_states=None,
        )

        assert signature == "phase8-signature"
        assert captured_parts
        spell_rows = captured_parts[0][4]
        assert spell_rows == (
            (
                "root",
                "root",
                Existence.unique.name,
                False,
                phase._freeze_phase11_schema_value(root_spell.mutation_override),
            ),
        )

        spellbook._lookup_contracted_spells = object()
        assert phase._build_phase8_occurrence_plan_input_signature(
            root_blueprint=blueprint,
            spell_lookup=spellbook._spell_id_pool,
            spellbook=spellbook,
            spell_system_states=None,
        ) is None
    finally:
        compiler_phase_8_module.SharedCompilerExecutions.hash_codegen_signature = original_hash


def test_run_reuses_cached_plan_when_input_signature_unchanged(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 8 should skip rebuild when the cached signature and plan still match."""
    phase = CompilerPhase8()
    spellbook = _make_spellbook_stub()
    spell = _make_spell_stub("root", spellbook=spellbook)
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _root_blueprint_phase5=object(),
        _phase8_occurrence_plan_fast_key=("fast",),
        _phase8_occurrence_plan_input_signature="sig",
        _occurrence_plan_phase8="cached-plan",
        _phase8_11_codegen_ir_dirty=False,
    )

    monkeypatch.setattr(
        CompilerPhase8,
        "_build_phase8_occurrence_plan_fast_key",
        lambda self, **kwargs: ("fast",),
    )
    monkeypatch.setattr(
        CompilerPhase8,
        "_build_phase8_occurrence_plan_input_signature",
        lambda self, **kwargs: (_ for _ in ()).throw(
            AssertionError("signature helper should not run")
        ),
    )
    monkeypatch.setattr(
        compiler_phase_8_module,
        "OccurrencePlanBuilder",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("builder should not run")
        ),
    )

    phase.run(spell, artifact, spellbook, None)

    assert artifact._occurrence_plan_phase8 == "cached-plan"
    assert artifact._phase8_11_codegen_ir_dirty is False


def test_run_rebuilds_when_input_signature_changes(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 8 should rebuild and mark IR dirty when the input signature changes."""
    phase = CompilerPhase8()
    spellbook = _make_spellbook_stub()
    spell = _make_spell_stub("root", spellbook=spellbook)
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _root_blueprint_phase5=object(),
        _phase8_occurrence_plan_fast_key=None,
        _phase8_occurrence_plan_input_signature="sig-old",
        _occurrence_plan_phase8="old-plan",
        _phase8_11_codegen_ir_dirty=False,
    )
    build_calls: list[str] = []
    cleanup_calls: list[str] = []
    built_plan = object()

    monkeypatch.setattr(
        CompilerPhase8,
        "_build_phase8_occurrence_plan_fast_key",
        lambda self, **kwargs: None,
    )
    monkeypatch.setattr(
        CompilerPhase8,
        "_build_phase8_occurrence_plan_input_signature",
        lambda self, **kwargs: "sig-new",
    )
    monkeypatch.setattr(
        CompilerPhase8,
        "_build_phase8_occurrence_shape_profile",
        staticmethod(lambda occurrence_plan: {}),
    )

    class _BuilderStub:
        def __init__(self, **kwargs: Any) -> None:
            build_calls.append("init")

        def build(self) -> object:
            build_calls.append("build")
            return built_plan

        def cleanup(self) -> None:
            cleanup_calls.append("cleanup")

    monkeypatch.setattr(compiler_phase_8_module, "OccurrencePlanBuilder", _BuilderStub)

    phase.run(spell, artifact, spellbook, None)

    assert build_calls == ["init", "build"]
    assert cleanup_calls == ["cleanup"]
    assert artifact._occurrence_plan_phase8 is built_plan
    assert artifact._phase8_occurrence_plan_input_signature == "sig-new"
    assert artifact._phase8_11_codegen_ir_dirty is True


def test_run_marks_phase8_11_dirty_without_eager_capture(monkeypatch) -> None:
    """Phase 8 rebuild should mark the late IR dirty without eagerly exporting it."""
    phase = CompilerPhase8()
    spellbook = _make_spellbook_stub()
    spell = _make_spell_stub("root", spellbook=spellbook)
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _root_blueprint_phase5=object(),
        _phase8_occurrence_plan_fast_key=None,
        _phase8_occurrence_plan_input_signature="sig-old",
        _occurrence_plan_phase8=None,
        _phase8_11_codegen_ir_dirty=False,
    )
    capture_calls: list[str] = []

    monkeypatch.setattr(
        CompilerPhase8,
        "_build_phase8_occurrence_plan_fast_key",
        lambda self, **kwargs: None,
    )
    monkeypatch.setattr(
        CompilerPhase8,
        "_build_phase8_occurrence_plan_input_signature",
        lambda self, **kwargs: "sig-new",
    )
    monkeypatch.setattr(
        CompilerPhase8,
        "_build_phase8_occurrence_shape_profile",
        staticmethod(lambda occurrence_plan: {}),
    )

    class _BuilderStub:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def build(self) -> object:
            return object()

        def cleanup(self) -> None:
            return None

    monkeypatch.setattr(compiler_phase_8_module, "OccurrencePlanBuilder", _BuilderStub)
    monkeypatch.setattr(
        compiler_phase_8_module.SharedCompilerExecutions,
        "capture_phase8_11_codegen_ir",
        lambda artifact: capture_calls.append("capture"),
    )

    phase.run(spell, artifact, spellbook, None)

    assert artifact._phase8_11_codegen_ir_dirty is True
    assert capture_calls == []
