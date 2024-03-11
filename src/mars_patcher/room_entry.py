from mars_patcher.constants.game_data import area_room_entry_ptrs
from mars_patcher.rom import Rom


class RoomEntry:
    def __init__(self, rom: Rom, area: int, room: int):
        self.rom = rom
        self.addr = rom.read_ptr(area_room_entry_ptrs(rom) + area * 4) + room * 0x3C

    def tileset(self) -> int:
        return self.rom.read_8(self.addr)

    def bg1_addr(self) -> int:
        return self.rom.read_ptr(self.addr + 0xC)

    def clip_addr(self) -> int:
        return self.rom.read_ptr(self.addr + 0x14)

    def default_sprite_layout_addr(self) -> int:
        return self.rom.read_ptr(self.addr + 0x20)

    def default_spriteset(self) -> int:
        return self.rom.read_8(self.addr + 0x24)
