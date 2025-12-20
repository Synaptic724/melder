from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

import pytest

from melder.spellbook.spell_crafter.spellbook_scanner import SpellbookScanner


class _SpellIndexStub:
    """
    Purpose:
        Provide a hashable spell index stub for scanner tests.
    Contract:
        Equality and hashing are derived from the provided key string.
    """

    def __init__(self, key: str) -> None:
        """
        Purpose:
            Initialize the stub with a key.
        Contract:
            Stores key for hashing and equality checks.
        Args:
            key: Unique key string for the index.
        Returns:
            None.
        """
        self.key = key

    def __hash__(self) -> int:
        """
        Purpose:
            Provide stable hashing for mapping usage.
        Contract:
            Hash is derived from the key string.
        Returns:
            int: Hash of the key.
        """
        return hash(self.key)

    def __eq__(self, other: object) -> bool:
        """
        Purpose:
            Compare two indices by key value.
        Contract:
            Returns True only for matching key strings.
        Args:
            other: Object to compare against.
        Returns:
            bool: True when keys match.
        """
        if not isinstance(other, _SpellIndexStub):
            return False
        return self.key == other.key

    def __repr__(self) -> str:
        """
        Purpose:
            Provide a debug-friendly representation.
        Contract:
            Includes the key in the string.
        Returns:
            str: Representation of the index stub.
        """
        return f"_SpellIndexStub({self.key!r})"


class _SpellStub:
    """
    Purpose:
        Provide a minimal spell stub for scanner queries.
    Contract:
        Exposes the attributes SpellbookScanner inspects.
    """

    def __init__(
        self,
        *,
        spellframe: object | None = None,
        binding_name: str | None = None,
        spell_name: str = "spell",
        spell_obj: object | None = None,
        has_existing_object: bool = False,
        user_created_object: object | None = None,
    ) -> None:
        """
        Purpose:
            Initialize the stub with spell metadata.
        Contract:
            Stores the provided values without validation.
        Args:
            spellframe: Frame object for the spell.
            binding_name: Optional binding name string.
            spell_name: Name of the spell.
            spell_obj: Underlying callable or class.
            has_existing_object: Whether an existing object is attached.
            user_created_object: Existing object attached to the spell.
        Returns:
            None.
        """
        self.spellframe = spellframe
        self.binding_name = binding_name
        self.spell_name = spell_name
        self.spell = spell_obj
        self.has_existing_object = has_existing_object
        self.user_created_object = user_created_object


class _SpellbookStub:
    """
    Purpose:
        Provide a Spellbook-like container for scanner tests.
    Contract:
        Exposes spells and contracted_spells mappings.
    """

    def __init__(
        self,
        *,
        spells: Mapping[_SpellIndexStub, _SpellStub],
        contracted_spells: object,
    ) -> None:
        """
        Purpose:
            Initialize the stub with local and contracted spell maps.
        Contract:
            Stores copies of mappings for scanner access.
        Args:
            spells: Mapping of local spell indices to spells.
            contracted_spells: Mapping-like object of contracted spells.
        Returns:
            None.
        """
        self.spells = dict(spells)
        self.contracted_spells = contracted_spells


class _ContractedSpellsStub:
    """
    Purpose:
        Provide a contracted spells mapping stub with call tracking.
    Contract:
        items() returns configured conduit mappings and records access.
    """

    def __init__(
        self,
        items_result: Sequence[tuple[str, Mapping[_SpellIndexStub, _SpellStub]]],
        *,
        raise_on_items: bool = False,
    ) -> None:
        """
        Purpose:
            Initialize the stub with conduit entries.
        Contract:
            Stores a list of conduit mappings and access behavior.
        Args:
            items_result: Sequence of (conduit_id, contracted_map) pairs.
            raise_on_items: Whether items() should raise on access.
        Returns:
            None.
        """
        self._items_result = [
            (conduit_id, dict(contracted))
            for conduit_id, contracted in items_result
        ]
        self._raise_on_items = raise_on_items
        self.items_calls = 0

    def items(self) -> list[tuple[str, dict[_SpellIndexStub, _SpellStub]]]:
        """
        Purpose:
            Return the configured conduit entries.
        Contract:
            Increments items_calls and returns a list of entries.
        Returns:
            list[tuple[str, dict[_SpellIndexStub, _SpellStub]]]: Conduit entries.
        Raises:
            RuntimeError: If raise_on_items is True.
        """
        self.items_calls += 1
        if self._raise_on_items:
            raise RuntimeError("contracted items accessed unexpectedly")
        return list(self._items_result)


