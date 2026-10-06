"""
Probe: direct meld of an injected provider from the same scope, on bare Melder (no MelderOps host).

    python direct_meld_probe.py <variant> <frame_name> <cache: on|off>

One fresh process per run, because Melder's roots are process singletons. Every result line is JSON prefixed
with RESULT. The frame name also names the root conduit, so it keys the creation-cache bundle
(<melder package>/__melder_cache__/<frame>/<conduit>.melc): a new frame name with cache "on" is a cold cache, the
same frame name run twice is a warm one, and cache "off" disables system caching for the frame.

Variants:
  diagnostic            the epic's body: dynamic root, late root.bind of the service (unique_per_conduit) and the
                        consumer (many) at spellframe native_probe, a named lesser melds the consumer, then melds
                        the service directly
  resident              as diagnostic, but the root already holds an unrelated spell at conjure (as a host root does)
  root_scope            as diagnostic, melding on the root instead of a lesser
  anonymous_lesser      as diagnostic, with an unnamed lesser
  provider_first        the direct service meld first, then the consumer, then the service again
  binds_before_conjure  both binds on the Book before conjure, then the named lesser melds
  service_many          as diagnostic with the service bound many (a direct meld builds a new object)
  service_unique        as diagnostic with the service bound unique
  sibling_scopes        as diagnostic in two sibling lessers: identity within each, isolation across them
"""
import json
import pathlib
import sys
import traceback
from typing import Any, Optional

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def _emit(**fields: object) -> None:
    """Print one JSON result line."""
    print("RESULT " + json.dumps(fields, default=str, sort_keys=True))


def _chain(error: BaseException) -> list[str]:
    """Summarize an exception and its causes, first line of each."""
    chain: list[str] = []
    cause: Optional[BaseException] = error
    while cause is not None and len(chain) < 5:
        chain.append(f"{type(cause).__name__}: {str(cause).splitlines()[0][:220]}")
        cause = cause.__cause__ or cause.__context__
    return chain


def _frames(error: BaseException) -> list[str]:
    """Return the innermost source frames of an exception as 'file:line in function' strings."""
    summary = traceback.extract_tb(error.__traceback__)
    return [f"{pathlib.Path(f.filename).name}:{f.lineno} in {f.name}" for f in summary[-7:]]


def _service_state(book: Any, service_id: str, conduit_id: Optional[str] = None) -> dict[str, object]:
    """Read-only look at the service spell's compiler payload, creation context and, when a resolution conduit id
    is given, its conduit-local verdicts (private reads, no mutation)."""
    state: dict[str, object] = {"book_validation_required": book._spellbook_validation_required}
    if conduit_id is not None:
        resolution_state = book._spell_system_states.get_conduit_resolution_state(conduit_id)
        if resolution_state is None:
            state["conduit_resolution_state"] = "missing"
        else:
            state["conduit_spell_validity"] = str(resolution_state.get_spell_validity(service_id))
            state["conduit_root_validity"] = str(resolution_state.get_root_validity(service_id))
    spell = book._spells_by_id.get(service_id)
    if spell is None:
        return {"spell": "missing"}
    try:
        artifact = spell._compiler_artifact
        state["artifact_present"] = artifact is not None
        if artifact is not None:
            state["codegen_payload_present"] = artifact._spell_codegen_creation is not None
    except AttributeError as error:
        state["artifact_read"] = f"AttributeError: {error}"
    try:
        state["creation_context_present"] = spell._creation_context is not None
    except AttributeError as error:
        state["creation_context_read"] = f"AttributeError: {error}"
    try:
        blueprint = spell._compiler_artifact._root_blueprint_phase5
        state["phase5_root_blueprint_present"] = blueprint is not None
        state["resolution_required"] = spell.resolution_required
    except AttributeError as error:
        state["blueprint_read"] = f"AttributeError: {error}"
    return state


def _bind_pair(target: Any, service_existence: str) -> tuple[str, str]:
    """Bind the epic's service and consumer on a Book or a normal conduit; return their spell ids."""
    from direct_meld_services import NativeConsumer, NativeService

    service_id = target.bind(spell=NativeService, existence=service_existence, spellframe="native_probe",
                             binding_name="NativeService", disposal_method_names=[])
    consumer_id = target.bind(spell=NativeConsumer, existence="many", spellframe="native_probe",
                              binding_name="NativeConsumer", disposal_method_names=[])
    return service_id, consumer_id


def _meld(scope: Any, binding_name: str) -> tuple[Any, Optional[BaseException]]:
    """Meld one of the pair by (spellframe, binding_name); return (instance, None) or (None, error)."""
    try:
        return scope.meld(spellframe="native_probe", binding_name=binding_name), None
    except Exception as error:
        return None, error


