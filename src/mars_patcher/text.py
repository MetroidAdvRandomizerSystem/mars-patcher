from enum import Enum

from mars_patcher.constants.game_data import character_widths, file_screen_text_ptrs
from mars_patcher.rom import Rom

NEXT = 0xFD00
NEWLINE = 0xFE00
END = 0xFF00
ESCAPE_EXPRESSIONS = {
    "NEXT": NEXT,
    "NEWLINE": NEWLINE,
    "END": END,
    "OBJECTIVE": 0xFB00,
    "/COLOR": 0x8100,
    "TARGET": 0xE00,
    "GAME_START": 0xB003,
}

CHARS = {
    " ": 0x40,
    "!": 0x41,
    '"': 0x42,
    "#": 0x43,
    "$": 0x44,
    "%": 0x45,
    "&": 0x46,
    "'": 0x47,
    "(": 0x48,
    ")": 0x49,
    "*": 0x4A,
    "+": 0x4B,
    ",": 0x4C,
    "-": 0x4D,
    ".": 0x4E,
    "/": 0x4F,
    "0": 0x50,
    "1": 0x51,
    "2": 0x52,
    "3": 0x53,
    "4": 0x54,
    "5": 0x55,
    "6": 0x56,
    "7": 0x57,
    "8": 0x58,
    "9": 0x59,
    ":": 0x5A,
    ";": 0x5B,
    "?": 0x5F,
    "A": 0x81,
    "B": 0x82,
    "C": 0x83,
    "D": 0x84,
    "E": 0x85,
    "F": 0x86,
    "G": 0x87,
    "H": 0x88,
    "I": 0x89,
    "J": 0x8A,
    "K": 0x8B,
    "L": 0x8C,
    "M": 0x8D,
    "N": 0x8E,
    "O": 0x8F,
    "P": 0x90,
    "Q": 0x91,
    "R": 0x92,
    "S": 0x93,
    "T": 0x94,
    "U": 0x95,
    "V": 0x96,
    "W": 0x97,
    "X": 0x98,
    "Y": 0x99,
    "Z": 0x9A,
    "a": 0xC1,
    "b": 0xC2,
    "c": 0xC3,
    "d": 0xC4,
    "e": 0xC5,
    "f": 0xC6,
    "g": 0xC7,
    "h": 0xC8,
    "i": 0xC9,
    "j": 0xCA,
    "k": 0xCB,
    "l": 0xCC,
    "m": 0xCD,
    "n": 0xCE,
    "o": 0xCF,
    "p": 0xD0,
    "q": 0xD1,
    "r": 0xD2,
    "s": 0xD3,
    "t": 0xD4,
    "u": 0xD5,
    "v": 0xD6,
    "w": 0xD7,
    "x": 0xD8,
    "y": 0xD9,
    "z": 0xDA,
    "\n": NEWLINE,
}


class Language(Enum):
    JAPANESE_KANJI = 0
    JAPANESE_HIRAGANA = 1
    ENGLISH = 2
    GERMAN = 3
    FRENCH = 4
    ITALIAN = 5
    SPANISH = 6


class MessageType(Enum):
    NAVIGATION = 0
    ITEM = 1


def parse_escape_expr(expr: str) -> int:
    if "=" in expr:
        label, value = expr.split("=", 1)
        if label == "COLOR":
            return 0x8100 | int(value, 16)
        else:
            raise NotImplementedError(f'Unimplemented bracketed expression "{expr}"')

    if expr in ESCAPE_EXPRESSIONS:
        return ESCAPE_EXPRESSIONS[expr]
    else:
        raise NotImplementedError(f'Unimplemented bracketed expression "{expr}"')


def encode_text(rom: Rom, message_type: MessageType, string: str, max_width: int) -> list[int]:
    char_widths = character_widths(rom)
    text = []
    line_width = 0
    line_number = 0

    prev_break = None
    width_since_break = 0
    escape_expr: list[str] | None = None

    for char in string:
        if escape_expr is None and char == "[":
            escape_expr = []
        elif escape_expr is not None and char == "]":
            text.append(parse_escape_expr("".join(escape_expr)))
            escape_expr = None
            continue
        elif escape_expr is not None:
            escape_expr.append(char)

        if escape_expr is not None:
            continue

        char_val = CHARS[char]
        char_width = rom.read_8(char_widths + char_val) if char_val < 0x4A0 else 10
        line_width += char_width
        width_since_break += char_width

        if char_val == CHARS[" "]:
            prev_break = len(text)
            width_since_break = 0

        extra_char = None

        if line_width > max_width:
            line_width = width_since_break
            width_since_break = 0
            line_number += 1
            extra_char = NEWLINE

        if line_number > 1:
            match message_type:
                case MessageType.NAVIGATION:
                    line_number = 0
                    extra_char = NEXT
                case MessageType.ITEM:
                    # Item messages can only have 2 lines, trim any other characters
                    break

        if extra_char is not None:
            if prev_break is not None:
                if len(text) <= prev_break:
                    text.append(extra_char)
                    continue
                else:
                    text[prev_break] = extra_char
                prev_break = None
            else:
                text.append(extra_char)

        text.append(char_val)

    if message_type == MessageType.ITEM and NEWLINE not in text:
        # Item messages MUST have two lines, append NEWLINE if none exists
        text.append(NEWLINE)

    text.append(END)
    return text


def write_seed_hash(rom: Rom, seed_hash: str) -> None:
    lang_ptrs = file_screen_text_ptrs(rom)
    for lang in Language:
        # Get address of first text entry
        text_ptrs = rom.read_ptr(lang_ptrs + lang.value * 4)
        addr = rom.read_ptr(text_ptrs)
        # Find newline after "SAMUS DATA"
        try:
            line_len = next(i for i in range(20) if rom.read_16(addr + i * 2) == NEWLINE)
        except StopIteration:
            raise ValueError("Invalid file screen text data")
        pad_left = (line_len - 8) // 2
        pad_right = line_len - 8 - pad_left
        # Overwrite with seed hash
        string = (" " * pad_left) + seed_hash + (" " * pad_right)
        for i, c in enumerate(string):
            rom.write_16(addr + i * 2, CHARS[c])
