from enum import Enum

from mars_patcher.rom import Rom

CREDITS_ADDR = 0x74B0B0
CREDITS_LEN = 0x2B98
FULL_LINE_LEN = 36


class CharHeight(Enum):
    INVALID = 0
    ONE_LINE = 1,
    TWO_LINES = 2


CONTROL_CHAR_VALS = {
    "BLUE_1": 0,
    "RED_1": 1,
    "WHITE_2": 2,
    "SKIP_1": 5,
    "END": 6,
    "COPYRIGHT1": 0xA,
    "COPYRIGHT2": 0xB,
    "COPYRIGHT3": 0xC,
    "COPYRIGHT4": 0xD
}

CONTROL_CHAR_HEIGHTS = {
    "BLUE_1": CharHeight.ONE_LINE,
    "RED_1": CharHeight.ONE_LINE,
    "WHITE_2": CharHeight.TWO_LINES
}

EXTRA_CHARS = {
    # does not support accented i or apostrophe
    CharHeight.ONE_LINE: {
        "&": 0x26,
        ",": 0x2C,
        ".": 0x2E
    },
    # does not support ampersand
    CharHeight.TWO_LINES: {
        "í": 0x2B,
        ",": 0x2C,
        "'": 0x2D,
        ".": 0x2E
    }
}


def write_credits(rom: Rom, text: str) -> None:
    pending_ctrl_expr = None
    curr_ctrl_expr = None
    curr_line = bytearray()
    char_height = CharHeight.INVALID
    addr = CREDITS_ADDR
    for char in text:
        if char == "[":
            # start of bracketed expression
            pending_ctrl_expr = []
            if len(curr_line) > 0:
                addr = write_line(rom, addr, curr_line)
            curr_line = bytearray()
        elif char == "]":
            # end of bracketed expression
            if pending_ctrl_expr is None:
                raise ValueError("Unexpected closing bracket")
            curr_ctrl_expr = "".join(pending_ctrl_expr)
            char_val = CONTROL_CHAR_VALS.get(curr_ctrl_expr)
            if char_val is None:
                raise ValueError(f"Invalid bracketed expression '{curr_ctrl_expr}'")
            pending_ctrl_expr = None
            curr_line.append(char_val)
            char_height = CONTROL_CHAR_HEIGHTS.get(curr_ctrl_expr, CharHeight.INVALID)
        elif pending_ctrl_expr is not None:
            # middle of bracketed expression
            pending_ctrl_expr.append(char)
        else:
            # normal character
            if char_height == CharHeight.INVALID:
                raise ValueError(f"{curr_ctrl_expr} cannot have any characters")
            if char == " " or "A" <= char <= "Z":
                char_val = ord(char)
            elif "a" <= char <= "z":
                if char_height == CharHeight.ONE_LINE:
                    raise ValueError(f"{curr_ctrl_expr} does not support lowercase characters")
                char_val = ord(char)
            else:
                char_val = EXTRA_CHARS[char_height].get(char)
                if char_val is None:
                    raise ValueError(f"{curr_ctrl_expr} does not support character '{char}'")
            curr_line.append(char_val)
    if pending_ctrl_expr is not None:
        raise ValueError("Bracketed expression not terminated")
    if len(curr_line) > 0:
        print(curr_line)
        addr = write_line(rom, addr, curr_line)
    last_line = bytearray([CONTROL_CHAR_VALS["END"]])
    write_line(rom, addr, last_line)


def write_line(rom: Rom, addr: int, line: bytearray) -> int:
    print(line)
    rom.write_bytes(addr, line, 0, len(line))
    for i in range(len(line), FULL_LINE_LEN):
        rom.write_8(addr + i, 0)
    return addr + FULL_LINE_LEN
