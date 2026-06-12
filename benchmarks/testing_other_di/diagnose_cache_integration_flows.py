"""
Diagnose the three failing cache-runtime integration flows with live tracing.

Purpose:
    Reproduce the surplus-full-hit, missing-live-ids, and changed-conduit
    integration test flows while printing every cache decision the runtime
    makes: conjure cache classification, cached vs live spell-id sets,
    per-spell load attempts (with the swallowed exception, if any), and every
    CreationContext publish with the call stack that produced it.

Usage:
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\diagnose_cache_integration_flows.py

Contract:
    - Read-only diagnosis: wraps runtime seams with tracing delegates; no
      behavior changes beyond prints.
    - Reuses the integration test module's own helpers so the reproduced
      flows match the failing tests exactly.
"""

import sys
import traceback
from pathlib import Path


def _ensure_paths() -> None:
    """Make src/ and the repo root importable for test-helper reuse."""
    repo_root = Path(__file__).resolve().parents[2]
    for candidate in (repo_root, repo_root / "src"):
        candidate_as_str = str(candidate)
        if candidate_as_str not in sys.path:
            sys.path.insert(0, candidate_as_str)


_ensure_paths()

from tests.integration.melder.spellbook import (  # noqa: E402
    test_cache_runtime_integration as flows,
)
from melder.aether.conduit.meld.creation_context.creation_context import (  # noqa: E402
    CreationContext,
)
from melder.aether.conduit.meld.creation_context.creation_context_factory import (  # noqa: E402
    CreationContextFactory,
)
from melder.aether.spellbook.spellbook_creation_system import (  # noqa: E402
    SpellbookCreationSystem,
)
from tests.mocks.spellbook.core_classes import BasicService  # noqa: E402


def _install_tracing() -> None:
    """Wrap the cache/publish seams with print-tracing delegates."""
    original_build_state = SpellbookCreationSystem._build_conjure_cache_state

    def traced_build_state(**kwargs):
        cache_state = original_build_state(**kwargs)
        print(
            f"[cache-state] path={cache_state['cache_path']} "
            f"live={sorted(s[:8] for s in cache_state['live_spell_ids'])} "
            f"cached={sorted(s[:8] for s in cache_state['cached_spell_ids'])} "
            f"missing={sorted(s[:8] for s in cache_state['missing_spell_ids'])}"
        )
        return cache_state

    SpellbookCreationSystem._build_conjure_cache_state = staticmethod(
        traced_build_state
    )

    original_publish = (
        SpellbookCreationSystem._publish_cached_creation_context_for_spell
    )

    def traced_publish(*, spell, spell_payload):
        try:
            original_publish(spell=spell, spell_payload=spell_payload)
        except Exception:
            print(
                f"[load-publish FAILED] spell={spell.spell_id[:8]} "
                f"family={spell_payload.get('family_id') if isinstance(spell_payload, dict) else type(spell_payload).__name__}"
            )
            traceback.print_exc()
            raise
        print(f"[load-publish ok] spell={spell.spell_id[:8]}")

    SpellbookCreationSystem._publish_cached_creation_context_for_spell = (
        staticmethod(traced_publish)
    )

    original_load_cached = CreationContext.load_cached.__func__

    def traced_load_cached(cls, **kwargs):
        spell = kwargs.get("spell")
        print(f"[load_cached] spell={spell.spell_id[:8]}")
        return original_load_cached(cls, **kwargs)

    CreationContext.load_cached = classmethod(traced_load_cached)

    original_build_bind = CreationContextFactory.build_and_bind_for_spell

    def traced_build_bind(self, spell):
        print(f"[factory build_and_bind] spell={spell.spell_id[:8]} from:")
        traceback.print_stack(limit=8)
        return original_build_bind(self, spell)

    CreationContextFactory.build_and_bind_for_spell = traced_build_bind


def _context_report(label: str, spellbook, spell_id: str) -> None:
    """Print the spell's context slot and resolution flags."""
    spell = spellbook._spell_id_pool[spell_id]
    print(
        f"[{label}] context={type(spell._creation_context).__name__ if spell._creation_context is not None else None} "
        f"resolution_complete={spell.resolution_complete} "
        f"resolution_required={spell.resolution_required}"
    )


def scenario_surplus() -> None:
    """Reproduce test_cache_integration_stale_surplus_cache_still_full_hits."""
    print("\n================ SCENARIO: surplus full hit ================")
    flows._reset_runtime_singletons()
    cache_root_path = flows._prepare_case_cache_root("_diag_surplus")
    first = flows._make_spellbook(
        frame_name="diag-surplus",
        cache_root_fragment=flows._build_cache_root_fragment(cache_root_path),
        dynamic=False,
    )
    first_ids = flows._bind_simple_spells(first, include_logger=True)
    first_conduit = flows._conjure(first, conduit_name="root", dynamic=False)
    flows._seed_cache(first_conduit, first_ids)
    first_conduit.cleanup()
    flows._reset_runtime_singletons()

    second = flows._make_spellbook(
        frame_name="diag-surplus",
        cache_root_fragment=flows._build_cache_root_fragment(cache_root_path),
        dynamic=False,
    )
    second_ids = flows._bind_simple_spells(second, include_logger=False)
    second_conduit = flows._conjure(second, conduit_name="root", dynamic=False)
    _context_report("surplus run-2", second, second_ids[BasicService])
    second_conduit.cleanup()


def scenario_changed_conduit() -> None:
    """Reproduce test_cache_integration_changed_conduit_name_misses_cache."""
    print("\n================ SCENARIO: changed conduit name ================")
    flows._reset_runtime_singletons()
    cache_root_path = flows._prepare_case_cache_root("_diag_changed_conduit")
    flows._seed_then_reset_single_spell_namespace(
        cache_root_path=cache_root_path,
        frame_name="diag-changed-conduit",
        conduit_name="alpha",
        dynamic=False,
    )
    spellbook = flows._make_spellbook(
        frame_name="diag-changed-conduit",
        cache_root_fragment=flows._build_cache_root_fragment(cache_root_path),
        dynamic=False,
    )
    spell_ids = flows._bind_simple_spells(spellbook)
    conduit = flows._conjure(spellbook, conduit_name="beta", dynamic=False)
    _context_report("changed-conduit run-2", spellbook, spell_ids[BasicService])
    conduit.cleanup()


def main() -> None:
    """Run both diagnosis scenarios with tracing installed."""
    _install_tracing()
    scenario_surplus()
    scenario_changed_conduit()
    flows._reset_runtime_singletons()
    print("\nDiagnosis complete.")


if __name__ == "__main__":
    main()
