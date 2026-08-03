"""tests/component/melder/aether/conduit/test_conduit_component_policy_reader.py

Validation: Not run.

Component tests for `Conduit.policy`, the read that closes a write-only door.

Why this file exists
--------------------
`set_new_policy` was public and had no counterpart read, so a caller could
change how linking behaves and then had no way to ask what the ward was
actually enforcing. That gap matters more here than it would elsewhere because
`set_new_policy` CAN REFUSE - on a lesser conduit, on an automatic frame, and
when contracts already exist - so the value last passed in was never evidence
of the value in force.

The tests are grouped by the guarantee they defend:
  * TRUTH      - the read reports the ward, not a remembered argument.
  * ASYMMETRY  - reading is ungated where writing is gated.
  * ROUND-TRIP - what the read returns is what the write accepts.
  * LIFECYCLE  - a cleaned conduit refuses.
"""

from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def reset_singletons_for_policy_reader() -> None:
    """Reset Nexus + Aether around each test so frames never leak."""

    def _reset() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


class _Linkable:
    def __init__(self) -> None:
        pass


def _conduit(frame_name: str, *, dynamic: bool) -> Conduit:
    """Conjure one root conduit on its own frame."""
    book = Spellbook(frame_name)
    # binding_name keeps each frame's spell_id distinct. The frame is NOT in the
    # bind-time fingerprint, so under process-wide uniqueness two frames binding
    # the same class with the same parameters mint the SAME id and collide.
    book.bind(spell=_Linkable, existence="unique", binding_name=frame_name)
    if dynamic:
        return book.conjure(dynamic=True, name=f"{frame_name}-root")
    return book.conjure(name=f"{frame_name}-root")


# --------------------------------------------------------------------------
# TRUTH
# --------------------------------------------------------------------------

def test_a_fresh_conduit_reports_the_default_policy() -> None:
    """The read has an answer before anything has been written."""
    assert _conduit("policy-default", dynamic=True).policy is Policies.default


def test_the_read_reflects_a_successful_write() -> None:
    """After an accepted swap the ward reports the new policy."""
    conduit = _conduit("policy-written", dynamic=True)
    conduit.set_new_policy("block_all")
    assert conduit.policy is Policies.block_all


def test_the_read_survives_a_refused_write() -> None:
    """
    The point of having a reader at all: a refused `set_new_policy` raises and
    the ward keeps the policy it had. Without this read a caller could not tell
    the difference between "my swap took" and "my swap was rejected and the old
    behaviour is still live".
    """
    conduit = _conduit("policy-refused", dynamic=True)
    conduit.set_new_policy("block_all")
    with pytest.raises(ValueError):
        conduit.set_new_policy("not_a_real_policy")
    assert conduit.policy is Policies.block_all


def test_the_read_is_not_a_memo_of_the_last_argument() -> None:
    """
    A string goes in, a `Policies` MEMBER comes out. The reader resolves
    through the ward rather than echoing what the caller passed.
    """
    conduit = _conduit("policy-resolved", dynamic=True)
    conduit.set_new_policy("block_all")
    observed = conduit.policy
    assert isinstance(observed, Policies)
    assert not isinstance(observed, str)
    assert observed.name == "block_all"


# --------------------------------------------------------------------------
# ASYMMETRY
# --------------------------------------------------------------------------

def test_an_automatic_conduit_can_be_read_but_not_written() -> None:
    """
    Writing is dynamic-only; reading is not. An automatic conduit still
    enforces a policy, so refusing to disclose it would be the library hiding
    live behaviour behind a mode gate.
    """
    conduit = _conduit("policy-automatic", dynamic=False)
    assert conduit.policy is Policies.default
    with pytest.raises(RuntimeError):
        conduit.set_new_policy("block_all")
    assert conduit.policy is Policies.default


def test_a_lesser_conduit_can_be_read_but_not_written() -> None:
    """
    Same asymmetry one level down the lineage. The ward refuses the write on a
    lesser conduit; the read still answers.
    """
    root = _conduit("policy-lesser", dynamic=True)
    lesser = root.create_lesser_conduit()
    assert isinstance(lesser.policy, Policies)
    with pytest.raises(RuntimeError):
        lesser.set_new_policy("block_all")


# --------------------------------------------------------------------------
# ROUND-TRIP
# --------------------------------------------------------------------------

def test_the_member_the_reader_returns_is_accepted_by_the_writer() -> None:
    """
    `set_new_policy` is annotated `Union[str, Policies]` because the ward
    resolves both. That annotation is what makes read-then-write a legal
    round-trip instead of a type error, so the round-trip is asserted here.
    """
    source = _conduit("policy-round-a", dynamic=True)
    source.set_new_policy("block_all")
    target = _conduit("policy-round-b", dynamic=True)
    target.set_new_policy(source.policy)
    assert target.policy is source.policy


def test_a_policy_can_be_captured_and_restored() -> None:
    """Read, change, restore - the read is durable enough to undo with."""
    conduit = _conduit("policy-restore", dynamic=True)
    original = conduit.policy
    conduit.set_new_policy("block_all")
    assert conduit.policy is not original
    conduit.set_new_policy(original)
    assert conduit.policy is original


# --------------------------------------------------------------------------
# LIFECYCLE
# --------------------------------------------------------------------------

def test_a_cleaned_conduit_refuses_the_read() -> None:
    """
    `check_cleaned()` fires rather than returning a stale member. Melder does
    not hand back the last known value of a torn-down object.
    """
    conduit = _conduit("policy-cleaned", dynamic=True)
    conduit.cleanup()
    with pytest.raises(RuntimeError):
        _ = conduit.policy
