from typing import Any, Dict

from mars_patcher.compress import comp_rle, decomp_rle
from mars_patcher.locations import ItemType, LocationSettings
from mars_patcher.rom import Rom
from mars_patcher.room_entry import RoomEntry
from mars_patcher.tileset import Tileset

# keep these in sync with base patch
MINOR_LOCS_ADDR = 0x7FF000
MAJOR_LOCS_ADDR = 0x7FF200
TANK_INC_ADDR = 0x7FF220

TANK_CLIP = (0x62, 0x63, 0x68)
HIDDEN_TANK_CLIP = (0x64, 0x65, 0x69)
TANK_BG1_START = 0x40
TANK_TILE = (0x50, 0x54, 0x58)


class ItemPatcher:
    """Class for writing item assignments to a ROM."""

    def __init__(self, rom: Rom, settings: LocationSettings):
        self.rom = rom
        self.settings = settings

    # TODO: use separate classes for handling tilesets and backgrounds
    def write_items(self) -> None:
        rom = self.rom
        # handle minor locations
        minor_locs = sorted(
            self.settings.minor_locs, key=lambda m: (m.area, m.room, m.block_x, m.block_y)
        )
        prev_area_room = (-1, -1)
        room_tank_count = 0
        for i, min_loc in enumerate(minor_locs):
            # update room tank count
            area_room = (min_loc.area, min_loc.room)
            if area_room == prev_area_room:
                room_tank_count += 1
            else:
                room_tank_count = 1
                prev_area_room = area_room
            tank_slot = room_tank_count - 1

            # overwrite clipdata
            room = RoomEntry(rom, min_loc.area, min_loc.room)
            clip_addr = room.clip_addr()
            val = HIDDEN_TANK_CLIP[tank_slot] if min_loc.hidden else TANK_CLIP[tank_slot]
            self.write_block_val(clip_addr, min_loc.block_x, min_loc.block_y, val)
            if not min_loc.hidden:
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
                self.write_block_val(bg1_addr, min_loc.block_x, min_loc.block_y, val)

            # write to minors table
            addr = MINOR_LOCS_ADDR + i * 4
            assert rom.read_8(addr) == min_loc.block_x
            assert rom.read_8(addr + 1) == min_loc.block_y
            assert rom.read_8(addr + 2) == min_loc.orig_item.value
            if min_loc.new_item != ItemType.UNDEFINED:
                rom.write_8(addr + 2, min_loc.new_item.value)
                rom.write_8(addr + 3, min_loc.new_item.value)

        # handle major locations
        for maj_loc in self.settings.major_locs:
            # write to majors table
            if maj_loc.new_item != ItemType.UNDEFINED:
                addr = MAJOR_LOCS_ADDR + maj_loc.major_src.value
                rom.write_8(addr, maj_loc.new_item.value)

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
BEAM_FLAGS = {"ChargeBeam": 1, "WideBeam": 2, "PlasmaBeam": 4, "WaveBeam": 8, "IceBeam": 0x10}
MISSILE_BOMB_FLAGS = {
    "Missiles": 1,
    "SuperMissiles": 2,
    "IceMissiles": 4,
    "DiffusionMissiles": 8,
    "Bombs": 0x10,
    "PowerBombs": 0x20,
}
SUIT_MISC_FLAGS = {
    "HiJump": 1,
    "SpeedBooster": 2,
    "SpaceJump": 4,
    "ScrewAttack": 8,
    "VariaSuit": 0x10,
    "GravitySuit": 0x20,
    "MorphBall": 0x40,
    "SaxSuit": 0x80,
}


def set_starting_items(rom: Rom, data: Any) -> None:
    def get_ability_flags(ability_flags: Dict[str, int]) -> int:
        status = 0
        for ability, flag in ability_flags.items():
            if ability in abilities:
                status |= flag
        return status

    # get health/ammo amounts
    energy = data.get("Energy", 99)
    missiles = data.get("Missiles", 10)
    power_bombs = data.get("PowerBombs", 10)
    # get ability status flags
    abilities = data.get("Abilities", [])
    beam_status = get_ability_flags(BEAM_FLAGS)
    missile_bomb_status = get_ability_flags(MISSILE_BOMB_FLAGS)
    suit_misc_status = get_ability_flags(SUIT_MISC_FLAGS)
    # get security level flags
    levels = data.get("SecurityLevels", [])
    level_status = 1
    for level in levels:
        level_status |= 1 << level
    # get downloaded map flags
    maps = data.get("DownloadedMaps", range(7))
    map_status = 0
    for map in maps:
        map_status |= 1 << map
    # write to rom
    addr = rom.starting_equipment_addr()
    rom.write_16(addr, energy)
    rom.write_16(addr + 2, energy)
    rom.write_16(addr + 4, missiles)
    rom.write_16(addr + 6, missiles)
    rom.write_8(addr + 8, power_bombs)
    rom.write_8(addr + 9, power_bombs)
    rom.write_8(addr + 0xA, beam_status)
    rom.write_8(addr + 0xB, missile_bomb_status)
    rom.write_8(addr + 0xC, suit_misc_status)
    rom.write_8(addr + 0xD, level_status)
    rom.write_8(addr + 0xE, map_status)


# TODO: move this?
def set_tank_increments(rom: Rom, data: Any) -> None:
    rom.write_16(TANK_INC_ADDR, data["MissileTank"])
    rom.write_16(TANK_INC_ADDR + 2, data["EnergyTank"])
    rom.write_16(TANK_INC_ADDR + 4, data["PowerBombTank"])
