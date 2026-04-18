from types import SimpleNamespace

import pytest

from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.rift_space.memory_system.rift_memory_system import (
    RiftMemorySystem,
)


def _make_conduit_record(
    conduit_id: str = "ops-conduit",
    conduit_name: str = "root",
) -> object:
    return SimpleNamespace(
        conduit_id=conduit_id,
        payload=SimpleNamespace(conduit_name=conduit_name),
    )


def _make_spell_record(
    *,
    spell_id: str = "sha-1",
    spell_index_id: str = "lineage-1",
    owner_conduit_id: str = "ops-conduit",
) -> object:
    return SimpleNamespace(
        origin_spellbook_id="ops-spellbook",
        frame_name="ops",
        owner_conduit_id=owner_conduit_id,
        spell_id=spell_id,
        spell_index_id=spell_index_id,
        spell_name="OpsSpell",
        binding_name="ops_spell",
    )


def _make_descriptor() -> object:
    return SimpleNamespace(
        frame_overview=SimpleNamespace(frame_name="ops"),
        frame_handle=None,
        conduit_records_by_id={},
        spell_records_by_key={},
    )


class _Viewer:
    def __init__(self) -> None:
        self.default_view_frame_name = "ops"
        self.descriptor = _make_descriptor()
        self.compiled_access_surface = SimpleNamespace(
            command_frame_enabled=True,
            enabled_conduit_ids=tuple(),
            enabled_spell_index_ids=tuple(),
        )
        self.frame_links = []

    def execute_method(self, method_name: str, *, frame_name: str = None):
        assert method_name == "list_targets"
        return list(self.frame_links)

    def _get_required_frame_descriptor(self, frame_name: str) -> object:
        return self.descriptor

    def _get_required_conduit_record(
        self,
        source_id: str,
        *,
        frame_name: str = None,
    ) -> tuple[str, object]:
        return frame_name or "ops", self.descriptor.conduit_records_by_id[source_id]

    def _get_required_spell_record(
        self,
        source_id: str,
        *,
        frame_name: str = None,
    ) -> tuple[str, object]:
        return frame_name or "ops", self.descriptor.spell_records_by_key[source_id]

    def _get_required_compiled_access_surface(self, frame_name: str) -> object:
        return self.compiled_access_surface


def _make_command_system(
    *,
    target: object = None,
    memory_system: object = None,
) -> tuple[CommandSystem, _Viewer, object]:
    viewer = _Viewer()
    workstation = SimpleNamespace(
        get_target=lambda: target,
        bind_object=lambda name, value, weak_ref=None: None,
        bind_attribute=lambda name, value, weak_ref=None: None,
        bind_method=lambda name, value, weak_ref=None: None,
    )
    selected_target_ids = []
    command_projection = SimpleNamespace(
        frame_descriptor=viewer.descriptor,
        compiled_access_surface=viewer.compiled_access_surface,
    )

    def _get_selected_target_link_for_command(*, frame_name=None):
        selected_frame_name = frame_name or viewer.default_view_frame_name
        if selected_frame_name is None:
            raise ValueError("RiftSpace has no default selected frame.")
        if len(selected_target_ids) == 0:
            raise ValueError(
                "RiftSpace has no selected target in frame '{0}'.".format(
                    selected_frame_name
                )
            )
        if len(selected_target_ids) > 1:
            raise ValueError(
                "RiftSpace selected target set is ambiguous in frame '{0}'.".format(
                    selected_frame_name
                )
            )
        for frame_link in viewer.frame_links:
            if frame_link.link_id == selected_target_ids[0]:
                return frame_link
        raise ValueError(
            "Selected target '{0}' was not found in frame '{1}'.".format(
                selected_target_ids[0],
                selected_frame_name,
            )
        )

    space = SimpleNamespace(
        space_id="space-1",
        get_required_frame_viewer=lambda: viewer,
        list_selected_target_ids=lambda frame_name: tuple(selected_target_ids),
        get_default_runtime_frame_name=lambda: viewer.default_view_frame_name,
        get_required_command_projection=lambda frame_name: command_projection,
        get_selected_target_link_for_command=_get_selected_target_link_for_command,
        rift_gate=None,
        memory_system=memory_system,
    )
    command_system = CommandSystem(space=space, workstation=workstation)
    return command_system, viewer, selected_target_ids


