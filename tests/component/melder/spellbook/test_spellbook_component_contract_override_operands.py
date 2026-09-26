"""
Component tests for contract override operands (owner ruling 2026-09-26).

A `SpellMap` / `SpellContract` override payload may hold any object. The compiled rows carry a
value-only reference to the consumer's descriptor and the hydration resolves it back to the live
object, so the provider's constructor receives the object by identity: in-process on the first
meld, and in a fresh interpreter after a creation-cache full hit.

The cross-process check runs two probes in fresh interpreters (different `PYTHONHASHSEED`s): the
first conjures the book and writes the bundle, the second conjures the same book from that bundle,
proves the plan phases were skipped, melds the consumer and reports whether the provider holds THAT
interpreter's payload object. Both probes import this module by its dotted path; the pytest process
itself imports it as a top-level module (no `__init__.py` under `tests/`), which changes the
consumer class's `__module__` and therefore its spell id, so the writer must not be this process.
"""

import inspect
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame_configuration import (
    AethericFrameConfiguration,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_contract_override_operands() -> None:
    """
    Reset singleton runtime state around every test.

    Returns:
        None.
    """
    _reset_runtime()
    yield
    _reset_runtime()


def _reset_runtime() -> None:
    """Reset the Nexus and Aether singletons and rebind the class-level Aether references."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class _PayloadObject:
    """Object payload probe with the default `object.__repr__`; never enters a row."""


PAYLOAD_OBJECT = _PayloadObject()
"""The object the SpellMap payload carries; the provider must receive THIS object."""


class MapPayloadConsumer:
    """
    Consumer whose provider arrives through a `SpellMap` carrying an object payload.

    Contract:
        - Phase 9 records the payload against the provider's dependency occurrence, so the
          executor builds `BasicService(marker=PAYLOAD_OBJECT)`.
    """

    def __init__(
            self,
            service: BasicService = SpellMap(spell=BasicService, override={"marker": PAYLOAD_OBJECT}),
    ) -> None:
        """
        Capture the mapped provider.

        Args:
            service:
                Provider resolved through the SpellMap default.
        """
        self.service = service


def _package_root() -> Path:
    """Return the melder package root the runtime anchors relative cache fragments against."""
    return Path(inspect.getfile(AethericFrameConfiguration)).resolve().parents[2]


def _cache_root_fragment(name: str) -> Path:
    """Return the package-relative cache root fragment for one test directory name."""
    return Path("tests/component/melder/spellbook") / name


def _prepare_cache_root(fragment: Path) -> Path:
    """Reset the repo-local cache root for the test and return its absolute path."""
    path = _package_root() / fragment
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _bundle_path(fragment: Path) -> Path:
    """Return the root conduit's `.melc` path under the default frame for one cache root."""
    return (_package_root() / fragment / "__conjure_cache__" / "default" / "root.melc").resolve()


def _activate_cache(fragment: Path, *, enabled: bool) -> None:
    """Activate the default frame's cache posture for the test."""
    configuration = Aether()._ensure_frame("default").frame_configuration
    assert configuration is not None
    configuration.with_system_caching_enabled(enabled)
    configuration.with_system_cache_root_path(fragment)


def _make_book() -> Tuple[Spellbook, str]:
    """Build the two-spell book (the provider and the SpellMap consumer); return it with the consumer id."""
    spellbook = Spellbook(aetheric_frame="default")
    spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(spell=BasicService, existence="unique", permissions="create")
    consumer_id = spellbook.bind(spell=MapPayloadConsumer, existence="unique", permissions="create")
    return spellbook, consumer_id


def _consumer_spell(spellbook: Spellbook) -> Any:
    """Return the live consumer spell of the book."""
    for spell_index, spell in spellbook.spells.items():
        if spell.spell is MapPayloadConsumer:
            return spell
    raise RuntimeError("The consumer spell is missing from the book.")


def test_component_spellmap_object_payload_reaches_the_provider_by_identity() -> None:
    """
    With caching disabled the first meld hydrates the executor from the in-process rows; the
    provider receives the payload object itself, not a projection of it.
    """
    _activate_cache(_cache_root_fragment("_contract_operands_in_process"), enabled=False)
    spellbook, _consumer_id = _make_book()
    spellbook.conjure(name="root")

    instance = spellbook._conduit.meld(spell=MapPayloadConsumer)

    assert isinstance(instance, MapPayloadConsumer)
    assert isinstance(instance.service, BasicService)
    assert instance.service.marker is PAYLOAD_OBJECT


def probe_write_bundle(fragment: str) -> Dict[str, Any]:
    """
    Conjure the book in THIS interpreter so the creation cache writes the bundle; meld once.

    Contract:
        - Runs in a fresh probe process against a cache root the parent prepared (empty).
        - Reports whether the bundle exists after conjure, whether the first meld handed the
          provider this process's `PAYLOAD_OBJECT`, and the consumer's spell id (the key the
          second probe's full hit depends on).

    Args:
        fragment:
            Package-relative cache root fragment prepared by the parent process.

    Returns:
        Dict[str, Any]:
            `{"bundle_exists": bool, "identity": bool, "consumer_spell_id": str}`.
    """
    _reset_runtime()
    _activate_cache(Path(fragment), enabled=True)
    spellbook, consumer_id = _make_book()
    spellbook.conjure(name="root")
    instance = spellbook._conduit.meld(spell=MapPayloadConsumer)
    return {
        "bundle_exists": _bundle_path(Path(fragment)).exists(),
        "identity": instance.service.marker is PAYLOAD_OBJECT,
        "consumer_spell_id": consumer_id,
    }


def probe_cache_hit_identity(fragment: str) -> Dict[str, Any]:
    """
    Conjure the book from an existing bundle in THIS interpreter and meld the consumer.

    Contract:
        - Runs in a fresh probe process: resets the runtime, activates the cache root the first
          probe wrote, conjures, melds once.
        - Reports the three full-hit facts separately (the bundle existed before conjure, the
          consumer has no published phase-10 plan because phases 8-11 were skipped, and the bundle
          was not rewritten), whether the provider holds this process's `PAYLOAD_OBJECT`, and the
          consumer's spell id.

    Args:
        fragment:
            Package-relative cache root fragment written by the first probe.

    Returns:
        Dict[str, Any]:
            `{"bundle_existed", "plan_skipped", "bundle_untouched", "identity", "marker_type",
            "consumer_spell_id"}`.
    """
    _reset_runtime()
    _activate_cache(Path(fragment), enabled=True)
    spellbook, consumer_id = _make_book()
    # The caching system binds to the conjured root, so the bundle is located from the cache
    # root directly before conjure and cross-checked against the caching system afterwards.
    bundle_path = _bundle_path(Path(fragment))
    bundle_existed = bundle_path.exists()
    bundle_mtime_ns = bundle_path.stat().st_mtime_ns if bundle_existed else None
    spellbook.conjure(name="root")
    caching_system = spellbook._get_or_create_caching_system()
    if caching_system.bundle_path.resolve() != bundle_path:
        raise RuntimeError("The caching system bundle path differs from the probed path.")
    consumer = _consumer_spell(spellbook)
    plan_skipped = consumer._compiler_artifact._spell_codegen_plan is None
    bundle_untouched = bundle_path.stat().st_mtime_ns == bundle_mtime_ns

    instance = spellbook._conduit.meld(spell=MapPayloadConsumer)

    return {
        "bundle_existed": bundle_existed,
        "plan_skipped": plan_skipped,
        "bundle_untouched": bundle_untouched,
        "identity": instance.service.marker is PAYLOAD_OBJECT,
        "marker_type": type(instance.service.marker).__name__,
        "consumer_spell_id": consumer_id,
    }


def _run_probe(probe_name: str, fragment: Path, hash_seed: str) -> Dict[str, Any]:
    """
    Run one module-level probe in a fresh interpreter and return its JSON report.

    Args:
        probe_name:
            Name of a module-level probe function in this module.
        fragment:
            Package-relative cache root fragment passed to the probe.
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
    source = (
        "import json, sys\n"
        "from tests.component.melder.spellbook."
        "test_spellbook_component_contract_override_operands import {0}\n"
        "print(json.dumps({0}(sys.argv[1])))\n"
    ).format(probe_name)
    result = subprocess.run(
        [sys.executable, "-c", source, str(fragment)],
        cwd=repository,
        env=environment,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert result.returncode == 0, "probe {0} failed:\n{1}".format(probe_name, result.stderr)
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_component_spellmap_object_payload_survives_a_cross_process_cache_hit() -> None:
    """
    One fresh interpreter writes the bundle; a second one full-hits it, skips phases 8-11, and
    still hands the provider its own `PAYLOAD_OBJECT`: the row carried a reference to the
    descriptor, never the object.
    """
    fragment = _cache_root_fragment("_contract_operands_cross_process")
    _prepare_cache_root(fragment)

    writer = _run_probe("probe_write_bundle", fragment, "3")
    assert writer["bundle_exists"] is True, writer
    assert writer["identity"] is True, writer

    reader = _run_probe("probe_cache_hit_identity", fragment, "7")
    assert reader["consumer_spell_id"] == writer["consumer_spell_id"], (writer, reader)
    assert reader["bundle_existed"] is True, reader
    assert reader["plan_skipped"] is True, reader
    assert reader["bundle_untouched"] is True, reader
    assert reader["identity"] is True, reader
    assert reader["marker_type"] == "_PayloadObject", reader
