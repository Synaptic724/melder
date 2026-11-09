"""
Probe plugin (scratch, read-only design work): the suite under the PROPOSED HIDDEN_PROVIDER rule.

TASK-2026-11-07-spellframe_ambiguity_validation_check part (a). No src edit: the proposed behaviour is
patched in at runtime so the suite tells which existing tests the change would break.

Modes (environment variable MELDER_PROBE_HIDDEN):
    "1": emulate the proposal -
         (a) a Phase 4 error HIDDEN_PROVIDER for every UNRESOLVED_INPUT socket whose annotation is a class
             lookup (a class, or a single string's type part) when the pool holds spells of that type key that
             a class lookup does not reach (bound under a spellframe or a non-default binding name);
         (b) `SpellMap(spell=X)` without a spellframe that misses X while X is registered elsewhere no longer
             raises in Phase 3: the socket compiles UNRESOLVED_INPUT and (a)'s strategy refuses it.
    anything else: behaviour as shipped.
Both modes redirect the default conjure cache root (`<melder>/__melder_cache__`) to a temp dir, as T1's
strict_class_match_plugin did, so no bundle replays phase 3-4 rows and nothing is written under src/.

Usage (repository root):
    PYTHONPATH=<scratch dir> MELDER_PROBE_HIDDEN=1 .venv_new/Scripts/python.exe -X gil=0 -m pytest tests \
        -p hidden_provider_plugin -p no:cacheprovider
"""
import dataclasses
import os
import shutil
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import pytest


