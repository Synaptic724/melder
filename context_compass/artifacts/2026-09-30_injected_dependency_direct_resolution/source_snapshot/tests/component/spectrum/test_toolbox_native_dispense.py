"""Toolbox admits native tool definitions while each product retains caller ownership."""

from typing import TYPE_CHECKING

import pytest
from melder import Cleanable

from melder_ops.command_center.spectrum.configurations.spectrum_configuration import SpectrumConfig
from melder_ops.command_center.spectrum.toolbox.base import BaseTool

if TYPE_CHECKING:
    from melder_ops.command_center.spectrum.spectrum import Spectrum


class ScopeService:
    """A native dependency whose identity distinguishes the requested construction scopes."""


class PayloadTool(BaseTool, Cleanable):
    """Caller-owned tool that preserves the exact supplied payload through native overrides."""

    def __init__(self, payload: object) -> None:
        """Borrow the supplied payload without copying or adopting its disposal."""
        Cleanable.__init__(self)
        self.payload = payload

    def cleanup(self) -> None:
        """Release the borrowed payload once; callers explicitly own this operation."""
        if self._cleaned:
            return
        self._cleaned = True
        del self.payload

    def execute(self) -> object:
        """Return the original payload while live, failing on use after cleanup."""
        self.check_cleaned()
        return self.payload


class AssistedTool(PayloadTool):
    """Require a native service to prove Toolbox performs DI rather than direct construction."""

    def __init__(self, service: ScopeService, payload: object) -> None:
        """Borrow the injected service and the caller's exact payload."""
        super().__init__(payload)
        self.service = service

    def cleanup(self) -> None:
        """Release the service without disposing its native scope's dependency."""
        if self._cleaned:
            return
        del self.service
        super().cleanup()


class OtherPayloadTool(PayloadTool):
    """Distinct concrete implementation for alias replacement."""


class ExplodingTool(BaseTool):
    """Raise a caller-supplied exception to verify native error translation."""

    def __init__(self, failure: Exception) -> None:
        """Refuse construction with the exact supplied failure instance."""
        raise failure

    def execute(self) -> None:
        """This method is unreachable because construction always fails."""
        raise AssertionError("ExplodingTool cannot be constructed.")


@pytest.fixture
def host(spectrum: Spectrum) -> Spectrum:
    """Configure real native definitions; the suite fixture retains teardown ownership."""
    spectrum.configure(SpectrumConfig().with_iris_logger_options(
        include_stream_mirror=False, include_system_stream_mirror=False,
    ))
    return spectrum


def test_toolbox_stays_unique_while_tools_are_fresh_and_inputs_keep_identity(host: Spectrum) -> None:
    """Shared manager identity never makes two requests share a tool product."""
    root = host.get_conduit()
    toolbox = host.toolbox
    assert root.meld(spellframe="spectrum", binding_name="Toolbox") is toolbox
    toolbox.register_tool("payload", PayloadTool)
    payload = {"items": []}
    first = toolbox.build_tool("payload", conduit=root, payload=payload)
    second = toolbox.build_tool("payload", conduit=root, payload=payload)
    try:
        assert first is not second
        assert first.execute() is payload
        assert second.execute() is payload
    finally:
        first.cleanup()
        second.cleanup()


def test_tool_dependencies_resolve_from_each_requested_scope(host: Spectrum) -> None:
    """Required collaborators are injected per scope while explicit inputs retain identity."""
    root = host.get_conduit()
    root.bind(spell=ScopeService, existence="unique_per_conduit", spellframe="tool_dependencies",
              binding_name="ScopeService", disposal_method_names=[])
    host.toolbox.register_tool("assisted", AssistedTool)
    first_scope = root.create_lesser_conduit(name="tool-first")
    second_scope = root.create_lesser_conduit(name="tool-second")
    payload = []
    first = host.toolbox.build_tool("assisted", conduit=first_scope, payload=payload)
    repeated = host.toolbox.build_tool("assisted", conduit=first_scope, payload=payload)
    second = host.toolbox.build_tool("assisted", conduit=second_scope, payload=payload)
    try:
        assert first.service is repeated.service
        assert first.service is not second.service
        assert first.execute() is payload and repeated.execute() is payload and second.execute() is payload
    finally:
        first.cleanup()
        repeated.cleanup()
        second.cleanup()
        first_scope.cleanup()
        second_scope.cleanup()


def test_tool_survives_alias_scope_and_manager_retirement_until_explicit_cleanup(host: Spectrum) -> None:
    """A cleanable product stays with its caller after every factory-side owner retires."""
    root = host.get_conduit()
    scope = root.create_lesser_conduit(name="caller-owned-tool")
    host.toolbox.register_tool("payload", PayloadTool)
    payload = []
    tool = host.toolbox.build_tool("payload", conduit=scope, payload=payload)
    host.toolbox.unregister_tool("payload")
    scope.cleanup()
    host.toolbox.cleanup()
    try:
        assert not tool.cleaned
        assert tool.execute() is payload
    finally:
        tool.cleanup()
    assert tool.cleaned


