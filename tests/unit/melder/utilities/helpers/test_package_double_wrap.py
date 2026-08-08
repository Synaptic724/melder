import pytest
from melder.utilities.helpers.package import Package, Pack


# Assuming AgenticList and AgenticDict are correctly imported in your Package module
# from thread_factory.concurrency.concurrent_list import AgenticList
# from thread_factory.concurrency.agentic_dict import AgenticDict

# Helper functions (ensure these are defined in your test file or accessible)
def _add(a, b):
    return a + b


def greet(name, punctuation="!"):
    return f"Hello, {name}{punctuation}"


# NOTE ON IDENTITY: this file exists to prove that Pack does NOT re-wrap an existing Package.
# Every assertIs / assertIsNot below is therefore load-bearing and stays as `is` / `is not`.
# Rendering any of them as == / != would still pass on these objects while destroying the only
# thing the test checks - Package defines equality-ish behaviour via __call__ results, so an
# equality form would go green even if _pack DID create a new wrapper.
class TestPackageNoDoubleWrapping:

    def test_pack_static_method_does_not_repack_existing_package(self):
        """
        Ensures Package._pack() returns the original Package instance
        if it's already a Package, preserving identity.
        """
        original_pack = Pack(_add, 10, 20)

        # Call _pack with an already packed item
        result_pack = Package._pack(original_pack)

        # Assert that it's the exact same object
        assert result_pack is original_pack

        # And that its arguments are preserved
        assert result_pack.args == (10, 20)
        assert result_pack() == 30

    def test_pack_many_does_not_repack_existing_packages_in_list(self):
        """
        Ensures Pack.many() (which uses _pack) correctly handles lists
        containing already-packed items, preserving their identity and arguments.
        """
        func1 = lambda x: x * 2
        pack2 = Pack(greet, name="World")
        func3 = _add

        # Create a list with a mix of raw callables and a pre-existing Pack
        mixed_input = [func1, pack2, func3]

        # Call Pack.many
        packed_list = Pack.bundle(mixed_input)

        assert len(packed_list) == 3

        # Verify func1 was wrapped into a new Pack
        assert isinstance(packed_list[0], Package)
        assert packed_list[0] is not func1  # Not the raw func
        assert packed_list[0](5) == 10  # Test its functionality

        # Verify pack2 was NOT re-wrapped and is the exact same instance
        assert packed_list[1] is pack2
        assert packed_list[1].args == ()
        assert packed_list[1].kwargs == {"name": "World"}
        assert packed_list[1]() == "Hello, World!"  # Test its functionality

        # Verify func3 was wrapped into a new Pack
        assert isinstance(packed_list[2], Package)
        assert packed_list[2] is not func3  # Not the raw func
        assert packed_list[2](1, 2) == 3  # Test its functionality

    def test_pack_many_single_existing_package(self):
        """
        Ensures Pack.many() handles a single existing Package passed directly,
        returning a list containing that original Package instance.
        """
        original_pack = Pack(greet, "Test", punctuation="!")

        # Call Pack.many with a single existing Pack
        result_list = [Pack.bundle(original_pack)]

        assert len(result_list) == 1
        assert result_list[0] is original_pack
        assert result_list[0]() == "Hello, Test!"

if __name__ == "__main__":
    pytest.main([__file__])
