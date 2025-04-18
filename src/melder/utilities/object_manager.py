import uuid
from typing import Optional, List
from melder.utilities.interfaces import IDisposable
import threading
import abc


class Node(IDisposable):
    """
    Node is a subclass of TreeNode that represents a node in the tree structure.
    It can be extended with additional attributes or methods if needed.
    """
    def __init__(self,
                 name: str,
                 node_type: str,
                 object_type: Optional[type] = None,
                 metadata: Optional[dict] = None):
        if node_type not in {"category", "item"}:
            raise ValueError("Type must be 'category' or 'item'.")
        if node_type == "item" and object_type is None:
            raise ValueError("Object type must be provided (class reference, not instance).")

        metadata = {
            "class_name": object_type.__name__,
            "class_type": object_type,
            "interfaces": Node.find_all_abc_names_for_class(object_type),
        }

        self.name: str = name
        self.type: str = node_type
        self.metadata: dict = metadata or {}
        self.children: List["Node"] = []
        self.unique_id: str = str(uuid.uuid4())
        self.disposed: bool = False

    @staticmethod
    def find_all_abc_names_for_class(cls):
        """
        Iteratively finds the names of all ABCs in the inheritance hierarchy
        of a given class using a loop. Accepts a class reference as input.
        Returns a list of unique ABC names.
        """
        queue = list(cls.__bases__)
        visited = {cls}
        abc_names = set()

        while queue:
            base = queue.pop(0)
            if base in visited:
                continue
            visited.add(base)

            if isinstance(base, abc.ABCMeta):
                abc_names.add(base.__name__)

            queue.extend(base.__bases__)

        return list(abc_names)

    def add_child(self, child: "Node") -> None:
        if self.type != "category":
            raise ValueError("Only category nodes can have children (items cannot have children).")
        self.children.append(child)


    def dispose(self):
        """
        Dispose of this node and all its children recursively.
        """
        if self.disposed:
            return

        for child in self.children:
            child.dispose()

        # Here you would release any resources held by this node.
        self.disposed = True
        if isinstance(self.metadata, dict):
            self.metadata.clear()
        self.children.clear()


class ScopeManager(IDisposable):
    """
    ObjectManager is a singleton that manages a TreeManager instance.
    """

    _instance = None
    _lock = threading.RLock()
    _initialized = False

    def __new__(cls, name: str = "Root"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ScopeManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, name: str = "Root"):
        if not ScopeManager._initialized:
            ScopeManager._initialized = True
            self.root: Node = Node(name=name, type="category")
            self.RLock = ScopeManager._lock
            self.disposed = False


    def add_object(self, name: str, node_type: str, parent_name: str, object_type: type) -> None:
        """
        Adds a new node to the tree under the specified parent with a Rlock.
        """
        parent_node = self.find_node(parent_name)
        if not parent_node:
            raise ValueError(f"Parent node '{parent_name}' not found.")
        if parent_node.type != "category":
            raise ValueError(f"Parent node '{parent_name}' must be a category.")
        new_node = Node(name=name, node_type=node_type, object_type=object_type)

        with self.RLock:
            parent_node.add_child(new_node)

    def detailed_find_node(
            self,
            name: str,
            parent_name: str,
            class_name: Optional[str] = None,
            class_type: Optional[str] = None,
            interface: Optional[str] = None
    ) -> Node | None:
        """
        Finds a node by name under the specified parent,
        with optional filtering by class_name, class_type, and interface.
        """
        parent_node = self.find_node(parent_name)
        if not parent_node:
            raise ValueError(f"Parent node '{parent_name}' not found.")

        for child in parent_node.children:
            if child.name == name:
                if class_name and child.metadata.get("class_name") != class_name:
                    continue
                if class_type and child.metadata.get("class_type").__name__ != class_type:
                    continue
                if interface and interface not in child.metadata.get("interfaces", []):
                    continue
                return child
        return None

    def detailed_find_node(self, name: str, parent_name: str) -> Optional[Node]:
        """
        Finds a node by name under the specified parent.
        """
        parent_node = self.find_node(parent_name)
        if not parent_node:
            raise ValueError(f"Parent node '{parent_name}' not found.")

        for child in parent_node.children:
            if child.name == name:
                return child
        return None

    def get_parent_node(self, name: str) -> Optional[Node]:
        """
        Finds the parent of a node by name using breadth-first search.
        """
        queue = [self.root]
        while queue:
            current = queue.pop(0)
            for child in current.children:
                if child.name == name and child.type == "category":
                    return current
            queue.extend(current.children)
        return None


    def add_node(self, name: str, type: str, parent_name: str, metadata: Optional[dict] = None) -> None:
        parent_node = self.find_node(parent_name)
        if not parent_node:
            raise ValueError(f"Parent node '{parent_name}' not found.")
        if parent_node.type != "category":
            raise ValueError(f"Parent node '{parent_name}' must be a category.")

        new_node = Node(name=name, type=type, metadata=metadata)
        parent_node.add_child(new_node)

    def find_node(self, name: str) -> Optional[Node]:
        """
        Finds a node by name using breadth-first search.
        """
        queue = [self.root]
        while queue:
            current = queue.pop(0)
            if current.name == name:
                return current
            queue.extend(current.children)
        return None

    def remove_node(self, name: str) -> None:
        """
        Removes a node by name and all its descendants.
        """
        if self.root.name == name:
            raise ValueError("Cannot remove the root node.")

        parent_node = None
        node_to_remove = None

        queue = [self.root]
        while queue:
            current = queue.pop(0)
            for child in current.children:
                if child.name == name:
                    parent_node = current
                    node_to_remove = child
                    break
            if node_to_remove:
                break
            queue.extend(current.children)

        if not node_to_remove:
            raise ValueError(f"Node '{name}' not found.")

        parent_node.children.remove(node_to_remove)
        print(f"Node '{name}' and its descendants removed.")

    def dispose(self):
        """
        Disposes of the entire tree structure.
        """
        if self.disposed:
            return
        self.root.dispose()
        self.root = None
        ScopeManager._instance = None
        self.disposed = True