class _EqFrameStub:
    """
    Purpose:
        Provide a frame stub with equality semantics.
    Contract:
        Equality compares the stored value.
    """

    def __init__(self, value: str) -> None:
        """
        Purpose:
            Initialize the stub with a value for equality checks.
        Contract:
            Stores the provided value.
        Args:
            value: Value used for equality comparisons.
        Returns:
            None.
        """
        self.value = value

    def __eq__(self, other: object) -> bool:
        """
        Purpose:
            Compare two frame stubs by value.
        Contract:
            Returns True only for matching values.
        Args:
            other: Object to compare against.
        Returns:
            bool: True when values match.
        """
        if not isinstance(other, _EqFrameStub):
            return False
        return self.value == other.value

    def __repr__(self) -> str:
        """
        Purpose:
            Provide a debug-friendly representation.
        Contract:
            Includes the value in the string.
        Returns:
            str: Representation of the frame stub.
        """
        return f"_EqFrameStub({self.value!r})"


class _EqTargetStub:
    """
    Purpose:
        Provide a target stub with equality semantics.
    Contract:
        Equality compares the stored value.
    """

    def __init__(self, value: str) -> None:
        """
        Purpose:
            Initialize the stub with a value for equality checks.
        Contract:
            Stores the provided value.
        Args:
            value: Value used for equality comparisons.
        Returns:
            None.
        """
        self.value = value

    def __eq__(self, other: object) -> bool:
        """
        Purpose:
            Compare two target stubs by value.
        Contract:
            Returns True only for matching values.
        Args:
            other: Object to compare against.
        Returns:
            bool: True when values match.
        """
        if not isinstance(other, _EqTargetStub):
            return False
        return self.value == other.value

    def __repr__(self) -> str:
        """
        Purpose:
            Provide a debug-friendly representation.
        Contract:
            Includes the value in the string.
        Returns:
            str: Representation of the target stub.
        """
        return f"_EqTargetStub({self.value!r})"


def _make_spell_pair(
    key: str,
    *,
    spellframe: object | None = None,
    binding_name: str | None = None,
    spell_name: str = "spell",
    spell_obj: object | None = None,
    has_existing_object: bool = False,
    user_created_object: object | None = None,
) -> tuple[_SpellIndexStub, _SpellStub]:
    """
    Purpose:
        Build a (index, spell) pair for scanner tests.
    Contract:
        Returns a new index and spell populated with the provided values.
    Args:
        key: Unique key for the spell index.
        spellframe: Frame object for the spell.
        binding_name: Optional binding name.
        spell_name: Name of the spell.
        spell_obj: Underlying callable or class.
        has_existing_object: Whether an existing object is attached.
        user_created_object: Existing object attached to the spell.
    Returns:
        tuple[_SpellIndexStub, _SpellStub]: The created index/spell pair.
    """
    index = _SpellIndexStub(key)
    spell = _SpellStub(
        spellframe=spellframe,
        binding_name=binding_name,
        spell_name=spell_name,
        spell_obj=spell_obj,
        has_existing_object=has_existing_object,
        user_created_object=user_created_object,
    )
    return index, spell


def _make_spellbook(
    *,
    local: Sequence[tuple[_SpellIndexStub, _SpellStub]] = (),
    contracted: Sequence[tuple[str, Mapping[_SpellIndexStub, _SpellStub]]] = (),
    contracted_spells_override: object | None = None,
) -> _SpellbookStub:
    """
    Purpose:
        Build a spellbook stub with local and contracted spells.
    Contract:
        Returns a stub with mappings derived from provided inputs.
    Args:
        local: Local spell entries.
        contracted: Contracted conduit entries.
        contracted_spells_override: Optional override for contracted_spells.
    Returns:
        _SpellbookStub: The constructed spellbook stub.
    """
    local_map = {index: spell for index, spell in local}
    if contracted_spells_override is None:
        contracted_map = {
            conduit_id: dict(contracted_spells)
            for conduit_id, contracted_spells in contracted
        }
    else:
        contracted_map = contracted_spells_override
    return _SpellbookStub(spells=local_map, contracted_spells=contracted_map)


