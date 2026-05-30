"""Unit tests for current-surface compiler phase 10 helper semantics."""

from types import SimpleNamespace
from typing import Any

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_10 as compiler_phase_10_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_10 import (
    CompilerPhase10,
)


def test_build_phase10_patch_maps_input_signature_uses_blueprint_shape_and_handles_failures() -> None:
    """Phase 10 patch-map signature helper should use blueprint shape and fail soft."""
    phase = CompilerPhase10()
    path_registry = object()
    blueprint = SimpleNamespace(
        root_spell_id="root",
        path_registry=path_registry,
        socket_refs=[object(), object()],
        ordered_node_ids=["a", "root"],
    )

    assert phase._build_phase10_patch_maps_input_signature(blueprint) == (
        "root",
        id(path_registry),
        2,
        2,
    )

    class _BrokenBlueprint:
        @property
        def root_spell_id(self):
            return "root"

        @property
        def path_registry(self):
            raise RuntimeError("boom")

    assert phase._build_phase10_patch_maps_input_signature(_BrokenBlueprint()) is None


def test_run_reuses_cached_maps_when_input_signature_unchanged(monkeypatch) -> None:
    """Phase 10 should skip rebuild when the cached signature and maps still match."""
    phase = CompilerPhase10()
    spell = SimpleNamespace(is_existing_creation=False)
    root_blueprint = object()
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _root_blueprint_phase5=root_blueprint,
        _phase10_patch_maps_input_signature=("sig",),
        _override_patch_map_phase10="override-map",
        _mutation_patch_map_phase10="mutation-map",
        _phase8_11_codegen_ir_dirty=False,
    )

    monkeypatch.setattr(
        CompilerPhase10,
        "_build_phase10_patch_maps_input_signature",
        lambda self, _root_blueprint: ("sig",),
    )
    monkeypatch.setattr(
        compiler_phase_10_module,
        "PatchMapBuilder",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("builder should not run")
        ),
    )

    phase.run(spell, artifact)

    assert artifact._override_patch_map_phase10 == "override-map"
    assert artifact._mutation_patch_map_phase10 == "mutation-map"
    assert artifact._phase8_11_codegen_ir_dirty is False


def test_run_rebuilds_when_input_signature_changes(monkeypatch) -> None:
    """Phase 10 should rebuild and mark IR dirty when the input signature changes."""
    phase = CompilerPhase10()
    spell = SimpleNamespace(is_existing_creation=False)
    root_blueprint = object()
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _root_blueprint_phase5=root_blueprint,
        _phase10_patch_maps_input_signature=("old",),
        _override_patch_map_phase10=None,
        _mutation_patch_map_phase10=None,
        _phase8_11_codegen_ir_dirty=False,
    )
    build_calls: list[str] = []
    cleanup_calls: list[str] = []
    override_map = object()
    mutation_map = object()

    monkeypatch.setattr(
        CompilerPhase10,
        "_build_phase10_patch_maps_input_signature",
        lambda self, _root_blueprint: ("new",),
    )

    class _BuilderStub:
        def __init__(self, **kwargs: Any) -> None:
            build_calls.append("init")

        def build_override_patch_map(self) -> object:
            build_calls.append("override")
            return override_map

        def build_mutation_patch_map(self) -> object:
            build_calls.append("mutation")
            return mutation_map

        def cleanup(self) -> None:
            cleanup_calls.append("cleanup")

    monkeypatch.setattr(compiler_phase_10_module, "PatchMapBuilder", _BuilderStub)
    monkeypatch.setattr(
        CompilerPhase10,
        "_build_phase10_override_shape_profile",
        staticmethod(lambda **kwargs: {}),
    )

    phase.run(spell, artifact)

    assert build_calls == ["init", "override", "mutation"]
    assert cleanup_calls == ["cleanup"]
    assert artifact._override_patch_map_phase10 is override_map
    assert artifact._mutation_patch_map_phase10 is mutation_map
    assert artifact._phase10_patch_maps_input_signature == ("new",)
    assert artifact._phase8_11_codegen_ir_dirty is True


def test_run_marks_phase8_11_dirty_without_eager_capture(monkeypatch) -> None:
    """Phase 10 rebuild should mark the late IR dirty without eagerly exporting it."""
    phase = CompilerPhase10()
    spell = SimpleNamespace(is_existing_creation=False)
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _root_blueprint_phase5=object(),
        _phase10_patch_maps_input_signature=("old",),
        _override_patch_map_phase10=None,
        _mutation_patch_map_phase10=None,
        _phase8_11_codegen_ir_dirty=False,
    )

    monkeypatch.setattr(
        CompilerPhase10,
        "_build_phase10_patch_maps_input_signature",
        lambda self, _root_blueprint: ("new",),
    )

    class _BuilderStub:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def build_override_patch_map(self) -> object:
            return object()

        def build_mutation_patch_map(self) -> object:
                return object()

        def cleanup(self) -> None:
            return None

    monkeypatch.setattr(compiler_phase_10_module, "PatchMapBuilder", _BuilderStub)
    monkeypatch.setattr(
        CompilerPhase10,
        "_build_phase10_override_shape_profile",
        staticmethod(lambda **kwargs: {}),
    )

    phase.run(spell, artifact)

    assert artifact._phase8_11_codegen_ir_dirty is True
