"""Rule 2 / D3 tests: a notch back reactivates a version grant; a grant of a parked version activates on its notch.

Inserted into test_conduit_integration_notch_revalidation.py before `_chain`. component_patch_notch_reactivation's
validation expectations (an index link behaves as today: the S1 test). melder_1.
usage: python <this script> <root> <relative path of test_conduit_integration_notch_revalidation.py> [--check]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from apply_lib import apply

ROOT = pathlib.Path(sys.argv[1])
REL = sys.argv[2]
CHECK = "--check" in sys.argv[3:]

ANCHOR = "def _chain(frame: str, *, by_class: bool = False) -> Tuple[Spellbook, Conduit, SpellIndex, type, type]:\n"

TESTS = '''def test_a_notch_back_reactivates_a_version_grant_and_its_consumer_rebuilds_with_one_pass(
        resolution_passes: List[str],
) -> None:
    """
    D3: the notch to B parks the borrower's version grant of A, so the consumer fails naming the lost contract; the
    notch back to A makes that copy active again, the consumer builds A with one 5-11 pass, an object built before
    keeps its provider, and a linked peer that never borrowed A gains no provider.
    """
    world = _lend("anchored_back", ImplA, index_link=False)
    bystander_book = Spellbook(aetheric_frame="anchored_back",
                               configuration=SpellbookConfiguration("anchored_back").with_defaults())
    bystander_id = bystander_book.bind(spell=Consumer, binding_name="bystander", existence=Existence.many,
                                       permissions="create")
    bystander = bystander_book.conjure(dynamic=True, name="bystander")
    try:
        world.lender.link(bystander)
        before = world.borrower.meld(spell=Consumer)
        assert before.service.ping() == "A"

        world.notch_to(ImplB)
        with pytest.raises(SpellbookValidationError) as lost:
            world.meld_ping()
        _assert_lost_contract_reported(lost.value)

        resolution_passes.clear()
        world.notch_back(world.provider_id)
        assert resolution_passes == []
        assert world.meld_ping() == "A"
        assert world.meld_ping() == "A"
        assert resolution_passes == ["Consumer"]
        assert before.service.ping() == "A"

        with pytest.raises(SpellbookValidationError) as untouched:
            bystander.meld(spell_id=bystander_id)
        _assert_lost_contract_reported(untouched.value)
    finally:
        bystander.cleanup()
        world.cleanup()


def test_a_grant_of_a_parked_version_becomes_active_when_the_lender_notches_to_it() -> None:
    """
    D3: a version granted while parked stays off resolution - the consumer fails naming the lost contract - until
    the lender notches to it; the notch makes the borrower's copy active and the consumer builds that version. The
    grant takes the parked Spell object, because `get_spell_by_id` answers a parked id with the active member.
    """
    lender_book, borrower_book = _books("grant_parked")
    a_id = lender_book.bind(spell=ImplA, spellframe=IService, binding_name="svc", existence=Existence.many,
                            permissions="create")
    borrower_book.bind(spell=Consumer, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        lender.link(borrower)
        index = lender_book.find_spell_by_id(a_id).spell_index
        b_id = lender.bind_inactive(spell=ImplB, spell_index=index, spellframe=IService, binding_name="svc",
                                    existence=Existence.many, permissions="create")
        parked_b = lender_book._get_owned_spell(b_id)
        with borrower.transaction("link", conduits=[borrower, lender]):
            assert borrower.add_spell_to_contract(spell=parked_b, conduit=lender, permissions="create")
        with pytest.raises(SpellbookValidationError) as lost:
            borrower.meld(spell=Consumer)
        _assert_lost_contract_reported(lost.value)

        lender.notch_spell(spell_index=index, spell_id=b_id)
        assert borrower.meld(spell=Consumer).service.ping() == "B"
    finally:
        borrower.cleanup()
        lender.cleanup()


'''

STEPS = [
    ("one", ANCHOR, TESTS + ANCHOR, ""),
]

# The anchor survives the insertion, so refuse a second application instead of inserting the tests twice.
if "def test_a_notch_back_reactivates_a_version_grant" in (ROOT / REL).read_text(encoding="utf-8"):
    raise SystemExit(f"{REL}: the D3 tests are already in place")

apply(ROOT, REL, STEPS, CHECK)
