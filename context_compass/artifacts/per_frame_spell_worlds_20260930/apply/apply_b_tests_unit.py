"""Part B red tests, unit level: the custody key on crystals, record, facade verbs, impact, retarget, stage 1."""
import sys

from apply_support import ApplySession

session = ApplySession(sys.argv[1])

# --- Spell doubles gain the owning frame (SpellCrystal now reads spell.aetheric_frame). ---
session.insert_after("tests/mocks/crystallizer/spell_crystal_harness.py", r'''        """Mirror the native bind policy and custody fields consumed by SpellCrystal."""
        self.spell_id = spell_id
        self.resolvable = True
''', r'''        # The owning frame (0.2.8214): per-frame spell ids key custody "<spell_id>@<frame>".
        self.aetheric_frame = "default"
''')
session.insert_after("tests/unit/melder/crystallizer/test_crystallizer.py", r'''            None.
        """
        self.spell_id = spell_id
''', r'''        self.aetheric_frame = "default"
''')

# --- Custody stubs expose the record key the profile now reads. ---
for relative in (
        "tests/unit/melder/crystallizer/persistence/test_persistence_system.py",
        "tests/unit/melder/crystallizer/persistence/test_persistence_twins.py",
        "tests/unit/melder/crystallizer/test_crystallizer_profile_facades.py",
        "tests/unit/melder/crystallizer/test_crystallizer_record_sinks.py",
        "tests/component/melder/crystallizer/test_crystallizer_record_component.py",
        "tests/component/melder/crystallizer/test_persistence_system_component.py",
):
    session.replace(relative, r'''        self.id = spell_id
        self.spellbook_id = spellbook_id
''', r'''        self.id = spell_id
        self.custody_key = spell_id  # the record key (the bare spell id under process-wide ids)
        self.spellbook_id = spellbook_id
''')
session.replace("tests/component/melder/crystallizer/test_crystallizer_cadence_soak_component.py", r'''        self.id = spell_id
        self.spellbook_id = None
''', r'''        self.id = spell_id
        self.custody_key = spell_id  # the record key (the bare spell id under process-wide ids)
        self.spellbook_id = None
''')

