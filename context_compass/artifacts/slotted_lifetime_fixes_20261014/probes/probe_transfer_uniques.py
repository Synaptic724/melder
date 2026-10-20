"""
Transfer and `unique` (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, D3 discussion with the owner).

Cases:
  e1 an existing-object spell (`unique`, a bound instance with `close`), default transfer
  e2 the same with move_creations=True
  u2 a constructed `unique` held by a per-conduit consumer of the source, default transfer:
     does the world end up with two instances of the `unique` spell?

Run (from a tree root that has src/ and tests/):  PYTHONPATH=src:. python probe_transfer_uniques.py
"""
import sys
from typing import Any, Callable, Dict, List, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Closable:
    """`close` is the declared disposal method and `closes` counts Melder's calls."""

    def __init__(self) -> None:
        self.closes = 0

    def close(self) -> None:
        self.closes += 1


class E1Tool(Closable):
    """Existing object bound as a `unique` spell (e1, e2)."""


class U2Tool(Closable):
    """Constructed `unique` spell (u2)."""


class U2User(Closable):
    """`unique_per_conduit` consumer of U2Tool on the source (u2)."""

    def __init__(self, tool: U2Tool) -> None:
        super().__init__()
        self.tool = tool


def reset_world() -> None:
    """Fresh Aether, as the component tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def dynamic_configuration(frame: str) -> SpellbookConfiguration:
    """A dynamic configuration for one frame with one phase worker."""
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def attempt(action: Callable[[], Any]) -> Tuple[bool, Any]:
    """Run one action; return (True, value) or (False, 'ExceptionType: message')."""
    try:
        return True, action()
    except BaseException as error:  # the probe reports every outcome
        return False, f"{type(error).__name__}: {str(error).splitlines()[0][:140] if str(error) else ''}"


def stored(conduit: Conduit, spell_id: str) -> Any:
    """What one conduit's own store holds under a spell id (None when absent or the store is gone)."""
    try:
        return conduit._creations._creations.get(spell_id)
    except AttributeError:
        return None


def case_existing(move: bool) -> Dict[str, Any]:
    """Transfer an existing-object spell with or without move_creations."""
    frame = f"tu-e{int(move)}"
    source_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    tool = E1Tool()
    tool_id = source_book.bind(spell=tool, existence=Existence.unique, permissions="create",
                               disposal_method_names=["close"])
    source = source_book.conjure(dynamic=True, name=f"tu-e{int(move)}-source")
    target = Spellbook(aetheric_frame=frame).conjure(dynamic=True, name=f"tu-e{int(move)}-target")
    out: Dict[str, Any] = {}
    try:
        out["setup_source_meld_is_tool"] = source.meld(spell_id=tool_id) is tool
        out["setup_in_source_store"] = stored(source, tool_id) is tool
        ok, value = attempt(lambda: source.transfer_spell_ownership(
            spell=tool_id, target_conduit=target, move_creations=move))
        out["transfer"] = "ok" if ok else value
        out["after_in_source_store"] = stored(source, tool_id) is tool
        out["after_in_target_store"] = stored(target, tool_id) is tool
        ok, value = attempt(lambda: target.meld(spell_id=tool_id))
        out["after_target_meld"] = "the bound object" if ok and value is tool else (
            "another object" if ok else value)
        source.cleanup()
        out["after_source_teardown_closes"] = tool.closes
        target.cleanup()
        out["after_target_teardown_closes"] = tool.closes
    finally:
        attempt(source.cleanup)
        attempt(target.cleanup)
    return out


def case_u2() -> Dict[str, Any]:
    """A constructed unique held by a source consumer, default transfer."""
    frame = "tu-u2"
    source_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    tool_id = source_book.bind(spell=U2Tool, existence=Existence.unique, permissions="create",
                               disposal_method_names=["close"])
    user_id = source_book.bind(spell=U2User, existence=Existence.unique_per_conduit, permissions="create",
                               disposal_method_names=["close"])
    source = source_book.conjure(dynamic=True, name="tu-u2-source")
    target = Spellbook(aetheric_frame=frame).conjure(dynamic=True, name="tu-u2-target")
    out: Dict[str, Any] = {}
    try:
        user = source.meld(spell_id=user_id)
        old_tool = user.tool
        out["setup_tool_is_shared"] = source.meld(spell_id=tool_id) is old_tool
        ok, value = attempt(lambda: source.transfer_spell_ownership(spell=tool_id, target_conduit=target))
        out["transfer"] = "ok" if ok else value
        ok, new_tool = attempt(lambda: target.meld(spell_id=tool_id))
        out["after_target_meld"] = "same tool" if ok and new_tool is old_tool else (
            "a second tool" if ok else new_tool)
        ok, value = attempt(lambda: source.meld(spell_id=user_id))
        out["after_source_user_still_holds_old_tool"] = (ok and value is user and value.tool is old_tool) if ok else value
        source.cleanup()
        target.cleanup()
        out["final_closes_old_tool"] = old_tool.closes
        out["final_closes_new_tool"] = new_tool.closes if isinstance(new_tool, Closable) else None
        out["final_closes_user"] = user.closes
    finally:
        attempt(source.cleanup)
        attempt(target.cleanup)
    return out


CASES: List[Tuple[str, Callable[[], Dict[str, Any]]]] = [
    ("e1", lambda: case_existing(False)),
    ("e2", lambda: case_existing(True)),
    ("u2", case_u2),
]


def main() -> int:
    """Run the selected cases (all when none is named) and print one line per observation."""
    wanted = set(sys.argv[1:])
    for name, case in CASES:
        if wanted and name not in wanted:
            continue
        reset_world()
        ok, value = attempt(case)
        if not ok:
            print(f"{name}.ERROR = {value}")
            continue
        for key, observed in value.items():
            print(f"{name}.{key} = {observed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