def _make_scanner(
    *,
    local: Sequence[tuple[_SpellIndexStub, _SpellStub]] = (),
    contracted: Sequence[tuple[str, Mapping[_SpellIndexStub, _SpellStub]]] = (),
    contracted_spells_override: object | None = None,
) -> tuple[SpellbookScanner, _SpellbookStub]:
    """
    Purpose:
        Build a SpellbookScanner with a stub spellbook.
    Contract:
        Returns the scanner and its underlying spellbook stub.
    Args:
        local: Local spell entries.
        contracted: Contracted conduit entries.
        contracted_spells_override: Optional override for contracted_spells.
    Returns:
        tuple[SpellbookScanner, _SpellbookStub]: Scanner and spellbook.
    """
    spellbook = _make_spellbook(
        local=local,
        contracted=contracted,
        contracted_spells_override=contracted_spells_override,
    )
    return SpellbookScanner(spellbook), spellbook


def _call_scanner_method(scanner: SpellbookScanner, method_name: str) -> object:
    """
    Purpose:
        Invoke a scanner method by name without reflection.
    Contract:
        Dispatches to supported methods and returns their results.
    Args:
        scanner: Scanner instance to call.
        method_name: Name of the method to invoke.
    Returns:
        object: Method return value.
    Raises:
        ValueError: If method_name is not supported.
    """
    if method_name == "iter_local_spells":
        return list(scanner.iter_local_spells())
    if method_name == "iter_contracted_spells":
        return list(scanner.iter_contracted_spells())
    if method_name == "iter_all_spells":
        return list(scanner.iter_all_spells())
    if method_name == "iter_spells_include_contracted":
        return list(scanner.iter_spells(include_contracted=True))
    if method_name == "iter_spells_local_only":
        return list(scanner.iter_spells(include_contracted=False))
    if method_name == "find_by_frame_and_binding":
        return scanner.find_by_frame_and_binding(spellframe=object(), binding_name=None)
    if method_name == "find_single_by_frame_and_binding":
        return scanner.find_single_by_frame_and_binding(spellframe=object(), binding_name=None)
    if method_name == "find_by_frame":
        return scanner.find_by_frame(spellframe=object())
    if method_name == "find_by_binding_name":
        return scanner.find_by_binding_name(binding_name=None)
    if method_name == "find_by_spell_name":
        return scanner.find_by_spell_name("spell")
    if method_name == "find_by_index":
        return scanner.find_by_index(_SpellIndexStub("idx"))
    if method_name == "find_by_target":
        return scanner.find_by_target(object())
    raise ValueError(f"Unsupported method name: {method_name}")


def test_init_requires_spellbook() -> None:
    """
    Purpose:
        Ensure the scanner rejects a None spellbook.
    Contract:
        __init__ raises ValueError when spellbook is None.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    with pytest.raises(ValueError, match="spellbook must not be None"):
        SpellbookScanner(None)


def test_spellbook_property_returns_bound_spellbook() -> None:
    """
    Purpose:
        Verify spellbook property exposes the bound spellbook.
    Contract:
        Property returns the exact spellbook instance provided at init.
    Returns:
        None.
    Raises:
        AssertionError: If the property does not return the bound spellbook.
    """
    scanner, spellbook = _make_scanner()

    assert scanner.spellbook is spellbook


def test_spellbook_property_raises_after_cleanup() -> None:
    """
    Purpose:
        Confirm spellbook property enforces cleaned checks.
    Contract:
        Access after cleanup raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not block access.
    """
    scanner, _ = _make_scanner()
    scanner.cleanup()

    with pytest.raises(RuntimeError, match="cleaned"):
        _ = scanner.spellbook


def test_cleanup_clears_spellbook_reference() -> None:
    """
    Purpose:
        Ensure cleanup drops the spellbook reference.
    Contract:
        cleanup sets _spellbook to None and marks cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear references.
    """
    scanner, _ = _make_scanner()

    scanner.cleanup()

    assert scanner.cleaned is True
    assert scanner._spellbook is None


def test_cleanup_idempotent() -> None:
    """
    Purpose:
        Verify cleanup is idempotent.
    Contract:
        Multiple cleanup calls do not raise and preserve cleaned state.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    scanner, _ = _make_scanner()

    scanner.cleanup()
    scanner.cleanup()

    assert scanner.cleaned is True


