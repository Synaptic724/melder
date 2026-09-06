"""Observe the original cluster test without changing runtime methods or fields.

Debugger trace callbacks control scheduling only. The report captures the
owning Spellbook at the original builder exception, then releases the peer so
pytest runs the original assertions and final cleanup. This is not a fix or a
measurement of how frequently production encounters the schedule.
"""

import json
import sys
import threading
from pathlib import Path
from types import FrameType, TracebackType
from typing import TYPE_CHECKING, Callable, Optional, cast

import pytest

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.spellbook.spell import Spell


class OwnerLifecycleProbe:
    """Own observer events and two bounded debugger scheduling pauses."""

    def __init__(self) -> None:
        """Create diagnostic-only coordination and an ordered value-only log."""
        self._lock = threading.Lock()
        self._owner_paused = threading.Event()
        self._peer_paused = threading.Event()
        self._release_peer = threading.Event()
        self._actors: dict[str, Conduit] = {}
        self._events: list[dict[str, object]] = []
        self._observed_exception = False
        self._control_failed = False

    def cleanup(self) -> None:
        """Release diagnostic pauses and borrowed references after pytest returns."""
        self._owner_paused.set()
        self._peer_paused.set()
        self._release_peer.set()
        self._actors.clear()

    def record(self, event: str, **values: object) -> None:
        """Append a numbered observation without changing runtime state."""
        with self._lock:
            self._events.append({
                "sequence": len(self._events),
                "event": event,
                "thread": threading.get_ident(),
                **values,
            })

    def book_states(self) -> dict[str, dict[str, object]]:
        """Read each actor's real owner; preserve deleted-slot evidence at teardown."""
        states = {}
        for name, conduit in self._actors.items():
            try:
                book = conduit._spellbook
                states[name] = {
                    "conduit_cleaned": conduit._cleaned,
                    "book_cleaned": book._cleaned,
                    "book_identity": id(book),
                }
            except AttributeError:
                states[name] = {"owner_reference_already_deleted": True}
        return states

    @staticmethod
    def stack(frame: Optional[FrameType]) -> list[str]:
        """Return a bounded caller stack with repository-relative paths."""
        result = []
        for _ in range(7):
            if frame is None:
                break
            filename = frame.f_code.co_filename.replace("\\", "/")
            if "/src/" in filename:
                filename = "src/" + filename.split("/src/", 1)[1]
            elif "/tests/" in filename:
                filename = "tests/" + filename.split("/tests/", 1)[1]
            result.append(f"{filename}:{frame.f_lineno} {frame.f_code.co_qualname}")
            frame = frame.f_back
        return result

    def spell_state(self, spell: Spell) -> dict[str, object]:
        """Capture the owning-book distinction before the original error propagates."""
        book = spell._spellbook
        return {
            "spell_id": spell.spell_id,
            "spell_cleaned": spell._cleaned,
            "spellbook_cleanup_requested": spell._spellbook_cleanup,
            "owning_book_identity": id(book),
            "owning_book_cleaned": book._cleaned,
            "owning_book_still_registers_spell": book._spells_by_id.get(spell.spell_id) is spell,
            "context_missing": spell._creation_context is None,
            "codegen_missing": spell._compiler_artifact._spell_codegen_creation is None,
            "artifact_cleaned": spell._compiler_artifact._cleaned,
            "switch_state": spell._creation_context_switch.state,
        }

    def wait(self, event: threading.Event, label: str) -> None:
        """Bound a pause; log control failure instead of injecting a runtime error."""
        if not event.wait(15.0):
            self._control_failed = True
            self.record("diagnostic_control_timeout", boundary=label)
            self._owner_paused.set()
            self._peer_paused.set()
            self._release_peer.set()

    def trace(self, frame: FrameType, event: str, arg: object) -> Optional[Callable]:
        """Observe the original workers, revalidation, builder and cleanup calls."""
        filename = frame.f_code.co_filename.replace("\\", "/")
        name = frame.f_code.co_name
        if event == "call" and name == "_run_concurrent_melds":
            self._actors = {key: conduit for key, conduit, _, _ in frame.f_locals["tasks"]}
            self.record("workers_about_to_start", books=self.book_states())
            return self.trace
        if not self._actors:
            return None
        if event == "call" and name == "cleanup":
            if filename.endswith(("/spellbook.py", "/spell.py", "/conduit.py", "/creation_context.py")):
                target = frame.f_locals["self"]
                self.record(
                    "cleanup_entered", target_type=type(target).__name__,
                    target_identity=id(target), already_cleaned=target._cleaned,
                    books=self.book_states(), caller_stack=self.stack(frame),
                )
        if filename.endswith("/conduit_meld.py") and name == "meld":
            return self.owner_read(frame, event)
        if filename.endswith("/compiler_phase_5.py") and name == "run_local":
            return self.peer_phase5(frame, event)
        if filename.endswith("/meld.py") and name == "_ensure_resolution_resolvable":
            if event == "line" and frame.f_lineno == 867:
                state = frame.f_locals["resolution_state"]
                verdict = frame.f_locals["resolution_validity"]
                reason = None if state is None else state._last_change_reason
                self.record(
                    "resolution_branch", conduit_id=frame.f_locals["conduit_id"],
                    validity=None if verdict is None else verdict.name,
                    change_reason=None if reason is None else reason.name,
                    spell=self.spell_state(frame.f_locals["spell"]),
                )
            return self.trace
        if filename.endswith("/creation_context_builder.py") and name == "build":
            if event == "exception":
                _, error, _ = cast(tuple[type[BaseException], BaseException, TracebackType], arg)
                if "Cannot build CreationContext before spell_codegen_creation exists" in str(error):
                    self._observed_exception = True
                    self.record(
                        "original_builder_exception", error=str(error),
                        spell=self.spell_state(frame.f_locals["spell"]),
                        books=self.book_states(), caller_stack=self.stack(frame),
                    )
                    self._release_peer.set()
            return self.trace
        return None

    def owner_read(self, frame: FrameType, event: str) -> Callable:
        """Pause the owner just before its existing context-read line."""
        if (
                event == "line" and frame.f_lineno == 371
                and not self._owner_paused.is_set()
                and frame.f_locals["self"]._conduit_id == self._actors["cluster-a-owner"].id
        ):
            self.record("owner_before_context_read", spell=self.spell_state(frame.f_locals["target_spell"]))
            self._owner_paused.set()
            self.wait(self._peer_paused, "owner waits for peer phase 5")
        return self.trace

    def peer_phase5(self, frame: FrameType, event: str) -> Callable:
        """Hold the peer after normal phase 5 until the owner failure is observed."""
        if frame.f_locals["conduit_id"] != self._actors["cluster-a-peer"].id:
            return self.trace
        if event == "call":
            self.wait(self._owner_paused, "peer waits for owner read boundary")
        elif event == "return":
            self.record("peer_after_phase5", spell=self.spell_state(frame.f_locals["spell"]))
            self._peer_paused.set()
            self.wait(self._release_peer, "peer waits for original exception observation")
        return self.trace

    def report(self, result: int) -> dict[str, object]:
        """Return observations with explicit control success and pytest exit status."""
        return {
            "pytest_exit_code": result,
            "original_exception_observed": self._observed_exception,
            "diagnostic_control_failed": self._control_failed,
            "python": sys.version,
            "gil_enabled": sys._is_gil_enabled(),
            "events": self._events,
        }


def main() -> int:
    """Run exactly the original test and persist generated lifecycle observations."""
    probe = OwnerLifecycleProbe()
    threading.settrace(probe.trace)
    sys.settrace(probe.trace)
    try:
        result = int(pytest.main([
            "tests/integration/melder/conduit/test_conduit_integration_concurrency.py"
            "::test_conduit_cluster_concurrent_meld_two_clusters_isolated",
            "-q", "-p", "no:cacheprovider",
        ]))
    finally:
        sys.settrace(None)
        threading.settrace(None)
    output = Path(__file__).with_name("owner-lifecycle-observation.json")
    output.write_text(json.dumps(probe.report(result), indent=2), encoding="utf-8")
    probe.cleanup()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
