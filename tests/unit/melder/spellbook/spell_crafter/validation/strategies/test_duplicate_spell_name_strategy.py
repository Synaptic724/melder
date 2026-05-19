import pytest
from typing import Dict, List, Optional

from melder.aether.spellbook.spell_crafter.validation.spell_validation_context import (
    SpellValidationContext,
)
from melder.aether.spellbook.spell_crafter.validation.spell_validation_issue import (
    SpellValidationIssue,
)
from melder.aether.spellbook.spell_crafter.validation.strategies.duplicate_spell_name_strategy import (
    DuplicateSpellNameStrategy,
)


class _SpellIndexStub:
    """
    Purpose:
        Provide a minimal spell index with id and current access.
    Contract:
        Exposes id and current, optionally raising on current access.
    """

    def __init__(
        self,
        *,
        current: Optional[str],
        index_id: Optional[str] = None,
        raise_on_current: bool = False,
    ) -> None:
        """
        Purpose:
            Initialize the stub with id values and error behavior.
        Contract:
            Stores current and id; optionally raises on current access.
        Args:
            current: Spell identifier returned by current.
            index_id: Optional index id for diagnostics.
            raise_on_current: Whether current access should raise.
        Returns:
            None.
        """
        self._current = current
        self.id = index_id
        self._raise_on_current = raise_on_current

    @property
    def current(self) -> Optional[str]:
        """
        Purpose:
            Return the current spell id or raise when configured.
        Contract:
            Raises RuntimeError when raise_on_current is True.
        Returns:
            Optional[str]: Current spell id.
        Raises:
            RuntimeError: When configured to raise.
        """
        if self._raise_on_current:
            raise RuntimeError("current error")
        return self._current


class _SpellStub:
    """
    Purpose:
        Provide a spell stub with name and identity attributes.
    Contract:
        Optionally omits spell_name for missing-name tests.
    """

    def __init__(
        self,
        *,
        spell_id: str,
        spell_name: Optional[str] = "spell-name",
        spellframe: Optional[object] = None,
        binding_name: Optional[str] = None,
        include_spell_name: bool = True,
    ) -> None:
        """
        Purpose:
            Initialize the stub with identifiers and optional metadata.
        Contract:
            Creates a spell_index stub and sets name metadata when requested.
        Args:
            spell_id: Spell identifier for spell_index.current.
            spell_name: Optional spell name value.
            spellframe: Optional spellframe metadata.
            binding_name: Optional binding name metadata.
            include_spell_name: Whether to set spell_name on the stub.
        Returns:
            None.
        """
        self.spell_index = _SpellIndexStub(current=spell_id)
        self.spell_name = spell_name if include_spell_name else None
        self.spellframe = spellframe
        self.binding_name = binding_name


class _SpellbookStub:
    """
    Purpose:
        Provide a spellbook stub exposing a spell_id pool.
    Contract:
        Stores spells by spell_id for validation strategies.
    """

    def __init__(
        self,
        spells: List[_SpellStub],
        *,
        spell_id_pool: Optional[Dict[str, _SpellStub]] = None,
    ) -> None:
        """
        Purpose:
            Store spells in the spell_id pool.
        Contract:
            Builds a mapping from spell_id to spell unless one is supplied.
        Args:
            spells: Spells to expose via spell_id pool.
            spell_id_pool: Optional prebuilt spell_id mapping to use directly.
        Returns:
            None.
        """
        if spell_id_pool is not None:
            self._spell_id_pool = spell_id_pool
            return
        self._spell_id_pool = {spell.spell_index.current: spell for spell in spells}


class _CancelStub:
    """
    Purpose:
        Provide a cancellation stub that raises when set.
    Contract:
        throw_if_set raises RuntimeError when is_set is True.
    """

    def __init__(self, *, is_set: bool) -> None:
        """
        Purpose:
            Initialize the stub with a fixed cancellation state.
        Contract:
            Stores the provided state for is_set queries.
        Args:
            is_set: Whether cancellation is active.
        Returns:
            None.
        """
        self._is_set = is_set
        self.throw_calls = 0

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Report whether cancellation is active.
        Contract:
            Returns the configured state.
        Returns:
            bool: True when cancellation is active.
        """
        return self._is_set

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise when cancellation is active.
        Contract:
            Increments throw_calls on each invocation.
        Raises:
            RuntimeError: When cancellation is active.
        """
        self.throw_calls += 1
        if self._is_set:
            raise RuntimeError("cancelled")


def _make_context(
    *,
    spell: _SpellStub,
    spellbook: Optional[_SpellbookStub],
    cancel_event: Optional[object] = None,
    issues: Optional[List[SpellValidationIssue]] = None,
) -> SpellValidationContext:
    """
    Purpose:
        Build a SpellValidationContext for strategy tests.
    Contract:
        Returns a context with the provided spell, spellbook, and issues list.
    Args:
        spell: Spell under validation.
        spellbook: Spellbook stub or None.
        cancel_event: Cancellation stub or None.
        issues: Optional issues list to populate.
    Returns:
        SpellValidationContext: The configured validation context.
    """
    if issues is None:
        issues = []
    return SpellValidationContext(
        spell=spell,
        spellbook=spellbook,
        requirements=None,
        symbolic_graph=None,
        resolution_frame=None,
        cancel_event=cancel_event,
        issues=issues,
    )


def test_init_sets_name_and_description() -> None:
    """
    Purpose:
        Verify strategy metadata is initialized.
    Contract:
        Name matches the expected identifier and description is non-empty.
    Returns:
        None.
    Raises:
        AssertionError: If metadata is missing or incorrect.
    """
    strategy = DuplicateSpellNameStrategy()
    assert strategy.name == "duplicate_spell_name"
    assert "spell_name" in strategy.description