# --- PersistenceProfile: frame-scoped custody. ---
PROFILE = "tests/unit/melder/crystallizer/persistence/test_persistence_profile.py"
session.insert_after(PROFILE, r'''from melder.crystallizer.crystals.spellbook_crystal import (
    SpellbookCrystal,
)
''', r'''from melder.crystallizer.crystals.spell_index_crystal import SpellIndexCrystal
''')
session.replace(PROFILE, r'''    Contract:
        - `id` is the spell SHA identity (SpellCrystal.id contract).
        - `spellbook_id` is the parent edge the subtree sweeps match on.
        - `cleaned`/`cleanup()` mirror the Cleanable surface.
        - `describe()` returns detached plain data for segment capture.
    """

    def __init__(self, spell_id, spellbook_id=None):
        self.id = spell_id
        self.spellbook_id = spellbook_id
        self.cleaned = False
''', r'''    Contract:
        - `id` is the spell SHA identity (SpellCrystal.id contract).
        - `custody_key` is the record key (SpellCrystal.custody_key contract): the spell id, or
          "<spell_id>@<frame>" for a crystal recorded under per-frame spell ids (0.2.8214).
        - `spellbook_id` is the parent edge the subtree sweeps match on.
        - `cleaned`/`cleanup()` mirror the Cleanable surface.
        - `describe()` returns detached plain data for segment capture.
    """

    def __init__(self, spell_id, spellbook_id=None, frame_name=None):
        self.id = spell_id
        self.custody_key = spell_id if frame_name is None else f"{spell_id}@{frame_name}"
        self.spellbook_id = spellbook_id
        self.cleaned = False
''')
session.replace(PROFILE, r'''    assert payloads["spell_activity"]["sha-a"] == {
        "spell_id": "sha-a", "active": False, "custody_present": False,
    }
    assert payloads["spell_removed"]["sha-a"] == {
        "spell_id": "sha-a", "removed": True,
    }
''', r'''    assert payloads["spell_activity"]["sha-a"] == {
        "spell_id": "sha-a", "custody_key": "sha-a", "active": False, "custody_present": False,
    }
    assert payloads["spell_removed"]["sha-a"] == {
        "spell_id": "sha-a", "custody_key": "sha-a", "removed": True,
    }
''')
session.append(PROFILE, r'''

def _record_one_class_in_two_frames(profile):
    """Record one spell id bound in two frames (two Books) the way per-frame ids key it; return both copies."""
    first = _StubSpellCrystal("sha", "book-a", frame_name="tenant_a")
    second = _StubSpellCrystal("sha", "book-b", frame_name="tenant_b")
    profile.record_spell_crystal(first, active=True)
    profile.record_spell_crystal(second, active=True)
    return first, second


def test_one_spell_id_in_two_frames_keeps_both_custody_entries():
    """
    Purpose:
        Verify custody keyed per frame: one spell id bound in two frames records twice (0.2.8214).
    Contract:
        Neither copy displaces the other; describe_spell_crystals is keyed by custody key; a lookup naming a frame
        answers that frame's copy, a bare spell id answers the lowest key, and a full key answers exactly.
    Returns:
        None.
    Raises:
        AssertionError: If one frame's copy displaces the other or a lookup picks the wrong copy.
    """
    profile = PersistenceProfile("p")
    first, second = _record_one_class_in_two_frames(profile)
    assert first.cleaned is False and second.cleaned is False
    assert profile.describe()["spell_crystal_count"] == 2
    assert sorted(profile.describe_spell_crystals()) == ["sha@tenant_a", "sha@tenant_b"]
    assert profile.get_spell_crystal("sha", frame_name="tenant_b") is second
    assert profile.get_spell_crystal("sha") is first
    assert profile.get_spell_crystal("sha@tenant_b") is second


def test_frame_lookup_never_answers_another_frames_copy():
    """
    Purpose:
        Verify a lookup that names a frame is exact.
    Contract:
        A frame holding no copy raises KeyError although another frame holds one; a bare (process-wide) key still
        answers a lookup that names a frame, because the frame is not part of that key.
    Returns:
        None.
    Raises:
        AssertionError: If a frame-scoped lookup falls back to another frame's copy.
    """
    profile = PersistenceProfile("p")
    _record_one_class_in_two_frames(profile)
    with pytest.raises(KeyError):
        profile.get_spell_crystal("sha", frame_name="tenant_c")
    bare = _StubSpellCrystal("sha-bare", "book-a")
    profile.record_spell_crystal(bare, active=True)
    assert profile.get_spell_crystal("sha-bare", frame_name="tenant_a") is bare


def test_activity_and_removal_address_one_frames_copy():
    """
    Purpose:
        Verify park/promote and removal move or evict one frame's copy only.
    Contract:
        Parking "sha@tenant_a" leaves tenant_b's copy active; removing "sha@tenant_b" cleans only that copy.
    Returns:
        None.
    Raises:
        AssertionError: If a verb reaches the other frame's copy.
    """
    profile = PersistenceProfile("p")
    first, second = _record_one_class_in_two_frames(profile)
    profile.record_spell_activity("sha@tenant_a", active=False)
    summary = profile.describe()
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 1
    profile.remove_spell_crystal("sha@tenant_b")
    assert second.cleaned is True and first.cleaned is False
    assert profile.get_spell_crystal("sha", frame_name="tenant_a") is first


def test_segment_payloads_name_the_spell_and_its_custody_key():
    """
    Purpose:
        Verify activity and removal tombstones carry both names.
    Contract:
        Entries journal under the custody key; spell_activity and spell_removed payloads carry the bare "spell_id"
        (read from the key once the crystal is gone) and the "custody_key".
    Returns:
        None.
    Raises:
        AssertionError: If a tombstone loses either name.
    """
    profile = PersistenceProfile("p")
    profile.record_spell_crystal(_StubSpellCrystal("sha", "book-a", frame_name="tenant_a"), active=True)
    profile.record_spell_activity("sha@tenant_a", active=False)
    profile.remove_spell_crystal("sha@tenant_a")
    payloads, entries, _rng = profile.capture_segment_since(0)
    assert [entry[2] for entry in entries] == ["sha@tenant_a", "sha@tenant_a", "sha@tenant_a"]
    assert payloads["spell_activity"]["sha@tenant_a"] == {
        "spell_id": "sha", "custody_key": "sha@tenant_a", "active": False, "custody_present": False,
    }
    assert payloads["spell_removed"]["sha@tenant_a"] == {
        "spell_id": "sha", "custody_key": "sha@tenant_a", "removed": True,
    }


def test_index_graft_takes_each_members_custody_from_the_index_book():
    """
    Purpose:
        Verify a graft reads its members' custody from the index's own Book.
    Contract:
        With one spell id recorded in two frames, the graft of tenant_b's index carries tenant_b's copy; the members
        map stays keyed by spell id, because one index lives in one Book.
    Returns:
        None.
    Raises:
        AssertionError: If the graft picks up another Book's copy.
    """
    profile = PersistenceProfile("p")
    _record_one_class_in_two_frames(profile)
    profile.record(SpellIndexCrystal(
        index_id="index-b", spellbook_id="book-b", selected_spell_id="sha", member_spell_ids=["sha"],
    ))
    record = profile.capture_index_graft("index-b")
    assert list(record["members"]) == ["sha"]
    assert record["members"]["sha"]["payload"]["spellbook_id"] == "book-b"
    assert record["members_without_custody"] == []
''')