class HiddenProviderProbe:
    """Install and remove the runtime patches for one pytest process."""

    def __init__(self, emulate: bool) -> None:
        self._emulate = emulate
        self._cache_root = Path(tempfile.mkdtemp(prefix="melder_hidden_probe_cache_"))
        self._originals: List[Tuple[Any, str, Any]] = []
        self._removed = False
        self._lock = threading.Lock()
        self._spellmap_misses: Dict[Tuple[int, str], bool] = {}

    def pytest_report_header(self, config: pytest.Config) -> str:
        mode = "PROPOSED HIDDEN_PROVIDER rule emulated" if self._emulate else "as shipped"
        if os.environ.get("MELDER_PROBE_HIDDEN") == "2":
            mode += " + option B announcers (type key)"
        return f"hidden_provider_plugin: {mode}; conjure cache root {self._cache_root}"

    def pytest_unconfigure(self, config: pytest.Config) -> None:
        if self._removed:
            return
        self._removed = True
        for owner, name, original in reversed(self._originals):
            setattr(owner, name, original)
        shutil.rmtree(self._cache_root, ignore_errors=True)

    def _install(self, owner: Any, name: str, replacement: Callable[..., Any]) -> None:
        self._originals.append((owner, name, owner.__dict__[name]))
        setattr(owner, name, replacement)

    def apply(self) -> None:
        import melder
        from melder.utilities.caching_system.caching_system import CachingSystem
        self._redirect_cache_root(CachingSystem, Path(melder.__file__).resolve().parent / "__melder_cache__")
        if self._emulate:
            self._patch_spellmap_miss()
            self._patch_topology()
            self._patch_strategies()
        if os.environ.get("MELDER_PROBE_HIDDEN") == "2":
            self._patch_announcers()

    # ---- (c) option B: a framed or named spell also announces its type key ------------------------------
    def _patch_announcers(self) -> None:
        from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import (
            ChangeControlManager,
        )
        from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
        from melder.aether.spellbook.spellbook import Spellbook
        from melder.utilities.helpers.general_helpers import SpellInputUtils

        def hidden_type_key(spell: Any) -> Any:
            if CompilerPhase3._answers_class_lookup(spell) or CompilerPhase3._spell_definition_key(spell) is not None:
                return None
            return CompilerPhase3._spell_type_key(spell)

        original_marker = ChangeControlManager.__dict__["_default_dirty_marker"]

        def default_dirty_marker(manager_self: Any, staged: Any) -> None:
            original_marker(manager_self, staged)
            if staged.spellbook_id is None or not staged.binding_keys:
                return
            spellbook = manager_self._resolve_spellbook_for_staged(staged)
            announced = {frame_key for frame_key, _ in staged.binding_keys if frame_key}
            extra = set()
            for spell in manager_self._resolve_spells_for_binding_keys(spellbook, staged.binding_keys):
                key = hidden_type_key(spell)
                if key and key not in announced:
                    extra.add(key)
            if extra:
                manager_self._spell_system_states.mark_collection_dependents_dirty(
                    spellbook_id=staged.spellbook_id, frame_keys=extra,
                )

        self._install(ChangeControlManager, "_default_dirty_marker", default_dirty_marker)

        original_add = Spellbook.__dict__["_add_contracted_spell"]

        def add_contracted_spell(book_self: Any, spell: Any, conduit_id: str) -> None:
            original_add(book_self, spell, conduit_id)
            key = hidden_type_key(spell)
            if key and book_self._conjured and key != spell.key[0]:
                book_self._mark_collection_dependents_dirty({key})

        self._install(Spellbook, "_add_contracted_spell", add_contracted_spell)

    def _redirect_cache_root(self, caching_system_class: Any, default_root: Path) -> None:
        original_init = caching_system_class.__dict__["__init__"]
        default_resolved = default_root.resolve()
        probe_root = self._cache_root

        def redirected_init(caching_self: Any, *, frame_name: str, conduit_name: str, cache_root_path: Path,
                            logger: Any = None) -> None:
            target = Path(cache_root_path)
            try:
                relative = target.resolve().relative_to(default_resolved)
            except ValueError:
                relative = None
            if relative is not None:
                target = probe_root / relative
            original_init(caching_self, frame_name=frame_name, conduit_name=conduit_name,
                          cache_root_path=target, logger=logger)

        self._install(caching_system_class, "__init__", redirected_init)

    # ---- (b) SpellMap(spell=X) without a spellframe: record, do not raise --------------------------------
    def _patch_spellmap_miss(self) -> None:
        from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
        original = CompilerPhase3.__dict__["_resolve_spellmap_default"]
        probe = self

        def resolve_spellmap_default(phase_self: Any, spell: Any, spellbook: Any, dep: Any) -> Dict[Any, Any]:
            try:
                return original(phase_self, spell, spellbook, dep)
            except RuntimeError as error:
                if "could not be resolved" not in str(error):
                    raise
                spellmap = dep.spellmap_default
                if spellmap is None or spellmap.spell is None or spellmap.spellframe is not None:
                    raise
                hidden = [s for s in spellbook._spell_id_pool.copy().values() if s.spell is spellmap.spell]
                if not hidden:
                    raise
                with probe._lock:
                    probe._spellmap_misses[(id(spell), dep.param_name)] = True
                return {}

        self._install(CompilerPhase3, "_resolve_spellmap_default", resolve_spellmap_default)

    def _patch_topology(self) -> None:
        from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
        from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
        from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import SpellLocalTopology
        original = CompilerPhase3.__dict__["_build_local_topology"]
        probe = self

        def build_local_topology(phase_self: Any, spell: Any, graph: Any, socket_targets: Any, **kwargs: Any) -> Any:
            topology = original(phase_self, spell, graph, socket_targets, **kwargs)
            with probe._lock:
                marked = {name for (spell_key, name) in list(probe._spellmap_misses) if spell_key == id(spell)}
                for name in marked:
                    probe._spellmap_misses.pop((id(spell), name), None)
            if not marked:
                return topology
            sockets = [
                dataclasses.replace(socket, socket_kind=SocketKind.UNRESOLVED_INPUT)
                if socket.param_name in marked and not socket.target_spell_ids else socket
                for socket in topology.sockets
            ]
            return SpellLocalTopology(spell_id=topology.spell_id, sockets=sockets)

        self._install(CompilerPhase3, "_build_local_topology", build_local_topology)

    # ---- (a) the Phase 4 strategy ---------------------------------------------------------------------------
    def _patch_strategies(self) -> None:
        from melder.aether.spellbook.spell_compiler.validation.validation_system import SpellValidationSystem
        original = SpellValidationSystem.__dict__["_register_builtin_strategies"]
        strategy_class = _build_strategy_class()

        def register_builtin_strategies(system_self: Any) -> None:
            original(system_self)
            system_self.register_strategy(strategy_class())

        self._install(SpellValidationSystem, "_register_builtin_strategies", register_builtin_strategies)


