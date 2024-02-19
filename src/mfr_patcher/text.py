from mfr_patcher.rom import Rom


CHARS = {
    " ": 0x40,
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
}

NEWLINE = 0xFE00


def write_seed_hash(rom: Rom, seed_hash: str) -> None:
    lang_ptrs = rom.file_screen_text()
    for lang in range(7):
        # get address of first text entry
        text_ptrs = rom.read_ptr(lang_ptrs + lang * 4)
        addr = rom.read_ptr(text_ptrs)
        # find newline after "SAMUS DATA"
        try:
            line_len = next(i for i in range(20) if rom.read_16(addr + i * 2) == NEWLINE)
        except StopIteration:
            raise ValueError("Invalid file screen text data")
        pad_left = (line_len - 8) // 2
        pad_right = line_len - 8 - pad_left
        # overwrite with seed hash
        string = (" " * pad_left) + seed_hash + (" " * pad_right)
        for i, c in enumerate(string):
            rom.write_16(addr + i * 2, CHARS[c])