# --- PersistenceSystem: pass-through of keys and the lookup frame. ---
session.append("tests/unit/melder/crystallizer/persistence/test_persistence_system.py", r'''

def test_spell_custody_verbs_route_frame_scoped_keys_to_the_active_profile():
    """
    Purpose:
        Verify the system passes custody keys and the lookup frame through to the active profile (0.2.8214).
    Contract:
        Two copies of one spell id recorded under per-frame keys coexist; activity and removal address one key;
        get_spell_crystal with a frame answers that frame's copy.
    Returns:
        None.
    Raises:
        AssertionError: If a verb loses the key or the frame on the way down.
    """
    system = PersistenceSystem()
    first = _StubSpellCrystal("sha", "book-a")
    first.custody_key = "sha@tenant_a"
    second = _StubSpellCrystal("sha", "book-b")
    second.custody_key = "sha@tenant_b"
    system.record_spell_crystal(first, active=True)
    system.record_spell_crystal(second, active=True)
    system.record_spell_activity("sha@tenant_a", active=False)
    assert system.get_spell_crystal("sha", frame_name="tenant_a") is first
    system.remove_spell_crystal("sha@tenant_b")
    assert second.cleaned is True and first.cleaned is False
    assert sorted(system.describe_spell_crystals()) == ["sha@tenant_a"]
    system.cleanup()
''')