def test_iter_local_spells_yields_local_entries() -> None:
    """
    Purpose:
        Validate local spell iteration yields local entries.
    Contract:
        iter_local_spells returns the local mapping in order.
    Returns:
        None.
    Raises:
        AssertionError: If local entries are missing or reordered.
    """
    local = [
        _make_spell_pair("a"),
        _make_spell_pair("b"),
    ]
    scanner, _ = _make_scanner(local=local)

    assert list(scanner.iter_local_spells()) == local


def test_iter_local_spells_empty() -> None:
    """
    Purpose:
        Ensure local spell iteration handles empty spellbooks.
    Contract:
        iter_local_spells yields no entries when local mapping is empty.
    Returns:
        None.
    Raises:
        AssertionError: If any entries are yielded.
    """
    scanner, _ = _make_scanner()

    assert list(scanner.iter_local_spells()) == []


def test_iter_contracted_spells_yields_entries() -> None:
    """
    Purpose:
        Validate contracted spell iteration yields contracted entries.
    Contract:
        iter_contracted_spells flattens conduit mappings in order.
    Returns:
        None.
    Raises:
        AssertionError: If contracted entries are missing or reordered.
    """
    contracted = [
        ("c1", dict([_make_spell_pair("a")])),
        ("c2", dict([_make_spell_pair("b"), _make_spell_pair("c")])),
    ]
    scanner, _ = _make_scanner(contracted=contracted)

    expected: list[tuple[_SpellIndexStub, _SpellStub]] = []
    expected.extend(contracted[0][1].items())
    expected.extend(contracted[1][1].items())

    assert list(scanner.iter_contracted_spells()) == expected


def test_iter_contracted_spells_empty() -> None:
    """
    Purpose:
        Ensure contracted iteration handles empty mappings.
    Contract:
        iter_contracted_spells yields no entries when none exist.
    Returns:
        None.
    Raises:
        AssertionError: If any entries are yielded.
    """
    scanner, _ = _make_scanner(contracted=[])

    assert list(scanner.iter_contracted_spells()) == []


def test_iter_all_spells_yields_local_then_contracted() -> None:
    """
    Purpose:
        Confirm all-spell iteration orders local before contracted.
    Contract:
        iter_all_spells yields local entries followed by contracted entries.
    Returns:
        None.
    Raises:
        AssertionError: If ordering is incorrect.
    """
    local = [_make_spell_pair("local")]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted")])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    expected: list[tuple[_SpellIndexStub, _SpellStub]] = []
    expected.extend(local)
    expected.extend(contracted[0][1].items())

    assert list(scanner.iter_all_spells()) == expected


def test_iter_spells_includes_contracted_by_default() -> None:
    """
    Purpose:
        Verify iter_spells includes contracted entries by default.
    Contract:
        iter_spells with include_contracted True yields all entries.
    Returns:
        None.
    Raises:
        AssertionError: If contracted entries are missing.
    """
    local = [_make_spell_pair("local")]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted")])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    result = list(scanner.iter_spells())

    assert result == local + list(contracted[0][1].items())


def test_iter_spells_excludes_contracted_when_false() -> None:
    """
    Purpose:
        Ensure iter_spells can exclude contracted entries.
    Contract:
        include_contracted False yields only local entries.
    Returns:
        None.
    Raises:
        AssertionError: If contracted entries are included.
    """
    local = [_make_spell_pair("local")]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted")])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    assert list(scanner.iter_spells(include_contracted=False)) == local


def test_iter_spells_does_not_touch_contracted_when_false() -> None:
    """
    Purpose:
        Ensure iter_spells avoids contracted access when excluded.
    Contract:
        include_contracted False does not access contracted_spells.items().
    Returns:
        None.
    Raises:
        AssertionError: If contracted access occurs.
    """
    local = [_make_spell_pair("local")]
    contracted_stub = _ContractedSpellsStub(
        items_result=[],
        raise_on_items=True,
    )
    scanner, _ = _make_scanner(local=local, contracted_spells_override=contracted_stub)

    assert list(scanner.iter_spells(include_contracted=False)) == local


