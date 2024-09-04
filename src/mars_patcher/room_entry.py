from mars_patcher.compress import comp_rle, decomp_rle
from mars_patcher.constants.game_data import area_room_entry_ptrs
from mars_patcher.rom import Rom


class RoomEntry:
    def __init__(self, rom: Rom, area: int, room: int):
        self.rom = rom
        self.addr = rom.read_ptr(area_room_entry_ptrs(rom) + area * 4) + room * 0x3C

    def bg1_ptr(self) -> int:
        return self.addr + 0xC

    def bg2_ptr(self) -> int:
        return self.addr + 0x10

    def clip_ptr(self) -> int:
        return self.addr + 0x14

    def tileset(self) -> int:
        return self.rom.read_8(self.addr)

    def bg1_addr(self) -> int:
        return self.rom.read_ptr(self.bg1_ptr())

    def bg2_addr(self) -> int:
        return self.rom.read_ptr(self.bg2_ptr())

    def clip_addr(self) -> int:
        return self.rom.read_ptr(self.clip_ptr())

    def default_sprite_layout_addr(self) -> int:
        return self.rom.read_ptr(self.addr + 0x20)

    def default_spriteset(self) -> int:
        return self.rom.read_8(self.addr + 0x24)

    def load_bg1(self) -> None:
        self.bg1_data = BlockLayer(self.rom, self.bg1_addr())

    def set_bg1_block(self, value: int, x: int, y: int) -> None:
        self.bg1_data.set_block_value(value, x, y)

    def write_bg1(self) -> None:
        self.bg1_data.write(self.rom, self.bg1_ptr())

    def load_bg2(self) -> None:
        self.bg2_data = BlockLayer(self.rom, self.bg2_addr())

    def set_bg2_block(self, value: int, x: int, y: int) -> None:
        self.bg2_data.set_block_value(value, x, y)

    def write_bg2(self) -> None:
        self.bg2_data.write(self.rom, self.bg2_ptr())

    def load_clip(self) -> None:
        self.clip_data = BlockLayer(self.rom, self.clip_addr())

    def get_clip_block(self, x: int, y: int) -> int:
        return self.clip_data.get_block_value(x, y)

    def set_clip_block(self, value: int, x: int, y: int) -> None:
        self.clip_data.set_block_value(value, x, y)

    def write_clip(self) -> None:
        self.clip_data.write(self.rom, self.clip_ptr())


class BlockLayer:
    def __init__(self, rom: Rom, addr: int):
        self.width = rom.read_8(addr)
        self.height = rom.read_8(addr + 1)
        self.block_data, self.comp_len = decomp_rle(rom.data, addr + 2)

    def get_block_value(self, x: int, y: int) -> int:
        idx = (y * self.width + x) * 2
        return self.block_data[idx] | self.block_data[idx + 1] << 8

    def set_block_value(self, value: int, x: int, y: int) -> None:
        idx = (y * self.width + x) * 2
        if idx >= len(self.block_data):
            raise IndexError(f"Block coordinate ({x}, {y}) is out of bounds! Room size: ({self.width}, {self.height})")
        self.block_data[idx] = value & 0xFF
        self.block_data[idx + 1] = value >> 8

    def write(self, rom: Rom, ptr: int) -> None:
        comp_data = comp_rle(self.block_data)
        comp_len = len(comp_data)
        if comp_len > self.comp_len:
            # repoint data
            addr = rom.reserve_free_space(comp_len + 2)
            rom.write_ptr(ptr, addr)
        else:
            addr = rom.read_ptr(ptr)
        rom.write_8(addr, self.width)
        rom.write_8(addr + 1, self.height)
        rom.write_bytes(addr + 2, comp_data)
        self.comp_len = comp_len
