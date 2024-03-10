from __future__ import annotations

from enum import Enum

from mars_patcher.constants.game_data import navigation_text_ptrs
from mars_patcher.rom import Rom
from mars_patcher.text import Language, encode_text

# keep these in sync with base patch
HINT_TEXT_ADDR = 0x7F0000
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

# Later down the line, when/if Nav terminals don't have their
# confirm text patched out, combine these two.
class ShipText(Enum):
    INITIAL_TEXT = 0
    CONFIRM_TEXT = 1


class NavigationText:
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

    INFO_TEXT_ENUMS = {
        "InitialText": ShipText.INITIAL_TEXT,
        "ConfirmText": ShipText.CONFIRM_TEXT,
    }

    def __init__(self, navigation_text: dict[Language, dict[str, dict[Enum, str]]]):
        self.navigation_text = navigation_text

    @classmethod
    def from_json(cls, data: dict) -> NavigationText:
        navigation_text: dict[Language, dict[str, dict[Enum, str]]] = {}
        for lang, lang_text in data.items():
            lang = cls.LANG_ENUMS[lang]
            navigation_text[lang] = {
                "NavigationTerminals":
                    {cls.NAV_ROOM_ENUMS[k]: v for k, v in lang_text["NavigationTerminals"].items()},
                "ShipText": {cls.INFO_TEXT_ENUMS[k]: v for k, v in lang_text["ShipText"].items()}
            }
        return cls(navigation_text)

    def write(self, rom: Rom) -> None:
        text_addr = HINT_TEXT_ADDR
        for lang, lang_texts in self.navigation_text.items():
            base_text_address = rom.read_ptr(navigation_text_ptrs(rom) + lang.value * 4)

            # Info Text
            for info_place, text in lang_texts["ShipText"].items():

                rom.write_ptr(base_text_address + info_place.value * 4, text_addr)
                rom.write_ptr(base_text_address + info_place.value * 4 + 4, text_addr)

                for char in encode_text(rom, text, 224):
                    rom.write_16(text_addr, char)
                    text_addr += 2
                    if text_addr >= HINT_TEXT_END:
                        raise ValueError("Attempted to write too much text to ROM.")

            # Navigation Text
            for nav_room, text in lang_texts["NavigationTerminals"].items():
                rom.write_ptr(base_text_address + nav_room.value * 8, text_addr)
                rom.write_ptr(base_text_address + nav_room.value * 8 + 4, text_addr)

                for char in encode_text(rom, text, 224):
                    rom.write_16(text_addr, char)
                    text_addr += 2
                    if text_addr >= HINT_TEXT_END:
                        raise ValueError("Attempted to write too much text to ROM.")


