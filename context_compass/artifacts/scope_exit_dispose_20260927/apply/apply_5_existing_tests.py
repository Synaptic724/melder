"""Scope-exit dispose lane, part 5: existing tests that pinned the old `with conduit:` and teardown behaviour.

melder_0, 2026-09-27. Edits exact line blocks (compared without endings), keeps each file's line endings and a
UTF-8 BOM when present, asserts every block matches exactly once and that the result still parses.
"""

import ast
import os
import sys

ROOT = sys.argv[1]
BOM = "﻿"


def replace_blocks(rel_path: str, pairs: list) -> None:
    """Apply (old, new) line-block replacements to one test file."""
    path = os.path.join(ROOT, rel_path)
    with open(path, "rb") as handle:
        text = handle.read().decode("utf-8")
    bom = text.startswith(BOM)
    if bom:
        text = text[1:]
    lines = text.splitlines(keepends=True)
    for old, new in pairs:
        old_lines = old.strip("\n").split("\n")
        hits = [i for i in range(len(lines) - len(old_lines) + 1)
                if all(lines[i + k].rstrip("\r\n") == old_lines[k] for k in range(len(old_lines)))]
        assert len(hits) == 1, (rel_path, old_lines[0], len(hits))
        i = hits[0]
        eol = "\r\n" if lines[i].endswith("\r\n") else "\n"
        lines[i:i + len(old_lines)] = [line + eol for line in new.strip("\n").split("\n")]
        print(f"  {os.path.basename(rel_path)}: {old_lines[0].strip()[:70]}")
    out = "".join(lines)
    ast.parse(out)
    with open(path, "wb") as handle:
        handle.write(((BOM if bom else "") + out).encode("utf-8"))


replace_blocks("tests/unit/melder/aether/conduit/test_conduit_lifecycle.py", [
("""
from unittest.mock import MagicMock
""", """
from typing import List
from unittest.mock import MagicMock
"""),
("""
def test_context_manager_acquires_and_releases_lock(conduit_lesser: Conduit) -> None:
    \"\"\"
    Verify Conduit context manager acquires and releases the lock.

    Contract:
        - __enter__ acquires the lock.
        - __exit__ releases the lock.
        - The context returns the same Conduit instance.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If acquire/release behavior is incorrect.
    \"\"\"
    lock = _LockProbe()
    conduit_lesser._lock = lock
    with conduit_lesser as ctx:
        assert ctx is conduit_lesser
    assert lock.acquire_calls == 1
    assert lock.release_calls == 1
""", """
def test_context_manager_returns_self_and_cleans_up_at_exit(
    conduit_lesser: Conduit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    \"\"\"
    Verify `with conduit:` is a dispose scope (0.2.8201; it used to hold the lock).

    Contract:
        - __enter__ returns the same Conduit instance and takes no lock.
        - __exit__ calls cleanup() once per block, also when the block raises,
          and never suppresses the block's exception.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        monkeypatch (pytest.MonkeyPatch): Replaces cleanup with a recorder.

    Raises:
        AssertionError: If enter/exit behavior is incorrect.
    \"\"\"
    lock = _LockProbe()
    conduit_lesser._lock = lock
    cleaned: List[Conduit] = []

    def record_cleanup(self: Conduit) -> None:
        \"\"\"Record the cleanup call instead of tearing the fixture down.\"\"\"
        cleaned.append(self)

    monkeypatch.setattr(Conduit, "cleanup", record_cleanup)
    with conduit_lesser as ctx:
        assert ctx is conduit_lesser
        assert cleaned == []
    assert cleaned == [conduit_lesser]
    with pytest.raises(ValueError, match="block failed"):
        with conduit_lesser:
            raise ValueError("block failed")
    assert cleaned == [conduit_lesser, conduit_lesser]
    assert lock.acquire_calls == 0
    assert lock.release_calls == 0
"""),
("""
    Verify soft cleanup is idempotent for a lesser conduit.

    Contract:
        - Multiple cleanup calls do not raise.
        - cleaned flag remains unset because the lesser is prepared for pooling.
""", """
    Verify soft cleanup is idempotent for a lesser conduit.

    Contract:
        - Multiple cleanup calls do not raise; the second finds the lesser
          pooled and does nothing.
        - cleaned flag remains unset because the lesser is prepared for pooling.
"""),
("""
    conduit_lesser._conduit_ward = MagicMock()
    conduit_lesser._meld = MagicMock()
    conduit_lesser._creations = MagicMock()
    conduit_lesser.cleanup()
    conduit_lesser.cleanup()
""", """
    conduit_lesser._conduit_ward = MagicMock()
    # Production contract: a lesser without children has an empty child map.
    conduit_lesser._conduit_ward._lesser_conduits = {}
    conduit_lesser._meld = MagicMock()
    conduit_lesser._creations = MagicMock()
    conduit_lesser.cleanup()
    conduit_lesser.cleanup()
"""),
])

