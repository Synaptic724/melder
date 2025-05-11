import uuid
from typing import List
from melder.aether.conduit.conduit_ward.links.permissions.permissions import Permission


class LinkContract:
    def __init__(self, object_id: uuid.UUID, permissions: List[Permission], propagate: bool = False):
        self.object_id = object_id
        self.permissions = permissions
        self.propagate = propagate
