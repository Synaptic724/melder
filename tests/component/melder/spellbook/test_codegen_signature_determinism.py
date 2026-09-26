"""
Component tests for the codegen signature path: byte-compatibility against the frozen
reference bodies over a real plan, and equality across interpreter processes.

Two fixtures feed the cross-process check:

- the PLAIN book (providers plus one consumer, no contracts) whose signatures were already
  deterministic before the single `CodegenSignature` implementation landed; it must be equal
  across processes before and after the change (regression guard);
- the CONTRACT-PAYLOAD book, whose consumer carries a `SpellContract` override payload holding
  an object with the default `object.__repr__`. Before the change that payload froze to a
  `repr` carrying a memory address, so its executor signature differed in every process; since
  2026-09-26 the rows carry a value-only reference to the consumer's descriptor instead of the
  object, the signatures agree, and the hydrated executor hands the provider the object itself
  (the fixture asserts identity).

The subprocess pattern follows `test_ordered_disposal_binding.py`: each probe runs in a fresh
interpreter with its own `PYTHONHASHSEED`, imports this module and prints one JSON document.
"""

import json
import marshal
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (
    build_package as build_legacy_package,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    MANIFEST_METADATA_KEY,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    build_package as build_manifest_package,
)
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.shared_assets.codegen_signature import (
    CodegenSignature,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
from tests.component.melder.spellbook.spell_compiler_runtime_test_support import (
    get_spell_by_version_id,
    make_spellbook,
    reset_aether_runtime,
    run_foundational_phases,
    run_plan_phases,
    run_structural_phases,
)
from tests.mocks.spellbook.codegen_signature_reference import (
    reference_hash_codegen_signature,
)
from tests.mocks.spellbook.core_classes import BasicConfig, BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_signature_determinism() -> None:
    """Reset Aether around each test so probes never see another test's frame posture."""
    reset_aether_runtime()
    yield
    reset_aether_runtime()


class PayloadMarker:
    """
    Contract-payload probe object whose `repr` is the default `object.__repr__`.

    Contract:
        - Deliberately defines no `__repr__`, so its textual form carries a memory
          address and differs between instances and between interpreter processes.
        - Picklable by reference to this module-level class; neither the signature path
          nor a step row ever holds it: the row carries the phase-9 reference and the
          hydration hands the provider the object itself.
    """

    def __init__(self, label: str) -> None:
        """
        Store the label the probe passes to the provider constructor.

        Args:
            label:
                Free text; never enters the signature.
        """
        self.label = label


PAYLOAD_MARKER = PayloadMarker("payload")
"""The object the contract fixture's payload carries; the provider must receive THIS object."""


class PlainConsumer:
    """Consumer of two local providers; the plain fixture's root spell."""

    def __init__(self, service: BasicService, config: BasicConfig) -> None:
        """
        Capture both injected providers.

        Args:
            service:
                Injected `BasicService`.
            config:
                Injected `BasicConfig`.
        """
        self.service = service
        self.config = config


class ContractConsumer:
    """
    Consumer whose provider arrives through a `SpellContract` carrying an object payload.

    Contract:
        - The contract is satisfied by a contracted `IService` provider named `primary`
          linked in from another conduit; the payload is applied to that provider's
          constructor (`BasicService(marker=PayloadMarker(...))`).
        - The payload object is what made the no-overrides executor signature
          process-local under the previous `repr` rendering; rows now carry a
          reference and the constructor receives `PAYLOAD_MARKER` by identity.
    """

    def __init__(
            self,
            service: IService = SpellContract(
                spellframe=IService,
                binding_name="primary",
                override={"marker": PAYLOAD_MARKER},
            ),
    ) -> None:
        """
        Capture the contracted service.

        Args:
            service:
                Provider resolved through the contract socket.
        """
        self.service = service


class StringPayloadContractConsumer:
    """
    Same contract shape as `ContractConsumer` with a replayable (string) payload value.

    Contract:
        - Its row carries the string itself; the object-payload sibling's row carries a reference.
    """

    def __init__(
            self,
            service: IService = SpellContract(
                spellframe=IService,
                binding_name="primary",
                override={"marker": "override"},
            ),
    ) -> None:
        """
        Capture the contracted service.

        Args:
            service:
                Provider resolved through the contract socket.
        """
        self.service = service


def _read_signatures(spell: Any, spell_id: str) -> Dict[str, Any]:
    """
    Read the executor signatures phase 11 published for one compiled spell.

    Args:
        spell:
            Live `Spell` whose compiler artifact holds a `SpellCodegenCreation`.
        spell_id:
            The spell's version id, echoed so id drift is visible in a mismatch.

    Returns:
        Dict[str, Any]:
            `spell_id`, the no-overrides executor signature (every family sets it) and the
            overrides lane's step-rows signature when the family publishes one.

    Raises:
        RuntimeError:
            When phase 11 has not published a creation for the spell.
    """
    creation = spell._compiler_artifact._spell_codegen_creation
    if creation is None:
        raise RuntimeError(
            "Phase 11 published no SpellCodegenCreation for spell {0}.".format(spell_id)
        )
    metadata = creation.metadata
    return {
        "spell_id": spell_id,
        "no_overrides_executor_signature": metadata["_no_overrides_executor_signature"],
        "override_steps_rows_signature": metadata.get("override_steps_rows_signature"),
    }


def probe_plain_book_signatures() -> Dict[str, Dict[str, Any]]:
    """
    Compile the plain fixture through `SpellCompilerSystem` and collect its signatures.

    Contract:
        - Binds `BasicService`, `BasicConfig` and `PlainConsumer` (all unique), runs the
          structural phases for all three and then phases 5-11 for each, through the shared
          runtime helpers; no conduit is conjured and the creation cache is never consulted.
        - Safe to call from a subprocess probe: it resets the Aether runtime itself.

    Returns:
        Dict[str, Dict[str, Any]]:
            Signatures keyed by `service`, `config` and `consumer`.
    """
    reset_aether_runtime()
    spellbook = make_spellbook()
    compiler_system = SpellCompilerSystem()
    try:
        bound: Tuple[Tuple[str, str], ...] = (
            (
                "service",
                spellbook.bind(
                    spell=BasicService, existence=Existence.unique, permissions="create",
                ),
            ),
            (
                "config",
                spellbook.bind(
                    spell=BasicConfig, existence=Existence.unique, permissions="create",
                ),
            ),
            (
                "consumer",
                spellbook.bind(
                    spell=PlainConsumer, existence=Existence.unique, permissions="create",
                ),
            ),
        )
        spells: List[Tuple[str, str, Any]] = []
        for label, spell_id in bound:
            spell = get_spell_by_version_id(spellbook, spell_id)
            if spell is None:
                raise RuntimeError("Bound spell {0} is missing from the pool.".format(label))
            spells.append((label, spell_id, spell))
        # Conjure order: every spell's structural phases run before any spell's
        # conduit phases, because phase 5 walks the whole book's local frames.
        for _label, _spell_id, spell in spells:
            run_structural_phases(compiler_system, spellbook, spell)
        signatures: Dict[str, Dict[str, Any]] = {}
        for label, spell_id, spell in spells:
            run_foundational_phases(
                compiler_system, spellbook, spell, "codegen-signature-probe",
            )
            run_plan_phases(compiler_system, spellbook, spell)
            signatures[label] = _read_signatures(spell, spell_id)
        return signatures
    finally:
        compiler_system.cleanup()
        spellbook.cleanup()


def _compile_contract_payload_book(consumer_class: type) -> Tuple[Any, Any, Any, str]:
    """
    Conjure the contract-payload fixture through the public API up to the first meld.

    Contract:
        - Two dynamic books in the default frame with the system creation cache disabled
          (so every process computes fresh signatures instead of loading a `.melc`).
        - The owner book provides `BasicService` as `IService`/`primary`; the borrower book
          binds `consumer_class`; the conduits are linked, the provider is added to the
          contract, contracts are validated and the consumer is melded once so phases 8-11
          compile the contract payload into the consumer's plan.
        - The caller owns cleanup: `borrower.cleanup()` then `owner.cleanup()`.

    Args:
        consumer_class:
            `ContractConsumer` or `StringPayloadContractConsumer`.

    Returns:
        Tuple[Any, Any, Any, str]:
            `(owner, borrower, borrower_book, consumer_id)`.

    Raises:
        RuntimeError:
            When the frame posture is missing, the contract cannot be added or validated,
            or the melded consumer did not receive the payload-constructed provider.
    """
    reset_aether_runtime()
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    frame_configuration = Aether()._ensure_frame("default").frame_configuration
    if frame_configuration is None:
        raise RuntimeError("The default frame carries no AethericFrameConfiguration.")
    frame_configuration.with_system_caching_enabled(False)

    owner_book = Spellbook(configuration=configuration)
    service_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )
    borrower_book = Spellbook(configuration=configuration)
    consumer_id = borrower_book.bind(
        spell=consumer_class, existence=Existence.unique, permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="codegen-signature-probe-owner")
    borrower = borrower_book.conjure(dynamic=True, name="codegen-signature-probe-borrower")
    try:
        if not owner.link(borrower):
            raise RuntimeError("owner.link(borrower) returned False.")
        with borrower.transaction("link", conduits=[borrower, owner]):
            if not borrower.add_spell_to_contract(
                    spell_id=service_id, conduit=owner, permissions="create",
            ):
                raise RuntimeError("add_spell_to_contract returned False.")
        verdicts = borrower.validate_contracts_and_define()
        if not verdicts or not all(verdicts.values()):
            raise RuntimeError("Contract validation failed: {0!r}".format(verdicts))
        instance = borrower.meld(spell_id=consumer_id)
        if not isinstance(instance.service, BasicService):
            raise RuntimeError("The contracted provider was not constructed.")
        consumer_spell = get_spell_by_version_id(borrower_book, consumer_id)
        if consumer_spell is None:
            raise RuntimeError("The consumer spell is missing from the borrower pool.")
        payload_value = _plan_contract_payload_value(consumer_spell, "marker")
        if consumer_class is StringPayloadContractConsumer:
            if payload_value != "override":
                raise RuntimeError("The string payload did not reach the consumer's plan.")
            if instance.service.marker != "override":
                raise RuntimeError("The string payload did not reach the provider constructor.")
        elif payload_value is not PAYLOAD_MARKER:
            raise RuntimeError("The object payload did not reach the consumer's plan.")
        elif instance.service.marker is not PAYLOAD_MARKER:
            # The manifest-first executor hydrates from the step rows in-process too; the
            # row carries a reference to the descriptor and the hydration resolves it to
            # the live object, so the provider must hold the very same object.
            raise RuntimeError("The object payload did not reach the provider by identity.")
    except BaseException:
        borrower.cleanup()
        owner.cleanup()
        raise
    return owner, borrower, borrower_book, consumer_id


