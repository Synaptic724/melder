from enum import Enum, auto
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Permissions(Enum):
    """
    Permission level attached to a contracted or locally owned spell lineage.

    The values are ordered by capability:

    - `read`:
      the spell may be resolved/inspected through a contract, but not used as a
      creation source for contract propagation.

    - `create`:
      the spell may be used as a creation-capable dependency and therefore
      implies read access too.

    - `block`:
      the spell is intentionally not contractable in normal policy flows and is
      used as an internal blocking signal within the spellbook/ward layer.
    """
    __melder_internal__ = _mrg.sentinel
    read = auto()   # Allows read/resolve access only.
    create = auto() # Allows creation-capable use and implies read.
    block = auto()  # Blocks sharing/contracting in normal flows.
