"""melder_0, 2026-10-18: category (c) of S1's test tranche, part A - tests that registered one object twice.

One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): a second registration of a class - under
another binding name, in another Book of the frame, or staged as a version - is refused. Each test keeps its subject
and gives the second registration other code: a class of its own where the test only needs a second spell, a
`version_of` the class (tests/_spell_identity_test_support.py) where it needs the same name, and a module-level class
where a restore or a graft must import the version. Part A: the conduit, aether and frame tests, and the frames'
cloud test of category (e).
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests_apply_s1_s2 import TestApplier

SUPPORT = "tests/_spell_identity_test_support.py"
SUPPORT_IMPORT = "from tests._spell_identity_test_support import version_of\n"

POLICY_READER = "tests/component/melder/aether/conduit/test_conduit_component_policy_reader.py"
FRAME_POSTURE = "tests/component/melder/aether/test_configure_aether_frame_posture_component.py"
INDEX_MOVES = "tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py"
NOTCH_BY_ID = "tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py"
CATEGORY = "tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py"
CLUSTER_CONCURRENCY = "tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py"
CLUSTER_MEMBERSHIP = "tests/integration/melder/aether/test_aether_integration_cluster_membership_transactions.py"
GRAPH_REPLAY = "tests/integration/melder/aether/test_non_resolvable_graph_replay.py"
FRAMES = "tests/integration/melder/aether/test_aether_integration_frames.py"
NOTCH_REVALIDATION = "tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py"


def _policy_reader(applier: "TestApplier") -> None:
    applier.edit(POLICY_READER, [
        ("class _Linkable:\n"
         "    def __init__(self) -> None:\n"
         "        pass\n"
         "\n"
         "\n"
         "def _conduit(frame_name: str, *, dynamic: bool) -> Conduit:\n"
         "    \"\"\"Conjure one root conduit on its own frame.\"\"\"\n"
         "    book = Spellbook(frame_name)\n"
         "    # binding_name keeps each frame's spell_id distinct. The frame is NOT in the\n"
         "    # bind-time fingerprint, so under process-wide uniqueness two frames binding\n"
         "    # the same class with the same parameters mint the SAME id and collide.\n"
         "    book.bind(spell=_Linkable, existence=\"unique\", binding_name=frame_name)\n",
         "class _Linkable:\n"
         "    def __init__(self) -> None:\n"
         "        pass\n"
         "\n"
         "\n"
         "class _SecondLinkable:\n"
         "    \"\"\"The class a second conduit binds while the first is alive: one class is one spell.\"\"\"\n"
         "\n"
         "    def __init__(self) -> None:\n"
         "        pass\n"
         "\n"
         "\n"
         "def _conduit(frame_name: str, *, dynamic: bool, spell: type = _Linkable) -> Conduit:\n"
         "    \"\"\"Conjure one root conduit on its own frame, binding `spell` there.\"\"\"\n"
         "    book = Spellbook(frame_name)\n"
         "    # A spell_id is the SHA256 of the class's code (S1 of EPIC-2026-10-18-spell_identity_is_the_code), not of\n"
         "    # how it is bound: under process-wide uniqueness a class bound in one frame is refused in another whatever\n"
         "    # its binding name, so a test that holds two conduits at once binds `_SecondLinkable` in the second.\n"
         "    book.bind(spell=spell, existence=\"unique\", binding_name=frame_name)\n"),
        ("    target = _conduit(\"policy-round-b\", dynamic=True)\n",
         "    target = _conduit(\"policy-round-b\", dynamic=True, spell=_SecondLinkable)\n"),
    ], "policy_reader")


def _frame_posture(applier: "TestApplier") -> None:
    applier.edit(FRAME_POSTURE, [
        ("class _Service:\n"
         "    def __init__(self) -> None:\n"
         "        pass\n"
         "\n"
         "\n"
         "def _book(frame_name: str) -> Spellbook:\n"
         "    \"\"\"Build a bound spellbook on its own frame, so postures stay isolated.\"\"\"\n"
         "    book = Spellbook(frame_name)\n"
         "    # binding_name keeps each frame's spell_id distinct - the frame itself is not\n"
         "    # in the bind-time fingerprint, so it cannot separate them under process-wide\n"
         "    # uniqueness.\n"
         "    book.bind(spell=_Service, existence=\"unique\", binding_name=frame_name)\n",
         "class _Service:\n"
         "    def __init__(self) -> None:\n"
         "        pass\n"
         "\n"
         "\n"
         "class _SecondService:\n"
         "    \"\"\"The class a second Book binds while the first is conjured: one class is one spell.\"\"\"\n"
         "\n"
         "    def __init__(self) -> None:\n"
         "        pass\n"
         "\n"
         "\n"
         "def _book(frame_name: str, spell: type = _Service) -> Spellbook:\n"
         "    \"\"\"Build a bound spellbook on its own frame, so postures stay isolated.\"\"\"\n"
         "    book = Spellbook(frame_name)\n"
         "    # A spell_id is the SHA256 of the class's code (S1 of EPIC-2026-10-18-spell_identity_is_the_code): under\n"
         "    # process-wide uniqueness a class bound in a conjured frame is refused in another whatever its binding\n"
         "    # name, so a test that conjures two frames binds `_SecondService` in the second.\n"
         "    book.bind(spell=spell, existence=\"unique\", binding_name=frame_name)\n"),
        ("    full = _book(\"codegen-full\")\n", "    full = _book(\"codegen-full\", _SecondService)\n"),
    ], "frame_posture")


def _index_moves(applier: "TestApplier") -> None:
    applier.edit(INDEX_MOVES, [
        ("class _ServiceY:\n"
         "    \"\"\"The spell bound active on index Y.\"\"\"\n"
         "\n"
         "    def __init__(self) -> None:\n"
         "        \"\"\"Tag the object with its spell.\"\"\"\n"
         "        self.tag = \"Y\"\n",
         "class _ServiceY:\n"
         "    \"\"\"The spell bound active on index Y.\"\"\"\n"
         "\n"
         "    def __init__(self) -> None:\n"
         "        \"\"\"Tag the object with its spell.\"\"\"\n"
         "        self.tag = \"Y\"\n"
         "\n"
         "\n"
         "class _ServiceOther:\n"
         "    \"\"\"The spell another Book of the frame owns: one class is one spell, so it is a class of its own.\"\"\"\n"
         "\n"
         "    def __init__(self) -> None:\n"
         "        \"\"\"Tag the object with its spell.\"\"\"\n"
         "        self.tag = \"other\"\n"),
        ("            spell=_ServiceB, existence=Existence.unique, permissions=\"create\", binding_name=\"other_b\",\n",
         "            spell=_ServiceOther, existence=Existence.unique, permissions=\"create\", binding_name=\"other_b\",\n"),
    ], "index_moves")


def _notch_by_id(applier: "TestApplier") -> None:
    applier.edit(NOTCH_BY_ID, [
        ("from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration\n",
         "from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration\n"
         + SUPPORT_IMPORT),
        ("        tag: Suffix for the binding names, so two worlds can share a frame.\n",
         "        tag: Names a second world sharing the frame: its binding names take the suffix and it binds versions\n"
         "            of the services of its own, since one class is one spell (S1 of\n"
         "            EPIC-2026-10-18-spell_identity_is_the_code).\n"),
        ("    book = _make_spellbook()\n"
         "    id_a = book.bind(spell=_ServiceA, existence=Existence.unique, permissions=\"create\", "
         "binding_name=f\"a{tag}\")\n",
         "    service_a = version_of(_ServiceA, world=tag) if tag else _ServiceA\n"
         "    service_b = version_of(_ServiceB, world=tag) if tag else _ServiceB\n"
         "    book = _make_spellbook()\n"
         "    id_a = book.bind(spell=service_a, existence=Existence.unique, permissions=\"create\", "
         "binding_name=f\"a{tag}\")\n"),
        ("        id_b = book.bind_inactive(\n"
         "            spell=_ServiceB, spell_index=index, existence=Existence.unique, permissions=\"create\",\n"
         "            binding_name=f\"b{tag}\",\n",
         "        id_b = book.bind_inactive(\n"
         "            spell=service_b, spell_index=index, existence=Existence.unique, permissions=\"create\",\n"
         "            binding_name=f\"b{tag}\",\n"),
        ("        id_b = root.bind_inactive(\n"
         "            spell=_ServiceB, spell_index=index, existence=Existence.unique, permissions=\"create\",\n"
         "            binding_name=f\"b{tag}\",\n",
         "        id_b = root.bind_inactive(\n"
         "            spell=service_b, spell_index=index, existence=Existence.unique, permissions=\"create\",\n"
         "            binding_name=f\"b{tag}\",\n"),
    ], "notch_by_id")


def _category(applier: "TestApplier") -> None:
    applier.edit(CATEGORY, [
        ("from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError\n",
         "from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError\n"
         + SUPPORT_IMPORT),
        ("    GUARD: two spells of the annotated TYPE at distinct addresses are a real ambiguity. Since 2026-10-04 it is\n"
         "    refused through the readable validation report (AMBIGUOUS_PROVIDER) naming both addresses and the remedies,\n"
         "    at the late bind in a dynamic world.\n",
         "    GUARD: two spells of the annotated TYPE at distinct addresses are a real ambiguity - the second a version of\n"
         "    Spectrum (its name, other code), since one class is one spell. Since 2026-10-04 it is refused through the\n"
         "    readable validation report (AMBIGUOUS_PROVIDER) naming both addresses and the remedies, at the late bind in a\n"
         "    dynamic world.\n"),
        ("        root.bind(spell=Spectrum, existence=\"unique_per_conduit\", spellframe=\"mirror\",\n",
         "        root.bind(spell=version_of(Spectrum, mirror=True), existence=\"unique_per_conduit\", "
         "spellframe=\"mirror\",\n"),
    ], "category")


def _cluster_concurrency(applier: "TestApplier") -> None:
    applier.edit(CLUSTER_CONCURRENCY, [
        ("from tests.mocks.spellbook.core_classes import BasicService\n",
         "from tests.mocks.spellbook.core_classes import BasicService\n" + SUPPORT_IMPORT),
        ("    Bind one unique_per_conduit_cluster spell (distinct via binding_name) + conjure.\n"
         "\n"
         "    The binding_name is the unique conduit name so every conduit in the frame gets a\n"
         "    distinct spell_id (the fingerprint includes binding_name, not the spellbook).\n",
         "    Bind one unique_per_conduit_cluster spell (a version of BasicService of its own) + conjure.\n"
         "\n"
         "    One class is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): every conduit in the frame\n"
         "    binds its own version of BasicService, named for the conduit, so each gets a distinct spell_id; the\n"
         "    binding_name is the conduit name too.\n"),
        ("        spell=BasicService,\n", "        spell=version_of(BasicService, conduit_name=name),\n"),
    ], "cluster_concurrency")


def _cluster_membership(applier: "TestApplier") -> None:
    applier.edit(CLUSTER_MEMBERSHIP, [
        ("from tests.mocks.spellbook.core_classes import BasicService\n",
         "from tests.mocks.spellbook.core_classes import BasicService\n" + SUPPORT_IMPORT),
        ("    The spell_id is fingerprinted from the structural profile + binding_name +\n"
         "    existence (NOT the spellbook), so multiple conduits in ONE frame must each bind\n"
         "    a distinct binding_name to avoid a spell_id collision. The binding_name defaults\n"
         "    to the (unique) conduit name.\n",
         "    One class is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): the\n"
         "    spell_id is the class's code, so every conduit in ONE frame binds its own\n"
         "    version of `spell`, named for the conduit. The binding_name defaults to the\n"
         "    (unique) conduit name.\n"),
        ("        spell=spell,\n"
         "        existence=existence,\n",
         "        spell=version_of(spell, conduit_name=name),\n"
         "        existence=existence,\n"),
    ], "cluster_membership")


def _graph_replay(applier: "TestApplier") -> None:
    applier.edit(GRAPH_REPLAY, [
        ("    def __init__(self, definition: GraphDefinition) -> None:\n"
         "        \"\"\"Retain the exact supplied object.\"\"\"\n"
         "        self.definition = definition\n",
         "    def __init__(self, definition: GraphDefinition) -> None:\n"
         "        \"\"\"Retain the exact supplied object.\"\"\"\n"
         "        self.definition = definition\n"
         "\n"
         "\n"
         "class GraphImplementationRevision(GraphDefinition):\n"
         "    \"\"\"\n"
         "    A revised GraphImplementation, staged beside it.\n"
         "\n"
         "    One object is one spell (S1 of EPIC-2026-10-18-spell_identity_is_the_code): staging GraphImplementation\n"
         "    itself again is refused, so a revision is new code - here a class of its own with the same base, so its\n"
         "    base relationship is GraphDefinition's as the original's is. Module level, so a restore or a graft\n"
         "    imports it.\n"
         "    \"\"\"\n"
         "\n"
         "    def value(self) -> str:\n"
         "        \"\"\"Return the revised value.\"\"\"\n"
         "        return \"revised\"\n"
         "\n"
         "\n"
         "class GraphConsumerRevision(GraphConsumer):\n"
         "    \"\"\"A revised GraphConsumer, staged non-resolvable: new code, since one object is one spell; module level.\"\"\"\n"
         "\n"
         "    revision = 2\n"),
        ("    revision_id = conduit.bind_inactive(spell=GraphImplementation, spell_index=index, existence=\"unique\")\n",
         "    revision_id = conduit.bind_inactive(spell=GraphImplementationRevision, spell_index=index, "
         "existence=\"unique\")\n"),
        ("        spell=GraphConsumer, spell_index=consumer_index, existence=\"many\", resolvable=False,\n",
         "        spell=GraphConsumerRevision, spell_index=consumer_index, existence=\"many\", resolvable=False,\n"),
        ("    true_id = conduit.bind_inactive(spell=GraphImplementation, spell_index=index, existence=\"unique\")\n",
         "    true_id = conduit.bind_inactive(spell=GraphImplementationRevision, spell_index=index, "
         "existence=\"unique\")\n"),
    ], "graph_replay")


def _frames(applier: "TestApplier") -> None:
    applier.edit(FRAMES, [
        ("    # binding_name per frame: the subject here is CONDUIT CLOUD isolation, and\n"
         "    # the bound spell is only scaffolding to give each frame a conduit. The frame\n"
         "    # is not in the bind-time fingerprint, so without this both books mint the\n"
         "    # same spell_id and process-wide uniqueness refuses the second conjure before\n"
         "    # the clouds are ever compared.\n",
         "    # One class per frame: the subject here is CONDUIT CLOUD isolation, and the\n"
         "    # bound spell is only scaffolding to give each frame a conduit. A spell_id is\n"
         "    # the class's code (S1 of EPIC-2026-10-18-spell_identity_is_the_code), so one\n"
         "    # class bound in both frames is one spell_id and process-wide uniqueness would\n"
         "    # refuse the second conjure before the clouds are ever compared.\n"),
        ("    book_b.bind(\n"
         "        spell=BasicService,\n",
         "    book_b.bind(\n"
         "        spell=BasicConfig,\n"),
    ], "frames")


def _notch_revalidation(applier: "TestApplier") -> None:
    applier.edit(NOTCH_REVALIDATION, [
        ("from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError\n",
         "from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError\n"
         + SUPPORT_IMPORT),
        ("    bystander_id = bystander_book.bind(spell=Consumer, binding_name=\"bystander\", existence=Existence.many,\n"
         "                                       permissions=\"create\")\n",
         "    # A version of Consumer of its own: one class is one spell, and the borrower bound Consumer.\n"
         "    bystander_id = bystander_book.bind(spell=version_of(Consumer, bystander=True), binding_name=\"bystander\",\n"
         "                                       existence=Existence.many, permissions=\"create\")\n"),
    ], "notch_revalidation")


def apply(applier: "TestApplier") -> None:
    """Stage part A's edits and copy the support module they import."""
    applier.copy(SUPPORT)
    _policy_reader(applier)
    _frame_posture(applier)
    _index_moves(applier)
    _notch_by_id(applier)
    _category(applier)
    _cluster_concurrency(applier)
    _cluster_membership(applier)
    _graph_replay(applier)
    _frames(applier)
    _notch_revalidation(applier)