# --- Crystallizer facade: key-aware verbs. ---
SINKS = "tests/unit/melder/crystallizer/test_crystallizer_record_sinks.py"
session.replace(SINKS, r'''from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
''', r'''from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_utility_system import AetherUtilitySystem
''')
session.append(SINKS, r'''

def _per_frame_ids():
    """Install per-frame spell ids on the fixture Aether before any frame exists."""
    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    policy.activate()
    Aether().activate(policy)


def _frame_scoped_stub(spell_id, spellbook_id, frame_name):
    """Build one custody stub keyed the way per-frame ids key it ("<spell_id>@<frame>")."""
    crystal = _StubSpellCrystal(spell_id, spellbook_id)
    crystal.custody_key = f"{spell_id}@{frame_name}"
    return crystal


def test_per_frame_spell_verbs_require_the_frame():
    """
    Purpose:
        Verify the key-aware verbs refuse an ambiguous address under per-frame ids (0.2.8214).
    Contract:
        emit_spell_activity and emit_spell_removed raise ValueError naming frame_name when none is given, because a
        spell id alone does not say which frame's copy is meant; the record is untouched.
    Returns:
        None.
    Raises:
        AssertionError: If a frameless per-frame emit is accepted.
    """
    _per_frame_ids()
    crystallizer = _activated_crystallizer()
    crystallizer.emit_spell_crystal(_frame_scoped_stub("sha", "book-a", "tenant_a"), active=True)
    with pytest.raises(ValueError, match="frame_name"):
        crystallizer.emit_spell_activity("sha", active=False)
    with pytest.raises(ValueError, match="frame_name"):
        crystallizer.emit_spell_removed("sha")
    summary = crystallizer.describe_profile()
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 0


def test_per_frame_spell_verbs_address_one_frames_copy():
    """
    Purpose:
        Verify park and removal under per-frame ids touch only the named frame's copy.
    Contract:
        Parking in tenant_a moves tenant_a's copy to the inactive location; removing in tenant_b cleans tenant_b's
        copy; get_spell_crystal with a frame answers that frame's copy.
    Returns:
        None.
    Raises:
        AssertionError: If a verb reaches the other frame's copy.
    """
    _per_frame_ids()
    crystallizer = _activated_crystallizer()
    first = _frame_scoped_stub("sha", "book-a", "tenant_a")
    second = _frame_scoped_stub("sha", "book-b", "tenant_b")
    crystallizer.emit_spell_crystal(first, active=True)
    crystallizer.emit_spell_crystal(second, active=True)
    crystallizer.emit_spell_activity("sha", active=False, frame_name="tenant_a")
    summary = crystallizer.describe_profile()
    assert summary["spell_crystal_count"] == 1
    assert summary["inactive_spell_crystal_count"] == 1
    crystallizer.emit_spell_removed("sha", frame_name="tenant_b")
    assert second.cleaned is True and first.cleaned is False
    assert crystallizer.get_spell_crystal("sha", frame_name="tenant_a") is first


def test_process_wide_spell_verbs_ignore_the_frame():
    """
    Purpose:
        Verify the frame is optional, and ignored, under process-wide ids.
    Contract:
        The key is the bare spell id, so a park and a removal that name a frame address the one recorded copy.
    Returns:
        None.
    Raises:
        AssertionError: If the frame changes the address under process-wide ids.
    """
    crystallizer = _activated_crystallizer()
    crystal = _StubSpellCrystal("sha-a", "book-1")
    crystallizer.emit_spell_crystal(crystal, active=True)
    crystallizer.emit_spell_activity("sha-a", active=False, frame_name="tenant_a")
    assert crystallizer.describe_profile()["inactive_spell_crystal_count"] == 1
    crystallizer.emit_spell_removed("sha-a", frame_name="tenant_a")
    assert crystal.cleaned is True
    assert crystallizer.describe_profile()["inactive_spell_crystal_count"] == 0
''')

