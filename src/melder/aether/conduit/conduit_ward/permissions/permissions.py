#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

from enum import Enum, auto

class Permissions(Enum):
    """
    Each level of permission inherits from the previous one.
    """
    read = auto() # Allows reading data
    create = auto() # Allows creating new data, and includes read
    block = auto() # Allows blocking data, used only within Spellbook