def probe_contract_payload_book_signatures() -> Dict[str, Dict[str, Any]]:
    """
    Conjure the object-payload contract fixture and collect the consumer's signatures.

    Contract:
        - Thin wrapper over `_compile_contract_payload_book(ContractConsumer)` that reads the
          signatures and cleans both conduits up.
        - Safe to call from a subprocess probe: it resets the Aether runtime itself.

    Returns:
        Dict[str, Dict[str, Any]]:
            Signatures keyed by `consumer`.
    """
    owner, borrower, borrower_book, consumer_id = _compile_contract_payload_book(ContractConsumer)
    try:
        consumer_spell = get_spell_by_version_id(borrower_book, consumer_id)
        if consumer_spell is None:
            raise RuntimeError("The consumer spell is missing from the borrower pool.")
        return {"consumer": _read_signatures(consumer_spell, consumer_id)}
    finally:
        borrower.cleanup()
        owner.cleanup()


def _plan_contract_payload_value(spell: Any, param_name: str) -> Any:
    """
    Return the raw contract payload value phase 10 recorded for `param_name` on any step.

    Args:
        spell:
            Live spell with a published phase-10 plan.
        param_name:
            Payload keyword to look up.

    Returns:
        Any:
            The raw value from the first step (either lane) whose payload carries it.

    Raises:
        RuntimeError:
            When no step of either lane carries the payload keyword.
    """
    plan = spell._compiler_artifact._spell_codegen_plan
    if plan is None:
        raise RuntimeError("The spell has no published phase-10 plan.")
    for lane_plan in (plan.no_overrides_plan, plan.overrides_plan):
        if lane_plan is None:
            continue
        for step in lane_plan.steps:
            contract_payload = step.contract_payload
            if contract_payload and param_name in contract_payload:
                return contract_payload[param_name]
    raise RuntimeError("No plan step carries the contract payload {0!r}.".format(param_name))