# --- SpellCrystal: frame and custody key. ---
SPELL_CRYSTAL = "tests/unit/melder/crystallizer/test_spell_crystal.py"
session.replace(SPELL_CRYSTAL, r'''from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.synthetic_module import SyntheticModule
''', r'''from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.synthetic_module import SyntheticModule
''')
session.append(SPELL_CRYSTAL, r'''

def _keyed_service_module(module_name: str) -> SyntheticModule:
    """Publish one trivial synthetic module for a KeyedService target; the caller cleans it and pops sys.modules."""
    module = SyntheticModule(
        module_name=module_name,
        spell_crystal_id="keyed-crystal",
        source_text="class KeyedService:\n    pass\n",
        source_sha256="keyed-sha",
        binding_signature="keyed-binding",
    )
    sys.modules[module_name] = module
    return module


def _keyed_spell(spell_id: str, module_name: str, frame_name: str) -> DummySpell:
    """Build one spell double bound in `frame_name` whose target lives in the keyed synthetic module."""
    spell = DummySpell(spell_id, type("KeyedService", (), {"__module__": module_name}))
    spell.aetheric_frame = frame_name
    return spell


def _install_regime(process_wide: bool) -> None:
    """Configure and activate the fixture's Aether with one spell-id regime before any frame exists."""
    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(process_wide)
    policy.activate()
    Aether().activate(policy)


def test_spell_crystal_default_custody_key_is_the_spell_id_and_records_the_frame() -> None:
    """
    Verify the process-wide key (0.2.8214): the custody key is the bare spell id, and the frame rides along.

    Returns:
        None.
    """
    module_name = "test.keyed_custody_default"
    module = _keyed_service_module(module_name)
    crystal = None
    try:
        crystal = SpellCrystal(_keyed_spell("sha-keyed", module_name, "tenant_a"))
        assert crystal.custody_key == "sha-keyed"
        assert crystal.frame_name == "tenant_a"
        description = crystal.describe()
        assert description["custody_key"] == "sha-keyed"
        assert description["frame_name"] == "tenant_a"
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)


def test_spell_crystal_per_frame_custody_key_composes_the_frame() -> None:
    """
    Verify the per-frame key: "<spell_id>@<frame>", so one spell bound in two frames records twice.

    Returns:
        None.
    """
    module_name = "test.keyed_custody_per_frame"
    module = _keyed_service_module(module_name)
    crystal = None
    try:
        crystal = SpellCrystal(_keyed_spell("sha-keyed", module_name, "tenant_b"), per_frame_custody=True)
        assert crystal.id == "sha-keyed"
        assert crystal.custody_key == "sha-keyed@tenant_b"
        assert crystal.describe()["custody_key"] == "sha-keyed@tenant_b"
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)


def test_custody_key_statics_round_trip_including_an_at_sign_in_the_frame() -> None:
    """
    Verify the key grammar: composition appends "@<frame>", and parsing splits at the FIRST "@", because a spell id
    (a SHA256 hex digest) never holds one while a frame name may.

    Returns:
        None.
    """
    assert SpellCrystal.compose_custody_key("abc", "tenant@eu") == "abc@tenant@eu"
    assert SpellCrystal.spell_id_of_custody_key("abc@tenant@eu") == "abc"
    assert SpellCrystal.spell_id_of_custody_key("abc") == "abc"


def test_facade_keys_custody_per_frame_under_per_frame_ids() -> None:
    """
    Verify the facade reads the regime: under per-frame ids `create_spell_crystal` builds a frame-scoped key.

    Returns:
        None.
    """
    _install_regime(False)
    module_name = "test.keyed_custody_facade_per_frame"
    module = _keyed_service_module(module_name)
    crystal = None
    try:
        crystal = _create_activated_crystallizer().create_spell_crystal(
            _keyed_spell("sha-keyed", module_name, "tenant_a")
        )
        assert crystal.custody_key == "sha-keyed@tenant_a"
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)


def test_facade_keeps_bare_keys_under_process_wide_ids() -> None:
    """
    Verify default worlds keep their record keys: under process-wide ids the facade builds the bare spell id key.

    Returns:
        None.
    """
    _install_regime(True)
    module_name = "test.keyed_custody_facade_process_wide"
    module = _keyed_service_module(module_name)
    crystal = None
    try:
        crystal = _create_activated_crystallizer().create_spell_crystal(
            _keyed_spell("sha-keyed", module_name, "tenant_a")
        )
        assert crystal.custody_key == "sha-keyed"
        assert crystal.frame_name == "tenant_a"
    finally:
        if crystal is not None:
            crystal.cleanup()
        module.cleanup()
        sys.modules.pop(module_name, None)
''')

