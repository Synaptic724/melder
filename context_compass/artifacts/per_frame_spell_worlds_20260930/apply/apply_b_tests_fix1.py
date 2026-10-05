"""Part B red tests, fix 1: the graft test targets the Book whose copy the old record displaced (tenant_a)."""
import sys

from apply_support import ApplySession

session = ApplySession(sys.argv[1])
session.replace("tests/unit/melder/crystallizer/persistence/test_persistence_profile.py", r'''    Contract:
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
''', r'''    Contract:
        With one spell id recorded in two frames, the graft of tenant_a's index (the copy recorded first) carries
        tenant_a's copy; the members map stays keyed by spell id, because one index lives in one Book.
    Returns:
        None.
    Raises:
        AssertionError: If the graft picks up another Book's copy.
    """
    profile = PersistenceProfile("p")
    _record_one_class_in_two_frames(profile)
    profile.record(SpellIndexCrystal(
        index_id="index-a", spellbook_id="book-a", selected_spell_id="sha", member_spell_ids=["sha"],
    ))
    record = profile.capture_index_graft("index-a")
    assert list(record["members"]) == ["sha"]
    assert record["members"]["sha"]["payload"]["spellbook_id"] == "book-a"
''')
long_lines = session.long_added_lines()
if long_lines:
    raise AssertionError("lines over 120:\n" + "\n".join(long_lines))
for path in session.write():
    print(path)
