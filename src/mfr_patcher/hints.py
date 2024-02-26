from enum import Enum
from typing import Any, Dict, List

from mfr_patcher.locations import Location
from mfr_patcher.rom import Rom
from mfr_patcher.text import Language, encode_text

HINT_TEXT_ADDR = 0x7FE000
HINT_TEXT_END = 0x7FF000

class NavRoom(Enum):
    MAIN_DECK_WEST = 1
    MAIN_DECK_EAST = 2
    OPERATIONS_DECK = 3
    SECTOR1_ENTRANCE = 4
    SECTOR5_ENTRANCE = 5
    SECTOR2_ENTRANCE = 6
    SECTOR4_ENTRANCE = 7
    SECTOR3_ENTRANCE = 8
    SECTOR6_ENTRANCE = 9
    AUXILIARY_POWER = 10
    RESTRICTED_LABS = 11

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

    NAV_ROOM_ENUMS = {
        "MainDeckWest": NavRoom.MAIN_DECK_WEST,
        "MainDeckEast": NavRoom.MAIN_DECK_EAST,
        "OperationsDeck": NavRoom.OPERATIONS_DECK,
        "Sector1Entrance": NavRoom.SECTOR1_ENTRANCE,
        "Sector2Entrance": NavRoom.SECTOR5_ENTRANCE,
        "Sector3Entrance": NavRoom.SECTOR2_ENTRANCE,
        "Sector4Entrance": NavRoom.SECTOR4_ENTRANCE,
        "Sector5Entrance": NavRoom.SECTOR3_ENTRANCE,
        "Sector6Entrance": NavRoom.SECTOR6_ENTRANCE,
        "AuxiliaryPower": NavRoom.AUXILIARY_POWER,
        "RestrictedLabs": NavRoom.RESTRICTED_LABS
    }

    def __init__(self, hints: Dict[Language, Dict[NavRoom, str]]):
        self.hints = hints
    
    @classmethod
    def from_json(cls, data: Any) -> "Hints":
        hints = {}
        for lang, lang_hints in data.items():
            lang = cls.LANG_ENUMS[lang]
            hints[lang] = {cls.NAV_ROOM_ENUMS[k]: v for k, v in lang_hints.items()}
        return cls(hints)

    def write(self, rom: Rom):
        for lang, lang_hints in self.hints.items():
            navigation_text = rom.read_ptr(rom.navigation_text() + lang.value * 4)
            text_addr = HINT_TEXT_ADDR

            for nav_room, hint in lang_hints.items():
                rom.write_ptr(navigation_text + nav_room.value * 8, text_addr)
                rom.write_ptr(navigation_text + nav_room.value * 8 + 4, text_addr)

                for char in encode_text(rom, hint, 224):
                    rom.write_16(text_addr, char)
                    text_addr += 2
                    if text_addr >= HINT_TEXT_END:
                        raise ValueError("Attempted to write too much text to ROM.")