def test_only_last_alias_removes_an_owned_definition(host: Spectrum) -> None:
    """Two aliases share one definition; removing either preserves the other until its removal."""
    root = host.get_conduit()
    host.toolbox.register_tool("first", PayloadTool)
    host.toolbox.register_tool("second", PayloadTool)
    definition = root.find_spell_id("spectrum", "PayloadTool", "PayloadTool")
    host.toolbox.unregister_tool("first")
    assert root.find_spell_id("spectrum", "PayloadTool", "PayloadTool") == definition
    tool = host.toolbox.build_tool("second", conduit=root, payload=21)
    try:
        assert tool.execute() == 21
    finally:
        tool.cleanup()
    host.toolbox.unregister_tool("second")
    with pytest.raises(ValueError):
        root.find_spell_id("spectrum", "PayloadTool", "PayloadTool")


def test_replacement_retires_only_the_displaced_definition(host: Spectrum) -> None:
    """Alias replacement selects the new implementation without cleaning an existing old product."""
    root = host.get_conduit()
    host.toolbox.register_tool("selected", PayloadTool)
    old = host.toolbox.build_tool("selected", conduit=root, payload="old")
    host.toolbox.register_tool("selected", OtherPayloadTool)
    new = host.toolbox.build_tool("selected", conduit=root, payload="new")
    try:
        assert type(new) is OtherPayloadTool
        assert old.execute() == "old" and new.execute() == "new"
        with pytest.raises(ValueError):
            root.find_spell_id("spectrum", "PayloadTool", "PayloadTool")
    finally:
        old.cleanup()
        new.cleanup()


def test_preexisting_compatible_definition_is_borrowed(host: Spectrum) -> None:
    """Removing an alias never removes the host's independently registered compatible definition."""
    root = host.get_conduit()
    original = root.bind(spell=PayloadTool, existence="many", spellframe="spectrum",
                         binding_name="PayloadTool", disposal_method_names=[])
    host.toolbox.register_tool("borrowed", PayloadTool)
    host.toolbox.unregister_tool("borrowed")
    host.toolbox.cleanup()
    assert root.find_spell_id("spectrum", "PayloadTool", "PayloadTool") == original


@pytest.mark.parametrize("mode", ["unique", "tracked", "discoverable"])
def test_incompatible_definition_refuses_replacement_before_alias_changes(host: Spectrum, mode: str) -> None:
    """Native lifetime/visibility refusal preserves the previously admitted alias."""
    root = host.get_conduit()
    host.toolbox.register_tool("selected", PayloadTool)
    root.bind(spell=OtherPayloadTool, existence="unique" if mode == "unique" else "many",
              resolvable=mode != "discoverable", spellframe="spectrum", binding_name="OtherPayloadTool",
              disposal_method_names=["cleanup"] if mode == "tracked" else [])
    with pytest.raises(ValueError):
        host.toolbox.register_tool("selected", OtherPayloadTool)
    tool = host.toolbox.build_tool("selected", conduit=root, payload="original")
    try:
        assert type(tool) is PayloadTool
        assert tool.execute() == "original"
    finally:
        tool.cleanup()


def test_abstract_tool_refused_before_publication(host: Spectrum) -> None:
    """An abstract BaseTool cannot become an alias that fails only when someone tries to use it."""
    with pytest.raises(TypeError, match="abstract"):
        host.toolbox.register_tool("abstract", BaseTool)
    assert "abstract" not in host.toolbox.list_tools()


@pytest.mark.parametrize("error_type", [ValueError, RuntimeError, TypeError])
def test_native_constructor_failures_keep_toolbox_error_contract(host: Spectrum, error_type: type[Exception]) -> None:
    """Unwrap native constructor failures, retaining Toolbox's existing TypeError diagnostic."""
    host.toolbox.register_tool("broken", ExplodingTool)
    failure = error_type("tool refused construction")
    with pytest.raises(error_type) as caught:
        host.toolbox.build_tool("broken", conduit=host.get_conduit(), failure=failure)
    if error_type is TypeError:
        assert "Failed to build tool 'broken'" in str(caught.value)
    else:
        assert caught.value is failure


def test_group_facade_builds_a_native_tool_without_exposing_scope_arguments(host: Spectrum) -> None:
    """Application callers use the usual group facade while the group forwards its own scope."""
    center = host.create_command_center("tools")
    center.register_tool("payload", PayloadTool)
    group = center.get_command_group(center.config.default_command_group_name)
    payload = []
    tool = group.build_tool("payload", payload=payload)
    try:
        assert tool.execute() is payload
        assert group.build_tool("missing") is None
        with pytest.raises(TypeError, match="conduit"):
            group.build_tool("payload", conduit=host.get_conduit(), payload=payload)
    finally:
        tool.cleanup()
