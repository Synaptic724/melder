"""melder_0, 2026-10-18: categories (c), (d) and (e) of S1's test tranche, part B - spellbook and managed tests.

One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): a second registration of a class is
refused, so each test gives its second registration other code - a `version_of` the class
(tests/_spell_identity_test_support.py), a class of its own, or a module-level class a restore or a graft imports -
and a test that needs one class in two frames installs per-frame spell ids. Release by class follows the class, so two
versions are two classes with a pool each, and one root cannot hold two pools of one class. The reversed premise (d):
the existence and the managed settings move the binding hash, not the spell_id. The process-stability test (e) calls
the inspector with the target alone.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests_apply_s1_s2 import TestApplier

SUPPORT = "tests/_spell_identity_test_support.py"
SUPPORT_IMPORT = "from tests._spell_identity_test_support import version_of\n"
S1_REF = "S1 of EPIC-2026-10-18-spell_identity_is_the_code"

CASE_PARITY = "tests/integration/melder/spellbook/test_binding_name_case_parity_integration.py"
ARTIFACT_OWNERSHIP = "tests/integration/melder/spellbook/test_provider_artifact_ownership.py"
CONTRACT_MORE = "tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_more.py"
MANAGED_TRANSFER = "tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py"
RELEASE = "tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py"
QUANTITY = "tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py"
QUANTITY_POOL = "tests/integration/melder/conduit/test_conduit_integration_managed_quantity_pool.py"
OPTIONS_RECORD = "tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py"
BIND_OPTIONS = "tests/integration/melder/spellbook/test_managed_bind_options_integration.py"
STABILITY = "tests/component/melder/spellbook/test_spell_id_process_stability.py"

PER_FRAME = (
    "    policy = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)\n"
    "    policy.activate()\n"
    "    Aether().activate(policy)\n"
)


def _case_parity(applier: "TestApplier") -> None:
    applier.edit(CASE_PARITY, [
        ("from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration\n",
         "from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration\n"
         + SUPPORT_IMPORT),
        ("    \"\"\"The provider, bound once under \"agents\" and once under \"artificial_intelligence_tools\".\"\"\"\n",
         "    \"\"\"The provider bound under \"agents\"; its namesake under \"artificial_intelligence_tools\" is a version.\"\"\"\n"),
        ("    book.bind(spell=ScanProfile, existence=\"unique\", spellframe=\"agents\", binding_name=\"ScanProfile\")\n"
         "    book.bind(spell=ScanProfile, existence=\"unique\", spellframe=\"artificial_intelligence_tools\",\n"
         "              binding_name=\"ScanProfile\")\n",
         "    book.bind(spell=ScanProfile, existence=\"unique\", spellframe=\"agents\", binding_name=\"ScanProfile\")\n"
         "    # The namesake is other code under the same name, as in the report: one class is one spell\n"
         "    # (" + S1_REF + "), so ScanProfile itself cannot be bound at a second address.\n"
         "    book.bind(spell=version_of(ScanProfile, toolset=\"artificial_intelligence_tools\"), existence=\"unique\",\n"
         "              spellframe=\"artificial_intelligence_tools\", binding_name=\"ScanProfile\")\n"),
    ], "case_parity")


def _artifact_ownership(applier: "TestApplier") -> None:
    applier.edit(ARTIFACT_OWNERSHIP, [
        ("from melder.aether.spellbook.spellbook import Spellbook\n",
         "from melder.aether.spellbook.spellbook import Spellbook\n" + SUPPORT_IMPORT),
        ("    def create_borrower(self, name: str) -> Conduit:\n"
         "        \"\"\"Link and import read access, then bind the required consumer locally.\"\"\"\n",
         "    def create_borrower(self, name: str) -> Conduit:\n"
         "        \"\"\"\n"
         "        Link and import read access, then bind the required consumer locally.\n"
         "\n"
         "        Each borrower binds its own version of ProviderConsumer, named for it: one class is one spell\n"
         "        (" + S1_REF + "), so two borrowers in the frame cannot both bind the class.\n"
         "        \"\"\"\n"),
        ("        borrower.bind(\n"
         "            spell=ProviderConsumer, existence=\"many\",\n"
         "            spellframe=\"consumers\", binding_name=name,\n",
         "        borrower.bind(\n"
         "            spell=version_of(ProviderConsumer, borrower=name), existence=\"many\",\n"
         "            spellframe=\"consumers\", binding_name=name,\n"),
    ], "artifact_ownership")


def _contract_more(applier: "TestApplier") -> None:
    applier.edit_preserving(CONTRACT_MORE, [
        ("from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError\n",
         "from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError\n"
         + SUPPORT_IMPORT),
        ("        - The spell fingerprint composes bind-time facts including the lookup\n"
         "          signature, so the same class under two binding names registers as\n"
         "          two distinct spells; binding no longer collides.\n",
         "        - One class is one spell (" + S1_REF + "):\n"
         "          binding _Repo again under another binding name is refused, so the second\n"
         "          provider is a version of _Repo - its name, other code - under 'secondary'.\n"),
        ("    spellbook.bind(\n"
         "        spell=_Repo,\n"
         "        existence=Existence.unique,\n"
         "        permissions=\"create\",\n"
         "        binding_name=\"secondary\",\n",
         "    spellbook.bind(\n"
         "        spell=version_of(_Repo, provider=\"secondary\"),\n"
         "        existence=Existence.unique,\n"
         "        permissions=\"create\",\n"
         "        binding_name=\"secondary\",\n"),
    ], "contract_more")


REGISTRY_OLD = (
    "def _registry(owner: Conduit, target: Conduit) -> List[Tuple[str, str, int, int]]:\n"
    "    \"\"\"The registry's rows for Session: (spell id, holding root label, count, idle count), sorted.\"\"\"\n"
    "    labels = {owner.id: \"owner\", target.id: \"target\"}\n"
    "    return sorted(\n"
    "        (row[\"spell_id\"], labels.get(row[\"holding_conduit_id\"], row[\"holding_conduit_id\"]), row[\"count\"],\n"
    "         row[\"idle_count\"])\n"
    "        for row in ReleaseManagedSpell().describe(Session)\n"
    "    )\n"
)
REGISTRY_NEW = (
    "def _registry(owner: Conduit, target: Conduit) -> List[Tuple[str, str, int, int]]:\n"
    "    \"\"\"\n"
    "    The registry's rows for Session and its versions: (spell id, holding root label, count, idle count), sorted.\n"
    "\n"
    "    A staged version is a class of its own (one object is one spell), registered under that class, so the rows\n"
    "    of every Session subclass count; a subclass with no live pool adds none.\n"
    "    \"\"\"\n"
    "    labels = {owner.id: \"owner\", target.id: \"target\"}\n"
    "    return sorted(\n"
    "        (row[\"spell_id\"], labels.get(row[\"holding_conduit_id\"], row[\"holding_conduit_id\"]), row[\"count\"],\n"
    "         row[\"idle_count\"])\n"
    "        for cls in (Session, *Session.__subclasses__())\n"
    "        for row in ReleaseManagedSpell().describe(cls)\n"
    "    )\n"
)


def _managed_transfer(applier: "TestApplier") -> None:
    applier.edit(MANAGED_TRANSFER, [
        ("from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration\n",
         "from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration\n"
         + SUPPORT_IMPORT),
        ("        \"\"\"A second disposal step the parked version names, so it is a version of its own (0.2.8254).\"\"\"\n",
         "        \"\"\"A second disposal step the parked version's binding names (its binding, not its version).\"\"\"\n"),
        ("    \"\"\"A `unique` class; a second version differs by its disposal names.\"\"\"\n",
         "    \"\"\"A `unique` class; its staged second version is `version_of(Keeper, version=2)`.\"\"\"\n"),
        ("        target_class: Session (limit 8, disposal \"close\" and \"flush\": a managed spell's settings are not part\n"
         "            of its spell_id since 0.2.8254, so the disposal names make the second version) or Keeper (disposal\n"
         "            \"close\").\n",
         "        target_class: Session (limit 8, disposal \"close\" and \"flush\") or Keeper (disposal \"close\"). The staged\n"
         "            class is `version_of(target_class, version=2)`: one object is one spell (S1 of\n"
         "            EPIC-2026-10-18-spell_identity_is_the_code), so a version is new code under the same name, and its\n"
         "            settings and disposal names are its binding.\n"),
        ("        parked_id = owner.bind_inactive(spell=Session, spell_index=spell_index,\n",
         "        parked_id = owner.bind_inactive(spell=version_of(Session, version=2), spell_index=spell_index,\n"),
        ("        parked_id = owner.bind_inactive(spell=Keeper, spell_index=spell_index, existence=Existence.unique,\n"
         "                                        permissions=\"create\", disposal_method_names=[\"close\"])\n",
         "        parked_id = owner.bind_inactive(spell=version_of(Keeper, version=2), spell_index=spell_index,\n"
         "                                        existence=Existence.unique, permissions=\"create\",\n"
         "                                        disposal_method_names=[\"close\"])\n"),
        ("    Once that version is notched in, a release by class meets three Session pools (the first version's in the\n"
         "    target, the second's in each root), two of them the selected version's, and raises the documented ambiguity; a\n"
         "    release naming the conduit reaches the target's pool.\n",
         "    Once that version is notched in, a release by class meets the second version's two pools - its class is its\n"
         "    own, since one object is one spell - one in each root, both the selected version's, and raises the\n"
         "    documented ambiguity; a release naming the conduit reaches the target's pool.\n"),
        ("    with pytest.raises(ValueError, match=\"is managed by 3 pools\"):\n",
         "    with pytest.raises(ValueError, match=\"is managed by 2 pools\"):\n"),
        (REGISTRY_OLD, REGISTRY_NEW),
    ], "managed_transfer")


def _release(applier: "TestApplier") -> None:
    applier.edit(RELEASE, [
        ("from melder.aether.aether import Aether\n",
         "from melder.aether.aether import Aether\n"
         "from melder.aether.aether_configuration import AetherConfiguration\n"),
        ("    set_frame_system_state_for_spellbook_configuration,\n"
         ")\n",
         "    set_frame_system_state_for_spellbook_configuration,\n"
         ")\n"
         + SUPPORT_IMPORT),
        ("def _bind_managed(book_or_root: Any, *, binding_name: Any = None, **options: Any) -> str:\n",
         "def _install_per_frame_spell_ids() -> None:\n"
         "    \"\"\"Configure and activate per-frame spell ids before any frame exists, so a class can be bound per frame.\"\"\"\n"
         + PER_FRAME +
         "\n"
         "\n"
         "def _bind_managed(book_or_root: Any, *, binding_name: Any = None, **options: Any) -> str:\n"),
        ("    # One anchor per root: under process-wide spell ids an identical binding in a second frame would collide.\n",
         "    # One anchor per root. Roots in two frames need per-frame spell ids (`_install_per_frame_spell_ids`): one\n"
         "    # class is one spell, so under process-wide ids a class bound in a second frame is refused.\n"),
        ("def _out(pool: ManagedSpellQuantity, label: str) -> Leased:\n",
         "def _out(pool: ManagedSpellQuantity, label: str, cls: type = Leased) -> Leased:\n"),
        ("        label: Label of a newly built object.\n"
         "\n"
         "    Returns:\n",
         "        label: Label of a newly built object.\n"
         "        cls: The class the pool's version builds - Leased, or a version of it.\n"
         "\n"
         "    Returns:\n"),
        ("        return Leased(label) if served is None else served\n",
         "        return cls(label) if served is None else served\n"),
        _release_versions(),
        _release_binding_names(),
        ("    \"\"\"The conduit names the root that holds the pool; a lesser names its root.\"\"\"\n"
         "    first_book, first_root, first_id = _conjured(",
         "    \"\"\"\n"
         "    The conduit names the root that holds the pool; a lesser names its root.\n"
         "\n"
         "    Leased is bound in two frames, which per-frame spell ids allow: one class is one spell\n"
         "    (" + S1_REF + "), so under process-wide ids the second frame's bind is refused.\n"
         "    \"\"\"\n"
         "    _install_per_frame_spell_ids()\n"
         "    first_book, first_root, first_id = _conjured("),
        ("        with pytest.raises(ValueError, match=\"Leased is managed by 2 pools\"):\n"
         "            ReleaseManagedSpell().release(Leased())\n"
         "        ReleaseManagedSpell().release(_out(first_pool, \"one\"), conduit=first_root)\n",
         "        with pytest.raises(ValueError, match=\"Leased is managed by 2 pools: .*Pass spell_id=... or conduit=...\"):\n"
         "            ReleaseManagedSpell().release(Leased())\n"
         "        ReleaseManagedSpell().release(_out(first_pool, \"one\"), conduit=first_root)\n"),
    ], "release")


def _release_versions() -> tuple:
    old = (
        "def test_a_post_conjure_bind_registers_and_a_notch_moves_the_releases() -> None:\n"
        "    \"\"\"\n"
        "    Two versions of one index: the active one takes a same-class release; a notch moves it.\n"
        "\n"
        "    The parked version differs by its disposal names: a managed spell's settings are not part of its spell_id\n"
        "    (0.2.8254), so the same class with only another limit would be the same spell.\n"
        "    \"\"\"\n"
        "    book = _dynamic_book()\n"
        "    book.bind(spell=Anchor, existence=Existence.unique, permissions=\"create\")\n"
        "    root = book.conjure(dynamic=True, name=\"managed-late\")\n"
        "    try:\n"
        "        active_id = _bind_managed(root, managed_spell_limit=16)\n"
        "        parked_id = root.bind_inactive(\n"
        "            spell=Leased, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n"
        "            existence=Existence.managed_spell_quantity, permissions=\"create\",\n"
        "            disposal_method_names=[\"close\", \"reset\"], managed_spell_limit=8,\n"
        "        )\n"
        "        active_pool, parked_pool = _pool_of(root, active_id), _pool_of(root, parked_id)\n"
        "        assert sorted(entry[\"spell_id\"] for entry in ReleaseManagedSpell().describe(Leased)) == sorted(\n"
        "            [active_id, parked_id],\n"
        "        )\n"
        "        ReleaseManagedSpell().release(_out(active_pool, \"first\"))\n"
        "        assert (active_pool.idle_count, parked_pool.idle_count) == (1, 0)\n"
        "        # The notch needs the parked version itself, which _get_owned_spell answers (until 0.2.8253\n"
        "        # find_spell_by_id answered a parked id with the index's live spell).\n"
        "        parked = book._get_owned_spell(parked_id)\n"
        "        root.notch_spell(spell_index=parked.spell_index, spell=parked)\n"
        "        ReleaseManagedSpell().release(_out(parked_pool, \"second\"))\n"
        "        assert (active_pool.idle_count, parked_pool.idle_count) == (1, 1)\n"
    )
    new = (
        "def test_a_post_conjure_bind_registers_and_each_version_takes_its_own_releases() -> None:\n"
        "    \"\"\"\n"
        "    Two versions of one index are two classes, so each version's pool takes the releases of its class.\n"
        "\n"
        "    One object is one spell (" + S1_REF + "): the parked version is a version\n"
        "    of Leased - its name, other code - registered under its own class, so a release by class reaches the pool\n"
        "    of the version that built the object, before and after a notch.\n"
        "    \"\"\"\n"
        "    book = _dynamic_book()\n"
        "    book.bind(spell=Anchor, existence=Existence.unique, permissions=\"create\")\n"
        "    root = book.conjure(dynamic=True, name=\"managed-late\")\n"
        "    try:\n"
        "        active_id = _bind_managed(root, managed_spell_limit=16)\n"
        "        second = version_of(Leased, version=2)\n"
        "        parked_id = root.bind_inactive(\n"
        "            spell=second, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n"
        "            existence=Existence.managed_spell_quantity, permissions=\"create\",\n"
        "            disposal_method_names=[\"close\", \"reset\"], managed_spell_limit=8,\n"
        "        )\n"
        "        active_pool, parked_pool = _pool_of(root, active_id), _pool_of(root, parked_id)\n"
        "        assert [entry[\"spell_id\"] for entry in ReleaseManagedSpell().describe(Leased)] == [active_id]\n"
        "        assert [entry[\"spell_id\"] for entry in ReleaseManagedSpell().describe(second)] == [parked_id]\n"
        "        ReleaseManagedSpell().release(_out(active_pool, \"first\"))\n"
        "        ReleaseManagedSpell().release(_out(parked_pool, \"second\", second))\n"
        "        assert (active_pool.idle_count, parked_pool.idle_count) == (1, 1)\n"
        "        # The notch needs the parked version itself, which _get_owned_spell answers (until 0.2.8253\n"
        "        # find_spell_by_id answered a parked id with the index's live spell).\n"
        "        parked = book._get_owned_spell(parked_id)\n"
        "        root.notch_spell(spell_index=parked.spell_index, spell=parked)\n"
        "        for leased in (_out(active_pool, \"third\"), _out(parked_pool, \"fourth\", second)):\n"
        "            ReleaseManagedSpell().release(leased)\n"
        "        assert (active_pool.idle_count, parked_pool.idle_count) == (1, 1)\n"
    )
    return old, new


def _release_binding_names() -> tuple:
    old = (
        "def test_two_binding_names_in_one_root_need_a_spell_id() -> None:\n"
        "    \"\"\"Both versions are selected in their own index; the conduit alone cannot pick, the spell id can.\"\"\"\n"
        "    book = _automatic_book()\n"
        "    book.bind(spell=Anchor, existence=Existence.unique, permissions=\"create\")\n"
        "    left_id = _bind_managed(book, binding_name=\"left\")\n"
        "    right_id = _bind_managed(book, binding_name=\"right\")\n"
        "    root = book.conjure(name=\"two-names\")\n"
        "    try:\n"
        "        right = _pool_of(root, right_id)\n"
        "        with pytest.raises(ValueError, match=\"Leased is managed by 2 pools: .*Pass spell_id=... or conduit=...\"):\n"
        "            ReleaseManagedSpell().release(Leased())\n"
        "        with pytest.raises(ValueError, match=\"Leased is managed by 2 pools\"):\n"
        "            ReleaseManagedSpell().release(Leased(), conduit=root)\n"
        "        ReleaseManagedSpell().release(_out(right, \"r\"), spell_id=right_id)\n"
        "        assert (right.idle_count, _pool_of(root, left_id).idle_count) == (1, 0)\n"
    )
    new = (
        "def test_a_second_binding_name_in_one_root_is_refused_and_one_pool_takes_the_releases() -> None:\n"
        "    \"\"\"\n"
        "    One object is one spell (" + S1_REF + "): Leased bound under a second binding name\n"
        "    is refused, so one root holds one pool of the class and a release by class reaches it without a filter.\n"
        "    \"\"\"\n"
        "    book = _automatic_book()\n"
        "    book.bind(spell=Anchor, existence=Existence.unique, permissions=\"create\")\n"
        "    left_id = _bind_managed(book, binding_name=\"left\")\n"
        "    with pytest.raises(RuntimeError, match=\"Spell ID collision detected: this object is already registered as \"\n"
        "                                           \"spell_id \" + left_id):\n"
        "        _bind_managed(book, binding_name=\"right\")\n"
        "    root = book.conjure(name=\"two-names\")\n"
        "    try:\n"
        "        left = _pool_of(root, left_id)\n"
        "        ReleaseManagedSpell().release(_out(left, \"l\"))\n"
        "        assert left.idle_count == 1\n"
    )
    return old, new


def _quantity(applier: "TestApplier") -> None:
    applier.edit(QUANTITY, [
        ("from melder.aether.aether import Aether\n",
         "from melder.aether.aether import Aether\n"
         "from melder.aether.aether_configuration import AetherConfiguration\n"),
        ("    A second version's class: a managed spell's settings are not part of its spell_id (0.2.8254), so a version of\n"
         "    its own needs another class (or address, or disposal names).\n",
         "    A second version's class: a spell_id is the class's code (" + S1_REF + "), so\n"
         "    a version of its own needs another class; its settings, address and disposal names are its binding.\n"),
        ("    \"\"\"Two automatic roots in two frames, each with its own Session binding.\"\"\"\n"
         "    roots = []\n",
         "    \"\"\"\n"
         "    Two automatic roots in two frames, each with its own Session binding.\n"
         "\n"
         "    Session is bound in both frames, which per-frame spell ids allow: one class is one spell (S1 of\n"
         "    EPIC-2026-10-18-spell_identity_is_the_code), so under process-wide ids the second frame's bind is refused.\n"
         "    \"\"\"\n"
         + PER_FRAME +
         "    roots = []\n"),
        ("    \"\"\"One class bound twice: two versions, two pools, a release picks one by spell id.\"\"\"\n"
         "    book = _automatic_book()\n"
         "    left_id = _bind_session(book, binding_name=\"left\")\n"
         "    right_id = _bind_session(book, binding_name=\"right\")\n"
         "    root = book.conjure(name=\"two-names\")\n"
         "    try:\n"
         "        left = root.meld(spell=Session, binding_name=\"left\")\n"
         "        right = root.meld(spell=Session, binding_name=\"right\")\n",
         "    \"\"\"\n"
         "    Two binding names in one root are two classes - one object is one spell (S1 of\n"
         "    EPIC-2026-10-18-spell_identity_is_the_code) - so each has its own pool; a release picks one by spell id.\n"
         "    \"\"\"\n"
         "    book = _automatic_book()\n"
         "    left_id = _bind_session(book, binding_name=\"left\")\n"
         "    right_id = book.bind(spell=SessionNext, binding_name=\"right\", existence=Existence.managed_spell_quantity,\n"
         "                         permissions=\"create\")\n"
         "    root = book.conjure(name=\"two-names\")\n"
         "    try:\n"
         "        left = root.meld(spell=Session, binding_name=\"left\")\n"
         "        right = root.meld(spell=SessionNext, binding_name=\"right\")\n"),
    ], "quantity")


def _quantity_pool(applier: "TestApplier") -> None:
    applier.edit(QUANTITY_POOL, [
        ("    set_frame_system_state_for_spellbook_configuration,\n"
         ")\n",
         "    set_frame_system_state_for_spellbook_configuration,\n"
         ")\n"
         + SUPPORT_IMPORT),
        ("            spell=OtherPooled, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n",
         "            spell=version_of(OtherPooled, version=2), spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n"),
        ("        # No disposal names: a version of its own (0.2.8254: a managed spell's settings are not in its spell_id).\n",
         "        # A version of its own is other code - one object is one spell; its settings and empty disposal list bind it.\n"),
    ], "quantity_pool")


def _options_record(applier: "TestApplier") -> None:
    applier.edit(OPTIONS_RECORD, [
        ("An active member and a parked member are covered on both lanes; the parked member differs by its disposal names,\n"
         "since a managed spell's settings are not part of its spell_id (0.2.8254). Managed spells are not melded here:\n"
         "dispensing arrives with STORY-2026-10-15-managed_dispense_codegen (S5).\n",
         "An active member and a parked member are covered on both lanes; the parked member is a second version's class\n"
         "(RecordedPoolNext): one object is one spell (" + S1_REF + "), so a version is new\n"
         "code, and its options, settings and disposal names are its binding. Managed spells are not melded here: dispensing\n"
         "arrives with STORY-2026-10-15-managed_dispense_codegen (S5).\n"),
        ("    def flush(self) -> None:\n"
         "        \"\"\"Write out buffered lines.\"\"\"\n"
         "\n"
         "\n"
         "class RecordedAnchor:\n",
         "    def flush(self) -> None:\n"
         "        \"\"\"Write out buffered lines.\"\"\"\n"
         "\n"
         "\n"
         "class RecordedPoolNext(RecordedPool):\n"
         "    \"\"\"The parked second version: new code, module-scoped so a restore and a graft import it by qualname.\"\"\"\n"
         "\n"
         "    version = 2\n"
         "\n"
         "\n"
         "class RecordedAnchor:\n"),
        ("        spell=RecordedPool, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n",
         "        spell=RecordedPoolNext, spell_index=book.find_spell_by_spell_id(active_id).spell_index,\n"),
    ], "options_record")


def _bind_options(applier: "TestApplier") -> None:
    applier.edit(BIND_OPTIONS, [
        ("from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration\n",
         "from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration\n"
         + SUPPORT_IMPORT),
        ("def test_a_managed_binding_changes_the_spell_id_and_its_settings_do_not() -> None:\n"
         "    \"\"\"The same class bound unique and managed gets two ids; managed with a limit keeps the managed one (0.2.8254).\"\"\"\n"
         "    ids = []\n",
         "def test_a_managed_binding_keeps_the_spell_id_and_moves_the_binding_hash() -> None:\n"
         "    \"\"\"\n"
         "    The same class bound unique, managed and managed with a limit is one spell_id - the class's code (S1 of\n"
         "    EPIC-2026-10-18-spell_identity_is_the_code) - and three bindings: the existence and the settings are the\n"
         "    binding, so each binding has its own binding hash (S2).\n"
         "    \"\"\"\n"
         "    ids = []\n"
         "    hashes = []\n"),
        ("            ids.append(book.bind(spell=PooledLogger, **options))\n"
         "        finally:\n"
         "            book.cleanup()\n"
         "    assert ids[0] != ids[1]\n"
         "    assert ids[1] == ids[2]\n",
         "            spell_id = book.bind(spell=PooledLogger, **options)\n"
         "            ids.append(spell_id)\n"
         "            hashes.append(book.find_spell_by_spell_id(spell_id).binding_hash)\n"
         "        finally:\n"
         "            book.cleanup()\n"
         "    assert ids[0] == ids[1] == ids[2]\n"
         "    assert len(set(hashes)) == 3\n"),
        ("    \"\"\"A root binds a managed class after conjure, then parks a second version (other disposal names) with its own.\"\"\"\n",
         "    \"\"\"A root binds a managed class after conjure, then parks a second version of it (other code) with its own.\"\"\"\n"),
        ("            spell=PooledLogger, spell_index=active.spell_index, existence=Existence.managed_spell_quantity,\n",
         "            spell=version_of(PooledLogger, version=2), spell_index=active.spell_index,\n"
         "            existence=Existence.managed_spell_quantity,\n"),
    ], "bind_options")


def _stability(applier: "TestApplier") -> None:
    applier.edit(STABILITY, [
        ("    from melder.aether.spellbook.bind.bind import Bind\n"
         "    from melder.aether.spellbook.existence.existence import Existence\n"
         "    import stability_shapes\n"
         "    print(json.dumps({k: Bind.spell_id_inspector(v, existence=Existence.unique)\n"
         "                      for k, v in stability_shapes.CANDIDATES.items()}))\n",
         "    from melder.aether.spellbook.bind.bind import Bind\n"
         "    import stability_shapes\n"
         "    print(json.dumps({k: Bind.spell_id_inspector(v) for k, v in stability_shapes.CANDIDATES.items()}))\n"),
    ], "stability")


def apply(applier: "TestApplier") -> None:
    """Stage part B's edits and copy the support module they import."""
    applier.copy(SUPPORT)
    _case_parity(applier)
    _artifact_ownership(applier)
    _contract_more(applier)
    _managed_transfer(applier)
    _release(applier)
    _quantity(applier)
    _quantity_pool(applier)
    _options_record(applier)
    _bind_options(applier)
    _stability(applier)
