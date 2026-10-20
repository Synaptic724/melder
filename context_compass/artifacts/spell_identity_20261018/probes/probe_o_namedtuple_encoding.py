"""Print the unhashed encoding of a few targets so -O and default runs can be diffed (probe, not src)."""
import sys
sys.path.insert(0, sys.argv[1])
from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest
from melder.utilities.ai_native_support_tools.system_document_view import Section
from melder.utilities.ai_native_support_tools.agent_text_reader import TextChunk


class Open(SpellCodeDigest):
    """A digest whose hash step returns its text, bracketed, so the encoding shows every line."""

    @staticmethod
    def _sha(text: str) -> str:
        return "[" + text + "]"


d = Open()
for target in (Section, TextChunk):
    print(target.__qualname__)
    print(d.target_encoding(target))
d.cleanup()
