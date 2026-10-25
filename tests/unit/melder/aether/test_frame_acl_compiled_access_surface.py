import threading

from melder.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)


def _build_surface() -> CompiledFrameACLAccessSurface:
    """
    Build one small compiled access surface for direct unit coverage.

    Returns:
        CompiledFrameACLAccessSurface: Directly constructed compiled ACL surface.
    """
    return CompiledFrameACLAccessSurface(
        frame_name="ops",
        configuration_id="cfg-1",
        view_profile_name="safe",
        view_profile_version="0.0.1",
        codegen_profile_name="safe",
        codegen_profile_version="0.0.1",
        allowed_kinds=("frame", "spell"),
        allowed_commands=("query", "describe"),
        frame_payload_fields=("system_state", "rift_enabled"),
        visible_conduit_ids=("conduit-1",),
        visible_spell_keys=(("spellbook-1", "spell-1"),),
        visible_spell_index_ids=("lineage-1",),
        conduit_payload_sections_by_id={"conduit-1": ("conduit_name",)},
        spell_payload_sections_by_key={
            ("spellbook-1", "spell-1"): ("binding_payload", "metadata")
        },
        metadata={"visible_spell_count": 1},
    )


def test_compiled_access_surface_exposes_expected_accessors() -> None:
    """
    Verify the compiled surface exposes the derived immutable answers it owns.

    Returns:
        None.
    """
    surface = _build_surface()

    assert surface.frame_name == "ops"
    assert surface.configuration_id == "cfg-1"
    assert surface.view_profile_name == "safe"
    assert surface.view_profile_version == "0.0.1"
    assert surface.codegen_profile_name == "safe"
    assert surface.codegen_profile_version == "0.0.1"
    assert surface.allowed_kinds == ("frame", "spell")
    assert surface.allowed_commands == ("query", "describe")
    assert surface.frame_payload_fields == ("system_state", "rift_enabled")
    assert surface.visible_conduit_ids == ("conduit-1",)
    assert surface.visible_spell_keys == (("spellbook-1", "spell-1"),)
    assert surface.visible_spell_index_ids == ("lineage-1",)
    assert surface.conduit_payload_sections_by_id == {
        "conduit-1": ("conduit_name",),
    }
    assert surface.spell_payload_sections_by_key == {
        ("spellbook-1", "spell-1"): ("binding_payload", "metadata"),
    }
    assert surface.metadata == {"visible_spell_count": 1}


def test_compiled_access_surface_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called more than once safely.

    Returns:
        None.
    """
    surface = _build_surface()

    surface.cleanup()
    surface.cleanup()

    assert surface.cleaned is True
    assert not hasattr(surface, '_lock')


def test_compiled_access_surface_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the surface.

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    surface = _build_surface()
    coordinated_lock = _CoordinatedLock()
    surface._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        surface.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert surface.cleaned is True
    assert not hasattr(surface, '_lock')


def test_compiled_access_surface_defaults_static_only_denied_builtins_to_empty() -> None:
    """
    Verify the new static-only denied-builtins field defaults to an empty tuple.

    Returns:
        None.
    """
    surface = _build_surface()

    assert surface.static_only_denied_builtin_names == ()


def test_compiled_access_surface_carries_and_clears_static_only_denied_builtins() -> None:
    """
    Verify the compiled surface stores the static-only denied-builtins field and clears it on cleanup.

    Returns:
        None.
    """
    surface = CompiledFrameACLAccessSurface(
        frame_name="ops",
        configuration_id="cfg-1",
        view_profile_name="hybrid",
        view_profile_version="0.0.1",
        codegen_profile_name="hybrid",
        codegen_profile_version="0.0.1",
        static_only_denied_builtin_names=("__import__",),
        allowed_kinds=(),
        allowed_commands=(),
        frame_payload_fields=(),
        visible_conduit_ids=(),
        visible_spell_keys=(),
        visible_spell_index_ids=(),
        conduit_payload_sections_by_id={},
        spell_payload_sections_by_key={},
    )

    assert surface.static_only_denied_builtin_names == ("__import__",)

    surface.cleanup()

    assert surface.cleaned is True
    assert not hasattr(surface, "_static_only_denied_builtin_names")


def test_compiled_access_surface_carries_generation_roots() -> None:
    """
    Verify (D-20) the generation-namespace fields default to None / () and carry what the compiler gives them.

    Returns:
        None.
    """
    assert _build_surface().generation_module_roots is None
    assert _build_surface().denied_generation_module_roots == ()

    surface = CompiledFrameACLAccessSurface(
        frame_name="ops",
        configuration_id="cfg-1",
        view_profile_name="hybrid",
        view_profile_version="0.0.1",
        codegen_profile_name="hybrid",
        codegen_profile_version="0.0.1",
        generation_module_roots=("gen",),
        denied_generation_module_roots=("gen.secret",),
        allowed_kinds=(),
        allowed_commands=(),
        frame_payload_fields=(),
        visible_conduit_ids=(),
        visible_spell_keys=(),
        visible_spell_index_ids=(),
        conduit_payload_sections_by_id={},
        spell_payload_sections_by_key={},
    )

    assert surface.generation_module_roots == ("gen",)
    assert surface.denied_generation_module_roots == ("gen.secret",)