def _record(steps: list[dict[str, object]], label: str, value: Any, error: Optional[BaseException]) -> None:
    """Append one step outcome."""
    if error is None:
        steps.append({"step": label, "ok": True, "type": type(value).__name__})
    else:
        steps.append({"step": label, "ok": False, "chain": _chain(error), "frames": _frames(error)})


def _scope_sequence(scope: Any, book: Any, service_id: str, steps: list[dict[str, object]],
                    prefix: str, identity_expected: bool) -> Optional[Any]:
    """Consumer, then the service directly, then both again; record identity and the service's state."""
    resolution_conduit_id = scope._meld._resolution_conduit_id
    steps.append({"step": f"{prefix}service_state_before", **_service_state(book, service_id, resolution_conduit_id)})
    consumer, error = _meld(scope, "NativeConsumer")
    _record(steps, f"{prefix}consumer", consumer, error)
    if consumer is not None:
        steps.append({"step": f"{prefix}consumer_service_value", "value": consumer.service.value})
    steps.append({"step": f"{prefix}service_state_after_consumer",
                  **_service_state(book, service_id, resolution_conduit_id)})
    service, error = _meld(scope, "NativeService")
    _record(steps, f"{prefix}service_direct", service, error)
    if service is not None and consumer is not None:
        steps.append({"step": f"{prefix}identity", "same_object": service is consumer.service,
                      "expected": identity_expected})
    again, error = _meld(scope, "NativeService")
    _record(steps, f"{prefix}service_direct_again", again, error)
    consumer_again, error = _meld(scope, "NativeConsumer")
    _record(steps, f"{prefix}consumer_again", consumer_again, error)
    if consumer_again is not None and consumer is not None:
        steps.append({"step": f"{prefix}consumer_again_same_service",
                      "same_object": consumer_again.service is consumer.service})
    return service


def run(variant: str, frame: str, cache: str) -> None:
    """Build the root the variant asks for, run its melds and print one RESULT line."""
    import melder
    from melder import Spellbook, SpellbookConfiguration
    from direct_meld_services import ResidentService

    service_existence = {"service_many": "many", "service_unique": "unique"}.get(variant, "unique_per_conduit")
    steps: list[dict[str, object]] = []
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                system_caching_enabled=(cache == "on"))
    if variant == "resident":
        book.bind(spell=ResidentService, existence="many")
    ids: tuple[str, str] = ("", "")
    if variant == "binds_before_conjure":
        ids = _bind_pair(book, service_existence)
    root = book.conjure(name=f"{frame}-root", dynamic=True)
    if variant != "binds_before_conjure":
        ids = _bind_pair(root, service_existence)
    service_id = ids[0]
    identity_expected = service_existence != "many"
    if variant == "provider_first":
        scope = root.create_lesser_conduit(name="native-provider-probe")
        resolution_conduit_id = scope._meld._resolution_conduit_id
        steps.append({"step": "service_state_before", **_service_state(book, service_id, resolution_conduit_id)})
        first, error = _meld(scope, "NativeService")
        _record(steps, "service_direct_first", first, error)
        steps.append({"step": "service_state_after_direct",
                      **_service_state(book, service_id, resolution_conduit_id)})
        consumer, error = _meld(scope, "NativeConsumer")
        _record(steps, "consumer_after_service", consumer, error)
        if first is not None and consumer is not None:
            steps.append({"step": "identity", "same_object": consumer.service is first, "expected": True})
        again, error = _meld(scope, "NativeService")
        _record(steps, "service_direct_again", again, error)
    elif variant == "sibling_scopes":
        left = root.create_lesser_conduit(name="native-provider-left")
        right = root.create_lesser_conduit(name="native-provider-right")
        left_service = _scope_sequence(left, book, service_id, steps, "left_", identity_expected)
        right_service = _scope_sequence(right, book, service_id, steps, "right_", identity_expected)
        if left_service is not None and right_service is not None:
            steps.append({"step": "sibling_isolation", "same_object": left_service is right_service,
                          "expected": False})
    else:
        if variant == "root_scope":
            scope = root
        elif variant == "anonymous_lesser":
            scope = root.create_lesser_conduit()
        else:
            scope = root.create_lesser_conduit(name="native-provider-probe")
        _scope_sequence(scope, book, service_id, steps, "", identity_expected)
    _emit(variant=variant, frame=frame, cache=cache, melder=melder.__version__, melder_file=melder.__file__,
          python=sys.version.split()[0], gil_enabled=sys._is_gil_enabled(), service_existence=service_existence,
          steps=steps)


if __name__ == "__main__":
    try:
        run(sys.argv[1], sys.argv[2], sys.argv[3])
    except Exception as error:
        _emit(step="probe_error", chain=_chain(error), trace=traceback.format_exc()[-1800:])
        raise
