from typing import Any

from mfr_patcher.compress import decomp_rle, comp_rle
from mfr_patcher.locations import LocationSettings, ItemType
from mfr_patcher.rom import Rom
from mfr_patcher.room_entry import RoomEntry
from mfr_patcher.tileset import Tileset


# keep these in sync with base patch
MINOR_LOCS_ADDR = 0x7FF000
MAJOR_LOCS_ADDR = 0x7FF200
TANK_INC_ADDR = 0x7FF220

TANK_CLIP = (0x62, 0x63, 0x68)
HIDDEN_TANK_CLIP = (0x64, 0x65, 0x69)
TANK_BG1_START = 0x40
TANK_TILE = (0x50, 0x54, 0x58)


class ItemPatcher(object):
    """Class for writing item assignments to a ROM."""

    def __init__(self, rom: Rom, settings: LocationSettings):
        self.rom = rom
        self.settings = settings

    # TODO: use separate classes for handling tilesets and backgrounds
    def write_items(self) -> None:
        rom = self.rom
        # handle minor locations
        minor_locs = sorted(
            self.settings.minor_locs,
            key=lambda l: (l.area, l.room, l.block_x, l.block_y)
        )
        prev_area_room = (-1, -1)
        room_tank_count = 0
        for i, loc in enumerate(minor_locs):
            # update room tank count
            area_room = (loc.area, loc.room)
            if area_room == prev_area_room:
                room_tank_count += 1
            else:
                room_tank_count = 1
                prev_area_room = area_room
            tank_slot = room_tank_count - 1

            # overwrite clipdata
            room = RoomEntry(rom, loc.area, loc.room)
            clip_addr = room.clip_addr()
            val = HIDDEN_TANK_CLIP[tank_slot] if loc.hidden else TANK_CLIP[tank_slot]
            self.write_block_val(clip_addr, loc.block_x, loc.block_y, val)
            if not loc.hidden:
                # overwrite BG1
                bg1_addr = room.bg1_addr()
                # get tilemap
                tileset = Tileset(rom, room.tileset())
                addr = tileset.rle_tilemap_addr()
                # find tank in tilemap
                addr += 2 + (TANK_BG1_START * 8)
                tile = TANK_TILE[tank_slot]
                idx = next(i for i in range(16) if rom.read_8(addr + i * 8) == tile)
                val = TANK_BG1_START + idx
                self.write_block_val(bg1_addr, loc.block_x, loc.block_y, val)

            # write to minors table
            addr = MINOR_LOCS_ADDR + i * 4
            assert rom.read_8(addr) == loc.block_x
            assert rom.read_8(addr + 1) == loc.block_y
            assert rom.read_8(addr + 2) == loc.orig_item.value
            if loc.new_item != ItemType.UNDEFINED:
                rom.write_8(addr + 2, loc.new_item.value)
                rom.write_8(addr + 3, loc.new_item.value)

        # handle major locations
        for loc in self.settings.major_locs:
            # write to majors table
            if loc.new_item != ItemType.UNDEFINED:
                addr = MAJOR_LOCS_ADDR + loc.major_src.value
                rom.write_8(addr, loc.new_item.value)

    def write_block_val(self, block_addr: int, x: int, y: int, val: int) -> None:
        # get block data
        width = self.rom.read_8(block_addr)
        data, comp_len = decomp_rle(self.rom.data, block_addr + 2)
        # overwrite value
        idx = (y * width + x) * 2
        data[idx] = val
        data[idx + 1] = 0
        # compress and write to rom
        comp_data = comp_rle(data)
        assert len(comp_data) <= comp_len, f"{len(comp_data):X} > {comp_len:X}"
        self.rom.write_bytes(block_addr + 2, comp_data, 0, len(comp_data))


# TODO: move this?
def set_tank_increments(rom: Rom, data: Any) -> None:
    rom.write_16(TANK_INC_ADDR, data["MissileTank"])
    rom.write_16(TANK_INC_ADDR + 2, data["EnergyTank"])
    rom.write_16(TANK_INC_ADDR + 4, data["PowerBombTank"])
