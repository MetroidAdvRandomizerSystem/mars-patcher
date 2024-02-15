from rom import Rom


class RoomEntry(object):
    def __init__(self, rom: Rom, area: int, room: int):
        self.rom = rom
        self.addr = rom.read_ptr(rom.room_entry_addr() + area * 4) + room * 0x3C

    def tileset(self) -> int:
        return self.rom.read_8(self.addr)

    def bg1_addr(self) -> int:
        return self.rom.read_ptr(self.addr + 0xC)

    def clip_addr(self) -> int:
        return self.rom.read_ptr(self.addr + 0x14)
