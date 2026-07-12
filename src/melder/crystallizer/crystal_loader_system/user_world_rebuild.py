"""
Shared user-world rebuild lane (spell_index_graft 2026-07-12 follow-up).

S2 physical custody taught the RestoreEngine to rebuild ABSENT user
modules from retained text through the SyntheticModule lifecycle. The
graft lane needs the identical behavior against a live host, so the
mechanics live here as one free function with collector callbacks - the
engine keeps its all-or-nothing built-stack semantics, the graft runner
keeps its shortfall rows, and the LAWS stay in exactly one place: the
live file always wins, sys.modules entries are never masked, modules
build in the crystal's recorded topological load order (dot-depth
parents-first as the pre-load-order fallback), every rebuild files the
honest shortfall.
"""

import sys
from pathlib import Path
from typing import Any, Callable, Dict


def rebuild_absent_user_modules(
        spell_id: str,
        crystal: Dict[str, object],
        on_built: Callable[[Any], None],
        on_shortfall: Callable[[str], None],
) -> bool:
    """
    Rebuild ABSENT user modules from retained source text.

    Purpose:
        The restore half of opt-in physical custody, shared by the
        RestoreEngine (world replays) and the GraftRunner (live-host
        grafts): retained `user_module_sources` payloads rebuild through
        the SyntheticModule lifecycle so the ordinary import lane can
        then resolve the bind target.

    Contract:
        - THE LIVE FILE ALWAYS WINS: a retained module whose recorded
          backing path still exists is NEVER rebuilt from text; modules
          already in sys.modules are skipped.
        - Modules build in recorded `module_load_order` when the crystal
          carries it (dot-depth fallback otherwise); every rebuilt
          module is handed to `on_built` (teardown custody is the
          CALLER'S semantics - the engine stacks for all-or-nothing, the
          graft runner keeps them as normal user activity) and files
          "user_module_rebuilt_synthetic_from_retained_source" through
          `on_shortfall`.
        - Returns True only when at least one module was rebuilt (the
          caller retries its import exactly once).
        - Payloads without retention return False untouched.

    Args:
        spell_id:
            Custody identity (rides the SyntheticModule as its
            spell_crystal_id).
        crystal:
            The custody payload (folded or graft-carried).
        on_built:
            Receives each live SyntheticModule after execute_source.
        on_shortfall:
            Receives each honest reason string.

    Returns:
        bool: True when a retry of the import lane is warranted.
    """
    from melder.crystallizer.synthetic_module import SyntheticModule

    sources = dict(crystal.get("user_module_sources", {}))
    if not sources:
        return False
    rebuilt_any = False
    # load_order residue fix (patch persistence_loop_load_order_r11_2026_07_12):
    # the crystal's topological module_load_order is the true dependency
    # order when present - dot-depth is only the fallback for payloads
    # sealed before the analysis service recorded load order. Names the
    # order does not know still rebuild, appended in dot-depth order.
    recorded_order = [
        str(name)
        for name in crystal.get("module_load_order", [])
        if str(name) in sources
    ]
    unordered_names = sorted(
        (name for name in sources.keys() if name not in set(recorded_order)),
        key=lambda name: (name.count("."), name),
    )
    for module_name in (*recorded_order, *unordered_names):
        if module_name in sys.modules:
            continue
        payload = dict(sources[module_name])
        recorded_path = payload.get("module_path")
        if (
            recorded_path is not None
            and Path(str(recorded_path)).exists()
        ):
            # Live file wins: never mask a real file with retained
            # text - whatever made its import fail stays visible.
            continue
        try:
            module = SyntheticModule(
                module_name=module_name,
                spell_crystal_id=spell_id,
                source_text=str(payload.get("source_text", "")),
                source_sha256=str(payload.get("source_sha256", "")),
                binding_signature="user_source_retained",
                parent_name=(
                    module_name.rsplit(".", 1)[0]
                    if "." in module_name
                    else None
                ),
                is_package=bool(payload.get("is_package", False)),
            )
            module.register_in_import_registry()
            module.publish_to_sys_modules()
            module.execute_source()
        except Exception as error:
            on_shortfall(
                "user_module_rebuild_failed ({0}): {1}".format(
                    module_name, error
                )
            )
            return False
        on_built(module)
        on_shortfall(
            "user_module_rebuilt_synthetic_from_retained_source: "
            "{0}".format(module_name)
        )
        rebuilt_any = True
    return rebuilt_any
