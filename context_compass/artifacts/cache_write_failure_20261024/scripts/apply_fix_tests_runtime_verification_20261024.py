"""Update the Spellbook cache-orchestration unit tests for the cache-save fix (melder_0, 2026-10-24; Note 21).

Anchored read-modify-write of tests/unit/melder/spellbook/test_cache_runtime_verification.py: the stub's `emit()`
returns a bool like `CachingSystem.emit()` and can refuse a save; new tests pin that a refused save returns False
with the flag cleared and no retry, that conjure end leaves the flag cleared, and that `Spellbook._emit_cache_file`
and `Spell.emit_cache_file` report a refused save as False (patch cache_save_best_effort_2026_10_24, M2).
"""
import pathlib
import sys

PATH = pathlib.Path.home() / "mnt/melder_private/tests/unit/melder/spellbook/test_cache_runtime_verification.py"


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        sys.exit(f"ANCHOR {label}: found {count}")
    return text.replace(old, new)


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    text = once(text, "from melder.aether.spellbook.spellbook import Spellbook\n",
                "from melder.aether.spellbook.spell import Spell\nfrom melder.aether.spellbook.spellbook import Spellbook\n",
                "import")
    text = once(text, "        self.emit_calls = 0\n        self.fail_emit = False\n", """\
        self.emit_calls = 0
        self.fail_emit = False
        # A save the operating system refuses: `CachingSystem.emit()` returns False instead of raising.
        self.refuse_emit = False
""", "stub init")
    text = once(text, """\
    def emit(self) -> None:
        self.emit_calls += 1
        if self.fail_emit:
            raise RuntimeError("emit failed")
""", """\
    def emit(self) -> bool:
        \"\"\"Mirror `CachingSystem.emit()`: True when written, False when the save is refused.\"\"\"
        self.emit_calls += 1
        if self.fail_emit:
            raise RuntimeError("emit failed")
        return not self.refuse_emit
""", "stub emit")
    text = once(text, """\
    with pytest.raises(RuntimeError, match="emit failed"):
        Spellbook._emit_cache_file_if_required(spellbook)

    assert spellbook._cache_emit_required is True
""", """\
    with pytest.raises(RuntimeError, match="emit failed"):
        Spellbook._emit_cache_file_if_required(spellbook)

    assert spellbook._cache_emit_required is True


def test_emit_cache_file_if_required_returns_false_and_keeps_the_flag_cleared_when_the_save_is_refused() -> None:
    \"\"\"
    A save the operating system refuses returns False and leaves the emit-required flag cleared.

    Contract (TASK-2026-10-24-cache_file_write_failure_fails_meld, 0.2.8266):
        `CachingSystem.emit()` reports a refused save as False; the Book passes it on and does not restore the
        flag, so the meld that triggered the save returns its object and no later meld retries it. Until 0.2.8266
        the refusal raised out of the meld and the flag came back set.
    \"\"\"
    caching_system = _StubCachingSystem()
    caching_system.refuse_emit = True
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True

    result = Spellbook._emit_cache_file_if_required(spellbook)

    assert result is False
    assert caching_system.emit_calls == 1
    assert spellbook._cache_emit_required is False


def test_emit_cache_file_if_required_does_not_retry_a_refused_save_until_cache_is_staged_again() -> None:
    \"\"\"
    After a refused save the next operation boundary does not save again until new cache is staged.

    Contract:
        No retry storm: a lasting refusal (a read-only folder) costs one save per staging, not one per meld.
    \"\"\"
    caching_system = _StubCachingSystem()
    caching_system.refuse_emit = True
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True
    Spellbook._emit_cache_file_if_required(spellbook)

    second = Spellbook._emit_cache_file_if_required(spellbook)
    spellbook._cache_emit_required = True
    caching_system.refuse_emit = False
    after_new_staging = Spellbook._emit_cache_file_if_required(spellbook)

    assert second is False
    assert after_new_staging is True
    assert caching_system.emit_calls == 2
""", "new if_required tests")
    text = once(text, """\
    with pytest.raises(RuntimeError, match="belong to this Spellbook"):
        Spellbook._emit_cache_file(spellbook, spell)
""", """\
    with pytest.raises(RuntimeError, match="belong to this Spellbook"):
        Spellbook._emit_cache_file(spellbook, spell)


def test_emit_spell_cache_file_returns_true_when_the_save_is_written() -> None:
    \"\"\"Verify the explicit file emit reports a written save as True.\"\"\"
    caching_system = _StubCachingSystem()
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True
    spell = _RecordingSpell()
    spell._spellbook = spellbook

    assert Spellbook._emit_cache_file(spellbook, spell) is True
    assert caching_system.emit_calls == 1


def test_emit_spell_cache_file_returns_false_when_the_save_is_refused() -> None:
    \"\"\"
    The explicit file emit reports a refused save as False instead of raising (D2, 0.2.8266).
    \"\"\"
    caching_system = _StubCachingSystem()
    caching_system.refuse_emit = True
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True
    spell = _RecordingSpell()
    spell._spellbook = spellbook

    assert Spellbook._emit_cache_file(spellbook, spell) is False
    assert caching_system.emit_calls == 1
    assert spellbook._cache_emit_required is False


def test_spell_emit_cache_file_returns_false_when_the_book_save_is_refused() -> None:
    \"\"\"
    `Spell.emit_cache_file()`, the public explicit save, returns False for a refused save (D2, 0.2.8266).

    Contract:
        The Spell delegates to its owning Spellbook and returns what the Book returned; until 0.2.8266 a save the
        operating system refused raised its OSError out of this call.
    \"\"\"
    caching_system = _StubCachingSystem()
    caching_system.refuse_emit = True
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    spellbook._cache_emit_required = True
    spell = SimpleNamespace(check_cleaned=lambda: None, _caching_enabled=True, _spellbook=spellbook)
    spellbook._emit_cache_file = lambda requesting_spell: Spellbook._emit_cache_file(spellbook, requesting_spell)

    assert Spell.emit_cache_file(spell) is False
    assert caching_system.emit_calls == 1
""", "new emit_cache_file tests")
    text = once(text, """\
    SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end(
        spellbook=spellbook,
    )

    assert spellbook._cache_emit_required is True
""", """\
    SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end(
        spellbook=spellbook,
    )

    assert spellbook._cache_emit_required is True


def test_emit_conduit_cache_file_at_conjure_end_leaves_the_flag_cleared_when_the_save_is_refused() -> None:
    \"\"\"
    A refused end-of-conjure save is no error: conjure logs nothing itself and the flag stays cleared.

    Contract (0.2.8266):
        The cache utility logs the refusal and returns False, so conjure's own error log stays silent and the first
        meld does not retry the save; the staged payloads are saved at the next staging.
    \"\"\"
    caching_system = _StubCachingSystem()
    caching_system.refuse_emit = True
    spellbook = _make_spellbook_stub(
        live_spell_ids=(),
        caching_enabled=True,
        caching_system=caching_system,
    )
    errors: list[tuple[Any, ...]] = []
    spellbook._logger = SimpleNamespace(error=lambda *args, **kwargs: errors.append(args))
    spellbook._cache_emit_required = True

    SpellbookCreationSystem._emit_conduit_cache_file_at_conjure_end(
        spellbook=spellbook,
    )

    assert caching_system.emit_calls == 1
    assert spellbook._cache_emit_required is False
    assert errors == []
""", "new conjure end test")
    if "\r" in text:
        sys.exit("CR")
    compile(text, str(PATH), "exec")
    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", PATH.name, len(text.splitlines()), "lines")


if __name__ == "__main__":
    main()
