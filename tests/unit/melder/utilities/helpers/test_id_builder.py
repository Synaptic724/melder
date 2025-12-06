from melder.utilities.helpers.id_builder import IDBuilder


def test_create_id_returns_ulid_like_string():
    result = IDBuilder.create_id()
    # ULID strings are 26 chars, alphanumeric
    assert isinstance(result, str)
    assert len(result) == 26
    assert result.isalnum()
