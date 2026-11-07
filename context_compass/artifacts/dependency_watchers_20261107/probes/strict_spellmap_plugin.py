"""
Probe plugin: the full test suite with `SpellMap(spell=X)` (no spellframe) reaching only a bare X.

Owner: TASK-2026-11-07-inventory_class_resolution_of_framed_spells (T1 of
EPIC-2026-11-07-spellframe_hides_the_concrete_class), melder_0.

Purpose:
    Measure the blast radius of one edge case before the owner decides it. On 0.2.8277
    `CompilerPhase3._resolve_spellmap_default` matches `SpellMap(spell=X)` without a
    spellframe by identity (`spell_obj.spell is X`) wherever X is bound, while `meld(X)`
    refuses an X bound under a spellframe. With MELDER_PROBE_STRICT_SPELLMAP=1 this plugin
    makes that branch skip spells bound under a spellframe; MELDER_PROBE_STRICT_SPELLMAP=2 (the
    Autofac reading, 2026-11-07) also skips spells with a binding name when the SpellMap names none.
    Every other SpellMap shape (a spellframe given, or `spell=None`) runs the shipped code.

Usage (from the repository root; load the cache redirect of strict_class_match_plugin too):
    PYTHONPATH=context_compass/artifacts/dependency_watchers_20261107/probes \
    MELDER_PROBE_STRICT=0 MELDER_PROBE_STRICT_SPELLMAP=1 .venv_new/Scripts/python.exe -X gil=0 \
        -m pytest tests -p strict_class_match_plugin -p strict_spellmap_plugin

Limits:
    A test that starts its own interpreter does not load the plugin.
"""
import os
from typing import Any, Dict

import pytest


class StrictSpellMapProbe:
    """
    Install and remove the strict explicit-spell SpellMap rule for one pytest process.

    Contract:
        - Replaces `CompilerPhase3._resolve_spellmap_default` only when
          MELDER_PROBE_STRICT_SPELLMAP is "1"; the replacement delegates every shape but
          `SpellMap(spell=X)` with no spellframe to the shipped method.
        - For that shape it keeps the shipped identity and binding-name tests, adds "bound
          with no spellframe", and raises the shipped RuntimeErrors on zero or several matches.
        - `pytest_unconfigure` restores the original once.

    Threading / Concurrency:
        Installed in `pytest_configure` and removed in `pytest_unconfigure` on pytest's main
        thread, before and after every test; the replacement keeps no state.
    """

    def __init__(self, enabled: bool, require_default_binding: bool = False) -> None:
        """
        Prepare the probe.

        Args:
            enabled: True to install the strict rule.
            require_default_binding: True (MELDER_PROBE_STRICT_SPELLMAP="2", the Autofac reading) to
                make `SpellMap(spell=X)` with no binding name match only an X bound with no binding
                name, as an unkeyed Autofac lookup never reaches a keyed registration.
        """
        self._enabled: bool = enabled
        self._require_default_binding: bool = require_default_binding
        self._owner: Any = None
        self._original: Any = None

    def apply(self) -> None:
        """Install the strict rule when enabled."""
        if not self._enabled:
            return
        from melder.aether.spellbook.spell_compiler.phases.compiler_phase_3 import CompilerPhase3
        from melder.utilities.helpers.general_helpers import SpellInputUtils

        original = CompilerPhase3.__dict__["_resolve_spellmap_default"]
        require_default_binding = self._require_default_binding

        def strict_resolve_spellmap_default(phase_self: Any, spell: Any, spellbook: Any, dep: Any) -> Dict[Any, Any]:
            """`SpellMap(spell=X)` with no spellframe reaches only an X bound with no spellframe."""
            spellmap = dep.spellmap_default
            if spellmap is None or spellmap.spell is None or spellmap.spellframe is not None:
                return original(phase_self, spell, spellbook, dep)
            binding_name = spellmap.binding_name
            binding_key = SpellInputUtils.normalize_binding_name(binding_name)
            candidates: Dict[Any, Any] = {}
            for index, spell_obj in phase_self._iter_all_spells(spellbook):
                if spell_obj.spell is not spellmap.spell or spell_obj.spellframe is not None:
                    continue
                if (binding_name is not None
                        and SpellInputUtils.normalize_binding_name(spell_obj.binding_name) != binding_key):
                    continue
                if (binding_name is None and require_default_binding
                        and SpellInputUtils.normalize_binding_name(spell_obj.binding_name)
                        != SpellInputUtils.DEFAULT_BINDING_NAME):
                    continue
                candidates[index] = spell_obj
            if not candidates:
                raise RuntimeError(
                    "SpellCrafter Phase 3: SpellMap default could not be resolved for "
                    f"parameter {dep.param_name!r} on spell {spell.spell_name!r}. "
                    f"SpellMap={spellmap!r}. [probe: strict explicit-spell SpellMap]"
                )
            if len(candidates) > 1:
                raise RuntimeError(
                    "SpellCrafter Phase 3: SpellMap default resolved to multiple candidates for "
                    f"parameter {dep.param_name!r} on spell {spell.spell_name!r}. "
                    "[probe: strict explicit-spell SpellMap]"
                )
            return candidates

        self._owner = CompilerPhase3
        self._original = original
        CompilerPhase3._resolve_spellmap_default = strict_resolve_spellmap_default

    def pytest_report_header(self, config: pytest.Config) -> str:
        """
        Name the probe's mode in the run's header.

        Args:
            config: The pytest configuration (unused).

        Returns:
            str: One header line.
        """
        if not self._enabled:
            mode = "as shipped"
        elif self._require_default_binding:
            mode = "strict, bare and unnamed only when no binding name is given (Autofac reading)"
        else:
            mode = "strict, bare only"
        return f"strict_spellmap_plugin: explicit-spell SpellMap {mode}"

    def pytest_unconfigure(self, config: pytest.Config) -> None:
        """
        Restore the shipped method.

        Args:
            config: The pytest configuration (unused).
        """
        if self._owner is not None:
            setattr(self._owner, "_resolve_spellmap_default", self._original)
            self._owner = None


def pytest_configure(config: pytest.Config) -> None:
    """
    Install the probe in this process (the xdist controller and every worker).

    Args:
        config: The pytest configuration.
    """
    mode = os.environ.get("MELDER_PROBE_STRICT_SPELLMAP")
    probe = StrictSpellMapProbe(enabled=mode in ("1", "2"), require_default_binding=mode == "2")
    probe.apply()
    config.pluginmanager.register(probe, "melder_strict_spellmap_probe")