def test_command_system_init_cleanup_and_property_guardrails() -> None:
    with pytest.raises(TypeError, match="space cannot be None"):
        CommandSystem(space=None, workstation=object())

    with pytest.raises(TypeError, match="workstation cannot be None"):
        CommandSystem(space=SimpleNamespace(space_id="space-1"), workstation=None)

    command_system, _, _ = _make_command_system()

    assert isinstance(command_system.command_system_id, str)
    assert command_system.owner_space_id == "space-1"

    command_system.cleanup()
    command_system.cleanup()

    assert command_system.cleaned is True


def test_command_system_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _RecheckLock:
        def __init__(self, command_system: CommandSystem) -> None:
            self._command_system = command_system

        def __enter__(self):
            self._command_system._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    command_system, _, _ = _make_command_system()
    original_id = command_system._command_system_id
    command_system._lock = _RecheckLock(command_system)

    command_system.cleanup()

    assert command_system._command_system_id == original_id
    assert command_system._lock is not None


def test_command_system_selected_target_guardrails_and_record_runtime_branches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command_system, viewer, selected_target_ids = _make_command_system()

    selected_target_ids[:] = ["a", "b"]
    with pytest.raises(ValueError, match="selected target set is ambiguous"):
        command_system.get_selected_target_link()

    selected_target_ids[:] = ["missing"]
    with pytest.raises(ValueError, match="Selected target 'missing' was not found"):
        command_system.get_selected_target_link()

    frame_link = SimpleNamespace(source_kind="frame", frame_name="ops", source_id="ops-frame")
    monkeypatch.setattr(
        type(command_system),
        "get_selected_target_link",
        lambda self, *, frame_name=None: frame_link,
    )
    viewer.descriptor.frame_overview = None
    with pytest.raises(ValueError, match="has no published frame overview"):
        command_system.get_selected_target_record()
    with pytest.raises(ValueError, match="has no live frame handle"):
        command_system.get_selected_target_runtime_object()

    viewer.descriptor.conduit_records_by_id["ops-conduit"] = _make_conduit_record()
    conduit_link = SimpleNamespace(
        source_kind="conduit",
        frame_name="ops",
        source_id="ops-conduit",
    )
    monkeypatch.setattr(
        type(command_system),
        "get_selected_target_link",
        lambda self, *, frame_name=None: conduit_link,
    )
    viewer.compiled_access_surface.enabled_conduit_ids = ("ops-conduit",)
    conduit_object = object()
    monkeypatch.setattr(
        type(command_system),
        "get_conduit_by_id",
        lambda self, conduit_id, *, frame_name=None: conduit_object,
    )
    assert command_system.get_selected_target_record() is viewer.descriptor.conduit_records_by_id["ops-conduit"]
    assert command_system.get_selected_target_runtime_object() is conduit_object

    spell_record = _make_spell_record()
    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-1"] = spell_record
    spell_link = SimpleNamespace(
        source_kind="spell",
        frame_name="ops",
        source_id="ops-spellbook:sha-1",
    )
    monkeypatch.setattr(
        type(command_system),
        "get_selected_target_link",
        lambda self, *, frame_name=None: spell_link,
    )
    viewer.compiled_access_surface.enabled_spell_index_ids = ("lineage-1",)
    spell_object = object()
    monkeypatch.setattr(
        type(command_system),
        "get_spell_by_source_id",
        lambda self, spell_source_id, *, frame_name=None: spell_object,
    )
    assert command_system.get_selected_target_record() is spell_record
    assert command_system.get_selected_target_runtime_object() is spell_object

    monkeypatch.setattr(
        type(command_system),
        "get_selected_target_link",
        lambda self, *, frame_name=None: SimpleNamespace(
            source_kind="mystery",
            frame_name="ops",
            source_id="mystery-1",
        ),
    )
    with pytest.raises(ValueError, match="Unsupported selected target kind 'mystery'"):
        command_system.get_selected_target_record()
    with pytest.raises(ValueError, match="Unsupported selected target kind 'mystery'"):
        command_system.get_selected_target_runtime_object()


def test_command_system_delete_cluster_and_target_getter_guardrails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = SimpleNamespace(status="ready", not_callable="value")
    command_system, _, _ = _make_command_system(target=target)
    deleted_cluster_names = []
    conduit = SimpleNamespace(
        delete_cluster=lambda cluster_name: deleted_cluster_names.append(cluster_name)
    )
    monkeypatch.setattr(
        type(command_system),
        "get_conduit_by_id",
        lambda self, conduit_id, *, frame_name=None: conduit,
    )

    command_system.delete_cluster("ops-conduit", "ops-cluster")

    assert deleted_cluster_names == ["ops-cluster"]

    with pytest.raises(ValueError, match="attribute_name cannot be empty"):
        command_system.get_target_attribute("")
    with pytest.raises(ValueError, match="method_name cannot be empty"):
        command_system.get_target_method("")
    with pytest.raises(RuntimeError, match="Target attribute 'not_callable' is not callable"):
        command_system.get_target_method("not_callable")