def _build_cache_package(spell: Any) -> Any:
    """
    Build the spell's creation-cache package the way `Spellbook._emit_spell_cache` dispatches.

    Args:
        spell:
            Live spell with phase-11 output.

    Returns:
        Any:
            The package dict (every plan packages since 2026-09-26).
    """
    creation = spell._compiler_artifact._spell_codegen_creation
    if creation.metadata.get(MANIFEST_METADATA_KEY) is not None:
        return build_manifest_package(spell)
    return build_legacy_package(spell)


def _probe_source(probe_name: str) -> str:
    """
    Build the `python -c` source that runs one probe and prints its JSON document.

    Args:
        probe_name:
            Name of a module-level probe function in this module.

    Returns:
        str:
            Source text; the printed document carries `environment` (the hash seed the
            process ran with) and `signatures` (the probe result), tuples rendered as lists
            and any non-JSON value rendered through `repr`.
    """
    return (
        "import json, os\n"
        "from tests.component.melder.spellbook.test_codegen_signature_determinism "
        "import {0}\n"
        "document = {{\"environment\": {{\"hash_seed\": os.environ.get(\"PYTHONHASHSEED\")}}, "
        "\"signatures\": {0}()}}\n"
        "print(json.dumps(document, default=repr, sort_keys=True))\n"
    ).format(probe_name)