def test_find_by_frame_and_binding_matches_identity() -> None:
    """
    Purpose:
        Verify frame matching uses identity checks.
    Contract:
        find_by_frame_and_binding returns spells with matching frame identity.
    Returns:
        None.
    Raises:
        AssertionError: If identity matches are not returned.
    """
    frame = object()
    local = [
        _make_spell_pair("match", spellframe=frame, binding_name="a"),
        _make_spell_pair("miss", spellframe=object(), binding_name="a"),
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_frame_and_binding(spellframe=frame, binding_name="a")

    assert list(result.keys()) == [local[0][0]]


def test_find_by_frame_and_binding_matches_equality() -> None:
    """
    Purpose:
        Confirm frame matching uses equality when identity differs.
    Contract:
        find_by_frame_and_binding matches when spellframe == requested frame.
    Returns:
        None.
    Raises:
        AssertionError: If equality matches are not returned.
    """
    spell_frame = _EqFrameStub("frame")
    requested = _EqFrameStub("frame")
    local = [_make_spell_pair("match", spellframe=spell_frame, binding_name=None)]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_frame_and_binding(spellframe=requested, binding_name=None)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_frame_and_binding_requires_binding_match() -> None:
    """
    Purpose:
        Ensure binding name mismatches are excluded from results.
    Contract:
        find_by_frame_and_binding returns empty when binding_name differs.
    Returns:
        None.
    Raises:
        AssertionError: If mismatched binding names are returned.
    """
    frame = object()
    local = [_make_spell_pair("match", spellframe=frame, binding_name="alpha")]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_frame_and_binding(spellframe=frame, binding_name="beta")

    assert result == {}


def test_find_by_frame_and_binding_handles_none_binding() -> None:
    """
    Purpose:
        Verify None binding_name matches only None-bound spells.
    Contract:
        find_by_frame_and_binding returns spells with binding_name None.
    Returns:
        None.
    Raises:
        AssertionError: If non-None bindings are returned.
    """
    frame = object()
    local = [
        _make_spell_pair("match", spellframe=frame, binding_name=None),
        _make_spell_pair("miss", spellframe=frame, binding_name="named"),
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_frame_and_binding(spellframe=frame, binding_name=None)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_frame_and_binding_excludes_contracted_when_false() -> None:
    """
    Purpose:
        Ensure contracted spells are excluded when requested.
    Contract:
        include_contracted False yields only local matches.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are returned.
    """
    frame = object()
    local = [_make_spell_pair("local", spellframe=frame, binding_name=None)]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted", spellframe=frame, binding_name=None)])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    result = scanner.find_by_frame_and_binding(
        spellframe=frame,
        binding_name=None,
        include_contracted=False,
    )

    assert list(result.keys()) == [local[0][0]]


def test_find_by_frame_and_binding_includes_contracted_when_true() -> None:
    """
    Purpose:
        Confirm contracted spells are included when requested.
    Contract:
        include_contracted True yields local and contracted matches.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are missing.
    """
    frame = object()
    local = [_make_spell_pair("local", spellframe=frame, binding_name=None)]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted", spellframe=frame, binding_name=None)])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    result = scanner.find_by_frame_and_binding(
        spellframe=frame,
        binding_name=None,
        include_contracted=True,
    )

    assert set(result.keys()) == {local[0][0], list(contracted[0][1].keys())[0]}


def test_find_single_by_frame_and_binding_returns_none_when_empty() -> None:
    """
    Purpose:
        Verify single resolution returns None when no matches exist.
    Contract:
        find_single_by_frame_and_binding returns None on empty matches.
    Returns:
        None.
    Raises:
        AssertionError: If a spell is returned.
    """
    scanner, _ = _make_scanner()

    result = scanner.find_single_by_frame_and_binding(spellframe=object(), binding_name=None)

    assert result is None


def test_find_single_by_frame_and_binding_returns_single() -> None:
    """
    Purpose:
        Confirm single resolution returns the only match.
    Contract:
        find_single_by_frame_and_binding returns the lone matching spell.
    Returns:
        None.
    Raises:
        AssertionError: If the single match is not returned.
    """
    frame = object()
    local = [_make_spell_pair("match", spellframe=frame, binding_name=None)]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_single_by_frame_and_binding(spellframe=frame, binding_name=None)

    assert result is local[0][1]