def test_command_system_conduit_lookup_reports_missing_lesser_conduit_and_name_miss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command_system, viewer, _ = _make_command_system()
    viewer.compiled_access_surface.enabled_conduit_ids = ("missing-lesser",)
    monkeypatch.setattr(
        type(command_system),
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: (_ for _ in ()).throw(
                ValueError("missing")
            ),
            _aetheric_frames={
                "ops": SimpleNamespace(
                    _conduits={
                        "root-1": SimpleNamespace(_conduit_ward=None),
                    }
                )
            },
        ),
    )

    with pytest.raises(ValueError, match="Conduit id 'missing-lesser' was not found in frame 'ops'"):
        command_system.get_conduit_by_id("missing-lesser")

    assert command_system.find_conduit_id_by_name("missing", frame_name="ops") is None


def test_command_system_find_conduit_id_by_name_reraises_non_missing_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command_system, _, _ = _make_command_system()
    monkeypatch.setattr(
        type(command_system),
        "_get_required_published_conduit_id_by_name",
        lambda self, conduit_name, *, frame_name: (_ for _ in ()).throw(
            ValueError("Conduit name '{0}' is ambiguous in frame '{1}'.".format(
                conduit_name,
                frame_name,
            ))
        ),
    )

    with pytest.raises(ValueError, match="is ambiguous in frame 'ops'"):
        command_system.find_conduit_id_by_name("root", frame_name="ops")


def test_command_system_spell_lookup_guardrails_and_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _SpellIndex:
        def __init__(self, version_id: str) -> None:
            self._version_id = version_id

        def has_version(self, version_id: str) -> bool:
            return self._version_id == version_id

    command_system, viewer, _ = _make_command_system()

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
        match="was not found in the owner spellbooks for frame 'ops'",
    ):
        command_system.get_spell_by_index_id("lineage-1")

    monkeypatch.setattr(
        type(command_system),
        "_aether",
        SimpleNamespace(
            _get_conduit_by_spell_id=lambda spell_id, frame_name: SimpleNamespace(
                _spellbook=None
            )
        ),
    )
    with pytest.raises(ValueError, match="has no spellbook"):
        command_system.get_spell_by_id("sha-1")

    monkeypatch.setattr(
        type(command_system),
        "_aether",
        SimpleNamespace(
            _get_conduit_by_spell_id=lambda spell_id, frame_name: SimpleNamespace(
                _spellbook=SimpleNamespace(
                    _spells={_SpellIndex("other-version"): object()},
                )
            )
        ),
    )
    with pytest.raises(ValueError, match="was not found in the owner spellbook"):
        command_system.get_spell_by_id("sha-1")


def test_command_system_internal_helper_validation_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command_system, viewer, _ = _make_command_system()

    viewer.default_view_frame_name = None
    with pytest.raises(ValueError, match="has no default selected frame"):
        command_system._resolve_selected_target_ids()
    with pytest.raises(ValueError, match="has no default runtime frame"):
        command_system._resolve_runtime_frame_name(None)

    viewer.default_view_frame_name = "ops"
    viewer.descriptor.conduit_records_by_id["ops-conduit"] = _make_conduit_record(
        conduit_id="ops-conduit",
        conduit_name="root",
    )
    viewer.descriptor.conduit_records_by_id["shadow-conduit"] = _make_conduit_record(
        conduit_id="shadow-conduit",
        conduit_name="root",
    )
    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-1"] = _make_spell_record(
        spell_index_id="lineage-1",
    )
    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-1-shadow"] = _make_spell_record(
        spell_id="sha-1",
        spell_index_id="lineage-2",
    )

    with pytest.raises(ValueError, match="conduit_name cannot be empty"):
        command_system._get_required_published_conduit_id_by_name(
            "",
            frame_name="ops",
        )
    with pytest.raises(ValueError, match="was not found in frame 'ops'"):
        command_system._get_required_published_conduit_id_by_name(
            "missing",
            frame_name="ops",
        )
    with pytest.raises(ValueError, match="is ambiguous in frame 'ops'"):
        command_system._get_required_published_conduit_id_by_name(
            "root",
            frame_name="ops",
        )

    with pytest.raises(ValueError, match="spell_id cannot be empty"):
        command_system._get_required_published_spell_index_id_by_spell_id(
            "",
            frame_name="ops",
        )
    with pytest.raises(ValueError, match="Spell id 'missing' was not found in frame 'ops'"):
        command_system._get_required_published_spell_index_id_by_spell_id(
            "missing",
            frame_name="ops",
        )
    with pytest.raises(ValueError, match="Spell id 'sha-1' is ambiguous in frame 'ops'"):
        command_system._get_required_published_spell_index_id_by_spell_id(
            "sha-1",
            frame_name="ops",
        )

    monkeypatch.setattr(
        type(command_system),
        "_aether",
        SimpleNamespace(_aetheric_frames={}),
    )
    with pytest.raises(ValueError, match="Aetheric frame 'ops' does not exist"):
        command_system._get_required_runtime_frame("ops")