def test_validate_without_spellbook_is_noop() -> None:
    """
    Purpose:
        Ensure validation exits when no spellbook is available.
    Contract:
        No issues are added without a spellbook.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DuplicateSpellNameStrategy()
    issues: list[SpellValidationIssue] = []
    context = _make_context(
        spell=_SpellStub(spell_id="root"),
        spellbook=None,
        issues=issues,
    )

    strategy.validate(context)

    assert issues == []


def test_validate_missing_spell_name_value_is_noop() -> None:
    """
    Purpose:
        Ensure missing spell_name value suppresses validation.
    Contract:
        No issues are added when the spell name is None.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DuplicateSpellNameStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", include_spell_name=False)
    spellbook = _SpellbookStub([spell])
    context = _make_context(spell=spell, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_empty_spell_name_is_noop() -> None:
    """
    Purpose:
        Ensure empty spell_name values suppress validation.
    Contract:
        No issues are added when the spell name is empty.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DuplicateSpellNameStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", spell_name="")
    spellbook = _SpellbookStub([spell])
    context = _make_context(spell=spell, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_non_matching_spell_name_is_noop() -> None:
    """
    Purpose:
        Ensure non-matching spell names do not emit issues.
    Contract:
        Validation completes without adding diagnostics.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DuplicateSpellNameStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", spell_name="Root")
    other = _SpellStub(spell_id="other", spell_name="Other")
    spellbook = _SpellbookStub([spell, other])
    context = _make_context(spell=spell, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_single_match_is_noop() -> None:
    """
    Purpose:
        Ensure a single matching spell does not emit issues.
    Contract:
        No issues are added for a single matching spell.
    Returns:
        None.
    Raises:
        AssertionError: If issues are added.
    """
    strategy = DuplicateSpellNameStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", spell_name="Root")
    spellbook = _SpellbookStub([spell])
    context = _make_context(spell=spell, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert issues == []


def test_validate_duplicates_emit_issue_with_collisions() -> None:
    """
    Purpose:
        Verify duplicates produce a detailed error issue.
    Contract:
        Issue includes collision metadata for each matching spell.
    Returns:
        None.
    Raises:
        AssertionError: If issue details are missing or incorrect.
    """
    strategy = DuplicateSpellNameStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", spell_name="Root")
    index_a = _SpellIndexStub(current="a", index_id="idx-a")
    index_b = _SpellIndexStub(current="b", index_id="idx-b")
    spell_a = _SpellStub(
        spell_id="a",
        spell_name="Root",
        spellframe="frame-a",
        binding_name="bind-a",
    )
    spell_a.spell_index = index_a
    spell_b = _SpellStub(
        spell_id="b",
        spell_name="Root",
        spellframe="frame-b",
        binding_name="bind-b",
    )
    spell_b.spell_index = index_b
    spellbook = _SpellbookStub([spell, spell_a, spell_b])
    context = _make_context(spell=spell, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    assert len(issues) == 1
    issue = issues[0]
    assert issue.severity == "error"
    assert issue.code == "DUPLICATE_SPELL_NAME"
    assert issue.details["spell_name"] == "Root"
    assert issue.details["collision_count"] == 3
    collisions = issue.details["collisions"]
    assert len(collisions) == 3
    by_spell_id = {entry["spell_id"]: entry for entry in collisions}
    assert by_spell_id["a"]["spell_index_id"] == "idx-a"
    assert by_spell_id["a"]["spellframe"] == "frame-a"
    assert by_spell_id["a"]["binding_name"] == "bind-a"
    assert by_spell_id["b"]["spell_index_id"] == "idx-b"
    assert by_spell_id["b"]["spellframe"] == "frame-b"
    assert by_spell_id["b"]["binding_name"] == "bind-b"


def test_validate_handles_index_current_errors() -> None:
    """
    Purpose:
        Ensure index.current errors do not block collision reporting.
    Contract:
        Collision entries use spell_id pool keys even if index.current fails.
    Returns:
        None.
    Raises:
        AssertionError: If spell_id does not match the pool key.
    """
    strategy = DuplicateSpellNameStrategy()
    issues: list[SpellValidationIssue] = []
    spell = _SpellStub(spell_id="root", spell_name="Root")
    index_bad = _SpellIndexStub(
        current="bad",
        index_id="idx-bad",
        raise_on_current=True,
    )
    index_ok = _SpellIndexStub(current="ok", index_id="idx-ok")
    spell_bad = _SpellStub(spell_id="bad", spell_name="Root")
    spell_bad.spell_index = index_bad
    spell_ok = _SpellStub(spell_id="ok", spell_name="Root")
    spell_ok.spell_index = index_ok
    spellbook = _SpellbookStub(
        [],
        spell_id_pool={"root": spell, "bad": spell_bad, "ok": spell_ok},
    )
    context = _make_context(spell=spell, spellbook=spellbook, issues=issues)

    strategy.validate(context)

    collisions = issues[0].details["collisions"]
    bad_entry = next(entry for entry in collisions if entry["spell_index_id"] == "idx-bad")
    assert bad_entry["spell_id"] == "bad"


def test_validate_cancellation_preempts() -> None:
    """
    Purpose:
        Ensure cancellation is honored before any work begins.
    Contract:
        validate raises and does not emit issues when cancelled.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    strategy = DuplicateSpellNameStrategy()
    issues: list[SpellValidationIssue] = []
    cancel_event = _CancelStub(is_set=True)
    spell = _SpellStub(spell_id="root", spell_name="Root")
    spellbook = _SpellbookStub([spell])
    context = _make_context(
        spell=spell,
        spellbook=spellbook,
        cancel_event=cancel_event,
        issues=issues,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.validate(context)

    assert issues == []
    assert cancel_event.throw_calls == 1
