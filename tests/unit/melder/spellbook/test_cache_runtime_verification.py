import threading
from types import SimpleNamespace
from typing import Any, Dict, Iterable, Optional

import pytest

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation import spell_codegen_creation_cache as creation_context_cache_codec
from melder.aether.conduit.meld.creation_context.creation_context_factory import (
    CreationContextFactory,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem


class _StubCachingSystem:
    """Minimal cache utility surface for unit cache-orchestration tests."""

    def __init__(self, payloads: Optional[Dict[str, Any]] = None) -> None:
        self._payloads: Dict[str, Any] = dict(payloads or {})
        self.emit_calls = 0
        self.fail_emit = False

    @property
    def cached_spell_ids(self):  # type: ignore[no-untyped-def]
        return self._payloads.keys()

    def has_spell_payload(self, spell_id: str) -> bool:
        return spell_id in self._payloads

    def get_spell_payload(self, spell_id: str) -> Optional[Any]:
        return self._payloads.get(spell_id)

    def upsert_spell_payload(self, spell_id: str, spell_payload: Any) -> None:
        self._payloads[spell_id] = spell_payload

    def emit(self) -> None:
        self.emit_calls += 1
        if self.fail_emit:
            raise RuntimeError("emit failed")


class _RecordingSpell:
    """Small spell stub with cache-facing behavior hooks."""

    def __init__(
            self,
            *,
            spell_id: str = "spell-a",
            caching_enabled: bool = True,
            emit_result: bool = True,
    ) -> None:
        self.spell_id = spell_id
        self.spell_name = spell_id
        self._caching_enabled = caching_enabled
        self._dynamic_environment = False
        self._creation_context = object()
        self._compiler_artifact = SimpleNamespace(_spell_codegen_creation=object())
        self._creation_context_factory = SimpleNamespace(
            _resolve_runtime_gate_for_spell=lambda spell: (None, None)
        )
        self.resolution_complete = False
        self.resolution_required = True
        self.emit_calls = 0
        self._emit_result = emit_result

    def emit_cache(self) -> bool:
        self.emit_calls += 1
        return self._emit_result


def _make_spellbook_stub(
        *,
        live_spell_ids: Iterable[str],
        caching_enabled: bool = True,
        caching_system: Optional[_StubCachingSystem] = None,
) -> Any:
    """Build a Spellbook-shaped stub for cache-state helpers."""
    payload = {
        spell_id: _RecordingSpell(spell_id=spell_id)
        for spell_id in live_spell_ids
    }
    spellbook = SimpleNamespace(
        _lock=threading.RLock(),
        _cache_emit_required=False,
        _spell_id_pool=payload,
        _system_caching_enabled_in_aether=lambda: caching_enabled,
        _get_or_create_caching_system=lambda conduit_name=None: caching_system,
        _logger=SimpleNamespace(error=lambda *args, **kwargs: None),
    )
    spellbook._emit_cache_file_if_required = lambda: Spellbook._emit_cache_file_if_required(
        spellbook
    )
    return spellbook


@pytest.mark.parametrize(
    ("is_existing_creation", "existence_name", "expected_route"),
    [
        (True, "unique", "existing_creation"),
        (False, "unique_per_spell_space", "spellspace"),
        (False, "unique_per_conduit", "unique_per_conduit"),
        (False, "many", "many"),
        (False, "unique", "shared"),
        (False, "unique_per_conduit_cluster", "shared"),
        (False, "unique_per_conduit_lineage", "shared"),
    ],
)
def test_resolve_route_key_for_spell_maps_supported_spell_routes(
        is_existing_creation: bool,
        existence_name: str,
        expected_route: str,
) -> None:
    """Verify cache codec route selection matches spell existence truth."""
    spell = SimpleNamespace(
        is_existing_creation=is_existing_creation,
        existence=SimpleNamespace(name=existence_name),
    )
    if not is_existing_creation:
        from melder.aether.spellbook.existence.existence import Existence

        spell.existence = Existence[existence_name]
    assert (
        creation_context_cache_codec._resolve_route_key_for_spell(spell)
        == expected_route
    )


def test_resolve_route_key_for_spell_rejects_unknown_existence() -> None:
    """Verify cache codec fails on unsupported existence values."""
    spell = SimpleNamespace(
        is_existing_creation=False,
        existence=SimpleNamespace(name="unsupported"),
    )
    with pytest.raises(RuntimeError, match="not cacheable"):
        creation_context_cache_codec._resolve_route_key_for_spell(spell)


@pytest.mark.parametrize(
    ("transient_schema", "expected"),
    [
        ({"step_count": 1}, True),
        (None, False),
    ],
)
def test_has_fast_transient_no_overrides_reflects_cached_schema(
        transient_schema: Optional[Dict[str, Any]],
        expected: bool,
) -> None:
    """Verify fast-transient detection matches package payload shape."""
    package = {
        "no_overrides": {
            "transient_schema": transient_schema,
        }
    }
    assert creation_context_cache_codec._has_fast_transient_no_overrides(package) is expected


@pytest.mark.parametrize(
    ("caching_enabled", "is_full_hit", "is_mixed", "expected"),
    [
        (False, False, False, "disabled"),
        (True, True, False, "full_hit"),
        (True, False, True, "mixed"),
        (True, False, False, "full_miss"),
    ],
)
def test_resolve_conjure_cache_path_reports_expected_label(
        caching_enabled: bool,
        is_full_hit: bool,
        is_mixed: bool,
        expected: str,
) -> None:
    """Verify cache-path labels are derived only from the classification flags."""
    assert (
        SpellbookCreationSystem._resolve_conjure_cache_path(
            caching_enabled=caching_enabled,
            is_full_hit=is_full_hit,
            is_mixed=is_mixed,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("caching_enabled", "cached_ids", "expected_path", "expected_full_hit", "expected_mixed", "expected_full_miss"),
    [
        (False, (), "disabled", False, False, True),
        (True, ("spell-a", "spell-b"), "full_hit", True, False, False),
        (True, ("spell-a", "spell-b", "stale-spell"), "full_hit", True, False, False),
        (True, ("spell-a",), "mixed", False, True, False),
        (True, (), "full_miss", False, False, True),
        (True, ("stale-spell",), "full_miss", False, False, True),
    ],
)
def test_build_conjure_cache_state_classifies_live_vs_cached_spell_sets(
        monkeypatch: pytest.MonkeyPatch,
        caching_enabled: bool,
        cached_ids: tuple[str, ...],
        expected_path: str,
        expected_full_hit: bool,
        expected_mixed: bool,
        expected_full_miss: bool,
) -> None:
    """Verify cache-state classification is driven by live subset coverage."""
    caching_system = _StubCachingSystem({spell_id: {"spell_id": spell_id} for spell_id in cached_ids})
    spellbook = _make_spellbook_stub(
        live_spell_ids=("spell-a", "spell-b"),
        caching_enabled=caching_enabled,
        caching_system=caching_system,
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_read_full_ahead_of_time_compilation",
        staticmethod(lambda **kwargs: True),
    )

    cache_state = SpellbookCreationSystem._build_conjure_cache_state(
        spellbook=spellbook,
        dynamic=False,
        conduit_name="root",
    )

    assert cache_state["cache_path"] == expected_path
    assert cache_state["is_full_hit"] is expected_full_hit
    assert cache_state["is_mixed"] is expected_mixed
    assert cache_state["is_full_miss"] is expected_full_miss


@pytest.mark.parametrize(
    ("full_aot", "expected_jit"),
    [
        (True, False),
        (False, True),
    ],
)
def test_build_conjure_cache_state_preserves_aot_vs_jit_posture(
        monkeypatch: pytest.MonkeyPatch,
        full_aot: bool,
        expected_jit: bool,
) -> None:
    """Verify cache-state includes the current AOT/JIT posture flags."""
    spellbook = _make_spellbook_stub(
        live_spell_ids=("spell-a",),
        caching_enabled=False,
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_read_full_ahead_of_time_compilation",
        staticmethod(lambda **kwargs: full_aot),
    )

    cache_state = SpellbookCreationSystem._build_conjure_cache_state(
        spellbook=spellbook,
        dynamic=True,
        conduit_name="root",
    )

    assert cache_state["full_ahead_of_time_compilation"] is full_aot
    assert cache_state["jit_mode"] is expected_jit


def test_build_conjure_cache_state_passes_conduit_name_into_cache_system(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify conjure cache classification uses the requested conduit namespace."""
    seen_conduit_names = []
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=("spell-a",),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._get_or_create_caching_system = lambda conduit_name=None: (
        seen_conduit_names.append(conduit_name) or caching_system
    )
    monkeypatch.setattr(
        SpellbookCreationSystem,
        "_read_full_ahead_of_time_compilation",
        staticmethod(lambda **kwargs: True),
    )

    SpellbookCreationSystem._build_conjure_cache_state(
        spellbook=spellbook,
        dynamic=False,
        conduit_name="common",
    )

    assert seen_conduit_names == ["common"]


def test_emit_cache_file_if_required_returns_false_when_not_required() -> None:
    """Verify no file emit happens when no payload was newly staged."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True)
    result = Spellbook._emit_cache_file_if_required(spellbook)
    assert result is False


def test_emit_cache_file_if_required_emits_once_when_required() -> None:
    """Verify one staged operation emits exactly once."""
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True

    result = Spellbook._emit_cache_file_if_required(spellbook)

    assert result is True
    assert caching_system.emit_calls == 1


def test_emit_cache_file_if_required_clears_emit_required_on_success() -> None:
    """Verify the emit-required flag clears after successful file emission."""
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True

    Spellbook._emit_cache_file_if_required(spellbook)

    assert spellbook._cache_emit_required is False


def test_emit_cache_file_if_required_restores_emit_required_on_failure() -> None:
    """Verify the emit-required flag is restored when file emission fails."""
    caching_system = _StubCachingSystem()
    caching_system.fail_emit = True
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True

    with pytest.raises(RuntimeError, match="emit failed"):
        Spellbook._emit_cache_file_if_required(spellbook)

    assert spellbook._cache_emit_required is True


@pytest.mark.parametrize(
    ("caching_enabled", "emit_result", "expected_emit_calls"),
    [
        (False, True, 0),
        (True, True, 1),
        (True, False, 1),
        (False, False, 0),
    ],
)
def test_stage_cache_after_publish_only_stages_at_publish_time(
        caching_enabled: bool,
        emit_result: bool,
        expected_emit_calls: int,
) -> None:
    """Verify publish-time cache handling never emits a file directly."""
    spell = _RecordingSpell(
        caching_enabled=caching_enabled,
        emit_result=emit_result,
    )
    spell.emit_cache_file = lambda: (_ for _ in ()).throw(AssertionError("should not flush in factory"))

    CreationContextFactory._stage_cache_after_publish(
        spell=spell,
        creation_context=object(),
    )

    assert spell.emit_calls == expected_emit_calls


def test_emit_spell_cache_returns_false_when_spell_cache_disabled(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify disabled spell cache posture short-circuits staging."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True)
    spell = _RecordingSpell(caching_enabled=False)
    spell._spellbook = spellbook

    assert Spellbook._emit_spell_cache(spellbook, spell) is False


def test_emit_spell_cache_raises_for_foreign_spellbook(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify stage requests must come from the owning Spellbook."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True)
    spell = _RecordingSpell()
    spell._spellbook = object()

    with pytest.raises(RuntimeError, match="belong to this Spellbook"):
        Spellbook._emit_spell_cache(spellbook, spell)


def test_emit_spell_cache_returns_false_when_payload_already_exists(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify duplicate spell ids do not restage payloads."""
    caching_system = _StubCachingSystem({"spell-a": {"package": 1}})
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spell = _RecordingSpell(spell_id="spell-a")
    spell._spellbook = spellbook

    assert Spellbook._emit_spell_cache(spellbook, spell) is False


def test_emit_spell_cache_returns_false_when_artifact_is_missing() -> None:
    """Verify cache staging needs a live compiler artifact."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True, caching_system=_StubCachingSystem())
    spell = _RecordingSpell()
    spell._spellbook = spellbook
    spell._compiler_artifact = None

    assert Spellbook._emit_spell_cache(spellbook, spell) is False


def test_emit_spell_cache_returns_false_when_codegen_creation_is_missing() -> None:
    """Verify cache staging requires phase-11 output on the compiler artifact."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True, caching_system=_StubCachingSystem())
    spell = _RecordingSpell()
    spell._spellbook = spellbook
    spell._compiler_artifact = SimpleNamespace(_spell_codegen_creation=None)

    assert Spellbook._emit_spell_cache(spellbook, spell) is False


def test_emit_spell_cache_returns_false_when_package_build_fails(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify package build failures do not stage broken cache payloads."""
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spell = _RecordingSpell()
    spell._spellbook = spellbook
    monkeypatch.setattr(
        creation_context_cache_codec,
        "build_package",
        lambda spell: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    assert Spellbook._emit_spell_cache(spellbook, spell) is False
    assert caching_system.has_spell_payload(spell.spell_id) is False
    assert spellbook._cache_emit_required is False


def test_emit_spell_cache_stages_payload_and_sets_emit_required(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify successful staging stores the payload and marks emit required."""
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spell = _RecordingSpell()
    spell._spellbook = spellbook
    monkeypatch.setattr(
        creation_context_cache_codec,
        "build_package",
        lambda spell: {"spell_id": spell.spell_id},
    )

    assert Spellbook._emit_spell_cache(spellbook, spell) is True
    assert caching_system.get_spell_payload(spell.spell_id) == {"spell_id": spell.spell_id}
    assert spellbook._cache_emit_required is True


def test_emit_spell_cache_second_call_returns_false_for_same_spell_id(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify duplicate staging attempts are ignored after the first success."""
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spell = _RecordingSpell()
    spell._spellbook = spellbook
    monkeypatch.setattr(
        creation_context_cache_codec,
        "build_package",
        lambda spell: {"spell_id": spell.spell_id},
    )

    assert Spellbook._emit_spell_cache(spellbook, spell) is True
    assert Spellbook._emit_spell_cache(spellbook, spell) is False


def test_emit_spell_cache_file_returns_false_when_spell_cache_disabled() -> None:
    """Verify explicit spell-facing file emit short-circuits when disabled."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True)
    spell = _RecordingSpell(caching_enabled=False)
    spell._spellbook = spellbook

    assert Spellbook._emit_cache_file(spellbook, spell) is False


def test_emit_spell_cache_file_raises_for_foreign_spellbook() -> None:
    """Verify explicit file emit still enforces spell ownership."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=True)
    spell = _RecordingSpell()
    spell._spellbook = object()

    with pytest.raises(RuntimeError, match="belong to this Spellbook"):
        Spellbook._emit_cache_file(spellbook, spell)


def test_emit_conduit_cache_file_at_conjure_end_noops_when_disabled() -> None:
    """Verify conjure-end emit does nothing when frame caching is disabled."""
    spellbook = _make_spellbook_stub(live_spell_ids=(), caching_enabled=False)
    SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end(
        spellbook=spellbook,
    )


def test_emit_conduit_cache_file_at_conjure_end_noops_when_not_required() -> None:
    """Verify conjure-end emit does not write without newly staged cache."""
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )

    SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end(
        spellbook=spellbook,
    )

    assert caching_system.emit_calls == 0


def test_emit_conduit_cache_file_at_conjure_end_emits_when_required() -> None:
    """Verify conjure-end emit writes once after staged cache."""
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True

    SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end(
        spellbook=spellbook,
    )

    assert caching_system.emit_calls == 1


def test_emit_conduit_cache_file_at_conjure_end_swallows_emit_failure() -> None:
    """Verify conjure-end emit logs and continues on file-write failure."""
    caching_system = _StubCachingSystem()
    caching_system.fail_emit = True
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True

    SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end(
        spellbook=spellbook,
    )

    assert spellbook._cache_emit_required is True


@pytest.mark.parametrize(
    ("package_by_spell_id", "expected_complete", "expected_required"),
    [
        ({"spell-a": {"package": 1}}, True, False),
        ({}, False, True),
        ({"spell-a": RuntimeError("bad package")}, False, True),
        ({"spell-b": {"package": 2}}, False, True),
    ],
)
def test_load_cached_creation_contexts_for_conjure_updates_runtime_flags(
        monkeypatch: pytest.MonkeyPatch,
        package_by_spell_id: Dict[str, Any],
        expected_complete: bool,
        expected_required: bool,
) -> None:
    """Verify full-hit cache load marks spells ready only on successful reload."""
    caching_system = _StubCachingSystem(package_by_spell_id)
    spell = _RecordingSpell(spell_id="spell-a")
    spellbook = _make_spellbook_stub(
        live_spell_ids=("spell-a",),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._spell_id_pool = {"spell-a": spell}

    def _load_creation_context(spell_obj: Any, package: Any, publish: bool = True) -> Any:
        if isinstance(package, Exception):
            raise package
        return object()

    monkeypatch.setattr(
        creation_context_cache_codec,
        "load_creation_context",
        _load_creation_context,
    )

    SpellbookCreationSystem._load_cached_creation_contexts_for_conjure(
        spellbook=spellbook,
        cache_state={
            "caching_system": caching_system,
            "live_spell_ids": {"spell-a"},
        },
    )

    assert spell.resolution_complete is expected_complete
    assert spell.resolution_required is expected_required


def test_load_cached_creation_contexts_for_conjure_skips_missing_spell_objects(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify full-hit load ignores live spell ids missing from the spell pool."""
    caching_system = _StubCachingSystem({"spell-a": {"package": 1}})
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._spell_id_pool = {}

    load_calls = []
    monkeypatch.setattr(
        creation_context_cache_codec,
        "load_creation_context",
        lambda spell, package, publish=True: load_calls.append((spell, package)),
    )

    SpellbookCreationSystem._load_cached_creation_contexts_for_conjure(
        spellbook=spellbook,
        cache_state={
            "caching_system": caching_system,
            "live_spell_ids": {"spell-a"},
        },
    )

    assert load_calls == []