def test_command_system_acl_helper_and_method_store_binding_paths() -> None:
    command_system, viewer, _ = _make_command_system()
    viewer.descriptor.conduit_records_by_id["ops-conduit"] = _make_conduit_record()
    viewer.descriptor.spell_records_by_key["ops-spellbook:sha-1"] = _make_spell_record()
    viewer.compiled_access_surface.enabled_conduit_ids = ("ops-conduit",)
    viewer.compiled_access_surface.enabled_spell_index_ids = ("lineage-1",)

    command_system._assert_selected_target_command_enabled(
        SimpleNamespace(
            source_kind="conduit",
            source_id="ops-conduit",
            frame_name="ops",
        )
    )
    command_system._assert_selected_target_command_enabled(
        SimpleNamespace(
            source_kind="spell",
            source_id="ops-spellbook:sha-1",
            frame_name="ops",
        )
    )

    bound_methods = []
    command_system._workstation = SimpleNamespace(
        bind_object=lambda name, value, weak_ref=None: None,
        bind_attribute=lambda name, value, weak_ref=None: None,
        bind_method=lambda name, value, weak_ref=None: bound_methods.append(
            (name, value, weak_ref)
        ),
    )
    command_system._bind_result(
        bind_as_name="runner",
        bind_as_store="methods",
        value="sentinel",
        bind_result_weak_ref=False,
    )
    assert bound_methods == [("runner", "sentinel", False)]

    with pytest.raises(ValueError, match="Unsupported workstation store 'unknown'"):
        command_system._bind_result(
            bind_as_name="runner",
            bind_as_store="unknown",
            value="sentinel",
        )


def test_command_system_emits_one_memory_for_top_level_public_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    memory_system = RiftMemorySystem(rift_id="rift-1", space_type="static")
    received_memories = []
    memory_system.register_memory_callback(lambda memory: received_memories.append(memory))
    command_system, viewer, _ = _make_command_system(memory_system=memory_system)
    conduit = SimpleNamespace(create_cluster=lambda cluster_name: None)

    viewer.descriptor.conduit_records_by_id["ops-conduit"] = _make_conduit_record()
    viewer.compiled_access_surface.enabled_conduit_ids = ("ops-conduit",)
    monkeypatch.setattr(
        type(command_system),
        "_aether",
        SimpleNamespace(
            get_conduit_by_id=lambda conduit_id, frame_name: conduit,
        ),
    )

    command_system.create_cluster("ops-conduit", "ops-cluster", frame_name="ops")

    assert len(received_memories) == 1
    assert received_memories[0].frame_name == "ops"
    assert received_memories[0].action_name == "create_cluster"
    assert received_memories[0].step_counter == 1
    assert received_memories[0].metadata["surface"] == "command"
    assert received_memories[0].metadata["command_system_id"] == command_system.command_system_id


def test_command_system_emits_memory_for_target_method_execution() -> None:
    memory_system = RiftMemorySystem(rift_id="rift-1", space_type="static")
    received_memories = []
    memory_system.register_memory_callback(lambda memory: received_memories.append(memory))
    target = SimpleNamespace(run=lambda value: "done:{0}".format(value))
    command_system, viewer, _ = _make_command_system(
        target=target,
        memory_system=memory_system,
    )

    result = command_system.execute_target_method("run", "job-1")

    assert result == "done:job-1"
    assert len(received_memories) == 1
    assert received_memories[0].frame_name == "ops"
    assert received_memories[0].action_name == "execute_target_method"