# --- ImpactEngine: a spell id answers through frame-scoped keys. ---
session.append("tests/unit/melder/crystallizer/crystal_analysis/test_impact_engine.py", r'''

def test_spell_radius_answers_a_spell_id_through_frame_scoped_keys():
    """
    Contract (0.2.8214): a record kept under per-frame ids keys custody "<spell_id>@<frame>"; the spell radius still
    answers the bare spell id (first matching key in sorted order) and lists every frame's copy, while an unknown
    id still answers unknown_spell.
    """
    world = {
        "sha-alpha@tenant_a": _crystal(
            spell_id="sha-alpha",
            root_module="userland.alpha",
            modules=["userland.alpha"],
            dependencies={},
        ),
        "sha-alpha@tenant_b": _crystal(
            spell_id="sha-alpha",
            root_module="userland.alpha",
            modules=["userland.alpha"],
            dependencies={},
            spellbook_id="book-2",
        ),
    }
    engine = ImpactEngine(world)
    try:
        radius = engine.blast_radius_of_spell("sha-alpha")
        assert radius["unknown_spell"] is False
        assert radius["spell"] == "sha-alpha"
        assert radius["root_module"] == "userland.alpha"
        assert radius["affected_spells"] == ["sha-alpha@tenant_a", "sha-alpha@tenant_b"]
        assert radius["affected_spellbooks"] == ["book-1", "book-2"]
        assert engine.blast_radius_of_spell("sha-missing")["unknown_spell"] is True
    finally:
        engine.cleanup()
''')

# --- LoadAdmission retarget: frame-scoped custody keys follow the target frame. ---
session.append("tests/unit/melder/crystallizer/crystal_loader_system/test_crystal_loader_system.py", r'''

def _custody_record(custody_key, spell_id):
    """A retargetable formation holding one custody entry recorded in frame alpha under `custody_key`."""
    record = _retargetable_record()
    record["payloads"]["spell_crystal"] = {
        custody_key: {
            "id": spell_id, "spellbook_id": "book-1", "frame_name": "alpha",
            "custody_key": custody_key, "custody_location": "active",
        },
    }
    return record


def test_retarget_rekeys_frame_scoped_custody_for_the_target_frame():
    """
    Contract (0.2.8214): a formation recorded under per-frame ids keys custody by frame; retargeting rebuilds each
    frame-scoped key for the target frame, rewrites the payload's frame_name and custody_key, and the minted journal
    names the new key. The caller's record is not mutated.
    """
    record_system = PersistenceSystem()
    admission_plane = LoadAdmission(record_system)
    formation_record = _custody_record("sha-a@alpha", "sha-a")
    try:
        plan = admission_plane.plan_formation_load(formation_record, target_frame_name="beta")
        try:
            window = plan.chain[0]
            custody = window["payloads"]["spell_crystal"]
            assert list(custody) == ["sha-a@beta"]
            assert custody["sha-a@beta"]["id"] == "sha-a"
            assert custody["sha-a@beta"]["frame_name"] == "beta"
            assert custody["sha-a@beta"]["custody_key"] == "sha-a@beta"
            assert [entry[2] for entry in window["journal"] if entry[1] == "spell_crystal"] == ["sha-a@beta"]
            assert list(formation_record["payloads"]["spell_crystal"]) == ["sha-a@alpha"]
        finally:
            plan.cleanup()
    finally:
        admission_plane.cleanup()
        record_system.cleanup()


def test_retarget_keeps_process_wide_custody_keys():
    """
    Contract (0.2.8214): a formation recorded under process-wide ids keys custody by the spell id alone; retargeting
    keeps that key and rewrites only the payload's frame_name.
    """
    record_system = PersistenceSystem()
    admission_plane = LoadAdmission(record_system)
    formation_record = _custody_record("sha-b", "sha-b")
    try:
        plan = admission_plane.plan_formation_load(formation_record, target_frame_name="beta")
        try:
            custody = plan.chain[0]["payloads"]["spell_crystal"]
            assert list(custody) == ["sha-b"]
            assert custody["sha-b"]["frame_name"] == "beta"
            assert custody["sha-b"]["custody_key"] == "sha-b"
        finally:
            plan.cleanup()
    finally:
        admission_plane.cleanup()
        record_system.cleanup()
''')

