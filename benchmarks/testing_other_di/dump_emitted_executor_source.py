"""
Dump every emitted executor source compiled during one gauntlet scope cycle.

Purpose:
    Capture the EXACT generated source for the construction-lane shapes
    (step factory + door templates) so per-step instruction and lock counts
    can be audited against the manifest rows. Zero src changes: wraps the
    single compile chokepoint (`get_or_compile_executor_code`) and runs one
    bind -> conjure -> create_lesser -> meld outer -> spellspace meld cycle.

Usage:
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\dump_emitted_executor_source.py

Output:
    emitted_executor_sources.txt next to this script: one section per
    distinct compiled source, headed by its source_name and line count.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _ensure_local_paths() -> None:
    """Ensure local source and benchmark helper paths are importable."""
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parents[1]
    src_dir = project_root / "src"
    for path in (src_dir, current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_local_paths()

import melder_gauntlet_support as _support  # noqa: E402

FRAME_NAME = "bench-dump-emitted-source"
CONDUIT_NAME = "bench-dump-emitted-source"


def _reset_runtime() -> None:
    """Reset the Aether singleton runtime."""
    from melder.aether.aether import Aether
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.nexus.nexus import Nexus

    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _existence_for(cls: type) -> Any:
    """Map one gauntlet class to its gauntlet existence (same as the suite)."""
    from melder.aether.spellbook.existence.existence import Existence

    if cls in set(_support.SINGLETON_TYPES):
        return Existence.unique
    if cls in set(_support.OUTER_SCOPED_TYPES):
        return Existence.unique_per_conduit
    if cls in set(_support.REQUEST_SCOPED_TYPES):
        return Existence.unique_per_spell_space
    return Existence.many


def main() -> None:
    """Capture every compiled executor source for one full scope cycle."""
    from melder.aether.spellbook.spell_compiler import executor_code_cache

    captured: List[Tuple[str, str]] = []
    seen_hashes: set = set()
    original = executor_code_cache.get_or_compile_executor_code

    def _capturing(*, source: str, source_name: str):
        digest = executor_code_cache._hash_source(source)
        if digest not in seen_hashes:
            seen_hashes.add(digest)
            captured.append((source_name, source))
        return original(source=source, source_name=source_name)

    executor_code_cache.get_or_compile_executor_code = _capturing
    # Patch the name as imported into every consumer module (from-import
    # binds module-locally, so the cache-module patch alone misses them).
    import melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.creation_runtime_door_compiler as door_compiler  # noqa: E501
    import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler as gen_no_compiler  # noqa: E501
    import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler as gen_ov_compiler  # noqa: E501
    import melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache as creation_cache_module  # noqa: E501
    patched_modules = []
    for module in (
            door_compiler,
            gen_no_compiler,
            gen_ov_compiler,
            creation_cache_module,
    ):
        if hasattr(module, "get_or_compile_executor_code"):
            patched_modules.append(
                (module, module.get_or_compile_executor_code)
            )
            module.get_or_compile_executor_code = _capturing

    try:
        from melder.aether.spellbook.spellbook import Spellbook

        _reset_runtime()
        spellbook = Spellbook(aetheric_frame=FRAME_NAME)
        configuration = spellbook.get_configuration()
        configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
        spellbook.configure_aether_frame(
            system_state=None,
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
        )
        spell_ids: Dict[type, str] = {}
        for cls in _support.ALL_CLASSES:
            spell_ids[cls] = spellbook.bind(
                spell=cls,
                existence=_existence_for(cls),
                permissions="create",
            )
        root = spellbook.conjure(name=CONDUIT_NAME, dynamic=False)
        outer_id = spell_ids[_support.OUTER_SCOPED_TYPES[0]]
        request_id = spell_ids[_support.REQUEST_SCOPED_TYPES[0]]
        lesser = root.create_lesser_conduit()
        try:
            lesser.meld(spell=outer_id)
            with lesser.enter_spellspace() as space:
                space.meld(spell=request_id)
        finally:
            lesser.cleanup()
        root.cleanup()
        _reset_runtime()
    finally:
        executor_code_cache.get_or_compile_executor_code = original
        for module, module_original in patched_modules:
            module.get_or_compile_executor_code = module_original

    sections: List[str] = []
    for source_name, source in captured:
        line_count = source.count("\n") + 1
        lock_count = source.count("._lock:")
        get_count = source.count(".get(")
        sections.append(
            "=" * 78
            + f"\n{source_name}\nlines={line_count}  with-lock-blocks={lock_count}  .get-calls={get_count}\n"
            + "=" * 78
            + "\n"
            + source
            + "\n"
        )
    text = (
        f"captured {len(captured)} distinct compiled sources\n\n"
        + "\n".join(sections)
    )
    output_path = Path(__file__).resolve().parent / "emitted_executor_sources.txt"
    output_path.write_text(text, encoding="utf-8")
    print(f"captured {len(captured)} distinct compiled sources")
    for source_name, source in captured:
        print(
            f"  {source_name}: lines={source.count(chr(10)) + 1} "
            f"lock-blocks={source.count('._lock:')} gets={source.count('.get(')}"
        )
    print(f"\nFull dump written to: {output_path}")


if __name__ == "__main__":
    main()
