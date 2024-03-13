from enum import Enum
from typing import Union

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
        # set free space address
        if self.is_mf():
            self.free_space_addr = 0x7E0000
        elif self.is_zm():
            raise NotImplementedError()

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

    def write_bytes(
        self,
        dst_addr: int,
        vals: BytesLike,
        src_addr: int = 0,
        size: int | None = None
    ) -> None:
        if size is None:
            size = len(vals) - src_addr
        dst_end = dst_addr + size
        src_end = src_addr + size
        self.data[dst_addr:dst_end] = vals[src_addr:src_end]

    def copy_bytes(self, src_addr: int, dst_addr: int, size: int) -> None:
        self.write_bytes(dst_addr, self.data, src_addr, size)

    def reserve_free_space(self, size: int, align: int = 1) -> int:
        remain = self.free_space_addr % align
        if remain != 0:
            self.free_space_addr += align - remain
        addr = self.free_space_addr
        self.free_space_addr += size
        return addr

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            f.write(self.data)
