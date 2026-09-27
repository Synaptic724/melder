"""Observe current override admission and lifecycle behavior without production changes.

Run from the repository root with root and src on PYTHONPATH. Each probe owns an
isolated world, disables disk caching and records outcomes rather than prescribing
the proposed structural fix. Exceptions are retained as diagnostic data so one
known blocked shape does not hide the remaining cases. No timings are collected.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Optional

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration
from tests.experimentation.test_melder_creation_overrides_performance import _source_fingerprints


class ProbeWorld:
    """Own one Book and optional Conduit, cleaned explicitly after each observation."""

    def __init__(self, dynamic: bool = False) -> None:
        """Reset the world and stage normal configuration with one compiler worker and no disk cache."""
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether
        configuration = SpellbookConfiguration().with_defaults()
        configuration.with_phase_scheduler_workers(1)
        posture = configure_frame_posture_for_spellbook_configuration(configuration, dynamic=dynamic)
        posture.with_system_caching_enabled(False)
        self.book = Spellbook(configuration=configuration)
        self.conduit: Optional[Conduit] = None
        self.dynamic = dynamic

    def cleanup(self) -> None:
        """Dispose the Conduit before its Book and reset process-owned test state on every path."""
        try:
            if self.conduit is not None:
                self.conduit.permanent_cleanup()
        finally:
            self.book.cleanup()
            Aether._reset_singleton_for_tests()

    def conjure(self) -> Conduit:
        """Conjure the staged Book and retain the resulting owner for guaranteed cleanup."""
        self.conduit = self.book.conjure(dynamic=self.dynamic)
        return self.conduit


def observe(call: Callable[[], object]) -> dict[str, object]:
    """Record a successful value summary or an explicit exception/cause without changing runtime policy."""
    try:
        result = call()
    except Exception as error:
        return {
            "status": "error", "type": type(error).__name__, "message": str(error),
            "cause_type": type(error.__cause__).__name__ if error.__cause__ is not None else None,
        }
    return {"status": "ok", "result": result}


def space_requirement(root_scoped: bool = False) -> dict[str, object]:
    """Compare a replaced Space dependency through Conduit and explicit SpellSpace doors."""
    events: list[str] = []

    class Resource:
        """A request-owned resource with observable construction and disposal."""

        def __init__(self) -> None:
            """Record factory execution without external resources."""
            events.append("resource:create")

        def dispose(self) -> None:
            """Record the owning store's explicit disposal."""
            events.append("resource:dispose")

    class Consumer:
        """Keep the effective resource reference for identity checks."""

        def __init__(self, resource: Resource) -> None:
            """Retain the selected argument and record consumer construction."""
            self.resource = resource
            events.append("consumer:create")

    world = ProbeWorld()
    try:
        world.book.bind(spell=Resource, existence="unique_per_spell_space", disposal_method_names=["dispose"])
        root_id = world.book.bind(
            spell=Consumer, existence="unique_per_spell_space" if root_scoped else "many",
        )
        root = world.conjure()
        supplied = object()
        answer: dict[str, object] = {
            "full_graph_requires_space": world.book._spells_by_id[root_id].requires_spellspace_request,
            "root_itself_scoped": root_scoped,
            "normal_conduit": observe(lambda: root.meld(spell_id=root_id) is not None),
            "replaced_conduit": observe(lambda: root.meld(spell_id=root_id, override={"resource": supplied}).resource is supplied),
            "events_after_conduit": list(events),
        }
        space = root.create_spellspace()
        try:
            answer["replaced_space"] = observe(lambda: space.meld(spell_id=root_id, override={"resource": supplied}).resource is supplied)
        finally:
            space.cleanup()
        answer["events_after_space_cleanup"] = list(events)
        return answer
    finally:
        world.cleanup()


def missing_contract(nested: bool, override_first: bool) -> dict[str, object]:
    """Observe whether whole replacement can avoid an unresolved contracted provider."""

    class Service:
        """A declaration that deliberately has no linked provider in this world."""

    class Consumer:
        """Declare a late-bound service contract."""

        def __init__(self, service: Service = SpellContract(spell=Service)) -> None:
            """Retain the service delivered to the contract socket."""
            self.service = service

    class Outer:
        """Place the unresolved contract below a replaceable child branch."""

        def __init__(self, child: Consumer) -> None:
            """Retain the child selected by the caller."""
            self.child = child

    world = ProbeWorld(dynamic=True)
    try:
        root_id = world.book.bind(spell=Consumer, existence="many")
        if nested:
            root_id = world.book.bind(spell=Outer, existence="many")
        conjure = observe(lambda: world.conjure() is not None)
        if conjure["status"] != "ok":
            return {"conjure": conjure}
        root = world.conduit
        supplied = object()
        selector = "child" if nested else "service"
        def attempt(replaced: bool) -> dict[str, object]:
            """Inspect the actual delivered value rather than accepting a successful root call alone."""
            instance = root.meld(
                spell_id=root_id, override={selector: supplied} if replaced else None,
            )
            if nested and replaced:
                return {"supplied_identity": instance.child is supplied}
            consumer = instance.child if nested else instance
            return {
                "service_type": type(consumer.service).__name__,
                "descriptor_leaked": isinstance(consumer.service, SpellContract),
                "supplied_identity": consumer.service is supplied,
            }

        answer: dict[str, object] = {"conjure": conjure, "override_first": override_first}
        order = (True, False) if override_first else (False, True)
        for replaced in order:
            answer["replaced" if replaced else "normal"] = observe(lambda: attempt(replaced))
        return answer
    finally:
        world.cleanup()


