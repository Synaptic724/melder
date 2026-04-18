from types import SimpleNamespace

import pytest

from melder.aether.nexus.rift.command_system.static_command_system import (
    StaticCommandSystem,
)
from melder.spellbook.existence.existence import Existence


def _make_spell_record(
    *,
    spell_id: str = "sha-1",
    spell_index_id: str = "lineage-1",
    owner_conduit_id: str = "ops-conduit",
    existence: Existence = Existence.unique,
) -> object:
    return SimpleNamespace(
        origin_spellbook_id="ops-spellbook",
        frame_name="ops",
        owner_conduit_id=owner_conduit_id,
        spell_id=spell_id,
        spell_index_id=spell_index_id,
        spell_name="OpsSpell",
        binding_name="ops_spell",
        existence=existence,
    )


class _Viewer:
    def __init__(self) -> None:
        self.default_view_frame_name = "ops"
        self.descriptor = SimpleNamespace(
            spell_records_by_key={},
        )
        self.compiled_access_surface = SimpleNamespace(
            command_frame_enabled=True,
            enabled_spell_index_ids=tuple(),
        )

    def _get_required_frame_descriptor(self, frame_name: str) -> object:
        return self.descriptor

    def _get_required_compiled_access_surface(self, frame_name: str) -> object:
        return self.compiled_access_surface

    def _get_required_spell_record(
        self,
        source_id: str,
        *,
        frame_name: str = None,
    ) -> tuple[str, object]:
        return frame_name or "ops", self.descriptor.spell_records_by_key[source_id]


def _make_static_command_system() -> tuple[StaticCommandSystem, _Viewer]:
    viewer = _Viewer()
    workstation = SimpleNamespace()
    command_projection = SimpleNamespace(
        frame_descriptor=viewer.descriptor,
        compiled_access_surface=viewer.compiled_access_surface,
    )
    space = SimpleNamespace(
        space_id="space-1",
        get_default_runtime_frame_name=lambda: viewer.default_view_frame_name,
        get_required_command_projection=lambda frame_name: command_projection,
        rift_gate=None,
        memory_system=None,
    )
    return StaticCommandSystem(space=space, workstation=workstation), viewer


def test_static_command_system_status_reports_missing_and_ambiguous_publication() -> None:
    command_system, viewer = _make_static_command_system()
    with pytest.raises(ValueError, match="spell_source_id cannot be empty"):
        command_system.describe_spell_status_by_source_id("")

    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-1"] = _make_spell_record(
        spell_index_id="lineage-1",
    )
    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-1-shadow"] = _make_spell_record(
        spell_id="sha-1",
        spell_index_id="lineage-2",
    )

    status = command_system.describe_spell_status_by_source_id("ops-spellbook:missing")
    assert status["reason"] == "not_published"

    status = command_system.describe_spell_status_by_source_id("ops-spellbook:sha-1")
    assert status["reason"] == "ambiguous_spell_source_id"

    status = command_system.describe_spell_status_by_id("missing")
    assert status["reason"] == "not_published"

    status = command_system.describe_spell_status_by_id("sha-1")
    assert status["reason"] == "ambiguous_spell_id"

    status = command_system.describe_spell_status_by_index_id("missing-lineage")
    assert status["reason"] == "not_published"

    viewer.descriptor.spell_records_by_key.pop("ops-spellbook:sha-1-shadow")
    command_system._aether = SimpleNamespace(
        _get_conduit_by_id=lambda conduit_id, frame_name: SimpleNamespace(
            has_live_creation=lambda *, spell: False
        )
    )
    status = command_system.describe_spell_status_by_id("sha-1")
    assert status["spell_id"] == "sha-1"


def test_static_command_system_reports_ambiguous_index_and_command_disabled_not_live() -> None:
    command_system, viewer = _make_static_command_system()
    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-1"] = _make_spell_record(
        spell_index_id="lineage-1",
    )
    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-2"] = _make_spell_record(
        spell_id="sha-2",
        spell_index_id="lineage-1",
    )

    status = command_system.describe_spell_status_by_index_id("lineage-1")
    assert status["reason"] == "ambiguous_spell_index_id"

    viewer.descriptor.spell_records_by_key.pop("ops-spellbook:sha-2")
    viewer.compiled_access_surface.command_frame_enabled = False
    command_system._aether = SimpleNamespace(
        _get_conduit_by_id=lambda conduit_id, frame_name: SimpleNamespace(
            has_live_creation=lambda *, spell: True
        )
    )
    status = command_system.describe_spell_status_by_index_id("lineage-1")
    assert status["is_command_enabled"] is False
    assert status["reason"] == "command_disabled"

    viewer.compiled_access_surface.command_frame_enabled = True
    viewer.compiled_access_surface.enabled_spell_index_ids = ("lineage-1",)
    command_system._aether = SimpleNamespace(
        _get_conduit_by_id=lambda conduit_id, frame_name: SimpleNamespace(
            has_live_creation=lambda *, spell: False
        )
    )
    status = command_system.describe_spell_status_by_index_id("lineage-1")
    assert status["is_command_enabled"] is True
    assert status["is_live"] is False
    assert status["reason"] == "not_live"


def test_static_command_system_get_spell_by_index_id_guardrails_and_ownerless_path() -> None:
    command_system, viewer = _make_static_command_system()

    with pytest.raises(ValueError, match="spell_index_id cannot be empty"):
        command_system.get_spell_by_index_id("")

    viewer.compiled_access_surface.enabled_spell_index_ids = ("lineage-1",)
    with pytest.raises(ValueError, match="Spell index id 'lineage-1' was not found"):
        command_system.get_spell_by_index_id("lineage-1")

    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-1"] = _make_spell_record(
        owner_conduit_id=None,
    )
    with pytest.raises(
        ValueError,
        match="Spell lineage 'lineage-1' is not live in frame 'ops'",
    ):
        command_system.get_spell_by_index_id("lineage-1")


def test_static_command_system_get_spell_by_index_id_reports_unsupported_static_existence() -> None:
    command_system, viewer = _make_static_command_system()
    viewer.compiled_access_surface.enabled_spell_index_ids = ("lineage-many",)
    viewer.descriptor.spell_records_by_key["ops-spellbook:many-sha"] = _make_spell_record(
        spell_id="many-sha",
        spell_index_id="lineage-many",
        existence=Existence.many,
    )

    with pytest.raises(ValueError, match="unsupported static existence 'many'"):
        command_system.get_spell_by_index_id("lineage-many")
