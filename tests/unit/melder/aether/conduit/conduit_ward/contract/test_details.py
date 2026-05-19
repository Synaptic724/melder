import pytest
from unittest.mock import MagicMock
from threading import RLock

from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.spellbook.bind.spell_index import SpellIndex # Direct import for mocking

# Fixtures for common mocked objects
@pytest.fixture
def mock_spell_index():
    """
    Purpose:
        Provide a mock SpellIndex for Detail tests.
    Contract:
        Returns a MagicMock with a prepopulated version map.
    Returns:
        MagicMock: SpellIndex mock instance.
    """
    mock = MagicMock(spec=SpellIndex)
    mock._versions = {"sha123": "version_data"}
    return mock

@pytest.fixture
def mock_permissions():
    """
    Purpose:
        Provide a Permissions enum value for Detail tests.
    Contract:
        Returns a concrete Permissions member.
    Returns:
        Permissions: Permission enum value.
    """
    return Permissions.create

@pytest.fixture
def mock_contract_type():
    """
    Purpose:
        Provide a ContractTypes enum value for Detail tests.
    Contract:
        Returns a concrete ContractTypes member.
    Returns:
        ContractTypes: Contract type enum value.
    """
    return ContractTypes.received

@pytest.fixture
def mock_detail_reason():
    """
    Purpose:
        Provide a DetailReason enum value for Detail tests.
    Contract:
        Returns a concrete DetailReason member.
    Returns:
        DetailReason: Detail reason enum value.
    """
    return DetailReason.other

