"""
License metadata exposed by the top-level Melder package.

Contract:
- `__license__` is the short machine-friendly license label exported by the
  package root. It carries the SPDX identifier, which is what `pyproject.toml`
  declares and what packaging tools read, so the two cannot drift apart
  silently.
- The embedded Apache-2.0 header is informational/legal context, not
  executable runtime logic. Melder moved from AGPL-3.0-or-later to the Apache
  License 2.0 on the owner's decision (2026-11-07, 0.2.8279).
"""

#    Melder - AI-native dependency graph runtime for free-threaded Python.
#    Copyright (C) 2025-2026 Mark Thomas Geleta
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

__license__ = "Apache-2.0"