def nested_selectors(root_hooks: bool = False) -> dict[str, object]:
    """Observe valid and invalid nested rules beneath an externally replaced ancestor."""
    events: list[str] = []

    class Child:
        """Expose a plain constructor value below the replaceable edge."""

        def __init__(self, value: int = 1) -> None:
            """Keep the value and record which discarded child was constructed."""
            self.value = value
            events.append(f"child:{value}")

    class Root:
        """Retain the effective child without mutating it."""

        def __init__(self, child: Child) -> None:
            """Store the received reference and record creation."""
            self.child = child
            events.append("root")

    world = ProbeWorld()
    try:
        def child_pre() -> None:
            """Record a direct child request's pre-hook invocation."""
            events.append("child:pre")

        def child_activation(instance: object) -> None:
            """Record the child's creation activation callback."""
            events.append("child:activation")

        def child_post() -> None:
            """Record a completed direct child request's post-hook invocation."""
            events.append("child:post")

        child_id = world.book.bind(
            spell=Child, existence="many", pre_hooks=[child_pre],
            activation_hooks=[child_activation], post_hooks=[child_post],
        )
        def root_pre() -> None:
            """Record when root entry hooks occur relative to selector rejection."""
            events.append("root:pre")

        def root_activation(instance: Root) -> None:
            """Record successful root activation after constructor completion."""
            events.append("root:activation")

        def root_post() -> None:
            """Record the root's successful post-hook boundary."""
            events.append("root:post")

        root_id = world.book.bind(
            spell=Root, existence="many", pre_hooks=[root_pre] if root_hooks else None,
            activation_hooks=[root_activation] if root_hooks else None,
            post_hooks=[root_post] if root_hooks else None,
        )
        conduit = world.conjure()
        supplied = Child(9)
        events.clear()
        conduit.meld(spell_id=child_id, override={"value": 4})
        direct_events = list(events)
        events.clear()
        conduit.meld(spell_id=root_id)
        nested_events = list(events)
        events.clear()
        valid = observe(lambda: conduit.meld(spell_id=root_id, override={"child": supplied, "child>value": 7}).child is supplied)
        valid_events = list(events)
        events.clear()
        invalid = observe(lambda: conduit.meld(spell_id=root_id, override={"child": supplied, "child>missing": 7}) is not None)
        return {
            "valid_nested": valid, "valid_events": valid_events,
            "invalid_nested": invalid, "invalid_events": list(events), "supplied_value": supplied.value,
            "direct_child_events": direct_events, "default_nested_events": nested_events,
        }
    finally:
        world.cleanup()


def shared_reuse() -> dict[str, object]:
    """Observe transient descendants below a reusable provider on subsequent root calls."""
    events: list[str] = []

    class Leaf:
        """A transient descendant with observable disposal."""

        def __init__(self) -> None:
            """Record one new transient leaf."""
            events.append("leaf:create")

        def dispose(self) -> None:
            """Record explicit store-owned disposal."""
            events.append("leaf:dispose")

    class Middle:
        """A reusable provider that retains its first generated leaf."""

        def __init__(self, leaf: Leaf) -> None:
            """Store the injected leaf and record provider construction."""
            self.leaf = leaf
            events.append("middle:create")

    class Root:
        """A transient consumer with an ordinary root-level override argument."""

        def __init__(self, middle: Middle, marker: int = 0) -> None:
            """Retain the provider and caller marker."""
            self.middle = middle
            self.marker = marker
            events.append(f"root:{marker}")

    world = ProbeWorld()
    try:
        world.book.bind(spell=Leaf, existence="many", disposal_method_names=["dispose"])
        world.book.bind(spell=Middle, existence="unique_per_conduit")
        root_id = world.book.bind(spell=Root, existence="many")
        root = world.conjure()
        first = root.meld(spell_id=root_id)
        first_events = list(events)
        events.clear()
        second = root.meld(spell_id=root_id)
        second_events = list(events)
        events.clear()
        third = root.meld(spell_id=root_id, override={"marker": 3})
        third_events = list(events)
        events.clear()
        supplied = object()
        replaced = root.meld(spell_id=root_id, override={"middle": supplied})
        replaced_events = list(events)
        events.clear()
        root.permanent_cleanup()
        world.conduit = None
        return {
            "first": first_events, "second_normal": second_events, "third_root_parameter": third_events,
            "shared_identity": first.middle is second.middle is third.middle,
            "replaced": replaced_events, "supplied_identity": replaced.middle is supplied,
            "cleanup": list(events),
        }
    finally:
        world.cleanup()


def main() -> None:
    """Persist bounded current-behavior observations and source provenance without timing."""
    directory = Path(__file__).resolve().parent
    repo = directory.parents[2]
    before = _source_fingerprints(repo)
    observations = {
        "space_requirement": observe(space_requirement),
        "root_space_requirement": observe(lambda: space_requirement(True)),
        "direct_missing_contract_normal_first": observe(lambda: missing_contract(False, False)),
        "direct_missing_contract_override_first": observe(lambda: missing_contract(False, True)),
        "nested_missing_contract_normal_first": observe(lambda: missing_contract(True, False)),
        "nested_missing_contract_override_first": observe(lambda: missing_contract(True, True)),
        "nested_selectors": observe(nested_selectors),
        "nested_selectors_root_hooks": observe(lambda: nested_selectors(True)),
        "shared_reuse": observe(shared_reuse),
    }
    after = _source_fingerprints(repo)
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    (directory / "semantics_observations.json").write_text(
        json.dumps({"observations": observations, "source_changed": changed, "source_sha256": before}, indent=2)
        + "\n", encoding="utf-8",
    )
    assert not changed, f"Source changed during diagnostic: {changed}"


if __name__ == "__main__":
    main()
