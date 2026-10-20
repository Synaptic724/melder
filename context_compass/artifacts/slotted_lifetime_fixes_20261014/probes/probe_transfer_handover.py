"""
The owner's handover scenario for the transfer docs (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, D3 docs, 0.2.8240).

Agent A builds a tool in its root, transfers the tool spell to agent B's root (default `move_creations=True`) and
throws out its trash (tears its root down). Agent B then registers the dependencies and builds its own version.
Records what B sees at each step. Public API only, as an agent would use it.

Run (any directory; melder importable):  python probe_transfer_handover.py
"""
from typing import Any, Callable, Dict, List, Tuple

import melder as md


class Closable:
    """`close` is the declared disposal method; `closes` counts Melder's calls."""

    def __init__(self) -> None:
        self.closes = 0

    def close(self) -> None:
        self.closes += 1


class Helper(Closable):
    """A `unique` dependency the tool uses (stays with A's book unless include_dependencies=True)."""


class Conn(Closable):
    """A disposal-bearing `many` dependency built for the tool (moves with it since 0.2.8238)."""


class Tool(Closable):
    """The `unique` tool A transfers to B."""

    def __init__(self, helper: Helper, conn: Conn) -> None:
        super().__init__()
        self.helper = helper
        self.conn = conn


def attempt(action: Callable[[], Any]) -> Tuple[bool, Any]:
    """Run one action; return (True, value) or (False, 'ExceptionType: first line')."""
    try:
        return True, action()
    except BaseException as error:  # the probe reports every outcome
        text = str(error).splitlines()[0][:150] if str(error) else ""
        return False, f"{type(error).__name__}: {text}"


def bind_all(book: Any, kinds: List[type]) -> Dict[type, str]:
    """Bind each class with its existence and `close`; return the spell ids."""
    existence = {Helper: "unique", Conn: "many", Tool: "unique"}
    return {kind: book.bind(spell=kind, existence=existence[kind], disposal_method_names=["close"]) for kind in kinds}


def handover(frame: str, include_dependencies: bool) -> Dict[str, Any]:
    """A builds and transfers the tool, tears down; B rebuilds it from its own registrations."""
    out: Dict[str, Any] = {}
    book_a = md.Spellbook(aetheric_frame=frame)
    ids_a = bind_all(book_a, [Helper, Conn, Tool])
    agent_a = book_a.conjure(dynamic=True, name=f"{frame}-a")
    book_b = md.Spellbook(aetheric_frame=frame)
    agent_b = book_b.conjure(dynamic=True, name=f"{frame}-b")
    tool = agent_a.meld("Tool")
    ok, report = attempt(lambda: agent_a.transfer_spell_ownership(
        spell=ids_a[Tool], target_conduit=agent_b, include_dependencies=include_dependencies))
    out["1_transfer"] = f"ok move_creations={report['options']['move_creations']}" if ok else report
    ok, value = attempt(lambda: agent_b.meld("Tool"))
    out["2_b_meld_before_a_teardown"] = "the moved tool" if ok and value is tool else (
        "another tool" if ok else value)
    ok, value = attempt(lambda: agent_a.meld("Tool"))
    out["3_a_meld_after_transfer"] = "still melds" if ok else value
    ok, value = attempt(agent_a.cleanup)
    out["4_a_teardown"] = "ok" if ok else value
    out["4_closes tool/helper/conn"] = f"{tool.closes}/{tool.helper.closes}/{tool.conn.closes}"
    ok, value = attempt(lambda: agent_b.meld("Tool"))
    out["5_b_meld_after_a_teardown"] = (
        f"the moved tool (its helper closed {tool.helper.closes}x)" if ok and value is tool else (
            "another tool" if ok else value))
    ok, value = attempt(lambda: agent_b.purge("Tool"))
    out["6_b_purges_the_moved_tool"] = f"ok -> {value}" if ok else value
    out["6_closes tool/helper/conn"] = f"{tool.closes}/{tool.helper.closes}/{tool.conn.closes}"
    ok, value = attempt(lambda: agent_b.meld("Tool"))
    out["7_b_meld_without_own_dependencies"] = (
        f"new tool (helper is A's old: {value.helper is tool.helper})" if ok else value)
    missing = [kind for kind in (Helper, Conn) if not attempt(lambda kind=kind: book_b.find_spell_by_id(
        ids_a[kind]))[1]]
    out["8_b_registers"] = ",".join(kind.__name__ for kind in missing) or "nothing (already owned)"
    ok, value = attempt(lambda: bind_all(book_b, missing))
    out["8_bind"] = "ok" if ok else value
    ok, mine = attempt(lambda: agent_b.meld("Tool"))
    out["9_b_meld_after_registering"] = (
        f"new tool: {mine is not tool}, fresh helper: {mine.helper is not tool.helper}, "
        f"fresh conn: {mine.conn is not tool.conn}" if ok else mine)
    ok, value = attempt(agent_b.cleanup)
    out["10_b_teardown"] = "ok" if ok else value
    if isinstance(mine, Tool):
        out["10_closes new tool/helper/conn"] = f"{mine.closes}/{mine.helper.closes}/{mine.conn.closes}"
    return out


def main() -> int:
    """Run the handover with and without include_dependencies and print one line per observation."""
    for name, frame, deps in (("h1", "handover-default", False), ("h2", "handover-with-deps", True)):
        ok, value = attempt(lambda: handover(frame, deps))
        if not ok:
            print(f"{name}.ERROR = {value}")
            continue
        for key, observed in value.items():
            print(f"{name}.{key} = {observed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