def _build_strategy_class() -> type:
    """Build the emulated strategy class after melder is importable."""
    from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
    from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import ParameterDIShape
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_issue import SpellValidationIssue
    from melder.aether.spellbook.spell_compiler.validation.strategies.spell_validation_strategy import (
        SpellValidationStrategy,
    )
    from melder.aether.spellbook.spell_types.spell_types import SpellType

    method_types = (SpellType.METHOD, SpellType.METHOD_WITH_BINDING_NAME, SpellType.LAMBDA_METHOD_WITH_BINDING_NAME)
    phase3 = CompilerPhase3()

    class EmulatedHiddenProviderStrategy(SpellValidationStrategy):
        """HIDDEN_PROVIDER as proposed: an UNRESOLVED_INPUT class lookup whose class is bound elsewhere."""

        __slots__ = SpellValidationStrategy.__slots__

        def __init__(self) -> None:
            super().__init__(name="hidden_provider_probe", description="probe emulation of HIDDEN_PROVIDER")

        def validate(self, context: Any) -> None:
            spell = context.spell
            requirements = context.requirements
            spellbook = context.spellbook
            if requirements is None or spellbook is None or not spell.resolvable:
                return
            topology = spell._spell_system_states.get_local_topology(spell.spell_index)
            if topology is None:
                return
            params = {param.name: param for param in requirements.parameters}
            for socket in topology.iter_sockets():
                if socket.socket_kind is not SocketKind.UNRESOLVED_INPUT:
                    continue
                param = params.get(socket.param_name)
                if param is None:
                    continue
                hidden = self._hidden(param, spellbook)
                if not hidden:
                    continue
                where = "; ".join(
                    f"{s.spell_name} at (spellframe={getattr(s.spellframe, '__name__', s.spellframe)!r}, "
                    f"binding_name={s.binding_name!r})" for s in hidden
                )
                context.issues.append(SpellValidationIssue(
                    severity="error",
                    code="HIDDEN_PROVIDER",
                    message=(f"Parameter {socket.param_name!r} on spell {spell.spell_name!r}: a class lookup reaches "
                             f"only a spell bound bare; it is bound only at {where}. [probe emulation]"),
                    details={"spell_id": spell.spell_id, "parameter_name": socket.param_name},
                ))

        @staticmethod
        def _hidden(param: Any, spellbook: Any) -> List[Any]:
            pool = list(spellbook._spell_id_pool.copy().values())
            if param.di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                spellmap = param.spellmap_default
                if spellmap is None or spellmap.spell is None or spellmap.spellframe is not None:
                    return []
                return [s for s in pool if s.spell is spellmap.spell]
            if param.di_shape is not ParameterDIShape.SINGLE_BY_ANNOTATION:
                return []
            annotation = phase3._normalize_annotation_for_matching(param.annotation)
            if phase3._annotation_kind(annotation) == phase3._KIND_CONTRACT:
                return []
            key = phase3._annotation_key(annotation)
            return [
                s for s in pool
                if s.spell_type not in method_types
                and not CompilerPhase3._answers_class_lookup(s)
                and CompilerPhase3._spell_type_key(s) == key
            ]

    return EmulatedHiddenProviderStrategy


def pytest_configure(config: pytest.Config) -> None:
    """Install the probe in this process (the xdist controller and every worker)."""
    src_path = str(config.rootpath / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    probe = HiddenProviderProbe(emulate=os.environ.get("MELDER_PROBE_HIDDEN") in ("1", "2"))
    probe.apply()
    config.pluginmanager.register(probe, "melder_hidden_provider_probe")