def test_find_single_by_frame_and_binding_raises_on_ambiguity() -> None:
    """
    Purpose:
        Ensure ambiguous single resolution raises by default.
    Contract:
        find_single_by_frame_and_binding raises when multiple matches exist.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguity does not raise.
    """
    frame = object()
    local = [
        _make_spell_pair("a", spellframe=frame, binding_name=None),
        _make_spell_pair("b", spellframe=frame, binding_name=None),
    ]
    scanner, _ = _make_scanner(local=local)

    with pytest.raises(RuntimeError, match="Ambiguous spell resolution"):
        scanner.find_single_by_frame_and_binding(spellframe=frame, binding_name=None)


def test_find_single_by_frame_and_binding_returns_none_on_ambiguity_when_no_raise() -> None:
    """
    Purpose:
        Confirm ambiguity can be suppressed when requested.
    Contract:
        find_single_by_frame_and_binding returns None when ambiguous and no-raise.
    Returns:
        None.
    Raises:
        AssertionError: If a spell is returned on ambiguity.
    """
    frame = object()
    local = [
        _make_spell_pair("a", spellframe=frame, binding_name=None),
        _make_spell_pair("b", spellframe=frame, binding_name=None),
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_single_by_frame_and_binding(
        spellframe=frame,
        binding_name=None,
        raise_on_ambiguity=False,
    )

    assert result is None


def test_find_single_by_frame_and_binding_excludes_contracted_when_false() -> None:
    """
    Purpose:
        Ensure contracted spells are excluded from single resolution when requested.
    Contract:
        include_contracted False returns None when only contracted matches exist.
    Returns:
        None.
    Raises:
        AssertionError: If contracted matches are returned.
    """
    frame = object()
    contracted = [
        ("c1", dict([_make_spell_pair("contracted", spellframe=frame, binding_name=None)])),
    ]
    scanner, _ = _make_scanner(local=[], contracted=contracted)

    result = scanner.find_single_by_frame_and_binding(
        spellframe=frame,
        binding_name=None,
        include_contracted=False,
    )

    assert result is None


def test_find_by_frame_matches_identity() -> None:
    """
    Purpose:
        Validate frame matching uses identity checks.
    Contract:
        find_by_frame returns spells with matching frame identity.
    Returns:
        None.
    Raises:
        AssertionError: If identity matches are missing.
    """
    frame = object()
    local = [
        _make_spell_pair("match", spellframe=frame),
        _make_spell_pair("miss", spellframe=object()),
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_frame(spellframe=frame)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_frame_matches_equality() -> None:
    """
    Purpose:
        Confirm frame matching uses equality when identity differs.
    Contract:
        find_by_frame matches when spellframe == requested frame.
    Returns:
        None.
    Raises:
        AssertionError: If equality matches are missing.
    """
    spell_frame = _EqFrameStub("frame")
    requested = _EqFrameStub("frame")
    local = [_make_spell_pair("match", spellframe=spell_frame)]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_frame(spellframe=requested)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_frame_excludes_contracted_when_false() -> None:
    """
    Purpose:
        Ensure contracted spells are excluded from frame search when requested.
    Contract:
        include_contracted False returns only local matches.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are returned.
    """
    frame = object()
    local = [_make_spell_pair("local", spellframe=frame)]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted", spellframe=frame)])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    result = scanner.find_by_frame(spellframe=frame, include_contracted=False)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_binding_name_matches_value() -> None:
    """
    Purpose:
        Verify binding name search returns matching spells.
    Contract:
        find_by_binding_name returns spells with the requested binding name.
    Returns:
        None.
    Raises:
        AssertionError: If matching bindings are missing.
    """
    local = [
        _make_spell_pair("match", binding_name="alpha"),
        _make_spell_pair("miss", binding_name="beta"),
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_binding_name(binding_name="alpha")

    assert list(result.keys()) == [local[0][0]]


def test_find_by_binding_name_matches_none() -> None:
    """
    Purpose:
        Ensure binding name search matches None bindings explicitly.
    Contract:
        find_by_binding_name with None returns only None-bound spells.
    Returns:
        None.
    Raises:
        AssertionError: If non-None bindings are returned.
    """
    local = [
        _make_spell_pair("match", binding_name=None),
        _make_spell_pair("miss", binding_name="named"),
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_binding_name(binding_name=None)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_binding_name_excludes_contracted_when_false() -> None:
    """
    Purpose:
        Confirm contracted spells are excluded from binding name search when requested.
    Contract:
        include_contracted False returns only local matches.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are returned.
    """
    local = [_make_spell_pair("local", binding_name="alpha")]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted", binding_name="alpha")])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    result = scanner.find_by_binding_name(binding_name="alpha", include_contracted=False)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_spell_name_requires_non_empty() -> None:
    """
    Purpose:
        Verify spell name search rejects empty names.
    Contract:
        find_by_spell_name raises ValueError for empty input.
    Returns:
        None.
    Raises:
        AssertionError: If empty names do not raise.
    """
    scanner, _ = _make_scanner()

    with pytest.raises(ValueError, match="spell_name cannot be empty"):
        scanner.find_by_spell_name("")


def test_find_by_spell_name_matches_exact() -> None:
    """
    Purpose:
        Ensure spell name search matches exact spell_name values.
    Contract:
        find_by_spell_name returns spells with matching spell_name.
    Returns:
        None.
    Raises:
        AssertionError: If exact matches are missing.
    """
    local = [
        _make_spell_pair("match", spell_name="alpha"),
        _make_spell_pair("miss", spell_name="beta"),
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_spell_name("alpha")

    assert list(result.keys()) == [local[0][0]]


def test_find_by_spell_name_excludes_contracted_when_false() -> None:
    """
    Purpose:
        Confirm contracted spells are excluded from spell name search when requested.
    Contract:
        include_contracted False returns only local matches.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are returned.
    """
    local = [_make_spell_pair("local", spell_name="alpha")]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted", spell_name="alpha")])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    result = scanner.find_by_spell_name("alpha", include_contracted=False)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_index_requires_non_none() -> None:
    """
    Purpose:
        Ensure find_by_index rejects None input.
    Contract:
        find_by_index raises ValueError when spell_index is None.
    Returns:
        None.
    Raises:
        AssertionError: If the expected error is not raised.
    """
    scanner, _ = _make_scanner()

    with pytest.raises(ValueError, match="spell_index cannot be None"):
        scanner.find_by_index(None)


def test_find_by_index_returns_local() -> None:
    """
    Purpose:
        Verify local index lookups return the local spell.
    Contract:
        find_by_index returns the local spell when present.
    Returns:
        None.
    Raises:
        AssertionError: If the local spell is not returned.
    """
    local = [_make_spell_pair("local")]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_index(local[0][0])

    assert result is local[0][1]


def test_find_by_index_returns_contracted() -> None:
    """
    Purpose:
        Ensure contracted index lookups return contracted spells when local is absent.
    Contract:
        find_by_index returns the first contracted match when not in local.
    Returns:
        None.
    Raises:
        AssertionError: If contracted matches are not returned.
    """
    contracted_index, contracted_spell = _make_spell_pair("contracted")
    contracted = [
        ("c1", {contracted_index: contracted_spell}),
    ]
    scanner, _ = _make_scanner(local=[], contracted=contracted)

    result = scanner.find_by_index(contracted_index)

    assert result is contracted_spell


def test_find_by_index_returns_none_when_missing() -> None:
    """
    Purpose:
        Confirm missing indices return None.
    Contract:
        find_by_index returns None when no match exists.
    Returns:
        None.
    Raises:
        AssertionError: If a spell is returned for a missing index.
    """
    scanner, _ = _make_scanner()

    result = scanner.find_by_index(_SpellIndexStub("missing"))

    assert result is None


def test_find_by_index_excludes_contracted_when_false() -> None:
    """
    Purpose:
        Ensure contracted lookups are skipped when include_contracted is False.
    Contract:
        find_by_index returns None when only contracted matches exist.
    Returns:
        None.
    Raises:
        AssertionError: If contracted matches are returned.
    """
    contracted_index, contracted_spell = _make_spell_pair("contracted")
    contracted = [
        ("c1", {contracted_index: contracted_spell}),
    ]
    scanner, _ = _make_scanner(local=[], contracted=contracted)

    result = scanner.find_by_index(contracted_index, include_contracted=False)

    assert result is None


def test_find_by_index_skips_contracted_when_local_found() -> None:
    """
    Purpose:
        Confirm local matches avoid contracted scans.
    Contract:
        find_by_index returns the local spell without accessing contracted maps.
    Returns:
        None.
    Raises:
        AssertionError: If contracted scans occur.
    """
    local = [_make_spell_pair("local")]
    contracted_stub = _ContractedSpellsStub(
        items_result=[],
        raise_on_items=True,
    )
    scanner, _ = _make_scanner(local=local, contracted_spells_override=contracted_stub)

    result = scanner.find_by_index(local[0][0])

    assert result is local[0][1]


def test_find_by_target_requires_non_none() -> None:
    """
    Purpose:
        Ensure target lookups reject None input.
    Contract:
        find_by_target raises ValueError when target is None.
    Returns:
        None.
    Raises:
        AssertionError: If None input does not raise.
    """
    scanner, _ = _make_scanner()

    with pytest.raises(ValueError, match="target cannot be None"):
        scanner.find_by_target(None)


def test_find_by_target_matches_spell_identity() -> None:
    """
    Purpose:
        Verify target lookups match spell objects by identity.
    Contract:
        find_by_target returns spells whose spell is target.
    Returns:
        None.
    Raises:
        AssertionError: If identity matches are missing.
    """
    target = object()
    local = [_make_spell_pair("match", spell_obj=target)]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_target(target)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_target_matches_spell_equality() -> None:
    """
    Purpose:
        Confirm target lookups match spell objects by equality.
    Contract:
        find_by_target returns spells whose spell equals target.
    Returns:
        None.
    Raises:
        AssertionError: If equality matches are missing.
    """
    spell_obj = _EqTargetStub("token")
    target = _EqTargetStub("token")
    local = [_make_spell_pair("match", spell_obj=spell_obj)]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_target(target)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_target_matches_existing_object() -> None:
    """
    Purpose:
        Ensure target lookups match existing objects when configured.
    Contract:
        find_by_target returns spells whose user_created_object is target.
    Returns:
        None.
    Raises:
        AssertionError: If existing-object matches are missing.
    """
    existing = object()
    local = [
        _make_spell_pair(
            "match",
            spell_obj=object(),
            has_existing_object=True,
            user_created_object=existing,
        )
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_target(existing)

    assert list(result.keys()) == [local[0][0]]


def test_find_by_target_skips_existing_object_when_flag_false() -> None:
    """
    Purpose:
        Confirm existing objects are ignored when the flag is false.
    Contract:
        find_by_target does not match user_created_object if has_existing_object is False.
    Returns:
        None.
    Raises:
        AssertionError: If a match occurs despite the flag.
    """
    existing = object()
    local = [
        _make_spell_pair(
            "miss",
            spell_obj=object(),
            has_existing_object=False,
            user_created_object=existing,
        )
    ]
    scanner, _ = _make_scanner(local=local)

    result = scanner.find_by_target(existing)

    assert result == {}


def test_find_by_target_excludes_contracted_when_false() -> None:
    """
    Purpose:
        Ensure contracted spells are excluded from target search when requested.
    Contract:
        include_contracted False returns only local matches.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells are returned.
    """
    target = object()
    local = [_make_spell_pair("local", spell_obj=target)]
    contracted = [
        ("c1", dict([_make_spell_pair("contracted", spell_obj=target)])),
    ]
    scanner, _ = _make_scanner(local=local, contracted=contracted)

    result = scanner.find_by_target(target, include_contracted=False)

    assert list(result.keys()) == [local[0][0]]


@pytest.mark.parametrize(
    "method_name",
    [
        "iter_local_spells",
        "iter_contracted_spells",
        "iter_all_spells",
        "iter_spells_include_contracted",
        "iter_spells_local_only",
        "find_by_frame_and_binding",
        "find_single_by_frame_and_binding",
        "find_by_frame",
        "find_by_binding_name",
        "find_by_spell_name",
        "find_by_index",
        "find_by_target",
    ],
)
def test_methods_raise_after_cleanup(method_name: str) -> None:
    """
    Purpose:
        Ensure scanner methods enforce cleaned checks.
    Contract:
        Each method raises RuntimeError after cleanup.
    Args:
        method_name: Name of the method to exercise.
    Returns:
        None.
    Raises:
        AssertionError: If any method does not enforce cleaned checks.
    """
    scanner, _ = _make_scanner()
    scanner.cleanup()

    with pytest.raises(RuntimeError, match="cleaned"):
        _call_scanner_method(scanner, method_name)