replace_blocks("tests/integration/melder/conduit/test_conduit_integration_public_api.py", [
("""
def test_conduit_public_api_context_manager_allows_meld() -> None:
    \"\"\"
    Purpose:
        Validate the Conduit context manager does not block meld.
    Contract:
        - Meld works inside the context manager.
        - Meld works after the context exits.
    Returns:
        None.
    Raises:
        AssertionError: If meld fails inside or outside the context.
    \"\"\"
""", """
def test_conduit_public_api_context_manager_disposes_the_root_at_exit() -> None:
    \"\"\"
    Purpose:
        Validate `with conduit:` as a dispose scope on a root conduit (0.2.8201).
    Contract:
        - Meld works inside the block.
        - The block exit tears the root down; it is cleaned afterwards.
    Returns:
        None.
    Raises:
        AssertionError: If meld fails inside the block or the root survives it.
    \"\"\"
"""),
("""
    conduit = spellbook.conjure(name="root")
    try:
        with conduit as ctx:
            instance = ctx.meld(spell_id=spell_id)
            assert isinstance(instance, BasicService)
        assert isinstance(conduit.meld(spell_id=spell_id), BasicService)
    finally:
        conduit.cleanup()
""", """
    conduit = spellbook.conjure(name="root")
    try:
        with conduit as ctx:
            instance = ctx.meld(spell_id=spell_id)
            assert isinstance(instance, BasicService)
        assert conduit.cleaned is True
    finally:
        conduit.cleanup()
"""),
])

replace_blocks("tests/integration/melder/conduit/test_conduit_integration_disposal_failures.py", [
("""
Contract under test:
    Every declared disposal method runs, in the book's declared order, even
    after an earlier one raised; conduit cleanup logs the failure and finishes.
\"\"\"
""", """
Contract under test:
    Every declared disposal method runs, in the book's declared order, even
    after an earlier one raised; conduit cleanup finishes its teardown and then
    raises the failure as an ExceptionGroup (since 0.2.8201; it used to only log
    it).
\"\"\"
"""),
("""
def test_conduit_cleanup_runs_every_disposal_method_after_one_fails() -> None:
    \"\"\"Conduit teardown releases the connection even though its `close` raised.\"\"\"
""", """
def _leaves(error: BaseException) -> List[BaseException]:
    \"\"\"Flatten nested exception groups to their leaf exceptions, in group order.

    Args:
        error: The raised exception or group.

    Returns:
        List[BaseException]: Every leaf exception.
    \"\"\"
    if isinstance(error, BaseExceptionGroup):
        leaves: List[BaseException] = []
        for inner in error.exceptions:
            leaves.extend(_leaves(inner))
        return leaves
    return [error]


def test_conduit_cleanup_runs_every_disposal_method_after_one_fails() -> None:
    \"\"\"Conduit teardown releases the connection even though its `close` raised, then reports it.\"\"\"
"""),
("""
    conduit = spellbook.conjure(dynamic=True, name="root")
    connection = conduit.meld(spell_id=connection_id)

    conduit.cleanup()

    assert connection.calls == ["close", "release"]
""", """
    conduit = spellbook.conjure(dynamic=True, name="root")
    connection = conduit.meld(spell_id=connection_id)

    with pytest.raises(ExceptionGroup) as raised:
        conduit.cleanup()

    assert connection.calls == ["close", "release"]
    assert conduit.cleaned is True
    assert [type(leaf.__cause__) for leaf in _leaves(raised.value)] == [ConnectionError]
"""),
])

replace_blocks("tests/component/melder/aether/conduit/test_named_lesser_directory_lifecycle.py", [
("""
def test_disposal_failure_leaves_name_until_pool_reset_completes(root: Conduit) -> None:
    \"\"\"Failed store disposal does not falsely advertise a completed scope retirement.\"\"\"
    with root.transaction("bind"):
        spell_id = root.bind(spell=FailingDisposal, existence=Existence.many, disposal_method_names=["cleanup"])
    child = root.create_lesser_conduit(name="disposal")
    instance = child.meld(spell_id=spell_id)
    with pytest.raises(ExceptionGroup):
        child.cleanup()
    assert instance.calls == 1
    assert root.get_conduit_cloud().get_conduit("disposal") is child
    assert child._conduit_state is ConduitState.lesser
    # Existing Creations semantics detach failed-disposal entries before raising.
    child.cleanup()
    assert instance.calls == 1
    assert child.name is None
    assert not root.get_conduit_cloud().has_conduit_name("disposal")
""", """
def test_disposal_failure_still_retires_the_name_and_pools_the_scope(root: Conduit) -> None:
    \"\"\"A failed store disposal finishes the named return - name retired, shell pooled - then raises (0.2.8201).\"\"\"
    with root.transaction("bind"):
        spell_id = root.bind(spell=FailingDisposal, existence=Existence.many, disposal_method_names=["cleanup"])
    child = root.create_lesser_conduit(name="disposal")
    instance = child.meld(spell_id=spell_id)
    with pytest.raises(ExceptionGroup):
        child.cleanup()
    assert instance.calls == 1
    assert child.name is None
    assert not root.get_conduit_cloud().has_conduit_name("disposal")
    assert child._conduit_state is ConduitState.pooled_lesser
    # Creations detached the failed entry before its method ran, and a second
    # cleanup of the pooled shell does nothing.
    child.cleanup()
    assert instance.calls == 1
    assert root.create_lesser_conduit() is child
"""),
])
print("part 5 done")
