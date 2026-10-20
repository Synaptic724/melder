"""Run the python block of release_note_s4.py's SECTION exactly as written (melder imported as md)."""
import ast
import pathlib
import re
import sys

source = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
section = ast.literal_eval(re.search(r"^SECTION = ('''.*?''')\n", source, re.S | re.M).group(1))
block = re.search(r"```python\n(.*?)```", section, re.S).group(1)
import melder as md

namespace = {"md": md, "__name__": "__release_note__"}
try:
    exec(compile(block, "release_note_block", "exec"), namespace)
except ValueError as error:
    print("raised ValueError:", str(error)[:14], "...", str(error)[-22:])
else:
    print("every assert holds")