def _run_probe_in_fresh_process(probe_name: str, hash_seed: str) -> Dict[str, Any]:
    """
    Run one probe in a fresh interpreter with the given `PYTHONHASHSEED`.

    Args:
        probe_name:
            Module-level probe function name.
        hash_seed:
            Value for `PYTHONHASHSEED` in the child process.

    Returns:
        Dict[str, Any]:
            The parsed JSON document the child printed.

    Raises:
        AssertionError:
            When the child exits non-zero; the message carries its stderr.
    """
    repository = Path(__file__).resolve().parents[4]
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = hash_seed
    environment["PYTHONPATH"] = os.pathsep.join((str(repository / "src"), str(repository)))
    result = subprocess.run(
        [sys.executable, "-c", _probe_source(probe_name)],
        cwd=repository,
        env=environment,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        "probe {0} failed under PYTHONHASHSEED={1}:\n{2}".format(
            probe_name, hash_seed, result.stderr,
        )
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    "probe_name",
    [
        "probe_plain_book_signatures",
        # Formerly xfail(strict=True): the consumer's spell id was process-local because the
        # SpellContract default's repr carried the PayloadMarker's address into the hashed
        # constructor signature. The bind fingerprint hashes address-free text since 2026-09-26.
        "probe_contract_payload_book_signatures",
    ],
)
def test_executor_signatures_are_equal_across_interpreter_processes(probe_name: str) -> None:
    """
    The same book yields byte-equal executor signatures in two processes with different
    hash seeds. The plain fixture guards byte-compatibility; the contract-payload fixture
    is the proof that object payloads no longer make the signature, or the consumer's bind-side
    spell id, process-local.
    """
    first = _run_probe_in_fresh_process(probe_name, "1")
    second = _run_probe_in_fresh_process(probe_name, "2")

    assert first["environment"]["hash_seed"] == "1"
    assert second["environment"]["hash_seed"] == "2"
    assert first["signatures"]
    for label, row in first["signatures"].items():
        # The solo family publishes a shape tuple, the generalized family a SHA256 hex
        # string; both must exist and both must agree across processes.
        assert row["no_overrides_executor_signature"] is not None, label
    assert first["signatures"] == second["signatures"]