# --- Restore stage 1: the B refusal; stage 6: per-Book translation. ---
REGIME = "tests/unit/melder/crystallizer/crystal_loader_system/test_restore_spell_id_regime.py"
session.replace(REGIME, r'''    5. a record without the regime reports it missing and rebuilds the default.
"""
''', r'''    5. a record without the regime reports it missing and rebuilds the default;
    6. a host running process-wide ids refuses, before building anything, a per-frame record that binds one spell id
       in two frames (a payload without its own frame is placed in its Book's frame);
    7. recorded-to-live spell translation is kept per Book.
"""
''')
session.replace(REGIME, "from typing import Dict, List, Optional\n", "from typing import Dict, List, Optional, Tuple\n")
session.append(REGIME, r'''

def _one_spell_id_in_two_frames() -> Tuple[List[List[object]], Dict[str, Dict[str, object]]]:
    """Journal rows and payloads of a per-frame world that bound one spell id in two frames (two Books)."""
    journal: List[List[object]] = [
        [2, "spellbook", "book-a"],
        [3, "spellbook", "book-b"],
        [4, "spell_crystal", "sha@tenant_a"],
        [5, "spell_crystal", "sha@tenant_b"],
    ]
    payloads: Dict[str, Dict[str, object]] = {
        "spellbook": {
            "book-a": {"spellbook_id": "book-a", "frame_name": "tenant_a"},
            "book-b": {"spellbook_id": "book-b", "frame_name": "tenant_b"},
        },
        "spell_crystal": {
            "sha@tenant_a": {"id": "sha", "spellbook_id": "book-a", "frame_name": "tenant_a"},
            "sha@tenant_b": {"id": "sha", "spellbook_id": "book-b"},
        },
    }
    return journal, payloads


def _messages(error: BaseException) -> List[str]:
    """Return the messages of one exception and its chained causes."""
    messages: List[str] = []
    current: Optional[BaseException] = error
    while current is not None:
        messages.append(str(current))
        current = current.__cause__ or current.__context__
    return messages


def test_process_wide_host_refuses_a_record_binding_one_spell_id_in_two_frames() -> None:
    """
    A per-frame record that binds one spell id in two frames cannot be rebuilt under the process-wide ids a host
    configured - the second frame's bind would collide. Stage 1 refuses before anything is built (0.2.8214) instead
    of rolling back half a world at stage 6. tenant_b's payload carries no frame, so its Book's frame is used.
    """
    _install(True)
    journal, payloads = _one_spell_id_in_two_frames()
    engine = _engine(_aether_payload(False), extra_journal=journal, extra_payloads=payloads)
    try:
        with pytest.raises(RuntimeError, match="aether_configuration") as raised:
            engine.restore()
        assert any("two frames" in message for message in _messages(raised.value))
        assert "tenant_a" not in Aether().list_frame_names()
        assert "tenant_b" not in Aether().list_frame_names()
    finally:
        engine.cleanup()


def test_spell_translation_is_kept_per_book() -> None:
    """
    Stage 6 keys recorded-to-live spell translation by Book: one spell id rebuilt in two Books may bind to two new
    ids (each Book applies its own receiving policy), and each Book's selections, parked members and contract
    grants must follow its own. No public surface exposes this map, so the engine's helpers are exercised directly.
    """
    engine = _engine(_aether_payload(None))
    try:
        engine._map_spell_identity("book-a", "sha", "sha-live-a")
        engine._map_spell_identity("book-b", "sha", "sha-live-b")
        engine._map_spell_identity("book-c", "sha", "sha")
        assert engine._translate_spell("book-a", "sha") == "sha-live-a"
        assert engine._translate_spell("book-b", "sha") == "sha-live-b"
        assert engine._translate_spell("book-c", "sha") == "sha"
        assert engine._translate_spell("book-d", "sha") == "sha"
    finally:
        engine.cleanup()
''')

long_lines = session.long_added_lines()
if long_lines:
    raise AssertionError("lines over 120:\n" + "\n".join(long_lines))
for path in session.write():
    print(path)
