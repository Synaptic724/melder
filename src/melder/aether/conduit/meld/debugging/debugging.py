from dataclasses import dataclass, field
import time
import uuid
from datetime import datetime

@dataclass
class ConduitCreationContext:
    """
    This class represents details on when the scope was created.
    """
    _conduit_id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)
    _creation_time: datetime = field(default_factory=datetime.now, init=False)
    _creation_time_ns: int = field(default_factory=time.time_ns, init=False)


@dataclass
class ObjectCreationContext:
    """
    This is a data class that represents details on which scope created the object.
    It will provide the conduit ID on creation and allow the user to better understand who made what and when.
    """
    _conduit_id: uuid.UUID

    _object_id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)
    _creation_time: datetime = field(default_factory=datetime.now, init=False)
    _creation_time_ns: int = field(default_factory=time.time_ns, init=False)
