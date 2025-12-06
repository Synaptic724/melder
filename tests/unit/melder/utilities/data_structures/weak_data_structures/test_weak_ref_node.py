from melder.utilities.data_structures.weak_data_structures.weak_ref_node import WeakRefNode


def test_weak_ref_node_holds_value():
    node = WeakRefNode("val")
    assert node.value == "val"
