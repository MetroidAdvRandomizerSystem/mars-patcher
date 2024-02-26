from enum import Enum
from typing import List, Tuple, Union

BytesLike = Union[bytes, bytearray]

SIZE_8MB = 0x800000
ROM_OFFSET = 0x8000000


class Game(Enum):
    MF = 1
    ZM = 2


class Region(Enum):
    U = 1
    E = 2
    J = 3
    C = 4


class Rom:
    def __init__(self, path: str):
        # read file
        with open(path, "rb") as f:
            self.data = bytearray(f.read())
        # check length
        if len(self.data) != SIZE_8MB:
            raise ValueError("ROM should be 8MB")
        # check title and code
        title = self.read_ascii(0xA0, 0x10)
        if title == "METROID4USA\0AMTE":
            self.game = Game.MF
            self.region = Region.U
        elif title == "METROID4EUR\0AMTP":
            self.game = Game.MF
            self.region = Region.E
        elif title == "METROID4JPN\0AMTJ":
            self.game = Game.MF
            self.region = Region.J
        elif title == "METFUSIONCHNAMTC":
            self.game = Game.MF
            self.region = Region.C
        elif title == "ZEROMISSIONEBMXE":
            self.game = Game.ZM
            self.region = Region.U
        elif title == "ZEROMISSIONPBMXP":
            self.game = Game.ZM
            self.region = Region.E
        elif title == "ZEROMISSIONJBMXJ":
            self.game = Game.ZM
            self.region = Region.J
        elif title == "ZEROMISSIONCBMXC":
            self.game = Game.ZM
            self.region = Region.C
        else:
            raise ValueError("Not a valid GBA Metroid ROM")
        # for now we only allow MF U
        if self.game == Game.ZM:
            raise ValueError("Not compatible with Metroid Zero Mission")
        if self.region != Region.U:
            raise ValueError("Only compatible with the North American (U) version")

    def is_mf(self) -> bool:
        return self.game == Game.MF

    def is_zm(self) -> bool:
        return self.game == Game.ZM

    def read_8(self, addr: int) -> int:
        return self.data[addr]

    def read_16(self, addr: int) -> int:
        return self.data[addr] | (self.data[addr + 1] << 8)

    def read_32(self, addr: int) -> int:
        return (
            self.data[addr]
            | (self.data[addr + 1] << 8)
            | (self.data[addr + 2] << 16)
            | (self.data[addr + 3] << 24)
        )

    def read_ptr(self, addr: int) -> int:
        val = self.read_32(addr)
        if val < ROM_OFFSET:
            raise ValueError(f"Invalid pointer {val:X} at {addr:X}")
        return val - ROM_OFFSET

    def read_bytes(self, addr: int, size: int) -> bytearray:
        end = addr + size
        return self.data[addr:end]

    def read_ascii(self, addr: int, size: int) -> str:
        return self.read_bytes(addr, size).decode("ascii")

    def write_8(self, addr: int, val: int) -> None:
        self.data[addr] = val & 0xFF

    def write_16(self, addr: int, val: int) -> None:
        val &= 0xFFFF
        self.data[addr] = val & 0xFF
        self.data[addr + 1] = val >> 8

    def write_32(self, addr: int, val: int) -> None:
        val &= 0xFFFFFFFF
        self.data[addr] = val & 0xFF
        self.data[addr + 1] = (val >> 8) & 0xFF
        self.data[addr + 2] = (val >> 16) & 0xFF
        self.data[addr + 3] = val >> 24

    def write_ptr(self, addr: int, val: int) -> None:
        assert val < ROM_OFFSET, f"Pointer should be less than {ROM_OFFSET:X} but is {val:X}"
        self.write_32(addr, val + ROM_OFFSET)

    def write_bytes(self, dst_addr: int, vals: BytesLike, src_addr: int, size: int) -> None:
        dst_end = dst_addr + size
        src_end = src_addr + size
        self.data[dst_addr:dst_end] = vals[src_addr:src_end]

    def copy_bytes(self, src_addr: int, dst_addr: int, size: int) -> None:
        self.write_bytes(dst_addr, self.data, src_addr, size)

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            f.write(self.data)

    # TODO: move these to separate file

    def room_entry_addr(self) -> int:
        """Returns the address of the room entries."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x79B8BC
            elif self.region == Region.E:
                return 0x79C0F0
            elif self.region == Region.J:
                return 0x7EDF6C
            elif self.region == Region.C:
                return 0x77D5C0
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return 0x75FAC4
            elif self.region == Region.E:
                return 0x773964
            elif self.region == Region.J:
                return 0x75FBD4
            elif self.region == Region.C:
                return 0x79ECBC

    def tileset_addr(self) -> int:
        """Returns the address of the tileset entries."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x3BF888
            elif self.region == Region.E:
                return 0x3BFEE4
            elif self.region == Region.J:
                return 0x3C1E50
            elif self.region == Region.C:
                return 0x3C1E94
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return 0x33DFDC
            elif self.region == Region.E:
                return 0x33EC68
            elif self.region == Region.J:
                return 0x33E038
            elif self.region == Region.C:
                return 0x3577C8

    def tileset_count(self) -> int:
        """Returns the number of tilesets in the game."""
        if self.game == Game.MF:
            return 0x62
        elif self.game == Game.ZM:
            return 0x4F

    def starting_equipment_addr(self) -> int:
        """Returns the address of the starting equipment data."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x28D2AC
            elif self.region == Region.E:
                return 0x28D908
            elif self.region == Region.J:
                return 0x28F5B4
            elif self.region == Region.C:
                return 0x28F5F8
        elif self.game == Game.ZM:
            raise NotImplementedError("Currently not implemented for ZM")

    def anim_palette_addr(self) -> int:
        """Returns the address of the animated palette entries."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x3E3764
            elif self.region == Region.E:
                return 0x3E3DC0
            elif self.region == Region.J:
                return 0x3E5D38
            elif self.region == Region.C:
                return 0x3E5D7C
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return 0x35FBFC
            elif self.region == Region.E:
                return 0x360888
            elif self.region == Region.J:
                return 0x35FC58
            elif self.region == Region.C:
                return 0x3793E8

    def anim_palette_count(self) -> int:
        """Returns the number of animated palettes in the game."""
        if self.game == Game.MF:
            if self.region == Region.U or self.region == Region.E:
                return 0x21
            elif self.region == Region.J or self.region == Region.C:
                return 0x22
        elif self.game == Game.ZM:
            return 0x12

    def sprite_vram_size_addr(self) -> int:
        """Returns the address of the sprite VRAM sizes."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x2E4A50
            elif self.region == Region.E:
                return 0x2E50AC
            elif self.region == Region.J:
                return 0x2E6D58
            elif self.region == Region.C:
                return 0x2E6D9C
        elif self.game == Game.ZM:
            raise NotImplementedError("Currently not implemented for ZM")

    def sprite_graphics_addr(self) -> int:
        """Returns the address of the sprite graphics pointers."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x79A5D8
            elif self.region == Region.E:
                return 0x79AE0C
            elif self.region == Region.J:
                return 0x7ECC88
            elif self.region == Region.C:
                return 0x77C2DC
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return 0x75EBF8
            elif self.region == Region.E:
                return 0x772A98
            elif self.region == Region.J:
                return 0x75ED08
            elif self.region == Region.C:
                return 0x79DDF0

    def sprite_palette_addr(self) -> int:
        """Returns the address of the sprite palette pointers."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x79A8D4
            elif self.region == Region.E:
                return 0x79B108
            elif self.region == Region.J:
                return 0x7ECF84
            elif self.region == Region.C:
                return 0x77C5D8
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return 0x75EEF0
            elif self.region == Region.E:
                return 0x772D90
            elif self.region == Region.J:
                return 0x75F000
            elif self.region == Region.C:
                return 0x79E0E8

    def sprite_count(self) -> int:
        """Returns the number of sprites in the game."""
        if self.game == Game.MF:
            return 0xCF
        elif self.game == Game.ZM:
            return 0xCE

    def spriteset_addr(self) -> int:
        """Returns the address of the spriteset pointers."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x79ADD8
            elif self.region == Region.E:
                return 0x79B60C
            elif self.region == Region.J:
                return 0x7ED488
            elif self.region == Region.C:
                return 0x77CADC
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return 0x75F31C
            elif self.region == Region.E:
                return 0x7731BC
            elif self.region == Region.J:
                return 0x75F42C
            elif self.region == Region.C:
                return 0x79E514

    def spriteset_count(self) -> int:
        """Returns the number of spritesets in the game."""
        if self.game == Game.MF:
            return 0x82
        elif self.game == Game.ZM:
            return 0x72

    def samus_palettes(self) -> List[Tuple[int, int]]:
        """Returns a list of (address, row count) pairs."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return [(0x28DD7C, 0x5E), (0x28EAFC, 0x70)]
            elif self.region == Region.E:
                return [(0x28E3D8, 0x5E), (0x28F158, 0x70)]
            elif self.region == Region.J:
                return [(0x290084, 0x5E), (0x290E04, 0x70)]
            elif self.region == Region.C:
                return [(0x2900C8, 0x5E), (0x290E48, 0x70)]
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return [(0x2376A8, 0xA3)]
            elif self.region == Region.E:
                return [(0x238334, 0xA3)]
            elif self.region == Region.J:
                return [(0x237704, 0xA3)]
            elif self.region == Region.C:
                return [(0x250E94, 0xA3)]

    def file_select_helmet_palettes(self) -> list[Tuple[int, int]]:
        """Returns a list of (address, row count) pairs."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return [(0x740E08, 0x1), (0x740EA8, 0x2)]
            elif self.region == Region.E:
                return [(0x741618, 0x1), (0x7416B8, 0x2)]
            elif self.region == Region.J:
                return [(0x73FCDC, 0x1), (0x73FD7C, 0x2)]
            elif self.region == Region.C:
                return [(0x6CE360, 0x1), (0x6CE400, 0x2)]
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return [(0x454938, 0x1), (0x4549B8, 0x1)]
            elif self.region == Region.E:
                return [(0x4603F8, 0x1), (0x460478, 0x1)]
            elif self.region == Region.J:
                return [(0x454994, 0x1), (0x454A14, 0x1)]
            elif self.region == Region.C:
                return [(0x4768FC, 0x1), (0x47697C, 0x1)]

    def beam_palettes(self) -> list[Tuple[int, int]]:
        """Returns a list of (address, row count) pairs."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return [(0x58B464, 0x6)]
            elif self.region == Region.E:
                return [(0x58BAC0, 0x6)]
            elif self.region == Region.J:
                return [(0x58BBF4, 0x6)]
            elif self.region == Region.C:
                return [(0x592578, 0x6)]
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return [(0x3270E8, 0x6)]
            elif self.region == Region.E:
                return [(0x327D74, 0x6)]
            elif self.region == Region.J:
                return [(0x327144, 0x6)]
            elif self.region == Region.C:
                return [(0x3408D4, 0x6)]

    def tourian_statues_cutscene_palette(self) -> int:
        """Returns the address of the palette used for the Tourian statue cutscenes."""
        if self.game == Game.ZM:
            if self.region == Region.U:
                return 0x3ED53C
            elif self.region == Region.E:
                return 0x3EE1C8
            elif self.region == Region.J:
                return 0x3ED598
            elif self.region == Region.C:
                return 0x406D28
        elif self.game == Game.MF:
            raise ValueError("Tourian statues are not supported for Fusion")

    def file_screen_text(self) -> int:
        """Returns the address of the file screen text pointers."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x79EC68
            elif self.region == Region.E:
                return 0x79F4C4
            elif self.region == Region.J:
                return 0x7F13FC
        raise NotImplementedError("Currently not implemented for ZM")

    def character_widths_addr(self) -> int:
        """Returns the address of the character width array."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x576234
            elif self.region == Region.E:
                return 0x576890
            elif self.region == Region.J:
                return 0x578934
            elif self.region == Region.C:
                return 0x57D21C
        elif self.game == Game.ZM:
            if self.region == Region.U:
                return 0x40D7B0
            elif self.region == Region.E:
                return 0x40E5E4
            elif self.region == Region.J:
                return 0x40D80C
            elif self.region == Region.C:
                return 0x42F34C

    def navigation_text(self) -> int:
        """Returns the address of the navigation room text pointers."""
        if self.game == Game.MF:
            if self.region == Region.U:
                return 0x79C0F0
            elif self.region == Region.E:
                return 0x79C924
            elif self.region == Region.J:
                return 0x7EE7A0
            elif self.region == Region.C:
                return 0x77DDF4
        if self.game == Game.ZM:
            raise ValueError("Navigation Station text is not supported for ZM")

