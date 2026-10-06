"""Isolate injected-provider lookup using public native APIs, without Toolbox construction."""

import pytest

from tests.component.spectrum.conftest import spectrum, reset_spectrum_and_melder
from tests.component.spectrum.test_toolbox_native_dispense import host


class NativeService:
    """Concrete no-argument dependency, intentionally unrelated to Toolbox."""

    def __init__(self) -> None:
        """Make ordinary instance state so this is not an empty-class signature probe."""
        self.value = 7


class NativeConsumer:
    """Require a service that the native graph supplies during construction."""

    def __init__(self, service: NativeService) -> None:
        """Retain the injected dependency for identity verification."""
        self.service = service


def test_native_dependency_can_be_melded_directly_after_injection(host) -> None:
    """A dependency resolved through a consumer should retain a usable direct creation plan."""
    root = host.get_conduit()
    root.bind(spell=NativeService, existence="unique_per_conduit", spellframe="native_probe",
              binding_name="NativeService", disposal_method_names=[])
    root.bind(spell=NativeConsumer, existence="many", spellframe="native_probe",
              binding_name="NativeConsumer", disposal_method_names=[])
    scope = root.create_lesser_conduit(name="native-provider-probe")
    consumer = scope.meld(spellframe="native_probe", binding_name="NativeConsumer")
    assert consumer.service.value == 7
    assert scope.meld(spellframe="native_probe", binding_name="NativeService") is consumer.service