def test_facade_hashes_match_the_reference_bytes_over_a_real_plan(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Every `hash_codegen_signature` call made while compiling the plain fixture through
    either facade produces the digest the frozen reference bodies produce for the same
    parts: the corpus byte-compatibility check, run against live parts instead of a
    captured fixture file.
    """
    observed: List[Tuple[Any, ...]] = []
    mismatches: List[Tuple[Any, ...]] = []

    def recording_hash(*parts: Any) -> str:
        """Compare the reference digest with the leaf's digest and record the parts."""
        observed.append(parts)
        expected = reference_hash_codegen_signature(*parts)
        actual = CodegenSignature.hash_codegen_signature(*parts)
        if actual != expected:
            mismatches.append(parts)
        return actual

    monkeypatch.setattr(
        SharedCompilerExecutions,
        "hash_codegen_signature",
        staticmethod(recording_hash),
        raising=True,
    )
    monkeypatch.setattr(
        CodegenCreationSchemaHelpers,
        "hash_codegen_signature",
        staticmethod(recording_hash),
        raising=True,
    )

    signatures = probe_plain_book_signatures()

    assert set(signatures) == {"service", "config", "consumer"}
    assert observed, "no signature was hashed while compiling the plain fixture"
    assert mismatches == []


def test_plain_fixture_signatures_are_stable_within_one_process() -> None:
    """
    Compiling the plain fixture twice in one process yields identical signatures: the
    pass-scoped analysis state and object identities never leak into the digests.
    """
    first = probe_plain_book_signatures()
    second = probe_plain_book_signatures()

    assert first == second
    assert first["consumer"]["no_overrides_executor_signature"] != (
        first["service"]["no_overrides_executor_signature"]
    )


def _package_no_overrides_rows(package: Dict[str, Any]) -> Tuple[Dict[str, Any], ...]:
    """
    Return the no-overrides step rows of a cache package, manifest-first or legacy.

    Args:
        package:
            A package from `_build_cache_package`.

    Returns:
        Tuple[Dict[str, Any], ...]:
            The rows the cache-load path hydrates the executor from.
    """
    if "manifest" in package:
        return tuple(package["manifest"]["no_overrides"]["steps_rows"])
    return tuple(package["no_overrides"]["steps_rows"])


def _row_payload_value(rows: Tuple[Dict[str, Any], ...], param_name: str) -> Any:
    """
    Return the row entry for `param_name` on the first row whose payload carries it.

    Raises:
        AssertionError:
            When no row carries the payload keyword.
    """
    for row in rows:
        for name, value in row["contract_payload_items"]:
            if name == param_name:
                return value
    raise AssertionError("no row carries the contract payload {0!r}".format(param_name))


@pytest.mark.parametrize(
    ("consumer_class", "expect_reference"),
    [(ContractConsumer, True), (StringPayloadContractConsumer, False)],
)
def test_cache_package_carries_a_reference_for_an_object_payload(
        consumer_class: type,
        expect_reference: bool,
) -> None:
    """
    Both consumers package (the emission gate is retired, 2026-09-26). The object-payload
    consumer's row carries the phase-9 reference naming the consumer, its parameter and the
    payload key - never the object - and the whole package marshals; the string-payload
    consumer's row carries the string itself, exactly as before.
    """
    owner, borrower, borrower_book, consumer_id = _compile_contract_payload_book(consumer_class)
    try:
        consumer_spell = get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None

        package = _build_cache_package(consumer_spell)

        assert package["spell_id"] == consumer_id
        rows = _package_no_overrides_rows(package)
        row_value = _row_payload_value(rows, "marker")
        if expect_reference:
            assert CodegenSignature.is_contract_override_ref(row_value)
            assert row_value == CodegenSignature.build_contract_override_ref(
                consumer_id, "service", "marker",
            )
        else:
            assert row_value == "override"
        assert not any(
            isinstance(value, PayloadMarker)
            for row in rows for _name, value in row["contract_payload_items"]
        )
        marshal.dumps(rows)
    finally:
        borrower.cleanup()
        owner.cleanup()