@pytest.fixture
def sample_detail(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """
    Purpose:
        Provide a basic Detail instance for reuse across tests.
    Contract:
        Returns a Detail populated with a spell id, reason, and sources.
    Args:
        mock_spell_index: SpellIndex mock fixture.
        mock_permissions: Permissions fixture.
        mock_contract_type: ContractTypes fixture.
        mock_detail_reason: DetailReason fixture.
    Returns:
        Detail: Detail instance under test.
    """
    return Detail(
        spell_index=mock_spell_index,
        spell_id="initial_sha",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason,
        sources={"root_spell_a"}
    )

# ----------------------------------------------------------------------
# Initialization Tests
# ----------------------------------------------------------------------

def test_detail_init_success(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """
    Purpose:
        Verify Detail initializes with provided attributes.
    Contract:
        All constructor inputs are stored and internal fields are set.
    Args:
        mock_spell_index: SpellIndex mock fixture.
        mock_permissions: Permissions fixture.
        mock_contract_type: ContractTypes fixture.
        mock_detail_reason: DetailReason fixture.
    Returns:
        None.
    Raises:
        AssertionError: If initialization fields are incorrect.
    """
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="test_spell_id",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason,
        sources={"root_a", "root_b"}
    )
    assert detail.spell_index == mock_spell_index
    assert detail.spell_id == "test_spell_id"
    assert detail.permissions == mock_permissions
    assert detail.contract_type == mock_contract_type
    assert detail.reason == mock_detail_reason
    assert detail.sources == {"root_a", "root_b"}
    assert isinstance(detail._lock, type(RLock()))
    assert not detail._cleaned
    assert detail._id is not None

def test_detail_init_default_sources(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """
    Purpose:
        Ensure sources default to an empty set when None is passed.
    Contract:
        Detail.sources is an empty set after initialization with None.
    Args:
        mock_spell_index: SpellIndex mock fixture.
        mock_permissions: Permissions fixture.
        mock_contract_type: ContractTypes fixture.
        mock_detail_reason: DetailReason fixture.
    Returns:
        None.
    Raises:
        AssertionError: If sources is not an empty set.
    """
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="test_spell_id",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason,
        sources=None
    )
    assert detail.sources == set()

def test_detail_init_type_error_spell_index():
    """
    Purpose:
        Ensure Detail rejects an invalid spell_index type.
    Contract:
        Constructor raises TypeError when spell_index is None.
    Returns:
        None.
    Raises:
        AssertionError: If TypeError is not raised.
    """
    with pytest.raises(TypeError, match="spell_index must be SpellIndex"):
        Detail(
            spell_index=None, # Invalid type
            spell_id="test_spell_id",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
            reason=DetailReason.other
        )

def test_detail_init_type_error_permissions(mock_spell_index):
    """
    Purpose:
        Ensure Detail rejects an invalid permissions type.
    Contract:
        Constructor raises TypeError when permissions is not Permissions.
    Args:
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If TypeError is not raised.
    """
    with pytest.raises(TypeError, match="permissions must be Permissions"):
        Detail(
            spell_index=mock_spell_index,
            spell_id="test_spell_id",
            permissions="invalid_perm", # Invalid type
            contract_type=ContractTypes.received,
            reason=DetailReason.other
        )

def test_detail_init_type_error_contract_type(mock_spell_index):
    """
    Purpose:
        Ensure Detail rejects an invalid contract_type type.
    Contract:
        Constructor raises TypeError when contract_type is not ContractTypes.
    Args:
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If TypeError is not raised.
    """
    with pytest.raises(TypeError, match="contract_type must be ContractTypes"):
        Detail(
            spell_index=mock_spell_index,
            spell_id="test_spell_id",
            permissions=Permissions.read,
            contract_type="invalid_type", # Invalid type
            reason=DetailReason.other
        )

def test_detail_init_type_error_reason(mock_spell_index):
    """
    Purpose:
        Ensure Detail rejects an invalid reason type.
    Contract:
        Constructor raises TypeError when reason is not DetailReason.
    Args:
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If TypeError is not raised.
    """
    with pytest.raises(TypeError, match="reason must be DetailReason"):
        Detail(
            spell_index=mock_spell_index,
            spell_id="test_spell_id",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
            reason="invalid_reason" # Invalid type
        )

def test_detail_init_type_error_sources(mock_spell_index):
    """
    Purpose:
        Ensure Detail rejects invalid sources types.
    Contract:
        Constructor raises TypeError when sources is not a set.
    Args:
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If TypeError is not raised.
    """
    with pytest.raises(TypeError, match="sources must be a set of spell_ids"):
        Detail(
            spell_index=mock_spell_index,
            spell_id="test_spell_id",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
            sources=["not_a_set"] # Invalid type
        )


# ----------------------------------------------------------------------
# Cleanup Tests
# ----------------------------------------------------------------------

def test_detail_cleanup_success(sample_detail):
    """
    Purpose:
        Verify cleanup nulls out attributes and marks the detail cleaned.
    Contract:
        cleanup clears owned references and marks the Detail as cleaned.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear or null expected fields.
    """
    sample_detail.cleanup()
    assert sample_detail._cleaned
    assert not hasattr(sample_detail, "spell_index")
    assert not hasattr(sample_detail, "spell_id")
    assert not hasattr(sample_detail, "permissions")
    assert not hasattr(sample_detail, "contract_type")
    assert not hasattr(sample_detail, "reason")
    assert not hasattr(sample_detail, "sources")
    assert hasattr(sample_detail, "_lock")
    assert not hasattr(sample_detail, "_id")

def test_detail_cleanup_idempotent(sample_detail):
    """
    Purpose:
        Ensure cleanup can be called multiple times safely.
    Contract:
        cleanup is idempotent and leaves the Detail cleaned.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not remain idempotent.
    """
    sample_detail.cleanup()
    assert sample_detail._cleaned
    sample_detail.cleanup() # Second call should not raise or change state further
    assert sample_detail._cleaned

def test_detail_cleanup_noops_when_marked_cleaned_inside_lock(sample_detail):
    """
    Purpose:
        Verify cleanup re-checks cleaned state after entering the lock.
    Contract:
        If cleaned flips to True inside the lock, cleanup returns before nulling fields.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup continues after the second cleaned check.
    """
    class LockThatMarksCleaned:
        """Context manager that flips the detail to cleaned once the lock is entered."""

        def __init__(self, target_detail):
            self._target_detail = target_detail

        def __enter__(self):
            self._target_detail._cleaned = True
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return None

    sample_detail._lock = LockThatMarksCleaned(sample_detail)

    original_spell_index = sample_detail.spell_index
    original_spell_id = sample_detail.spell_id
    original_permissions = sample_detail.permissions
    original_contract_type = sample_detail.contract_type
    original_reason = sample_detail.reason
    original_sources = sample_detail.sources
    original_id = sample_detail._id

    sample_detail.cleanup()

    assert sample_detail._cleaned is True
    assert sample_detail.spell_index is original_spell_index
    assert sample_detail.spell_id == original_spell_id
    assert sample_detail.permissions == original_permissions
    assert sample_detail.contract_type == original_contract_type
    assert sample_detail.reason == original_reason
    assert sample_detail.sources is original_sources
    assert sample_detail._id == original_id

# ----------------------------------------------------------------------
# has_version Tests
# ----------------------------------------------------------------------

def test_has_version_exists(sample_detail):
    """
    Purpose:
        Verify has_version returns True when a version exists.
    Contract:
        has_version returns True for a version present in the SpellIndex.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If has_version does not return True for a known version.
    """
    assert sample_detail.has_version("sha123")

def test_has_version_does_not_exist(sample_detail):
    """
    Purpose:
        Verify has_version returns False for missing versions.
    Contract:
        has_version returns False when the version id is absent.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If has_version returns True for a missing version.
    """
    assert not sample_detail.has_version("non_existent_sha")

def test_has_version_empty_spell_index(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """
    Purpose:
        Ensure has_version handles an empty SpellIndex.
    Contract:
        has_version returns False when SpellIndex._versions is empty.
    Args:
        mock_spell_index: SpellIndex mock fixture.
        mock_permissions: Permissions fixture.
        mock_contract_type: ContractTypes fixture.
        mock_detail_reason: DetailReason fixture.
    Returns:
        None.
    Raises:
        AssertionError: If has_version returns True for empty versions.
    """
    mock_spell_index._versions = {}
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="initial_sha",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason
    )
    assert not detail.has_version("any_sha")

def test_has_version_after_cleanup(sample_detail):
    """
    Purpose:
        Ensure has_version rejects use after cleanup.
    Contract:
        has_version raises RuntimeError once the Detail is cleaned.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If has_version does not raise after cleanup.
    """
    sample_detail.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        sample_detail.has_version("sha123")

# ----------------------------------------------------------------------
# add_source Tests
# ----------------------------------------------------------------------

def test_add_source_new_source(sample_detail):
    """
    Purpose:
        Verify add_source records a new root id.
    Contract:
        add_source inserts the root id into the sources set.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If the new root id is not stored.
    """
    sample_detail.add_source("new_root_spell")
    assert "new_root_spell" in sample_detail.sources
    assert len(sample_detail.sources) == 2

def test_add_source_existing_source(sample_detail):
    """
    Purpose:
        Ensure add_source is idempotent for an existing root id.
    Contract:
        add_source keeps the sources set unchanged when the id exists.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If the sources set changes for a duplicate id.
    """
    sample_detail.add_source("root_spell_a")
    assert "root_spell_a" in sample_detail.sources
    assert len(sample_detail.sources) == 1 # Still 1 unique source

def test_add_source_none(sample_detail):
    """
    Purpose:
        Verify add_source ignores None.
    Contract:
        add_source with None leaves sources unchanged.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If sources are modified by a None input.
    """
    initial_len = len(sample_detail.sources)
    sample_detail.add_source(None)
    assert len(sample_detail.sources) == initial_len # No change

def test_add_source_recreates_sources_when_none(sample_detail):
    """
    Purpose:
        Verify add_source recreates the sources set when it has become None.
    Contract:
        add_source initializes a new set and stores the incoming root id.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If sources are not recreated correctly.
    """
    sample_detail.sources = None

    sample_detail.add_source("new_root_after_none")

    assert sample_detail.sources == {"new_root_after_none"}

def test_add_source_after_cleanup(sample_detail):
    """
    Purpose:
        Ensure add_source raises after cleanup.
    Contract:
        add_source raises RuntimeError when the Detail is cleaned.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If add_source does not raise after cleanup.
    """
    sample_detail.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        sample_detail.add_source("new_root")

# ----------------------------------------------------------------------
# remove_source Tests
# ----------------------------------------------------------------------

def test_remove_source_existing(sample_detail):
    """
    Purpose:
        Verify remove_source removes a root without deleting the detail.
    Contract:
        remove_source returns False when sources remain after removal.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If sources are not updated correctly.
    """
    sample_detail.add_source("root_spell_b")
    assert sample_detail.remove_source("root_spell_a") is False
    assert "root_spell_a" not in sample_detail.sources
    assert "root_spell_b" in sample_detail.sources
    assert len(sample_detail.sources) == 1

def test_remove_source_last_one(sample_detail):
    """
    Purpose:
        Verify remove_source signals deletion when removing the last source.
    Contract:
        remove_source returns True when the sources set becomes empty.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If remove_source does not return True for last source.
    """
    assert sample_detail.remove_source("root_spell_a") is True
    assert "root_spell_a" not in sample_detail.sources
    assert len(sample_detail.sources) == 0

def test_remove_source_non_existent(sample_detail):
    """
    Purpose:
        Verify remove_source ignores missing sources.
    Contract:
        remove_source returns False when the root id is not present.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If remove_source returns True for a missing root id.
    """
    assert sample_detail.remove_source("non_existent_root") is False
    assert len(sample_detail.sources) == 1 # No change

def test_remove_source_none(sample_detail):
    """
    Purpose:
        Verify remove_source ignores None inputs.
    Contract:
        remove_source returns False when root_spell_id is None.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If remove_source returns True for None input.
    """
    initial_len = len(sample_detail.sources)
    assert sample_detail.remove_source(None) is False
    assert len(sample_detail.sources) == initial_len # No change

def test_remove_source_from_empty(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """
    Purpose:
        Ensure remove_source returns True when the sources set remains empty.
    Contract:
        Removing any root from an empty sources set returns True and keeps sources empty.
    Args:
        mock_spell_index: SpellIndex mock fixture.
        mock_permissions: Permissions fixture.
        mock_contract_type: ContractTypes fixture.
        mock_detail_reason: DetailReason fixture.
    Returns:
        None.
    Raises:
        AssertionError: If remove_source does not return True for empty sources.
    """
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="initial_sha",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason,
        sources=None
    )
    assert detail.sources == set()
    assert detail.remove_source("any_root") is True

def test_remove_source_after_cleanup(sample_detail):
    """
    Purpose:
        Ensure remove_source rejects use after cleanup.
    Contract:
        remove_source raises RuntimeError when the Detail is cleaned.
    Args:
        sample_detail: Detail fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If remove_source does not raise after cleanup.
    """
    sample_detail.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        sample_detail.remove_source("root_spell_a")
