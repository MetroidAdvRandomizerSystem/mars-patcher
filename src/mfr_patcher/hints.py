from typing import Any, Dict, List

from mfr_patcher.locations import Location
from mfr_patcher.rom import Rom
from mfr_patcher.text import Language, encode_text

HINT_TEXT_ADDR = 0x7FE000
HINT_TEXT_END = 0x7FF000

class Hints:
    LANG_ENUMS = {
        "JapaneseKanji": Language.JAPANESE_KANJI,
        "JapaneseHiragana": Language.JAPANESE_HIRAGANA,
        "English": Language.ENGLISH,
        "German": Language.GERMAN,
        "French": Language.FRENCH,
        "Italian": Language.ITALIAN,
        "Spanish": Language.SPANISH
    }

    def __init__(self, hints: Dict[Language, List[str]]):
        self.hints = hints
    
    @classmethod
    def from_json(cls, data: Any) -> "Hints":
        return cls({cls.LANG_ENUMS[x["Language"]]: x["Hints"] for x in data})

    def write(self, rom: Rom):
        for lang, hints in self.hints.items():
            navigation_text = rom.read_ptr(rom.navigation_text() + lang.value * 4)
            text_addr = HINT_TEXT_ADDR

            for i, hint in enumerate(hints):
                rom.write_ptr(navigation_text + (i + 1) * 8, text_addr)
                rom.write_ptr(navigation_text + (i + 1) * 8 + 4, text_addr)

                for char in encode_text(rom, hint, 224):
                    rom.write_16(text_addr, char)
                    text_addr += 2
                    if text_addr >= HINT_TEXT_END:
                        raise ValueError("Attempted to write too much text to ROM.")
